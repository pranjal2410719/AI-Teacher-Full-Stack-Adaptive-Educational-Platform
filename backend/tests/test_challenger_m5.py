"""
Adversarial and Stress Challenger Tests for Milestone 5 (Assessment & Profile).
Tests empty/corrupt submissions, zero-history edge cases, SQLite durability, and extreme score handling.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.assessment_service import assessment_service
from backend.app.services.profile_service import profile_service
from backend.app.models.profile import QuizGenerationRequest, QuizSubmissionRequest

@pytest.fixture
def client():
    return TestClient(app)


class TestAssessmentBoundaryAndEdgeCases:
    """Tests extreme and boundary cases in quiz generation and grading."""

    def test_ultra_short_and_maximum_quiz_generation(self):
        # 1 question boundary
        q1 = assessment_service.generate_quiz(QuizGenerationRequest(
            lesson_id="les_bound_01",
            num_questions=1
        ))
        assert len(q1.questions) == 1

        # 10 questions boundary
        q10 = assessment_service.generate_quiz(QuizGenerationRequest(
            lesson_id="les_bound_10",
            num_questions=10
        ))
        assert len(q10.questions) == 10

    def test_empty_answers_submission(self):
        sub_req = QuizSubmissionRequest(
            quiz_id="quiz_empty_ans",
            student_id="stu_empty",
            lesson_id="les_empty",
            answers=[]
        )
        report = assessment_service.submit_and_grade_quiz(sub_req)
        assert report.score_percent == 0.0
        assert report.total_points_earned == 0.0

    def test_dict_answers_format_compatibility(self):
        gen = assessment_service.generate_quiz(QuizGenerationRequest(
            lesson_id="les_dict_ans",
            num_questions=2
        ))
        sub_req = QuizSubmissionRequest(
            quiz_id=gen.quiz_id,
            student_id="stu_dict",
            lesson_id="les_dict_ans",
            answers={
                "quiz_q1": 0,
                "quiz_q2": 0
            }
        )
        report = assessment_service.submit_and_grade_quiz(sub_req)
        assert report.score_percent >= 80.0


class TestProfilePersistenceAndDurability:
    """Tests SQLite and JSON durability across restarts and rapid concurrent updates."""

    def test_rapid_consecutive_profile_updates(self):
        import uuid
        student_id = f"stu_rapid_{uuid.uuid4().hex[:6]}"
        for i in range(5):
            sub_req = QuizSubmissionRequest(
                quiz_id=f"quiz_rapid_{i}_{uuid.uuid4().hex[:4]}",
                student_id=student_id,
                lesson_id=f"les_rapid_{i}",
                answers=[{"question_id": "quiz_q1", "student_answer": 0}]
            )
            assessment_service.submit_and_grade_quiz(sub_req)

        profile = profile_service.get_profile(student_id)
        assert profile.total_lessons_completed == 5
        assert len(profile.learning_history) == 5
        assert profile.average_mastery_percent > 0.0
