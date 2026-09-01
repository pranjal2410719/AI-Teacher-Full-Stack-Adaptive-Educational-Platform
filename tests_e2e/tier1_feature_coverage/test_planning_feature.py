"""
Tier 1 Feature Coverage: R2 Lesson Planning
Covers >= 5 discrete tests:
1. test_lesson_plan_generation_from_document
2. test_lesson_plan_generation_from_topic
3. test_duration_scaling_short_vs_long
4. test_learner_level_adaptation_beginner_vs_advanced
5. test_visual_slide_specifications_generation
6. test_lesson_plan_crud_and_editing
"""

import pytest
from tests_e2e.harness import E2ETestHarness

@pytest.fixture
def harness():
    return E2ETestHarness()

def test_lesson_plan_generation_from_document(harness, math_pdf_path):
    """Verifies lesson plan generation grounded in uploaded document."""
    upload_res = harness.upload_material(math_pdf_path)
    assert upload_res["status_code"] == 200
    doc_id = upload_res["data"]["document_id"]

    profile = {
        "student_id": "stu_math_01",
        "level": "intermediate",
        "language": "en",
        "time_budget_min": 15,
        "learning_goal": "Understand derivatives via limits"
    }

    res = harness.create_lesson_plan(learner_profile=profile, document_id=doc_id)
    assert res["status_code"] == 200, f"Plan generation failed: {res['data']}"
    plan = res["data"]
    assert "plan_id" in plan
    assert plan["target_duration_sec"] == 15 * 60
    assert plan["level"] == "intermediate"
    assert len(plan["modules"]) >= 3
    
    # Check intro and summary segments
    assert plan["modules"][0]["segment_type"] == "avatar_intro"
    assert plan["modules"][-1]["segment_type"] == "avatar_summary"

def test_lesson_plan_generation_from_topic(harness):
    """Verifies lesson plan generation from a parametric topic."""
    topic_res = harness.ingest_topic(topic="Binary Search Trees", subject_category="Computer Science")
    assert topic_res["status_code"] == 200
    top_id = topic_res["data"]["topic_id"]

    profile = {
        "student_id": "stu_cs_01",
        "level": "beginner",
        "language": "en",
        "time_budget_min": 10
    }

    res = harness.create_lesson_plan(learner_profile=profile, topic_id=top_id)
    assert res["status_code"] == 200
    plan = res["data"]
    assert "plan_id" in plan
    assert "bst" in plan["title"].lower() or "binary" in plan["title"].lower() or "trees" in plan["title"].lower()

def test_duration_scaling_short_vs_long(harness):
    """Verifies that a 5-min budget produces a shorter plan than a 60-min budget."""
    short_profile = {"student_id": "stu_01", "level": "intermediate", "language": "en", "time_budget_min": 5}
    long_profile = {"student_id": "stu_02", "level": "intermediate", "language": "en", "time_budget_min": 60}

    short_plan = harness.create_lesson_plan(learner_profile=short_profile)["data"]
    long_plan = harness.create_lesson_plan(learner_profile=long_profile)["data"]

    assert short_plan["target_duration_sec"] == 300
    assert long_plan["target_duration_sec"] == 3600
    assert len(short_plan["modules"]) < len(long_plan["modules"])

def test_learner_level_adaptation_beginner_vs_advanced(harness):
    """Verifies distinct plan configurations for beginner vs advanced profiles."""
    beg_profile = {"student_id": "stu_b", "level": "beginner", "language": "hi", "time_budget_min": 15}
    adv_profile = {"student_id": "stu_a", "level": "advanced", "language": "en", "time_budget_min": 15}

    beg_plan = harness.create_lesson_plan(learner_profile=beg_profile)["data"]
    adv_plan = harness.create_lesson_plan(learner_profile=adv_profile)["data"]

    assert beg_plan["level"] == "beginner"
    assert beg_plan["language"] == "hi"
    assert adv_plan["level"] == "advanced"
    assert adv_plan["language"] == "en"

def test_visual_slide_specifications_generation(harness, cs_docx_path):
    """Verifies visual slide specs (equations, code, diagrams) in generated modules."""
    upload_res = harness.upload_material(cs_docx_path)
    doc_id = upload_res["data"]["document_id"]

    profile = {"student_id": "stu_cs_02", "level": "intermediate", "language": "en", "time_budget_min": 15}
    plan = harness.create_lesson_plan(learner_profile=profile, document_id=doc_id)["data"]

    # Check for visual_spec in concept modules
    concept_modules = [m for m in plan["modules"] if m["segment_type"] == "visual_concept"]
    assert len(concept_modules) >= 1
    spec = concept_modules[0]["visual_spec"]
    assert "visual_type" in spec
    assert "headline" in spec
    assert "bullet_points" in spec

def test_lesson_plan_crud_and_editing(harness):
    """Verifies fetching and editing lesson plan before video synthesis."""
    profile = {"student_id": "stu_edit", "level": "intermediate", "language": "en", "time_budget_min": 15}
    plan = harness.create_lesson_plan(learner_profile=profile)["data"]
    plan_id = plan["plan_id"]

    # Fetch plan
    get_res = harness.get_lesson_plan(plan_id)
    assert get_res["status_code"] == 200
    assert get_res["data"]["plan_id"] == plan_id

    # Update plan title
    update_res = harness.update_lesson_plan(plan_id, {"title": "Custom Edited Calculus Masterclass"})
    assert update_res["status_code"] == 200
    assert update_res["data"]["title"] == "Custom Edited Calculus Masterclass"
