# Original User Request

## 2026-09-02T11:03:46Z

Perform a deep, real-user audit of the AI Teacher Adaptive Learning Platform — a full-stack app with a React/Vite frontend and FastAPI backend. Simulate the entire user journey end-to-end across the critical 4-stage path, find every broken flow, UI inconsistency, backend error, and logic gap, then fix them in-place and verify the full loop works from start to finish.

Working directory: /home/dev/Desktop/projects/AI-InnovationHackathon

Integrity mode: benchmark

---

## Context

The app is a 5-tab pipeline: **Ingestion → Lesson Plan → Video & Checks → Quiz & Report → Profile & Analytics**.

Key files:
- Frontend entry: `frontend/src/App.tsx`
- API layer: `frontend/src/services/api.ts` (base: `/api/v1`)
- All tabs: `frontend/src/components/{Ingestion,Planner,VideoPlayer,Assessment,Analytics}/`
- Backend: FastAPI at `localhost:8000` (already running)
- Frontend dev server: run with `cd frontend && npm run dev` (port 5173) if needed
- Build: `cd frontend && npm run build`

The 5 stages and what each does:
1. **Ingestion** — Upload doc (PDF/DOCX/PPTX) OR type a topic → `POST /api/v1/materials/upload` or `POST /api/v1/materials/topic`
2. **Lesson Plan** — ProfileModal auto-opens → user sets level/language → `POST /api/v1/lessons/plan` → editable plan
3. **Video & Checks** — `POST /api/v1/lessons/generate-video` → async poll → video player with pause markers *(skip for audit — treat as best-effort)*
4. **Quiz & Report** — `POST /api/v1/assessment/generate` + `POST /api/v1/assessment/submit` → LearningReport
5. **Analytics** — `GET /api/v1/profile/{id}` + `GET /api/v1/profile/{id}/recommendations` → AnalyticsDashboard

Note: A previous audit run was interrupted by a server restart. The `.agents/` directory in the working directory contains leftover scaffolding from the previous run — ignore it and start fresh.

---

## Requirements

### R1. Backend API Audit
Test every API endpoint used by the frontend against the running backend at `localhost:8000`. For each endpoint: send a realistic request, check the response shape matches what the frontend's TypeScript types expect, and document any mismatch, 4xx/5xx error, missing field, or wrong data type. Fix backend issues found.

### R2. Frontend Flow Audit
Simulate the full user journey through the critical path (Ingestion → Lesson Plan → Quiz & Report → Analytics) by reading the component code and tracing state transitions in `App.tsx`. Identify: broken tab transitions, missing loading/error states, uncaught promise rejections, state that never gets set, components that never render due to a guard condition being wrong, and any dead ends where the user cannot proceed. Fix all issues found.

### R3. UI Consistency & Integrity
The app uses a strict dark slate theme (`bg-slate-950`/`slate-900` backgrounds, `purple`/`indigo` brand, `emerald` accent, `amber` warnings). Audit every component for: hardcoded light colors that break the theme (`#fdfbf9`, `#2b1a07`, cream/brown tones), missing hover states on interactive elements, buttons that look like divs or vice-versa, and missing empty states. Fix all inconsistencies to match the theme established in `Header.tsx` and the already-redesigned `AnalyticsDashboard.tsx`.

### R4. Adaptive Loop Integrity
Verify the feedback loop closes correctly: after a quiz is submitted, the learner profile is updated with mastery scores and weak areas, and the Analytics tab shows the correct updated data including AI recommendations. Trace the data from `POST /assessment/submit` → profile update → `GET /profile/{id}/recommendations` and confirm no data is dropped or stale. Fix any breaks.

### R5. Rebuild and Git Push
After all fixes are applied, run `cd /home/dev/Desktop/projects/AI-InnovationHackathon/frontend && npm run build` and confirm it exits with code 0 and zero TypeScript errors. Then commit all changes with a descriptive message and push to `origin main`.

---

## Acceptance Criteria

### Backend API Health
- [ ] All 10 API endpoints used by the frontend return responses that structurally match the TypeScript types in `frontend/src/types/index.ts`
- [ ] No endpoint returns a 500 error on a valid realistic request
- [ ] Missing or incorrect fields in responses are identified and fixed

### Frontend Flow Completeness
- [ ] The user can complete the full critical path (Ingestion → Plan → Quiz → Analytics) without hitting a dead end, crash, or blank screen
- [ ] Every tab transition in `App.tsx` is guarded correctly — no tab renders with `null` data
- [ ] All async operations (API calls) have loading states and error handling visible to the user

### UI Consistency
- [ ] Zero components use `#fdfbf9`, `#2b1a07`, or any cream/brown hardcoded color
- [ ] Every clickable element (button, card, recommendation) has a visible hover state
- [ ] All empty states show an icon + descriptive message (no blank white boxes)

### Adaptive Loop
- [ ] After quiz submission, `profile.concept_mastery`, `profile.known_weak_areas`, and `profile.average_mastery_percent` reflect the quiz results when the Analytics tab loads
- [ ] `GET /profile/{id}/recommendations` returns at least one recommendation after a lesson is completed
- [ ] Clicking a recommendation in the Analytics tab successfully restarts the flow from Ingestion with the recommended topic pre-filled

### Build & Deploy
- [ ] `npm run build` exits with code 0 and no TypeScript errors
- [ ] All changes committed to `origin/main` with a clear commit message describing what was fixed

## 2026-09-04T17:43:33Z

# Teamwork Project Prompt — Draft

> Status: Step 2 — Defining requirements
> Goal: craft prompt → get user approval → delegate to teamwork_preview
> Requested team: [none — default]

Project description: ApniHelp is a full‑stack adaptive educational platform that generates short explanatory videos from provided documents. It should generate videos quickly (≤20 seconds of processing per minute of output), present a single “Generate Video” button, use a light colour theme (white, yellow, gray, dark blue), and display a photorealistic AI teacher avatar.

Working directory: ~/teamwork_projects/apnihelp

## Requirements

### R1. Video generation performance
The system must generate a video in ≤20 seconds of processing for each minute of final video length (e.g., a 5‑minute video ≤100 seconds, 10‑minute ≤200 seconds).

### R2. UI simplicity
The frontend must expose a single “Generate Video” button that triggers the whole pipeline for any uploaded document or input.

### R3. Light visual theme
The UI colour palette shall be a light theme based on a mixture of white, yellow, gray, and dark blue.

### R4. AI teacher avatar
The video presenter must be a photorealistic human‑like AI teacher image generated via an image model, not a cartoon illustration.

### R5. Project naming
All branding, repository names, and displayed titles shall use the name “ApniHelp”.

## Acceptance Criteria

- [ ] Video generation time meets R1 for test videos of 5 min and 10 min.
- [ ] The UI shows only one button labeled “Generate Video” and no other manual steps.
- [ ] The UI colour scheme matches the specified light palette across all pages.
- [ ] The generated video features a photorealistic teacher avatar that syncs with the narration.
- [ ] All visible project titles and repo names are “ApniHelp”.

---
*Next: when approved → delegate via invoke_subagent (see Delegation Protocol)*
