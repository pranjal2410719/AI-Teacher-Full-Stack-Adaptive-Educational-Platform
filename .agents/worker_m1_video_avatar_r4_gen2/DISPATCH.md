## 2026-09-04T18:21:10Z

You are worker_m1_video_avatar_r4_gen2, an expert backend and video systems engineer.
Your working directory: /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/worker_m1_video_avatar_r4_gen2
Project root: /home/dev/Desktop/projects/AI-InnovationHackathon

Read ORIGINAL_REQUEST.md first:
/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/ORIGINAL_REQUEST.md (specifically lines 81-120).

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Mission: Implement Milestone 1 (Backend Video Engine & Photorealistic Avatar - R1, R4, R5-Backend):
1. Copy photorealistic teacher assets:
   Copy `/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_r3_video_avatar/teacher_portrait.png` and `teacher_portrait_male.png` to `/home/dev/Desktop/projects/AI-InnovationHackathon/data/avatars/`.
2. Photorealistic AI Teacher Avatar (`backend/app/services/avatar_service.py`):
   - Replace the legacy 2D cartoon drawing primitives with the photorealistic AI teacher portrait composited with audio RMS-driven Region-of-Interest (ROI) visemes and natural blinking.
   - Reference `/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_r3_video_avatar/handoff.md` and `analysis.md` for the tested high-speed (>400 FPS) implementation.
   - Ensure the lower-third banner uses "ApniHelp" branding.
3. Video Engine Speedup (`backend/app/services/video_stitcher.py`):
   - Replace sequential TTS loop with concurrent synthesis using `asyncio.gather`.
   - Parallelize segment rendering using `ThreadPoolExecutor(max_workers=4)`.
   - Enforce stream-copy concatenation (`-c copy`) in FFmpeg concat demuxer so concatenation completes in <1s.
   - Ensure video generation completes in <=20s of processing per minute of final video length (e.g. 5-min <=100s, 10-min <=200s).
4. Slide Render Standardization & Watermark (`backend/app/services/slide_render_service.py`):
   - Standardize output encoding parameters (`-ar 44100 -ac 2`, H.264, 30 fps) so they match avatar clips for seamless `-c copy` concat.
   - Update watermark text from "AI TEACHER" to "ApniHelp".
5. Backend Branding (`backend/app/config.py`, `backend/app/main.py`, `backend/tests/test_ingestion.py`):
   - Update app name, descriptions, logger names, and welcome messages to "ApniHelp" / "apnihelp".
   - Concurrently update `backend/tests/test_ingestion.py` line 483 to assert "ApniHelp".
6. Verification:
   - Run `pytest backend/tests/ -v` to ensure all 30+ backend tests pass cleanly.
   - Benchmark video generation time on test lessons (confirming <=20s/min).
   - Document all commands, file diffs, test outputs, and benchmarks in `handoff.md` in your working directory.
   - Send completion message to parent when done.
