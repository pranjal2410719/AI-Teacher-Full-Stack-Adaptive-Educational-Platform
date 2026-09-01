"""
Video Stitcher & Assembly Service for AI Teacher Platform.
Assembles hybrid video segments (Avatar Intro -> Subject-Aware Concept Slides -> Avatar Outro),
concatenates them via FFmpeg into a 1280x720 30fps H.264/AAC web-streamable MP4 (+faststart),
and generates comprehensive VideoManifests with continuous chapters and pause checkpoint markers.
"""

import os
import json
import uuid
import math
import logging
import asyncio
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple, Callable
from datetime import datetime, timezone

from backend.app.config import settings
from backend.app.models.lesson_plan import LessonPlan, LessonSegmentPlan
from backend.app.models.video import (
    VideoGenerationRequest,
    VideoGenerationStatus,
    VideoSegmentMeta,
    VideoChapter,
    CheckpointPauseMarker,
    VideoManifest,
    VideoStage,
)
from backend.app.services.tts_service import tts_service, TTSService
from backend.app.services.avatar_service import avatar_service, AvatarService
from backend.app.services.slide_render_service import slide_render_service, SlideRenderService

logger = logging.getLogger(__name__)


class VideoStitcher:
    """Orchestrates multi-stage hybrid video rendering, stitching, and manifest generation."""

    def __init__(
        self,
        video_dir: Optional[Path] = None,
        tts: Optional[TTSService] = None,
        avatar: Optional[AvatarService] = None,
        slide_render: Optional[SlideRenderService] = None,
    ):
        self.video_dir = Path(video_dir) if video_dir else settings.video_dir
        self.video_dir.mkdir(parents=True, exist_ok=True)
        self.tasks_dir = self.video_dir / "tasks"
        self.tasks_dir.mkdir(parents=True, exist_ok=True)
        self.manifests_dir = self.video_dir / "manifests"
        self.manifests_dir.mkdir(parents=True, exist_ok=True)
        self.clips_dir = self.video_dir / "clips"
        self.clips_dir.mkdir(parents=True, exist_ok=True)

        self.tts = tts or tts_service
        self.avatar = avatar or avatar_service
        self.slide_render = slide_render or slide_render_service
        self.ffmpeg_path = settings.ffmpeg_path
        self.ffprobe_path = settings.ffprobe_path

        # In-memory caches
        self._tasks: Dict[str, VideoGenerationStatus] = {}
        self._manifests: Dict[str, VideoManifest] = {}

    def update_task_status(
        self,
        task_id: str,
        status: str,
        stage: str,
        progress_percent: float,
        stages_completed: Optional[List[str]] = None,
        manifest_url: Optional[str] = None,
        video_url: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> VideoGenerationStatus:
        """Updates and persists the task status record."""
        current = self._tasks.get(task_id)
        if not current:
            return None

        current.status = status
        current.current_stage = stage
        current.progress_percent = round(progress_percent, 1)
        if stages_completed is not None:
            current.stages_completed = stages_completed
        elif stage not in current.stages_completed and stage not in ["pending", "ready", "failed"]:
            current.stages_completed.append(stage)

        if manifest_url:
            current.manifest_url = manifest_url
        if video_url:
            current.video_url = video_url
        if error_message:
            current.error_message = error_message
        if status == "completed":
            current.completed_at = datetime.now(timezone.utc).isoformat()

        # Save to disk
        try:
            task_file = self.tasks_dir / f"{task_id}.json"
            task_file.write_text(json.dumps(current.model_dump(), indent=2))
        except Exception as e:
            logger.warning(f"Failed to persist task {task_id}: {e}")

        return current

    def get_task_status(self, task_id: str) -> Optional[VideoGenerationStatus]:
        """Retrieves task status from memory or disk cache."""
        if task_id in self._tasks:
            return self._tasks[task_id]

        task_file = self.tasks_dir / f"{task_id}.json"
        if task_file.exists():
            try:
                data = json.loads(task_file.read_text())
                status = VideoGenerationStatus(**data)
                self._tasks[task_id] = status
                return status
            except Exception as e:
                logger.warning(f"Error loading task status file {task_file}: {e}")
        return None

    def get_manifest(self, lesson_id: str) -> Optional[VideoManifest]:
        """Retrieves video manifest by lesson_id / video_id."""
        if lesson_id in self._manifests:
            return self._manifests[lesson_id]

        manifest_file = self.manifests_dir / f"{lesson_id}.json"
        if manifest_file.exists():
            try:
                data = json.loads(manifest_file.read_text())
                manifest = VideoManifest(**data)
                self._manifests[lesson_id] = manifest
                return manifest
            except Exception as e:
                logger.warning(f"Error loading manifest file {manifest_file}: {e}")
        return None

    def get_video_path(self, lesson_id: str) -> Optional[Path]:
        """Returns the local filesystem path to the stitched MP4 file."""
        # Strip any extension if given
        clean_id = lesson_id.replace(".mp4", "")
        target = self.video_dir / f"{clean_id}.mp4"
        if target.exists():
            return target
        return None

    async def generate_lesson_video(
        self,
        plan: LessonPlan,
        request: VideoGenerationRequest,
        task_id: Optional[str] = None,
    ) -> Tuple[VideoManifest, Path]:
        """
        Executes the full hybrid video rendering pipeline:
        1. TTS speech audio generation for all modules.
        2. Avatar talking head clips for intro/summary segments.
        3. Subject-aware visual slide clips for concept explanation segments.
        4. FFmpeg concatenation with -movflags +faststart.
        5. VideoManifest construction with continuous chapters and pause checkpoint markers.
        """
        lesson_id = f"les_{uuid.uuid4().hex[:8]}"
        task_id = task_id or f"task_vid_{uuid.uuid4().hex[:8]}"
        
        # Initialize task record
        task_status = VideoGenerationStatus(
            task_id=task_id,
            plan_id=plan.plan_id,
            lesson_id=lesson_id,
            status="processing",
            progress_percent=5.0,
            current_stage=VideoStage.TTS_AUDIO_SYNTHESIS.value,
            stages_completed=[],
        )
        self._tasks[task_id] = task_status

        output_video_path = self.video_dir / f"{lesson_id}.mp4"
        segment_clips: List[Path] = []
        segment_metas: List[VideoSegmentMeta] = []
        pause_markers: List[CheckpointPauseMarker] = []
        chapters: List[Dict[str, Any]] = []

        try:
            # -------------------------------------------------------------
            # Stage 1: Multilingual TTS Audio Synthesis
            # -------------------------------------------------------------
            self.update_task_status(task_id, "processing", VideoStage.TTS_AUDIO_SYNTHESIS.value, 15.0)
            logger.info(f"Task {task_id}: Stage 1 - Synthesizing TTS audio for plan {plan.plan_id}")

            audio_tracks: List[Tuple[Path, float]] = []
            for i, module in enumerate(plan.modules):
                script_text = (module.script or f"Section {i+1}: {module.title}").strip()
                audio_path, duration = await self.tts.synthesize(
                    text=script_text,
                    language=plan.language or "en",
                    voice=request.voice_preference,
                )
                audio_tracks.append((audio_path, duration))

            completed_stages = [VideoStage.TTS_AUDIO_SYNTHESIS.value]
            self.update_task_status(task_id, "processing", VideoStage.AVATAR_LIP_SYNC.value, 35.0, stages_completed=completed_stages)

            # -------------------------------------------------------------
            # Stage 2 & 3: Render Avatar Clips and Subject-Aware Slides
            # -------------------------------------------------------------
            current_sec = 0.0

            for i, module in enumerate(plan.modules):
                audio_path, audio_dur = audio_tracks[i]
                clip_path = self.clips_dir / f"{lesson_id}_seg_{i+1:02d}_{module.segment_id}.mp4"
                seg_type = str(module.segment_type).lower()

                # Determine if this segment should be talking avatar or visual slide
                is_avatar = (
                    ("intro" in seg_type or "summary" in seg_type or i == 0 or i == len(plan.modules) - 1)
                    and "visual_concept" not in seg_type
                )

                if is_avatar:
                    # Render 2.5D Audio-Driven Viseme Avatar Clip
                    self.update_task_status(task_id, "processing", VideoStage.AVATAR_LIP_SYNC.value, 40.0 + (i / len(plan.modules)) * 30.0)
                    self.avatar.generate_avatar_clip(
                        audio_path=audio_path,
                        output_path=clip_path,
                        persona=request.custom_persona or "professor_alex",
                        subject_title=plan.title,
                        teacher_name="Prof. Alexander Vance" if plan.language != "hi" else "प्रो. मधुर शर्मा",
                    )
                else:
                    # Render Subject-Aware Visual Slide Video Clip
                    self.update_task_status(task_id, "processing", VideoStage.RENDERING_VISUAL_SLIDES.value, 40.0 + (i / len(plan.modules)) * 30.0)
                    self.slide_render.render_slide_video(
                        spec=module.visual_spec,
                        title=module.title,
                        audio_path=audio_path,
                        output_video_path=clip_path,
                        duration_sec=audio_dur,
                    )

                segment_clips.append(clip_path)

                start_ts = round(current_sec, 2)
                end_ts = round(current_sec + audio_dur, 2)

                # Append Chapter Metadata
                chapters.append({
                    "title": module.title,
                    "start_sec": start_ts,
                    "end_sec": end_ts,
                    "type": str(module.segment_type),
                })

                # Check for Checkpoint Pause Question
                if module.checkpoint_question:
                    q = module.checkpoint_question
                    q_dict = q.model_dump() if hasattr(q, "model_dump") else dict(q)
                    # Normalize prompt / question_text field for harness & frontend
                    if "prompt" not in q_dict and "question_text" in q_dict:
                        q_dict["prompt"] = q_dict["question_text"]
                    if "question_id" not in q_dict:
                        q_dict["question_id"] = f"q_{module.segment_id}"

                    marker = CheckpointPauseMarker(
                        marker_id=f"pm_{q_dict['question_id']}",
                        checkpoint_id=f"chk_{module.segment_id}",
                        timestamp_sec=round(start_ts + (audio_dur / 2.0), 2),
                        concept=q_dict.get("concept") or module.title,
                        question=q_dict,
                    )
                    pause_markers.append(marker)

                # Append Segment Metadata
                v_type = module.visual_spec.visual_type if module.visual_spec else None
                seg_meta = VideoSegmentMeta(
                    segment_id=module.segment_id,
                    order=i + 1,
                    segment_type=str(module.segment_type),
                    title=module.title,
                    start_sec=start_ts,
                    end_sec=end_ts,
                    duration_sec=round(audio_dur, 2),
                    video_file=str(clip_path),
                    audio_file=str(audio_path),
                    visual_type=str(v_type) if v_type else None,
                )
                segment_metas.append(seg_meta)
                current_sec += audio_dur

            completed_stages.extend([VideoStage.AVATAR_LIP_SYNC.value, VideoStage.RENDERING_VISUAL_SLIDES.value])

            # -------------------------------------------------------------
            # Stage 4: FFmpeg Concat Demuxer & Faststart MP4 Assembly
            # -------------------------------------------------------------
            self.update_task_status(task_id, "processing", VideoStage.STITCHING_FFMPEG.value, 85.0, stages_completed=completed_stages)
            logger.info(f"Task {task_id}: Stage 4 - Concatenating {len(segment_clips)} clips into {output_video_path}")

            concat_file = self.clips_dir / f"concat_{lesson_id}.txt"
            concat_lines = [f"file '{clip.resolve()}'" for clip in segment_clips]
            concat_file.write_text("\n".join(concat_lines) + "\n")

            ffmpeg_cmd = [
                self.ffmpeg_path,
                "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_file),
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-r", "30",
                "-preset", "ultrafast",
                "-c:a", "aac",
                "-b:a", "128k",
                "-movflags", "+faststart",
                str(output_video_path),
            ]

            proc = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            concat_file.unlink(missing_ok=True)

            if proc.returncode != 0:
                err = proc.stderr.decode(errors="ignore")
                logger.error(f"FFmpeg concatenation failed: {err}")
                raise RuntimeError(f"FFmpeg stitching failed: {err}")

            completed_stages.append(VideoStage.STITCHING_FFMPEG.value)

            # -------------------------------------------------------------
            # Stage 5: Manifest Construction & Persistence
            # -------------------------------------------------------------
            total_duration = round(current_sec, 2)
            video_url = f"/api/v1/video/stream/{lesson_id}.mp4"
            manifest_url = f"/api/v1/video/manifest/{lesson_id}"

            manifest = VideoManifest(
                lesson_id=lesson_id,
                video_id=lesson_id,
                plan_id=plan.plan_id,
                title=plan.title,
                video_url=video_url,
                total_duration_sec=total_duration,
                duration_sec=total_duration,
                language=plan.language or "en",
                resolution="1280x720",
                fps=30,
                chapters=chapters,
                segments=segment_metas,
                pause_markers=pause_markers,
                pause_checkpoints=pause_markers,
            )

            # Persist manifest to disk
            manifest_file = self.manifests_dir / f"{lesson_id}.json"
            manifest_file.write_text(json.dumps(manifest.model_dump(), indent=2))
            self._manifests[lesson_id] = manifest

            # Finalize Task Status
            self.update_task_status(
                task_id=task_id,
                status="completed",
                stage=VideoStage.READY.value,
                progress_percent=100.0,
                stages_completed=completed_stages,
                manifest_url=manifest_url,
                video_url=video_url,
            )

            return manifest, output_video_path

        except Exception as e:
            logger.exception(f"Video generation task {task_id} failed: {e}")
            self.update_task_status(
                task_id=task_id,
                status="failed",
                stage=VideoStage.FAILED.value,
                progress_percent=0.0,
                error_message=str(e),
            )
            raise


video_stitcher = VideoStitcher()
