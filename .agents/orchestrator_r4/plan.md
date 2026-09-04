# Project Plan: ApniHelp Full-Stack Platform Adaptation (Round 4)

## Architecture Overview
- **Backend (`backend/app/`)**: FastAPI server providing ingestion, RAG, lesson planning, and video generation.
  - Video Generation Engine: `video_stitcher.py`, `avatar_service.py`, `slide_render_service.py`, `tts_service.py`.
  - Optimized for R1: concurrent TTS via `asyncio.gather`, parallel slide rendering via `ThreadPoolExecutor`, ROI viseme avatar compositing at >400 FPS, FFmpeg `-c copy` stream concat.
  - Photorealistic Avatar for R4: High-resolution AI-generated portrait (`data/avatars/teacher_portrait.png`) with dynamic audio RMS-driven viseme patch overlay and natural blinking.
  - Backend branding for R5: ApniHelp throughout configuration, loggers, messages, and slide watermarks.
- **Frontend (`frontend/src/`)**: React/Vite/Tailwind educational interface.
  - R2 Simplicity: Single primary **[ Generate Video ]** CTA button on input view chaining `upload/topic` -> `plan` -> `generate-video` without intermediate modal interruptions. (STATUS: COMPLETED & VERIFIED)
  - R3 Light Palette: White (`bg-white`), Light Gray (`bg-slate-50`, `border-gray-200`), Dark Blue (`text-blue-950`, `bg-blue-900`), and Warm Vibrant Yellow (`bg-yellow-400`). (STATUS: COMPLETED & VERIFIED)
- **Branding & Packaging (R5)**: 100% "ApniHelp" branding across all frontend/backend titles, OpenAPI docs, watermarks, Docker container names, launcher scripts, and documentation. (STATUS: COMPLETED & VERIFIED)
- **E2E Testing Suite**: Automated tests asserting R1 (≤20s/min video generation benchmark for 5m and 10m), R2 (single button), R3 (light theme palette tokens), R4 (avatar photorealism and audio sync), and R5 (zero legacy branding).

---

## Feature Inventory & Assignment
| # | Feature | Description | Milestone | Status |
|---|---------|-------------|-----------|--------|
| 1 | R1 Video Performance Engine | Concurrent TTS + parallel slide rendering + stream copy concat (<=20s/min) | M1 | IN_PROGRESS |
| 2 | R4 Photorealistic Avatar | Image model AI teacher portrait + audio-synced ROI visemes | M1 | IN_PROGRESS |
| 3 | Backend Branding Migration | ApniHelp in config, main, watermarks, slide branding | M1 | IN_PROGRESS |
| 4 | R2 Single-Button Video Pipeline | 1-click 'Generate Video' button with chained async pipeline | M2 | DONE |
| 5 | R3 Light Theme Palette | White, yellow, gray, dark blue across all components | M2 | DONE |
| 6 | Frontend Branding Migration | ApniHelp in index.html, Header, tutor, analytics, package.json | M2 | DONE |
| 7 | Infra & Docs Re-branding | docker-compose.yml, run.sh, README.md, docs/* | M3 | DONE |
| 8 | E2E Benchmark & Acceptance Suite | Automated tests for R1-R5, 100% pass verification | M4 | READY TO RUN |

---

## Milestones
| # | Milestone Name | Scope | Exclusively Owned Files | Dependencies | Status |
|---|----------------|-------|-------------------------|--------------|--------|
| M1 | Backend Video Engine & Avatar (R1, R4, R5-Backend) | Video speedup (<=20s/min), photorealistic avatar, backend branding | `backend/app/services/video_stitcher.py`, `backend/app/services/avatar_service.py`, `backend/app/services/slide_render_service.py`, `backend/app/config.py`, `backend/app/main.py`, `backend/tests/test_ingestion.py`, `data/avatars/` | None | IN_PROGRESS |
| M2 | Frontend Flow & Light Theme (R2, R3, R5-Frontend) | Single 'Generate Video' button, light palette styling, frontend branding | `frontend/src/*`, `frontend/index.html`, `frontend/index.css`, `frontend/tailwind.config.js`, `frontend/package.json` | None | DONE |
| M3 | Infrastructure & Documentation (R5-Infra/Docs) | Container names, launcher banners, root README, docs | `docker-compose.yml`, `run.sh`, `README.md`, `docs/*` | None | DONE |
| M4 | Comprehensive E2E Verification & Audit Gate | Run backend tests, E2E test suite (Tiers 1-5), R1 benchmark, review, challenge, and forensic audit | `tests_e2e/*` | M1, M2, M3 | PLANNED |
