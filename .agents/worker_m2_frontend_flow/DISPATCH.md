## 2026-09-02T11:11:40Z
<USER_REQUEST>
You are a Worker implementing Milestone M2: Frontend Flow, Guards & Empty States.

Authoritative Request: /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/ORIGINAL_REQUEST.md (READ THIS FIRST)
Survey Report: /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_survey_frontend_flow/survey_frontend_flow_report.md
Project Plan: /home/dev/Desktop/projects/AI-InnovationHackathon/PROJECT.md
Your working directory: /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/worker_m2_frontend_flow

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Exclusive File Ownership:
- frontend/src/services/api.ts
- frontend/src/App.tsx
- frontend/src/types/index.ts

Your Tasks:
1. In frontend/src/services/api.ts:
   - In `createLessonPlan`: add `topic?: string` to parameters/payload so it sends `{ learner_profile, document_id, topic_id, topic }` to POST /api/v1/lessons/plan.
   - In `getLessonPlan` and `updateLessonPlan`: ensure paths correctly match backend endpoints (e.g., `${API_BASE}/lessons/${planId}`).

2. In frontend/src/App.tsx:
   - Fix `handleSelectTopicFromDashboard(topic)` and `generatePlanForMaterial`:
     Ensure `api.createLessonPlan` receives `topic: material.title || (material as any).topic` so `POST /api/v1/lessons/plan` does not fail with 400 Bad Request when restarting from an AI recommendation.
   - In Tab 2 (`plan`), when `!plan`:
     Render an empty state fallback card (dark slate theme, e.g. `bg-slate-900 border border-slate-800 rounded-xl p-8 text-center text-slate-200`) with an icon, title "No Lesson Plan Generated Yet", message "Upload learning materials or choose a topic in the Ingestion tab to create your lesson plan.", and a primary button "Go to Ingestion" that switches tab to 'ingest'.
   - In Tab 3 (`video`), when `!videoManifest`:
     Render an empty state fallback card with an icon, title "No Video Ready Yet", message "Approve and generate a lesson plan first to produce interactive video checkpoints.", and buttons to switch to 'plan' or 'ingest'.
   - Add visible error alerts and loading indicators for plan creation and video generation rather than silently swallowing errors.

3. Verification:
   - Run `cd /home/dev/Desktop/projects/AI-InnovationHackathon/frontend && npm run build` and ensure exit code 0 with zero TypeScript errors.
   - Write handoff.md in your working directory documenting changes and build verification.

Communicate completion back to orchestrator via send_message.
</USER_REQUEST>
