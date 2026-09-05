"""
ApniHelp illustrated teacher avatar service.

The avatar is a flat, cartoon-style 2D character drawn directly with PIL
(no photograph, no 3D model, no portrait asset). The face is composed
of vector-like shapes:

  * oval head with a warm skin tone and a soft outline
  * hair cap
  * two large cartoon eyes (whites, irises, pupils, highlights) with a
    natural periodic blink
  * eyebrows that raise slightly when the mouth is open
  * small triangular nose
  * five-shape mouth (smile, slight, medium, wide, round-O) driven by
    the audio RMS envelope for lip-sync
  * cheek blush, neck, shirt collar

The character sits in the upper portion of a 1280x720 frame; the lower
third carries the ApniHelp banner with the teacher name and lesson
title. The public ``render_avatar_frame`` and ``generate_avatar_clip``
API is preserved so that ``video_stitcher.py`` and the
``pyrender_avatar_service`` shim keep working unchanged.
"""

import os
import math
import logging
import subprocess
from pathlib import Path
from typing import Optional, Tuple
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from backend.app.config import settings

logger = logging.getLogger(__name__)


# Branded palette
BG_TOP_RGB    = (15, 23, 42)      # slate-900
BG_BOT_RGB    = (30, 41, 59)      # slate-800
ACCENT_RGB    = (234, 179, 8)     # amber-400 (live indicator)
BANNER_BG_RGB = (15, 23, 42)
BANNER_BORDER = (71, 85, 105)
TITLE_RGB     = (255, 255, 255)
SUBTITLE_RGB  = (203, 213, 225)
WATERMARK_RGB = (100, 210, 170)

# Teacher palette (warm, friendly)
SKIN_RGB        = (244, 206, 178)   # warm peach
SKIN_SHADE_RGB  = (224, 178, 150)   # soft shadow on the face
OUTLINE_RGB     = (50, 38, 30)      # dark brown outline
HAIR_RGB        = (62, 38, 26)      # dark brown
HAIR_HIGHLIGHT  = (110, 78, 60)
EYE_WHITE_RGB   = (252, 252, 250)
IRIS_RGB        = (95, 60, 35)      # warm brown iris
PUPIL_RGB       = (15, 10, 5)
EYEBROW_RGB     = (60, 40, 28)
NOSE_RGB        = (210, 160, 130)
LIP_RGB         = (210, 100, 95)
LIP_DARK_RGB    = (90, 30, 30)
TOOTH_RGB       = (252, 250, 245)
TONGUE_RGB      = (210, 90, 90)
CHEEK_RGB       = (240, 170, 160)
SHIRT_RGB       = (40, 70, 110)
SHIRT_DARK_RGB  = (24, 48, 80)


# Anchor coordinates for the illustrated character on a 1280x720 frame
HEAD_CX = 640
HEAD_CY = 290
HEAD_RX = 175   # half-width of the head ellipse
HEAD_RY = 215   # half-height of the head ellipse

# Eyes (relative to head center)
EYE_OFFSET_X = 60       # horizontal distance from head center
EYE_OFFSET_Y = -30      # vertical offset (above center)
EYE_RX = 28             # eye width (radius x)
EYE_RY = 32             # eye height (radius y)
IRIS_R = 16
PUPIL_R = 8

# Eyebrows sit just above the eyes
BROW_OFFSET_Y = -65
BROW_LEN = 50
BROW_THICK = 8

# Nose (small triangle just below eye line)
NOSE_OFFSET_Y = 25
NOSE_W = 16
NOSE_H = 22

# Mouth — the centre of the mouth moves slightly with the head
MOUTH_OFFSET_Y = 110
MOUTH_BASE_W = 70
MOUTH_BASE_H = 30


class AvatarService:
    """Illustrated 2D teacher character with audio-driven lip-sync."""

    def __init__(self, avatar_dir: Optional[Path] = None):
        self.avatar_dir = Path(avatar_dir) if avatar_dir else settings.avatar_dir
        self.avatar_dir.mkdir(parents=True, exist_ok=True)
        self.ffmpeg_path = settings.ffmpeg_path
        self.ffprobe_path = settings.ffprobe_path
        self.width = 1280
        self.height = 720
        self.fps = 30

    # ------------------------------------------------------------------
    # Audio analysis
    # ------------------------------------------------------------------
    def extract_audio_energy_envelope(self, audio_path: Path, fps: int = 30) -> np.ndarray:
        """Decodes audio into 16 kHz mono PCM and returns a normalized
        per-frame RMS energy array (length = total_frames)."""
        sample_rate = 16000
        cmd = [
            self.ffmpeg_path, "-v", "error",
            "-i", str(audio_path),
            "-f", "s16le", "-ac", "1", "-ar", str(sample_rate),
            "pipe:1",
        ]
        try:
            raw_pcm = subprocess.check_output(cmd)
            audio_samples = np.frombuffer(raw_pcm, dtype=np.int16).astype(np.float32)
        except Exception as e:
            logger.warning(f"Audio PCM extraction failed for {audio_path}: {e}, using synthetic envelope.")
            audio_samples = np.zeros(sample_rate * 3, dtype=np.float32)

        total_audio_sec = len(audio_samples) / float(sample_rate)
        total_frames = max(1, int(math.ceil(total_audio_sec * fps)))
        samples_per_frame = int(sample_rate / fps)
        envelope = np.zeros(total_frames, dtype=np.float32)
        for f in range(total_frames):
            start = f * samples_per_frame
            end = min(len(audio_samples), start + samples_per_frame)
            if start < len(audio_samples) and end > start:
                chunk = audio_samples[start:end]
                envelope[f] = np.sqrt(np.mean(chunk ** 2))
        max_val = float(np.max(envelope)) if len(envelope) else 0.0
        if max_val > 100.0:
            envelope = envelope / max_val
        else:
            envelope = np.clip(envelope / 2000.0, 0.0, 1.0)
        smoothed = np.zeros_like(envelope)
        curr = 0.0
        for i, val in enumerate(envelope):
            curr = 0.4 * val + 0.6 * curr
            smoothed[i] = curr
        return smoothed

    # ------------------------------------------------------------------
    # Background and branding
    # ------------------------------------------------------------------
    def _gradient_backdrop(self) -> Image.Image:
        img = Image.new("RGB", (self.width, self.height), BG_TOP_RGB)
        draw = ImageDraw.Draw(img)
        top = np.array(BG_TOP_RGB, dtype=np.int16)
        bot = np.array(BG_BOT_RGB, dtype=np.int16)
        for y in range(self.height):
            t = y / max(1, self.height - 1)
            color = tuple((top * (1 - t) + bot * t).astype(int).tolist())
            draw.line([(0, y), (self.width, y)], fill=color)
        return img

    def _draw_banner(self, draw: ImageDraw.ImageDraw, teacher_name: str, subject_title: str) -> None:
        banner_x, banner_y = 60, 600
        draw.rounded_rectangle(
            [banner_x, banner_y, banner_x + 540, banner_y + 80],
            radius=10, fill=BANNER_BG_RGB, outline=BANNER_BORDER, width=2,
        )
        draw.ellipse([banner_x + 20, banner_y + 22, banner_x + 36, banner_y + 38], fill=ACCENT_RGB)
        draw.text((banner_x + 48, banner_y + 14), teacher_name, fill=TITLE_RGB)
        draw.text((banner_x + 48, banner_y + 42), f"ApniHelp • {subject_title}", fill=SUBTITLE_RGB)

    def _draw_watermark(self, draw: ImageDraw.ImageDraw) -> None:
        draw.rounded_rectangle(
            [self.width - 165, 18, self.width - 30, 52],
            radius=6, fill=BANNER_BG_RGB,
        )
        draw.text((self.width - 145, 26), "ApniHelp", fill=WATERMARK_RGB)

    def _draw_equalizer(self, draw: ImageDraw.ImageDraw, energy: float, t: float) -> None:
        eq_x, eq_y = 980, 660
        num_bars, bar_width, bar_gap = 16, 12, 5
        draw.rounded_rectangle(
            [eq_x - 20, eq_y - 60, eq_x + num_bars * (bar_width + bar_gap) + 15, eq_y + 20],
            radius=8, fill=BANNER_BG_RGB, outline=BANNER_BORDER, width=1,
        )
        for b in range(num_bars):
            harmonic_mod = 0.5 + 0.5 * math.sin(2.0 * math.pi * (0.8 * t + b * 0.15))
            bar_h = max(4, int(45 * energy * harmonic_mod + 4 * math.sin(t * 5 + b)))
            bx = eq_x + b * (bar_width + bar_gap)
            by = eq_y - bar_h
            col = (
                int(50 + 180 * (b / num_bars)),
                int(180 + 75 * (1.0 - b / num_bars)),
                int(230),
            )
            draw.rounded_rectangle([bx, by, bx + bar_width, eq_y], radius=3, fill=col)

    # ------------------------------------------------------------------
    # Character drawing helpers
    # ------------------------------------------------------------------
    def _draw_shirt(self, draw: ImageDraw.ImageDraw) -> None:
        """Shoulders + collar under the head."""
        # Two shoulder blobs forming a trapezoid
        left  = [(HEAD_CX - 250, 720), (HEAD_CX - 90, 580), (HEAD_CX - 50, 580), (HEAD_CX - 110, 720)]
        right = [(HEAD_CX + 250, 720), (HEAD_CX + 90, 580), (HEAD_CX + 50, 580), (HEAD_CX + 110, 720)]
        draw.polygon(left,  fill=SHIRT_RGB, outline=OUTLINE_RGB)
        draw.polygon(right, fill=SHIRT_RGB, outline=OUTLINE_RGB)
        # V-neck collar (a small darker triangle)
        draw.polygon(
            [
                (HEAD_CX - 60, 600),
                (HEAD_CX + 60, 600),
                (HEAD_CX + 30, 660),
                (HEAD_CX - 30, 660),
            ],
            fill=SKIN_RGB, outline=OUTLINE_RGB,
        )
        # Tie / shirt placket
        draw.rectangle([HEAD_CX - 8, 600, HEAD_CX + 8, 720], fill=SHIRT_DARK_RGB, outline=OUTLINE_RGB)

    def _draw_hair(self, draw: ImageDraw.ImageDraw) -> None:
        """Hair cap on top of the head."""
        # A wide arc that follows the top of the head
        hair_box = [
            HEAD_CX - HEAD_RX - 10, HEAD_CY - HEAD_RY - 20,
            HEAD_CX + HEAD_RX + 10, HEAD_CY + 40,
        ]
        draw.pieslice(hair_box, start=200, end=340, fill=HAIR_RGB, outline=OUTLINE_RGB)
        # Side hair tufts
        draw.ellipse(
            [HEAD_CX - HEAD_RX - 15, HEAD_CY - HEAD_RY + 60,
             HEAD_CX - HEAD_RX + 30, HEAD_CY + 30],
            fill=HAIR_RGB, outline=OUTLINE_RGB,
        )
        draw.ellipse(
            [HEAD_CX + HEAD_RX - 30, HEAD_CY - HEAD_RY + 60,
             HEAD_CX + HEAD_RX + 15, HEAD_CY + 30],
            fill=HAIR_RGB, outline=OUTLINE_RGB,
        )
        # Hair highlight (a thin curved line on top)
        draw.arc(
            [HEAD_CX - 100, HEAD_CY - HEAD_RY - 10,
             HEAD_CX + 100, HEAD_CY - HEAD_RY + 60],
            start=200, end=320, fill=HAIR_HIGHLIGHT, width=4,
        )

    def _draw_ears(self, draw: ImageDraw.ImageDraw) -> None:
        for side in (-1, +1):
            ex = HEAD_CX + side * (HEAD_RX - 5)
            ey = HEAD_CY + 10
            draw.ellipse([ex - 22, ey - 30, ex + 22, ey + 40], fill=SKIN_RGB, outline=OUTLINE_RGB)
            # Inner ear curve
            draw.arc(
                [ex - 12, ey - 15, ex + 12, ey + 25],
                start=270 if side < 0 else 90,
                end=90 if side < 0 else 270,
                fill=SKIN_SHADE_RGB, width=3,
            )

    def _draw_face_base(self, draw: ImageDraw.ImageDraw) -> None:
        """Head + cheek shading + cheeks."""
        # Head
        draw.ellipse(
            [HEAD_CX - HEAD_RX, HEAD_CY - HEAD_RY,
             HEAD_CX + HEAD_RX, HEAD_CY + HEAD_RY],
            fill=SKIN_RGB, outline=OUTLINE_RGB, width=3,
        )
        # Soft cheek shading on the right (light from the left)
        draw.chord(
            [HEAD_CX - HEAD_RX + 10, HEAD_CY - 20,
             HEAD_CX + HEAD_RX - 10, HEAD_CY + HEAD_RY - 20],
            start=300, end=60, fill=SKIN_SHADE_RGB,
        )
        # Blush dots
        for side in (-1, +1):
            cx = HEAD_CX + side * 110
            cy = HEAD_CY + 60
            draw.ellipse([cx - 18, cy - 12, cx + 18, cy + 12], fill=CHEEK_RGB)

    def _draw_eyebrows(self, draw: ImageDraw.ImageDraw, raise_amount: float = 0.0) -> None:
        """Slightly curved eyebrows; raise them when mouth is open."""
        brow_y = HEAD_CY + EYE_OFFSET_Y + BROW_OFFSET_Y - int(raise_amount * 8)
        for side in (-1, +1):
            cx = HEAD_CX + side * EYE_OFFSET_X
            # Slight curve
            draw.line(
                [(cx - BROW_LEN // 2, brow_y + 4),
                 (cx, brow_y - 4),
                 (cx + BROW_LEN // 2, brow_y + 4)],
                fill=EYEBROW_RGB, width=BROW_THICK,
            )

    def _draw_eyes(
        self, draw: ImageDraw.ImageDraw, blink_amount: float = 0.0
    ) -> None:
        """Open or partially closed eyes (driven by blink_amount 0..1)."""
        # As blink approaches 1, the eye height shrinks to a thin slit
        eye_h = max(2, int(EYE_RY * (1.0 - blink_amount)))
        for side in (-1, +1):
            cx = HEAD_CX + side * EYE_OFFSET_X
            cy = HEAD_CY + EYE_OFFSET_Y
            # Eye white
            draw.ellipse(
                [cx - EYE_RX, cy - eye_h,
                 cx + EYE_RX, cy + eye_h],
                fill=EYE_WHITE_RGB, outline=OUTLINE_RGB, width=2,
            )
            # Iris (only when eye is mostly open)
            if eye_h > EYE_RY * 0.4:
                iris_r = max(2, int(IRIS_R * (1.0 - blink_amount * 0.5)))
                draw.ellipse(
                    [cx - iris_r, cy - iris_r,
                     cx + iris_r, cy + iris_r],
                    fill=IRIS_RGB, outline=OUTLINE_RGB, width=1,
                )
                # Pupil
                pupil_r = max(1, int(PUPIL_R * (1.0 - blink_amount * 0.7)))
                draw.ellipse(
                    [cx - pupil_r, cy - pupil_r,
                     cx + pupil_r, cy + pupil_r],
                    fill=PUPIL_RGB,
                )
                # Highlight (small white dot)
                if eye_h > EYE_RY * 0.6:
                    draw.ellipse(
                        [cx - iris_r // 2, cy - iris_r,
                         cx - iris_r // 4, cy - iris_r + iris_r // 2],
                        fill=EYE_WHITE_RGB,
                    )
            else:
                # Eye is mostly closed — draw the eyelid line
                draw.line(
                    [(cx - EYE_RX, cy), (cx + EYE_RX, cy)],
                    fill=OUTLINE_RGB, width=3,
                )

    def _draw_nose(self, draw: ImageDraw.ImageDraw) -> None:
        """Small triangular nose."""
        nx = HEAD_CX
        ny = HEAD_CY + NOSE_OFFSET_Y
        # Triangle
        draw.polygon(
            [(nx - NOSE_W // 2, ny - NOSE_H // 2),
             (nx + NOSE_W // 2, ny - NOSE_H // 2),
             (nx, ny + NOSE_H // 2)],
            fill=(0, 0, 0, 0),  # transparent fill (we'll draw outline only)
        )
        # The above is invisible (RGBA 0 alpha) so we use a tinted fill:
        draw.polygon(
            [(nx - NOSE_W // 2, ny - NOSE_H // 2),
             (nx + NOSE_W // 2, ny - NOSE_H // 2),
             (nx, ny + NOSE_H // 2)],
            fill=SKIN_SHADE_RGB, outline=OUTLINE_RGB,
        )
        # Nostril dots
        for side in (-1, +1):
            draw.ellipse(
                [nx + side * 5 - 2, ny + NOSE_H // 2 - 4,
                 nx + side * 5 + 2, ny + NOSE_H // 2],
                fill=OUTLINE_RGB,
            )

    def _draw_mouth(self, draw: ImageDraw.ImageDraw, energy: float) -> None:
        """Lip-sync mouth. 5 shapes driven by audio energy.

        0.00 - 0.08 : closed gentle smile
        0.08 - 0.25 : slight opening (small dark oval)
        0.25 - 0.50 : medium opening (oval with teeth + tongue)
        0.50 - 0.75 : wide opening (big oval, teeth + tongue)
        0.75 - 1.00 : round O shape (small circle)
        """
        mx = HEAD_CX
        my = HEAD_CY + MOUTH_OFFSET_Y
        # Subtle mouth follows head bob
        my += int(1.2 * math.sin(2.0 * math.pi * 0.5 * (energy + 0.5)))

        if energy < 0.08:
            # Closed gentle smile
            smile_w = 70
            draw.arc(
                [mx - smile_w, my - 18, mx + smile_w, my + 18],
                start=20, end=160, fill=LIP_RGB, width=5,
            )
        elif energy < 0.25:
            # Slight open
            open_w = 28 + int(8 * (energy - 0.08) / 0.17)
            open_h = 10
            draw.ellipse(
                [mx - open_w, my - open_h, mx + open_w, my + open_h],
                fill=LIP_DARK_RGB, outline=LIP_RGB, width=3,
            )
            # Top teeth sliver
            draw.rectangle(
                [mx - open_w + 4, my - open_h + 1, mx + open_w - 4, my - open_h + 4],
                fill=TOOTH_RGB,
            )
        elif energy < 0.50:
            # Medium open
            t = (energy - 0.25) / 0.25
            open_w = 36 + int(10 * t)
            open_h = 18 + int(8 * t)
            draw.ellipse(
                [mx - open_w, my - open_h, mx + open_w, my + open_h],
                fill=LIP_DARK_RGB, outline=LIP_RGB, width=3,
            )
            # Upper teeth
            draw.rectangle(
                [mx - open_w + 5, my - open_h + 1, mx + open_w - 5, my - open_h + 5],
                fill=TOOTH_RGB,
            )
            # Tongue
            draw.ellipse(
                [mx - open_w // 2, my + open_h - 9,
                 mx + open_w // 2, my + open_h - 1],
                fill=TONGUE_RGB,
            )
        elif energy < 0.75:
            # Wide open (the "ah" shape)
            t = (energy - 0.50) / 0.25
            open_w = 46 + int(10 * t)
            open_h = 28 + int(10 * t)
            draw.ellipse(
                [mx - open_w, my - open_h, mx + open_w, my + open_h],
                fill=LIP_DARK_RGB, outline=LIP_RGB, width=3,
            )
            draw.rectangle(
                [mx - open_w + 6, my - open_h + 1, mx + open_w - 6, my - open_h + 6],
                fill=TOOTH_RGB,
            )
            draw.ellipse(
                [mx - open_w // 2 - 2, my + open_h - 12,
                 mx + open_w // 2 + 2, my + open_h - 1],
                fill=TONGUE_RGB,
            )
        else:
            # Round O shape (the "oh" sound)
            t = min(1.0, (energy - 0.75) / 0.25)
            r = int(18 + 8 * t)
            draw.ellipse(
                [mx - r, my - r, mx + r, my + r],
                fill=LIP_DARK_RGB, outline=LIP_RGB, width=4,
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def render_avatar_frame(
        self,
        frame_idx: int,
        total_frames: int,
        energy: float,
        persona: str = "professor_alex",  # API compat; unused
        subject_title: str = "AI Teaching Lecture",
        teacher_name: str = "Prof. Alexander Vance",
    ) -> Image.Image:
        """Render one 1280x720 RGB frame of the illustrated teacher.

        The frame contains:
          * gradient backdrop
          * illustrated cartoon teacher (head, hair, eyes, eyebrows, nose,
            mouth) in the upper 2/3 of the frame
          * ApniHelp banner + watermark in the lower 2/3
          * audio-driven equalizer in the bottom-right
        """
        # 1) Background + branding
        img = self._gradient_backdrop()
        draw = ImageDraw.Draw(img)
        self._draw_watermark(draw)

        # 2) Compute animation parameters
        t = frame_idx / float(self.fps) if self.fps else 0.0
        # Subtle head bob
        bob_y = int(1.5 * math.sin(2.0 * math.pi * 0.5 * t))
        bob_x = int(0.8 * math.sin(2.0 * math.pi * 0.25 * t))

        # 3) Shirt first (so the head sits on top)
        #    Temporarily shift the global head anchor for the bob
        global HEAD_CX, HEAD_CY
        orig_cx, orig_cy = HEAD_CX, HEAD_CY
        HEAD_CX += bob_x
        HEAD_CY += bob_y
        try:
            self._draw_shirt(draw)
            self._draw_hair(draw)
            self._draw_face_base(draw)
            self._draw_ears(draw)
            self._draw_eyebrows(draw, raise_amount=energy)
            self._draw_eyes(draw, blink_amount=self._blink_amount(frame_idx))
            self._draw_nose(draw)
            self._draw_mouth(draw, energy)
        finally:
            HEAD_CX, HEAD_CY = orig_cx, orig_cy

        # 4) Banner + equalizer
        self._draw_banner(draw, teacher_name, subject_title)
        self._draw_equalizer(draw, energy, t)
        return img

    @staticmethod
    def _blink_amount(frame_idx: int, period: int = 96, closure: int = 4) -> float:
        """Periodic blink: a short closure once every ``period`` frames."""
        phase = frame_idx % period
        if phase >= period - closure:
            # Triangular envelope: 0 → 1 → 0 over `closure` frames
            t = (phase - (period - closure)) / float(closure)
            return 1.0 - abs(t - 0.5) * 2
        return 0.0

    def generate_avatar_clip(
        self,
        audio_path: Path,
        output_path: Path,
        persona: str = "professor_alex",  # API compat; unused
        subject_title: str = "AI Teacher Lecture",
        teacher_name: str = "Prof. Alexander Vance",
    ) -> Path:
        """Render a 1280x720 30fps MP4 of the illustrated teacher, mixed
        with the supplied TTS audio. The audio RMS envelope drives the
        mouth shape (5 viseme states) and the equalizer bars."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        envelope = self.extract_audio_energy_envelope(audio_path, fps=self.fps)
        total_frames = len(envelope)

        cmd = [
            self.ffmpeg_path, "-y",
            "-f", "rawvideo", "-vcodec", "rawvideo",
            "-s", f"{self.width}x{self.height}",
            "-pix_fmt", "rgb24", "-r", str(self.fps),
            "-i", "-",
            "-i", str(audio_path),
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(self.fps),
            "-preset", "ultrafast", "-tune", "zerolatency",
            "-crf", "26", "-threads", "2",
            "-c:a", "aac", "-ar", "44100", "-ac", "2", "-b:a", "128k",
            "-shortest", "-movflags", "+faststart",
            str(output_path),
        ]
        proc = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        assert proc.stdin is not None
        try:
            for f in range(total_frames):
                energy = float(envelope[f])
                img = self.render_avatar_frame(
                    frame_idx=f, total_frames=total_frames, energy=energy,
                    subject_title=subject_title, teacher_name=teacher_name,
                )
                proc.stdin.write(img.tobytes())
            proc.stdin.close()
            proc.wait()
            if proc.returncode != 0:
                err = proc.stderr.read().decode(errors="ignore") if proc.stderr else ""
                logger.error(f"FFmpeg avatar rendering failed: {err}")
                raise RuntimeError(f"FFmpeg avatar rendering failed: {err}")
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


avatar_service = AvatarService()
