# Project Plan: ApniHelp Full-Stack Platform Adaptation

## Architecture Overview
- **Backend (`backend/app/`)**: FastAPI server providing ingestion, RAG, lesson planning, and video generation.
  - Video Generation Engine: `video_stitcher.py`, `avatar_service.py`, `slide_render_service.py`, `tts_service.py`.
  - Optimized for R1 (concurrent TTS via `asyncio.gather`, parallel slide rendering via `ThreadPoolExecutor`, ROI viseme avatar compositing at >400 FPS, FFmpeg `-c copy` stream concat).
  - Photorealistic Avatar for R4: High-resolution AI-generated portrait (`data/avatars/teacher_portrait.png`) with dynamic audio RMS-driven viseme patch overlay and natural blinking.
- **Frontend (`frontend/src/`)**: React/Vite/Tailwind educational interface.
  - R2 Simplicity: Single primary **[ Generate Video ]** CTA button on input view chaining `upload/topic` -> `plan` -> `generate-video` without intermediate modal interruptions.
  - R3 Light Palette: White (`bg-white` surfaces), Light Gray (`bg-slate-50` backdrop, `border-gray-200`, `text-slate-600`), Dark Blue (`text-blue-950` headings, `bg-blue-900`), and Warm Vibrant Yellow (`bg-yellow-400 hover:bg-yellow-500 text-slate-950 font-bold` for primary CTA button).
  - Seamless continuation to video playback, interactive pause checkpoints, quiz, and analytics.
- **Branding & Packaging (R5)**: 100% "ApniHelp" branding across all frontend/backend titles, OpenAPI docs, watermarks, Docker container names, launcher scripts, and documentation.
- **E2E Testing Suite**: Automated tests asserting R1 (≤20s/min video generation benchmark for 5m and 10m), R2 (single button), R3 (light theme palette tokens), R4 (avatar photorealism and audio sync), and R5 (zero legacy branding).

---

## Feature Inventory & Assignment
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | R1 Video Performance Engine | Concurrent TTS + parallel slide rendering + stream copy concat | M1 | ORIGINAL_REQUEST.md line 95 |
| 2 | R4 Photorealistic Avatar | Image model AI teacher portrait + audio-synced ROI visemes | M1 | ORIGINAL_REQUEST.md line 104 |
| 3 | Backend Branding Migration | ApniHelp in config, main, watermarks, slide branding | M1 | ORIGINAL_REQUEST.md line 107 |
| 4 | R2 Single-Button Video Pipeline | 1-click 'Generate Video' button with chained async pipeline | M2 | ORIGINAL_REQUEST.md line 98 |
| 5 | R3 Light Theme Palette | White, yellow, gray, dark blue across all components | M2 | ORIGINAL_REQUEST.md line 101 |
| 6 | Frontend Branding Migration | ApniHelp in index.html, Header, tutor, analytics, package.json | M2 | ORIGINAL_REQUEST.md line 107 |
| 7 | Infra & Docs Re-branding | docker-compose.yml, run.sh, README.md, docs/* | M3 | ORIGINAL_REQUEST.md line 107 |
| 8 | E2E Benchmark & Acceptance Suite | Automated tests for R1-R5, 100% pass verification | M4 | ORIGINAL_REQUEST.md line 110 |

---

## Milestones Status & Ownership
| # | Milestone Name | Scope | Exclusively Owned Files | Status |
|---|----------------|-------|-------------------------|--------|
| M1 | Backend Video Engine & Avatar (R1, R4, R5-Backend) | Video speedup (<=20s/min), photorealistic avatar, backend branding | `backend/app/services/video_stitcher.py`, `backend/app/services/avatar_service.py`, `backend/app/services/slide_render_service.py`, `backend/app/config.py`, `backend/app/main.py`, `backend/tests/test_ingestion.py`, `data/avatars/` | IN_PROGRESS (Worker M1 was finishing pytest & benchmarks) |
| M2 | Frontend Flow & Light Theme (R2, R3, R5-Frontend) | Single 'Generate Video' button, light palette styling, frontend branding | `frontend/src/*`, `frontend/index.html`, `frontend/index.css`, `frontend/tailwind.config.js`, `frontend/package.json` | COMPLETED & VERIFIED (worker_m2_frontend_ui_gen2) |
| M3 | Infrastructure & Documentation (R5-Infra/Docs) | Container names, launcher banners, root README, docs | `docker-compose.yml`, `run.sh`, `README.md`, `docs/*`, `package.json` | COMPLETED & VERIFIED (worker_m3_infra_docs_gen2) |
| M4 | Comprehensive E2E Verification & Audit Gate | Test suite for R1-R5, run all backend & E2E tests, audit gate | `tests_e2e/*` | READY FOR DISPATCH upon M1 completion |
