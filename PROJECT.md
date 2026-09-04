# Project: AI Teacher Adaptive Educational Platform — Real-User Audit & Hardening

## Architecture
- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS. Single-page app with 5 pipeline tabs: Ingestion -> Lesson Plan -> Video & Checks -> Quiz & Report -> Profile & Analytics.
- **Backend**: Python FastAPI at `http://localhost:8000`, Pydantic models, SQLite / JSON persistence, hybrid RAG with NumpyVectorStore + BM25, parametric fallback engine.
- **Shared Interface**: Base URL `/api/v1`, JSON payloads matching TypeScript types in `frontend/src/types/index.ts`.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Backend Route Parity | Route aliases for `/api/v1/lessons/plan/{id}` and `/api/v1/lessons/{id}` | M1 | Survey Backend |
| 2 | Tutor Chat RAG Grounding | Fix `vector_store.query(query=msg)` keyword argument and results unpacking | M1 | Survey Backend |
| 3 | Checkpoint Question Schema | Support `prompt`, `type`, `correct_option_index` in `CheckpointQuestion` model | M1 | Survey Backend |
| 4 | Frontend API Topic Plan Creation | Add `topic` parameter in `api.createLessonPlan` and pass from `App.tsx` | M2 | Survey Frontend |
| 5 | App Tab Guards & Empty States | Add fallback empty cards with icons, messages, and CTAs for tabs 2 & 3 in `App.tsx` | M2 | Survey Frontend |
| 6 | Frontend Error & Loading States | Visible loading indicators, retry CTAs, and error handling in async actions | M2 | Survey Frontend |
| 7 | UI Theme Slate & Purple Alignment | Remove `#2b1a07`, `#ff6f1e`, `#ce500a` across ProfileModal, IngestionView, SidePanelTutor | M3 | Survey UI Theme |
| 8 | Button Semantics & Hover States | Convert interactive `<div>` elements to `<button>` with distinct hover feedback | M3 | Survey UI Theme |
| 9 | Text Contrast & Readability | Upgrade washed-out `text-slate-400` primary headings and inputs to `text-slate-100`/`text-slate-200` | M3 | Survey UI Theme |
| 10 | Adaptive Loop End-to-End | Verify Quiz submit -> Profile update -> Analytics recommendation click -> New Plan | M4 | Survey Full Loop |
| 11 | Production Build & Git Push | Zero TS errors in `npm run build`, pytest 100% pass, git commit & push to origin main | M4 | User Request |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Backend API Alignment & Fixes | Route aliases, RAG vector query fix, CheckpointQuestion schema | None | IN_PROGRESS |
| M2 | Frontend Flow, Guards & Empty States | `api.ts`, `App.tsx` topic plan creation, Tab empty states, error handling | M1 | PLANNED |
| M3 | UI Consistency, Theme & Button Semantics | ProfileModal, IngestionView, SidePanelTutor, LessonPlanEditor, QuizView, VideoPlayer | None | IN_PROGRESS |
| M4 | E2E Adaptive Loop Verification, Build & Git Push | End-to-end simulation, `npm run build`, pytest, git commit & push | M1, M2, M3 | PLANNED |

## Interface Contracts
### Frontend ↔ Backend API (`/api/v1`)
- `POST /api/v1/lessons/plan`: Request body `{ learner_profile: LearnerProfile, document_id?: string, topic_id?: string, topic?: string }` -> returns `LessonPlan`
- `GET /api/v1/lessons/{plan_id}` and `GET /api/v1/lessons/plan/{plan_id}` -> returns `LessonPlan`
- `PUT /api/v1/lessons/{plan_id}` and `PUT /api/v1/lessons/plan/{plan_id}` -> returns `LessonPlan`
- `POST /api/v1/assessment/submit`: Request body `{ student_id: string, lesson_id: string, answers: Record<string, number> }` -> returns `LearningReport`
- `GET /api/v1/profile/{student_id}` -> returns `LearnerProfile`
- `GET /api/v1/profile/{student_id}/recommendations` -> returns `RecommendationResponse`

## Code Layout
- `backend/app/api/`: FastAPI route handlers (`lessons.py`, `assessment.py`, `profile.py`, `materials.py`)
- `backend/app/models/`: Pydantic data models (`lesson_plan.py`, `assessment.py`, `profile.py`)
- `backend/app/services/`: Business logic & storage (`interaction_service.py`, `profile_service.py`, `vector_store.py`)
- `frontend/src/App.tsx`: Main application coordinator and tab navigation
- `frontend/src/services/api.ts`: API client layer
- `frontend/src/types/index.ts`: TypeScript interfaces
- `frontend/src/components/`: UI tab components (Ingestion, Planner, VideoPlayer, Assessment, Analytics, Profile, TutorChat)
