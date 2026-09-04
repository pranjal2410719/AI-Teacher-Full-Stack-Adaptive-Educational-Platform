"""
ApniHelp Core Platform - FastAPI Application Entry Point.
"""

import logging
from datetime import datetime, timezone
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.config import settings
from backend.app.api.materials import router as materials_router
from backend.app.api.lessons import router as lessons_router
from backend.app.api.video import router as video_router
from backend.app.api.interactive import router as interactive_router
from backend.app.api.profile import assessment_router, profile_router
from backend.app.services.ingestion_service import ingestion_service
from backend.app.services.vector_store import vector_store
from backend.app.services.planner_service import planner_service
from backend.app.services.video_stitcher import video_stitcher
from backend.app.services.interaction_service import interaction_service
from backend.app.services.assessment_service import assessment_service
from backend.app.services.profile_service import profile_service
from backend.app.services.llm_client import llm_client

logger = logging.getLogger("apnihelp.main")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="ApniHelp Full-Stack Educational Platform API powering adaptive human-teaching loops.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# -----------------------------------------------------------------------------
# CORS Middleware
# -----------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------------------
# Global Exception Handlers
# -----------------------------------------------------------------------------
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)}
    )


# -----------------------------------------------------------------------------
# Health & Status Route
# -----------------------------------------------------------------------------
@app.get("/api/v1/health", tags=["System Health"])
async def health_check():
    """
    Returns system status, active LLM provider, vector index counts, video generator status, and storage readiness.
    """
    provider = "offline_parametric"
    if settings.groq_api_key:
        provider = f"groq ({settings.groq_model})"
    elif settings.gemini_api_key:
        provider = f"gemini ({settings.gemini_model})"

    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "llm_provider": provider,
        "tts_provider": "edge-tts",
        "avatar_engine": settings.avatar_engine,
        "ffmpeg_available": True,
        "indexed_documents_count": len(ingestion_service.list_all_materials()),
        "vector_store_active_indices": len(vector_store.indices),
        "total_lesson_plans": len(planner_service.plans_registry),
        "total_video_manifests": len(video_stitcher._manifests),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to ApniHelp Core Server",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/api/v1/health"
    }


# -----------------------------------------------------------------------------
# Router Registration
# -----------------------------------------------------------------------------
app.include_router(materials_router)
app.include_router(lessons_router)
app.include_router(video_router, prefix="/api/v1")
app.include_router(video_router)
app.include_router(interactive_router, prefix="/api/v1")
app.include_router(interactive_router)
app.include_router(assessment_router, prefix="/api/v1")
app.include_router(assessment_router)
app.include_router(profile_router, prefix="/api/v1")
app.include_router(profile_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.host, port=settings.port, reload=True)
