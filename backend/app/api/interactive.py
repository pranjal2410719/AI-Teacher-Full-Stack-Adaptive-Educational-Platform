"""
API Router for Milestone 4: Interactive & Adaptive Teaching Loop.
"""

from fastapi import APIRouter, HTTPException, status
from backend.app.models.interaction import (
    AnswerEvaluationRequest,
    AnswerEvaluationResponse,
    LanguageSwitchRequest,
    LanguageSwitchResponse,
    TutorChatRequest,
    TutorChatResponse,
    InteractionSessionState,
)
from backend.app.services.interaction_service import interaction_service

router = APIRouter(prefix="/interactive", tags=["Interactive Teaching Loop"])


@router.post("/evaluate", response_model=AnswerEvaluationResponse, summary="Evaluate Checkpoint Answer")
def evaluate_checkpoint_answer(payload: AnswerEvaluationRequest):
    """
    Evaluates student answer submitted during an in-video checkpoint pause,
    diagnoses root misconceptions, produces scaffolded re-explanations, and generates follow-up checks.
    """
    if not payload.student_answer.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Student answer cannot be empty."
        )
    return interaction_service.evaluate_student_answer(payload)


@router.post("/chat", response_model=TutorChatResponse, summary="Side-Panel AI Tutor Chat")
def side_panel_tutor_chat(payload: TutorChatRequest):
    """
    Provides real-time, RAG-grounded contextual Q&A for unscripted student questions during video viewing.
    """
    if not payload.message.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Message cannot be empty."
        )
    return interaction_service.tutor_chat(payload)


@router.post("/switch-language", response_model=LanguageSwitchResponse, summary="Mid-Session Multilingual Switch")
def switch_session_language(payload: LanguageSwitchRequest):
    """
    Switches active teaching language mid-session while preserving conversational and misconception history.
    """
    if not payload.target_language.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Target language cannot be empty."
        )
    return interaction_service.switch_session_language(payload)


@router.get("/session/{session_id}", response_model=InteractionSessionState, summary="Get Session State")
def get_session_state(session_id: str):
    """
    Retrieves interaction history and active misconception status for a session.
    """
    return interaction_service.get_or_create_session(session_id)
