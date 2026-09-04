# System Architecture & Technical Design

[![Build Status](https://img.shields.io/badge/Build-Passing-emerald.svg)](../README.md)
[![E2E Test Suite](https://img.shields.io/badge/E2E%20Tests-56%2F56%20Passed%20(100%25)-blue.svg)](../TEST_READY.md)
[![Architecture Tier](https://img.shields.io/badge/Architecture-5--Tier%20Modular-purple.svg)](#system-architecture-overview)
[![Video Engine](https://img.shields.io/badge/Video%20Pipeline-FFmpeg%20720p%2030fps-rose.svg)](#hybrid-video-generation-pipeline-r3)

Welcome to the comprehensive architectural documentation for the **ApniHelp** platform. This document provides an in-depth exploration of the system's design, component interactions, pedagogical state machines, media rendering pipelines, and technical decision rationale.

---

## Table of Contents

- [1. Executive Architectural Overview](#1-executive-architectural-overview)
- [2. The 8-Phase Human Teaching Loop](#2-the-8-phase-human-teaching-loop)
- [3. Visual Architecture Diagram](#3-visual-architecture-diagram)
- [4. Multi-Tier Subsystem Breakdown](#4-multi-tier-subsystem-breakdown)
  - [Tier 1: Presentation Layer (React / Vite)](#tier-1-presentation-layer-react-vite)
  - [Tier 2: API Gateway & Router Layer (FastAPI)](#tier-2-api-gateway-router-layer-fastapi)
  - [Tier 3: Core Pedagogical Services (R1–R5)](#tier-3-core-pedagogical-services-r1r5)
  - [Tier 4: Media & Visual Compute Engines](#tier-4-media-visual-compute-engines)
  - [Tier 5: AI Providers, Vector Store & Storage](#tier-5-ai-providers-vector-store-storage)
- [5. Core Algorithms & Subsystem Deep Dives](#5-core-algorithms-subsystem-deep-dives)
  - [5.1 Multi-Format Ingestion & Hybrid RAG (R1)](#51-multi-format-ingestion-hybrid-rag-r1)
  - [5.2 Personalized Lesson Planning & Duration Scaling (R2)](#52-personalized-lesson-planning-duration-scaling-r2)
  - [5.3 Hybrid Video Generation Pipeline & Manifests (R3)](#53-hybrid-video-generation-pipeline-manifests-r3)
  - [5.4 2.5D Audio-Driven Viseme Avatar & Wav2Lip (R3)](#54-25d-audio-driven-viseme-avatar-wav2lip-r3)
  - [5.5 Subject-Aware Visual Slide Renderers (R3)](#55-subject-aware-visual-slide-renderers-r3)
  - [5.6 Interactive Teaching Loop & Misconception Remediation (R4)](#56-interactive-teaching-loop-misconception-remediation-r4)
  - [5.7 Multilingual State Machine & Language Switching (R4)](#57-multilingual-state-machine-language-switching-r4)
  - [5.8 Assessment, Rubric Grading & Persistent Profile Graph (R5)](#58-assessment-rubric-grading-persistent-profile-graph-r5)
- [6. Architecture Decision Records (ADRs)](#6-architecture-decision-records-adrs)
- [7. Verification & Quality Assurance](#7-verification-quality-assurance)
- [8. Navigation & Related Documentation](#8-navigation-related-documentation)

---

## 1. Executive Architectural Overview

Traditional online educational video delivery is inherently passive, linear, and non-adaptive. If a student struggles with a prerequisite concept, the video continues uninterrupted, leading to cognitive disengagement.

The **ApniHelp** platform solves this fundamental limitation by combining:
1. **RAG-Grounded Parametric & Document Ingestion**: Eliminating hallucinations by grounding lesson plans in uploaded course materials (PDF, DOCX, PPTX, TXT) or verified syllabus structures.
2. **Pedagogical Duration Scaling**: Dynamically structuring learning modules whether the student has 5 minutes for a quick summary or 60 minutes for a deep dive.
3. **Hybrid Neural Video Synthesis**: Merging human teacher rapport (via 2.5D audio-driven viseme avatars) with rich, subject-aware technical visuals (LaTeX math equations, syntax-highlighted IDE windows, biological cell callouts, chronological timelines).
4. **Active Human-in-the-Loop Interaction**: Enforcing checkpoint pause questions directly inside the video stream, diagnosing root student misconceptions, and providing scaffolded analogies before resuming playback.
5. **Continuous Mastery Tracking**: Persisting cross-session learning profiles and synthesizing adaptive next-step study roadmaps.

---

## 2. The 8-Phase Human Teaching Loop

The entire architecture is engineered around the complete cognitive model of expert human tutoring:

```
+---------------------------------------------------------------------------------------------------------+
|                                  THE 8-PHASE HUMAN TEACHING LOOP                                        |
+---------------------------------------------------------------------------------------------------------+
|  1. UNDERSTAND   ──► Ingest uploaded documents or syllabus topic into hybrid RAG vector store.          |
|  2. PLAN         ──► Synthesize personalized lesson plan tailored to student level and time budget.     |
|  3. EXPLAIN      ──► Deliver core concepts using AI-narrated subject-aware visual slides.               |
|  4. DEMONSTRATE  ──► Walk through step-by-step worked examples, code traces, and formula derivations.   |
|  5. QUESTION     ──► Automatically pause the video at pedagogical checkpoints to prompt the student.    |
|  6. EVALUATE     ──► Evaluate student answers against rubrics and diagnose underlying misconceptions.   |
|  7. ADAPT        ──► Provide scaffolded re-explanations with real-world analogies and follow-up checks. |
|  8. CONTINUE     ──► Resume lesson stream, administer post-lesson quiz, and recommend next learning path.|
+---------------------------------------------------------------------------------------------------------+
```

---

## 3. Visual Architecture Diagram

The ApniHelp platform is organized into five decoupled tiers:

![ApniHelp System Architecture](architecture_diagram.png)

*Vector format available for high-DPI scaling: [architecture_diagram.svg](architecture_diagram.svg).*

---

## 4. Multi-Tier Subsystem Breakdown

### Tier 1: Presentation Layer (React / Vite)
The user interface is built as a single-page application (SPA) using React 18, Vite, and Tailwind CSS. It communicates with the backend via REST endpoints and streaming media protocols:
- **Document Dropzone & Topic Ingest UI**: Multi-file drag-and-drop supporting PDF, DOCX, PPTX, TXT, and free-form topic seed inputs.
- **Learner Profile Configurator**: Allows students to select knowledge level (`Beginner`, `Intermediate`, `Advanced`), target language (`English`, `Hindi`), time budget (`5–60 min`), and learning goals.
- **Visual Lesson Plan Reviewer & Editor**: Interactive card interface enabling users to inspect, reorder, modify scripts, or customize slide specs prior to video synthesis.
- **Custom Interactive HTML5 Video Player**: Synchronized with backend `VideoManifest` data, supporting HTTP 206 byte-range streaming, chapter jumping, and interactive checkpoint overlays.
- **Misconception Drawer & Re-Explanation Modal**: Non-intrusive slide-over providing step-by-step analogy scaffolding when an incorrect answer is submitted.
- **Grounded Side-Panel AI Tutor Chat**: Real-time RAG query panel enabling students to ask unscripted questions while watching the video.
- **Post-Lesson Quiz & Diagnostic Dashboard**: Visual analytics display showing scores, strong vs. weak concepts, and personalized study roadmaps.

### Tier 2: API Gateway & Router Layer (FastAPI)
The backend is driven by FastAPI running on Python 3.11 (`:8000`), exposing 25 REST endpoints organized into 5 modular routers:
1. `/api/v1/materials/*`: Multi-format parsing, text extraction, structure-aware chunking, vector indexing, and hybrid RAG search.
2. `/api/v1/lessons/*`: Lesson plan generation, retrieval, customization, and plan listing.
3. `/api/v1/video/*`: Asynchronous multi-stage video generation, polling, manifest delivery, and HTTP 206 partial-content streaming.
4. `/api/v1/interactive/*`: Checkpoint answer evaluation, misconception diagnosis, analogy generation, mid-session language switching, and tutor chat.
5. `/api/v1/assessment/*` & `/api/v1/profile/*`: Dynamic quiz generation, rubric grading, persistent profile management, and next-topic recommendations.

### Tier 3: Core Pedagogical Services (R1–R5)
- **Ingestion & RAG Engine (`R1`)**: Extracts structured text and slide content using `pypdf`, `python-docx`, and `python-pptx`. Splits content with sliding window overlaps and generates parametric seed content when no file is uploaded.
- **Adaptive Lesson Planner (`R2`)**: Allocates time budgets, determines pedagogical pacing, selects domain-specific slide types, and generates formative checkpoint questions.
- **Hybrid Video Stitcher (`R3`)**: Coordinates the multi-stage asynchronous generation worker, generating TTS audio, avatar clips, visual slide clips, and final FFmpeg concatenation.
- **Interactive Teaching Loop Service (`R4`)**: Evaluates open-ended and MCQ student responses against rubrics, detects cognitive misconceptions, and generates contextual follow-up checks.
- **Assessment & Profile Service (`R5`)**: Synthesizes comprehensive diagnostic post-quizzes, evaluates submissions, updates student mastery matrices, and produces next-step study roadmaps.

### Tier 4: Media & Visual Compute Engines
- **Multilingual Neural TTS Engine**: Utilizes Microsoft Edge Neural Voices (`edge-tts`) with instant fallback to Google Translate TTS (`gTTS`) and an offline harmonic PCM synthesizer.
- **2.5D Audio-Driven Viseme Avatar Generator**: Analyzes audio RMS energy envelopes to drive 5 phonetic viseme mouth states, natural 3.2s periodic eye blinking, subtle breathing bobbing, and a real-time studio HUD.
- **Subject-Aware Visual Slide Renderers**:
  - *Math*: LaTeX equation typesetter and Matplotlib 2D function curve grapher.
  - *Computer Science*: Pygments syntax-highlighted IDE window with line numbers and algorithmic complexity indicators.
  - *Biology*: Anatomical and cellular structure diagrams with coordinate callout pins.
  - *History*: Chronological milestone cards and event timelines.
- **FFmpeg 1280x720 30fps H.264/AAC Stitcher**: Combines avatar clips and slide clips using the FFmpeg Concat demuxer with `-movflags +faststart` for instant web streaming.

### Tier 5: AI Providers, Vector Store & Storage
- **Free-Tier LLM Cloud Providers**: Integrates with Groq (`llama-3-70b-versatile`, `llama-3-8b-instant`) and Google AI Studio (`gemini-1.5-flash`), with an offline parametric heuristic fallback engine.
- **Vector Storage & Lexical Search**: High-speed, in-memory `NumpyVectorStore` performing dense cosine similarity paired with a pure-Python Okapi BM25 lexical inverted index.
- **Profile & Session Store**: SQLite database and JSON storage persisting learner records, mastery scores, and session histories across visits.
- **File System Assets**: Structured storage under `data/` managing uploads, lesson plans, rendered MP4 videos, manifests, quizzes, and learning reports.

---

## 5. Core Algorithms & Subsystem Deep Dives

### 5.1 Multi-Format Ingestion & Hybrid RAG (R1)

```
[Uploaded File] ──► [Parser (PDF/DOCX/PPTX/TXT)] ──► [Structure-Aware Chunker]
                                                              │
                                     ┌────────────────────────┴────────────────────────┐
                                     ▼                                                 ▼
                         [Dense Embedding Vector]                           [Okapi BM25 Inverted Index]
                                     │                                                 │
                                     └────────────────────────┬────────────────────────┘
                                                              ▼
                                              [Reciprocal Rank Fusion (RRF)]
                                                              ▼
                                              [Top-K Grounded Context Chunks]
```

1. **Document Parsing**: Extracted text preserves page numbers, slide titles, and table structures.
2. **Chunking Strategy**: Text is split into 400-word segments with 80-word sliding window overlaps. Chunks maintain metadata tags (`doc_id`, `chunk_id`, `page_number`, `heading`).
3. **Hybrid Search Scoring**: Given a user query $q$, the relevance score $S(c, q)$ for chunk $c$ is computed using Reciprocal Rank Fusion:
   $$S(c, q) = \frac{\alpha}{60 + \text{rank}_{\text{dense}}(c)} + \frac{1 - \alpha}{60 + \text{rank}_{\text{BM25}}(c)}$$
   where $\alpha = 0.6$ balances semantic similarity and exact keyword matching.

### 5.2 Personalized Lesson Planning & Duration Scaling (R2)

The planner service converts learner profile constraints into a structured sequence of pedagogical modules:

| Time Budget | Number of Modules | Segment Distribution | Checkpoint Frequency |
|---|---|---|---|
| **5–10 min** (Concise) | 3–4 modules | 1 Avatar Intro, 1–2 Concept Slides, 1 Avatar Summary | 1 Checkpoint Question |
| **15–25 min** (Standard) | 5–6 modules | 1 Avatar Intro, 3 Concept Slides, 1 Demonstration, 1 Avatar Summary | 2 Checkpoint Questions |
| **30–60 min** (Comprehensive) | 7–10 modules | 1 Avatar Intro, 4 Concept Slides, 2 Demonstrations, 1 Deep-Dive, 1 Avatar Summary | 3–4 Checkpoint Questions |

**Pedagogical Adaptation by Level**:
- **Beginner**: Emphasizes foundational definitions, intuitive analogies, simplified vocabulary, and conceptual multiple-choice questions.
- **Intermediate**: Introduces formal terminology, step-by-step derivations, practical code implementations, and short-answer questions.
- **Advanced**: Focuses on edge cases, mathematical proofs, asymptotic complexity analysis, and multi-step problem-solving questions.

### 5.3 Hybrid Video Generation Pipeline & Manifests (R3)

Video generation runs as an asynchronous background worker managed by `video_stitcher.py`:

```
                    [Lesson Plan JSON]
                            │
             ┌──────────────┴──────────────┐
             ▼                             ▼
    [Avatar Script]                [Visual Slide Spec]
             │                             │
    [TTS Audio Synthesis]         [TTS Audio Synthesis]
             │                             │
    [2.5D Viseme Avatar Video]    [Slide Frame Render + FFmpeg Loop]
             │                             │
             └──────────────┬──────────────┘
                            ▼
             [FFmpeg Concat Demuxer Assembly]
                            │
             ┌──────────────┴──────────────┐
             ▼                             ▼
   [Stitched 720p MP4 Video]     [VideoManifest JSON]
```

#### VideoManifest Structure
The `VideoManifest` coordinates continuous playback in the frontend while specifying exact timestamp pause triggers:
```json
{
  "video_id": "vid_abc123",
  "plan_id": "plan_xyz789",
  "title": "Introduction to Calculus Limits",
  "total_duration_sec": 135.4,
  "video_url": "/api/v1/video/stream/vid_abc123",
  "chapters": [
    { "chapter_id": "chap_1", "title": "Teacher Welcome", "start_time_sec": 0.0, "end_time_sec": 18.2, "segment_type": "avatar_intro" },
    { "chapter_id": "chap_2", "title": "Definition of a Limit", "start_time_sec": 18.2, "end_time_sec": 62.5, "segment_type": "visual_concept" }
  ],
  "pause_checkpoints": [
    {
      "checkpoint_id": "chk_1",
      "timestamp_sec": 62.5,
      "concept": "One-Sided Limits",
      "question": {
        "question_id": "q1",
        "question_text": "What happens when left-hand and right-hand limits differ?",
        "question_type": "multiple_choice",
        "options": ["Limit exists", "Limit does not exist", "Limit is zero", "Limit is infinity"],
        "correct_answer": "Limit does not exist"
      }
    }
  ]
}
```

### 5.4 2.5D Audio-Driven Viseme Avatar & Wav2Lip (R3)

The avatar generator produces lifelike talking head video from audio and static portrait assets:
1. **Audio Envelope Analysis**: The synthesized audio WAV file is sampled at 100ms intervals. Root-mean-square (RMS) energy is extracted and normalized to $[0.0, 1.0]$.
2. **Phonetic Viseme Mapping**:
   - $\text{RMS} < 0.05 \rightarrow$ `viseme_rest` (mouth closed)
   - $0.05 \le \text{RMS} < 0.20 \rightarrow$ `viseme_slight` (subtle open)
   - $0.20 \le \text{RMS} < 0.45 \rightarrow$ `viseme_open` (moderate open)
   - $0.45 \le \text{RMS} < 0.70 \rightarrow$ `viseme_wide` (wide vowel)
   - $\text{RMS} \ge 0.70 \rightarrow$ `viseme_o` (rounded plosive)
3. **Natural Dynamics**:
   - **Periodic Blinking**: A 150ms blink cycle triggers every 3.2 seconds.
   - **Breathing Bobbing**: A vertical sine displacement $y(t) = 3 \cdot \sin(2\pi \cdot 0.3 \cdot t)$ simulates breathing posture.
   - **Studio Equalizer HUD**: A dynamic audio waveform overlay displays in the lower corner to signify live speech.
4. **Wav2Lip Hook**: When enabled via `AVATAR_ENGINE=wav2lip`, the system delegates frame synthesis to the local Wav2Lip GAN model.

### 5.5 Subject-Aware Visual Slide Renderers (R3)

The platform generates high-definition visual slide frames customized to the subject domain:

```
+-----------------------------------------------------------------------------------------------+
|  DOMAIN                | VISUAL ENGINE             | OUTPUT ELEMENTS                          |
+------------------------+---------------------------+------------------------------------------+
|  Mathematics / Physics | Matplotlib / LaTeX Engine | Rendered equations, 2D curves, proofs    |
|  Computer Science      | Pygments + PIL IDE Frame  | Dark-theme editor, line numbers, O(N)    |
|  Biology / Medicine    | Coordinate Shape Engine   | Cell membranes, organelles, callout pins |
|  History / Humanities  | Chronological Layout      | Milestone cards, dates, event flow       |
+-----------------------------------------------------------------------------------------------+
```

Each rendered slide PNG is converted into a 720p H.264 video segment matching the exact duration of its narrated TTS audio.

### 5.6 Interactive Teaching Loop & Misconception Remediation (R4)

When video playback reaches a checkpoint timestamp, the video player pauses automatically. The student enters an answer, which is evaluated through the pedagogical evaluation engine:

```
[Student Response] ──► [LLM Rubric Evaluator]
                              │
               ┌──────────────┴──────────────┐
               ▼                             ▼
        [Answer Correct]             [Answer Incorrect]
               │                             │
      [Positive Feedback]           [Misconception Diagnosis]
               │                             │
      [Resume Video Stream]         [Scaffolded Analogy Generation]
                                             │
                                    [Targeted Follow-Up Question]
                                             │
                                    [Comprehension Verified?]
                                             │
                                    [Resume Video Stream]
```

- **Misconception Diagnosis**: Instead of a generic "Wrong, try again", the system identifies the cognitive error (e.g., *Confusing one-sided limit discontinuity with asymptote behavior*).
- **Scaffolded Analogy**: Synthesizes a real-world parallel (e.g., *Two trains approaching a broken bridge from opposite directions*).
- **Follow-Up Question**: Validates understanding before allowing the learner to resume video playback.

### 5.7 Multilingual State Machine & Language Switching (R4)

Learners can switch instruction language on the fly (e.g., from English to Hindi):
1. **Endpoint**: `POST /api/v1/interactive/switch-language`
2. **Context Migration**: The active session state retains all previously mastered concepts, weak concepts, and diagnosed misconceptions.
3. **Localized Prompting**: The system generates a Hindi recap of the current concept and transitions subsequent quiz questions and side-panel tutor conversations into Hindi (`hi-IN-MadhurNeural`).

### 5.8 Assessment, Rubric Grading & Persistent Profile Graph (R5)

Following video completion, the assessment engine conducts a comprehensive evaluation:
1. **Dynamic Quiz Generation**: Creates a balanced assessment (MCQs + conceptual short-answer) targeting the specific concepts taught in the lesson.
2. **Rubric-Based Grading**: Evaluates each response, computing a percentage mastery score for each concept.
3. **Diagnostic Learning Report**:
   - **Strong Concepts**: Topics with $\ge 80\%$ score.
   - **Weak Concepts**: Topics with $< 60\%$ score.
   - **Identified Misconceptions**: Summary of cognitive pitfalls encountered.
   - **Recommended Revision**: Specific review modules.
   - **Suggested Next Topics**: Adaptive next steps.
4. **Persistent Profile**: Stored in SQLite/JSON, tracking cumulative learning history across multiple sessions.

---

## 6. Architecture Decision Records (ADRs)

### ADR-001: In-Memory Pure-Python Vector Store with BM25 vs External Milvus
- **Status**: Accepted
- **Context**: Hackathon evaluation requires seamless zero-configuration startup without requiring external container dependencies to be running.
- **Decision**: Implemented `NumpyVectorStore` with cosine similarity and Okapi BM25 lexical ranking as the default zero-dependency storage engine, while maintaining Docker Compose support for Milvus 2.4.0.
- **Consequences**: Fast cold-start startup, instant local test execution, and full RAG capability without external dependencies.

### ADR-002: High-Speed 2.5D Audio-Driven Viseme Avatar vs Cloud Video APIs
- **Status**: Accepted
- **Context**: Cloud talking-head video APIs incur cost, latency (30–60s per clip), and network fragility.
- **Decision**: Developed a high-speed local 2.5D viseme avatar generator driven by RMS audio energy with Wav2Lip CLI support.
- **Consequences**: Instant rendering (~1.5s for 15s audio), zero API cost, 100% offline capability.

### ADR-003: Edge-TTS Neural Synthesis with Multi-Tier Fallback
- **Status**: Accepted
- **Context**: Natural-sounding multilingual audio (English and Hindi) is required without paid API keys.
- **Decision**: Implemented Microsoft Edge Neural Voices (`en-US-GuyNeural`, `hi-IN-MadhurNeural`) via `edge-tts` with fallback to `gTTS` and local harmonic PCM synthesis.
- **Consequences**: Studio-quality speech in English and Hindi, high resilience against network interruptions.

### ADR-004: FFmpeg Concat Demuxer with HTTP 206 Partial Content Streaming
- **Status**: Accepted
- **Context**: Users must be able to seek through generated videos without waiting for the entire file to download.
- **Decision**: Assembled clips using FFmpeg's concat demuxer with `-movflags +faststart` and implemented custom HTTP 206 Range header handling in FastAPI.
- **Consequences**: Instant seeking, low memory footprint, smooth HTML5 video player integration.

### ADR-005: Decoupled Video Manifests for Interactive Checkpoints
- **Status**: Accepted
- **Context**: Re-rendering an entire video whenever a student pauses or answers a question is computationally wasteful.
- **Decision**: Separated media rendering (continuous MP4 video) from interaction metadata (`VideoManifest` with timestamp pause markers).
- **Consequences**: Single video render pass per lesson plan; infinite interactivity, question branching, and re-explanations executed via client overlay without video re-encoding.

---

## 7. Verification & Quality Assurance

The architecture has been verified against a rigorous 4-Tier End-to-End Test Suite:
- **Tier 1 (Feature Coverage)**: 30 tests verifying R1 through R5.
- **Tier 2 (Boundary & Corner Cases)**: 18 tests verifying 0-byte uploads, corrupt files, Devanagari text, prompt injection defenses, and invalid IDs.
- **Tier 3 (Cross-Feature Combinations)**: 4 tests verifying end-to-end multi-service pipeline flows.
- **Tier 4 (Real-World Persona Scenarios)**: 4 tests covering Math in Hindi, College CS in English, Biology cell diagrams, and History timelines.

**Current Test Status**: **56/56 Tests Passed (100%)**.

---

## 8. Navigation & Related Documentation

| Document | Description |
|---|---|
| [Project Overview (README.md)](../README.md) | High-level project summary, features, and quickstart |
| [API Specification](api_specification.md) | Comprehensive reference for all 25 REST endpoints |
| [Setup & Deployment Guide](setup_and_deployment.md) | Docker Compose, `./run.sh`, and local setup instructions |
| [User Guide & Demo Video Walkthrough](user_guide.md) | End-to-end user journey and demo video generation |
| [Multilingual Support Guide](multilingual_support.md) | English/Hindi neural voice mappings and Devanagari rendering |
| [E2E Testing Infrastructure](../TEST_INFRA.md) | 4-tier testing specification and harness architecture |
| [E2E Testing Readiness Declaration](../TEST_READY.md) | 56/56 test suite readiness verification report |
