# Original User Request

## Initial Request — 2026-09-02T11:02:36+05:30

Simulate the entire user journey end-to-end across the critical 4-stage path (Ingestion -> Lesson Plan -> Quiz & Report -> Profile & Analytics), audit every API endpoint, find every broken flow, UI inconsistency, backend error, and logic gap, fix them in-place, and verify the full loop works from start to finish.

Requirements to fulfill:
- R1. Backend API Audit: Test every API endpoint used by the frontend against FastAPI at localhost:8000. Send realistic requests, check response shape against frontend TypeScript types (`frontend/src/types/index.ts`), fix backend issues (4xx/5xx errors, missing fields, type mismatches).
- R2. Frontend Flow Audit: Simulate the critical path (Ingestion -> Lesson Plan -> Quiz & Report -> Analytics) by reading component code and tracing state transitions in `App.tsx`. Fix broken tab transitions, missing loading/error states, uncaught promise rejections, state bugs, guard conditions, and dead ends.
- R3. UI Consistency & Integrity: Ensure strict dark slate theme (`bg-slate-950`/`slate-900`, `purple`/`indigo` brand, `emerald` accent, `amber` warnings). Fix any hardcoded cream/brown colors (`#fdfbf9`, `#2b1a07`), add missing hover states on interactive elements, fix button/div styling issues, and ensure proper empty states (icon + descriptive message). Match `Header.tsx` and `AnalyticsDashboard.tsx`.
- R4. Adaptive Loop Integrity: Verify quiz submission updates `profile.concept_mastery`, `profile.known_weak_areas`, and `profile.average_mastery_percent` on the backend profile, and `GET /profile/{id}/recommendations` returns recommendations. Confirm clicking recommendations pre-fills Ingestion topic.
- R5. Rebuild and Git Push: Run `cd /home/dev/Desktop/projects/AI-InnovationHackathon/frontend && npm run build` (must exit 0 with zero TS errors), commit all changes with a descriptive message, and push to `origin main`.

## Follow-up — 2026-09-04T17:43:33Z

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
