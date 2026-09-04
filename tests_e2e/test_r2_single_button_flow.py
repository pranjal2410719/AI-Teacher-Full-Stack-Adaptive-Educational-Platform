"""
R2 Acceptance Test: UI Simplicity & Single 'Generate Video' Flow
===============================================================
Authoritative Specification: ORIGINAL_REQUEST.md (lines 98-99, 113)
"The frontend must expose a single 'Generate Video' button that triggers the whole
pipeline for any uploaded document or input."
Acceptance Criteria: "The UI shows only one button labeled 'Generate Video' and no other manual steps."

This test suite verifies:
  1. Ingestion screen presents the primary action button labeled 'Generate Video'.
  2. Complete removal of the legacy multi-step button 'Proceed to Configure Learner Profile & Plan'.
  3. Direct pipeline trigger in App.tsx: 1-click execution chaining Ingestion -> Plan -> Video Generation.
  4. Backend API contract for direct video pipeline triggering.
  5. Input boundary and loading state handling for the single CTA button.
"""

import re
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.config import settings

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_SRC = PROJECT_ROOT / "frontend" / "src"
INGESTION_VIEW = FRONTEND_SRC / "components" / "Ingestion" / "IngestionView.tsx"
APP_TSX = FRONTEND_SRC / "App.tsx"
PLANNER_VIEW = FRONTEND_SRC / "components" / "Planner" / "LessonPlanEditor.tsx"


def test_r2_single_button_label_in_ingestion_view():
    """
    R2.1: Verifies that IngestionView.tsx exposes the single primary CTA button
    labeled 'Generate Video' on both Document Upload and Topic Parametric modes.
    """
    assert INGESTION_VIEW.exists(), f"IngestionView.tsx not found at {INGESTION_VIEW}"
    code = INGESTION_VIEW.read_text(encoding="utf-8")

    # Match exact visible button labels: <span>Generate Video</span>
    matches = re.findall(r"<span>Generate Video</span>", code)
    assert len(matches) >= 2, (
        f"Expected at least 2 'Generate Video' button labels (Upload + Topic), found {len(matches)}"
    )

    # Verify primary styling: yellow accent CTA
    assert "bg-yellow-400" in code, "Primary 'Generate Video' button must use vibrant yellow accent"
    assert "hover:bg-yellow-500" in code, "Generate Video button must have visible hover state"


def test_r2_legacy_multi_step_button_removed():
    """
    R2.2: Asserts that legacy multi-step button 'Proceed to Configure Learner Profile & Plan'
    is completely eradicated from the frontend codebase.
    """
    assert INGESTION_VIEW.exists()
    ingestion_code = INGESTION_VIEW.read_text(encoding="utf-8")

    assert "Proceed to Configure Learner Profile & Plan" not in ingestion_code, (
        "R2 VIOLATION: Legacy multi-step button 'Proceed to Configure Learner Profile & Plan' "
        "still exists in IngestionView.tsx"
    )

    # Check all frontend files to ensure no remaining references
    for tsx_file in FRONTEND_SRC.rglob("*.tsx"):
        content = tsx_file.read_text(encoding="utf-8")
        assert "Proceed to Configure Learner Profile & Plan" not in content, (
            f"R2 VIOLATION: Legacy multi-step button found in {tsx_file}"
        )


def test_r2_direct_pipeline_chained_handler_in_app():
    """
    R2.3: Verifies that App.tsx implements handleGenerateVideo which automatically
    chains: (1) material ingestion, (2) lesson plan creation, (3) video generation,
    and (4) async status polling into video player transition, without intermediate modals.
    """
    assert APP_TSX.exists(), f"App.tsx not found at {APP_TSX}"
    app_code = APP_TSX.read_text(encoding="utf-8")

    # Assert chained handler presence
    assert "handleGenerateVideo" in app_code, (
        "R2 VIOLATION: handleGenerateVideo handler missing in App.tsx"
    )

    # Verify automated pipeline chaining steps inside handleGenerateVideo
    assert "api.createLessonPlan" in app_code, "handleGenerateVideo must automatically call createLessonPlan"
    assert "api.generateVideo" in app_code, "handleGenerateVideo must automatically trigger generateVideo"
    assert "api.getVideoStatus" in app_code, "handleGenerateVideo must poll video status"
    assert "setCurrentTab('video')" in app_code, "handleGenerateVideo must transition directly to video tab upon completion"

    # Verify IngestionView wiring
    assert "onGenerateVideo={handleGenerateVideo}" in app_code, (
        "App.tsx must pass handleGenerateVideo directly to IngestionView component"
    )


def test_r2_button_loading_and_guard_states():
    """
    R2.4: Verifies that the single 'Generate Video' button properly guards against
    empty input and displays active loading states during generation.
    """
    code = INGESTION_VIEW.read_text(encoding="utf-8")

    # Verify disabled conditions
    assert "disabled={isGenerating}" in code, "Generate Video button must disable when generation is in progress"
    assert "disabled={isGenerating || !topicText.trim()}" in code, (
        "Topic Generate Video button must disable when topic is empty or generating"
    )

    # Verify animated spinner indicator
    assert "Loader2" in code, "Must display loading spinner while video is generating"
    assert "animate-spin" in code, "Spinner must include animate-spin Tailwind utility"
    assert "Generating Video" in code, "Button label must reflect active generation state"


def test_r2_backend_direct_pipeline_trigger_contract():
    """
    R2.5: Verifies that the backend API supports triggering the complete pipeline
    directly from material ingestion to video synthesis.
    """
    client = TestClient(app)

    # Step 1: Ingest Topic directly
    res_topic = client.post(
        "/api/v1/materials/topic",
        json={"topic": "Limits in Calculus", "subject_category": "Mathematics"},
    )
    assert res_topic.status_code == 200, f"Topic ingestion failed: {res_topic.text}"
    topic_data = res_topic.json()
    assert "topic_id" in topic_data
    topic_id = topic_data["topic_id"]

    # Step 2: Formulate Lesson Plan
    res_plan = client.post(
        "/api/v1/lessons/plan",
        json={
            "topic": topic_data["topic"],
            "topic_id": topic_id,
            "learner_profile": {
                "student_id": "stu_r2_e2e",
                "level": "intermediate",
                "language": "en",
                "time_budget_min": 10,
            },
        },
    )
    assert res_plan.status_code in [200, 201], f"Plan creation failed: {res_plan.text}"
    plan_data = res_plan.json()
    plan_id = plan_data["plan_id"]

    # Step 3: Trigger Video Generation directly
    res_video = client.post("/api/v1/video/generate", json={"plan_id": plan_id})
    assert res_video.status_code in [200, 202], f"Video generation trigger failed: {res_video.text}"
    video_data = res_video.json()
    assert "task_id" in video_data
    assert video_data["plan_id"] == plan_id

    # Step 4: Verify task status is pollable immediately
    task_id = video_data["task_id"]
    res_status = client.get(f"/api/v1/video/status/{task_id}")
    assert res_status.status_code == 200
    status_data = res_status.json()
    assert status_data["task_id"] == task_id
    assert status_data["status"] in ["pending", "processing", "completed"]
