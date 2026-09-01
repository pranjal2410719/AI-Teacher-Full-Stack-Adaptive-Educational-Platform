"""
Tier 4 Real-World Scenario: High School Mathematics in Hindi (Calculus Limits)
Persona: Aarav (High School Student)
Goal: Master the formal concept of Limits and Derivatives in Hindi.
Journey: Upload PDF -> Hindi Lesson Plan -> Video Generation -> Hindi In-Lesson Checkpoint -> Quiz -> Profile Update.
"""

import pytest
from tests_e2e.harness import E2ETestHarness

@pytest.fixture
def harness():
    return E2ETestHarness()

def test_scenario_high_school_math_in_hindi(harness, math_pdf_path):
    student_id = "stu_aarav_hindi_math"

    # Step 1: Upload authentic Calculus limits PDF
    upload_res = harness.upload_material(math_pdf_path)
    assert upload_res["status_code"] == 200
    doc_id = upload_res["data"]["document_id"]
    assert upload_res["data"]["file_type"] == "pdf"

    # Step 2: Configure learner profile for Beginner in Hindi with 15-minute budget
    profile = {
        "student_id": student_id,
        "level": "beginner",
        "language": "hi",
        "time_budget_min": 15,
        "prior_knowledge": "Basic algebra and graphs",
        "learning_goal": "Understand limits intuitively and mathematically in Hindi"
    }
    plan_res = harness.create_lesson_plan(learner_profile=profile, document_id=doc_id)
    assert plan_res["status_code"] == 200
    plan = plan_res["data"]
    plan_id = plan["plan_id"]
    assert plan["language"] == "hi"
    assert plan["target_duration_sec"] == 900
    assert len(plan["modules"]) >= 3

    # Verify LaTeX equation visual spec
    equation_mods = [m for m in plan["modules"] if m["visual_spec"]["visual_type"] == "math_equation"]
    assert len(equation_mods) >= 1
    assert len(equation_mods[0]["visual_spec"]["latex_equations"]) >= 1

    # Step 3: Trigger Video Generation with Hindi Voice
    gen_res = harness.generate_video(plan_id=plan_id, voice_preference="hi-IN-MadhurNeural")
    assert gen_res["status_code"] in [200, 202]
    task_id = gen_res["data"]["task_id"]

    # Step 4: Verify Video Manifest
    task_status = harness.get_video_status(task_id)["data"]
    lesson_id = task_status["lesson_id"]
    manifest = harness.get_video_manifest(lesson_id)["data"]
    assert manifest["language"] == "hi"
    assert len(manifest["pause_markers"]) >= 1

    # Step 5: In-Video Checkpoint Interaction in Hindi
    checkpoint_eval = harness.evaluate_answer(
        session_id=f"ses_{student_id}",
        question_id=manifest["pause_markers"][0]["question"]["question_id"],
        student_answer="दोनो तरफ की सीमाएं बराबर होनी चाहिए। (Left and right limits must be equal)",
        concept="One-sided Limits",
        language="hi"
    )["data"]
    assert checkpoint_eval["is_correct"] is True
    assert checkpoint_eval["can_resume_video"] is True

    # Step 6: Post-Lesson Mastery Quiz
    quiz = harness.generate_quiz(lesson_id=lesson_id, student_id=student_id, num_questions=3)["data"]
    quiz_id = quiz["quiz_id"]
    answers = [
        {"question_id": "quiz_q1", "selected_option_index": 0},
        {"question_id": "quiz_q2", "text_answer": "सीमा का अर्थ है जब x किसी बिंदु के अत्यंत समीप पहुंचता है।"},
        {"question_id": "quiz_q3", "selected_option_index": 0}
    ]
    report = harness.submit_quiz(quiz_id=quiz_id, student_id=student_id, lesson_id=lesson_id, answers=answers)["data"]
    assert report["score_percent"] >= 80.0
    assert len(report["strong_concepts"]) >= 1

    # Step 7: Profile Persistence & Recommendations
    final_profile = harness.get_profile(student_id)["data"]
    assert final_profile["student_id"] == student_id
    assert final_profile["total_lessons_completed"] >= 1
    assert len(report["recommended_next_topics"]) >= 1
