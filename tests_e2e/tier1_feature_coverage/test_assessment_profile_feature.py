"""
Tier 1 Feature Coverage: R5 Assessment & Profile Engine
Covers >= 5 discrete tests:
1. test_dynamic_quiz_generation_for_lesson
2. test_quiz_submission_and_rubric_scoring
3. test_learning_report_strengths_and_weaknesses
4. test_persistent_student_profile_update
5. test_next_step_recommendation_engine
6. test_new_guest_student_profile_default
"""

import pytest
from tests_e2e.harness import E2ETestHarness

@pytest.fixture
def harness():
    return E2ETestHarness()

def test_dynamic_quiz_generation_for_lesson(harness):
    """Verifies generating dynamic multi-format post-lesson quiz."""
    res = harness.generate_quiz(
        lesson_id="les_e2e_quiz_01",
        student_id="stu_e2e_01",
        num_questions=4
    )
    assert res["status_code"] == 200, f"Generate quiz failed: {res['data']}"
    quiz = res["data"]
    assert "quiz_id" in quiz
    assert quiz["lesson_id"] == "les_e2e_quiz_01"
    assert len(quiz["questions"]) == 4
    
    # Check question types
    types = [q["type"] for q in quiz["questions"]]
    assert "mcq" in types
    assert "short_answer" in types

def test_quiz_submission_and_rubric_scoring(harness):
    """Verifies submitting quiz answers and receiving score percentage."""
    quiz = harness.generate_quiz(lesson_id="les_calc_01", student_id="stu_e2e_02", num_questions=2)["data"]
    quiz_id = quiz["quiz_id"]

    answers = [
        {"question_id": "quiz_q1", "selected_option_index": 0},
        {"question_id": "quiz_q2", "text_answer": "Limit exists when one-sided limits are equal."}
    ]

    res = harness.submit_quiz(
        quiz_id=quiz_id,
        student_id="stu_e2e_02",
        lesson_id="les_calc_01",
        answers=answers
    )
    assert res["status_code"] == 200, f"Submit quiz failed: {res['data']}"
    report = res["data"]
    assert "submission_id" in report
    assert report["score_percent"] >= 70.0
    assert report["total_points_earned"] > 0

def test_learning_report_strengths_and_weaknesses(harness):
    """Verifies diagnostic learning report identifies strong and weak concepts."""
    quiz_id = harness.generate_quiz(lesson_id="les_calc_02", student_id="stu_e2e_03")["data"]["quiz_id"]
    answers = [{"question_id": "quiz_q1", "selected_option_index": 0}]

    report = harness.submit_quiz(quiz_id=quiz_id, student_id="stu_e2e_03", lesson_id="les_calc_02", answers=answers)["data"]
    assert "strong_concepts" in report
    assert "weak_concepts" in report
    assert len(report["strong_concepts"]) >= 1
    assert "misconceptions_resolved" in report
    assert "recommended_revision" in report

def test_persistent_student_profile_update(harness):
    """Verifies that submitting a quiz updates the student's persistent profile."""
    student_id = "stu_persistent_01"
    quiz_id = harness.generate_quiz(lesson_id="les_calc_03", student_id=student_id)["data"]["quiz_id"]
    harness.submit_quiz(quiz_id=quiz_id, student_id=student_id, lesson_id="les_calc_03", answers=[{"question_id": "quiz_q1", "selected_option_index": 0}])

    profile_res = harness.get_profile(student_id)
    assert profile_res["status_code"] == 200
    profile = profile_res["data"]
    assert profile["student_id"] == student_id
    assert profile["total_lessons_completed"] >= 1
    assert profile["average_mastery_percent"] > 0
    assert len(profile["learning_history"]) >= 1

def test_next_step_recommendation_engine(harness):
    """Verifies actionable next-step topic recommendations in the post-lesson report."""
    quiz_id = harness.generate_quiz(lesson_id="les_calc_04", student_id="stu_e2e_04")["data"]["quiz_id"]
    report = harness.submit_quiz(quiz_id=quiz_id, student_id="stu_e2e_04", lesson_id="les_calc_04", answers=[{"question_id": "quiz_q1", "selected_option_index": 0}])["data"]
    
    recs = report["recommended_next_topics"]
    assert isinstance(recs, list)
    assert len(recs) >= 1
    assert "topic" in recs[0]
    assert "level" in recs[0]

def test_new_guest_student_profile_default(harness):
    """Verifies querying a non-existent student ID returns a valid guest profile."""
    res = harness.get_profile("stu_brand_new_guest_999")
    assert res["status_code"] == 200
    profile = res["data"]
    assert profile["student_id"] == "stu_brand_new_guest_999"
    assert profile["total_lessons_completed"] == 0
    assert profile["average_mastery_percent"] == 0.0
