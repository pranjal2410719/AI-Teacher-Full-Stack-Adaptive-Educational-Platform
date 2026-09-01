"""
API Routers for Milestone 5: Assessment, Learning Profile & Recommendation Engine.
"""

from typing import List
from fastapi import APIRouter, HTTPException, status
from backend.app.models.profile import (
    QuizGenerationRequest,
    Quiz,
    QuizSubmissionRequest,
    LearningReport,
    StudentProfile,
    StudentProfileUpdateRequest,
    TopicRecommendation,
)
from backend.app.services.assessment_service import assessment_service
from backend.app.services.profile_service import profile_service

assessment_router = APIRouter(prefix="/assessment", tags=["Assessment & Quizzes"])
profile_router = APIRouter(prefix="/profile", tags=["Learner Profile & Recommendations"])


# -----------------------------------------------------------------------------
# Assessment Endpoints
# -----------------------------------------------------------------------------
@assessment_router.post("/generate", response_model=Quiz, summary="Generate Post-Lesson Quiz")
def generate_quiz_endpoint(payload: QuizGenerationRequest):
    """
    Dynamically generates a diagnostic quiz covering concepts taught in the lesson.
    """
    if not payload.lesson_id.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Lesson ID cannot be empty."
        )
    return assessment_service.generate_quiz(payload)


@assessment_router.post("/submit", response_model=LearningReport, summary="Submit Quiz for Grading")
def submit_quiz_endpoint(payload: QuizSubmissionRequest):
    """
    Grades submitted quiz answers against rubrics, computes concept mastery,
    and returns a diagnostic learning report.
    """
    if not payload.quiz_id.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Quiz ID cannot be empty."
        )
    return assessment_service.submit_and_grade_quiz(payload)


@assessment_router.get("/report/{submission_id}", response_model=LearningReport, summary="Get Learning Report")
def get_learning_report_endpoint(submission_id: str):
    """
    Retrieves a previously generated learning report by submission ID.
    """
    report = assessment_service.get_report(submission_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Learning report '{submission_id}' not found."
        )
    return report


# -----------------------------------------------------------------------------
# Profile & Recommendation Endpoints
# -----------------------------------------------------------------------------
@profile_router.get("/{student_id}", response_model=StudentProfile, summary="Get Student Profile")
def get_student_profile_endpoint(student_id: str):
    """
    Retrieves the persistent learning profile, mastery statistics, and weak areas for a student.
    """
    return profile_service.get_profile(student_id)


@profile_router.put("/{student_id}", response_model=StudentProfile, summary="Update Student Profile")
def update_student_profile_endpoint(student_id: str, payload: StudentProfileUpdateRequest):
    """
    Updates learner profile preferences (language, level, name, weak areas).
    """
    return profile_service.update_profile(student_id, payload)


@profile_router.get("/{student_id}/recommendations", response_model=List[TopicRecommendation], summary="Get Recommendations")
def get_recommendations_endpoint(student_id: str):
    """
    Synthesizes adaptive next-step study roadmap and topic recommendations.
    """
    return profile_service.get_recommendations(student_id)
