"""
Unit and integration tests for the ``PyrenderAvatarService`` shim.

The shim keeps the public ``render_avatar_clip`` API so that
``video_stitcher.py`` can call it unchanged, but delegates to the
original high-speed 2.5D photorealistic viseme engine (see
``AvatarService``) — there is no longer a procedural 3D head.

These tests verify:
- shim initialization and public attributes
- end-to-end MP4 clip generation (size + duration parity with audio)
- graceful ``RuntimeError`` when ffmpeg fails
- that the rendered output contains the ApniHelp branding banner
- that the shim does not import or call into the 3D mesh helpers
"""

import os
import io
import subprocess
from pathlib import Path

import pytest

os.environ.setdefault("PYOPENGL_PLATFORM", "egl")

from backend.app.config import settings  # noqa: E402
from backend.app.services.pyrender_avatar_service import (  # noqa: E402
    PyrenderAvatarService,
    pyrender_avatar_service,
)
from backend.app.services.avatar_service import avatar_service  # noqa: E402
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
    """Provide a clean avatar directory so init paths can be exercised."""
    avatar_dir = tmp_path / "avatars"
    avatar_dir.mkdir(parents=True, exist_ok=True)
    return avatar_dir


@pytest.fixture
def fresh_service(isolated_avatar_dir: Path) -> PyrenderAvatarService:
    """Create a service against an isolated dir; legacy engine still runs."""
    return PyrenderAvatarService(avatar_dir=isolated_avatar_dir)


@pytest.fixture
def synthesized_audio() -> tuple[Path, float]:
    """Generate a short, low-cost audio sample for clip rendering tests."""
    return tts_service.synthesize_sync(
        "Quick avatar rendering test clip.",
        language="en",
    )


# =============================================================================
# 1. Initialization (shim)
# =============================================================================
def test_service_initializes_with_isolated_avatar_dir(fresh_service, isolated_avatar_dir):
    """A service built against a fresh avatar dir must still come up cleanly."""
    assert fresh_service.avatar_dir == isolated_avatar_dir
    assert fresh_service.avatar_dir.exists()
    # The shim reports the canonical 1280x720 output size.
    assert fresh_service.width == 1280
    assert fresh_service.height == 720
    assert fresh_service.fps == 30


def test_service_exposes_legacy_engine_reference(fresh_service):
    """The shim must hold a reference to the legacy AvatarService for delegation."""
    assert fresh_service._avatar_engine is avatar_service


def test_service_model_path_under_avatar_dir(fresh_service, isolated_avatar_dir):
    """The ``model_path`` attribute is the legacy compat slot for the GLB path."""
    assert fresh_service.model_path == isolated_avatar_dir / "default_teacher.glb"


# =============================================================================
# 2. 3D face helpers are removed
# =============================================================================
def test_no_procedural_face_helpers_exported():
    """The 3D face construction helpers must no longer be exported."""
    import backend.app.services.pyrender_avatar_service as mod
    # These were the trimesh-based face builders in the previous iteration.
    assert not hasattr(mod, "_build_face_components")
    assert not hasattr(mod, "_build_head_base")
    assert not hasattr(mod, "_build_eyeball")
    assert not hasattr(mod, "_build_mouth")


# =============================================================================
# 3. End-to-end clip generation (delegated to AvatarService)
# =============================================================================
def test_render_avatar_clip_produces_mp4(pyrender_service, synthesized_audio, tmp_path):
    """The renderer must produce a valid MP4 whose duration tracks the audio."""
    audio_path, audio_duration = synthesized_audio
    output_path = tmp_path / "pyrender_clip.mp4"

    returned = pyrender_service.render_avatar_clip(
        audio_path=audio_path,
        output_path=output_path,
        persona="professor_alex",
        subject_title="Avatar Test",
        teacher_name="Prof. Test Avatar",
    )

    assert returned == output_path
    assert returned.exists(), "Output MP4 was not created"
    assert returned.stat().st_size > 5000, "Output MP4 is suspiciously small (< 5 KB)"

    video_duration = tts_service.get_audio_duration(returned)
    assert abs(video_duration - audio_duration) < 0.5, (
        f"Video duration {video_duration:.2f}s diverges from audio {audio_duration:.2f}s by >0.5s"
    )


def test_render_avatar_clip_uses_legacy_engine(pyrender_service, synthesized_audio, tmp_path, monkeypatch):
    """The shim must call into the legacy ``AvatarService`` (not run a 3D scene)."""
    audio_path, _ = synthesized_audio
    output_path = tmp_path / "pyrender_legacy_check.mp4"

    called: dict = {}

    real_generate = avatar_service.generate_avatar_clip

    def spy(audio_path, output_path, **kwargs):
        called["yes"] = True
        called["persona"] = kwargs.get("persona")
        called["teacher_name"] = kwargs.get("teacher_name")
        return real_generate(audio_path, output_path, **kwargs)

    monkeypatch.setattr(avatar_service, "generate_avatar_clip", spy)

    pyrender_service.render_avatar_clip(
        audio_path=audio_path,
        output_path=output_path,
        persona="professor_alex",
        teacher_name="Prof. Spy Check",
    )

    assert called.get("yes") is True
    assert called.get("persona") == "professor_alex"
    assert called.get("teacher_name") == "Prof. Spy Check"


# =============================================================================
# 4. Branding consistency — the legacy service paints the ApniHelp banner
#    on every frame, so the output MP4 should contain the banner overlay.
# =============================================================================
def test_render_avatar_clip_contains_apnihelp_branding(pyrender_service, synthesized_audio, tmp_path):
    """A sampled frame must contain the ApniHelp lower-third banner."""
    from PIL import Image
    import subprocess as sp

    audio_path, _ = synthesized_audio
    output_path = tmp_path / "pyrender_clip_brand.mp4"
    sample_path = tmp_path / "pyrender_clip_brand.png"

    pyrender_service.render_avatar_clip(
        audio_path=audio_path,
        output_path=output_path,
        teacher_name="Prof. Test Brand",
        subject_title="Avatar Branding",
    )
    assert output_path.exists()

    # Extract the middle frame as a PNG for inspection.
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-ss", "00:00:00.5", "-i", str(output_path),
        "-frames:v", "1", str(sample_path),
    ]
    sp.run(cmd, check=False)
    assert sample_path.exists(), f"ffmpeg failed to extract a frame: {sample_path}"

    img = Image.open(sample_path).convert("RGB")
    # The banner sits at x in [60, 600], y in [600, 680] in the 1280x720
    # frame. The fill colour is (15, 23, 42) per the legacy renderer.
    fill_pixel = img.getpixel((100, 640))
    assert fill_pixel[0] < 60 and fill_pixel[1] < 60 and fill_pixel[2] < 80, (
        f"Banner fill color {fill_pixel} does not match expected dark slate"
    )
    sample_path.unlink(missing_ok=True)


# =============================================================================
# 5. Error fallback
# =============================================================================
def test_render_avatar_clip_raises_on_ffmpeg_failure(
    pyrender_service, synthesized_audio, tmp_path, monkeypatch
):
    """A non-zero ffmpeg return code must surface as a RuntimeError."""
    audio_path, _ = synthesized_audio
    output_path = tmp_path / "pyrender_clip_fail.mp4"

    class FakeStdin:
        def write(self, data: bytes) -> None: pass
        def close(self) -> None: pass

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
        # The legacy engine starts ffmpeg with rawvideo + libx264. Catch
        # the encoding call to simulate failure.
        if isinstance(cmd, list) and "rawvideo" in cmd:
            return FailingProc()
        return real_popen(cmd, *args, **kwargs)

    monkeypatch.setattr(subprocess, "Popen", fake_popen)

    with pytest.raises(RuntimeError) as excinfo:
        pyrender_service.render_avatar_clip(audio_path=audio_path, output_path=output_path)
    assert "FFmpeg" in str(excinfo.value) or "ffmpeg" in str(excinfo.value)


def test_render_avatar_clip_raises_when_ffmpeg_binary_missing(
    pyrender_service, synthesized_audio, tmp_path, monkeypatch
):
    """When the ffmpeg binary cannot be invoked, a clean error must propagate."""
    from backend.app.services import pyrender_avatar_service as mod

    audio_path, _ = synthesized_audio
    output_path = tmp_path / "pyrender_clip_nobinary.mp4"

    def fake_ffmpeg(*args, **kwargs):
        raise FileNotFoundError("ffmpeg not available")

    monkeypatch.setattr(mod.subprocess, "Popen", fake_ffmpeg)

    with pytest.raises(Exception):
        # FileNotFoundError is acceptable; we just must not silently succeed.
        pyrender_service.render_avatar_clip(audio_path=audio_path, output_path=output_path)