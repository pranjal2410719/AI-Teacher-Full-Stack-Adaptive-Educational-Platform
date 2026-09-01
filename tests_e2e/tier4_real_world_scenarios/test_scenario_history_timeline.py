"""
Tier 4 Real-World Scenario: AP World History (Industrial Revolution and Socio-Economic Impact)
Persona: Sophia (Advanced High School / AP History Student)
Goal: Analyze Key Inventions, Chronology, and Socio-Economic Transformations.
Journey: Upload TXT -> Advanced Plan with Timeline Specs -> Video -> AI Tutor Dialogue -> Essay Assessment -> Learning Report.
"""

import pytest
from tests_e2e.harness import E2ETestHarness

@pytest.fixture
def harness():
    return E2ETestHarness()

def test_scenario_history_industrial_revolution_timeline(harness, history_txt_path):
    student_id = "stu_sophia_history"

    # Step 1: Upload authentic History TXT
    upload_res = harness.upload_material(history_txt_path)
    assert upload_res["status_code"] == 200
    doc_id = upload_res["data"]["document_id"]
    assert upload_res["data"]["file_type"] == "txt"

    # Step 2: Configure learner profile for Advanced in English with 15-minute budget
    profile = {
        "student_id": student_id,
        "level": "advanced",
        "language": "en",
        "time_budget_min": 15,
        "learning_goal": "Analyze technological catalysts and socio-economic consequences"
    }
    plan_res = harness.create_lesson_plan(learner_profile=profile, document_id=doc_id)
    assert plan_res["status_code"] == 200
    plan = plan_res["data"]
    plan_id = plan["plan_id"]
    assert plan["level"] == "advanced"

    # Step 3: Video Generation & Manifest
    task_id = harness.generate_video(plan_id=plan_id)["data"]["task_id"]
    lesson_id = harness.get_video_status(task_id)["data"]["lesson_id"]
    manifest = harness.get_video_manifest(lesson_id)["data"]
    assert len(manifest["chapters"]) >= 3

    # Step 4: Engage AI Tutor on Social Legislation & Marx Critique
    chat_res = harness.tutor_chat(
        message="How did parliamentary investigative reports influence the Factory Act of 1833?",
        session_id=f"ses_{student_id}"
    )["data"]
    assert "reply" in chat_res
    assert len(chat_res["reply"]) > 10

    # Step 5: Post-Lesson Mastery Assessment
    quiz = harness.generate_quiz(lesson_id=lesson_id, student_id=student_id, num_questions=2)["data"]
    answers = [
        {"question_id": "quiz_q1", "selected_option_index": 0},
        {"question_id": "quiz_q2", "text_answer": "Watt's separate condenser transformed thermal energy into rotary power, liberating mills from waterways."}
    ]
    report = harness.submit_quiz(quiz_id=quiz["quiz_id"], student_id=student_id, lesson_id=lesson_id, answers=answers)["data"]
    assert report["score_percent"] >= 75.0
    assert len(report["recommended_next_topics"]) >= 1

    # Step 6: Verify student profile updated
    profile_data = harness.get_profile(student_id)["data"]
    assert profile_data["total_lessons_completed"] >= 1
