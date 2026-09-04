# Comprehensive Frontend Flow & Component State Transition Survey Report

**Project**: AI Teacher Adaptive Educational Platform  
**Target Codebase**: `frontend/src/`  
**Date**: September 2026  
**Auditor**: Teamwork Explorer (Read-Only Investigation)  

---

## 1. Executive Summary

A comprehensive investigation of the AI Teacher React/Vite frontend application was performed across all 5 pipeline stages (**Ingestion → Lesson Plan → Video & Checks → Quiz & Report → Profile & Analytics**), covering `App.tsx`, `services/api.ts`, `types/index.ts`, and all components in `components/{Ingestion,Planner,VideoPlayer,Assessment,Analytics,Profile,TutorChat,Header}`.

### Key Audit Findings:
1. **Critical Adaptive Loop Break (Topic Plan Generation 400 Error)**: When a learner clicks an AI recommendation or weak area refresher in the Analytics tab or Quiz report, `handleSelectTopicFromDashboard` calls `generatePlanForMaterial({ title: topic })`. However, `api.createLessonPlan` does not include the `topic` field in its TypeScript signature or HTTP payload. The backend `LessonPlanCreateRequest` validator rejects the request with `HTTP 400: ValueError: At least one of 'document_id', 'topic_id', or 'topic' must be provided.`. The error is silently swallowed in `App.tsx`, leaving the user stuck with no feedback.
2. **Guard Condition Failures Leading to Blank Screens**: Navigating directly via Header tabs to **Tab 2 (Lesson Plan)** or **Tab 3 (Video & Checks)** before generating data renders a completely blank screen because `App.tsx` guards (`currentTab === 'plan' && plan` and `currentTab === 'video' && videoManifest`) lack fallback empty states.
3. **API Route Path Mismatches**: In `services/api.ts`, `getLessonPlan` and `updateLessonPlan` target `${API_BASE}/lessons/plan/${planId}`. The backend router in `backend/app/api/lessons.py` defines routes as `GET /api/v1/lessons/{plan_id}` and `PUT /api/v1/lessons/{plan_id}`, causing 404 Not Found errors on direct plan retrieval or updates.
4. **Strict Theme & Color Violations (Requirement R3)**: Multiple components contain hardcoded hex colors that violate the dark slate theme:
   - `ProfileModal.tsx`: `bg-[#2b1a07]/70` (hardcoded brown background overlay, explicitly banned in R3).
   - `IngestionView.tsx`, `ProfileModal.tsx`, `SidePanelTutor.tsx`: Hardcoded orange (`#ff6f1e`, `#ce500a`) and hardcoded green (`#22c55e`) instead of Tailwind theme classes (`purple-500`/`indigo-500`/`emerald-400`).
5. **Missing Loading & Error States**:
   - Ingestion "Proceed" button does not show a loading spinner or disable when `generatePlanForMaterial` is running.
   - Video generation polling runs an indefinite `setInterval` that never terminates on repeated network or server errors.
   - Checkpoint answer evaluation in `InteractiveVideoPlayer.tsx` logs errors to console without showing user feedback on failure.

---

## 2. Component Hierarchy & Main Control Loop Analysis

### 2.1 State Architecture in `App.tsx`
`App.tsx` acts as the single source of truth for pipeline progression, active learning artifacts, and profile synchronization:

```
App.tsx (Root State Orchestrator)
 ├── currentTab: 'ingest' | 'plan' | 'video' | 'quiz' | 'analytics'
 ├── profile: LearnerProfile
 ├── activeMaterial: { documentId?, topicId?, title, summary } | null
 ├── plan: LessonPlan | null
 ├── isCreatingPlan: boolean
 ├── isGeneratingVideo: boolean, videoProgressPercent: number, videoCurrentStage: string
 ├── videoManifest: VideoManifest | null
 ├── isProfileModalOpen: boolean
 └── isTutorChatOpen: boolean
```

---

## 3. Tab-by-Tab Flow & State Transition Audit

### Tab 1: Ingestion (`IngestionView.tsx`)
* **Purpose**: Ingest source materials via file upload (PDF/DOCX/PPTX/TXT/MD) or parametric topic synthesis.
* **Flow**:
  1. **Upload Sub-tab**: Drag/drop or file selection → `POST /api/v1/materials/upload` → `DocumentMetadata` displayed in card → Click "Proceed to Configure Learner Profile & Plan".
  2. **Topic Sub-tab**: Enter topic and select subject category → `POST /api/v1/materials/topic` → `TopicIngestionResponse` displayed in card → Click "Proceed to Configure Learner Profile & Plan".
  3. **Transition**: Calls `onMaterialReady(material)` in `App.tsx` which invokes `generatePlanForMaterial(...)`.
* **Identified Issues**:
  - **No Loading Feedback on Proceed**: `onMaterialReady` initiates an async API call in `App.tsx` (`api.createLessonPlan`), but `IngestionView` has no prop or local indicator to show that plan generation is in progress. The user can click the button multiple times.
  - **No Prefilled Topic Support**: `IngestionView` has no props to receive a prefilled topic when restarting the ingestion flow from Analytics recommendations.
  - **Theme Violations**: Extensive use of `#ff6f1e`, `#ce500a`, and `#22c55e`.

---

### Tab 2: Lesson Plan (`LessonPlanEditor.tsx`)
* **Purpose**: Inspect personalized lesson structure, reorder modules, edit scripts, review LaTeX formulas/code snippets, customize profile constraints, and trigger AI video synthesis.
* **Flow**:
  1. Renders 2-column view: Pedagogical module sequence on the left, selected module inspector on the right.
  2. Clicking "Customize Level/Time" triggers `onOpenProfileModal()` → opens `ProfileModal.tsx` → on save, regenerates plan with updated parameters.
  3. Clicking "Approve & Generate AI Video" triggers `handleApproveAndGenerateVideo()` in `App.tsx`.
* **Identified Issues**:
  - **Blank Screen Guard Condition**: `{currentTab === 'plan' && plan && <LessonPlanEditor ... />}`. If the user clicks the tab before a plan exists, nothing renders.
  - **Plan Generation Error Swallowing**: If `createLessonPlan` fails in `App.tsx`, the error is only logged to `console.error` and `isCreatingPlan` resets to `false`, leaving the user on a blank or stuck screen.
  - **Video Generation Infinite Polling Risk**: If status polling encounters continuous network or server errors, `setInterval` continues indefinitely without timeout or error threshold.
  - **Low Contrast Elements**: Main lesson title and module headings use `text-slate-400` which has lower contrast against `bg-slate-900`.

---

### Tab 3: Video & Checks (`InteractiveVideoPlayer.tsx`)
* **Purpose**: Stream stitched lesson video, trigger automatic comprehension pauses at checkpoint markers, evaluate student answers, diagnose misconceptions with scaffolded re-explanations, and support mid-session language switching / tutor chat.
* **Flow**:
  1. HTML5 `<video>` plays `manifest.video_url`.
  2. Time update detects timestamp near `pause_markers[i].timestamp_sec`.
  3. Video pauses and displays Checkpoint Question overlay.
  4. User submits answer → `POST /api/v1/interactive/evaluate` → If correct, displays mastery confirmation and allows video resume; if incorrect, displays diagnosed root misconception, scaffolded analogy, and follow-up check.
  5. User can switch language (EN ↔ HI), open side-panel AI tutor, or click "Take Post-Quiz" (`onLessonComplete` → switches to Tab 4).
* **Identified Issues**:
  - **Blank Screen Guard Condition**: `{currentTab === 'video' && videoManifest && <InteractiveVideoPlayer ... />}`. No fallback empty state if user clicks Tab 3 directly.
  - **Silent Error on Answer Evaluation**: `handleAnswerSubmit` catches errors and only calls `console.error`, with no error banner inside the checkpoint overlay.

---

### Tab 4: Quiz & Report (`QuizView.tsx`)
* **Purpose**: Generate post-lesson diagnostic quiz (`POST /api/v1/assessment/generate`), collect answers, grade against rubrics (`POST /api/v1/assessment/submit`), and display comprehensive `LearningReport`.
* **Flow**:
  1. On mount / `lessonId` change: calls `api.generateQuiz(lessonId, studentId, 3)`.
  2. User selects answers for MCQs or types short answer responses.
  3. User clicks "Submit & Generate Diagnostic Report" → `api.submitQuiz(...)`.
  4. Backend grades submission, updates student profile, and returns `LearningReport`.
  5. `LearningReport` displays mastery percentage circle, strong concepts, weak concepts, resolved misconceptions, and recommended next topics.
  6. CTAs: "Retake Assessment" (reloads quiz), "View Full Learning Analytics & Profile" (loads profile and switches to Tab 5), or click recommended next topic (restarts learning loop).
* **Identified Issues**:
  - **Error Recovery State**: If `loadQuiz` fails on initial load, only a small error box renders without a "Retry" CTA button.
  - **Recommendation Click Breakdown**: Clicking a recommended next topic invokes `handleSelectTopicFromDashboard` which fails due to the missing `topic` parameter in `createLessonPlan`.

---

### Tab 5: Profile & Analytics (`AnalyticsDashboard.tsx`)
* **Purpose**: Comprehensive learning analytics, mastery progress bars, prerequisite refresher gap list, AI next-step recommendations, and historical session logs.
* **Flow**:
  1. Displays profile stats: Lessons Completed, Average Mastery (%), Total Study Time.
  2. Concept Mastery Index: Color-coded progress bars (emerald for ≥75%, amber for <75%).
  3. Targeted Gaps & Prerequisite Refreshers: Clickable cards for each weak area in `profile.known_weak_areas`.
  4. AI Teacher Adaptive Recommendations: Loaded from `GET /api/v1/profile/{id}/recommendations`.
  5. Learning History: Timeline of completed assessments.
* **Identified Issues**:
  - **Stale Profile on Direct Tab Switch**: `loadProfile()` is only called when arriving via `QuizView`'s "View Analytics" button. If the user clicks the Header tab directly, profile metrics might be stale.
  - **Recommendation Click Failure**: Clicking any recommendation triggers `handleSelectTopicFromDashboard(rec.topic)` which fails with HTTP 400 on `POST /api/v1/lessons/plan`.

---

## 4. API Endpoints & Contract Discrepancy Matrix

| Frontend Method (`api.ts`) | Endpoint Path Used in Frontend | Backend Defined Route (`backend/app/api/`) | Status / Issue | Fix Required |
|---|---|---|---|---|
| `uploadDocument` | `POST /api/v1/materials/upload` | `POST /api/v1/materials/upload` | ✅ Exact Match | None |
| `ingestTopic` | `POST /api/v1/materials/topic` | `POST /api/v1/materials/topic` | ✅ Exact Match | None |
| `createLessonPlan` | `POST /api/v1/lessons/plan` | `POST /api/v1/lessons/plan` | ⚠️ **Payload Schema Mismatch** | Add `topic?: string` and `subject_domain?: string` to payload |
| `getLessonPlan` | `GET /api/v1/lessons/plan/{id}` | `GET /api/v1/lessons/{plan_id}` | ❌ **404 Route Mismatch** | Change to `${API_BASE}/lessons/${planId}` |
| `updateLessonPlan` | `PUT /api/v1/lessons/plan/{id}` | `PUT /api/v1/lessons/{plan_id}` | ❌ **404 Route Mismatch** | Change to `${API_BASE}/lessons/${planId}` |
| `generateVideo` | `POST /api/v1/lessons/generate-video` | `POST /api/v1/lessons/generate-video` | ✅ Exact Match | None |
| `getVideoStatus` | `GET /api/v1/lessons/video-status/{id}` | `GET /api/v1/lessons/video-status/{id}` | ✅ Exact Match | None |
| `getVideoManifest` | `GET /api/v1/lessons/video-manifest/{id}` | `GET /api/v1/lessons/video-manifest/{id}` | ✅ Exact Match | None |
| `evaluateAnswer` | `POST /api/v1/interactive/evaluate` | `POST /api/v1/interactive/evaluate` | ✅ Exact Match | None |
| `switchLanguage` | `POST /api/v1/interactive/switch-language` | `POST /api/v1/interactive/switch-language` | ✅ Exact Match | None |
| `tutorChat` | `POST /api/v1/interactive/chat` | `POST /api/v1/interactive/chat` | ✅ Exact Match | None |
| `generateQuiz` | `POST /api/v1/assessment/generate` | `POST /api/v1/assessment/generate` | ✅ Exact Match | None |
| `submitQuiz` | `POST /api/v1/assessment/submit` | `POST /api/v1/assessment/submit` | ✅ Exact Match | None |
| `getProfile` | `GET /api/v1/profile/{id}` | `GET /api/v1/profile/{student_id}` | ✅ Exact Match | None |
| `updateProfile` | `PUT /api/v1/profile/{id}` | `PUT /api/v1/profile/{student_id}` | ✅ Exact Match | None |
| `getRecommendations` | `GET /api/v1/profile/{id}/recommendations` | `GET /api/v1/profile/{student_id}/recommendations` | ✅ Exact Match | None |

---

## 5. UI Consistency & Theme Audit (Requirement R3)

### 5.1 Hardcoded Colors Audit

| File | Line(s) | Hardcoded Color Found | Violation Description | Target Replacement |
|---|---|---|---|---|
| `ProfileModal.tsx` | 48 | `bg-[#2b1a07]/70` | Brown overlay breaking slate dark theme | `bg-slate-950/80` |
| `ProfileModal.tsx` | 53, 74, 112, 118, 165, 187 | `text-[#ff6f1e]`, `border-[#ff6f1e]` | Hardcoded orange accents | `text-purple-400`, `border-purple-500` |
| `ProfileModal.tsx` | 129 | `text-[#22c55e]` | Hardcoded green | `text-emerald-400` |
| `IngestionView.tsx` | 87, 98 | `text-[#ff6f1e]` | Orange tab active text | `text-purple-400` |
| `IngestionView.tsx` | 140, 164, 181, 282, 299 | `text-[#ff6f1e]` | Orange icons and text | `text-purple-400` |
| `IngestionView.tsx` | 215, 261 | `bg-[#ff6f1e]` | Orange category and submit buttons | `bg-purple-600 hover:bg-purple-500` |
| `IngestionView.tsx` | 247 | `hover:border-[#ce500a]/60` | Dark orange border hover | `hover:border-purple-500/60` |
| `IngestionView.tsx` | 174, 292 | `text-[#22c55e]`, `border-[#22c55e]/40` | Hardcoded green status tag | `text-emerald-400`, `border-emerald-500/40` |
| `SidePanelTutor.tsx` | 95, 129, 144, 145, 175 | `text-[#ff6f1e]` | Orange bot icon and spinner | `text-purple-400` |
| `SidePanelTutor.tsx` | 136, 200 | `bg-[#ff6f1e]` | Orange user bubbles & submit button | `bg-purple-600 hover:bg-purple-500` |
| `SidePanelTutor.tsx` | 109 | `text-[#22c55e]` | Hardcoded green | `text-emerald-400` |

---

## 6. Concrete Fix Recommendations & Implementation Blueprints

### Fix 1: Fix `createLessonPlan` Payload & Topic Flow in `api.ts` and `App.tsx`
**Files**: `frontend/src/services/api.ts`, `frontend/src/App.tsx`

**In `frontend/src/services/api.ts`**:
```typescript
// Update createLessonPlan parameter type:
async createLessonPlan(payload: {
  learner_profile: {
    student_id?: string;
    level: string;
    language: string;
    time_budget_min: number;
    prior_knowledge?: string;
    learning_goal?: string;
  };
  document_id?: string;
  topic_id?: string;
  topic?: string;
  subject_domain?: string;
}): Promise<LessonPlan> {
  const res = await fetch(`${API_BASE}/lessons/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return handleResponse<LessonPlan>(res);
}

// Fix getLessonPlan and updateLessonPlan paths:
async getLessonPlan(planId: string): Promise<LessonPlan> {
  const res = await fetch(`${API_BASE}/lessons/${planId}`);
  return handleResponse<LessonPlan>(res);
}

async updateLessonPlan(planId: string, updatedPlan: Partial<LessonPlan>): Promise<LessonPlan> {
  const res = await fetch(`${API_BASE}/lessons/${planId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updatedPlan),
  });
  return handleResponse<LessonPlan>(res);
}
```

**In `frontend/src/App.tsx`**:
```typescript
const generatePlanForMaterial = async (
  material: { documentId?: string; topicId?: string; title: string },
  level: LearnerLevel,
  language: string,
  timeBudgetMin: number,
  priorKnowledge?: string,
  learningGoal?: string
) => {
  setIsCreatingPlan(true);
  setPlanError(null);
  try {
    const newPlan = await api.createLessonPlan({
      learner_profile: {
        student_id: profile.student_id,
        level,
        language,
        time_budget_min: timeBudgetMin,
        prior_knowledge: priorKnowledge,
        learning_goal: learningGoal,
      },
      document_id: material.documentId,
      topic_id: material.topicId,
      topic: !material.documentId && !material.topicId ? material.title : undefined,
    });
    setPlan(newPlan);
    setCurrentTab('plan');
  } catch (err: any) {
    console.error('Failed to create lesson plan:', err);
    setPlanError(err.message || 'Failed to create lesson plan.');
  } finally {
    setIsCreatingPlan(false);
  }
};
```

---

### Fix 2: Guard Condition Fallbacks & Empty States in `App.tsx`
**File**: `frontend/src/App.tsx`

Add fallback UI for tabs when data is not yet generated:
```tsx
{currentTab === 'plan' && (
  plan ? (
    <LessonPlanEditor
      plan={plan}
      onUpdatePlan={setPlan}
      onApproveAndGenerateVideo={handleApproveAndGenerateVideo}
      isGeneratingVideo={isGeneratingVideo}
      videoProgressPercent={videoProgressPercent}
      videoCurrentStage={videoCurrentStage}
      onOpenProfileModal={() => setIsProfileModalOpen(true)}
    />
  ) : (
    <div className="max-w-xl mx-auto py-20 px-4 text-center space-y-4">
      <div className="w-16 h-16 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center mx-auto text-purple-400">
        <Sparkles className="w-8 h-8" />
      </div>
      <h2 className="text-xl font-bold text-slate-100">No Lesson Plan Generated Yet</h2>
      <p className="text-xs text-slate-400 leading-relaxed">
        Upload a document or choose an academic topic in the Ingestion stage to synthesize your personalized lesson blueprint.
      </p>
      <button
        onClick={() => setCurrentTab('ingest')}
        className="px-5 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold transition-all shadow-lg shadow-purple-600/30"
      >
        Start at Ingestion
      </button>
    </div>
  )
)}

{currentTab === 'video' && (
  videoManifest ? (
    <InteractiveVideoPlayer
      manifest={videoManifest}
      onLessonComplete={() => setCurrentTab('quiz')}
      onToggleTutorChat={() => setIsTutorChatOpen((prev) => !prev)}
      currentLanguage={currentLanguage}
      onLanguageSwitch={(l: string) => setCurrentLanguage(l as LanguageCode)}
    />
  ) : (
    <div className="max-w-xl mx-auto py-20 px-4 text-center space-y-4">
      <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center mx-auto text-indigo-400">
        <PlayCircle className="w-8 h-8" />
      </div>
      <h2 className="text-xl font-bold text-slate-100">No Lesson Video Ready</h2>
      <p className="text-xs text-slate-400 leading-relaxed">
        Review and approve a lesson plan in the Lesson Plan tab to generate the AI video lecture with interactive checkpoint questions.
      </p>
      <button
        onClick={() => setCurrentTab(plan ? 'plan' : 'ingest')}
        className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition-all shadow-lg shadow-indigo-600/30"
      >
        {plan ? 'Go to Lesson Plan' : 'Start at Ingestion'}
      </button>
    </div>
  )
)}
```

---

### Fix 3: UI Theme Purification across `ProfileModal.tsx`, `IngestionView.tsx`, and `SidePanelTutor.tsx`
- Replace `bg-[#2b1a07]/70` in `ProfileModal.tsx:48` with `bg-slate-950/80`.
- Replace all instances of `text-[#ff6f1e]` with `text-purple-400`.
- Replace all instances of `bg-[#ff6f1e]` with `bg-purple-600 hover:bg-purple-500`.
- Replace `hover:border-[#ce500a]/60` with `hover:border-purple-500/60`.
- Replace all instances of `text-[#22c55e]` and `border-[#22c55e]/40` with `text-emerald-400` and `border-emerald-500/40`.

---

### Fix 4: Video Generation Polling Resilience & Timeout
**File**: `frontend/src/App.tsx`
- Add a timeout and retry limit to `handleApproveAndGenerateVideo` so that polling terminates after 120 seconds or 5 consecutive network errors.
- Display error state in UI if video generation fails or times out.

---

## 7. Verification Strategy & Acceptance Checklist

| Requirement | Test Scenario | Expected Outcome |
|---|---|---|
| **R1. Backend API Match** | Call all endpoints with realistic payloads | 10/10 endpoints return matching schemas without 4xx/5xx |
| **R2. Critical Path Flow** | Ingestion → Plan → Video → Quiz → Analytics | 100% completion without blank screens, crashes, or dead ends |
| **R2. Tab Navigation** | Click Header tabs out of order on initial load | Clean empty state cards with CTAs rendered; zero blank screens |
| **R3. Theme Consistency** | Search codebase for `#2b1a07`, `#ff6f1e`, `#ce500a` | Zero occurrences of non-theme colors |
| **R4. Adaptive Loop** | Submit quiz → verify profile updates → click recommendation | Recommendation seamlessly restarts Ingestion/Plan with prefilled topic |
| **R5. Build** | Run `npm run build` | Exits code 0 with zero TypeScript errors |
