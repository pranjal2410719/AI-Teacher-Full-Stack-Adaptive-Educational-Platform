"""
Pydantic Data Models for Milestone 4: Interactive & Adaptive Teaching Loop.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class FollowUpQuestion(BaseModel):
    """Targeted follow-up comprehension question after a diagnosed misconception."""
    question_id: str = Field(..., description="Unique ID for follow-up question")
    type: str = Field(default="short_answer", description="'short_answer' or 'mcq'")
    prompt: str = Field(..., description="Question prompt text")
    options: Optional[List[str]] = Field(default=None, description="Options if MCQ")
    correct_option_index: Optional[int] = Field(default=None, description="Index of correct option")
    hint: Optional[str] = Field(default=None, description="Helpful hint for learner")


class AnswerEvaluationRequest(BaseModel):
    """Payload for evaluating a student answer during a checkpoint question pause."""
    session_id: str = Field(..., description="Active learning session ID")
    question_id: str = Field(..., description="Checkpoint question ID")
    student_answer: str = Field(..., min_length=1, description="Student submitted text response")
    current_concept: Optional[str] = Field(default="General", description="Topic/concept being checked")
    language: Optional[str] = Field(default="en", description="Language of response ('en', 'hi')")
    context: Optional[str] = Field(default=None, description="Optional slide/lesson script context")
    expected_answer: Optional[str] = Field(default=None, description="Optional reference solution")
    learner_level: Optional[str] = Field(default="intermediate", description="'beginner', 'intermediate', 'advanced'")


class AnswerEvaluationResponse(BaseModel):
    """Pedagogical evaluation result returned to learner and video player."""
    is_correct: bool = Field(..., description="Whether answer demonstrates conceptual mastery")
    score: float = Field(..., ge=0.0, le=1.0, description="Normalized score 0.0 to 1.0")
    feedback: str = Field(..., description="Constructive pedagogical feedback")
    misconception: Optional[str] = Field(default=None, description="Root misconception identified")
    misconception_detected: Optional[str] = Field(default=None, description="Alias for misconception_detected")
    pedagogical_re_explanation: Optional[str] = Field(default=None, description="Scaffolded explanation with analogies")
    re_explanation: Optional[str] = Field(default=None, description="Alias for pedagogical_re_explanation")
    follow_up_question: Optional[FollowUpQuestion] = Field(default=None, description="Targeted follow-up question")
    can_resume_video: bool = Field(default=False, description="Whether player can resume video")
    can_proceed: Optional[bool] = Field(default=None, description="Alias for can_resume_video")
    detected_language: str = Field(default="en", description="Language of evaluation")


class LanguageSwitchRequest(BaseModel):
    """Request to switch active teaching language mid-session."""
    session_id: str = Field(..., description="Active session ID")
    target_language: str = Field(..., description="Target language code ('en', 'hi')")
    current_concept_id: Optional[str] = Field(default=None, description="Current concept or module ID")
    context: Optional[str] = Field(default=None, description="Optional conversation context")


class LanguageSwitchResponse(BaseModel):
    """Response confirming mid-session language switch."""
    session_id: str
    language: str
    translated_summary: str
    next_prompt: str
    status: str = "switched"


class TutorChatRequest(BaseModel):
    """Side-panel AI tutor conversation message."""
    session_id: Optional[str] = Field(default=None, description="Session ID for state tracking")
    message: str = Field(..., min_length=1, description="Student question or query")
    current_timestamp_sec: Optional[float] = Field(default=0.0, description="Video timestamp where query occurred")
    document_id: Optional[str] = Field(default=None, description="Uploaded document context ID")
    topic_id: Optional[str] = Field(default=None, description="Topic context ID")
    current_concept: Optional[str] = Field(default=None, description="Concept currently on screen")
    language: Optional[str] = Field(default="en", description="Preferred language")


class TutorChatResponse(BaseModel):
    """Grounded AI tutor response."""
    session_id: str
    reply: str
    language: str = "en"
    suggested_actions: List[str] = Field(default_factory=list)
    grounded_sources: List[str] = Field(default_factory=list)


class InteractionSessionState(BaseModel):
    """Persistent session state tracking student interactions."""
    session_id: str
    student_id: Optional[str] = "stu_default"
    language: str = "en"
    current_level: str = "intermediate"
    interaction_history: List[Dict[str, Any]] = Field(default_factory=list)
    diagnosed_misconceptions: List[str] = Field(default_factory=list)
    resolved_misconceptions: List[str] = Field(default_factory=list)
    active_question_id: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
