# BRIEFING — 2026-09-04T17:56:00Z

## Mission
Investigate video generation performance (R1: <= 20s processing per minute of video) and AI teacher avatar (R4: photorealistic human-like avatar with synced lip/speech) to provide concrete architectural optimizations and actionable implementation specs for ApniHelp.

## 🔒 My Identity
- Archetype: explorer
- Roles: Teamwork explorer
- Working directory: /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_r3_video_avatar
- Original parent: 9b3dbfce-1695-4086-9710-9092c545fed8
- Milestone: ApniHelp Video & Avatar Architecture Investigation

## 🔒 Key Constraints
- Read-only investigation — do NOT implement in source code (only write to our own agent folder)
- Must read ORIGINAL_REQUEST.md directly (especially ApniHelp requirements lines 81-120)
- Deliver findings in analysis.md and handoff.md in our folder
- Report back with send_message to parent

## Current Parent
- Conversation ID: 9b3dbfce-1695-4086-9710-9092c545fed8
- Updated: 2026-09-04T17:46:18Z

## Investigation State
- **Explored paths**: ORIGINAL_REQUEST.md, DISPATCH.md, backend/app/services/video_stitcher.py, avatar_service.py, slide_render_service.py, tts_service.py, backend/app/models/video.py, backend/tests/test_video.py.
- **Key findings**:
  - Baseline video generation took ~74.7s per minute of final video (failed R1 by 3.7x).
  - Existing avatar was 100% 2D vector/cartoon polygons and ellipses (violating R4).
  - Generated photorealistic AI teacher portraits for female (Dr. Sarah Vance) and male (Prof. Alexander Vance) in 1280x720 16:9 format with ApniHelp branding.
  - Developed and benchmarked ROI-based viseme compositing engine running at 439 FPS (1.52s for 667 frames).
  - Benchmarked concrete optimizations: concurrent TTS (asyncio.gather, 8.6x faster), parallel slide rendering (ThreadPoolExecutor, 2.1x faster), stream copy concat (-c copy, 27x faster).
  - Total projected time: 5-min video in ~47.7s (<= 100s limit), 10-min video in ~87.5s (<= 200s limit).
- **Unexplored areas**: None. Investigation complete and empirically validated.

## Key Decisions Made
- Selected ROI-based viseme compositing over heavy neural diffusion/Wav2Lip to guarantee offline real-time speed (>400 FPS) without GPU dependency.
- Enforced stream parameter alignment (1280x720 30fps yuv420p, AAC 44.1kHz stereo) across all clips to enable -c copy stream muxing.
- Saved photorealistic assets in .agents/explorer_r3_video_avatar/ (teacher_portrait.png, teacher_portrait_male.png).

## Artifact Index
- analysis.md — Full technical analysis and empirical benchmark report
- handoff.md — 5-component structured handoff report for builder/parent
- progress.md — Liveness heartbeat and completed task index
- teacher_portrait.png — 1280x720 photorealistic female AI teacher portrait
- teacher_portrait_male.png — 1280x720 photorealistic male AI teacher portrait
- test_avatar_sample.mp4 — Validated 10s photorealistic talking avatar MP4 clip
