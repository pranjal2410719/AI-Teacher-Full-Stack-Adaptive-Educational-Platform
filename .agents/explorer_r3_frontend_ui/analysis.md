# ApniHelp Frontend UI & Visual Theme Investigation Report

**Agent**: `explorer_r3_frontend_ui`  
**Date**: 2026-09-04  
**Context**: Transitioning AI Teacher to **ApniHelp** — a full-stack adaptive educational platform delivering rapid AI-generated explanatory videos with photorealistic avatars.  
**Focus Areas**:  
1. **R2. UI Simplicity**: Expose a single "Generate Video" button triggering the whole pipeline for any uploaded document or input with zero manual intermediate steps, while keeping interactive video checkpoints, quiz, and analytics seamlessly integrated.  
2. **R3. Light Visual Theme**: Establish a clean, accessible light colour palette based on a mixture of **white, yellow, gray, and dark blue** across all pages and modals, replacing the legacy dark slate/purple theme.  
3. **R5. Project Naming**: Update all visible project titles, branding, and repository configurations to **ApniHelp**.

---

## 1. Executive Summary

The legacy frontend implementation relied on a fragmented, multi-step tabbed workflow:
- The learner had to upload a document or type a topic in the **Ingestion** tab, click an intermediate button (*"Proceed to Configure Learner Profile & Plan"*), wait for a lesson plan to generate, land in the **Lesson Plan** tab, manually review JSON-based segment modules, click a second button (*"Approve & Generate AI Video"*), wait for async polling, land in the **Video** tab, manually navigate to the **Quiz** tab, and then visit the **Analytics** tab.
- Visually, the app used an aggressive dark slate palette (`bg-slate-950`, `bg-slate-900`, `border-slate-800`) paired with deep purple/indigo gradients and low-contrast muted slate text.

To satisfy **R2** and **R3**, this investigation provides:
1. An architecture to collapse the multi-step initiation into a **single, prominent "Generate Video" button**. When clicked, the pipeline asynchronously chains document ingestion/topic grounding, automated lesson plan formulation, and video generation without requiring any manual clicks or intermediate approvals, while smoothly transitioning the user into the interactive video player, post-video quiz, and analytics dashboard.
2. A complete design token mapping replacing all dark slate and purple styles with a harmonized, WCAG-compliant light palette:
   - **White (`#ffffff`)**: Clean card surfaces, modal dialog bodies, and active elements.
   - **Light Gray (`#f8fafc` / `#e2e8f0` / `#64748b`)**: Neutral page backgrounds (`bg-slate-50`), crisp dividing borders (`border-gray-200`), and secondary text.
   - **Dark Blue (`#0f172a` / `#172554` / `#1e3a8a`)**: Primary brand typography, headings, authoritative headers, and primary accent elements.
   - **Warm Vibrant Yellow (`#facc15` / `#eab308`)**: The signature primary CTA button (*"Generate Video"*), key highlight chips, attention badges, and active progress accents.

---

## 2. UI Simplicity (R2): One-Click "Generate Video" Flow

### 2.1 Audit of Existing Friction & Intermediate Steps

Tracing `frontend/src/App.tsx`, `frontend/src/components/Ingestion/IngestionView.tsx`, and `frontend/src/components/Planner/LessonPlanEditor.tsx`:

| Step # | User Action in Current App | Technical Event | Friction / Violation of R2 |
|---|---|---|---|
| **Step 1** | Drag/drop or browse a file in `IngestionView.tsx:120-158` | File uploads automatically to `POST /api/v1/materials/upload` | Requires file selection. |
| **Step 2 (Manual Friction)** | User must inspect card and click *"Proceed to Configure Learner Profile & Plan"* (`IngestionView.tsx:186-195`) | Calls `onMaterialReady(material)` in `App.tsx:123` | **Intermediate manual step**. Blocks progression until user clicks. |
| **Step 3** | App calls `POST /api/v1/lessons/plan` (`App.tsx:140`) | Generates `LessonPlan` and forces tab transition to `'plan'` (`App.tsx:154`) | Navigation disruption; user did not ask to inspect raw pedagogical modules. |
| **Step 4 (Manual Friction)** | User lands on `LessonPlanEditor.tsx`, reviews modules, and must click *"Approve & Generate AI Video"* (`LessonPlanEditor.tsx:118-133`) | Calls `onApproveAndGenerateVideo()` in `App.tsx:163` | **Second manual roadblock**. R2 states the frontend must expose a single 'Generate Video' button with *zero manual intermediate steps*. |
| **Step 5** | Video generation task is created (`POST /api/v1/lessons/generate-video`) and polled | Polls `GET /api/v1/lessons/video-status/{task_id}` every 1500ms | Async polling runs in background. |
| **Step 6** | Status reaches `'completed'` | Fetches manifest from `GET /api/v1/lessons/video-manifest/{id}` and switches to `'video'` (`App.tsx:201`) | Automatic transition. |

### 2.2 Proposed One-Click Architecture

Under the new ApniHelp architecture, the input screen exposes **one single primary action button labeled "Generate Video"**.

```
+-----------------------------------------------------------------------------------+
|  ApniHelp                                               [Language: EN]  [Profile] |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|                   Transform Any Document or Topic into an                         |
|                         Interactive AI Video Lesson                               |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  |                                                                             |  |
|  |   [ Upload Document ]            [ Type Topic / Prompt ]                    |  |
|  |                                                                             |  |
|  |   +---------------------------------------------------------------------+   |  |
|  |   |                                                                     |   |  |
|  |   |    Drag & drop your PDF, DOCX, PPTX or lecture notes here           |   |  |
|  |   |    (or choose a curriculum topic below)                             |   |  |
|  |   |                                                                     |   |  |
|  |   +---------------------------------------------------------------------+   |  |
|  |                                                                             |  |
|  |   Selected: "Calculus_Limits_Continuity.pdf" (Ready for synthesis)          |  |
|  |                                                                             |  |
|  |   =======================================================================   |  |
|  |   ||                    [ GENERATE VIDEO ]                             ||   |  |
|  |   =======================================================================   |  |
|  |   (Single click triggers Document Ingestion -> Lesson Planning -> Video)    |  |
|  +-----------------------------------------------------------------------------+  |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

#### Pipeline Chaining in `App.tsx`:
Instead of requiring manual intermediate confirmations, clicking **"Generate Video"** invokes `handleStartPipeline()`:
1. **Material Stage**:
   - If a file is selected: calls `api.uploadDocument(file)`.
   - If a topic is provided: calls `api.ingestTopic(topic)`.
2. **Planning Stage (Automatic)**:
   - Uses the returned document ID or topic ID with the learner's profile preferences (`profile.preferred_level`, `currentLanguage`, default 15-minute time budget).
   - Calls `api.createLessonPlan(...)` immediately.
3. **Video Stage (Automatic)**:
   - Immediately takes `newPlan.plan_id` and calls `api.generateVideo(newPlan.plan_id)`.
   - Initiates async polling against `api.getVideoStatus(task_id)`.
4. **Live Progress Feedback**:
   - During generation (which completes rapidly per R1 ≤20s/min), a clean, animated progress card displays real-time stage updates:
     - *Phase 1: Ingesting & indexing semantic knowledge (Done)*
     - *Phase 2: Generating structured lesson plan & checkpoints (Done)*
     - *Phase 3: Synthesizing neural narration & photorealistic AI teacher avatar (Polling %)*
5. **Direct Video Transition**:
   - As soon as polling detects `'completed'`, the frontend retrieves the video manifest (`api.getVideoManifest(...)`) and switches the view directly to the `InteractiveVideoPlayer`.

### 2.3 Downstream Continuity: Checkpoints, Quiz, and Analytics

Simplifying the generation initiation does **not** degrade the downstream interactive capabilities:
- **Interactive Checkpoints**: As the video plays, pause markers defined in the manifest pause playback at predetermined timestamps (`currentTime ≈ timestamp_sec`). The student answers the checkpoint question in an overlay, receives instant feedback, and resumes video.
- **Post-Lesson Quiz**: When the video finishes (or when the learner clicks *"Take Post-Quiz"* in the video controls bar), the app smoothly transitions to `QuizView`.
- **Diagnostic Learning Report**: Upon quiz submission, the learner receives an immediate mastery report detailing scores, strong concepts, and areas for revision.
- **Analytics & Continuous Adaptive Loop**: Clicking *"View Full Learning Analytics & Profile"* in the quiz report reloads the student profile and displays `AnalyticsDashboard`. Clicking any recommended topic pre-populates the input on the home screen and allows immediate one-click generation of the next adaptive lesson.

### 2.4 Header Navigation Refactoring

The legacy header displayed 5 numbered tabs: `1. Ingestion`, `2. Lesson Plan`, `3. Video & Checks`, `4. Quiz & Report`, `5. Profile & Analytics`.
To reinforce R2:
- Remove the manual "2. Lesson Plan" tab from primary navigation, as lesson plan generation is now a silent, automated sub-step of video generation.
- Streamline the remaining navigation into clear, purposeful destinations:
  - **Create Video** (or **Studio**): Home / Ingestion with the single "Generate Video" button.
  - **Video Player**: Active once a video has been generated.
  - **Quiz**: Accessible after video or when a lesson is active.
  - **Analytics**: Learner profile, mastery index, and personalized recommendations.

---

## 3. Light Visual Theme (R3): Detailed Color Mapping

The requirement mandates:
> *"The UI colour palette shall be a light theme based on a mixture of white, yellow, gray, and dark blue across all pages."*

### 3.1 Design System Tokens & Semantic Assignments

| Color Family | Hex Value | Tailwind Class | Semantic Usage & Component Role |
|---|---|---|---|
| **White** | `#ffffff` | `bg-white`, `text-white` (on dark elements) | Primary card containers, modal dialogue bodies, input form surfaces, dropdown menus, button text on dark blue buttons. |
| **Light Gray (Background)** | `#f8fafc` | `bg-slate-50` / `bg-gray-50` | Full-page backdrop (`body`, main viewport container). Soft, low eye-strain surface. |
| **Muted Gray (Subtle Fill)** | `#f1f5f9` / `#f3f4f6` | `bg-slate-100` / `bg-gray-100` | Secondary backgrounds, inactive tab pills, subtle code block backgrounds, empty progress tracks. |
| **Border Gray** | `#e2e8f0` / `#e5e7eb` | `border-slate-200` / `border-gray-200` | Card borders, table dividers, form field outlines, modal dividers. |
| **Text Gray (Body/Subtle)** | `#475569` / `#64748b` | `text-slate-600` / `text-slate-500` | Subtitles, helper text, timestamps, secondary labels, metadata tags. |
| **Dark Blue (Brand / Text)** | `#0f172a` / `#172554` | `text-slate-900` / `text-blue-950` | Primary headings (`h1`, `h2`, `h3`), card headlines, high-contrast readable typography. |
| **Dark Blue (Elements)** | `#1e3a8a` / `#172554` | `bg-blue-900`, `hover:bg-blue-800` | Primary brand badges, navigation accents, secondary solid action buttons, user avatar circles. |
| **Dark Blue (Header)** | `#0f172a` or `#ffffff` | `bg-white border-b border-gray-200` | Clean, luminous white navbar with dark blue brand lettering and yellow accent icons. |
| **Vibrant Warm Yellow** | `#facc15` / `#eab308` | `bg-yellow-400`, `hover:bg-yellow-500` | **The Signature "Generate Video" CTA button**, active state highlights, star icons, primary interactive focus rings. |
| **Yellow Accent Text** | `#0f172a` | `text-slate-950` (on yellow bg) | High-contrast font on yellow buttons (ensures strict WCAG AAA contrast ratio of >10:1). |
| **Yellow Badge / Pill** | `#fef9c3` / `#854d0e` | `bg-yellow-100 text-yellow-800 border-yellow-300` | Accent chips, "AI Teacher" status badges, highlight alerts. |

### 3.2 Contrast & Accessibility Analysis (WCAG 2.1 Compliance)

- **Yellow Button Accessibility**: Yellow (`#facc15`) against white text fails WCAG (<2:1 contrast). Therefore, all yellow buttons **must** use dark slate/dark blue text (`#020617` or `#0f172a`), achieving a contrast ratio of **10.8:1** (exceeding WCAG AAA minimum of 7:1).
- **Body Text**: Dark slate (`#0f172a` / `#1e293b`) on white (`#ffffff`) gives a contrast ratio of **15.4:1**, ensuring optimal readability across all lighting environments.
- **Secondary Text**: Gray (`#475569`) on white (`#ffffff`) gives a contrast ratio of **7.5:1** (passes WCAG AAA).

---

## 4. Component-by-Component Style Audit & Replacement Specifications

### 4.1 Global Styles & HTML Shell

#### `frontend/index.html`
- **Current**:
  ```html
  <title>AI Teacher — Adaptive Educational Platform</title>
  <body class="bg-slate-950 text-slate-50 min-h-screen antialiased selection:bg-purple-500 selection:text-white font-sans">
  ```
- **Replacement**:
  ```html
  <title>ApniHelp — AI Adaptive Educational Platform</title>
  <body class="bg-slate-50 text-slate-900 min-h-screen antialiased selection:bg-yellow-300 selection:text-slate-900 font-sans">
  ```

#### `frontend/src/index.css`
- **Current**:
  ```css
  body {
    margin: 0;
    background-color: #020617;
    color: #f8fafc;
    font-family: 'Inter', sans-serif;
  }
  ::-webkit-scrollbar-track { background: #020617; }
  ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 4px; }
  ::-webkit-scrollbar-thumb:hover { background: #334155; }
  ```
- **Replacement**:
  ```css
  body {
    margin: 0;
    background-color: #f8fafc;
    color: #0f172a;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  }
  ::-webkit-scrollbar { width: 6px; height: 6px; }
  ::-webkit-scrollbar-track { background: #f1f5f9; }
  ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
  ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
  ```

---

### 4.2 Component: `Header.tsx`
- **File**: `frontend/src/components/Header.tsx`
- **Current Dark Styles**:
  - Container: `bg-slate-900/90 backdrop-blur-md border-b border-slate-800/80`
  - Logo box: `from-purple-600 via-indigo-600 to-emerald-400 p-0.5`, inner `bg-slate-950 text-purple-400`
  - Logo text: `"AI Teacher"` in `from-purple-400 via-indigo-200 to-emerald-300`
  - Tabs bar: `bg-slate-950/60 border-slate-800/60`
  - Active tab: `bg-purple-600 text-white shadow-purple-600/30`
  - Inactive tab: `text-slate-400 hover:text-slate-200 hover:bg-slate-900`
  - Language button: `bg-slate-800/80 border-slate-700 text-slate-200`
  - Profile button: `bg-gradient-to-r from-purple-950/80 to-slate-900 border-purple-800/40 text-slate-200`, avatar `bg-purple-600`
- **Proposed Light Theme & ApniHelp Branding**:
  - Container: `sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-gray-200 shadow-sm px-4 lg:px-8 py-3`
  - Logo:
    - Box: `w-10 h-10 rounded-xl bg-blue-900 text-yellow-400 flex items-center justify-center shadow-sm`
    - Brand title: `<span className="font-black text-xl tracking-tight text-blue-950">ApniHelp</span>`
    - Badge: `<span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full bg-yellow-100 text-yellow-800 border border-yellow-300">AI Teacher</span>`
    - Subtitle: `<p className="text-xs text-gray-500 hidden sm:block">Adaptive Educational Platform</p>`
  - Navigation tabs (streamlined without intermediate manual tabs):
    - Container: `hidden md:flex items-center gap-1 bg-gray-100 p-1 rounded-xl border border-gray-200 text-xs font-medium`
    - Active tab: `bg-white text-blue-950 shadow-sm border border-gray-200 font-bold`
    - Inactive tab: `text-gray-600 hover:text-gray-900 hover:bg-gray-200/60`
  - Language toggle: `bg-white hover:bg-gray-50 border border-gray-200 text-gray-700 text-xs font-semibold shadow-sm`
  - Profile badge: `bg-white hover:bg-gray-50 border border-gray-200 text-gray-800 text-xs font-medium shadow-sm`, avatar `bg-blue-900 text-yellow-400 font-bold`

---

### 4.3 Component: `IngestionView.tsx`
- **File**: `frontend/src/components/Ingestion/IngestionView.tsx`
- **Current Dark Styles & Multiple Steps**:
  - Heading: `text-white`, `text-slate-400`
  - Mode switch: `border-slate-800`, active `border-purple-500 text-purple-400`
  - Drag/drop zone: `border-slate-800 hover:border-purple-500/50 bg-slate-900/40`, icon `bg-purple-950/40 text-purple-400`
  - Uploaded doc card: `bg-slate-900 border-slate-800`, summary `bg-slate-800/60 text-slate-300`
  - Multi-step button: `"Proceed to Configure Learner Profile & Plan"` (`bg-gradient-to-r from-purple-600 to-indigo-600`)
  - Topic form: `bg-slate-900 border-slate-800`, input `bg-slate-900 border-slate-800 text-slate-100`
  - Topic sample cards: `bg-slate-900/70 border-slate-800/80 hover:bg-slate-800/80`
- **Proposed Light Theme & Single-Click Pipeline**:
  - Main Heading: `<h1 className="text-3xl font-black text-blue-950 tracking-tight sm:text-4xl mb-2">Create Your Video Lesson</h1>`
  - Subtitle: `<p className="text-gray-600 text-sm max-w-2xl mx-auto">Upload any document or type an academic topic to generate an interactive AI teacher video lesson in seconds.</p>`
  - Mode Switch: Inactive `text-gray-500 hover:text-gray-900`, Active `border-b-2 border-blue-900 text-blue-900 font-bold`
  - Drag/Drop Zone:
    - Container: `bg-white border-2 border-dashed border-gray-300 hover:border-blue-900 hover:bg-blue-50/20 rounded-2xl p-10 text-center transition-all shadow-sm`
    - Icon: `w-16 h-16 mx-auto mb-4 rounded-2xl bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-900`
    - Title: `text-base font-bold text-gray-900 mb-1`
    - Subtext: `text-xs text-gray-500 mb-3`
    - Badge: `bg-gray-100 text-gray-600 border border-gray-200`
  - Topic Card:
    - Container: `bg-white border border-gray-200 rounded-2xl p-6 shadow-sm space-y-4`
    - Category pills: Active `bg-blue-900 text-white font-semibold shadow-sm`, Inactive `bg-gray-100 text-gray-700 hover:bg-gray-200 border border-gray-200`
    - Textarea: `bg-white border border-gray-300 text-gray-900 placeholder-gray-400 rounded-xl p-3.5 focus:border-blue-900 focus:ring-1 focus:ring-blue-900 text-sm`
    - Sample topics: `bg-gray-50 border border-gray-200 hover:border-blue-300 hover:bg-blue-50/40 text-gray-800`
  - **The Single "Generate Video" Primary Action Button**:
    - Replaces all intermediate buttons (`"Proceed to Configure..."`, `"Generate Grounded Syllabus..."`).
    - Exact styling:
      ```tsx
      <button
        onClick={handleOneClickGenerateVideo}
        disabled={isGenerating || (!selectedFile && !topicText.trim())}
        className="w-full py-4 px-6 rounded-xl bg-yellow-400 hover:bg-yellow-500 active:bg-yellow-600 disabled:opacity-50 disabled:cursor-not-allowed text-slate-950 font-black text-base flex items-center justify-center gap-2.5 shadow-lg shadow-yellow-500/25 transition-all transform hover:-translate-y-0.5"
      >
        {isGenerating ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin text-slate-950" />
            <span>Synthesizing Video Pipeline ({progressStage})...</span>
          </>
        ) : (
          <>
            <Play className="w-5 h-5 fill-slate-950 text-slate-950" />
            <span>Generate Video</span>
          </>
        )}
      </button>
      ```

---

### 4.4 Component: `InteractiveVideoPlayer.tsx`
- **File**: `frontend/src/components/VideoPlayer/InteractiveVideoPlayer.tsx`
- **Current Dark Styles**:
  - Container: `bg-slate-950 border border-slate-800 shadow-2xl`
  - Checkpoint modal overlay: `bg-slate-950/95 backdrop-blur-md`
  - Modal card: `bg-slate-900 border border-purple-900/60`
  - MCQ buttons: `border-slate-800 bg-slate-950/60 text-slate-300` / selected `border-purple-500 bg-purple-950/40 text-purple-200`
  - Correct card: `bg-emerald-950/50 border-emerald-800/60 text-emerald-400`
  - Misconception card: `bg-amber-950/40 border-amber-800/50 text-amber-400`
  - Analogy card: `bg-indigo-950/40 border-indigo-800/60 text-indigo-100`
  - Follow-up card: `bg-slate-950 border-purple-900/40`
- **Proposed Light Theme Styling**:
  - Video Wrapper: `relative rounded-2xl bg-black border border-gray-300 shadow-xl overflow-hidden` (Video content itself remains framed on clean black canvas).
  - Video Controls bar: `bg-gradient-to-t from-black/90 via-black/60 to-transparent text-white`
    - Play button: `bg-yellow-400 hover:bg-yellow-500 text-slate-950 font-bold p-2 rounded-lg`
    - Pause marker dots: `bg-yellow-400 border-white shadow-md shadow-yellow-400/80` (answered markers `bg-emerald-400`)
    - Post-Quiz CTA: `bg-yellow-400 hover:bg-yellow-500 text-slate-950 font-bold px-3 py-1 rounded-lg text-xs`
    - Tutor chat toggle: `bg-blue-900 hover:bg-blue-800 text-white px-3 py-1 rounded-lg text-xs font-semibold`
  - **In-Video Checkpoint Modal Dialog**:
    - Backdrop: `bg-slate-900/60 backdrop-blur-sm`
    - Card: `bg-white border border-gray-200 rounded-2xl p-6 shadow-2xl space-y-5 max-w-2xl`
    - Header: `border-b border-gray-200 pb-3 text-blue-950 font-bold text-sm flex items-center justify-between`
    - Pause timestamp chip: `bg-yellow-100 text-yellow-800 border border-yellow-300 font-mono text-xs px-2.5 py-0.5 rounded-full font-bold`
    - Prompt: `text-gray-900 font-bold text-base leading-snug`
    - MCQ options:
      - Default: `border-gray-200 bg-gray-50 text-gray-800 hover:border-blue-400 hover:bg-blue-50/30 p-3.5 rounded-xl border text-xs text-left transition-all`
      - Selected: `border-2 border-blue-900 bg-blue-50/70 text-blue-950 font-semibold shadow-sm`
    - Submit button: `bg-yellow-400 hover:bg-yellow-500 text-slate-950 font-black py-3 rounded-xl shadow-md text-xs`
    - Evaluation Correct feedback: `bg-emerald-50 border border-emerald-300 text-emerald-900 p-4 rounded-xl`
    - Misconception Alert: `bg-amber-50 border border-amber-300 text-amber-900 p-4 rounded-xl`
    - Re-explanation & Analogy: `bg-blue-50 border border-blue-200 text-blue-950 p-4 rounded-xl`
    - Resume button: `bg-blue-900 hover:bg-blue-800 text-white font-bold py-2.5 rounded-xl shadow-sm text-xs`

---

### 4.5 Component: `QuizView.tsx`
- **File**: `frontend/src/components/Assessment/QuizView.tsx`
- **Current Dark Styles**:
  - Header & Question cards: `bg-slate-900 border-slate-800`, text `text-slate-100`
  - MCQ options: `bg-slate-950/60 border-slate-800 text-slate-300` / selected `border-purple-500 bg-purple-950/40 text-purple-200`
  - Submit button: `bg-gradient-to-r from-purple-600 to-indigo-600`
  - Diagnostic Learning Report:
    - Container: `bg-slate-900 border border-purple-900/50 shadow-2xl`
    - Score circle: `bg-gradient-to-tr from-purple-950 via-slate-900 to-emerald-950 border-2 border-emerald-500/80`
    - Concepts cards: `bg-slate-900/80 border-emerald-900/40`, `bg-slate-900/80 border-amber-900/40`
    - Action button: `bg-purple-600 hover:bg-purple-500`
- **Proposed Light Theme Styling**:
  - Header Card: `bg-white border border-gray-200 rounded-2xl p-6 shadow-sm`
    - Title: `text-blue-950 font-black text-xl`
    - Description: `text-gray-600 text-xs`
  - Question Cards: `bg-white border border-gray-200 rounded-2xl p-6 shadow-sm space-y-3`
    - Question chip: `bg-blue-50 text-blue-900 border border-blue-200 font-mono text-[10px] font-bold px-2 py-0.5 rounded`
    - Prompt: `text-gray-900 font-bold text-sm`
    - MCQ options:
      - Default: `border-gray-200 bg-gray-50 text-gray-800 hover:border-blue-400 hover:bg-blue-50/40 p-3.5 rounded-xl text-xs text-left transition-all`
      - Selected: `border-2 border-blue-900 bg-blue-50 text-blue-950 font-bold shadow-sm`
    - Textarea: `bg-white border border-gray-300 text-gray-900 focus:border-blue-900 rounded-xl p-3 text-xs`
  - Submit Button: `w-full py-3.5 rounded-xl bg-yellow-400 hover:bg-yellow-500 active:bg-yellow-600 text-slate-950 font-black text-sm flex items-center justify-center gap-2 shadow-md shadow-yellow-500/20 transition-all`
  - Diagnostic Report:
    - Summary card: `bg-white border border-gray-200 rounded-2xl p-6 shadow-md`
    - Score badge: `w-24 h-24 rounded-full bg-emerald-50 border-4 border-emerald-500 text-emerald-800 flex flex-col items-center justify-center font-black`
    - Demonstrated Strengths: `bg-emerald-50/60 border border-emerald-200 text-emerald-900 p-5 rounded-2xl`
    - Revision Gaps: `bg-amber-50/60 border border-amber-200 text-amber-900 p-5 rounded-2xl`
    - Recommendation cards: `bg-white border border-gray-200 hover:border-blue-400 hover:bg-blue-50/30 text-gray-900 p-4 rounded-xl shadow-sm cursor-pointer`
    - Analytics CTA: `bg-blue-900 hover:bg-blue-800 text-white font-bold py-3 px-6 rounded-xl shadow-md text-xs`

---

### 4.6 Component: `AnalyticsDashboard.tsx`
- **File**: `frontend/src/components/Analytics/AnalyticsDashboard.tsx`
- **Current Dark Styles**:
  - Profile header card: `bg-slate-900 border-slate-800`, gradient `from-purple-900/20`
  - 3 Stats cards: `bg-slate-900 border-slate-800`
  - Mastery index card: `bg-slate-900 border-slate-800`, progress track `bg-slate-800`
  - Weak areas card: `bg-slate-900 border-slate-800`, item button `bg-slate-800/60 border-amber-900/30`
  - AI recommendations card: `bg-slate-900 border-slate-800`, item button `bg-slate-800/50 border-slate-700/60`
- **Proposed Light Theme Styling**:
  - Profile Header Card:
    - Container: `bg-white border border-gray-200 rounded-2xl p-6 shadow-sm`
    - Avatar: `w-14 h-14 rounded-2xl bg-blue-900 text-yellow-400 flex items-center justify-center text-xl font-black shadow-sm`
    - Title: `text-blue-950 font-black text-xl`
    - Level chip: `bg-yellow-100 text-yellow-800 border border-yellow-300 font-mono text-[10px] uppercase font-bold`
    - Edit Profile button: `bg-gray-100 hover:bg-gray-200 text-gray-800 border border-gray-200 text-xs font-semibold px-4 py-2 rounded-xl`
  - Stats Cards (3 cards):
    - Container: `bg-white border border-gray-200 rounded-2xl p-5 shadow-sm hover:border-blue-300 transition-all`
    - Label: `text-xs text-gray-500 font-semibold mb-2`
    - Numbers: Lessons Completed in `text-blue-950 font-black text-3xl`, Mastery % in `text-emerald-700 font-black text-3xl`, Time in `text-blue-900 font-black text-3xl`
  - Concept Mastery Index:
    - Container: `bg-white border border-gray-200 rounded-2xl p-6 shadow-sm space-y-5`
    - Title: `text-xs font-bold text-gray-500 uppercase tracking-widest`
    - Track: `bg-gray-100 h-2 rounded-full overflow-hidden`
    - Bar: `bg-emerald-500 h-full rounded-full transition-all` (or `bg-yellow-500` for developing concepts)
  - Weak Areas & Refresher Cards:
    - Container: `bg-white border border-gray-200 rounded-2xl p-6 shadow-sm`
    - List items: `bg-gray-50 border border-gray-200 hover:border-yellow-400 hover:bg-yellow-50/40 text-gray-900 p-3 rounded-xl transition-all`
  - AI Teacher Recommendations:
    - Container: `bg-white border border-gray-200 rounded-2xl p-6 shadow-sm space-y-5`
    - Recommendation cards: `bg-gray-50 border border-gray-200 hover:border-blue-400 hover:bg-blue-50/50 text-gray-900 p-4 rounded-xl cursor-pointer transition-all shadow-sm`
    - Level badge: `bg-blue-100 text-blue-900 border border-blue-200 font-mono text-[10px] uppercase font-bold`

---

### 4.7 Component: `ProfileModal.tsx` & `SidePanelTutor.tsx`
- **ProfileModal**:
  - Modal overlay: `bg-slate-900/50 backdrop-blur-sm`
  - Dialog container: `bg-white border border-gray-200 rounded-2xl shadow-2xl`
  - Header: `bg-gray-50 border-b border-gray-200 text-blue-950 font-bold px-6 py-4`
  - Form labels: `text-gray-900 font-semibold text-xs`
  - Form inputs: `bg-white border border-gray-300 text-gray-900 focus:border-blue-900 rounded-xl px-3.5 py-2.5 text-xs`
  - Level cards: Inactive `bg-gray-50 border-gray-200 text-gray-700 hover:border-blue-300`, Selected `bg-blue-50 border-2 border-blue-900 text-blue-950 font-bold`
  - Language options: Selected `bg-blue-900 text-white font-semibold`, Inactive `bg-gray-50 border-gray-200 text-gray-700`
  - Save button: `bg-yellow-400 hover:bg-yellow-500 text-slate-950 font-black py-2.5 px-5 rounded-xl shadow-md text-xs`
- **SidePanelTutor**:
  - Drawer container: `bg-white border-l border-gray-200 shadow-2xl`
  - Header: `bg-gray-50 border-b border-gray-200 text-blue-950 font-bold`
  - Tutor message bubble: `bg-gray-100 border border-gray-200 text-gray-900 rounded-2xl`
  - Student message bubble: `bg-blue-900 text-white rounded-2xl font-medium`
  - Action chips: `bg-white border border-gray-300 hover:border-blue-400 hover:bg-blue-50 text-gray-700 text-[10px]`
  - Send button: `bg-yellow-400 hover:bg-yellow-500 text-slate-950 font-bold p-2.5 rounded-xl shadow-sm`

---

## 5. Summary Matrix: Legacy vs. ApniHelp Target Implementation

| Dimension | Legacy AI Teacher Implementation | ApniHelp Target Implementation | Rationale / Compliance |
|---|---|---|---|
| **Pipeline Trigger** | 3 manual steps across Ingestion, ProfileModal, LessonPlanEditor | **Single "Generate Video" button** on primary view | **R2**: Zero manual intermediate steps |
| **Lesson Plan Editor** | Mandatory blocking step between ingestion and video | Seamlessly synthesized in background, viewable optionally | Removes user bottleneck while preserving underlying pedagogy |
| **Color Scheme** | Dark slate (`#020617`, `slate-950/900`) & purple | **Light theme**: White (`#fff`), Light Gray (`#f8fafc`), Dark Blue (`#0f172a`), Yellow (`#facc15`) | **R3**: Fully standardized light palette |
| **Primary CTA Button** | Purple/indigo gradient (`from-purple-600 to-indigo-600`) | **Warm Vibrant Yellow (`bg-yellow-400`) with Dark Slate text** | High visibility, AAA accessibility, consistent visual hierarchy |
| **Card Surfaces** | Dark slate boxes (`bg-slate-900 border-slate-800`) | **Clean White Cards (`bg-white border-gray-200 shadow-sm`)** | Luminous, professional, educational aesthetic |
| **Project Branding** | "AI Teacher — Adaptive Educational Platform" | **"ApniHelp"** | **R5**: Standardized across headers, titles, and config |

---

## 6. Verification and Implementation Roadmap

1. **Phase 1: Foundations**:
   - Update `frontend/index.html` title to "ApniHelp" and body class to `bg-slate-50 text-slate-900`.
   - Update `frontend/src/index.css` to light background (`#f8fafc`), dark text (`#0f172a`), and gray scrollbars.
   - Update `frontend/package.json` project name to `"apnihelp-frontend"`.
2. **Phase 2: R2 Flow Orchestration in `App.tsx`**:
   - Implement `handleGenerateVideo({ file, topic })` to chain `uploadDocument` / `ingestTopic` → `createLessonPlan` → `generateVideo` → status polling → manifest retrieval.
   - Add unified progress state and auto-transition to `currentTab === 'video'`.
3. **Phase 3: Component Theme & Button Replacements**:
   - Update `Header.tsx` (brand title to "ApniHelp", clean white navbar, dark blue text, yellow accents).
   - Update `IngestionView.tsx` (single "Generate Video" button, white cards, gray borders, blue headers).
   - Update `InteractiveVideoPlayer.tsx` (light checkpoint overlay modal, yellow resume/quiz buttons).
   - Update `QuizView.tsx` (white cards, yellow submit button, clear diagnostic badges).
   - Update `AnalyticsDashboard.tsx` (white dashboard cards, dark blue stats, yellow recommendations).
   - Update `ProfileModal.tsx` & `SidePanelTutor.tsx` (light dialogs/drawers).
4. **Phase 4: Build Verification**:
   - Run `cd frontend && npm run build` to ensure exit code 0 and zero TypeScript errors.
