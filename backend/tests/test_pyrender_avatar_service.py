"""
Unit and integration tests for the off-screen ``PyrenderAvatarService``.

These tests exercise every layer of the new renderer:
- placeholder GLB generation + mesh load,
- procedural face geometry (head, eyes, nose, mouth, hair),
- head-state pre-rendering and cache,
- end-to-end MP4 clip generation (size + duration parity with audio),
- ApniHelp branding consistency on a sampled frame,
- graceful ``RuntimeError`` when ffmpeg fails.
"""

import os
import io
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest
import trimesh

os.environ.setdefault("PYOPENGL_PLATFORM", "egl")

from backend.app.config import settings  # noqa: E402
from backend.app.services.pyrender_avatar_service import (  # noqa: E402
    PyrenderAvatarService,
    pyrender_avatar_service,
    _build_face_components,
)
from backend.app.services.tts_service import tts_service  # noqa: E402


# =============================================================================
# Fixtures
# =============================================================================
@pytest.fixture(scope="module")
def pyrender_service() -> PyrenderAvatarService:
    """Reuse the module-level service so we exercise the singleton path too."""
    return pyrender_avatar_service


@pytest.fixture
def isolated_avatar_dir(tmp_path: Path) -> Path:
    """Provide a clean avatar directory so the placeholder creation path is tested."""
    avatar_dir = tmp_path / "avatars"
    avatar_dir.mkdir(parents=True, exist_ok=True)
    return avatar_dir


@pytest.fixture
def fresh_service(isolated_avatar_dir: Path) -> PyrenderAvatarService:
    """Create a service against an empty avatar dir to trigger placeholder creation."""
    return PyrenderAvatarService(avatar_dir=isolated_avatar_dir)


@pytest.fixture
def synthesized_audio() -> tuple[Path, float]:
    """Generate a short, low-cost audio sample for clip rendering tests."""
    return tts_service.synthesize_sync(
        "Quick pyrender avatar rendering test clip.",
        language="en",
    )


# =============================================================================
# 1. Initialization
# =============================================================================
def test_initialization_creates_placeholder_glb_when_missing(fresh_service, isolated_avatar_dir):
    """When no default_teacher.glb is present, the service must create a procedural head."""
    placeholder = isolated_avatar_dir / "default_teacher.glb"
    assert placeholder.exists(), "Placeholder GLB must be generated on first init"
    assert placeholder.stat().st_size > 0


def test_initialization_reuses_existing_glb(isolated_avatar_dir):
    """A pre-existing GLB must be respected (not overwritten) by the service."""
    model_path = isolated_avatar_dir / "default_teacher.glb"
    pre_existing = trimesh.creation.box(extents=[0.5, 0.5, 0.5])
    pre_existing.visual.vertex_colors = [10, 20, 30, 255]
    pre_existing.export(str(model_path))

    service = PyrenderAvatarService(avatar_dir=isolated_avatar_dir)

    assert service.model_path == model_path
    # Mesh should still be loadable as a trimesh after init
    assert isinstance(service.mesh, trimesh.Trimesh)
    assert service.mesh.vertices.shape[0] > 0


def test_initialization_loads_mesh_with_vertices(pyrender_service):
    """The mesh attribute must contain a populated vertex array."""
    assert isinstance(pyrender_service.mesh, trimesh.Trimesh)
    assert pyrender_service.mesh.vertices.shape[1] == 3
    assert pyrender_service.mesh.vertices.shape[0] > 10


# =============================================================================
# 2. Procedural face geometry
# =============================================================================
def test_build_face_components_returns_single_mesh():
    """``_build_face_components`` must return a single concatenated trimesh."""
    mesh = _build_face_components(open_amount=0.0, eyes_closed=False)
    assert isinstance(mesh, trimesh.Trimesh)
    # Head + hair + 2 ears + neck + collar + 3*2 eye parts + 2 eyelids +
    # 2 brows + nose + 2 cheeks + chin + 2 mouth parts
    assert mesh.vertices.shape[0] > 100, "Face mesh should have a substantial vertex count"


@pytest.mark.parametrize("open_amount", [0.5, 1.0])
def test_build_face_components_mouth_state_changes_geometry(open_amount):
    """The mouth-open state must change the mesh compared to the closed state."""
    closed = _build_face_components(open_amount=0.0, eyes_closed=False)
    open_ = _build_face_components(open_amount=open_amount, eyes_closed=False)
    # The open mouth drops the lower lip and exposes the inner cavity, so
    # either the vertex count differs OR the vertices themselves differ.
    if closed.vertices.shape == open_.vertices.shape:
        assert not np.allclose(closed.vertices, open_.vertices), (
            f"Mouth-open amount={open_amount} produced identical vertices to closed"
        )
    else:
        # Different vertex count is itself a valid signal of geometry change
        # (the open mouth adds the inner-cavity mesh).
        assert open_.vertices.shape[0] > closed.vertices.shape[0]


def test_build_face_components_eyes_closed_changes_geometry():
    """The eyes-closed state must change the mesh compared to the open-eyes state."""
    open_eyes = _build_face_components(open_amount=0.0, eyes_closed=False)
    closed_eyes = _build_face_components(open_amount=0.0, eyes_closed=True)
    if open_eyes.vertices.shape == closed_eyes.vertices.shape:
        assert not np.allclose(open_eyes.vertices, closed_eyes.vertices), (
            "Eyes-closed state should drop eyelids over the eyeballs"
        )
    else:
        # Different vertex count is a valid signal of geometry change
        assert closed_eyes.vertices.shape[0] != open_eyes.vertices.shape[0]


def test_head_state_cache_populates_on_first_render(pyrender_service, tmp_path, monkeypatch):
    """After rendering, the service must cache all 4 head states."""
    # Bypass real ffmpeg; we only want to trigger state cache population.
    class FakeStdin:
        def write(self, data: bytes) -> None: pass
        def close(self) -> None: pass

    class FakeProc:
        stdin = FakeStdin()
        stdout = None
        stderr = None
        returncode = 0
        def wait(self, timeout=None): return 0
        def kill(self): pass

    real_popen = subprocess.Popen
    def fake_popen(cmd, *args, **kwargs):
        if isinstance(cmd, list) and "rawvideo" in cmd:
            return FakeProc()
        return real_popen(cmd, *args, **kwargs)
    monkeypatch.setattr(subprocess, "Popen", fake_popen)

    audio, _ = tts_service.synthesize_sync("cache test", language="en")
    out = tmp_path / "state_cache.mp4"
    pyrender_service.render_avatar_clip(audio, out)

    # All 4 (mouth_open, eyes_closed) combinations should be cached.
    assert (False, False) in pyrender_service._state_cache
    assert (True, False) in pyrender_service._state_cache
    assert (False, True) in pyrender_service._state_cache
    assert (True, True) in pyrender_service._state_cache
    for img in pyrender_service._state_cache.values():
        assert img.mode == "RGBA"
        assert img.size[0] > 0 and img.size[1] > 0


# =============================================================================
# 3. End-to-end clip generation
# =============================================================================
def test_render_avatar_clip_produces_mp4(pyrender_service, synthesized_audio, tmp_path):
    """The renderer must produce a valid MP4 whose duration tracks the audio."""
    audio_path, audio_duration = synthesized_audio
    output_path = tmp_path / "pyrender_clip.mp4"

    returned = pyrender_service.render_avatar_clip(
        audio_path=audio_path,
        output_path=output_path,
        persona="professor_alex",
        subject_title="Pyrender Test",
        teacher_name="Prof. Test Avatar",
    )

    assert returned == output_path
    assert returned.exists(), "Output MP4 was not created"
    assert returned.stat().st_size > 5000, "Output MP4 is suspiciously small (< 5 KB)"

    video_duration = tts_service.get_audio_duration(returned)
    assert abs(video_duration - audio_duration) < 0.5, (
        f"Video duration {video_duration:.2f}s diverges from audio {audio_duration:.2f}s by >0.5s"
    )


def test_render_avatar_clip_does_not_write_intermediate_files(pyrender_service, synthesized_audio, tmp_path):
    """The new pipe-based pipeline must not leave any frames_* directories behind."""
    audio_path, _ = synthesized_audio
    output_path = tmp_path / "pyrender_clip_cleanup.mp4"
    pyrender_service.render_avatar_clip(audio_path=audio_path, output_path=output_path)

    leftover = list(output_path.parent.glob("frames_*"))
    assert leftover == [], f"Renderer left intermediate frame directories: {leftover}"
    # The single MP4 is the only artifact.
    assert output_path.exists()


# =============================================================================
# 4. Branding consistency
# =============================================================================
def test_render_avatar_clip_branding_present(pyrender_service, synthesized_audio, tmp_path, monkeypatch):
    """A sampled frame from the rendered clip must contain the teacher name banner.

    We monkey-patch the ffmpeg ``Popen`` so we can capture the raw RGB24
    frame stream the renderer writes to ffmpeg's stdin; the first frame is
    saved next to the expected output for inspection.
    """
    from PIL import Image

    audio_path, _ = synthesized_audio
    output_path = tmp_path / "pyrender_clip_brand.mp4"
    sample = output_path.with_suffix(".png")

    # Fake ``Popen`` that captures the first frame written to stdin instead of
    # invoking the real ffmpeg.
    class FakeStdin:
        def __init__(self):
            self._buf = bytearray()

        def write(self, data: bytes) -> None:
            self._buf.extend(data)

        def close(self) -> None:
            pass

    fake_stdin = FakeStdin()

    class FakeProc:
        stdin = fake_stdin
        stdout = None
        stderr = None
        returncode = 0

        def wait(self, timeout=None):
            # Save the first frame as a PNG for the test to inspect.
            if fake_stdin._buf:
                frame_size = pyrender_service.width * pyrender_service.height * 3
                first_frame = bytes(fake_stdin._buf[:frame_size])
                img = Image.frombytes(
                    "RGB",
                    (pyrender_service.width, pyrender_service.height),
                    first_frame,
                )
                img.save(sample)
                # Create a tiny valid MP4 placeholder so the output path "exists".
                output_path.write_bytes(b"\x00")
                self.returncode = 0
            else:
                # If we somehow got no frames, fail loudly so the test
                # diagnostic is clear rather than silently producing no sample.
                raise AssertionError(
                    "Fake Popen never received any frame bytes on stdin; "
                    "check that the renderer's per-frame loop is actually running."
                )
            return 0

        def kill(self):
            pass

    real_popen = subprocess.Popen

    def fake_popen(cmd, *args, **kwargs):
        # ffmpeg cmd layout: ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", ...]
        if isinstance(cmd, list) and "rawvideo" in cmd:
            return FakeProc()
        return real_popen(cmd, *args, **kwargs)

    monkeypatch.setattr(subprocess, "Popen", fake_popen)

    pyrender_service.render_avatar_clip(
        audio_path=audio_path,
        output_path=output_path,
        teacher_name="Prof. Test Brand",
        subject_title="Pyrender Branding",
    )

    assert sample.exists(), "No sample frame was captured for branding inspection"
    img = Image.open(sample)
    banner_x, banner_y = 60, 600
    fill_pixel = img.getpixel((banner_x + 100, banner_y + 40))
    # Fill is (15, 23, 42) per the service; allow small AA deviation.
    assert fill_pixel[0] < 60 and fill_pixel[1] < 60 and fill_pixel[2] < 80, (
        f"Banner fill color {fill_pixel} does not match expected dark slate"
    )
    sample.unlink(missing_ok=True)


# =============================================================================
# 5. Error fallback
# =============================================================================
def test_render_avatar_clip_raises_on_ffmpeg_failure(pyrender_service, synthesized_audio, tmp_path, monkeypatch):
    """A non-zero ffmpeg return code must surface as a RuntimeError."""
    audio_path, _ = synthesized_audio
    output_path = tmp_path / "pyrender_clip_fail.mp4"

    class FakeStdin:
        def write(self, data: bytes) -> None:
            pass

        def close(self) -> None:
            pass

    class FailingProc:
        stdin = FakeStdin()
        stdout = None
        stderr = io.BytesIO(b"simulated ffmpeg failure")

        def wait(self, timeout=None):
            self.returncode = 1
            return 1

        def kill(self):
            pass

    real_popen = subprocess.Popen

    def fake_popen(cmd, *args, **kwargs):
        # ffmpeg cmd layout: ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", ...]
        if isinstance(cmd, list) and "rawvideo" in cmd:
            return FailingProc()
        # Audio PCM extraction in AvatarService still uses subprocess.run
        # so it won't hit this branch; but be permissive in case ffmpeg is
        # also called for any auxiliary purpose.
        return real_popen(cmd, *args, **kwargs)

    monkeypatch.setattr(subprocess, "Popen", fake_popen)

    with pytest.raises(RuntimeError) as excinfo:
        pyrender_service.render_avatar_clip(audio_path=audio_path, output_path=output_path)
    assert "FFmpeg" in str(excinfo.value) or "ffmpeg" in str(excinfo.value)


def test_render_avatar_clip_raises_when_ffmpeg_binary_missing(pyrender_service, synthesized_audio, tmp_path, monkeypatch):
    """When the ffmpeg binary cannot be invoked, a clean error must propagate."""
    from backend.app.services import pyrender_avatar_service as mod

    audio_path, _ = synthesized_audio
    output_path = tmp_path / "pyrender_clip_nobinary.mp4"

    def fake_ffmpeg(*args, **kwargs):
        raise FileNotFoundError("ffmpeg not available")

    monkeypatch.setattr(mod.subprocess, "Popen", fake_ffmpeg)

    with pytest.raises(Exception):
        # FileNotFoundError is acceptable here; we just must not silently succeed.
        pyrender_service.render_avatar_clip(audio_path=audio_path, output_path=output_path)