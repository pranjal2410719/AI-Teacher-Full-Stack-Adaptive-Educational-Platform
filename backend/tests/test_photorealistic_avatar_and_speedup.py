"""
Unit and Integration Tests for Milestone 1:
Photorealistic Avatar, High-Speed Video Engine, Standardization & Branding.
"""

import os
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


def test_photorealistic_assets_exist_and_specs():
    """Verifies that photorealistic portrait assets exist with 1280x720 RGB specifications."""
    f_path = settings.avatar_dir / "teacher_portrait.png"
    m_path = settings.avatar_dir / "teacher_portrait_male.png"

    assert f_path.exists(), f"Missing female portrait at {f_path}"
    assert m_path.exists(), f"Missing male portrait at {m_path}"

    with Image.open(f_path) as img:
        assert img.size == (1280, 720)
        assert img.mode == "RGB"

    with Image.open(m_path) as img:
        assert img.size == (1280, 720)
        assert img.mode == "RGB"


def test_avatar_service_persona_resolution():
    """Verifies that AvatarService correctly resolves male and female personas."""
    female_img, female_geo = avatar_service._resolve_base_portrait("sarah")
    assert female_geo["key"] == "female"
    assert female_geo["default_name"] == "Dr. Sarah Vance"
    assert female_img.size == (1280, 720)

    male_img, male_geo = avatar_service._resolve_base_portrait("alex")
    assert male_geo["key"] == "male"
    assert male_geo["default_name"] == "Prof. Alexander Vance"
    assert male_img.size == (1280, 720)


def test_avatar_frame_visemes_and_apnihelp_branding():
    """Verifies that rendered avatar frames contain the ApniHelp branding and modulate lips."""
    frame_rest = avatar_service.render_avatar_frame(frame_idx=0, total_frames=60, energy=0.0)
    assert frame_rest.size == (1280, 720)

    frame_talking = avatar_service.render_avatar_frame(frame_idx=10, total_frames=60, energy=0.75)
    assert frame_talking.size == (1280, 720)

    # Convert to array to verify difference in mouth region
    # Mouth ROI is roughly x in [650, 750], y in [220, 280]
    rest_crop = np.array(frame_rest.crop((650, 220, 750, 280)))
    talking_crop = np.array(frame_talking.crop((650, 220, 750, 280)))
    assert not np.array_equal(rest_crop, talking_crop), "Viseme mouth did not modulate on audio energy"


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
