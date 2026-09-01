## 2026-09-01T01:07:11Z
You are worker_m3_video.
Your working directory is /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/worker_m3_video/
Read ORIGINAL_REQUEST.md at /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/ORIGINAL_REQUEST.md
Read PROJECT.md at /home/dev/Desktop/projects/AI-InnovationHackathon/PROJECT.md
Read M1 & M2 handoffs at /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/worker_m1_ingestion/handoff.md and /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/worker_m2_planner/handoff.md
Read survey report at /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_survey_2/handoff.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Your objective:
Implement Milestone 3 (M3: Hybrid Video Generation Pipeline) completely and authentically:
1. `backend/app/models/video.py`: Pydantic models for `VideoGenerationRequest`, `VideoGenerationStatus`, `VideoSegmentMeta`, `CheckpointPauseMarker`, `VideoManifest`.
2. `backend/app/services/tts_service.py`: Multilingual TTS engine:
   - Uses `edge-tts` for high-fidelity neural voices (English: `en-US-GuyNeural`, `en-US-AriaNeural`; Hindi: `hi-IN-MadhurNeural`, `hi-IN-SwaraNeural`).
   - Instant fallback to `gTTS` or wave synthesis if offline or network unreachable.
   - Computes audio duration in seconds.
3. `backend/app/services/avatar_service.py`: High-Speed Audio-Driven 2.5D Viseme Avatar Generator:
   - Takes teacher portrait image/canvas and TTS audio file.
   - Computes audio energy and volume envelope to drive mouth viseme opening/closing, natural eye blinking, subtle sinusoidal head bobbing, and audio visualizer waves.
   - Encodes into an H.264 MP4 clip synchronized with the audio.
   - Pluggable Wav2Lip CLI backend hook when model weights are present.
4. `backend/app/services/slide_render_service.py`: Subject-Aware Visual Slide Renderers:
   - Math: Render LaTeX formulas, derivations, and mathematical graphs into video frames.
   - CS: Render syntax-highlighted code blocks (using Pygments) inside modern IDE window frames.
   - Biology: Render cellular/organelle diagrams with clear labeled callouts.
   - History: Render chronological milestone timelines.
   - Audio sync: Slides are rendered as continuous 30fps video clips matching the exact duration of the TTS audio narration.
5. `backend/app/services/video_stitcher.py`:
   - Assembles the sequence: Avatar Intro -> Subject-Aware Concept Slides (with checkpoint pause markers) -> Avatar Outro/Summary.
   - Uses FFmpeg to concatenate clips into a unified 1280x720 30fps H.264/AAC web-optimized MP4 (`-movflags +faststart`).
   - Generates `VideoManifest` containing video URL, total duration, chapter segments, and timestamped `CheckpointPauseMarker`s for R4 in-video interactive questions.
6. `backend/app/api/video.py`: REST routes:
   - `POST /api/v1/video/generate`: Trigger background generation task for a `plan_id`.
   - `GET /api/v1/video/status/{task_id}`: Poll generation progress (TTS -> Avatar -> Slides -> Stitching -> Ready).
   - `GET /api/v1/video/manifest/{video_id}`: Retrieve video manifest and pause checkpoints.
   - `GET /api/v1/video/stream/{video_id}`: Stream video file supporting HTTP 206 Range headers.
7. Mount `video_router` in `backend/app/main.py`.
8. `backend/tests/test_video.py`: Comprehensive test suite verifying TTS generation in English & Hindi, Avatar clip rendering, Math/Code/Bio/History slide renders, FFmpeg video assembly, Range streaming, and manifest pause markers.
9. Run `pytest backend/tests/ -v` and `python3 tests_e2e/test_runner.py --tier 1` to verify all tests pass.
10. Write handoff report to /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/worker_m3_video/handoff.md and notify parent via send_message.
