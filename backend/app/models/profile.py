"""
Pydantic Data Models for Milestone 5: Assessment, Learning Profile & Recommendation Engine.
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class QuizQuestion(BaseModel):
    """A single diagnostic question in a post-lesson assessment."""
    question_id: str = Field(..., description="Unique ID for quiz question")
    type: str = Field(default="mcq", description="'mcq' or 'short_answer'")
    prompt: str = Field(..., description="The question text")
    options: Optional[List[str]] = Field(default=None, description="Answer choices if MCQ")
    correct_option_index: Optional[int] = Field(default=None, description="0-based index of correct option")
    correct_answer_text: Optional[str] = Field(default=None, description="Reference answer for short answer")
    concept: str = Field(default="General", description="Concept or learning objective tested")
    points: int = Field(default=1, description="Point value of question")
    explanation: Optional[str] = Field(default=None, description="Pedagogical explanation of solution")


class QuizGenerationRequest(BaseModel):
    """Payload to dynamically synthesize a post-lesson assessment."""
    lesson_id: str = Field(..., description="Lesson or plan ID")
    student_id: Optional[str] = Field(default="stu_default", description="Student ID")
    num_questions: Optional[int] = Field(default=3, ge=1, le=20, description="Number of questions to generate")
    focus_concepts: Optional[List[str]] = Field(default=None, description="Optional concepts to emphasize")


class Quiz(BaseModel):
    """Generated diagnostic assessment."""
    quiz_id: str
    lesson_id: str
    student_id: str
    title: str
    questions: List[QuizQuestion]
    total_points: int = Field(default=3)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class QuizSubmissionRequest(BaseModel):
    """Payload submitting student responses for rubric grading."""
    quiz_id: str
    student_id: Optional[str] = Field(default="stu_default")
    lesson_id: Optional[str] = Field(default="les_default")
    answers: Union[List[Dict[str, Any]], Dict[str, Any]] = Field(..., description="Submitted answers list or dict")


class TopicRecommendation(BaseModel):
    """Personalized next topic recommendation."""
    topic: str
    level: str = "intermediate"
    rationale: Optional[str] = None
    prerequisite_concepts: List[str] = Field(default_factory=list)


class LearningReport(BaseModel):
    """Diagnostic post-lesson performance report."""
    submission_id: str
    quiz_id: str
    student_id: str
    lesson_id: str
    score_percent: float = Field(..., ge=0.0, le=100.0)
    total_points_earned: float
    total_points_possible: float
    strong_concepts: List[str] = Field(default_factory=list)
    weak_concepts: List[str] = Field(default_factory=list)
    misconceptions_resolved: List[str] = Field(default_factory=list)
    misconceptions_identified: List[str] = Field(default_factory=list)
    recommended_revision: Optional[str] = None
    recommended_next_topics: List[Dict[str, Any]] = Field(default_factory=list)
    suggested_next_topics: List[str] = Field(default_factory=list)
    learning_report_summary: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class StudentProfile(BaseModel):
    """Persistent student learning profile and analytics record."""
    student_id: str
    name: str = "Learner"
    preferred_language: str = "en"
    preferred_level: str = "intermediate"
    total_lessons_completed: int = 0
    average_mastery_percent: float = 0.0
    mastery_by_subject: Dict[str, float] = Field(default_factory=dict)
    concept_mastery: Dict[str, float] = Field(default_factory=dict)
    known_weak_areas: List[str] = Field(default_factory=list)
    weak_areas: List[str] = Field(default_factory=list)
    learning_history: List[Dict[str, Any]] = Field(default_factory=list)
    completed_lessons: List[str] = Field(default_factory=list)
    total_time_spent_min: int = 0
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class StudentProfileUpdateRequest(BaseModel):
    """Payload to update student profile settings."""
    name: Optional[str] = None
    preferred_language: Optional[str] = None
    preferred_level: Optional[str] = None
    known_weak_areas: Optional[List[str]] = None
