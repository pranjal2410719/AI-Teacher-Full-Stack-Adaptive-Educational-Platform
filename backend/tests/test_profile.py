"""
Unit and Integration Tests for Milestone 5: Assessment, Learning Profile & Recommendation Engine.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.assessment_service import assessment_service
from backend.app.services.profile_service import profile_service
from backend.app.models.profile import (
    QuizGenerationRequest,
    QuizSubmissionRequest,
    StudentProfileUpdateRequest,
)

@pytest.fixture
def client():
    return TestClient(app)


def test_assessment_models_validation():
    gen_req = QuizGenerationRequest(
        lesson_id="les_test_01",
        student_id="stu_01",
        num_questions=4
    )
    assert gen_req.lesson_id == "les_test_01"
    assert gen_req.num_questions == 4


def test_dynamic_quiz_generation():
    req = QuizGenerationRequest(
        lesson_id="les_calc_limits",
        student_id="stu_calc_01",
        num_questions=3
    )
    quiz = assessment_service.generate_quiz(req)
    assert quiz.quiz_id.startswith("quiz_")
    assert len(quiz.questions) == 3
    assert quiz.total_points >= 3
    assert any(q.type == "mcq" for q in quiz.questions)
    assert any(q.type == "short_answer" for q in quiz.questions)


def test_quiz_submission_and_rubric_scoring():
    # 1. Generate quiz
    gen_req = QuizGenerationRequest(
        lesson_id="les_calc_grading",
        student_id="stu_grade_01",
        num_questions=3
    )
    quiz = assessment_service.generate_quiz(gen_req)

    # 2. Submit answers
    sub_req = QuizSubmissionRequest(
        quiz_id=quiz.quiz_id,
        student_id="stu_grade_01",
        lesson_id="les_calc_grading",
        answers=[
            {"question_id": "quiz_q1", "student_answer": 0},
            {"question_id": "quiz_q2", "student_answer": 0},
            {"question_id": "quiz_q3", "student_answer": "For every epsilon > 0 there exists a delta > 0"}
        ]
    )
    report = assessment_service.submit_and_grade_quiz(sub_req)
    assert report.submission_id.startswith("sub_")
    assert report.score_percent >= 80.0
    assert len(report.strong_concepts) >= 1
    assert len(report.recommended_next_topics) >= 1


def test_persistent_student_profile_update_and_mastery():
    import uuid
    student_id = f"stu_persistent_{uuid.uuid4().hex[:6]}"
    
    # 1. Check default profile
    initial_prof = profile_service.get_profile(student_id)
    assert initial_prof.student_id == student_id
    assert initial_prof.total_lessons_completed == 0
    assert initial_prof.average_mastery_percent == 0.0

    # 2. Complete lesson assessment
    sub_req = QuizSubmissionRequest(
        quiz_id=f"quiz_p_{uuid.uuid4().hex[:4]}",
        student_id=student_id,
        lesson_id="les_calculus_01",
        answers=[
            {"question_id": "quiz_q1", "student_answer": 0},
            {"question_id": "quiz_q2", "student_answer": 0}
        ]
    )
    report = assessment_service.submit_and_grade_quiz(sub_req)

    # 3. Verify profile updated
    updated_prof = profile_service.get_profile(student_id)
    assert updated_prof.total_lessons_completed == 1
    assert updated_prof.average_mastery_percent > 0.0
    assert "les_calculus_01" in updated_prof.completed_lessons
    assert len(updated_prof.learning_history) == 1


def test_next_step_recommendation_engine():
    student_id = "stu_recom_01"
    
    # Submit quiz with known weak area
    sub_req = QuizSubmissionRequest(
        quiz_id="quiz_rec",
        student_id=student_id,
        lesson_id="les_calculus_limits",
        answers=[{"question_id": "quiz_q1", "student_answer": 0}]
    )
    assessment_service.submit_and_grade_quiz(sub_req)

    recs = profile_service.get_recommendations(student_id)
    assert len(recs) >= 2
    assert any("Calculus" in r.topic or "Rule" in r.topic for r in recs)


def test_api_assessment_and_profile_endpoints(client):
    # 1. Generate quiz via API
    r_gen = client.post("/api/v1/assessment/generate", json={
        "lesson_id": "les_api_01",
        "student_id": "stu_api_01",
        "num_questions": 3
    })
    assert r_gen.status_code == 200
    quiz_data = r_gen.json()
    quiz_id = quiz_data["quiz_id"]
    assert len(quiz_data["questions"]) == 3

    # 2. Submit quiz via API
    r_sub = client.post("/api/v1/assessment/submit", json={
        "quiz_id": quiz_id,
        "student_id": "stu_api_01",
        "lesson_id": "les_api_01",
        "answers": [
            {"question_id": "quiz_q1", "student_answer": 0},
            {"question_id": "quiz_q2", "student_answer": 0}
        ]
    })
    assert r_sub.status_code == 200
    report_data = r_sub.json()
    sub_id = report_data["submission_id"]
    assert report_data["score_percent"] >= 75.0

    # 3. Retrieve report via API
    r_rep = client.get(f"/api/v1/assessment/report/{sub_id}")
    assert r_rep.status_code == 200
    assert r_rep.json()["submission_id"] == sub_id

    # 4. Get profile via API
    r_prof = client.get("/api/v1/profile/stu_api_01")
    assert r_prof.status_code == 200
    assert r_prof.json()["total_lessons_completed"] >= 1

    # 5. Update profile via API
    r_upd = client.put("/api/v1/profile/stu_api_01", json={
        "name": "Jane Scholar",
        "preferred_level": "advanced",
        "preferred_language": "hi"
    })
    assert r_upd.status_code == 200
    assert r_upd.json()["name"] == "Jane Scholar"
    assert r_upd.json()["preferred_level"] == "advanced"

    # 6. Get recommendations via API
    r_rec = client.get("/api/v1/profile/stu_api_01/recommendations")
    assert r_rec.status_code == 200
    assert len(r_rec.json()) >= 1


def test_api_assessment_not_found_and_errors(client):
    # Non-existent report
    r = client.get("/api/v1/assessment/report/sub_nonexistent_999")
    assert r.status_code == 404

    # Empty lesson ID
    r = client.post("/api/v1/assessment/generate", json={
        "lesson_id": "   "
    })
    assert r.status_code == 422
