# Dispatch: worker_m1_video_avatar

## Objective
Implement Milestone 1: Backend Video Engine & Photorealistic Avatar (R1, R4, R5-Backend) for ApniHelp.

## Working Directory
`/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/worker_m1_video_avatar`

## Exclusively Owned Files
- `backend/app/services/video_stitcher.py`
- `backend/app/services/avatar_service.py`
- `backend/app/services/slide_render_service.py`
- `backend/app/config.py`
- `backend/app/main.py`
- `backend/tests/test_ingestion.py`
- `data/avatars/*`

## Inputs & Context
1. Read `/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/ORIGINAL_REQUEST.md` (lines 81-120).
2. Read the investigation report from `explorer_r3_video_avatar`:
   - `/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_r3_video_avatar/analysis.md`
   - `/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_r3_video_avatar/handoff.md`
3. Teacher avatar image assets are available at:
   - `/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_r3_video_avatar/teacher_portrait.png`
   - `/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_r3_video_avatar/teacher_portrait_male.png`

## Specific Instructions
1. **Photorealistic Avatar Asset Installation (R4)**:
   - Copy `teacher_portrait.png` and `teacher_portrait_male.png` from `.agents/explorer_r3_video_avatar/` into `data/avatars/`.
   - Update `backend/app/services/avatar_service.py` to replace cartoon vector shapes with photorealistic ROI viseme compositing on top of the portrait.
   - Implement audio RMS-energy based lip-sync (closed, slight_open, wide_open, round_o, smile/rest) and natural 3-frame eye blinking.
   - Update avatar banner text to display "ApniHelp" instead of "AI Teacher".
2. **Concurrent TTS & Video Generation Speedup (R1)**:
   - In `backend/app/services/video_stitcher.py`:
     - Synthesize module narration audio concurrently using `asyncio.gather`.
     - Render slide video segments in parallel using `concurrent.futures.ThreadPoolExecutor(max_workers=4)`.
     - Standardize video/audio stream codecs across avatar and slide generators (`1280x720`, `30fps`, `yuv420p`, `aac`, `44100Hz`, `2 channels`).
     - In FFmpeg concatenation, use `-c copy` (stream copy) rather than full re-encoding.
   - Ensure `backend/app/services/slide_render_service.py` uses `-tune stillimage -crf 26 -threads 2 -g 120 -ar 44100 -ac 2` and updates any "AI TEACHER" watermark to "ApniHelp".
3. **Backend Branding (R5)**:
   - In `backend/app/config.py`: `app_name: str = "ApniHelp Core Platform"`
   - In `backend/app/main.py`: Update logger to `apnihelp.main`, API title/description to ApniHelp, and root endpoint message to `"Welcome to ApniHelp Core Server"`.
   - In `backend/tests/test_ingestion.py:483`: Update assertion to expect `"Welcome to ApniHelp"`.
4. **Verification**:
   - Run backend tests: `pytest backend/tests/ -v` and confirm 100% pass.
   - Benchmark 1-min / test video generation time to confirm it meets $\le 20\text{s}$ per minute of final video length.

## MANDATORY INTEGRITY WARNING
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Deliver your results in `handoff.md` and report back with `send_message`.

## 2026-09-04T17:57:42Z
You are worker_m1_video_avatar, a specialized implementation worker.
Your working directory is: /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/worker_m1_video_avatar
Please read your assignment file: /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/worker_m1_video_avatar/DISPATCH.md
MANDATORY: Read /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/ORIGINAL_REQUEST.md before starting work. Do NOT summarize or filter it — read lines 81-120 directly.

Your mission:
Implement Milestone 1 (Backend Video Engine & Photorealistic Avatar).
- Copy photorealistic teacher assets from /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_r3_video_avatar/ (teacher_portrait.png, teacher_portrait_male.png) to data/avatars/
- Upgrade backend/app/services/avatar_service.py with photorealistic ROI viseme compositing and audio RMS-synced lip sync.
- Optimize backend/app/services/video_stitcher.py with concurrent TTS (asyncio.gather), parallel slide rendering (ThreadPoolExecutor), and stream-copy concat (-c copy) to guarantee <=20s processing per minute of video.
- Rebrand backend/app/config.py, backend/app/main.py, backend/app/services/slide_render_service.py, backend/tests/test_ingestion.py to ApniHelp.
- Run tests and benchmarks, and write a thorough handoff.md in your working directory.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## 2026-09-04T18:13:37Z
**Context**: Milestone 1 implementation status check
**Content**: Checking in on progress for Milestone 1 (Backend Video Engine & Avatar). Please provide a status update on your implementation, test execution, and handoff report.
**Action**: Report current status and any blockers.
