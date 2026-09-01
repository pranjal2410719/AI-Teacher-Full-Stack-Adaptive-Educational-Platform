# Project: AI Teacher — Full-Stack Adaptive Educational Platform

## Architecture & System Overview

The **AI Teacher** platform is a full-stack, modular, human-in-the-loop educational system following the complete human teaching paradigm:
**Understand → Plan → Explain → Demonstrate → Question → Evaluate → Adapt → Continue**.

```
+---------------------------------------------------------------------------------------------------------+
|                                     Frontend: Next.js / React Web App                                   |
|  - Document Dropzone & Topic Ingestion UI       - Learner Profile Config (Level, Lang, Time)            |
|  - Visual Lesson Plan Reviewer & Editor         - Custom Interactive Video Player with Pause Markers    |
|  - Misconception & Re-explanation Drawer        - Post-Lesson Quiz & Learning Report Dashboard          |
|  - Multilingual Language Switcher               - Persistent Profile & Next-Topic Recommender           |
+---------------------------------------------------------------------------------------------------------+
                                                     |
                                   REST / WebSockets (JSON API)
                                                     v
+---------------------------------------------------------------------------------------------------------+
|                                        Backend: FastAPI Core Server                                     |
|                                                                                                         |
|  +---------------------------+  +---------------------------+  +-------------------------------------+  |
|  |  R1: Ingestion & RAG      |  |  R2: Lesson Planner       |  |  R3: Hybrid Video Pipeline          |  |
|  |  - PDF, DOCX, PPTX, TXT   |  |  - Multi-Level Adaptation |  |  - Multilingual Neural TTS          |  |
|  |  - Structure-Aware Chunks |  |  - Duration Scaling       |  |  - Audio-Driven 2.5D Avatar Gen     |  |
|  |  - Numpy Vector Store     |  |  - Visual Slide Specs     |  |  - Math/Code/Diagram/Timeline Slides|  |
|  |  - Topic Parametric Mode  |  |  - Pedagogical Sequencing |  |  - FFmpeg 720p H.264/AAC Stitcher   |  |
|  +---------------------------+  +---------------------------+  +-------------------------------------+  |
|                                                                                                         |
|  +---------------------------+  +---------------------------+  +-------------------------------------+  |
|  |  R4: Interactive Teaching |  |  R5: Assessment & Profile |  |  Core AI & Data Providers           |  |
|  |  - In-Video Pause Checks  |  |  - Dynamic Post-Quiz Gen  |  |  - Groq / Gemini Free Tier LLMs     |  |
|  |  - Misconception Diagnosis|  |  - Rubric-Based Grading   |  |  - SQLite / JSON Profile Store      |  |
|  |  - Adaptive Re-explanation|  |  - Strong/Weak Analytics  |  |  - Pure-Python BM25 & Cosine RAG    |  |
|  |  - Mid-Session Lang Switch|  |  - Next-Topic Recommender |  |  - Local File Storage & Cache       |  |
|  +---------------------------+  +---------------------------+  +-------------------------------------+  |
+---------------------------------------------------------------------------------------------------------+
```

---

## Feature Inventory

| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| F1.1 | Multi-Format Document Ingestion | Ingests PDF (`pypdf`), DOCX (`python-docx`), PPT/PPTX (`python-pptx`), and TXT files, extracting structured text, slides, and metadata. | M1 | Survey / `ORIGINAL_REQUEST.md § R1` |
| F1.2 | Plain-Text Topic Parametric Mode | Generates structured educational seed syllabus using LLM parametric knowledge when no document is uploaded. | M1 | Survey / `ORIGINAL_REQUEST.md § R1` |
| F1.3 | Structure-Aware Chunking & Indexing | Chunks text along slide/section headers with sliding overlap and stores chunk metadata (page, slide, section). | M1 | Survey / `ORIGINAL_REQUEST.md § R1` |
| F1.4 | High-Speed Vector Retrieval & BM25 Fallback | In-memory `NumpyVectorStore` with Gemini/Groq dense embeddings + zero-API pure-Python BM25 lexical fallback for grounded context. | M1 | Survey / `ORIGINAL_REQUEST.md § R1` |
| F2.1 | Learner Profile Capture | Collects student educational level (Beginner/Intermediate/Advanced), language (English, Hindi, etc.), time budget (5–60 min), prior knowledge, and goals. | M2 | Survey / `ORIGINAL_REQUEST.md § R2` |
| F2.2 | Adaptive Pedagogical Lesson Planner | Synthesizes structured JSON lesson plans (concepts, sequence, duration scaling, visual slide specs, checkpoint pause markers). | M2 | Survey / `ORIGINAL_REQUEST.md § R2` |
| F2.3 | Visual Lesson Plan Reviewer & Editor API | Provides endpoints and data models for learners to inspect, customize, and approve lesson plans before video synthesis. | M2 | Survey / `ORIGINAL_REQUEST.md § R2` |
| F3.1 | Multilingual Neural TTS Engine | Converts lesson scripts to high-quality audio using `edge-tts` (`en-US-GuyNeural`, `hi-IN-MadhurNeural`) with instant `gTTS` fallback. | M3 | Survey / `ORIGINAL_REQUEST.md § R3` |
| F3.2 | Audio-Driven Talking Avatar Generator | Synthesizes talking avatar segments (intro, transitions, summary) using audio-driven 2.5D dynamic viseme animation and Wav2Lip support. | M3 | Survey / `ORIGINAL_REQUEST.md § R3` |
| F3.3 | Subject-Aware Visual Slide Renderers | Dynamically renders Math LaTeX derivations, CS syntax-highlighted code in IDE frames, Biology diagrams, and History timelines into video slides. | M3 | Survey / `ORIGINAL_REQUEST.md § R3` |
| F3.4 | FFmpeg Video Assembly & Stitcher | Assembles avatar clips, visual slide clips, and synchronized audio into a unified 1280x720 30fps H.264/AAC web-streamable MP4. | M3 | Survey / `ORIGINAL_REQUEST.md § R3` |
| F3.5 | Real-Time Video Generation Progress API | Streams multi-stage progress (TTS → Avatar → Slides → Stitching) to the client. | M3 | Survey / `ORIGINAL_REQUEST.md § R3` |
| F4.1 | In-Video Question Pause Markers | Generates timestamped checkpoint markers in video manifests that trigger interactive questions during playback. | M4 | Survey / `ORIGINAL_REQUEST.md § R4` |
| F4.2 | Student Response Evaluator | LLM-based evaluation of open-ended and MCQ student answers against pedagogical rubrics and grounded source material. | M4 | Survey / `ORIGINAL_REQUEST.md § R4` |
| F4.3 | Misconception Diagnosis & Re-Explanation | Diagnoses root misconceptions from wrong answers and generates scaffolding with alternative analogies rather than just marking "incorrect". | M4 | Survey / `ORIGINAL_REQUEST.md § R4` |
| F4.4 | Follow-Up Comprehension Checks | Prompts targeted follow-up questions after re-explanation to verify conceptual mastery before resuming the lesson. | M4 | Survey / `ORIGINAL_REQUEST.md § R4` |
| F4.5 | Mid-Session Multilingual Switching | Switches lesson interaction and explanation language on the fly (e.g., English to Hindi) while retaining conversational context. | M4 | Survey / `ORIGINAL_REQUEST.md § R4` |
| F4.6 | Grounded Side-Panel AI Tutor Chat | Provides real-time, RAG-grounded contextual Q&A for unscripted student questions during video viewing. | M4 | Survey / `ORIGINAL_REQUEST.md § R4` |
| F5.1 | Dynamic Post-Lesson Quiz Generator | Generates comprehensive multi-format quizzes (MCQ, short-answer) tailored to concepts taught and student checkpoint history. | M5 | Survey / `ORIGINAL_REQUEST.md § R5` |
| F5.2 | Automated Quiz Grading & Learning Report | Grades quiz submissions, identifies strong and weak concepts, and generates an actionable diagnostic learning report. | M5 | Survey / `ORIGINAL_REQUEST.md § R5` |
| F5.3 | Persistent Student Learning Profile | Persists student mastery history, weak concepts, and studied topics in SQLite/JSON for cross-session tracking. | M5 | Survey / `ORIGINAL_REQUEST.md § R5` |
| F5.4 | Next-Step Recommendation Engine | Generates personalized recommendations for next topics, prerequisite refreshers, and revision paths based on student performance. | M5 | Survey / `ORIGINAL_REQUEST.md § R5` |
| F6.1 | Full-Stack Frontend Web Application | Complete Next.js / React UI implementing upload/topic input, profile setup, plan review, interactive video player, quiz, and analytics dashboard. | M6 | Survey / Full-Stack Spec |
| F6.2 | One-Command Setup & Local Verification | Automated setup scripts, environment verification, and clean local run commands (`./run.sh` / `npm run dev` + `uvicorn`). | M6 | Survey / Acceptance Criteria |
| F7.1 | 4-Tier Automated E2E Test Suite & Hardening | Complete test suite covering Tier 1 (Features), Tier 2 (Boundaries), Tier 3 (Cross-Feature Combinations), Tier 4 (Real-World Scenarios), and Tier 5 (Adversarial Coverage). | M7 / E2E Track | Survey / E2E Track Spec |

---

## Milestones

| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| **E2E Track** | E2E Testing Suite & Harness | Design `TEST_INFRA.md`, implement test runner, fixtures, and Tiers 1-4 tests (Feature, Boundary, Combinations, Real-World scenarios for Math, CS, Biology, History) and publish `TEST_READY.md`. | none | DONE |
| **M1** | Ingestion & RAG Engine | PDF, DOCX, PPTX, TXT parsers, chunking, `NumpyVectorStore` + BM25 fallback, grounding retrieval, topic-only parametric mode. | none | DONE |
| **M2** | Personalized Lesson Planner | Learner profile models, pedagogical sequencing (Beginner/Inter/Adv, 5m..60m), visual slide spec generation, plan editor APIs. | M1 | DONE |
| **M3** | Hybrid Video Generation Pipeline | `edge-tts` & `gTTS` multilingual audio, 2.5D Audio-Driven Viseme Avatar generator, subject-aware slide renderers (Math LaTeX, CS Code, Bio Diagram, History Timeline), FFmpeg MP4 stitcher. | M2 | DONE |
| **M4** | Interactive & Adaptive Teaching Loop | Checkpoint pause markers, LLM evaluation, misconception diagnosis & pedagogical re-explanation, follow-up questions, mid-session language switching, side-panel tutor chat. | M2, M3 | DONE |
| **M5** | Assessment & Learning Profile Engine | Post-lesson quiz generator, rubric grading, learning report synthesis, persistent SQLite/JSON student profiles, next-step recommendation engine. | M4 | DONE |
| **M6** | Frontend Full-Stack Web App Integration | Next.js/React UI (upload, profile, plan review, interactive video player with question overlay, quiz, analytics dashboard), FastAPI routing, setup scripts. | M1..M5 | DONE |
| **M7** | Final Milestone: 100% E2E Test Pass & Adversarial Hardening | Verify 100% pass on E2E test suite (Tiers 1-4) against running application + Tier 5 Adversarial Coverage Hardening. | M6, E2E Track | DONE |
| **M8** | Comprehensive Documentation & Diagrams | Complete README.md, docs/ suite (architecture, API spec, setup, user guide, multilingual), SVG & PNG diagrams, link verification & spell-check. | M1..M6 | DONE |
| **M9** | Docker Packaging & Demo Generation Pipeline | backend/frontend Dockerfiles, docker-compose.yml, run.sh with automated >= 2 min video generation and interactive checkpoints. | M1..M7 | DONE |

---

## Interface Contracts

### 1. Ingestion & RAG ↔ Lesson Planner
- **Function / Endpoint**: `POST /api/v1/materials/upload`, `POST /api/v1/materials/topic`, `POST /api/v1/materials/query`
- **Data Models**:
  - `DocumentMetadata`: `{document_id: str, filename: str, file_type: str, total_pages: int, chunk_count: int, extracted_summary: str}`
  - `RAGQuery`: `{document_id: Optional[str], topic_id: Optional[str], query: str, top_k: int = 4}`
  - `RAGResponse`: `{query: str, results: List[ChunkMatch]}`

### 2. Lesson Planner ↔ Video Pipeline & Teaching Loop
- **Function / Endpoint**: `POST /api/v1/lessons/plan`, `GET /api/v1/lessons/{plan_id}`
- **Data Models**:
  - `LearnerProfile`: `{student_id: str, level: "beginner"|"intermediate"|"advanced", language: str, time_budget_min: int, prior_knowledge: Optional[str], learning_goal: Optional[str]}`
  - `LessonPlan`: `{plan_id: str, title: str, target_duration_sec: int, level: str, language: str, modules: List[LessonSegmentPlan]}`
  - `LessonSegmentPlan`: `{segment_id: str, order: int, segment_type: "avatar_intro"|"visual_concept"|"demonstration"|"checkpoint_question"|"avatar_summary", title: str, duration_sec: int, script: str, visual_spec: VisualSpec, checkpoint_question: Optional[CheckpointQuestion]}`
  - `VisualSpec`: `{visual_type: "math_equation"|"code_snippet"|"diagram"|"timeline"|"general_slide", subject_domain: str, headline: str, bullet_points: List[str], code_content: Optional[str], code_language: Optional[str], latex_equations: List[str], diagram_mermaid: Optional[str], timeline_events: Optional[List[Dict[str, str]]]}`

### 3. Video Pipeline ↔ Frontend & Player
- **Function / Endpoint**: `POST /api/v1/video/generate`, `GET /api/v1/video/status/{task_id}`, `GET /api/v1/video/stream/{video_id}`
- **Data Models**:
  - `VideoGenerationRequest`: `{plan_id: str, voice_preference: Optional[str]}`
  - `VideoManifest`: `{video_id: str, video_url: str, duration_sec: float, segments: List[VideoSegmentMeta], pause_checkpoints: List[CheckpointPauseMarker]}`
  - `CheckpointPauseMarker`: `{checkpoint_id: str, timestamp_sec: float, question_id: str, concept: str, question: CheckpointQuestion}`

### 4. Interactive Teaching Loop ↔ Frontend & Profile
- **Function / Endpoint**: `POST /api/v1/interactive/evaluate`, `POST /api/v1/interactive/switch-language`, `POST /api/v1/interactive/chat`
- **Data Models**:
  - `AnswerEvaluationRequest`: `{session_id: str, question_id: str, student_answer: str, concept: str, context: Optional[str]}`
  - `EvaluationResult`: `{is_correct: bool, score: float, feedback: str, misconception: Optional[str], re_explanation: Optional[str], follow_up_question: Optional[CheckpointQuestion], can_proceed: bool}`
  - `LanguageSwitchRequest`: `{session_id: str, target_language: str, current_concept_id: Optional[str]}`
  - `LanguageSwitchResponse`: `{language: str, translated_summary: str, next_prompt: str}`

### 5. Assessment & Profile ↔ Frontend
- **Function / Endpoint**: `POST /api/v1/assessment/quiz/generate`, `POST /api/v1/assessment/quiz/submit`, `GET /api/v1/profile/{student_id}`
- **Data Models**:
  - `QuizSubmission`: `{quiz_id: str, student_id: str, answers: Dict[str, str]}`
  - `LearningReport`: `{report_id: str, student_id: str, score_percent: float, total_questions: int, strong_concepts: List[str], weak_concepts: List[str], misconceptions_identified: List[str], recommended_revision: List[str], suggested_next_topics: List[str]}`
  - `StudentProfile`: `{student_id: str, preferred_level: str, preferred_language: str, completed_lessons: List[str], concept_mastery: Dict[str, float], weak_areas: List[str], total_time_spent_min: int}`

---

## Code Layout

```
/home/dev/Desktop/projects/AI-InnovationHackathon/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                     # FastAPI app entry point & router mounting
│   │   ├── config.py                   # Environment & settings (Groq/Gemini keys, paths)
│   │   ├── models/                     # Pydantic data schemas
│   │   │   ├── __init__.py
│   │   │   ├── ingestion.py
│   │   │   ├── lesson_plan.py
│   │   │   ├── video.py
│   │   │   ├── interaction.py
│   │   │   └── profile.py
│   │   ├── services/                   # Core business logic services
│   │   │   ├── __init__.py
│   │   │   ├── llm_client.py           # Unified Groq / Gemini free-tier LLM wrapper
│   │   │   ├── ingestion_service.py    # Document parsers (PDF, DOCX, PPTX, TXT)
│   │   │   ├── vector_store.py         # Numpy Cosine Vector Store + BM25 Ranker
│   │   │   ├── planner_service.py      # Adaptive lesson planner
│   │   │   ├── tts_service.py          # edge-tts & gTTS multilingual audio generator
│   │   │   ├── avatar_service.py       # 2.5D viseme avatar generator & lip-sync
│   │   │   ├── slide_render_service.py # Math, Code, Diagram, Timeline visual slide renderers
│   │   │   ├── video_stitcher.py       # FFmpeg video stitching & manifest assembler
│   │   │   ├── interaction_service.py  # Checkpoint evaluation, misconception re-explanation
│   │   │   ├── assessment_service.py   # Quiz generator & grading engine
│   │   │   └── profile_service.py      # SQLite / JSON student profile & recommender
│   │   └── api/                        # REST & WebSocket API routes
│   │       ├── __init__.py
│   │       ├── materials.py
│   │       ├── lessons.py
│   │       ├── video.py
│   │       ├── interactive.py
│   │       └── profile.py
│   └── tests/                          # Backend unit & integration tests
│       ├── test_ingestion.py
│       ├── test_planner.py
│       ├── test_video.py
│       ├── test_interaction.py
│       └── test_profile.py
├── frontend/
│   ├── package.json
│   ├── next.config.js / vite.config.ts
│   ├── src/
│   │   ├── app/ (or pages/)
│   │   ├── components/
│   │   │   ├── Ingestion/              # Document upload & topic selector
│   │   │   ├── Profile/                # Learner profile configuration
│   │   │   ├── Planner/                # Visual lesson plan reviewer/editor
│   │   │   ├── VideoPlayer/            # Custom player with synchronized pause checkpoints
│   │   │   ├── Interaction/            # Question modal, misconception re-explanation drawer
│   │   │   ├── Assessment/             # Post-lesson quiz interface & learning report
│   │   │   └── Analytics/              # Student profile & progress analytics
│   │   ├── services/api.ts             # Typed API client connecting to FastAPI
│   │   └── types/index.ts              # TypeScript interface definitions matching backend schemas
├── tests_e2e/                          # 4-Tier E2E Test Suite (Opaque-Box)
│   ├── test_runner.py                  # E2E test runner executing Tiers 1-4
│   ├── fixtures/                       # Test documents (PDF, DOCX, PPTX, TXT)
│   ├── tier1_feature_coverage/         # >= 5 tests per feature
│   ├── tier2_boundary_corner/          # Boundary, edge case, and error inputs
│   ├── tier3_cross_feature/            # Pairwise feature interaction tests
│   └── tier4_real_world_scenarios/     # Complete real-world teaching scenarios (Math, CS, Bio, Hist)
├── run.sh                              # Single command setup & launch script
└── README.md                           # Documentation, architecture, and usage guide
```
