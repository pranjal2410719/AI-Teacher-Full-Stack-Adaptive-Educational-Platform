"""
Tier 3 Cross-Feature Combination: Topic Ingestion to Post-Quiz & Persistent Profile Cycle
Pipeline: Topic Ingestion (R1) -> Planning (R2) -> Post-Quiz Generation (R5) -> Grading & Profile Persistence (R5).
"""

import pytest
from tests_e2e.harness import E2ETestHarness

@pytest.fixture
def harness():
    return E2ETestHarness()

def test_topic_to_quiz_and_profile_cycle(harness):
    """
    Executes full pipeline:
    1. Ingest CS Topic "Binary Search Trees in Python".
    2. Create 10-minute Intermediate Lesson Plan.
    3. Generate Post-Lesson Mastery Quiz.
    4. Submit Quiz Answers.
    5. Verify Learning Report and Persistent Student Profile Update.
    """
    student_id = "stu_cs_cycle_01"

    # 1. Ingest Topic
    top_res = harness.ingest_topic(topic="Binary Search Trees in Python", subject_category="Computer Science")
    assert top_res["status_code"] == 200
    topic_id = top_res["data"]["topic_id"]

    # 2. Plan Lesson
    profile = {"student_id": student_id, "level": "intermediate", "language": "en", "time_budget_min": 10}
    plan = harness.create_lesson_plan(learner_profile=profile, topic_id=topic_id)["data"]
    plan_id = plan["plan_id"]

    # 3. Generate Video & Lesson
    task_id = harness.generate_video(plan_id=plan_id)["data"]["task_id"]
    lesson_id = harness.get_video_status(task_id)["data"]["lesson_id"]

    # 4. Generate & Submit Quiz
    quiz = harness.generate_quiz(lesson_id=lesson_id, student_id=student_id, num_questions=2)["data"]
    quiz_id = quiz["quiz_id"]

    answers = [
        {"question_id": "quiz_q1", "selected_option_index": 0},
        {"question_id": "quiz_q2", "text_answer": "Binary Search Trees guarantee O(log n) average time complexity."}
    ]
    report = harness.submit_quiz(quiz_id=quiz_id, student_id=student_id, lesson_id=lesson_id, answers=answers)["data"]

    assert report["score_percent"] >= 70.0
    assert len(report["strong_concepts"]) >= 1

    # 5. Check Persistent Profile
    user_profile = harness.get_profile(student_id)["data"]
    assert user_profile["student_id"] == student_id
    assert user_profile["total_lessons_completed"] >= 1
    assert user_profile["average_mastery_percent"] >= 70.0
