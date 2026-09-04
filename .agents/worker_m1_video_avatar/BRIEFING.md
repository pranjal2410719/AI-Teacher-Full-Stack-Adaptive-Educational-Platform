# BRIEFING — 2026-09-04T17:58:00Z

## Mission
Implement Milestone 1 (Backend Video Engine & Photorealistic Avatar): copy photorealistic teacher assets to data/avatars, upgrade avatar_service.py with ROI viseme compositing and audio RMS-synced lip sync, optimize video_stitcher.py with concurrent TTS, parallel slide rendering, and stream-copy concat, rebrand backend files to ApniHelp, verify <=20s/min performance and 100% pytest pass rate.

## 🔒 My Identity
- Archetype: implementer, qa, specialist
- Roles: implementer, qa, specialist
- Working directory: /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/worker_m1_video_avatar
- Original parent: 9b3dbfce-1695-4086-9710-9092c545fed8
- Milestone: Milestone 1 (Backend Video Engine & Photorealistic Avatar)

## 🔒 Key Constraints
- Exclusively owned files:
  - backend/app/services/video_stitcher.py
  - backend/app/services/avatar_service.py
  - backend/app/services/slide_render_service.py
  - backend/app/config.py
  - backend/app/main.py
  - backend/tests/test_ingestion.py
  - data/avatars/*
- Video generation performance: strictly <= 20s processing per minute of final video (R1)
- Photorealistic human AI teacher avatar generated via image model (R4)
- ApniHelp branding (R5)
- All implementations must be genuine, maintaining real state and behavior (Integrity Mandate)
- .agents/ holds only metadata (plans, progress, handoffs), never source/test/data code

## Current Parent
- Conversation ID: 9b3dbfce-1695-4086-9710-9092c545fed8
- Updated: 2026-09-04T17:58:00Z

## Task Summary
- **What to build**: Photorealistic avatar engine in avatar_service.py, parallel TTS + parallel slides + stream copy in video_stitcher.py, ApniHelp branding in config.py, main.py, slide_render_service.py, test_ingestion.py.
- **Success criteria**: <= 20s/min video generation benchmark, 100% test pass on pytest backend/tests/, photorealistic avatar rendered with RMS audio lip-sync.
- **Interface contracts**: backend/app/models/lesson.py, VideoGenerationRequest, VideoGenerationResponse.
- **Code layout**: backend/app/services, backend/tests, data/avatars.

## Key Decisions Made
- Use ROI viseme compositing on top of cached photorealistic teacher portraits for ultra-fast (400+ FPS) avatar animation.
- Standardize AV format to 1280x720, 30fps, yuv420p, aac, 44100Hz, 2 channels to enable instant FFmpeg `-c copy` concatenation.
- Use asyncio.gather for parallel TTS synthesis and ThreadPoolExecutor(max_workers=4) for slide video rendering.

## Change Tracker
- **Files modified**: None yet
- **Build status**: Pending initial run
- **Pending issues**: None

## Quality Status
- **Build/test result**: Pending
- **Lint status**: Pending
- **Tests added/modified**: Pending

## Loaded Skills
- None specified in dispatch prompt.

## Artifact Index
- .agents/worker_m1_video_avatar/DISPATCH.md — Assignment and instructions
- .agents/worker_m1_video_avatar/BRIEFING.md — Persistent working memory
- .agents/worker_m1_video_avatar/progress.md — Liveness heartbeat and progress
