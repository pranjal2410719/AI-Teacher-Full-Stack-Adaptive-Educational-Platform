# """
# Server-side off-screen avatar rendering using pyrender & trimesh.
#
# Renders a procedurally generated human-like teacher head as a 3D scene:
#   - skull (taller-than-wide ellipsoid for a head silhouette)
#   - hair cap, ears, neck, shoulders
#   - eyes with whites, irises, pupils, eyelids (blink animation)
#   - eyebrows, nose, lips + inner mouth (audio-driven lip-sync)
#   - cheeks, chin
#
# The head is rendered ONCE per "state" combination (mouth open/closed,
# eyes open/closed) at session start; subsequent frames PIL-alpha-blend
# between cached states to produce smooth audio-driven animation without
# any per-frame GL work.
#
# Performance: the 3D scene is rendered only 4 times (4 states), not once
# per video frame. Per-frame cost is dominated by PIL compositing (~3 ms).
# """

import os
import subprocess
import json
import math
import threading
import contextlib
import numpy as np
from pathlib import Path
from typing import Tuple, Optional, List

import trimesh
import pyrender
from PIL import Image, ImageDraw, ImageFont

# Force a headless OpenGL backend (EGL preferred, OSMesa fallback) so that
# off-screen rendering works inside CI / sandboxed environments that have no
# display server attached.
os.environ.setdefault("PYOPENGL_PLATFORM", "egl")

from backend.app.config import settings
from backend.app.services.avatar_service import AvatarService  # reuse envelope extraction

# -----------------------------------------------------------------------------
# Layout constants
# -----------------------------------------------------------------------------
INTERNAL_WIDTH = 960
INTERNAL_HEIGHT = 540

OUTPUT_WIDTH = 1280
OUTPUT_HEIGHT = 720

# Per-frame state cache size: 4 head states (mouth-closed/eyes-open,
# mouth-open/eyes-open, mouth-closed/eyes-closed, mouth-open/eyes-closed)
# we pre-render once and cross-fade between them. This is the single
# performance trick that makes per-frame work sub-millisecond.
HEAD_STATES: List[Tuple[str, bool, bool]] = [
    ("rest",       False, False),  # name, mouth_open, eyes_closed
    ("talking",    True,  False),
    ("blink",      False, True),
    ("blink_talk", True,  True),
]


# -----------------------------------------------------------------------------
# Color palette (RGB, 0-255)
# -----------------------------------------------------------------------------
SKIN_RGB     = (236, 202, 168)   # warm peach skin tone
HAIR_RGB     = (40,  26,  18)    # dark brown
EYE_WHITE    = (245, 244, 240)
IRIS_RGB     = (78,  52,  37)    # brown iris
PUPIL_RGB    = (8,   6,   4)
LIP_RGB      = (200, 110, 105)   # muted coral
LIP_DARK_RGB = (90,  30,  28)    # inner-mouth shadow
BROW_RGB     = (50,  34,  22)
NOSE_SHADOW  = (200, 165, 140)
CHEEK_RGB    = (228, 162, 145)
SHIRT_RGB    = (38,  58,  92)    # navy shirt collar
SHIRT_DARK   = (24,  38,  64)
GLASSES_RGB  = (60,  60,  70)


# -----------------------------------------------------------------------------
# Mesh primitives
# -----------------------------------------------------------------------------
def _colored(mesh: trimesh.Trimesh, rgb: Tuple[int, int, int]) -> trimesh.Trimesh:
    """Attach a flat RGB color (with full alpha) to a mesh's vertex colors."""
    color = np.array([rgb[0], rgb[1], rgb[2], 255], dtype=np.uint8)
    n = mesh.vertices.shape[0]
    mesh.visual.vertex_colors = np.tile(color, (n, 1))
    return mesh


def _uvsphere(radius: float, subdivisions: int = 2) -> trimesh.Trimesh:
    return trimesh.creation.uv_sphere(radius=radius, count=[subdivisions * 8, subdivisions * 4])


def _build_head_base() -> trimesh.Trimesh:
    """Skull + jaw: a slightly elongated egg shape built from a sphere scaled in Y."""
    skull = _uvsphere(1.0, subdivisions=2)
    # Elongate vertically, narrow slightly on Z to give a head profile.
    skull.vertices[:, 0] *= 0.92
    skull.vertices[:, 1] *= 1.12
    skull.vertices[:, 2] *= 0.95
    # Add a slight chin point: push the lower-front vertices forward a bit.
    lower_mask = skull.vertices[:, 1] < -0.2
    front_mask = skull.vertices[:, 2] > 0.2
    chin = lower_mask & front_mask
    skull.vertices[chin, 2] += 0.08
    return _colored(skull, SKIN_RGB)


def _build_hair() -> trimesh.Trimesh:
    """A hair cap: top half of a slightly larger sphere."""
    hair = _uvsphere(1.02, subdivisions=2)
    hair.vertices[:, 0] *= 0.96
    hair.vertices[:, 1] *= 1.10
    hair.vertices[:, 2] *= 0.98
    # Keep only the top portion (above y=0.05) and add a slight fringe at the
    # forehead by keeping a narrow strip below.
    keep = hair.vertices[:, 1] > -0.05
    # Add some volume to the sides for hair-over-ears
    sides = (np.abs(hair.vertices[:, 0]) > 0.7) & (hair.vertices[:, 1] < 0.5) & (hair.vertices[:, 1] > -0.4)
    keep = keep | sides
    hair.update_vertices(keep)
    # Re-attach the cap geometry
    hair.vertices[:, 1] += 0.02  # raise slightly so it sits on the head
    return _colored(hair, HAIR_RGB)


def _build_ear(side: int) -> trimesh.Trimesh:
    """A small flattened ellipsoid ear at the side of the head."""
    ear = _uvsphere(0.18, subdivisions=1)
    ear.vertices[:, 0] *= 0.55  # narrow along the depth axis
    ear.vertices[:, 1] *= 1.25
    ear.vertices[:, 2] *= 0.45
    ear.apply_translation([0.95 * side, 0.05, 0.02])
    return _colored(ear, SKIN_RGB)


def _build_neck() -> trimesh.Trimesh:
    """Short cylinder neck below the head, no shoulders."""
    neck = trimesh.creation.cylinder(radius=0.32, height=0.4, sections=24)
    neck.apply_translation([0, -1.20, -0.05])
    return _colored(neck, SKIN_RGB)


def _build_shirt_collar() -> trimesh.Trimesh:
    """A flat shirt collar at the very bottom of the head silhouette."""
    collar = trimesh.creation.cylinder(radius=0.55, height=0.18, sections=32)
    collar.vertices[:, 1] *= 0.6
    collar.apply_translation([0, -1.45, 0.0])
    return _colored(collar, SHIRT_RGB)


def _build_eyeball(side: int) -> List[trimesh.Trimesh]:
    """Returns [white, iris, pupil] for one eye (side = -1 left, +1 right)."""
    x = 0.36 * side
    y = 0.20
    z = 0.83
    # Sclera (eye white): flattened sphere
    white = _uvsphere(0.13, subdivisions=1)
    white.vertices[:, 0] *= 1.10
    white.vertices[:, 1] *= 0.80  # flatten vertically
    white.vertices[:, 2] *= 1.05
    white.apply_translation([x, y, z])
    # Iris: a small disc on the front of the eyeball
    iris = _uvsphere(0.065, subdivisions=1)
    iris.vertices[:, 0] *= 1.0
    iris.vertices[:, 1] *= 1.0
    iris.vertices[:, 2] *= 0.30
    iris.apply_translation([x, y, z + 0.115])
    # Pupil: smaller dark disc in front of iris
    pupil = _uvsphere(0.030, subdivisions=1)
    pupil.vertices[:, 2] *= 0.20
    pupil.apply_translation([x, y, z + 0.135])
    return [
        _colored(white, EYE_WHITE),
        _colored(iris, IRIS_RGB),
        _colored(pupil, PUPIL_RGB),
    ]


def _build_eyelid(side: int, open_amount: float) -> trimesh.Trimesh:
    """Eyelid ellipsoid. open_amount=1 fully open (sitting above eye); 0 fully closed (covering eye)."""
    x = 0.36 * side
    y = 0.20 + 0.10 * open_amount  # raise lid higher when open
    z = 0.85
    lid = _uvsphere(0.15, subdivisions=1)
    lid.vertices[:, 0] *= 1.05
    lid.vertices[:, 1] *= 0.40 * (0.3 + 0.7 * open_amount)  # thin sliver when open, full coverage when closed
    lid.vertices[:, 2] *= 1.05
    lid.apply_translation([x, y, z])
    return _colored(lid, SKIN_RGB)


def _build_eyebrow(side: int) -> trimesh.Trimesh:
    """Curved brow ridge above each eye."""
    x = 0.36 * side
    y = 0.43
    z = 0.85
    brow = trimesh.creation.box(extents=[0.22, 0.045, 0.05])
    # Tilt the inner end slightly down for a thoughtful, calm expression
    inner = brow.vertices[:, 0] * side < 0
    brow.vertices[inner, 1] -= 0.012
    brow.apply_translation([x, y, z])
    return _colored(brow, BROW_RGB)


def _build_nose() -> trimesh.Trimesh:
    """A small triangular nose pyramid + nostril dots."""
    # Build a custom pyramid with the tip pushed forward
    nose = _uvsphere(0.15, subdivisions=1)
    nose.vertices[:, 0] *= 0.55
    nose.vertices[:, 1] *= 0.85
    nose.vertices[:, 2] *= 1.30
    # Push the lower-front portion out further
    front = nose.vertices[:, 2] > 0.05
    nose.vertices[front, 2] += 0.05
    nose.apply_translation([0, -0.10, 0.85])
    # Bridge highlight: a slightly darker strip
    bridge = _uvsphere(0.05, subdivisions=1)
    bridge.vertices[:, 2] *= 1.5
    bridge.apply_translation([0, 0.05, 1.05])
    return _colored(trimesh.util.concatenate([nose, bridge]), NOSE_SHADOW)


def _build_cheek(side: int) -> trimesh.Trimesh:
    """Subtle cheek blush dot."""
    cheek = _uvsphere(0.10, subdivisions=1)
    cheek.vertices[:, 0] *= 1.10
    cheek.vertices[:, 1] *= 0.55
    cheek.vertices[:, 2] *= 0.30
    cheek.apply_translation([0.55 * side, -0.18, 0.78])
    return _colored(cheek, CHEEK_RGB)


def _build_chin() -> trimesh.Trimesh:
    """Chin point: a small bump under the lower lip."""
    chin = _uvsphere(0.10, subdivisions=1)
    chin.vertices[:, 0] *= 1.10
    chin.vertices[:, 1] *= 0.65
    chin.vertices[:, 2] *= 0.75
    chin.apply_translation([0, -0.55, 0.80])
    return _colored(chin, SKIN_RGB)


def _build_mouth(open_amount: float) -> List[trimesh.Trimesh]:
    """Build the lips + inner mouth cavity.

    open_amount in [0, 1] controls how far the mouth is open:
      0 = closed, lips touch
      1 = wide open (e.g. "ah" sound)
    """
    # Upper lip: thin curved strip
    upper = _uvsphere(0.18, subdivisions=1)
    upper.vertices[:, 0] *= 1.10
    upper.vertices[:, 1] *= 0.18
    upper.vertices[:, 2] *= 0.45
    upper.apply_translation([0, -0.30, 0.90])
    upper_top = upper.vertices[:, 1] > -0.30
    upper.update_vertices(upper_top)

    # Lower lip: same but with a vertical offset that grows with open_amount
    lower = _uvsphere(0.18, subdivisions=1)
    lower.vertices[:, 0] *= 1.05
    lower.vertices[:, 1] *= 0.22 + 0.10 * open_amount
    lower.vertices[:, 2] *= 0.45
    lower_y = -0.36 - 0.20 * open_amount
    lower.apply_translation([0, lower_y, 0.90])
    lower_keep = lower.vertices[:, 1] < -0.30 - 0.05 * open_amount
    lower.update_vertices(lower_keep)

    lips = trimesh.util.concatenate([upper, lower])

    # Inner mouth cavity (only visible when mouth is open)
    if open_amount > 0.05:
        cavity = _uvsphere(0.10, subdivisions=1)
        cavity.vertices[:, 0] *= 1.10
        cavity.vertices[:, 1] *= 0.15 + 0.25 * open_amount
        cavity.vertices[:, 2] *= 0.40
        cavity_y = -0.34 - 0.15 * open_amount
        cavity.apply_translation([0, cavity_y, 0.95])
        inner = _colored(cavity, LIP_DARK_RGB)
    else:
        inner = trimesh.Trimesh(vertices=np.zeros((0, 3)), faces=np.zeros((0, 3), dtype=int))

    return [_colored(lips, LIP_RGB), inner]


def _build_face_components(open_amount: float, eyes_closed: bool) -> trimesh.Trimesh:
    """Assemble the full face mesh for a given animation state."""
    parts: List[trimesh.Trimesh] = [
        _build_head_base(),
        _build_hair(),
        _build_ear(-1),
        _build_ear(+1),
        _build_neck(),
        _build_shirt_collar(),
    ]
    # Eyes + eyelids
    for side in (-1, +1):
        for part in _build_eyeball(side):
            parts.append(part)
        # open eyelid sits high; closed eyelid sits low covering the eye
        parts.append(_build_eyelid(side, 0.0 if eyes_closed else 1.0))
    # Eyebrows
    parts.append(_build_eyebrow(-1))
    parts.append(_build_eyebrow(+1))
    # Nose, cheeks, chin
    parts.append(_build_nose())
    parts.append(_build_cheek(-1))
    parts.append(_build_cheek(+1))
    parts.append(_build_chin())
    # Mouth (lips + cavity)
    for part in _build_mouth(open_amount):
        parts.append(part)

    return trimesh.util.concatenate(parts)


# -----------------------------------------------------------------------------
# Service
# -----------------------------------------------------------------------------
class PyrenderAvatarService:
    """Generate avatar video clips with off-screen rendering.

    The implementation mirrors the API of ``AvatarService.generate_avatar_clip``
    so that existing pipeline code can be swapped with minimal changes.
    """

    def __init__(self, avatar_dir: Path | None = None):
        self.avatar_dir = Path(avatar_dir) if avatar_dir else settings.avatar_dir
        self.avatar_dir.mkdir(parents=True, exist_ok=True)
        self.ffmpeg_path = settings.ffmpeg_path
        self.width = OUTPUT_WIDTH
        self.height = OUTPUT_HEIGHT
        self.fps = 30
        # Reuse the RMS-energy envelope logic from the original AvatarService
        self._base_avatar = AvatarService()
        # Path to the GLB model used for rendering
        self.model_path = self.avatar_dir / "default_teacher.glb"
        if not self.model_path.exists():
            self._create_placeholder_glb()
        # Load the mesh once (kept for API compatibility / future custom GLB)
        self.mesh = trimesh.load(str(self.model_path), force='scene')
        if isinstance(self.mesh, trimesh.Scene):
            dumped = getattr(self.mesh, "to_geometry", None)
            self.mesh = dumped() if callable(dumped) else self.mesh.dump(concatenate=True)
        # EGL contexts are per-thread
        self._tls = threading.local()
        # Key light: warm, from the front-right. Pyrender DirectionalLight
        # intensity is in lux; total lighting = sum of intensities is the
        # "luminance budget" that should land around 1.5-2.5 for a well-lit
        # face with vertex colors in the 0-1 range.
        self._light = pyrender.DirectionalLight(color=np.array([1.0, 0.97, 0.92]), intensity=1.1)
        # Fill light: cool, from the opposite side
        self._fill_light = pyrender.DirectionalLight(color=np.array([0.85, 0.90, 1.0]), intensity=0.5)
        # Rim light: from behind for hair/silhouette separation
        self._rim_light = pyrender.DirectionalLight(color=np.ones(3), intensity=0.5)
        # Camera positioned for a tight head-and-shoulders portrait.
        # Head extends from y=-1.3 to y=+1.2, about 2.5 units tall; we frame
        # the face from y=+1.0 (top of hair) to y=-0.8 (just below the chin).
        # At z=1.9 with FOV π/2.6 (~69°), the visible vertical range at z=0
        # is 2 * 1.9 * tan(35°) ≈ 2.66 units, which gives us a tight crop.
        self._camera = pyrender.PerspectiveCamera(yfov=np.pi / 2.6)
        self._camera_pose = np.eye(4)
        self._camera_pose[2, 3] = 1.9
        # Slight downward look (the head is above the optical axis)
        self._camera_pose[1, 3] = 0.0
        # Cached pre-rendered head states (RGBA images, transparent background)
        # Built lazily on the first call to render_avatar_clip.
        self._state_cache: dict = {}
        self._cache_lock = threading.Lock()

    # -------------------------------------------------------------------------
    # Renderer helpers
    # -------------------------------------------------------------------------
    def _get_renderer(self) -> "pyrender.OffscreenRenderer":
        renderer = getattr(self._tls, "renderer", None)
        if renderer is None:
            renderer = pyrender.OffscreenRenderer(
                viewport_width=INTERNAL_WIDTH, viewport_height=INTERNAL_HEIGHT
            )
            self._tls.renderer = renderer
        return renderer

    def _create_placeholder_glb(self) -> None:
        """Create the default teacher head as a GLB on first init.

        Exports the ``rest`` state mesh (eyes open, mouth closed) as a
        reference file. The runtime renderer rebuilds the full set of
        animated states in-memory on demand.
        """
        head = _build_face_components(open_amount=0.0, eyes_closed=False)
        head.export(str(self.model_path))
        print(f"Created teacher head GLB at {self.model_path}")

    # -------------------------------------------------------------------------
    # State pre-rendering
    # -------------------------------------------------------------------------
    def _render_state(self, mouth_open: bool, eyes_closed: bool) -> Image.Image:
        """Render one (mouth_open, eyes_closed) head state to an RGBA PIL Image."""
        mesh = _build_face_components(
            open_amount=0.85 if mouth_open else 0.0,
            eyes_closed=eyes_closed,
        )
        mesh.faces = mesh.faces.astype(np.int64)
        pr_mesh = pyrender.Mesh.from_trimesh(mesh, smooth=True)
        scene = pyrender.Scene(
            bg_color=[0, 0, 0, 0], ambient_light=[0.65, 0.65, 0.70]
        )
        scene.add(pr_mesh, pose=np.eye(4))
        scene.add(self._light, pose=np.eye(4))
        # Fill light from the opposite side to lift shadow areas
        fill_pose = np.eye(4)
        fill_pose[:3, 3] = [-2.0, 0.5, 1.5]
        scene.add(self._fill_light, pose=fill_pose)
        # Rim light from behind for hair/silhouette separation
        rim_pose = np.eye(4)
        rim_pose[:3, 3] = [0.0, 1.0, -2.0]
        scene.add(self._rim_light, pose=rim_pose)
        scene.add(self._camera, pose=self._camera_pose)
        renderer = self._get_renderer()
        color, _ = renderer.render(scene)
        rgba = np.concatenate(
            [color, np.full(color.shape[:2] + (1,), 255, dtype=np.uint8)],
            axis=-1,
        )
        # Treat only truly black pixels as transparent (background).
        # Keep dark face features (eyes, pupils, mouth cavity) opaque.
        luma = rgba[..., :3].astype(np.int16).sum(axis=-1)
        rgba[luma < 12, 3] = 0
        return Image.fromarray(rgba, mode="RGBA")

    def _get_state(self, mouth_open: bool, eyes_closed: bool) -> Image.Image:
        key = (bool(mouth_open), bool(eyes_closed))
        if key in self._state_cache:
            return self._state_cache[key]
        with self._cache_lock:
            if key in self._state_cache:
                return self._state_cache[key]
            img = self._render_state(*key)
            self._state_cache[key] = img
            return img

    def _ensure_all_states(self) -> None:
        """Eagerly render all 4 head states (used to warm the cache)."""
        for mouth_open in (False, True):
            for eyes_closed in (False, True):
                self._get_state(mouth_open, eyes_closed)

    # -------------------------------------------------------------------------
    # Per-frame compositing
    # -------------------------------------------------------------------------
    def _composite_frame(
        self,
        energy: float,
        teacher_name: str,
        subject_title: str,
        frame_idx: int,
        total_frames: int,
    ) -> Image.Image:
        """Composite one output frame from the cached states + audio energy.

        The mouth-closed/eyes-open state is the base; the mouth-open state is
        alpha-blended in proportional to audio energy; the eyes-closed state
        is alpha-blended in during a natural periodic blink.
        """
        frame = Image.new("RGB", (OUTPUT_WIDTH, OUTPUT_HEIGHT), (18, 24, 38))
        draw = ImageDraw.Draw(frame)

        ax = (OUTPUT_WIDTH - INTERNAL_WIDTH) // 2
        ay = 30

        # ----- Eyes: periodic blink (~ every 3.2 s, 150 ms closure) -----
        # Use a deterministic blink schedule based on frame index so it stays
        # stable across calls with the same audio.
        cycle_pos = (frame_idx / self.fps) % 3.2
        blink_phase = cycle_pos / 3.2
        # Sharp blink: 150 ms closed (~5 frames at 30 fps)
        eyes_closed_amount = 0.0
        if 0.94 < blink_phase < 1.0:
            # triangular envelope
            t = (blink_phase - 0.94) / 0.06
            eyes_closed_amount = 1.0 - abs(t - 0.5) * 2

        # ----- Mouth: open proportional to audio energy -----
        # Threshold so quiet/silence closes the mouth fully.
        mouth_open_amount = min(1.0, max(0.0, (energy - 0.02) * 2.5))

        # Fetch the 4 pre-rendered states
        rest_img = self._get_state(False, False)
        talk_img = self._get_state(True, False)
        blink_img = self._get_state(False, True)
        blink_talk_img = self._get_state(True, True)

        # Build the eyes-open mouth-blend layer (rest <-> talk)
        if mouth_open_amount > 0.01:
            mouth_layer = Image.blend(rest_img, talk_img, mouth_open_amount)
        else:
            mouth_layer = rest_img

        # Build the eyes-blend layer (mouth_layer <-> blink equivalents)
        if eyes_closed_amount > 0.01:
            blink_layer_mouth_closed = blink_img
            if mouth_open_amount > 0.01:
                blink_layer_talk = blink_talk_img
                blink_layer = Image.blend(
                    blink_layer_mouth_closed, blink_layer_talk, mouth_open_amount
                )
            else:
                blink_layer = blink_layer_mouth_closed
            face = Image.blend(mouth_layer, blink_layer, eyes_closed_amount)
        else:
            face = mouth_layer

        # Centre-paste the face onto the frame
        frame.paste(face, (ax, ay), face)

        # Subtle motion: gentle 2 px vertical bob to simulate breathing
        bob = int(2 * math.sin(2 * math.pi * 0.25 * (frame_idx / self.fps)))

        # ApniHelp banner with teacher name + subject title.
        banner_x, banner_y = 60, 600 + bob
        draw.rounded_rectangle(
            [banner_x, banner_y, banner_x + 540, banner_y + 80],
            radius=10,
            fill=(15, 23, 42),
            outline=(51, 65, 85),
            width=2,
        )
        draw.ellipse(
            [banner_x + 20, banner_y + 22, banner_x + 36, banner_y + 38],
            fill=(234, 179, 8),
        )
        draw.text((banner_x + 48, banner_y + 14), teacher_name, fill=(255, 255, 255))
        draw.text(
            (banner_x + 48, banner_y + 42),
            f"ApniHelp • {subject_title}",
            fill=(203, 213, 225),
        )
        return frame

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------
    def render_avatar_clip(
        self,
        audio_path: Path,
        output_path: Path,
        persona: str = "professor_alex",
        subject_title: str = "AI Teacher Lecture",
        teacher_name: str = "Prof. Alexander Vance",
    ) -> Path:
        """Render an avatar clip synchronised to ``audio_path``.

        Pipeline:
        1. Extract RMS-energy envelope from audio.
        2. Eagerly render the 4 head states (rest, talking, blink, blink+talk).
        3. Per frame: PIL-blend cached states driven by audio energy + time.
        4. Pipe raw RGB24 frames to ffmpeg (no PNG round-trip).
        """
        audio_path = Path(audio_path)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        envelope = self._base_avatar.extract_audio_energy_envelope(audio_path, fps=self.fps)
        total_frames = len(envelope)

        # Warm the head-state cache on this thread.
        self._ensure_all_states()

        ffmpeg_cmd = [
            self.ffmpeg_path,
            "-y",
            "-f", "rawvideo",
            "-pix_fmt", "rgb24",
            "-s", f"{OUTPUT_WIDTH}x{OUTPUT_HEIGHT}",
            "-r", str(self.fps),
            "-i", "pipe:0",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "ultrafast",
            "-crf", "26",
            "-movflags", "+faststart",
            str(output_path),
        ]
        try:
            proc = subprocess.Popen(
                ffmpeg_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except FileNotFoundError as e:
            raise RuntimeError(f"FFmpeg binary not available: {e}")

        assert proc.stdin is not None
        try:
            for i in range(total_frames):
                energy = float(envelope[i])
                img = self._composite_frame(
                    energy, teacher_name, subject_title,
                    frame_idx=i, total_frames=total_frames,
                )
                proc.stdin.write(img.tobytes())
            proc.stdin.close()
            proc.wait(timeout=900)
            if proc.returncode != 0:
                err = proc.stderr.read(4096).decode(errors="ignore") if proc.stderr else ""
                raise RuntimeError(f"FFmpeg rendering failed: {err}")
            return output_path
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
            raise
        finally:
            for stream in (proc.stdout, proc.stderr):
                try:
                    if stream is not None:
                        stream.close()
                except Exception:
                    pass


# Module-level singleton used by video_stitcher.
pyrender_avatar_service = PyrenderAvatarService()