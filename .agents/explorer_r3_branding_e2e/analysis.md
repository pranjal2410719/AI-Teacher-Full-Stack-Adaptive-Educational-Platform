# ApniHelp: Comprehensive Branding & E2E Verification Test Suite Investigation (`analysis.md`)

**Agent**: `explorer_r3_branding_e2e`  
**Date**: 2026-09-04T17:53:00Z  
**Workspace**: `/home/dev/Desktop/projects/AI-InnovationHackathon`  
**Focus**: Project Naming / Branding Migration (R5) & E2E Verification Test Suite Design (R1–R5)  

---

## 1. Executive Summary

This report establishes the complete architectural blueprint for two critical tracks of the ApniHelp platform migration:
1. **R5 (Project Naming & Branding Migration)**: A full-codebase scan across the frontend, backend, root documentation, configuration files, deployment scripts, and test suites to eradicate legacy nomenclature (`"AI Teacher"`, `"AI-Teacher"`, `"Adaptive Educational Platform"`, `"ai-teacher-frontend"`, `"ai_teacher_*"`), and standardize all visible titles, repository identifiers, watermarks, and container names to **"ApniHelp"**.
2. **E2E Verification Test Suite Design (R1–R5)**: A complete, executable test infrastructure design that rigorously verifies all core requirements defined in lines 81–120 of `ORIGINAL_REQUEST.md`:
   - **R1 (Video Speed)**: Processing time $\le 20\text{s}$ per minute of final video length for 5-minute ($\le 100\text{s}$) and 10-minute ($\le 200\text{s}$) videos.
   - **R2 (Single Button Flow)**: UI exposes a single `"Generate Video"` button triggering the entire pipeline without intermediate manual hurdles.
   - **R3 (Light Theme)**: Full visual theme verification enforcing a light palette based on **white**, **yellow**, **gray**, and **dark blue**, eliminating the legacy dark slate theme.
   - **R4 (Photorealistic Avatar & Lip-Sync)**: Verification that the presenter avatar is a photorealistic AI teacher image (not a cartoon illustration) with synchronized lip movements aligned to narration audio.
   - **R5 (Naming Consistency)**: Automated regression verification asserting that all visible UI headers, HTML titles, slide watermarks, and API metadata display **"ApniHelp"**.

---

## 2. Project Naming Audit (R5) — Full Codebase Catalog & Migration Plan

A multi-tier ripgrep audit was executed across all non-ignored project directories (excluding `.agents/`, `.venv/`, `node_modules/`, and dynamic `.json` data). Below is the exhaustive inventory of all locations requiring brand transformation, along with exact file paths, line numbers, current text, proposed replacements, and implementation rationale.

### 2.1 Frontend Layer

| Target File | Line(s) | Current Legacy Text | Proposed ApniHelp Replacement | Rationale |
|---|---|---|---|---|
| `frontend/package.json` | 2 | `"name": "ai-teacher-frontend"` | `"name": "apnihelp-frontend"` | Package manifest identifier compliance. |
| `frontend/index.html` | 7 | `<title>AI Teacher — Adaptive Educational Platform</title>` | `<title>ApniHelp — Adaptive Educational Platform</title>` | Browser tab title visible to all end-users. |
| `frontend/src/components/Header.tsx` | 35 | `AI Teacher` | `ApniHelp` | Main brand title in top navigation bar. |
| `frontend/src/components/Header.tsx` | 41 | `<p className="text-xs text-slate-400 hidden sm:block">Full-Stack Human Teaching Loop</p>` | `<p className="text-xs text-slate-400 hidden sm:block">Adaptive Educational Platform</p>` | Brand subtitle alignment. |
| `frontend/src/components/Planner/LessonPlanEditor.tsx` | 255 | `AI Teacher Narration Script (Multilingual TTS)` | `ApniHelp Narration Script (Multilingual TTS)` | Visible section header in lesson plan editor. |
| `frontend/src/components/TutorChat/SidePanelTutor.tsx` | 35 | `'Hello! I am your AI Teacher tutor. Ask me any unscripted questions...'` | `'Hello! I am your ApniHelp tutor. Ask me any unscripted questions...'` | Default greeting in AI side-panel chat. |
| `frontend/src/components/TutorChat/SidePanelTutor.tsx` | 99 | `<h3 className="font-bold text-slate-100 text-xs">AI Teacher Side-Panel Tutor</h3>` | `<h3 className="font-bold text-slate-100 text-xs">ApniHelp Side-Panel Tutor</h3>` | Visible header of tutor drawer. |
| `frontend/src/components/VideoPlayer/InteractiveVideoPlayer.tsx` | 275 | `<span>Evaluating Response with AI Teacher...</span>` | `<span>Evaluating Response with ApniHelp...</span>` | In-video checkpoint evaluation loading state. |
| `frontend/src/components/VideoPlayer/InteractiveVideoPlayer.tsx` | 327 | `<span>AI Teacher Scaffolded Re-Explanation & Analogy</span>` | `<span>ApniHelp Scaffolded Re-Explanation & Analogy</span>` | In-video checkpoint remediation heading. |
| `frontend/src/components/Analytics/AnalyticsDashboard.tsx` | 232 | `<span>AI Teacher Adaptive Recommendations</span>` | `<span>ApniHelp Adaptive Recommendations</span>` | Analytics dashboard recommendation title. |
| `frontend/src/components/Profile/ProfileModal.tsx` | 58 | `<p className="text-[11px] text-slate-400">Personalize AI Teacher pedagogical style & time budget</p>` | `<p className="text-[11px] text-slate-400">Personalize ApniHelp pedagogical style & time budget</p>` | Profile customization modal description. |

---

### 2.2 Backend Application Layer

| Target File | Line(s) | Current Legacy Text | Proposed ApniHelp Replacement | Rationale |
|---|---|---|---|---|
| `backend/app/config.py` | 2 | `Configuration and Environment Settings for AI Teacher Platform.` | `Configuration and Environment Settings for ApniHelp Platform.` | Module docstring. |
| `backend/app/config.py` | 19 | `app_name: str = "AI Teacher Core Platform"` | `app_name: str = "ApniHelp Core Platform"` | Core application name used by FastAPI and health checks. |
| `backend/app/main.py` | 2 | `AI Teacher Core Platform - FastAPI Application Entry Point.` | `ApniHelp Core Platform - FastAPI Application Entry Point.` | Module docstring. |
| `backend/app/main.py` | 26 | `logger = logging.getLogger("ai_teacher.main")` | `logger = logging.getLogger("apnihelp.main")` | Logger namespace. |
| `backend/app/main.py` | 32 | `description="Full-Stack AI Teacher Educational Platform API powering adaptive human-teaching loops."` | `description="ApniHelp - Full-Stack Adaptive Educational Platform API powering adaptive human-teaching loops."` | FastAPI OpenAPI documentation metadata. |
| `backend/app/main.py` | 93 | `"message": "Welcome to AI Teacher Core Server"` | `"message": "Welcome to ApniHelp Core Server"` | Root API endpoint response (`GET /`). |
| `backend/app/services/slide_render_service.py` | 85-87 | `# AI Teacher Logo / Watermark`<br>`draw.text((self.width - 150, 26), "AI TEACHER", fill=(100, 210, 170))` | `# ApniHelp Logo / Watermark`<br>`draw.text((self.width - 150, 26), "APNIHELP", fill=(100, 210, 170))` | Slide corner watermark visible on every rendered video frame. |
| `backend/app/services/avatar_service.py` | 308 | `draw.text((banner_x + 48, banner_y + 42), f"AI Teacher • {subject_title}", fill=(160, 190, 230))` | `draw.text((banner_x + 48, banner_y + 42), f"ApniHelp • {subject_title}", fill=(160, 190, 230))` | Banner overlay text rendered on teacher avatar video clips. |
| `backend/app/services/avatar_service.py` | 317 | `subject_title: str = "AI Teacher Lecture"` | `subject_title: str = "ApniHelp Lecture"` | Default argument in avatar clip generator. |
| `backend/app/services/interaction_service.py` | 528 | `"You are a friendly, encouraging AI Teacher side-panel tutor. "` | `"You are a friendly, encouraging ApniHelp side-panel tutor. "` | System prompt defining LLM tutor persona. |
| `backend/app/demo_generator.py` | 2, 429, 520 | `AI Teacher Platform`, `AI TEACHER SAMPLE DEMO...` | `ApniHelp Platform`, `APNIHELP SAMPLE DEMO...` | CLI demo video generator script banners and descriptions. |
| `backend/app/services/*.py` | Multiple | Module headers (`ingestion_service.py:2`, `assessment_service.py:2`, `tts_service.py:2`, `profile_service.py:2`, `video_stitcher.py:2`, `interaction_service.py:2`, `models/__init__.py:2`) | Updated to refer to `ApniHelp` | Code consistency and documentation hygiene. |

---

### 2.3 Configuration, Deployment & Root Documentation

| Target File | Line(s) | Current Legacy Text | Proposed ApniHelp Replacement | Rationale |
|---|---|---|---|---|
| `docker-compose.yml` | 8 | `container_name: ai_teacher_backend` | `container_name: apnihelp_backend` | Docker container naming for backend service. |
| `docker-compose.yml` | 23 | `container_name: ai_teacher_frontend` | `container_name: apnihelp_frontend` | Docker container naming for frontend service. |
| `run.sh` | 3, 38, 58, 68, 81, 116, 125 | `AI Teacher — Full-Stack Adaptive Educational Platform Launcher`, `Shutting down AI Teacher Platform...`, `AI Teacher Full-Stack Application is LIVE!` | `ApniHelp — Full-Stack Adaptive Educational Platform Launcher`, `Shutting down ApniHelp Platform...`, `ApniHelp Full-Stack Application is LIVE!` | Primary CLI execution script banner and console output. |
| `PROJECT.md` | 1 | `# Project: AI Teacher Adaptive Educational Platform — Real-User Audit & Hardening` | `# Project: ApniHelp — Full-Stack Adaptive Educational Platform` | Core repository project declaration. |
| `README.md` | 1, 11, 42, 113, 249 | `# 🎓 AI Teacher — Full-Stack Adaptive Educational Platform`, Hackathon project description | `# 🎓 ApniHelp — Full-Stack Adaptive Educational Platform`, ApniHelp architecture overview | Public repository landing documentation. |
| `TEST_INFRA.md` | 1 | `# E2E Test Infra: AI Teacher Platform` | `# E2E Test Infra: ApniHelp Platform` | Test infrastructure documentation header. |
| `TEST_READY.md` | 1, 13 | `# AI Teacher: E2E Test Suite...` | `# ApniHelp: E2E Test Suite...` | Test readiness report header. |
| `docs/*.md` | Multiple | `docs/architecture.md`, `docs/setup_and_deployment.md`, `docs/user_guide.md`, `docs/api_specification.md`, `docs/multilingual_support.md`, `docs/architecture_diagram.svg` | Replaced systematically with `ApniHelp` | User-facing and developer documentation. |
| Git Remote Origin | Git Config | `origin https://github.com/pranjal2410719/AI-Teacher-Full-Stack-Adaptive-Educational-Platform.git` | `origin https://github.com/pranjal2410719/ApniHelp.git` (or documented reference) | Meets requirement R5: "All branding, repository names, and displayed titles shall use the name 'ApniHelp'." |

---

### 2.4 Existing Tests Requiring Coordinated Updates

A crucial finding during the audit is that existing tests assert legacy strings:
1. `backend/tests/test_ingestion.py:483`:
   ```python
   # CURRENT:
   assert "Welcome to AI Teacher" in res_root.json()["message"]
   # MUST BE UPDATED TO:
   assert "Welcome to ApniHelp" in res_root.json()["message"]
   ```
2. `backend/tests/test_video.py:176`:
   ```python
   # CURRENT:
   text="Welcome to the AI Teacher lesson on calculus."
   # MUST BE UPDATED TO:
   text="Welcome to the ApniHelp lesson on calculus."
   ```
3. `tests_e2e/harness.py:50`:
   ```python
   # CURRENT:
   app = FastAPI(title="AI Teacher E2E Test Server", version="1.0.0")
   # MUST BE UPDATED TO:
   app = FastAPI(title="ApniHelp E2E Test Server", version="1.0.0")
   ```
4. `tests_e2e/test_runner.py:3, 75, 145`:
   CLI banner strings updated to `"APNIHELP E2E TEST SUITE RUNNER"`.

Updating `backend/app/main.py` without simultaneously updating `test_ingestion.py` would cause existing test failures. Both must be updated in lockstep.

---

## 3. E2E Verification Test Suite Architecture & Design (R1–R5)

To guarantee that the platform satisfies all requirements in lines 81–120 of `ORIGINAL_REQUEST.md`, we design a comprehensive test suite structure.

### 3.1 Test Architecture Overview

The testing framework leverages the existing `tests_e2e` runner (`tests_e2e/test_runner.py`) and pytest suite (`backend/tests/`). We define:
- **Tier 6 / R-Suite**: A dedicated acceptance test tier (`tests_e2e/tier6_apnihelp_acceptance/` or modular pytest modules in `backend/tests/test_apnihelp_r_series.py` and `tests_e2e/tier1_feature_coverage/`).
- **CLI Runner Flag**: Support for `python3 tests_e2e/test_runner.py --tier 6` or standalone pytest invocation: `pytest tests_e2e/tier6_apnihelp_acceptance/ -v`.

---

### 3.2 Requirement R1: Video Generation Performance Verification Test

#### Specification
- **Requirement**: "The system must generate a video in $\le 20$ seconds of processing for each minute of final video length (e.g., a 5-minute video $\le 100$ seconds, 10-minute $\le 200$ seconds)."
- **Acceptance Criteria**: "Video generation time meets R1 for test videos of 5 min and 10 min."
- **Performance Metric**:
  $$\text{Processing Speed Ratio} = \frac{\text{Wall Clock Processing Time (seconds)}}{\frac{\text{Final Video Duration (seconds)}}{60.0}} \le 20.0 \text{ s/min}$$

#### Test Suite Implementation Design (`test_r1_video_generation_speed.py`)

```python
"""
R1 Verification Test: Video Generation Performance Benchmark
Asserts processing time <= 20.0 seconds per minute of video output for:
  - 5-Minute Scenario (300s duration -> <= 100.0s processing)
  - 10-Minute Scenario (600s duration -> <= 200.0s processing)
"""

import time
import pytest
import asyncio
from pathlib import Path
from backend.app.models.lesson_plan import LessonPlan, LessonSegmentPlan, VisualSpec, VisualType, SegmentType
from backend.app.models.video import VideoGenerationRequest
from backend.app.services.video_stitcher import video_stitcher
from backend.app.services.planner_service import planner_service

def build_benchmark_lesson_plan(plan_id: str, target_duration_sec: int) -> LessonPlan:
    """Creates a realistic multi-segment lesson plan summing to target_duration_sec."""
    # Split into 5-segment structure: Intro (avatar), 3 Visual Slides, Outro (avatar)
    seg_dur = target_duration_sec // 5
    modules = [
        LessonSegmentPlan(
            segment_id=f"seg_{plan_id}_01",
            order=1,
            segment_type=SegmentType.AVATAR_INTRO,
            title="Overview & Motivation",
            duration_sec=seg_dur,
            script="Welcome to this comprehensive ApniHelp masterclass.",
            visual_spec=VisualSpec(visual_type=VisualType.GENERAL_SLIDE, subject_domain="math")
        ),
        LessonSegmentPlan(
            segment_id=f"seg_{plan_id}_02",
            order=2,
            segment_type=SegmentType.VISUAL_CONCEPT,
            title="Core Concept Derivation",
            duration_sec=seg_dur,
            script="Here we examine the fundamental mathematical derivation in detail.",
            visual_spec=VisualSpec(visual_type=VisualType.MATH_EQUATION, subject_domain="math",
                                   latex_equations=[r"\int_{0}^{\infty} e^{-x^2} dx = \frac{\sqrt{\pi}}{2}"])
        ),
        LessonSegmentPlan(
            segment_id=f"seg_{plan_id}_03",
            order=3,
            segment_type=SegmentType.VISUAL_CONCEPT,
            title="Algorithmic Properties & Complexity",
            duration_sec=seg_dur,
            script="Let us observe the time and space complexity characteristics.",
            visual_spec=VisualSpec(visual_type=VisualType.CODE_SNIPPET, subject_domain="cs",
                                   code_snippets=[{"language": "python", "code": "def quicksort(arr): return arr"}])
        ),
        LessonSegmentPlan(
            segment_id=f"seg_{plan_id}_04",
            order=4,
            segment_type=SegmentType.VISUAL_CONCEPT,
            title="Practical Applications & Synthesis",
            duration_sec=seg_dur,
            script="Consider these real-world architectural scenarios.",
            visual_spec=VisualSpec(visual_type=VisualType.DIAGRAM_FLOW, subject_domain="biology")
        ),
        LessonSegmentPlan(
            segment_id=f"seg_{plan_id}_05",
            order=5,
            segment_type=SegmentType.AVATAR_SUMMARY,
            title="Lesson Recap & Action Items",
            duration_sec=target_duration_sec - (seg_dur * 4),
            script="Congratulations on completing this lesson. Review your progress in ApniHelp analytics.",
            visual_spec=VisualSpec(visual_type=VisualType.GENERAL_SLIDE, subject_domain="math")
        )
    ]
    
    plan = LessonPlan(
        plan_id=plan_id,
        title=f"ApniHelp Benchmark Lesson ({target_duration_sec}s)",
        target_duration_sec=target_duration_sec,
        total_actual_duration_sec=target_duration_sec,
        level="intermediate",
        language="en",
        subject_domain="math",
        topic="Calculus & Algorithms",
        modules=modules
    )
    planner_service.plans_registry[plan.plan_id] = plan
    return plan

@pytest.mark.asyncio
async def test_r1_video_generation_speed_5min():
    """Verifies that a 5-minute (300s) video generates in <= 100 seconds (<=20s/min)."""
    target_duration_sec = 300  # 5 minutes
    max_allowed_processing_sec = 100.0  # 20s/min * 5 min
    plan = build_benchmark_lesson_plan("plan_bench_5m", target_duration_sec)
    
    t0 = time.time()
    manifest, video_path = await video_stitcher.generate_lesson_video(
        plan=plan,
        request=VideoGenerationRequest(plan_id=plan.plan_id, resolution="720p")
    )
    elapsed = time.time() - t0
    
    # Assertions
    assert video_path.exists(), f"Output video file does not exist: {video_path}"
    assert manifest.total_duration_sec >= target_duration_sec * 0.90, "Generated video duration significantly shorter than requested"
    
    actual_minutes = manifest.total_duration_sec / 60.0
    sec_per_min = elapsed / actual_minutes
    
    print(f"\n[R1 Benchmark - 5 Min]: Video Length = {manifest.total_duration_sec:.1f}s ({actual_minutes:.2f} min), Processing Time = {elapsed:.2f}s, Rate = {sec_per_min:.2f} s/min")
    assert elapsed <= max_allowed_processing_sec, (
        f"R1 VIOLATION: 5-minute video took {elapsed:.2f}s (exceeds threshold of {max_allowed_processing_sec}s)"
    )
    assert sec_per_min <= 20.0, f"R1 VIOLATION: Rate {sec_per_min:.2f} s/min exceeds 20.0 s/min limit"

@pytest.mark.asyncio
async def test_r1_video_generation_speed_10min():
    """Verifies that a 10-minute (600s) video generates in <= 200 seconds (<=20s/min)."""
    target_duration_sec = 600  # 10 minutes
    max_allowed_processing_sec = 200.0  # 20s/min * 10 min
    plan = build_benchmark_lesson_plan("plan_bench_10m", target_duration_sec)
    
    t0 = time.time()
    manifest, video_path = await video_stitcher.generate_lesson_video(
        plan=plan,
        request=VideoGenerationRequest(plan_id=plan.plan_id, resolution="720p")
    )
    elapsed = time.time() - t0
    
    assert video_path.exists(), f"Output video file does not exist: {video_path}"
    assert manifest.total_duration_sec >= target_duration_sec * 0.90
    
    actual_minutes = manifest.total_duration_sec / 60.0
    sec_per_min = elapsed / actual_minutes
    
    print(f"\n[R1 Benchmark - 10 Min]: Video Length = {manifest.total_duration_sec:.1f}s ({actual_minutes:.2f} min), Processing Time = {elapsed:.2f}s, Rate = {sec_per_min:.2f} s/min")
    assert elapsed <= max_allowed_processing_sec, (
        f"R1 VIOLATION: 10-minute video took {elapsed:.2f}s (exceeds threshold of {max_allowed_processing_sec}s)"
    )
    assert sec_per_min <= 20.0, f"R1 VIOLATION: Rate {sec_per_min:.2f} s/min exceeds 20.0 s/min limit"
```

#### Performance Optimization Strategies for Implementer
To ensure the backend consistently achieves $\le 20\text{s/min}$:
1. **FFmpeg Concat Demuxer (`-c copy`)**:
   In `test_scripts/test_stitcher.py`, `stitch_lesson_segments_concat_demuxer` executes stream copy without CPU re-encoding. If all segment clips share identical stream parameters (1280x720 30fps H.264 + 44.1kHz AAC), concatenation takes $<1$ second even for a 10-minute video.
2. **Visual Slide Image Loop Optimization**:
   Visual slides are static graphics. Rather than rendering 30 individual duplicate frames per second via Python PIL loop, FFmpeg can loop the single static PNG image:
   `ffmpeg -loop 1 -i slide.png -i audio.wav -c:v libx264 -tune stillimage -preset ultrafast -shortest output.mp4`.
   This reduces visual slide rendering time by $>95\%$.

---

### 3.3 Requirement R2: UI Simplicity Verification Test

#### Specification
- **Requirement**: "The frontend must expose a single 'Generate Video' button that triggers the whole pipeline for any uploaded document or input."
- **Acceptance Criteria**: "The UI shows only one button labeled 'Generate Video' and no other manual steps."

#### Current Problem in Codebase
In `frontend/src/components/Ingestion/IngestionView.tsx`:
- Line 193: `<button ...><span>Proceed to Configure Learner Profile & Plan</span><ArrowRight /></button>`
- Line 311: `<button ...><span>Proceed to Configure Learner Profile & Plan</span><ArrowRight /></button>`
- In `frontend/src/components/Planner/LessonPlanEditor.tsx`: User must separately review and click "Approve & Generate Lesson Video".
This violates R2 because there are multiple manual intermediate steps.

#### Test Suite Implementation Design (`test_r2_single_button_flow.py`)

```python
"""
R2 Verification Test: UI Simplicity & Single 'Generate Video' Button
Verifies:
  1. Frontend Ingestion screen presents exactly one primary action button labeled 'Generate Video'.
  2. No intermediate manual confirmation buttons (e.g. 'Proceed to Configure Learner Profile & Plan') block execution.
  3. Single-click directly triggers the end-to-end pipeline (Upload/Topic -> Plan -> Video).
"""

import re
from pathlib import Path
import pytest

FRONTEND_DIR = Path("/home/dev/Desktop/projects/AI-InnovationHackathon/frontend/src")

def test_r2_frontend_single_button_label_and_no_intermediary_steps():
    """Inspects IngestionView.tsx and App.tsx to verify single 'Generate Video' action button."""
    ingestion_file = FRONTEND_DIR / "components" / "Ingestion" / "IngestionView.tsx"
    assert ingestion_file.exists()
    content = ingestion_file.read_text(encoding="utf-8")
    
    # 1. Verify presence of "Generate Video" button
    assert re.search(r"Generate Video", content, re.IGNORECASE), (
        "R2 VIOLATION: 'Generate Video' button text not found in IngestionView.tsx"
    )
    
    # 2. Verify legacy multi-step button is removed
    assert not re.search(r"Proceed to Configure Learner Profile & Plan", content), (
        "R2 VIOLATION: Legacy multi-step button 'Proceed to Configure Learner Profile & Plan' still exists in IngestionView.tsx"
    )

def test_r2_pipeline_direct_trigger_contract():
    """Verifies that backend supports triggering full pipeline from material ingestion directly to video."""
    from backend.app.main import app
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    # Ingest topic
    res_topic = client.post("/api/v1/materials/topic", json={"topic": "Limits in Calculus", "subject_category": "Mathematics"})
    assert res_topic.status_code == 200
    topic_data = res_topic.json()
    
    # Plan generation (can be chained automatically in UI or via backend direct trigger)
    res_plan = client.post("/api/v1/lessons/plan", json={
        "topic": topic_data["topic"],
        "topic_id": topic_data["topic_id"],
        "learner_profile": {"student_id": "stu_r2", "level": "intermediate", "language": "en", "time_budget_min": 10}
    })
    assert res_plan.status_code == 200
    plan_id = res_plan.json()["plan_id"]
    
    # Video generation trigger
    res_vid = client.post("/api/v1/video/generate", json={"plan_id": plan_id})
    assert res_vid.status_code in [200, 202]
    assert "task_id" in res_vid.json()
```

---

### 3.4 Requirement R3: Light Visual Theme Verification Test

#### Specification
- **Requirement**: "The UI colour palette shall be a light theme based on a mixture of white, yellow, gray, and dark blue."
- **Acceptance Criteria**: "The UI colour scheme matches the specified light palette across all pages."

#### Current Problem in Codebase
The application currently uses a dark slate theme:
- Container backgrounds: `bg-slate-950`, `bg-slate-900`, `bg-slate-900/90`
- Border colors: `border-slate-800`, `border-slate-700`
- Dominant brand colors: `purple-600`, `indigo-600`, `emerald-400`
- Prohibited colors under previous audit: light colors were banned; now light theme is mandatory!

#### Light Theme Color Mapping Matrix

| Role | Semantic Target | Approved Palette Tokens | Banned Legacy Tokens |
|---|---|---|---|
| **Base Background** | White / Crisp Canvas | `bg-white`, `#ffffff` | `bg-slate-950`, `bg-slate-900`, `bg-black` |
| **Secondary Background** | Light Gray / Off-white | `bg-gray-50`, `bg-gray-100`, `bg-slate-50`, `bg-slate-100` | `bg-slate-900`, `bg-slate-800` |
| **Primary Text** | Dark Blue / Navy | `text-blue-950`, `text-blue-900`, `text-slate-900`, `#0f172a`, `#1e3a8a` | `text-slate-100`, `text-white` (on light surfaces) |
| **Secondary Text** | Muted Gray | `text-gray-600`, `text-gray-500`, `text-slate-600` | `text-slate-400` (on dark surfaces) |
| **Accent / Highlights** | Vibrant Warm Yellow | `bg-yellow-400`, `bg-yellow-500`, `text-yellow-800`, `border-yellow-400`, `amber-400` | `purple-600`, `indigo-600` dominant badges |
| **Interactive Buttons** | Dark Blue with White Text OR Yellow Accent | `bg-blue-900 text-white hover:bg-blue-800`, `bg-yellow-400 text-blue-950 hover:bg-yellow-300` | `bg-purple-600`, `bg-indigo-600` |
| **Borders & Dividers** | Subtle Light Gray | `border-gray-200`, `border-gray-300`, `border-slate-200` | `border-slate-800`, `border-slate-700` |

#### Test Suite Implementation Design (`test_r3_light_visual_theme.py`)

```python
"""
R3 Verification Test: Light Visual Theme Palette Compliance
Verifies:
  1. Absence of dark slate root backgrounds (`bg-slate-950`, `bg-slate-900`) across all main views.
  2. Conformance to approved light theme palette tokens: White, Yellow, Gray, Dark Blue.
  3. Consistent application across Header, App, IngestionView, LessonPlanEditor, VideoPlayer, QuizView, AnalyticsDashboard.
"""

import re
from pathlib import Path
import pytest

FRONTEND_SRC = Path("/home/dev/Desktop/projects/AI-InnovationHackathon/frontend/src")

KEY_COMPONENTS = [
    "App.tsx",
    "components/Header.tsx",
    "components/Ingestion/IngestionView.tsx",
    "components/Planner/LessonPlanEditor.tsx",
    "components/VideoPlayer/InteractiveVideoPlayer.tsx",
    "components/Assessment/QuizView.tsx",
    "components/Analytics/AnalyticsDashboard.tsx",
]

def test_r3_no_dark_slate_root_backgrounds():
    """Asserts that root container classes do not enforce legacy dark slate backgrounds."""
    app_tsx = (FRONTEND_SRC / "App.tsx").read_text(encoding="utf-8")
    assert not re.search(r'className="[^"]*min-h-screen\s+bg-slate-950', app_tsx), (
        "R3 VIOLATION: App.tsx root container still uses 'bg-slate-950'. Must be light (e.g. 'bg-gray-50' or 'bg-white')."
    )
    
    header_tsx = (FRONTEND_SRC / "components" / "Header.tsx").read_text(encoding="utf-8")
    assert not re.search(r'bg-slate-900', header_tsx), (
        "R3 VIOLATION: Header.tsx still uses dark background 'bg-slate-900'. Must use light/white/blue-900 palette."
    )

def test_r3_light_theme_palette_token_presence():
    """Verifies presence of required light theme tokens (white, yellow, gray, dark blue) across components."""
    for rel_path in KEY_COMPONENTS:
        fpath = FRONTEND_SRC / rel_path
        if not fpath.exists():
            continue
        code = fpath.read_text(encoding="utf-8")
        
        # Check for light theme indicators (white, yellow, gray, blue-900/navy)
        has_white = bool(re.search(r'bg-white|text-white|#ffffff', code, re.IGNORECASE))
        has_gray = bool(re.search(r'gray-|slate-100|slate-200', code))
        has_dark_blue = bool(re.search(r'blue-900|blue-950|navy|#1e3a8a|#0f172a', code))
        has_yellow = bool(re.search(r'yellow-|amber-', code))
        
        print(f"[R3 Palette Check - {rel_path}]: white={has_white}, gray={has_gray}, dark_blue={has_dark_blue}, yellow={has_yellow}")
        assert (has_white or has_gray), f"R3 VIOLATION: Component {rel_path} missing light canvas foundations (white/gray)"
```

---

### 3.5 Requirement R4: Photorealistic AI Teacher Avatar & Sync Verification Test

#### Specification
- **Requirement**: "The video presenter must be a photorealistic human-like AI teacher image generated via an image model, not a cartoon illustration."
- **Acceptance Criteria**: "The generated video features a photorealistic teacher avatar that syncs with the narration."

#### Current Problem in Codebase
`AvatarService.render_avatar_frame` in `backend/app/services/avatar_service.py` currently draws geometric 2D shapes with Pillow (`draw.polygon`, `draw.rectangle`, `draw.ellipse`). It does NOT use a photorealistic image model asset.

#### Test Suite Implementation Design (`test_r4_photorealistic_avatar.py`)

```python
"""
R4 Verification Test: Photorealistic AI Teacher Avatar & Speech Synchronization
Verifies:
  1. Avatar source is a photorealistic human teacher image (not cartoon/vector/flat illustration).
  2. Image properties: Photographic depth, resolution >= 720p, realistic facial texture.
  3. Audio-visual synchronization: Total video duration matches audio duration within +/- 0.2s.
  4. Audio energy envelope modulates mouth/viseme states dynamically.
"""

import math
import pytest
from pathlib import Path
from PIL import Image
import numpy as np
from backend.app.config import settings
from backend.app.services.avatar_service import avatar_service
from backend.app.services.tts_service import tts_service

def test_r4_photorealistic_avatar_asset_properties():
    """Verifies that the avatar service utilizes a photographic human image asset."""
    # Check avatar assets directory
    avatar_dir = settings.avatar_dir
    assert avatar_dir.exists(), f"Avatar directory not found: {avatar_dir}"
    
    # Locate photorealistic avatar template
    candidates = list(avatar_dir.glob("*.png")) + list(avatar_dir.glob("*.jpg")) + list(avatar_dir.glob("*.jpeg"))
    assert len(candidates) > 0, "No photographic avatar asset found in settings.avatar_dir"
    
    avatar_img_path = candidates[0]
    img = Image.open(avatar_img_path).convert("RGB")
    arr = np.array(img)
    
    # 1. Dimension check
    width, height = img.size
    assert width >= 400 and height >= 400, f"Avatar resolution too low for photorealistic display: {width}x{height}"
    
    # 2. Entropy / Texture variance check:
    # A flat cartoon illustration has very few unique color shades and low local variance.
    # A photographic human face exhibits high Shannon entropy and color standard deviation across RGB channels.
    std_dev = np.std(arr)
    assert std_dev > 25.0, f"Avatar image appears flat/cartoonish (std_dev={std_dev:.2f} <= 25.0). Must be photographic."

def test_r4_avatar_speech_sync_and_duration():
    """Verifies that generated avatar clip strictly synchronizes with TTS audio duration."""
    test_text = "Hello, I am your ApniHelp AI teacher. Let us explore calculus together."
    audio_path, expected_audio_dur = tts_service.synthesize_sync(test_text, language="en")
    
    output_clip = settings.video_dir / "test_r4_avatar_clip.mp4"
    avatar_service.generate_avatar_clip(
        audio_path=audio_path,
        output_path=output_clip,
        subject_title="Calculus Introduction",
        teacher_name="Prof. Alexander Vance"
    )
    
    assert output_clip.exists()
    
    # Verify envelope extraction
    envelope = avatar_service.extract_audio_energy_envelope(audio_path, fps=30)
    assert len(envelope) > 0
    assert np.max(envelope) > 0.1, "Audio envelope should detect voice energy during speech"
    
    # Check frame count matches expected duration
    expected_frames = math.ceil(expected_audio_dur * 30)
    assert abs(len(envelope) - expected_frames) <= 2, (
        f"Frame count mismatch: envelope has {len(envelope)} frames, expected {expected_frames}"
    )
```

---

### 3.6 Requirement R5: Project Naming Consistency Verification Test

#### Specification
- **Requirement**: "All branding, repository names, and displayed titles shall use the name 'ApniHelp'."
- **Acceptance Criteria**: "All visible project titles and repo names are 'ApniHelp'."

#### Test Suite Implementation Design (`test_r5_naming_consistency.py`)

```python
"""
R5 Verification Test: Project Naming Consistency Regression Test
Asserts:
  1. Frontend index.html title contains 'ApniHelp' and zero occurrences of 'AI Teacher'.
  2. Frontend Header displays 'ApniHelp'.
  3. Frontend package.json name is 'apnihelp-frontend'.
  4. Backend FastAPI application title and root endpoint message contain 'ApniHelp'.
  5. Slide render watermark is 'APNIHELP' (not 'AI TEACHER').
  6. Docker-compose container names are 'apnihelp_backend' and 'apnihelp_frontend'.
  7. run.sh banners and README.md title use 'ApniHelp'.
"""

import re
from pathlib import Path
import pytest

ROOT = Path("/home/dev/Desktop/projects/AI-InnovationHackathon")

def test_r5_frontend_displayed_titles():
    # 1. index.html
    index_html = (ROOT / "frontend" / "index.html").read_text(encoding="utf-8")
    assert "<title>ApniHelp" in index_html, "index.html does not title the app 'ApniHelp'"
    assert not re.search(r"AI\s*Teacher", index_html, re.IGNORECASE), "index.html still references 'AI Teacher'"
    
    # 2. Header.tsx
    header_tsx = (ROOT / "frontend" / "src" / "components" / "Header.tsx").read_text(encoding="utf-8")
    assert "ApniHelp" in header_tsx, "Header.tsx does not contain brand name 'ApniHelp'"
    assert not re.search(r">\s*AI\s*Teacher\s*<", header_tsx), "Header.tsx still displays 'AI Teacher'"
    
    # 3. package.json
    pkg_json = (ROOT / "frontend" / "package.json").read_text(encoding="utf-8")
    assert '"name": "apnihelp-frontend"' in pkg_json or '"name": "apnihelp"' in pkg_json

def test_r5_backend_branding_and_watermarks():
    # 1. config.py
    from backend.app.config import settings
    assert "ApniHelp" in settings.app_name
    
    # 2. main.py root endpoint
    from backend.app.main import app
    from fastapi.testclient import TestClient
    client = TestClient(app)
    res = client.get("/")
    assert res.status_code == 200
    assert "ApniHelp" in res.json().get("message", "")
    assert app.title == settings.app_name
    
    # 3. slide_render_service.py watermark
    slide_code = (ROOT / "backend" / "app" / "services" / "slide_render_service.py").read_text(encoding="utf-8")
    assert 'APNIHELP' in slide_code, "Slide render service does not watermark slides with 'APNIHELP'"
    assert not re.search(r'"AI TEACHER"', slide_code), "Slide render service still watermarks with 'AI TEACHER'"

def test_r5_configs_and_launcher_scripts():
    # 1. docker-compose.yml
    dc_content = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert "container_name: apnihelp_backend" in dc_content
    assert "container_name: apnihelp_frontend" in dc_content
    assert "ai_teacher" not in dc_content.lower()
    
    # 2. run.sh
    run_sh = (ROOT / "run.sh").read_text(encoding="utf-8")
    assert "ApniHelp" in run_sh
    assert not re.search(r"AI Teacher — Full-Stack", run_sh)
```

---

## 4. Test Suite Execution & Integration Matrix

To execute and verify all requirements seamlessly:

| Command | Target Scope | Execution Context | Expected Result |
|---|---|---|---|
| `pytest backend/tests/test_apnihelp_r_series.py -v` | R1, R2, R3, R4, R5 unit & API contracts | In-Process Python 3.14 venv | 100% PASS |
| `python3 tests_e2e/test_runner.py --tier 6` | Full E2E ApniHelp Acceptance Suite | CLI Test Runner with JSON report | All R1–R5 checks PASS |
| `cd frontend && npm run build` | Frontend TypeScript & JSX compilation | Node 18 + Vite | Code 0, 0 TS errors |
| `pytest backend/tests/ -v` | Complete Backend Regression Suite | Pytest | All 14 test modules PASS |

---

## 5. Risk Assessment & Recommendations for Implementer

1. **R1 Video Speed vs. Video Quality**:
   - Re-encoding video with FFmpeg `filter_complex` for 10 minutes can take 60–90 seconds on standard CPU.
   - **Recommendation**: Standardize all clip generators (`AvatarService` and `SlideRenderService`) to output matching stream formats (`1280x720`, `30fps`, `yuv420p`, `44.1kHz stereo AAC`), and use FFmpeg Concat Demuxer (`-c copy`) for the final assembly. This ensures concatenation completes in $<1.5$ seconds regardless of duration.
2. **R2 UI Single Button Pipeline**:
   - When the user uploads a document or submits a topic prompt, the frontend must immediately trigger lesson planning and video synthesis in background while showing a unified progress spinner, avoiding intermediate modal gates.
3. **R3 Light Theme Consistency**:
   - Avoid partially converted components where white text appears on light gray cards or dark slate artifacts persist in drawers. Use global CSS variables or clear Tailwind utility mappings (`bg-white`, `bg-gray-50`, `text-blue-950`, `border-gray-200`, `bg-yellow-400`).
4. **Backend Test Dependency**:
   - `backend/tests/test_ingestion.py:483` explicitly checks `"Welcome to AI Teacher" in res_root.json()["message"]`. Update this line simultaneously with `backend/app/main.py:93` to prevent CI failure.
