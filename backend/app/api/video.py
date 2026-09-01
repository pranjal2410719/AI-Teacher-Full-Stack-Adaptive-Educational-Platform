"""
REST API Endpoints for Hybrid Video Generation, Polling, Manifest, and Range Streaming.
"""

import os
import uuid
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks, Request, Response, status
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse

from backend.app.config import settings
from backend.app.models.video import (
    VideoGenerationRequest,
    VideoGenerationTaskResponse,
    VideoGenerationStatus,
    VideoManifest,
)
from backend.app.services.planner_service import planner_service
from backend.app.services.video_stitcher import video_stitcher

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Video Generation"])


async def _run_video_generation_task(plan, request_data: VideoGenerationRequest, task_id: str):
    """Background execution worker for video generation."""
    try:
        await video_stitcher.generate_lesson_video(plan, request_data, task_id=task_id)
    except Exception as e:
        logger.exception(f"Background video generation task {task_id} failed: {e}")


# -----------------------------------------------------------------------------
# Trigger Video Generation
# -----------------------------------------------------------------------------
@router.post(
    "/video/generate",
    response_model=VideoGenerationTaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger asynchronous video generation for a lesson plan",
)
@router.post(
    "/lessons/generate-video",
    response_model=VideoGenerationTaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    include_in_schema=False,
)
async def generate_video(
    payload: VideoGenerationRequest,
    background_tasks: BackgroundTasks,
):
    """Triggers multi-stage rendering of talking avatar, concept slides, and stitched MP4 video."""
    plan = planner_service.get_plan(payload.plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson plan '{payload.plan_id}' not found. Please create a lesson plan first.",
        )

    task_id = f"task_vid_{uuid.uuid4().hex[:8]}"
    estimated_time = max(5, int(len(plan.modules) * 3))

    # Initialize task record in stitcher
    task_status = VideoGenerationStatus(
        task_id=task_id,
        plan_id=plan.plan_id,
        lesson_id=f"les_{uuid.uuid4().hex[:8]}",
        status="processing",
        progress_percent=5.0,
        current_stage="tts_audio_synthesis",
        stages_completed=[],
    )
    video_stitcher._tasks[task_id] = task_status

    # Launch background task
    background_tasks.add_task(_run_video_generation_task, plan, payload, task_id)

    return VideoGenerationTaskResponse(
        task_id=task_id,
        plan_id=payload.plan_id,
        status="processing",
        estimated_duration_sec=estimated_time,
        websocket_stream_url=f"/ws/v1/lessons/video-progress/{task_id}",
    )


# -----------------------------------------------------------------------------
# Poll Video Generation Status
# -----------------------------------------------------------------------------
@router.get(
    "/video/status/{task_id}",
    response_model=VideoGenerationStatus,
    summary="Poll status and progress of a video generation task",
)
@router.get(
    "/lessons/video-status/{task_id}",
    response_model=VideoGenerationStatus,
    include_in_schema=False,
)
async def get_video_status(task_id: str):
    """Retrieves current stage, completion percentage, and asset URLs for a task."""
    task_status = video_stitcher.get_task_status(task_id)
    if not task_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video generation task '{task_id}' not found.",
        )
    return task_status


# -----------------------------------------------------------------------------
# Fetch Video Manifest
# -----------------------------------------------------------------------------
@router.get(
    "/video/manifest/{video_id}",
    response_model=VideoManifest,
    summary="Get video manifest with chapters and pause checkpoint markers",
)
@router.get(
    "/lessons/video-manifest/{lesson_id}",
    response_model=VideoManifest,
    include_in_schema=False,
)
async def get_video_manifest(video_id: Optional[str] = None, lesson_id: Optional[str] = None):
    """Retrieves the full VideoManifest for interactive video player navigation."""
    target_id = video_id or lesson_id
    if not target_id:
        raise HTTPException(status_code=400, detail="Missing video_id or lesson_id.")

    clean_id = target_id.replace(".mp4", "")
    manifest = video_stitcher.get_manifest(clean_id)
    if not manifest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video manifest for '{target_id}' not found.",
        )
    return manifest


# -----------------------------------------------------------------------------
# Stream Video File (HTTP 206 Partial Content / Range Requests)
# -----------------------------------------------------------------------------
@router.get(
    "/video/stream/{video_id}",
    summary="Stream MP4 video file with HTTP 206 Range support",
)
@router.get(
    "/lessons/video/{video_id}",
    include_in_schema=False,
)
async def stream_video(video_id: str, request: Request):
    """
    Streams the requested MP4 video with full HTTP 206 Range header support,
    enabling fast seeking and instant playback in HTML5 video players.
    """
    clean_id = video_id.replace(".mp4", "")
    video_path = video_stitcher.get_video_path(clean_id)

    if not video_path or not video_path.exists():
        # Check clips directory as well
        clip_target = video_stitcher.clips_dir / f"{video_id}"
        if clip_target.exists():
            video_path = clip_target
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video file '{video_id}' not found.",
            )

    file_size = video_path.stat().st_size
    range_header = request.headers.get("range")

    if not range_header:
        # Full content response
        return FileResponse(
            str(video_path),
            media_type="video/mp4",
            headers={
                "Accept-Ranges": "bytes",
                "Content-Length": str(file_size),
            },
        )

    # Parse Range Header: e.g. "bytes=0-1048575" or "bytes=500-"
    try:
        h_val = range_header.strip().lower().replace("bytes=", "")
        parts = h_val.split("-")
        start = int(parts[0]) if parts[0] else 0
        end = int(parts[1]) if len(parts) > 1 and parts[1] else file_size - 1

        if start >= file_size or end >= file_size or start > end:
            return Response(
                status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
                headers={"Content-Range": f"bytes */{file_size}"},
            )

        chunk_size = (end - start) + 1

        def iter_file_chunk(path: Path, offset: int, length: int):
            with open(path, "rb") as f:
                f.seek(offset)
                remaining = length
                while remaining > 0:
                    read_bytes = min(remaining, 64 * 1024)
                    data = f.read(read_bytes)
                    if not data:
                        break
                    remaining -= len(data)
                    yield data

        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(chunk_size),
            "Content-Type": "video/mp4",
        }

        return StreamingResponse(
            iter_file_chunk(video_path, start, chunk_size),
            status_code=status.HTTP_206_PARTIAL_CONTENT,
            headers=headers,
        )

    except Exception as e:
        logger.warning(f"Error handling Range request for {video_id}: {e}")
        return FileResponse(str(video_path), media_type="video/mp4")
