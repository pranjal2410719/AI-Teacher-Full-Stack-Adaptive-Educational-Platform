"""
REST API Endpoints for Milestone 2: Lesson Planning & Review Engine.
Routes:
- POST /api/v1/lessons/plan: Generate personalized lesson plan
- GET /api/v1/lessons/{plan_id}: Fetch saved lesson plan
- PUT /api/v1/lessons/{plan_id}: Update / reorder / edit lesson plan
- GET /api/v1/lessons: List generated lesson plans
"""

import logging
from typing import List
from fastapi import APIRouter, HTTPException, status, Query

from backend.app.models.lesson_plan import (
    LessonPlan,
    LessonPlanCreateRequest,
    LessonPlanUpdateRequest,
    LessonPlanSummary,
)
from backend.app.services.planner_service import planner_service

logger = logging.getLogger("ai_teacher.api.lessons")

router = APIRouter(prefix="/api/v1/lessons", tags=["Lesson Planning & Review"])


@router.post(
    "/plan",
    response_model=LessonPlan,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a Personalized Lesson Plan",
    description=(
        "Synthesizes an adaptive, multi-segment lesson plan tailored to the learner's level, "
        "time budget, language, and grounding material (uploaded document or parametric topic). "
        "Includes domain-aware visual slide specifications and formative checkpoint pause questions."
    )
)
async def generate_lesson_plan(request: LessonPlanCreateRequest) -> LessonPlan:
    """Generates a personalized lesson plan."""
    try:
        plan = planner_service.create_lesson_plan(request)
        return plan
    except ValueError as ve:
        logger.warning(f"Validation error in generate_lesson_plan: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error generating lesson plan: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate lesson plan: {str(e)}"
        )


@router.get(
    "/plan/{plan_id}",
    response_model=LessonPlan,
    status_code=status.HTTP_200_OK,
    summary="Fetch Saved Lesson Plan (Route Alias)",
    description="Retrieves a previously synthesized lesson plan by plan_id."
)
@router.get(
    "/{plan_id}",
    response_model=LessonPlan,
    status_code=status.HTTP_200_OK,
    summary="Fetch Saved Lesson Plan",
    description="Retrieves a previously synthesized lesson plan by plan_id."
)
async def get_lesson_plan(plan_id: str) -> LessonPlan:
    """Retrieves a saved lesson plan."""
    clean_id = plan_id.strip()
    plan = planner_service.get_plan(clean_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson plan with ID '{clean_id}' was not found."
        )
    return plan


@router.put(
    "/plan/{plan_id}",
    response_model=LessonPlan,
    status_code=status.HTTP_200_OK,
    summary="Update or Reorder Lesson Plan (Route Alias)",
    description=(
        "Enables learners and teachers to customize, reorder segments, modify titles, "
        "or replace modules before video generation."
    )
)
@router.put(
    "/{plan_id}",
    response_model=LessonPlan,
    status_code=status.HTTP_200_OK,
    summary="Update or Reorder Lesson Plan",
    description=(
        "Enables learners and teachers to customize, reorder segments, modify titles, "
        "or replace modules before video generation."
    )
)
async def update_lesson_plan(plan_id: str, request: LessonPlanUpdateRequest) -> LessonPlan:
    """Updates or reorders segments in a lesson plan."""
    clean_id = plan_id.strip()
    try:
        updated = planner_service.update_plan(clean_id, request)
        return updated
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error updating lesson plan '{clean_id}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update lesson plan: {str(e)}"
        )


@router.get(
    "",
    response_model=List[LessonPlanSummary],
    status_code=status.HTTP_200_OK,
    summary="List All Generated Lesson Plans",
    description="Returns a list of all synthesized lesson plans with summary metadata."
)
async def list_lesson_plans() -> List[LessonPlanSummary]:
    """Lists all saved lesson plans."""
    return planner_service.list_all_plans()
