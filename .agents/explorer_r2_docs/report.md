# Comprehensive Documentation & Architecture Investigation Report

**Project**: AI Teacher — Full-Stack Adaptive Educational Platform  
**Agent**: `explorer_r2_docs` (Read-Only Documentation & Architecture Investigator)  
**Date**: 2026-09-01  
**Working Directory**: `/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_r2_docs`  
**Workspace Root**: `/home/dev/Desktop/projects/AI-InnovationHackathon`  

---

## Executive Summary

This report delivers a thorough investigation and architectural blueprint for the complete documentation suite of the **AI Teacher** platform. Following an exhaustive audit of the workspace, backend APIs, frontend components, media generation services, and test harnesses, this document establishes the precise structure, detailed contents, interface contracts, and diagram specifications needed to build out production-ready, hackathon-winning documentation.

The documentation plan encompasses:
1. `README.md` — The central project hub featuring an executive overview, architecture summary, quickstart guide, demo-video generation instructions, and complete feature inventory.
2. `docs/architecture.md` — Deep-dive system architecture, multi-tier data flow, architecture decision records (ADRs), and vector/PNG/SVG architecture diagrams.
3. `docs/api_specification.md` — Complete REST & WebSocket API reference detailing 25 endpoints with request/response Pydantic models, JSON examples, HTTP status codes, and `curl` snippets.
4. `docs/setup_and_deployment.md` — Comprehensive deployment guide covering single-command `./run.sh`, Docker Compose multi-container setup, manual local execution, environment configuration, and troubleshooting.
5. `docs/user_guide.md` — Step-by-step user journey across the full teaching loop (Ingest → Plan → Video → Checkpoints → Misconceptions → Quiz → Report → Profile) and instructions for generating 2+ minute demo videos.
6. `docs/multilingual_support.md` — Architectural guide for multilingual education covering English & Hindi neural TTS voice mappings, Devanagari rendering, mid-session language switching, and prompt localization.

---

## Table of Contents

- [1. Current Documentation Inventory & Gap Analysis](#1-current-documentation-inventory--gap-analysis)
- [2. Requirements Analysis from ORIGINAL_REQUEST.md](#2-requirements-analysis-from-original_requestmd)
- [3. Documentation Architecture & Directory Structure](#3-documentation-architecture--directory-structure)
- [4. Detailed Plan: README.md](#4-detailed-plan-readmemd)
- [5. Detailed Plan: docs/architecture.md (with Diagrams)](#5-detailed-plan-docsarchitecturemd-with-diagrams)
- [6. Detailed Plan: docs/api_specification.md](#6-detailed-plan-docsapi_specificationmd)
- [7. Detailed Plan: docs/setup_and_deployment.md](#7-detailed-plan-docssetup_and_deploymentmd)
- [8. Detailed Plan: docs/user_guide.md](#8-detailed-plan-docsuser_guidemd)
- [9. Detailed Plan: docs/multilingual_support.md](#9-detailed-plan-docsmultilingual_supportmd)
- [10. Architecture Diagram Specifications (SVG & PNG)](#10-architecture-diagram-specifications-svg--png)
- [11. Verification & Link Consistency Strategy](#11-verification--link-consistency-strategy)

---

## 1. Current Documentation Inventory & Gap Analysis

### 1.1 Workspace Audit Findings

An exhaustive scan of the `/home/dev/Desktop/projects/AI-InnovationHackathon` workspace revealed the following state:

| Artifact Path | Current Status | Description / Content |
|---|---|---|
| `/README.md` | **MISSING** | No root README currently exists in the workspace. |
| `/docs/` | **MISSING** | No dedicated documentation folder exists in the root. |
| `/docs/architecture.md` | **MISSING** | Architecture documentation does not yet exist. |
| `/docs/architecture_diagram.svg` | **MISSING** | Vector architecture diagram does not yet exist. |
| `/docs/architecture_diagram.png` | **MISSING** | Raster architecture diagram does not yet exist. |
| `/docs/api_specification.md` | **MISSING** | Dedicated API reference file does not yet exist. |
| `/docs/setup_and_deployment.md`| **MISSING** | Dedicated setup and deployment guide does not yet exist. |
| `/docs/user_guide.md` | **MISSING** | User guide and demo generation instructions do not yet exist. |
| `/docs/multilingual_support.md`| **MISSING** | Multilingual architecture guide does not yet exist. |
| `/PROJECT.md` | **PRESENT** | High-level system architecture, feature inventory (F1.1–F7.1), and interface contracts. |
| `/TEST_INFRA.md` | **PRESENT** | E2E testing infrastructure specification and dual-mode test harness design. |
| `/TEST_READY.md` | **PRESENT** | E2E testing track readiness declaration (56/56 tests passing across 4 tiers). |
| `/docker-compose.yml` | **PRESENT** | Multi-container definitions for backend, frontend, and Milvus vectorstore. |
| `/run.sh` | **PRESENT** | Shell script for single-command launch of backend (FastAPI :8000) and frontend (Vite :3000). |
| `/backend/app/main.py` | **PRESENT** | FastAPI server mounting 5 routers, CORS, exception handlers, and `/api/v1/health`. |
| `/frontend/src/App.tsx` | **PRESENT** | React UI managing the complete user journey and interactive state. |

### 1.2 Identified Gaps to Fulfill

1. **Root Documentation Hub**: Need a standard, comprehensive `README.md` meeting all hackathon presentation criteria.
2. **Modular Documentation Directory (`docs/`)**: Need a well-structured `docs/` hierarchy with clear separation of concerns.
3. **Visual Architecture Diagrams**: Need high-clarity SVG and PNG architecture diagrams illustrating the 5 core milestones and data flow.
4. **Comprehensive API Reference**: Need exhaustive documentation for all 25 active REST endpoints with JSON schemas, payload examples, and status codes.
5. **Operational Guides**: Need clean, tested instructions for Docker Compose, `./run.sh`, manual development, and troubleshooting.
6. **User Journey & Demo Guidelines**: Need step-by-step instructions for running the end-to-end teaching loop and generating sample demo videos.
7. **Multilingual Specifications**: Need formal documentation of English/Hindi neural voice pipelines and mid-session switching mechanics.

---

## 2. Requirements Analysis from ORIGINAL_REQUEST.md

According to `ORIGINAL_REQUEST.md`, the documentation and platform deliverables must satisfy the following explicit criteria:

### 2.1 Core Architectural Requirements
- **R1. Learning Material Ingestion & RAG**: Multi-format parsing (PDF, DOCX, PPT/PPTX, TXT), structure-aware chunking, vector embeddings with BM25 fallback, parametric topic mode.
- **R2. Personalized Lesson Planning**: Learner profiling (level: beginner/intermediate/advanced, language: en/hi, time budget: 5–60 min), structured pedagogical sequencing, domain-aware visual slide specs, formative checkpoint pause questions.
- **R3. AI Teaching Video Generation (Hybrid)**: Talking avatar segments (audio-driven viseme animation / Wav2Lip) for intro & summary; subject-aware visual slides (Math LaTeX, CS Code with Pygments, Biology cellular diagrams, History timelines) for concept explanation; multilingual TTS via `edge-tts` / `gTTS`; FFmpeg 1280x720 30fps H.264/AAC stitching.
- **R4. Interactive & Adaptive Teaching Loop**: In-video pause markers, LLM evaluation of student answers, misconception diagnosis with scaffolding/analogies (not just right/wrong), follow-up comprehension checks, mid-session language switching, side-panel tutor chat.
- **R5. Assessment & Persistent Learning Profile**: Dynamic post-lesson quiz generation, rubric grading, diagnostic learning reports (scores, strong/weak concepts, revision advice), persistent student profile (SQLite/JSON), next-step topic recommendations.

### 2.2 Explicit Documentation Constraints & Standards
1. **Format**: Valid Markdown with clean Table of Contents (TOC), structured heading hierarchies (`#`, `##`, `###`), and syntax-highlighted code blocks.
2. **`README.md`**: Project overview, architecture summary, setup instructions, deployment guide, and demo-video generation guidelines (must pass spell-check and grammar verification).
3. **`docs/` Folder**: Separate sections for architecture, API specification, setup/deployment, user guide, and multilingual support.
4. **Architecture Diagrams**: Must include both **PNG** and **SVG** format diagrams.
5. **Internal Link Integrity**: All relative links between `README.md` and files within `docs/` must resolve cleanly without broken anchors or missing targets.

---

## 3. Documentation Architecture & Directory Structure

The recommended file layout for the project's documentation is as follows:

```
/home/dev/Desktop/projects/AI-InnovationHackathon/
├── README.md                           # Main Project Overview, Quickstart, Features, Demo Guidelines
├── docs/                               # Dedicated Documentation Folder
│   ├── architecture.md                 # System Architecture, Subsystems, Dataflow, ADRs
│   ├── architecture_diagram.svg        # Scalable Vector Graphics Architecture Diagram
│   ├── architecture_diagram.png        # High-Resolution Raster Architecture Diagram
│   ├── api_specification.md            # Exhaustive REST API Specification (25 Endpoints)
│   ├── setup_and_deployment.md         # Deployment Guide (Docker, run.sh, Local, Env Vars)
│   ├── user_guide.md                   # End-to-End User Guide & Demo Video Generation
│   └── multilingual_support.md         # English/Hindi TTS, Avatar Sync & Mid-Session Switching
├── PROJECT.md                          # Engineering Blueprint & Feature Inventory
├── TEST_INFRA.md                       # E2E Test Suite Specification
└── TEST_READY.md                       # E2E Test Suite Readiness Declaration
```

---

## 4. Detailed Plan: README.md

### 4.1 Purpose and Target Audience
The `README.md` serves as the primary landing page for hackathon judges, open-source contributors, and developers. It must be concise yet comprehensive, visually appealing, grammatically pristine, and equipped with one-click navigation to deeper documentation.

### 4.2 Required Sections & Outline

1. **Header & Badges**:
   - Project Title: `AI Teacher — Full-Stack Adaptive Educational Platform`
   - Badges: Build Status (`Passing`), E2E Test Suite (`56/56 Passed`), Python (`3.11`), Frontend (`React 18 / Vite`), Backend (`FastAPI`), License (`MIT`), Video Engine (`FFmpeg 720p 30fps`).
2. **Executive Overview & The Teaching Paradigm**:
   - Motivation: Traditional video lectures are passive and monolithic. AI Teacher implements a genuine human teaching loop: **Understand → Plan → Explain → Demonstrate → Question → Evaluate → Adapt → Continue**.
   - Hybrid Video Innovation: Merging talking avatar human presence with rich, domain-aware technical visual slides (LaTeX equations, IDE code traces, anatomical diagrams, historical timelines).
3. **Core Feature Highlights (Milestones R1–R5)**:
   - *R1 Ingestion & RAG*: Multi-format parsers (PDF, DOCX, PPTX, TXT) + Parametric Topic mode + Hybrid Cosine/BM25 retrieval.
   - *R2 Personalized Planning*: Tailored by level (Beginner/Intermediate/Advanced), duration (5–60 min), and language.
   - *R3 Hybrid Video Generation*: High-speed 2.5D audio-reactive viseme avatar + subject-aware slide renderers + `edge-tts` / `gTTS` multilingual audio.
   - *R4 Interactive Teaching Loop*: Checkpoint pause questions, misconception diagnosis with analogies, follow-up verification, mid-session language switching, side-panel tutor chat.
   - *R5 Assessment & Analytics*: Dynamic quiz generation, rubric grading, diagnostic learning reports, persistent student profile, next-step recommendations.
4. **Architecture Overview & System Diagram**:
   - High-level text and ASCII diagram linking to `docs/architecture.md` and `docs/architecture_diagram.svg`.
5. **Technology Stack Table**:
   - Component, Technology, Purpose, Free-Tier Compliance.
6. **Quick Start Guide (3 Execution Options)**:
   - Option 1: Single-command script (`./run.sh`).
   - Option 2: Docker Compose (`docker-compose up --build`).
   - Option 3: Manual Local Development (`uvicorn` + `npm run dev`).
7. **Demo Video Generation Guidelines**:
   - How to run automated video generation on sample topics (Math Calculus, CS Binary Search, Cell Biology, Industrial Revolution) producing 2+ minute stitched MP4 files with pause checkpoints.
8. **Automated Testing & Quality Assurance**:
   - Overview of 4-Tier E2E test runner (`python3 tests_e2e/test_runner.py`), passing 100% of 56 tests.
9. **Documentation Hub**:
   - Table of links to all 5 dedicated guides in `docs/`.
10. **License & Acknowledgments**:
    - AI Innovation Hackathon 2026 attribution.

---

## 5. Detailed Plan: docs/architecture.md (with Diagrams)

### 5.1 Purpose
Provides an in-depth, structural breakdown of the AI Teacher software architecture, subsystem dependencies, data models, state machines, and key design decisions.

### 5.2 Required Sections & Outline

1. **System Architecture Overview**:
   - Layered architecture: Presentation Layer (React/Vite) → API Gateway Layer (FastAPI) → Service Domain Layer (Ingestion, Planner, Video, Interaction, Assessment, Profile) → Engine & Provider Layer (LLM Clients, Neural TTS, Slide Renderers, FFmpeg, Vector Store).
2. **Subsystem Deep Dives**:
   - **Ingestion & RAG Engine (`R1`)**: Chunking strategies, `NumpyVectorStore` cosine similarity calculations, Okapi BM25 lexical ranking fallback, hybrid reciprocal rank fusion, parametric seed generation.
   - **Pedagogical Lesson Planner (`R2`)**: Adaptive sequencing algorithm, time budget allocation (5 min vs 60 min), cognitive load balancing, visual slide spec synthesis, checkpoint question placement.
   - **Hybrid Video Generation Pipeline (`R3`)**:
     - *TTS Synthesis*: `edge-tts` WebSocket interface with `gTTS` HTTP fallback and local harmonic PCM voice synthesis fallback.
     - *2.5D Audio-Reactive Viseme Avatar*: RMS audio energy envelope extraction, 5-viseme phonetic mouth opening states, 3.2s periodic eye blinking, sinusoidal breathing bobbing, real-time equalizer HUD, Wav2Lip CLI backend hook.
     - *Subject-Aware Slide Renderers*: Matplotlib LaTeX formula & graph generator, Pygments syntax-highlighted IDE window renderer, cellular diagram callout renderer, chronological timeline milestone renderer.
     - *FFmpeg Concat Demuxer*: Assembly of clips into 1280x720 30fps H.264/AAC MP4 with `-movflags +faststart`.
   - **Interactive & Adaptive Teaching Loop (`R4`)**: Checkpoint pause marker synchronization, LLM-based rubric evaluation, cognitive misconception classifier, analogy-driven re-explanation generator, follow-up validation loop, mid-session language switching state machine.
   - **Assessment & Profile Engine (`R5`)**: Post-lesson diagnostic quiz generation, multi-concept rubric grading, persistent SQLite/JSON student profiles, next-step recommendation graph.
3. **End-to-End Sequence & Data Flow**:
   - Step-by-step chronological sequence diagram tracing a learner's journey from document upload to final report and next-step recommendation.
4. **Architecture Decision Records (ADRs)**:
   - *ADR-001*: In-Memory Pure-Python Vector Store with BM25 vs External Milvus (Zero-dependency cold start).
   - *ADR-002*: High-Speed Audio-Driven 2.5D Viseme Avatar vs Cloud Video APIs (Hackathon zero-cost constraint & instant rendering speed).
   - *ADR-003*: Edge-TTS Neural Voice Engine with Two-Tier Fallback (High fidelity multilingual speech without paid API keys).
   - *ADR-004*: FFmpeg Concat Demuxer with HTTP 206 Byte Range Streaming (Seamless web player seeking and low latency).
5. **Diagram Embeds**:
   - References and embedded SVG/PNG diagrams (`architecture_diagram.svg`, `architecture_diagram.png`).

---

## 6. Detailed Plan: docs/api_specification.md

### 6.1 Purpose
Comprehensive REST and WebSocket API reference for all backend endpoints. Enables frontend developers, third-party integrators, and automated test runners to interact with the API seamlessly.

### 6.2 Complete Route Catalog (25 Endpoints)

#### Group 1: Learning Materials & Ingestion (`/api/v1/materials`)
1. `POST /api/v1/materials/upload`: Ingest educational file (PDF, DOCX, PPT, PPTX, TXT, MD), chunk, embed, and index.
2. `POST /api/v1/materials/topic`: Generate parametric seed syllabus from LLM knowledge when no file is uploaded.
3. `POST /api/v1/materials/query`: Query hybrid vector/BM25 store for grounded context chunks.
4. `GET /api/v1/materials/{doc_id}`: Retrieve document/topic metadata, page count, and summary.
5. `GET /api/v1/materials`: List all indexed materials and topics in the system.

#### Group 2: Lesson Planning & Review (`/api/v1/lessons`)
6. `POST /api/v1/lessons/plan`: Synthesize personalized, adaptive lesson plan tailored to profile and grounded material.
7. `GET /api/v1/lessons/{plan_id}`: Retrieve saved lesson plan by ID.
8. `PUT /api/v1/lessons/{plan_id}`: Update, reorder, or customize lesson plan segments prior to video synthesis.
9. `GET /api/v1/lessons`: List all synthesized lesson plans.

#### Group 3: Hybrid Video Generation (`/api/v1/video`)
10. `POST /api/v1/video/generate`: Trigger asynchronous multi-stage video generation task.
11. `GET /api/v1/video/status/{task_id}`: Poll status, stage, completion percentage, and asset URLs.
12. `GET /api/v1/video/manifest/{video_id}`: Fetch complete VideoManifest with continuous chapters and pause checkpoint markers.
13. `GET /api/v1/video/stream/{video_id}`: Stream MP4 video file with HTTP 206 Range header support.

#### Group 4: Interactive Teaching Loop (`/api/v1/interactive`)
14. `POST /api/v1/interactive/evaluate`: Evaluate student answer during checkpoint pause, diagnose misconceptions, and generate analogies.
15. `POST /api/v1/interactive/chat`: Real-time RAG-grounded contextual Q&A with side-panel AI tutor.
16. `POST /api/v1/interactive/switch-language`: Switch session language mid-lesson while preserving state.
17. `GET /api/v1/interactive/session/{session_id}`: Retrieve active session state, misconception history, and progress.

#### Group 5: Assessment & Learner Profiles (`/api/v1/assessment` & `/api/v1/profile`)
18. `POST /api/v1/assessment/generate`: Dynamically generate post-lesson diagnostic quiz.
19. `POST /api/v1/assessment/submit`: Submit quiz answers for rubric grading and learning report generation.
20. `GET /api/v1/assessment/report/{submission_id}`: Fetch previously generated learning report.
21. `GET /api/v1/profile/{student_id}`: Retrieve persistent learning profile, mastery statistics, and weak areas.
22. `PUT /api/v1/profile/{student_id}`: Update learner preferences (language, level, name, weak areas).
23. `GET /api/v1/profile/{student_id}/recommendations`: Synthesize adaptive next-step study roadmap.

#### Group 6: System & Health
24. `GET /api/v1/health`: System health probe, LLM provider, vector index counts, video stitcher status.
25. `GET /`: API root greeting and documentation index.

### 6.3 Standard Endpoint Documentation Template
For each endpoint, the specification must include:
- **HTTP Method & Path**
- **Summary & Description**
- **Request Parameters** (Path, Query, Form-Data)
- **Request Body JSON Schema & Concrete Example**
- **Response Status Codes** (`200 OK`, `201 Created`, `202 Accepted`, `400 Bad Request`, `404 Not Found`, `413 Entity Too Large`, `422 Unprocessable Entity`, `500 Server Error`)
- **Response Body JSON Schema & Concrete Example**
- **Executable `curl` Command**

---

## 7. Detailed Plan: docs/setup_and_deployment.md

### 7.1 Purpose
Guides users and evaluators through launching the AI Teacher application across various environments (local development, Docker Compose, production containers).

### 7.2 Required Sections & Outline

1. **System Prerequisites**:
   - Operating System: Linux (Ubuntu 20.04+ recommended), macOS, or Windows WSL2.
   - Python: 3.11+
   - Node.js: 18+ (with `npm`)
   - System Utilities: `ffmpeg` (with `libx264` and `libmp3lame`), `git`, `curl`
   - Docker & Docker Compose (optional, for containerized execution).
2. **Method 1: Single-Command Quickstart (`./run.sh`)**:
   - Execution command: `chmod +x run.sh && ./run.sh`
   - Under the hood: Directory initialization (`data/uploads`, `data/plans`, `data/rendered_videos`, etc.), Python/Node runtime verification, frontend dependency install, FastAPI backend start on `:8000`, Vite frontend start on `:3000`, graceful cleanup trap on `Ctrl+C`.
3. **Method 2: Multi-Container Docker Compose**:
   - Execution command: `docker-compose up --build`
   - Container breakdown:
     - `ai_teacher_backend`: FastAPI on port 8000 with FFmpeg runtime and mounted data volume.
     - `ai_teacher_frontend`: Node 18 runtime on port 3000 serving React web app.
     - `ai_teacher_vectorstore`: Milvus 2.4.0 vector database on port 19530 (with fallback to internal Numpy vector store).
4. **Method 3: Manual Step-by-Step Local Development**:
   - Backend setup: Virtual environment creation, `pip install -r backend/requirements.txt`, running `uvicorn backend.app.main:app --reload --port 8000`.
   - Frontend setup: `cd frontend`, `npm install`, `npm run dev`.
5. **Environment Configuration (`.env`)**:
   - Complete table of environment variables:
     - `GROQ_API_KEY`: Groq free-tier API key (optional; fallback to parametric knowledge).
     - `GEMINI_API_KEY`: Google AI Studio Gemini API key (optional).
     - `HOST` / `PORT`: Server host (`0.0.0.0`) and port (`8000`).
     - `TTS_DEFAULT_VOICE_EN`: Default English neural voice (`en-US-GuyNeural`).
     - `TTS_DEFAULT_VOICE_HI`: Default Hindi neural voice (`hi-IN-MadhurNeural`).
     - `AVATAR_ENGINE`: Avatar engine selector (`viseme_2_5d` or `wav2lip`).
6. **Health Verification & Smoke Testing**:
   - `curl http://localhost:8000/api/v1/health`
   - Verifying frontend availability at `http://localhost:3000`.
7. **Comprehensive Troubleshooting Guide**:
   - *Issue 1*: `ffmpeg: command not found` → Fix: `sudo apt-get install -y ffmpeg`.
   - *Issue 2*: Port 8000 or 3000 already in use → Fix: Identifying and killing orphan PIDs or configuring alternate ports.
   - *Issue 3*: Edge-TTS connection timeout in restricted networks → Fix: System automatically falls back to `gTTS` and offline harmonic PCM waveform.
   - *Issue 4*: Video player Range seeking errors → Fix: Verifying HTTP 206 Range headers in backend `video.py`.

---

## 8. Detailed Plan: docs/user_guide.md

### 8.1 Purpose
Provides a detailed walkthrough of the end-to-end user experience, illustrating how a learner or instructor interacts with every stage of the platform, alongside instructions for generating demo videos for hackathon evaluation.

### 8.2 Required Sections & Outline

1. **The Human Teaching Loop Journey**:
   - Detailed walkthrough of each step in the AI Teacher workflow:
     - **Step 1: Document Upload or Topic Ingestion**: Drag-and-drop PDF, DOCX, PPTX, or enter a topic (e.g., "Calculus Limits", "Binary Search Trees", "Cellular Biology", "The Industrial Revolution").
     - **Step 2: Learner Profile Configuration**: Select Level (Beginner, Intermediate, Advanced), Language (English, Hindi), Time Budget (5 min to 60 min), and optional learning goals.
     - **Step 3: Visual Lesson Plan Reviewer & Customization**: Inspect generated module cards, review visual slide specs (LaTeX equations, code blocks, diagrams), reorder or edit segment scripts before video synthesis.
     - **Step 4: Hybrid Video Synthesis & Playback**: Launch video rendering and watch real-time progress bar. Experience the hybrid video player:
       - Talking avatar introduction establishing lesson context and rapport.
       - Subject-aware visual slides explaining core theoretical mechanisms with synchronized narration.
     - **Step 5: In-Video Interactive Checkpoints & Misconception Remediation**:
       - Automatic video pause at pedagogical checkpoints.
       - Answer evaluation: If student answers incorrectly, the AI diagnoses the specific misconception, provides an analogy-driven re-explanation, and serves a targeted follow-up question before resuming video.
     - **Step 6: Real-Time AI Tutor Chat & Mid-Session Language Switch**:
       - Asking unscripted questions in the side panel during video playback.
       - Switching language on the fly (e.g., "Explain this in Hindi") without losing lesson progress.
     - **Step 7: Post-Lesson Diagnostic Quiz & Assessment**:
       - Taking dynamic post-lesson quiz covering key concepts.
       - Automated rubric grading with concept mastery breakdown.
     - **Step 8: Diagnostic Learning Report & Progress Analytics**:
       - Viewing strong concepts, weak areas, identified misconceptions, and suggested next topics.
       - Inspecting persistent profile showing cumulative learning history across sessions.
2. **Demo Video Generation Guidelines**:
   - Instructions for generating complete, standalone MP4 lesson videos for presentation:
     - Running the standalone video generation script: `python3 test_scripts/test_stitcher.py`.
     - Running real-world E2E persona scenarios (Tier 4) to generate 2+ minute videos with interactive pause markers for Math, Computer Science, Biology, and History.
     - Accessing generated MP4 files in `data/rendered_videos/` and manifests in `data/rendered_videos/manifests/`.
     - Recommendations for screen-recording live interactive checkpoint pauses for video pitch submissions.

---

## 9. Detailed Plan: docs/multilingual_support.md

### 9.1 Purpose
Documents the multilingual architecture of the AI Teacher platform, detailing how English and Hindi (and future language extensions) are supported across TTS audio synthesis, avatar lip-sync, visual slide rendering, interactive question evaluation, and mid-session language switching.

### 9.2 Required Sections & Outline

1. **Multilingual Architecture & Design Principles**:
   - Universal accessibility: Delivering high-quality STEM education in regional languages without linguistic compromise.
   - Dual-mode support: Full native Hindi (Devanagari script + Hindi audio) and English.
2. **Neural TTS Voice Mapping & Synthesizer Pipeline**:
   - Detailed voice mapping table:
     - English Male: `en-US-GuyNeural`
     - English Female: `en-US-AriaNeural` / `en-US-JennyNeural`
     - English Indian Accent: `en-IN-PrabhatNeural`
     - Hindi Male (Default): `hi-IN-MadhurNeural`
     - Hindi Female: `hi-IN-SwaraNeural`
     - Spanish: `es-ES-AlvaroNeural` / `es-ES-ElviraNeural`
     - French: `fr-FR-HenriNeural` / `fr-FR-DeniseNeural`
     - German: `de-DE-ConradNeural` / `de-DE-KatjaNeural`
   - Fallback hierarchy: `edge-tts` (Neural) → `gTTS` (Google Translate TTS) → Local Harmonic PCM Waveform Synthesizer.
3. **Devanagari & Unicode Typography in Visual Slides**:
   - Matplotlib and PIL font configuration for crisp Devanagari script rendering.
   - Bidi and Unicode normalization for complex mathematical formulas combined with Hindi explanatory text.
4. **Mid-Session Dynamic Language Switching (`/api/v1/interactive/switch-language`)**:
   - State preservation architecture: Transferring session history, diagnosed misconceptions, and current concept index when a student requests a language switch.
   - Response generation: Translating summary of preceding content, providing localized next prompt, and configuring subsequent evaluation in the new language.
5. **Evaluation and Testing of Multilingual Capabilities**:
   - Review of E2E Tier 4 Scenario 1 (High School Calculus in Hindi with Devanagari equations and Hindi quiz grading).
   - Verifying phonetic viseme synchronization with Hindi phonology in the 2.5D avatar generator.

---

## 10. Architecture Diagram Specifications (SVG & PNG)

### 10.1 Diagram Topology & Layout

The architecture diagram illustrates the end-to-end data flow across 5 distinct tiers:

1. **Tier 1: Presentation Layer (Frontend - React 18 / Vite / Tailwind)**
   - Ingestion Dropzone & Topic Ingest UI
   - Learner Profile Config (Level, Language, Time Budget)
   - Visual Lesson Plan Reviewer & Editor
   - Custom Interactive Video Player with Pause Checkpoint Overlays
   - Misconception & Re-Explanation Modal Drawer
   - Grounded Side-Panel AI Tutor Chat
   - Post-Lesson Quiz & Learning Report Analytics Dashboard
2. **Tier 2: API Gateway & Router Layer (FastAPI :8000)**
   - `/api/v1/materials` (Upload, Topic, RAG Query)
   - `/api/v1/lessons` (Plan Synthesizer, Plan Editor)
   - `/api/v1/video` (Async Generation, Polling, HTTP 206 Streaming, Manifests)
   - `/api/v1/interactive` (Checkpoint Evaluation, Misconception Diagnosis, Language Switcher, Tutor Chat)
   - `/api/v1/assessment` & `/api/v1/profile` (Quiz Generator, Rubric Grading, Profile Persistence, Recommendations)
3. **Tier 3: Core Pedagogical & AI Services Layer**
   - R1: Ingestion Parser (PDF, DOCX, PPTX, TXT) & Hybrid Cosine/BM25 Vector Store
   - R2: Adaptive Lesson Planner (Duration Scaling, Pedagogical Sequencing, Visual Specs)
   - R3: Hybrid Video Stitcher & Manifest Assembler
   - R4: Interactive Checkpoint Evaluator & Misconception Diagnosis Engine
   - R5: Quiz Generator, Rubric Grader & Next-Step Recommender
4. **Tier 4: Media & Subject-Aware Compute Engines**
   - Multilingual Neural TTS Engine (`edge-tts` / `gTTS` / Local PCM)
   - Audio-Driven 2.5D Viseme Avatar Generator (RMS Envelope, 5 Visemes, Eye Blink, Studio HUD) + Wav2Lip Hook
   - Subject-Aware Visual Slide Renderers:
     - Math: Matplotlib LaTeX Equations + 2D Function Curve Grapher
     - CS: Pygments Syntax-Highlighted IDE Frame + Runtime Complexity Watch
     - Biology: Cellular Anatomical Diagram with Callout Pins
     - History: Horizontal Chronological Timeline with Milestone Cards
   - FFmpeg 1280x720 30fps H.264/AAC Stitcher (`-movflags +faststart`)
5. **Tier 5: Infrastructure, AI Providers & Storage**
   - Free-Tier LLMs (Groq Llama 3 / Google AI Studio Gemini 1.5 Flash)
   - Pure-Python `NumpyVectorStore` & In-Memory Indices
   - SQLite / JSON Profile & Session Database
   - Local File Storage (`data/uploads`, `data/plans`, `data/rendered_videos`, `data/profiles`)

### 10.2 Production SVG Generation Design

The vector diagram will be generated as a modern dark-themed, 1200x800 SVG (`docs/architecture_diagram.svg`) using crisp rounded containers, color-coded subsystem badges (Emerald for Ingestion, Blue for Planning, Purple for Video, Amber for Interactive, Rose for Assessment), glowing connection lines, and clean typographic hierarchy.

A Python script using Matplotlib or Pillow can render the corresponding raster version (`docs/architecture_diagram.png`) with identical fidelity.

---

## 11. Verification & Link Consistency Strategy

To guarantee that all documentation passes hackathon verification and acceptance criteria:

1. **Relative Link Cross-Verification**:
   - `README.md` links directly to `docs/architecture.md`, `docs/api_specification.md`, `docs/setup_and_deployment.md`, `docs/user_guide.md`, `docs/multilingual_support.md`, `docs/architecture_diagram.svg`, and `docs/architecture_diagram.png`.
   - Each `docs/*.md` file includes a top navigation bar with working links back to `README.md` and sister documentation pages.
2. **Spell-Check & Grammar Validation**:
   - Zero typos, clear pedagogical vocabulary, accurate technical terminology, and consistent markdown table alignment.
3. **Code Snippet Executability**:
   - All `curl` commands, CLI invocations (`./run.sh`, `python3 tests_e2e/test_runner.py`), and Docker commands tested against the actual codebase.
4. **Interface Contract Alignment**:
   - All documented JSON schemas match the active Pydantic models in `backend/app/models/` verbatim.

---

## Conclusion & Next Steps

This investigation provides the complete structural blueprint and detailed content plans required to produce the full documentation suite for the AI Teacher platform. With all 25 API endpoints mapped, architecture subsystems specified, SVG/PNG diagram designs established, and multilingual mechanisms documented, the implementation phase can proceed with total clarity and zero ambiguity.
