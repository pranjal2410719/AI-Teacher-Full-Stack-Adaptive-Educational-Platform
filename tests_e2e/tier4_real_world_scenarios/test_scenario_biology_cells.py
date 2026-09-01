"""
Tier 4 Real-World Scenario: High School Biology (Cell Structure and Organelles)
Persona: Marcus (High School Biology Student)
Goal: Understand Eukaryotic Organelle Functions and Energy Conversion (ATP).
Journey: Upload PPTX -> Plan with Diagram Specs -> Video -> Pause Checkpoint on Mitochondria -> Quiz -> Learning Report.
"""

import pytest
from tests_e2e.harness import E2ETestHarness

@pytest.fixture
def harness():
    return E2ETestHarness()

def test_scenario_biology_cell_structure_and_diagrams(harness, bio_pptx_path):
    student_id = "stu_marcus_biology"

    # Step 1: Upload authentic Biology PPTX
    upload_res = harness.upload_material(bio_pptx_path)
    assert upload_res["status_code"] == 200
    doc_id = upload_res["data"]["document_id"]
    assert upload_res["data"]["file_type"] == "pptx"

    # Step 2: Configure learner profile (Intermediate, English, 20-minute budget)
    profile = {
        "student_id": student_id,
        "level": "intermediate",
        "language": "en",
        "time_budget_min": 20,
        "learning_goal": "Understand cell organelle structure and ATP synthesis"
    }
    plan_res = harness.create_lesson_plan(learner_profile=profile, document_id=doc_id)
    assert plan_res["status_code"] == 200
    plan = plan_res["data"]
    plan_id = plan["plan_id"]
    assert plan["target_duration_sec"] == 1200

    # Verify diagram visual spec exists
    diagram_mods = [m for m in plan["modules"] if m["visual_spec"]["visual_type"] == "diagram"]
    assert len(diagram_mods) >= 1

    # Step 3: Video Generation & Manifest
    task_id = harness.generate_video(plan_id=plan_id)["data"]["task_id"]
    lesson_id = harness.get_video_status(task_id)["data"]["lesson_id"]
    manifest = harness.get_video_manifest(lesson_id)["data"]
    assert len(manifest["chapters"]) >= 3

    # Step 4: Checkpoint evaluation on cellular energy
    eval_res = harness.evaluate_answer(
        session_id=f"ses_{student_id}",
        question_id=manifest["pause_markers"][0]["question"]["question_id"],
        student_answer="Mitochondria produce ATP through aerobic cellular respiration across the cristae inner membrane.",
        concept="Mitochondrial ATP Synthesis"
    )["data"]
    assert eval_res["is_correct"] is True
    assert eval_res["can_resume_video"] is True

    # Step 5: Post-Lesson Assessment
    quiz = harness.generate_quiz(lesson_id=lesson_id, student_id=student_id, num_questions=2)["data"]
    answers = [
        {"question_id": "quiz_q1", "selected_option_index": 0},
        {"question_id": "quiz_q2", "text_answer": "Plant cells contain chloroplasts and rigid cellulose walls, whereas animal cells do not."}
    ]
    report = harness.submit_quiz(quiz_id=quiz["quiz_id"], student_id=student_id, lesson_id=lesson_id, answers=answers)["data"]
    assert report["score_percent"] >= 75.0
    assert len(report["strong_concepts"]) >= 1

    # Step 6: Verify student profile update
    profile_data = harness.get_profile(student_id)["data"]
    assert profile_data["total_lessons_completed"] >= 1
