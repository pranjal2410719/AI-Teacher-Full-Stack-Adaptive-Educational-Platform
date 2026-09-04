# Comprehensive UI Theme Consistency & Integrity Survey Report

**Platform**: AI Teacher Adaptive Educational Platform  
**Target Standard**: Strict Dark Slate Theme (`bg-slate-950` / `bg-slate-900` / `bg-slate-800`, `purple`/`indigo` brand accents, `emerald` success/mastery accents, `amber` warnings)  
**Reference Implementations**: `Header.tsx` & `AnalyticsDashboard.tsx`  
**Date**: 2026-09-02  

---

## 1. Executive Summary

A comprehensive, line-by-line audit of all frontend components in `/home/dev/Desktop/projects/AI-InnovationHackathon/frontend/src/` was conducted to benchmark UI consistency against the Dark Slate design system.

### Key Audit Findings:
1. **Critical Forbidden Colors**: Discovered multiple instances of forbidden light/cream/brown/orange colors, notably hardcoded brown `#2b1a07` backdrop in `ProfileModal.tsx` and legacy neon orange `#ff6f1e` / `#ce500a` across `ProfileModal.tsx`, `IngestionView.tsx`, and `SidePanelTutor.tsx`.
2. **Low-Contrast Washed Out Text**: Widespread usage of `text-slate-400` and `text-slate-400/60` / `text-slate-400/70` on primary headings, module titles, user/tutor chat messages, and form input controls instead of high-contrast `text-slate-100` or `text-slate-200`.
3. **Missing / Ineffective Hover States**: Multiple interactive elements (category selectors, level cards, language toggles, dropzones) had hover classes identical to their base styles (e.g. `border-slate-800 hover:border-slate-800`), rendering interactions imperceptible.
4. **Interactive Semantics (Unclickable Divs)**: Quiz options, In-Video checkpoint options, and recommended topic cards were styled as `<div>` elements with `onClick` handlers rather than semantic `<button>` elements with keyboard accessibility and focus rings.
5. **Blank Screen Tab Transitions (Missing Empty States)**: In `App.tsx`, navigating to the **Lesson Plan** (Tab 2) or **Video & Checks** (Tab 3) tabs when `plan` or `videoManifest` is `null` caused a blank screen render with no empty state or guidance.

---

## 2. Design System Tokens & Reference Standard

| Category | Tailwind Classes / Hex Standard | Purpose |
|---|---|---|
| **App Canvas** | `bg-slate-950` (`#020617`), `text-slate-100` | Base background and root text |
| **Card Surface** | `bg-slate-900`, `border-slate-800`, `rounded-2xl` | Primary container cards & modals |
| **Elevated Surface** | `bg-slate-800/60`, `border-slate-700/60`, `rounded-xl` | Inner sections, stat cards, chat bubbles |
| **Primary Brand** | `bg-gradient-to-r from-purple-600 to-indigo-600`, `text-purple-400`, `border-purple-500/30`, `bg-purple-500/20` | Action buttons, active tabs, brand icons |
| **Success / Mastery** | `text-emerald-400`, `bg-emerald-500/10`, `border-emerald-500/20`, `from-emerald-500 to-teal-400` | High mastery scores, ready badges, success states |
| **Warnings / Gaps** | `text-amber-400`, `bg-amber-500/10`, `border-amber-900/30`, `hover:border-amber-500/50` | Misconceptions, weak areas, revision topics |
| **Primary Text** | `text-slate-100`, `text-slate-200`, `text-white` | Headings, card titles, button labels, user input |
| **Secondary Text** | `text-slate-400`, `text-slate-500` | Timestamps, subtitles, helper descriptions |

---

## 3. Component-by-Component Detailed Audit & Fix Plan

---

### Component 1: `ProfileModal.tsx` (`src/components/Profile/ProfileModal.tsx`)

#### Issues Identified:
1. **Line 48**: `bg-[#2b1a07]/70` backdrop overlay — Hardcoded brown tone explicitly breaking the dark theme.
2. **Lines 53, 74, 112, 118, 165, 187**: Hardcoded neon orange `#ff6f1e` used for icons, active level cards, checkboxes, and text.
3. **Line 129**: Hardcoded hex `text-[#22c55e]` instead of standard `text-emerald-400`.
4. **Lines 57, 73, 81, 88, 117, 128, 161, 186, 194**: Washed-out `text-slate-400` / `text-slate-400/70` on modal titles, input boxes, and labels.
5. **Line 113, 139, 150**: Ineffective hover states (`hover:border-slate-800` where base is `border-slate-800`).
6. **Line 210**: `bg-purple-600 hover:bg-purple-600` (identical hover state).
7. **Line 107-123**: Level selection cards rendered as unclickable `<div>` elements instead of `<button type="button">`.
8. **Lines 49, 53, 63, 81, 110, 136, 204, 210**: Inconsistent arbitrary border radius (`rounded-[8px]`, `rounded-[12px]`) and arbitrary shadows (`shadow-[rgba(0,0,0,0.06)...]`).

#### Remediation Snippet:
```tsx
// BEFORE (Line 48)
<div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#2b1a07]/70 backdrop-blur-sm animate-in fade-in">
  <div className="w-full max-w-xl bg-slate-900 border border-slate-800 rounded-[12px] shadow-[rgba(0,0,0,0.06)_0px_2px_20px_0px] overflow-hidden flex flex-col max-h-[90vh]">

// AFTER
<div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in">
  <div className="w-full max-w-xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
```

```tsx
// BEFORE (Lines 107-123)
<div
  key={lvl.id}
  onClick={() => setLevel(lvl.id as LearnerLevel)}
  className={`p-3 rounded-[8px] border cursor-pointer transition-all ${
    level === lvl.id
      ? 'border-purple-500 bg-slate-800/40 text-[#ff6f1e] shadow-sm'
      : 'border-slate-800 bg-slate-900/60 hover:border-slate-800 text-slate-400/60'
  }`}
>
  <div className="flex items-center justify-between mb-1">
    <span className="font-bold text-slate-400">{lvl.label}</span>
    {level === lvl.id && <Check className="w-3.5 h-3.5 text-[#ff6f1e]" />}
  </div>
  <p className="text-[10px] text-slate-400/60 leading-tight">{lvl.desc}</p>
</div>

// AFTER
<button
  type="button"
  key={lvl.id}
  onClick={() => setLevel(lvl.id as LearnerLevel)}
  className={`p-3.5 rounded-xl border text-left cursor-pointer transition-all ${
    level === lvl.id
      ? 'border-purple-500 bg-purple-950/40 text-purple-200 shadow-md shadow-purple-950/30'
      : 'border-slate-800 bg-slate-900/60 hover:border-slate-700 hover:bg-slate-800/50 text-slate-400'
  }`}
>
  <div className="flex items-center justify-between mb-1">
    <span className="font-bold text-slate-100">{lvl.label}</span>
    {level === lvl.id && <Check className="w-3.5 h-3.5 text-purple-400" />}
  </div>
  <p className="text-[11px] text-slate-400 leading-tight">{lvl.desc}</p>
</button>
```

---

### Component 2: `IngestionView.tsx` (`src/components/Ingestion/IngestionView.tsx`)

#### Issues Identified:
1. **Lines 87, 98**: Tabs active indicator uses `text-[#ff6f1e]`. Should be `text-purple-400 border-purple-500`.
2. **Lines 140, 164, 181, 215, 261, 282, 299**: Hardcoded `#ff6f1e` used for upload icon, summary headers, category active pills, generate button, and book icons.
3. **Line 174, 292**: Hardcoded `text-[#22c55e] border-[#22c55e]/40` instead of Tailwind `text-emerald-400 bg-emerald-950/40 border-emerald-500/30`.
4. **Line 247**: Quick-pick sample topics use `hover:border-[#ce500a]/60` (hardcoded dark orange) and rendered as unclickable `<div>`.
5. **Line 125**: Dropzone has `hover:border-slate-800` (identical to base border `border-slate-800`).
6. **Line 217**: Unselected subject category has `hover:bg-slate-900` (same as base `bg-slate-900`).
7. **Lines 161, 204, 279**: Malformed duplicate border & shadow classes: `border-[1.5px] border-slate-800/90 border border-slate-800/60 shadow-[rgba(0,0,0,0.06)_0px_2px_20px_0px]`.
8. **Lines 148, 168, 180, 206, 226, 232, 247, 286, 298**: Low-contrast text in headings, inputs, summaries, and pills (`text-slate-400` / `text-slate-400/70`).

#### Remediation Snippet:
```tsx
// BEFORE (Lines 213-221)
className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all ${
  subjectCategory === cat
    ? 'bg-[#ff6f1e] text-white shadow-sm'
    : 'bg-slate-900 text-slate-400/60 hover:bg-slate-900 hover:text-slate-400'
}`}

// AFTER
className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all ${
  subjectCategory === cat
    ? 'bg-purple-600 text-white shadow-md shadow-purple-600/30 font-semibold'
    : 'bg-slate-800/60 text-slate-400 border border-slate-800 hover:bg-slate-800 hover:text-slate-200'
}`}
```

```tsx
// BEFORE (Lines 240-255)
<div
  key={idx}
  onClick={() => {
    setTopicText(item.title);
    setSubjectCategory(item.cat);
  }}
  className="p-2.5 rounded-xl bg-slate-900/70 border border-slate-800/80 hover:border-[#ce500a]/60 text-xs text-slate-400/70 cursor-pointer flex items-center justify-between transition-colors"
>
  <span className="truncate">{item.title}</span>
  <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-900 text-slate-400/60 font-mono flex-shrink-0">
    {item.cat}
  </span>
</div>

// AFTER
<button
  type="button"
  key={idx}
  onClick={() => {
    setTopicText(item.title);
    setSubjectCategory(item.cat);
  }}
  className="p-3 rounded-xl bg-slate-900/70 border border-slate-800/80 hover:border-purple-500/50 hover:bg-slate-800/80 text-xs text-slate-300 cursor-pointer flex items-center justify-between transition-all group text-left"
>
  <span className="truncate group-hover:text-purple-200 transition-colors">{item.title}</span>
  <span className="text-[10px] px-2 py-0.5 rounded-md bg-slate-800 text-slate-400 font-mono flex-shrink-0 border border-slate-700/50">
    {item.cat}
  </span>
</button>
```

---

### Component 3: `SidePanelTutor.tsx` (`src/components/TutorChat/SidePanelTutor.tsx`)

#### Issues Identified:
1. **Line 136**: User message bubble styled as `bg-[#ff6f1e] text-white` (harsh bright orange bubble).
2. **Lines 95, 129, 144, 145, 175, 200**: Hardcoded `#ff6f1e` on icons, grounded sources, spinner, and send button.
3. **Line 109**: Hardcoded `#22c55e` on Globe icon.
4. **Line 137**: AI Tutor message text is washed-out `text-slate-400` inside `bg-slate-900`. Should be crisp `text-slate-100` on elevated card `bg-slate-800/80 border border-slate-700/60`.
5. **Line 99, 107, 157, 195**: Low-contrast text in panel header, chips, and chat input.
6. **Line 107, 200**: Ineffective hover states (`hover:bg-slate-800` on base `bg-slate-800`; `hover:bg-[#ff6f1e]` on base `bg-[#ff6f1e]`).

#### Remediation Snippet:
```tsx
// BEFORE (Lines 134-149)
<div
  className={`max-w-[85%] p-3.5 rounded-2xl leading-relaxed ${
    m.sender === 'user'
      ? 'bg-[#ff6f1e] text-white rounded-br-none shadow-md shadow-slate-900/50'
      : 'bg-slate-900 border border-slate-800/80 text-slate-400 rounded-bl-none shadow-sm'
  }`}
>
  <p className="whitespace-pre-line">{m.text}</p>
  {m.sources && m.sources.length > 0 && (
    <div className="mt-2.5 pt-2 border-t border-slate-800/80 text-[10px] text-[#ff6f1e] flex items-center gap-1.5">
      <BookOpen className="w-3 h-3 text-[#ff6f1e]" />
      <span>Grounded in: {m.sources.join(', ')}</span>
    </div>
  )}
</div>

// AFTER
<div
  className={`max-w-[85%] p-3.5 rounded-2xl leading-relaxed ${
    m.sender === 'user'
      ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-br-none shadow-md shadow-purple-900/30'
      : 'bg-slate-800/80 border border-slate-700/60 text-slate-100 rounded-bl-none shadow-sm'
  }`}
>
  <p className="whitespace-pre-line">{m.text}</p>
  {m.sources && m.sources.length > 0 && (
    <div className="mt-2.5 pt-2 border-t border-slate-700/60 text-[10px] text-purple-300 flex items-center gap-1.5">
      <BookOpen className="w-3 h-3 text-purple-400" />
      <span>Grounded in: {m.sources.join(', ')}</span>
    </div>
  )}
</div>
```

---

### Component 4: `LessonPlanEditor.tsx` (`src/components/Planner/LessonPlanEditor.tsx`)

#### Issues Identified:
1. **Line 101**: Primary lesson plan title `<h2 className="text-2xl font-bold text-slate-400">{plan.title}</h2>` rendered in washed-out slate-400. Should be `text-slate-100 tracking-tight`.
2. **Lines 188, 241, 261, 277, 283, 323**: Washed-out `text-slate-400` / `text-slate-400/70` in module titles, visual spec headlines, and checkpoint prompt questions.
3. **Line 175**: Module list items have `hover:border-slate-800` (identical to base `border-slate-800/80`). Should be `hover:border-purple-500/40 hover:bg-slate-900/90`.
4. **Line 111**: Customize button text is `text-slate-400/70`. Should be `text-slate-300 hover:text-white border border-slate-700`.
5. **Line 294**: LaTeX formula section is inside `bg-cyan-950/30 border-cyan-800/40`, but header label is `text-purple-400`. Should be `text-cyan-400` for consistent sub-theme harmony.

#### Remediation Snippet:
```tsx
// BEFORE (Lines 101-105)
<h2 className="text-2xl font-bold text-slate-400">{plan.title}</h2>
<p className="text-xs text-slate-400/60 mt-1">
  Total Target Duration: <span className="font-mono text-purple-400 font-semibold">{formatDuration(plan.target_duration_sec)}</span> • {plan.modules.length} Pedagogical Modules
</p>

// AFTER
<h2 className="text-2xl font-extrabold text-slate-100 tracking-tight">{plan.title}</h2>
<p className="text-xs text-slate-400 mt-1">
  Total Target Duration: <span className="font-mono text-purple-400 font-semibold">{formatDuration(plan.target_duration_sec)}</span> • {plan.modules.length} Pedagogical Modules
</p>
```

---

### Component 5: `InteractiveVideoPlayer.tsx` (`src/components/VideoPlayer/InteractiveVideoPlayer.tsx`)

#### Issues Identified:
1. **Lines 220-240**: MCQ checkpoint options are rendered as unclickable `<div>` elements instead of `<button type="button">`.
2. **Line 423**: Reset time button `className="p-1.5 text-slate-400 hover:text-white"` lacks background hover/focus feedback.
3. **Line 437**: Language switch button `className="... bg-slate-900 border border-slate-700 hover:bg-slate-800"` lacks `hover:border-slate-600 transition-colors`.
4. **Line 446**: Side tutor toggle `hover:bg-purple-900` lacks `hover:border-purple-700`.

#### Remediation Snippet:
```tsx
// BEFORE (Lines 220-240)
{activeCheckpoint.question.options.map((opt, idx) => (
  <div
    key={idx}
    onClick={() => setSelectedOptionIndex(idx)}
    className={`p-3 rounded-xl border text-xs cursor-pointer transition-all flex items-center justify-between ${
      selectedOptionIndex === idx
        ? 'border-purple-500 bg-purple-950/40 text-purple-200 shadow-md shadow-purple-950/30'
        : 'border-slate-800 bg-slate-950/60 text-slate-300 hover:border-slate-700'
    }`}
  >
    <span>{opt}</span>
    <div className={`w-4 h-4 rounded-full border flex items-center justify-center text-[10px] ${
      selectedOptionIndex === idx
        ? 'border-purple-500 bg-purple-600 text-white'
        : 'border-slate-700'
    }`}>
      {selectedOptionIndex === idx && '✓'}
    </div>
  </div>
))}

// AFTER
{activeCheckpoint.question.options.map((opt, idx) => (
  <button
    type="button"
    key={idx}
    onClick={() => setSelectedOptionIndex(idx)}
    className={`w-full p-3.5 rounded-xl border text-xs text-left cursor-pointer transition-all flex items-center justify-between ${
      selectedOptionIndex === idx
        ? 'border-purple-500 bg-purple-950/40 text-purple-200 shadow-md shadow-purple-950/30'
        : 'border-slate-800 bg-slate-950/60 text-slate-300 hover:border-slate-700 hover:bg-slate-900/60'
    }`}
  >
    <span>{opt}</span>
    <div className={`w-4 h-4 rounded-full border flex items-center justify-center text-[10px] flex-shrink-0 ml-2 ${
      selectedOptionIndex === idx
        ? 'border-purple-500 bg-purple-600 text-white'
        : 'border-slate-700'
    }`}>
      {selectedOptionIndex === idx && '✓'}
    </div>
  </button>
))}
```

---

### Component 6: `QuizView.tsx` (`src/components/Assessment/QuizView.tsx`)

#### Issues Identified:
1. **Lines 143-163**: Question options inside the Quiz are `<div>` elements with `onClick` instead of `<button type="button">`.
2. **Lines 286-304**: Recommended next topic cards in the post-quiz diagnostic report are `<div>` elements with `onClick` instead of `<button type="button">`.
3. **Line 289**: `hover:border-purple-600/70` on recommendation cards lacks background hover feedback (`hover:bg-slate-800/80`).
4. **Lines 107-111**: Error state displays an isolated red bar with no retry or recovery CTA if quiz generation fails.

#### Remediation Snippet:
```tsx
// BEFORE (Lines 285-305)
<div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
  {report.recommended_next_topics.map((t, idx) => (
    <div
      key={idx}
      onClick={() => onSelectNextTopic(t.topic)}
      className="p-4 rounded-xl bg-slate-900 border border-slate-800 hover:border-purple-600/70 cursor-pointer transition-all space-y-1.5 group"
    >
      <div className="flex items-center justify-between">
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800/40">
          {t.level.toUpperCase()}
        </span>
        <ChevronRight className="w-4 h-4 text-slate-500 group-hover:text-purple-400 transition-colors" />
      </div>
      <h4 className="font-bold text-slate-100 text-xs group-hover:text-purple-300 transition-colors">
        {t.topic}
      </h4>
      {t.rationale && (
        <p className="text-[11px] text-slate-400 leading-tight">{t.rationale}</p>
      )}
    </div>
  ))}
</div>

// AFTER
<div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
  {report.recommended_next_topics.map((t, idx) => (
    <button
      type="button"
      key={idx}
      onClick={() => onSelectNextTopic(t.topic)}
      className="p-4 rounded-xl bg-slate-900 border border-slate-800 hover:border-purple-500/50 hover:bg-slate-800/70 cursor-pointer transition-all space-y-1.5 group text-left w-full"
    >
      <div className="flex items-center justify-between">
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
          {t.level.toUpperCase()}
        </span>
        <ChevronRight className="w-4 h-4 text-slate-500 group-hover:text-purple-400 transition-colors" />
      </div>
      <h4 className="font-bold text-slate-100 text-xs group-hover:text-purple-300 transition-colors">
        {t.topic}
      </h4>
      {t.rationale && (
        <p className="text-[11px] text-slate-400 leading-tight">{t.rationale}</p>
      )}
    </button>
  ))}
</div>
```

---

### Component 7: `App.tsx` (`src/App.tsx`)

#### Issues Identified:
1. **Line 243**: `{currentTab === 'plan' && plan && (...)` — If user navigates to Tab 2 without an active plan, a blank `<main>` renders.
2. **Line 255**: `{currentTab === 'video' && videoManifest && (...)` — If user navigates to Tab 3 without a generated video manifest, a blank `<main>` renders.

#### Remediation Plan:
Add fallback empty states inside `App.tsx` when `plan` or `videoManifest` is null:
- For `currentTab === 'plan' && !plan`: Render an empty state card with `Sparkles` icon:
  ```tsx
  {currentTab === 'plan' && (
    plan ? (
      <LessonPlanEditor ... />
    ) : (
      <div className="max-w-md mx-auto my-20 p-8 rounded-2xl bg-slate-900 border border-slate-800 text-center space-y-4">
        <div className="w-12 h-12 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center mx-auto text-purple-400">
          <Sparkles className="w-6 h-6" />
        </div>
        <h3 className="text-lg font-bold text-slate-100">No Active Lesson Plan</h3>
        <p className="text-xs text-slate-400 leading-relaxed">
          Upload a document or enter a topic in the Ingestion stage to synthesize an AI lesson blueprint.
        </p>
        <button
          onClick={() => setCurrentTab('ingest')}
          className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold transition-all shadow-md shadow-purple-600/30"
        >
          Go to Ingestion
        </button>
      </div>
    )
  )}
  ```
- For `currentTab === 'video' && !videoManifest`: Render an empty state card with `PlayCircle` icon:
  ```tsx
  {currentTab === 'video' && (
    videoManifest ? (
      <InteractiveVideoPlayer ... />
    ) : (
      <div className="max-w-md mx-auto my-20 p-8 rounded-2xl bg-slate-900 border border-slate-800 text-center space-y-4">
        <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center mx-auto text-indigo-400">
          <PlayCircle className="w-6 h-6" />
        </div>
        <h3 className="text-lg font-bold text-slate-100">No Generated Video Stream</h3>
        <p className="text-xs text-slate-400 leading-relaxed">
          Approve a lesson plan in the Lesson Plan tab to render the AI teacher interactive video.
        </p>
        <button
          onClick={() => setCurrentTab(plan ? 'plan' : 'ingest')}
          className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold transition-all shadow-md shadow-purple-600/30"
        >
          {plan ? 'View Lesson Plan' : 'Start with Ingestion'}
        </button>
      </div>
    )
  )}
  ```

---

## 4. Summary Matrix of Required Modifications

| Component | File Path | Hex / Light Color Fixes | Hover & Button Fixes | Empty State Fixes |
|---|---|---|---|---|
| **Header.tsx** | `src/components/Header.tsx` | Clean (Reference) | Clean (Reference) | N/A |
| **AnalyticsDashboard.tsx** | `src/components/Analytics/AnalyticsDashboard.tsx` | Clean (Reference) | Clean (Reference) | Clean (Reference) |
| **ProfileModal.tsx** | `src/components/Profile/ProfileModal.tsx` | 🔴 `#2b1a07`, `#ff6f1e`, `#22c55e` | 🔴 Fix card `<button>`, hover states, radius | N/A (Modal) |
| **IngestionView.tsx** | `src/components/Ingestion/IngestionView.tsx` | 🔴 `#ff6f1e`, `#ce500a`, `#22c55e` | 🔴 Dropzone hover, category hover, quick-pick button | Clean |
| **SidePanelTutor.tsx** | `src/components/TutorChat/SidePanelTutor.tsx` | 🔴 `#ff6f1e`, `#22c55e` | 🔴 Bubble gradient, hover states, input contrast | Clean |
| **LessonPlanEditor.tsx** | `src/components/Planner/LessonPlanEditor.tsx` | 🟡 Washed out slate-400 text | 🟡 Module hover, customize hover | Guarded via App.tsx |
| **InteractiveVideoPlayer.tsx** | `src/components/VideoPlayer/InteractiveVideoPlayer.tsx` | Clean | 🟡 Checkpoint options `<button>`, control hovers | Guarded via App.tsx |
| **QuizView.tsx** | `src/components/Assessment/QuizView.tsx` | Clean | 🟡 Options `<button>`, recommendation `<button>` | 🟡 Add error recovery CTA |
| **App.tsx** | `src/App.tsx` | Clean | Clean | 🔴 Add fallback empty states for Tab 2 & 3 |

---

## 5. Verification Commands for Implementers

1. **Verify No Forbidden Colors**:
   ```bash
   grep -rn -E '#2b1a07|#ff6f1e|#ce500a|#fdfbf9|#22c55e' /home/dev/Desktop/projects/AI-InnovationHackathon/frontend/src/
   # Expected result: Zero matches (except standard #020617 in index.css)
   ```
2. **Build and Typecheck**:
   ```bash
   cd /home/dev/Desktop/projects/AI-InnovationHackathon/frontend && npm run build
   # Expected result: Exit code 0, 0 errors
   ```
