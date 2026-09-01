"""
Services Package for AI Teacher Core Server.
"""

from backend.app.services.llm_client import llm_client, UnifiedLLMClient
from backend.app.services.vector_store import vector_store, NumpyVectorStore, BM25Ranker
from backend.app.services.ingestion_service import ingestion_service, IngestionService
from backend.app.services.planner_service import planner_service, PlannerService
from backend.app.services.tts_service import tts_service, TTSService
from backend.app.services.avatar_service import avatar_service, AvatarService
from backend.app.services.slide_render_service import slide_render_service, SlideRenderService
from backend.app.services.video_stitcher import video_stitcher, VideoStitcher

__all__ = [
    "llm_client",
    "UnifiedLLMClient",
    "vector_store",
    "NumpyVectorStore",
    "BM25Ranker",
    "ingestion_service",
    "IngestionService",
    "planner_service",
    "PlannerService",
    "tts_service",
    "TTSService",
    "avatar_service",
    "AvatarService",
    "slide_render_service",
    "SlideRenderService",
    "video_stitcher",
    "VideoStitcher",
]
