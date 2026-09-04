# Dispatch: worker_m2_frontend_ui

## Objective
Implement Milestone 2: Frontend Single-Button Flow & Light Visual Theme (R2, R3, R5-Frontend) for ApniHelp.

## Working Directory
`/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/worker_m2_frontend_ui`

## Exclusively Owned Files
- `frontend/src/*` (all files under `frontend/src/`)
- `frontend/index.html`
- `frontend/index.css`
- `frontend/tailwind.config.js`
- `frontend/package.json`

## Inputs & Context
1. Read `/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/ORIGINAL_REQUEST.md` (lines 81-120).
2. Read the investigation report from `explorer_r3_frontend_ui`:
   - `/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_r3_frontend_ui/analysis.md`
   - `/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_r3_frontend_ui/handoff.md`

## Specific Instructions
1. **R2. UI Simplicity (Single 'Generate Video' Button)**:
   - On the input / ingestion view (`frontend/src/components/Ingestion/IngestionView.tsx`), remove the intermediate button *"Proceed to Configure Learner Profile & Plan"*.
   - Expose a single primary, prominent button labeled **"Generate Video"**.
   - In `frontend/src/App.tsx`, implement a chained async generation handler:
     When the user clicks "Generate Video", the app automatically:
     (1) Ingests the material (via `api.uploadDocument` or `api.ingestTopic`),
     (2) Automatically creates the lesson plan (via `api.createLessonPlan` using active/default profile),
     (3) Automatically triggers video generation (via `api.generateVideo`),
     (4) Polls status until completed, fetches manifest, and smoothly transitions directly into `InteractiveVideoPlayer`.
   - Maintain the downstream learning loop: once the video plays, interactive pause checkpoints, the post-video quiz (`QuizView`), diagnostic learning report, and continuous adaptive analytics (`AnalyticsDashboard`) remain fully functional.
2. **R3. Light Visual Theme (White, Yellow, Gray, Dark Blue)**:
   - Complete replacement of dark slate (`bg-slate-950`, `bg-slate-900`, `border-slate-800`) and purple colors across `index.html`, `index.css`, `App.tsx`, and all components (`Header.tsx`, `IngestionView.tsx`, `LessonPlanEditor.tsx`, `InteractiveVideoPlayer.tsx`, `QuizView.tsx`, `AnalyticsDashboard.tsx`, `ProfileModal.tsx`, `SidePanelTutor.tsx`).
   - Use the approved light palette:
     - **Surfaces**: `bg-white` (`#ffffff`) for cards, dialogs, inputs, panels.
     - **Backdrop & Neutrals**: `bg-slate-50` (`#f8fafc`), `border-gray-200` (`#e2e8f0`), `text-slate-600`.
     - **Primary Dark Blue**: `text-blue-950` / `text-slate-900` (`#0f172a`, `#172554`) for titles and high-contrast text, `bg-blue-900` for dark blue accents.
     - **Signature Warm Yellow**: `bg-yellow-400 hover:bg-yellow-500 text-slate-950 font-bold` for the primary "Generate Video" CTA button.
3. **R5. Frontend Branding to "ApniHelp"**:
   - `frontend/index.html`: Update title to "ApniHelp — Adaptive Educational Platform".
   - `frontend/src/components/Header.tsx`: Brand name "ApniHelp", remove "AI Teacher".
   - `frontend/package.json`: `"name": "apnihelp-frontend"`.
   - Update all references in `SidePanelTutor.tsx`, `InteractiveVideoPlayer.tsx`, `AnalyticsDashboard.tsx`, `ProfileModal.tsx`, etc., from "AI Teacher" to "ApniHelp".
4. **Build Verification**:
   - Run `cd /home/dev/Desktop/projects/AI-InnovationHackathon/frontend && npm run build` and confirm exit code 0 with zero TypeScript errors.

## MANDATORY INTEGRITY WARNING
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Deliver your results in `handoff.md` and report back with `send_message`.

## 2026-09-04T17:57:42Z
You are worker_m2_frontend_ui, a specialized implementation worker.
Your working directory is: /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/worker_m2_frontend_ui
Please read your assignment file: /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/worker_m2_frontend_ui/DISPATCH.md
MANDATORY: Read /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/ORIGINAL_REQUEST.md before starting work. Do NOT summarize or filter it — read lines 81-120 directly.

Your mission:
Implement Milestone 2 (Frontend Flow & Light Theme).
- R2 UI Simplicity: On the ingestion view, remove the intermediate manual button and provide a single primary 'Generate Video' CTA button. In App.tsx, chain material ingestion -> lesson planning -> video generation automatically in one click, transitioning directly to the video player while keeping interactive pause checkpoints, quiz, and analytics fully functional.
- R3 Light Visual Theme: Replace all dark slate/purple styles across index.html, index.css, and all 9 components with the light palette (white #ffffff, light gray #f8fafc/#e2e8f0, dark blue #0f172a/#172554, and warm yellow #facc15/#eab308 for the 'Generate Video' CTA button).
- R5 Branding: Update all titles, header text, and metadata to "ApniHelp".
- Verify frontend build: Run `cd /home/dev/Desktop/projects/AI-InnovationHackathon/frontend && npm run build` and confirm exit code 0.
- Write a thorough handoff.md in your working directory.

