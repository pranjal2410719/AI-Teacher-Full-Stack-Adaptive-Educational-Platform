"""
Pydantic Models and Data Contracts for R3 Hybrid Video Generation Pipeline.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field, field_validator


class VideoResolution(str, Enum):
    P720 = "720p"
    P1080 = "1080p"
    P480 = "480p"


class VideoStage(str, Enum):
    PENDING = "pending"
    TTS_AUDIO_SYNTHESIS = "tts_audio_synthesis"
    AVATAR_LIP_SYNC = "avatar_lip_sync"
    RENDERING_VISUAL_SLIDES = "rendering_visual_slides"
    STITCHING_FFMPEG = "stitching_ffmpeg"
    READY = "ready"
    FAILED = "failed"


class VideoGenerationRequest(BaseModel):
    """Payload to trigger asynchronous video generation for a lesson plan."""
    plan_id: str = Field(..., description="ID of the validated LessonPlan to synthesize.")
    resolution: str = Field(default="720p", description="Output video resolution: 720p or 1080p.")
    voice_preference: Optional[str] = Field(default=None, description="Preferred TTS neural voice key (e.g. 'en-US-GuyNeural', 'hi-IN-MadhurNeural').")
    avatar_engine: Optional[str] = Field(default=None, description="Avatar engine override: 'viseme_2_5d' or 'wav2lip'.")
    include_avatar_intro: bool = Field(default=True, description="Render talking avatar introduction segment.")
    include_avatar_summary: bool = Field(default=True, description="Render talking avatar summary outro segment.")
    custom_persona: Optional[str] = Field(default="professor_alex", description="Avatar character persona identifier.")

    @field_validator("plan_id")
    @classmethod
    def validate_plan_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("plan_id cannot be empty")
        return v.strip()


class VideoGenerationTaskResponse(BaseModel):
    """Immediate response returned when video generation is triggered."""
    task_id: str = Field(..., description="Unique task identifier for polling.")
    plan_id: str = Field(..., description="Target lesson plan ID.")
    status: str = Field(default="processing", description="Initial task status.")
    estimated_duration_sec: int = Field(default=15, description="Estimated total rendering time in seconds.")
    websocket_stream_url: str = Field(..., description="WebSocket endpoint for real-time progress events.")


class VideoGenerationStatus(BaseModel):
    """Detailed progress status polled by the frontend or test runner."""
    task_id: str = Field(..., description="Unique task identifier.")
    plan_id: str = Field(..., description="Target lesson plan ID.")
    lesson_id: str = Field(..., description="Resulting lesson media ID.")
    status: str = Field(..., description="Current status: processing, completed, failed, pending.")
    progress_percent: float = Field(default=0.0, ge=0.0, le=100.0, description="Overall completion percentage.")
    current_stage: str = Field(default="pending", description="Current execution stage.")
    stages_completed: List[str] = Field(default_factory=list, description="List of completed stages.")
    manifest_url: Optional[str] = Field(default=None, description="URL to fetch the finalized VideoManifest.")
    video_url: Optional[str] = Field(default=None, description="Streamable video URL.")
    error_message: Optional[str] = Field(default=None, description="Error details if generation failed.")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = Field(default=None)


class VideoSegmentMeta(BaseModel):
    """Metadata for an individual rendered video segment clip."""
    segment_id: str = Field(..., description="Unique segment identifier.")
    order: int = Field(..., description="1-indexed sequence order.")
    segment_type: str = Field(..., description="Type: avatar_intro, visual_concept, demonstration, checkpoint_question, avatar_summary.")
    title: str = Field(..., description="Segment title.")
    start_sec: float = Field(default=0.0, description="Start timestamp in stitched video.")
    end_sec: float = Field(default=0.0, description="End timestamp in stitched video.")
    duration_sec: float = Field(..., description="Duration of this segment in seconds.")
    video_file: Optional[str] = Field(default=None, description="Local path to rendered video segment clip.")
    audio_file: Optional[str] = Field(default=None, description="Local path to synthesized TTS narration audio.")
    visual_type: Optional[str] = Field(default=None, description="Slide visual style: math_equation, code_snippet, diagram, timeline.")


class VideoChapter(BaseModel):
    """Chapter entry for interactive video navigation."""
    title: str = Field(..., description="Chapter title.")
    start_sec: float = Field(..., description="Start timestamp in seconds.")
    end_sec: float = Field(..., description="End timestamp in seconds.")
    type: str = Field(..., description="Segment type.")


class CheckpointPauseMarker(BaseModel):
    """Interactive pause checkpoint where video halts for question evaluation."""
    marker_id: str = Field(..., description="Unique marker identifier.")
    checkpoint_id: Optional[str] = Field(default=None, description="Associated checkpoint ID.")
    timestamp_sec: float = Field(..., description="Exact video timestamp in seconds to trigger pause.")
    concept: Optional[str] = Field(default=None, description="Concept being assessed.")
    question: Dict[str, Any] = Field(..., description="Question payload containing prompt, type, options, etc.")


class VideoManifest(BaseModel):
    """Full pedagogical video manifest containing stream URL, chapters, and pause markers."""
    lesson_id: str = Field(..., description="Unique lesson media identifier.")
    video_id: Optional[str] = Field(default=None, description="Alias for lesson_id.")
    plan_id: str = Field(..., description="Source lesson plan ID.")
    title: str = Field(default="AI Teaching Lesson", description="Lesson title.")
    video_url: str = Field(..., description="Streamable MP4 video URL.")
    total_duration_sec: float = Field(..., description="Total video duration in seconds.")
    duration_sec: Optional[float] = Field(default=None, description="Alias for total_duration_sec.")
    language: str = Field(default="en", description="Lesson narration language code.")
    resolution: str = Field(default="1280x720", description="Video dimensions.")
    fps: int = Field(default=30, description="Frames per second.")
    chapters: List[Dict[str, Any]] = Field(default_factory=list, description="Continuous chapter timeline entries.")
    segments: List[VideoSegmentMeta] = Field(default_factory=list, description="Detailed segment metadata.")
    pause_markers: List[CheckpointPauseMarker] = Field(default_factory=list, description="Interactive pause markers for R4.")
    pause_checkpoints: List[CheckpointPauseMarker] = Field(default_factory=list, description="Alias for pause_markers.")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def model_post_init(self, __context: Any) -> None:
        if self.video_id is None:
            self.video_id = self.lesson_id
        if self.duration_sec is None:
            self.duration_sec = self.total_duration_sec
        if not self.pause_checkpoints and self.pause_markers:
            self.pause_checkpoints = self.pause_markers
        elif not self.pause_markers and self.pause_checkpoints:
            self.pause_markers = self.pause_checkpoints
