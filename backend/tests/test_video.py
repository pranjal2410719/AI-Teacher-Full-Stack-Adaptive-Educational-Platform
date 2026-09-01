"""
Unit and Integration Tests for Milestone 3: Hybrid Video Generation Pipeline.
Covers TTS Multilingual Synthesis, 2.5D Viseme Avatar, Subject-Aware Slide Renderers,
FFmpeg Video Stitcher, Manifests with Checkpoint Markers, and Range Streaming REST APIs.
"""

import os
import io
import time
import asyncio
import numpy as np
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.config import settings
from backend.app.models.video import (
    VideoGenerationRequest,
    VideoGenerationStatus,
    VideoSegmentMeta,
    VideoChapter,
    CheckpointPauseMarker,
    VideoManifest,
    VideoStage,
)
from backend.app.models.lesson_plan import (
    LessonPlan,
    LessonSegmentPlan,
    VisualSpec,
    VisualType,
    CheckpointQuestion,
    LearnerProfile,
    SegmentType,
)
from backend.app.services.tts_service import tts_service, TTSService
from backend.app.services.avatar_service import avatar_service, AvatarService
from backend.app.services.slide_render_service import slide_render_service, SlideRenderService
from backend.app.services.video_stitcher import video_stitcher, VideoStitcher
from backend.app.services.planner_service import planner_service

client = TestClient(app)


@pytest.fixture(scope="module")
def sample_lesson_plan():
    """Generates a concise 3-segment lesson plan optimized for fast video test execution."""
    modules = [
        LessonSegmentPlan(
            segment_id="seg_01",
            order=1,
            segment_type=SegmentType.AVATAR_INTRO,
            title="Introduction to Limits",
            duration_sec=20,
            script="Welcome to today's lesson on calculus limits.",
            visual_spec=VisualSpec(
                visual_type=VisualType.GENERAL_SLIDE,
                subject_domain="math",
                headline="Lesson Overview",
                bullet_points=["Calculus foundational concepts", "Rate of change"],
            ),
        ),
        LessonSegmentPlan(
            segment_id="seg_02",
            order=2,
            segment_type=SegmentType.VISUAL_CONCEPT,
            title="The Limit Concept",
            duration_sec=20,
            script="A limit describes the behavior of a function near a point.",
            visual_spec=VisualSpec(
                visual_type=VisualType.MATH_EQUATION,
                subject_domain="math",
                headline="Definition of a Limit",
                latex_equations=[r"\lim_{x \to 0} \frac{\sin x}{x} = 1"],
                bullet_points=["Direct substitution evaluation", "Convergence verification"],
            ),
            checkpoint_question=CheckpointQuestion(
                question_id="q_lim_01",
                question_text="What does a limit represent geometrically?",
                prompt="What does a limit represent geometrically?",
                question_type="mcq",
                options=["Approaching value", "Exact derivative", "Integral area", "Undefined"],
                correct_answer="Approaching value",
                explanation="A limit describes the value a function approaches.",
                concept="Limit Definition",
            ),
        ),
        LessonSegmentPlan(
            segment_id="seg_03",
            order=3,
            segment_type=SegmentType.AVATAR_SUMMARY,
            title="Summary & Next Steps",
            duration_sec=20,
            script="Great work! You now understand the limit foundation.",
            visual_spec=VisualSpec(
                visual_type=VisualType.GENERAL_SLIDE,
                subject_domain="math",
                headline="Key Takeaways",
                bullet_points=["Limits precede derivatives", "Continuous convergence"],
            ),
        ),
    ]

    plan = LessonPlan(
        plan_id="plan_test_video_concise",
        title="Calculus Limits Masterclass",
        target_duration_sec=60,
        total_actual_duration_sec=60,
        level="intermediate",
        language="en",
        subject_domain="math",
        topic="Calculus Limits",
        modules=modules,
    )
    planner_service.plans_registry[plan.plan_id] = plan
    return plan


@pytest.fixture(scope="module")
def generated_video_bundle(sample_lesson_plan):
    """Executes video generation once for the test module and provides manifest & video path."""
    req = VideoGenerationRequest(plan_id=sample_lesson_plan.plan_id, resolution="720p")
    task_id = "task_test_bundle_01"
    manifest, video_path = asyncio.run(
        video_stitcher.generate_lesson_video(sample_lesson_plan, req, task_id=task_id)
    )
    return manifest, video_path, task_id


# =============================================================================
# 1. Pydantic Models Validation Tests
# =============================================================================
def test_video_models_validation():
    """Validates video request, status, chapter, marker, and manifest schema validation."""
    # VideoGenerationRequest
    req = VideoGenerationRequest(plan_id="plan_12345", resolution="720p")
    assert req.plan_id == "plan_12345"
    assert req.resolution == "720p"

    with pytest.raises(ValueError):
        VideoGenerationRequest(plan_id="")

    # CheckpointPauseMarker
    marker = CheckpointPauseMarker(
        marker_id="pm_01",
        timestamp_sec=45.5,
        concept="Limits",
        question={"prompt": "What is the limit?", "type": "mcq"},
    )
    assert marker.timestamp_sec == 45.5
    assert marker.question["prompt"] == "What is the limit?"

    # VideoManifest
    manifest = VideoManifest(
        lesson_id="les_01",
        plan_id="plan_12345",
        video_url="/api/v1/video/stream/les_01.mp4",
        total_duration_sec=120.0,
        language="en",
        chapters=[{"title": "Intro", "start_sec": 0.0, "end_sec": 30.0, "type": "avatar_intro"}],
        pause_markers=[marker],
    )
    assert manifest.lesson_id == "les_01"
    assert manifest.video_id == "les_01"
    assert manifest.total_duration_sec == 120.0
    assert len(manifest.pause_markers) == 1
    assert manifest.pause_markers[0].marker_id == "pm_01"


# =============================================================================
# 2. TTS Multilingual Synthesis Tests
# =============================================================================
def test_tts_service_english_synthesis():
    """Verifies English speech synthesis with edge-tts neural voice and duration calculation."""
    audio_path, duration = tts_service.synthesize_sync(
        text="Welcome to the AI Teacher lesson on calculus.",
        language="en",
        voice="en-US-GuyNeural",
    )
    assert audio_path.exists()
    assert audio_path.stat().st_size > 1000
    assert duration > 0.5


def test_tts_service_hindi_synthesis():
    """Verifies Hindi speech synthesis with edge-tts neural voice."""
    audio_path, duration = tts_service.synthesize_sync(
        text="गणित की कक्षा में आपका स्वागत है।",
        language="hi",
        voice="hi-IN-MadhurNeural",
    )
    assert audio_path.exists()
    assert audio_path.stat().st_size > 1000
    assert duration > 0.5


def test_tts_service_voice_resolution_and_offline_fallback():
    """Verifies voice resolution mapping and offline harmonic waveform generation."""
    v_en = tts_service.resolve_voice("en")
    assert "Neural" in v_en
    v_hi = tts_service.resolve_voice("hi")
    assert "Madhur" in v_hi or "Neural" in v_hi

    # Test offline waveform generator
    tmp_wav = settings.audio_dir / "test_offline_fallback.wav"
    dur = tts_service._generate_offline_waveform("Testing local harmonic speech waveform synthesis.", tmp_wav)
    assert tmp_wav.exists()
    assert dur > 1.0
    tmp_wav.unlink(missing_ok=True)


# =============================================================================
# 3. 2.5D Audio-Driven Viseme Avatar Tests
# =============================================================================
def test_avatar_energy_envelope_extraction():
    """Verifies audio PCM extraction and normalized energy envelope generation."""
    audio_path, _ = tts_service.synthesize_sync("Testing audio energy envelope.", language="en")
    envelope = avatar_service.extract_audio_energy_envelope(audio_path, fps=30)
    assert len(envelope) > 10
    assert np.all(envelope >= 0.0)
    assert np.all(envelope <= 1.0)


def test_avatar_frame_rendering():
    """Verifies avatar canvas rendering across resting, talking, and blinking states."""
    frame_rest = avatar_service.render_avatar_frame(frame_idx=0, total_frames=60, energy=0.0)
    assert frame_rest.size == (1280, 720)
    assert frame_rest.mode == "RGB"

    frame_speech = avatar_service.render_avatar_frame(frame_idx=15, total_frames=60, energy=0.85)
    assert frame_speech.size == (1280, 720)

    frame_blink = avatar_service.render_avatar_frame(frame_idx=0, total_frames=60, energy=0.2)
    assert frame_blink.size == (1280, 720)


def test_avatar_video_clip_generation():
    """Verifies synthesis of synchronized talking avatar MP4 video clip."""
    audio_path, duration = tts_service.synthesize_sync("Hello students! Let us begin.", language="en")
    out_clip = settings.video_dir / "test_avatar_clip.mp4"
    clip = avatar_service.generate_avatar_clip(audio_path, out_clip, subject_title="Calculus Intro")

    assert clip.exists()
    assert clip.stat().st_size > 5000
    clip_dur = tts_service.get_audio_duration(clip)
    assert abs(clip_dur - duration) < 0.5


# =============================================================================
# 4. Subject-Aware Visual Slide Renderers Tests
# =============================================================================
def test_slide_render_math():
    """Verifies Math slide rendering with LaTeX formulas and function plot."""
    spec = VisualSpec(
        visual_type=VisualType.MATH_EQUATION,
        subject_domain="Mathematics",
        headline="Limits and Continuous Derivatives",
        latex_equations=[r"\lim_{x \to 0} \frac{\sin x}{x} = 1", r"f'(x) = 2x"],
        bullet_points=["Direct substitution yields indeterminate form.", "Apply trigonometric limit theorem."],
    )
    img = slide_render_service.render_math_slide(spec, "Calculus Limits")
    assert img.size == (1280, 720)


def test_slide_render_code():
    """Verifies CS code slide rendering with Pygments syntax-highlighted IDE window."""
    code = "def binary_search(arr, target):\n    low, high = 0, len(arr) - 1\n    return -1"
    spec = VisualSpec(
        visual_type=VisualType.CODE_SNIPPET,
        subject_domain="Computer Science",
        headline="Binary Search Algorithm",
        code_content=code,
        code_language="python",
        bullet_points=["Array must be sorted in ascending order.", "Time complexity is logarithmic O(log n)."],
    )
    img = slide_render_service.render_code_slide(spec, "Binary Search in Python")
    assert img.size == (1280, 720)


def test_slide_render_biology():
    """Verifies Biology diagram slide rendering with cellular anatomy and callouts."""
    spec = VisualSpec(
        visual_type=VisualType.DIAGRAM,
        subject_domain="Biology",
        headline="Eukaryotic Cell Organelles",
        bullet_points=["Mitochondria synthesize cellular ATP.", "Nucleus houses genomic DNA."],
    )
    img = slide_render_service.render_diagram_slide(spec, "Cell Biology Structure")
    assert img.size == (1280, 720)


def test_slide_render_history():
    """Verifies History timeline slide rendering with chronological milestone nodes."""
    spec = VisualSpec(
        visual_type=VisualType.TIMELINE,
        subject_domain="History",
        headline="The Industrial Revolution",
        timeline_events=[
            {"year": "1769", "title": "Watt Steam Engine", "description": "Condenser steam engine patented."},
            {"year": "1804", "title": "First Locomotive", "description": "Trevithick railway engine."},
        ],
        bullet_points=["Mechanized factories replaced manual craft production."],
    )
    img = slide_render_service.render_timeline_slide(spec, "Industrial Revolution")
    assert img.size == (1280, 720)


def test_slide_video_generation_with_audio_sync():
    """Verifies slide rendering to 30fps continuous video clip matching TTS duration."""
    spec = VisualSpec(
        visual_type=VisualType.MATH_EQUATION,
        subject_domain="Mathematics",
        headline="Derivatives Derivation",
    )
    audio_path, duration = tts_service.synthesize_sync("Here we examine the mathematical derivation.", language="en")
    out_video = settings.video_dir / "test_slide_clip.mp4"
    clip = slide_render_service.render_slide_video(spec, "Derivatives", audio_path, out_video, duration)

    assert clip.exists()
    assert clip.stat().st_size > 5000
    clip_dur = tts_service.get_audio_duration(clip)
    assert abs(clip_dur - duration) < 0.5


# =============================================================================
# 5. Video Stitcher & Manifest Assembly Tests
# =============================================================================
def test_video_stitcher_full_pipeline(generated_video_bundle):
    """Verifies full assembly: Avatar Intro -> Slide -> Checkpoint -> Avatar Outro into faststart MP4."""
    manifest, video_path, task_id = generated_video_bundle

    assert video_path.exists()
    assert video_path.stat().st_size > 20000
    assert manifest.lesson_id.startswith("les_")
    assert manifest.total_duration_sec > 0
    assert manifest.video_url.endswith(".mp4")

    # Verify Chapter Continuity
    chapters = manifest.chapters
    assert len(chapters) >= 3
    assert chapters[0]["start_sec"] == 0.0
    for i in range(len(chapters) - 1):
        assert abs(chapters[i]["end_sec"] - chapters[i + 1]["start_sec"]) < 0.1

    # Verify Checkpoint Pause Markers
    assert len(manifest.pause_markers) >= 1
    marker = manifest.pause_markers[0]
    assert marker.timestamp_sec > 0.0
    assert "prompt" in marker.question or "question_text" in marker.question

    # Verify Task Status
    status = video_stitcher.get_task_status(task_id)
    assert status is not None
    assert status.status == "completed"
    assert status.progress_percent == 100.0
    assert "tts_audio_synthesis" in status.stages_completed
    assert "stitching_ffmpeg" in status.stages_completed


# =============================================================================
# 6. REST API Endpoints & HTTP Range Streaming Tests
# =============================================================================
def test_api_trigger_video_generation(sample_lesson_plan):
    """Tests POST /api/v1/video/generate and POST /api/v1/lessons/generate-video."""
    resp = client.post("/api/v1/video/generate", json={"plan_id": sample_lesson_plan.plan_id})
    assert resp.status_code in [200, 202]
    data = resp.json()
    assert "task_id" in data
    assert data["plan_id"] == sample_lesson_plan.plan_id
    assert "websocket_stream_url" in data

    # Test alias route
    resp_alias = client.post("/api/v1/lessons/generate-video", json={"plan_id": sample_lesson_plan.plan_id})
    assert resp_alias.status_code in [200, 202]


def test_api_video_status_polling(generated_video_bundle):
    """Tests GET /api/v1/video/status/{task_id}."""
    _, _, task_id = generated_video_bundle
    status_resp = client.get(f"/api/v1/video/status/{task_id}")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["task_id"] == task_id
    assert status_data["status"] in ["processing", "completed"]
    assert "stages_completed" in status_data


def test_api_video_manifest_retrieval(generated_video_bundle):
    """Tests GET /api/v1/video/manifest/{video_id}."""
    manifest, _, _ = generated_video_bundle
    manifest_resp = client.get(f"/api/v1/video/manifest/{manifest.lesson_id}")
    assert manifest_resp.status_code == 200
    data = manifest_resp.json()
    assert data["lesson_id"] == manifest.lesson_id
    assert data["total_duration_sec"] > 0
    assert len(data["chapters"]) >= 3


def test_api_video_streaming_and_range_requests(generated_video_bundle):
    """Tests GET /api/v1/video/stream/{video_id} with full file and HTTP 206 Range headers."""
    manifest, _, _ = generated_video_bundle

    # 1. Full Stream (HTTP 200)
    full_resp = client.get(f"/api/v1/video/stream/{manifest.lesson_id}.mp4")
    assert full_resp.status_code == 200
    assert full_resp.headers["content-type"] == "video/mp4"
    assert "accept-ranges" in full_resp.headers

    # 2. Range Request (HTTP 206 Partial Content)
    range_resp = client.get(
        f"/api/v1/video/stream/{manifest.lesson_id}.mp4",
        headers={"Range": "bytes=0-1023"},
    )
    assert range_resp.status_code == 206
    assert range_resp.headers["content-type"] == "video/mp4"
    assert "bytes 0-1023/" in range_resp.headers["content-range"]
    assert len(range_resp.content) == 1024


def test_api_video_not_found_errors():
    """Verifies proper 404 responses for non-existent plans, tasks, manifests, and videos."""
    # Non-existent plan
    r1 = client.post("/api/v1/video/generate", json={"plan_id": "plan_non_existent_999"})
    assert r1.status_code == 404

    # Non-existent task
    r2 = client.get("/api/v1/video/status/task_fake_999")
    assert r2.status_code == 404

    # Non-existent manifest
    r3 = client.get("/api/v1/video/manifest/les_fake_999")
    assert r3.status_code == 404

    # Non-existent stream
    r4 = client.get("/api/v1/video/stream/les_fake_999.mp4")
    assert r4.status_code == 404
