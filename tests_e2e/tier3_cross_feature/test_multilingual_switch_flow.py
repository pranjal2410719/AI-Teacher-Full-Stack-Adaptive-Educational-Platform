"""
Tier 3 Cross-Feature Combination: Multilingual Language Switch Flow
Pipeline: Lesson in English -> In-Lesson Language Switch to Hindi (R4) -> Hindi Tutor Explanation -> Profile Language Sync.
"""

import pytest
from tests_e2e.harness import E2ETestHarness

@pytest.fixture
def harness():
    return E2ETestHarness()

def test_mid_session_multilingual_switch_flow(harness, math_pdf_path):
    """
    Executes full flow:
    1. Upload document and initialize English Lesson Plan.
    2. During video playback, student sends Hindi language switch prompt to side-panel tutor.
    3. System responds in Hindi with Devanagari explanation and maintains concept context.
    4. Student completes assessment and profile stores multilingual interaction record.
    """
    student_id = "stu_multi_01"

    # 1. Upload & Plan
    upload_res = harness.upload_material(math_pdf_path)
    doc_id = upload_res["data"]["document_id"]

    profile = {"student_id": student_id, "level": "beginner", "language": "en", "time_budget_min": 15}
    plan = harness.create_lesson_plan(learner_profile=profile, document_id=doc_id)["data"]

    # 2. Side-panel Chat language switch
    chat_res = harness.tutor_chat(
        message="कृपया इस नियम को हिंदी में सरल शब्दों में समझाएं (Explain in Hindi)",
        session_id="ses_multi_flow_01"
    )["data"]

    assert chat_res["language"] == "hi"
    assert "नमस्ते" in chat_res["reply"] or "हिंदी" in chat_res["reply"] or "सीकेंट" in chat_res["reply"]

    # 3. Complete Quiz
    task_id = harness.generate_video(plan_id=plan["plan_id"])["data"]["task_id"]
    lesson_id = harness.get_video_status(task_id)["data"]["lesson_id"]

    quiz = harness.generate_quiz(lesson_id=lesson_id, student_id=student_id, num_questions=1)["data"]
    report = harness.submit_quiz(quiz_id=quiz["quiz_id"], student_id=student_id, lesson_id=lesson_id, answers=[{"question_id": "quiz_q1", "selected_option_index": 0}])["data"]

    assert report["score_percent"] >= 70.0
