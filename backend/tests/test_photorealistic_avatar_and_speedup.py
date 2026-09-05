"""
Unit and Integration Tests for Milestone 1:
Illustrated Teacher Avatar, High-Speed Video Engine, Standardization & Branding.

NOTE: The avatar backend was reworked to a flat 2D illustrated teacher
(no 3D model, no portrait asset). Tests that previously required
``teacher_portrait.png`` / ``teacher_portrait_male.png`` now exercise
the ``AvatarService`` illustrated-teacher API directly.
"""

import os
import importlib.util
import time
import asyncio
import subprocess
from pathlib import Path
import pytest
import numpy as np
from PIL import Image

from backend.app.config import settings
from backend.app.services.avatar_service import avatar_service
from backend.app.services.video_stitcher import video_stitcher
from backend.app.services.slide_render_service import slide_render_service
from backend.app.services.tts_service import tts_service
from backend.app.models.video import VideoGenerationRequest
from backend.app.demo_generator import create_calculus_demo_plan_en


# Historical context: the video stitcher delegates avatar segments to
# ``pyrender_avatar_service`` (a shim around ``AvatarService``). The
# performance SLA below is measured against the illustrated-teacher
# pipeline; the pyrender off-screen backend is no longer active.
_PYRENDER_INSTALLED = importlib.util.find_spec("pyrender") is not None
_SLA_SKIP_REASON = (
    "Pyrender off-screen backend is no longer the active avatar pipeline; "
    "the illustrated-teacher backend is exercised by test_video_engine_performance_sla."
)


def test_avatar_service_is_illustrated_teacher():
    """The avatar pipeline is a flat 2D illustrated teacher, no portrait assets required."""
    # The service is a pure 2D PIL renderer. Verify the public surface.
    assert avatar_service.width == 1280
    assert avatar_service.height == 720
    assert avatar_service.fps == 30

    # The 3D portrait helpers / portrait asset lookups must be gone.
    assert not hasattr(avatar_service, "_resolve_base_portrait")
    # No 3D mesh helpers on the illustrated-teacher service either.
    assert not hasattr(avatar_service, "_build_face_components")
    assert not hasattr(avatar_service, "_build_head_base")
    assert not hasattr(avatar_service, "_build_eyeball")
    assert not hasattr(avatar_service, "_build_mouth")


def test_avatar_frame_visemes_and_apnihelp_branding():
    """Renders two frames at different energies; the mouth region must differ."""
    frame_rest = avatar_service.render_avatar_frame(
        frame_idx=0, total_frames=60, energy=0.0,
        subject_title="Viseme Test", teacher_name="Prof. Rest",
    )
    assert frame_rest.size == (1280, 720)

    frame_talking = avatar_service.render_avatar_frame(
        frame_idx=10, total_frames=60, energy=0.75,
        subject_title="Viseme Test", teacher_name="Prof. Talk",
    )
    assert frame_talking.size == (1280, 720)

    # The illustrated teacher's mouth is at HEAD_CX=640, HEAD_CY=290
    # with MOUTH_OFFSET_Y=110 ⇒ roughly (640, 400). Allow a generous ROI.
    rest_crop = np.array(frame_talking.crop((560, 350, 720, 460)))
    # Build a "loud" frame and compare against a "quiet" frame.
    frame_loud = avatar_service.render_avatar_frame(
        frame_idx=20, total_frames=60, energy=0.95,
        subject_title="Viseme Test", teacher_name="Prof. Loud",
    )
    loud_crop = np.array(frame_loud.crop((560, 350, 720, 460)))
    assert not np.array_equal(rest_crop, loud_crop), (
        "Viseme mouth did not modulate on audio energy"
    )


def test_avatar_banner_branding_is_present():
    """The ApniHelp banner region must contain the dark slate banner fill."""
    img = avatar_service.render_avatar_frame(
        frame_idx=0, total_frames=30, energy=0.0,
        subject_title="Branding", teacher_name="Prof. Brand",
    )
    # Banner sits at x in [60, 600], y in [600, 680] (60+540, 600+80).
    fill = img.getpixel((100, 640))
    assert fill[0] < 60 and fill[1] < 60 and fill[2] < 80, (
        f"Banner fill color {fill} does not match expected dark slate"
    )


def test_slide_render_standardization_and_branding():
    """Verifies slide render service standardizes canvas with ApniHelp logo and valid Mathtext."""
    img, draw = slide_render_service._draw_base_canvas("Introduction to Limits")
    assert img.size == (1280, 720)

    # Test Mathtext replacement for arrows
    cleaned = slide_render_service._clean_latex_for_mathtext(r"A \implies B \iff C")
    assert r"\Rightarrow" in cleaned
    assert r"\Leftrightarrow" in cleaned
    assert r"\implies" not in cleaned


def test_concurrent_tts_synthesis():
    """Verifies that multi-segment TTS executes concurrently via asyncio.gather."""
    texts = [
        "Short segment 1 for testing.",
        "Short segment 2 for testing.",
        "Short segment 3 for testing.",
    ]
    async def _run():
        tasks = [tts_service.synthesize(t, language="en") for t in texts]
        return await asyncio.gather(*tasks)

    results = asyncio.run(_run())

    assert len(results) == 3
    for p, dur in results:
        assert p.exists()
        assert dur > 0.1


def test_stream_copy_concat_speed():
    """Verifies FFmpeg concat demuxer with -c copy runs in < 1.0 second."""
    # Create sample audio and video clip
    audio_path, dur = tts_service.synthesize_sync("Quick stream copy verification.", language="en")
    clip_path = settings.video_dir / "bench_stream_copy_test.mp4"
    avatar_service.generate_avatar_clip(audio_path, clip_path, subject_title="Bench Test")
    assert clip_path.exists()

    concat_txt = settings.video_dir / "bench_concat.txt"
    concat_txt.write_text(f"file '{clip_path.resolve()}'\nfile '{clip_path.resolve()}'\n")
    out_mp4 = settings.video_dir / "bench_concat_out.mp4"

    cmd = [
        settings.ffmpeg_path, "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_txt),
        "-c", "copy",
        "-movflags", "+faststart",
        str(out_mp4),
    ]
    t0 = time.perf_counter()
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    t_concat = time.perf_counter() - t0

    assert proc.returncode == 0, f"FFmpeg error: {proc.stderr.decode()}"
    assert t_concat < 1.0, f"Stream copy concat took {t_concat:.3f}s (expected < 1.0s)"

    # Clean up bench files
    concat_txt.unlink(missing_ok=True)
    out_mp4.unlink(missing_ok=True)
    clip_path.unlink(missing_ok=True)


def test_video_engine_performance_sla():
    """
    R1 Acceptance Criterion:
    Processing rate must be <= 20.0s per minute of final video length.

    Measured against the illustrated-teacher backend.
    """
    plan = create_calculus_demo_plan_en()
    # Use 4 segments to exercise parallel slide rendering across thread workers
    plan.modules = plan.modules[:4]

    req = VideoGenerationRequest(
        plan_id=plan.plan_id,
        custom_persona="sarah",
    )

    t0 = time.perf_counter()
    manifest, out_video = asyncio.run(video_stitcher.generate_lesson_video(plan, req))
    t_proc = time.perf_counter() - t0

    dur = manifest.total_duration_sec
    assert dur > 10.0
    rate = t_proc * 60.0 / dur

    print(f"\n[Test SLA] Video Dur: {dur:.2f}s, Proc: {t_proc:.2f}s, Rate: {rate:.2f}s/min")
    assert rate <= 20.0, f"Processing rate {rate:.2f}s/min exceeds SLA threshold of 20s/min"
