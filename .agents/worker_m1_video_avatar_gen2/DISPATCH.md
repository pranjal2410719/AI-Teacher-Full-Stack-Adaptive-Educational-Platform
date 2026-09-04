## 2026-09-04T18:22:42Z

You are worker_m1_video_avatar_gen2, an implementation worker for Milestone 1 of the ApniHelp platform.

Your working directory: /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/worker_m1_video_avatar_gen2
Project root: /home/dev/Desktop/projects/AI-InnovationHackathon
Original user request file: /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/ORIGINAL_REQUEST.md
Predecessor Plan: /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/orchestrator_r3_gen2/plan.md
Explorer handoff report: /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_r3_video_avatar/handoff.md
Explorer detailed analysis: /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_r3_video_avatar/analysis.md
Pre-generated photorealistic avatar assets:
- Female portrait: /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_r3_video_avatar/teacher_portrait.png
- Male portrait: /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_r3_video_avatar/teacher_portrait_male.png

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Exclusively Owned Files:
- backend/app/services/video_stitcher.py
- backend/app/services/avatar_service.py
- backend/app/services/slide_render_service.py
- backend/app/config.py
- backend/app/main.py
- backend/tests/test_ingestion.py
- data/avatars/

Tasks:
1. Copy the photorealistic teacher portraits from `/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_r3_video_avatar/teacher_portrait.png` and `teacher_portrait_male.png` into `data/avatars/`.
2. Implement photorealistic human-like AI teacher avatar in `backend/app/services/avatar_service.py`:
   - Load high-res photorealistic teacher portrait (`data/avatars/teacher_portrait.png`).
   - Implement ROI (Region-of-Interest) mouth viseme patch compositing and audio RMS energy lip synchronization (replacing cartoon drawings).
   - Maintain natural blinking and light-palette lower-third ApniHelp branding.
3. Optimize `backend/app/services/video_stitcher.py`:
   - Implement concurrent TTS synthesis using `asyncio.gather`.
   - Implement parallel slide video clip rendering using `concurrent.futures.ThreadPoolExecutor`.
   - Standardize output encoding parameters across all clips (`-pix_fmt yuv420p -r 30 -c:a aac -ar 44100 -ac 2`) so that FFmpeg concat can execute stream-copy (`-c copy`) without re-encoding.
   - Ensure the pipeline achieves ≤20s processing per minute of final video length (R1).
4. Update `backend/app/services/slide_render_service.py`:
   - Add FFmpeg stillimage optimization flags and standardized audio parameters.
   - Use ApniHelp branding in slide watermarks/headers.
5. Update backend branding in `backend/app/config.py` and `backend/app/main.py`:
   - Ensure title, description, and OpenAPI metadata reflect "ApniHelp".
6. Run `pytest backend/tests/ -v` and fix any issues so that all tests pass 100%.
7. Run empirical performance benchmarks verifying video generation performance ≤20s per minute for representative 5-minute and 10-minute workloads.
8. Document all findings, commands, and benchmark results in `/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/worker_m1_video_avatar_gen2/handoff.md`.
9. Update your progress.md and send a completion message back to the orchestrator.
