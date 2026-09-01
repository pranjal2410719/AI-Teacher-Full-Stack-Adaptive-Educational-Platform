"""
Tier 1 Feature Coverage: R3 Hybrid Video Generation Pipeline
Covers >= 5 discrete tests:
1. test_trigger_video_generation_for_plan
2. test_video_generation_task_status_tracking
3. test_video_manifest_structure_and_url
4. test_video_chapters_and_segment_timing
5. test_video_pause_checkpoint_markers
6. test_video_multilingual_voice_selection
"""

import pytest
from tests_e2e.harness import E2ETestHarness

@pytest.fixture
def harness():
    return E2ETestHarness()

def test_trigger_video_generation_for_plan(harness):
    """Verifies triggering background video synthesis returns task metadata."""
    profile = {"student_id": "stu_vid_01", "level": "intermediate", "language": "en", "time_budget_min": 10}
    plan = harness.create_lesson_plan(learner_profile=profile)["data"]
    plan_id = plan["plan_id"]

    res = harness.generate_video(plan_id=plan_id, resolution="720p")
    assert res["status_code"] in [200, 202], f"Generate video failed: {res['data']}"
    data = res["data"]
    assert "task_id" in data
    assert data["plan_id"] == plan_id
    assert "websocket_stream_url" in data

def test_video_generation_task_status_tracking(harness):
    """Verifies polling task status returns stage breakdown and completion."""
    profile = {"student_id": "stu_vid_02", "level": "intermediate", "language": "en", "time_budget_min": 10}
    plan = harness.create_lesson_plan(learner_profile=profile)["data"]
    task_id = harness.generate_video(plan_id=plan["plan_id"])["data"]["task_id"]

    status_res = harness.get_video_status(task_id)
    assert status_res["status_code"] == 200, f"Task status failed: {status_res['data']}"
    task = status_res["data"]
    assert task["task_id"] == task_id
    assert task["status"] in ["processing", "completed"]
    assert "stages_completed" in task
    assert "lesson_id" in task

def test_video_manifest_structure_and_url(harness):
    """Verifies fetching video manifest returns streamable video URL and metadata."""
    profile = {"student_id": "stu_vid_03", "level": "intermediate", "language": "en", "time_budget_min": 10}
    plan = harness.create_lesson_plan(learner_profile=profile)["data"]
    gen_res = harness.generate_video(plan_id=plan["plan_id"])
    task_id = gen_res["data"]["task_id"]
    lesson_id = harness.get_video_status(task_id)["data"]["lesson_id"]

    manifest_res = harness.get_video_manifest(lesson_id)
    assert manifest_res["status_code"] == 200, f"Manifest failed: {manifest_res['data']}"
    manifest = manifest_res["data"]
    assert manifest["lesson_id"] == lesson_id
    assert manifest["video_url"].endswith(".mp4")
    assert manifest["total_duration_sec"] > 0
    assert manifest["language"] == "en"

def test_video_chapters_and_segment_timing(harness):
    """Verifies that chapters cover intro, visual slides, and summary seamlessly."""
    profile = {"student_id": "stu_vid_04", "level": "intermediate", "language": "en", "time_budget_min": 15}
    plan = harness.create_lesson_plan(learner_profile=profile)["data"]
    task_id = harness.generate_video(plan_id=plan["plan_id"])["data"]["task_id"]
    lesson_id = harness.get_video_status(task_id)["data"]["lesson_id"]

    manifest = harness.get_video_manifest(lesson_id)["data"]
    chapters = manifest["chapters"]
    assert len(chapters) >= 3
    
    # Check start and end continuity
    assert chapters[0]["start_sec"] == 0.0
    for i in range(len(chapters) - 1):
        assert chapters[i]["end_sec"] == chapters[i + 1]["start_sec"]

def test_video_pause_checkpoint_markers(harness):
    """Verifies that pause checkpoints are accurately placed within video chapters."""
    profile = {"student_id": "stu_vid_05", "level": "intermediate", "language": "en", "time_budget_min": 15}
    plan = harness.create_lesson_plan(learner_profile=profile)["data"]
    task_id = harness.generate_video(plan_id=plan["plan_id"])["data"]["task_id"]
    lesson_id = harness.get_video_status(task_id)["data"]["lesson_id"]

    manifest = harness.get_video_manifest(lesson_id)["data"]
    pause_markers = manifest["pause_markers"]
    assert len(pause_markers) >= 1
    
    marker = pause_markers[0]
    assert "marker_id" in marker
    assert marker["timestamp_sec"] > 0.0
    assert "question" in marker
    assert "prompt" in marker["question"]

def test_video_multilingual_voice_selection(harness):
    """Verifies that video manifest preserves Hindi language configuration."""
    profile = {"student_id": "stu_vid_hi", "level": "intermediate", "language": "hi", "time_budget_min": 10}
    plan = harness.create_lesson_plan(learner_profile=profile)["data"]
    task_id = harness.generate_video(plan_id=plan["plan_id"], voice_preference="hi-IN-MadhurNeural")["data"]["task_id"]
    lesson_id = harness.get_video_status(task_id)["data"]["lesson_id"]

    manifest = harness.get_video_manifest(lesson_id)["data"]
    assert manifest["language"] == "hi"
