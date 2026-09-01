"""
Tier 3 Cross-Feature Combination: Document Upload to Stitched Video Manifest Flow
Pipeline: Ingestion (R1) -> Lesson Planning (R2) -> Hybrid Video Synthesis & Manifest (R3).
"""

import pytest
from tests_e2e.harness import E2ETestHarness

@pytest.fixture
def harness():
    return E2ETestHarness()

def test_full_pipeline_doc_to_video_manifest(harness, math_pdf_path):
    """
    Executes full pipeline:
    1. Upload Calculus PDF.
    2. Create a 15-minute Intermediate Lesson Plan.
    3. Trigger Video Generation.
    4. Fetch and validate Video Manifest containing chapters, slide visuals, and pause checkpoints.
    """
    # 1. Ingest PDF
    upload_res = harness.upload_material(math_pdf_path)
    assert upload_res["status_code"] == 200
    doc_id = upload_res["data"]["document_id"]

    # 2. Plan Lesson
    profile = {
        "student_id": "stu_cross_01",
        "level": "intermediate",
        "language": "en",
        "time_budget_min": 15,
        "learning_goal": "Master limits and derivatives"
    }
    plan_res = harness.create_lesson_plan(learner_profile=profile, document_id=doc_id)
    assert plan_res["status_code"] == 200
    plan_id = plan_res["data"]["plan_id"]

    # 3. Generate Video
    gen_res = harness.generate_video(plan_id=plan_id, resolution="720p")
    assert gen_res["status_code"] in [200, 202]
    task_id = gen_res["data"]["task_id"]

    # 4. Track task & retrieve manifest
    status = harness.get_video_status(task_id)["data"]
    lesson_id = status["lesson_id"]

    manifest = harness.get_video_manifest(lesson_id)["data"]
    assert manifest["lesson_id"] == lesson_id
    assert manifest["plan_id"] == plan_id
    assert manifest["video_url"].endswith(".mp4")
    assert manifest["total_duration_sec"] > 0
    assert len(manifest["chapters"]) >= 3
    assert len(manifest["pause_markers"]) >= 1
