# REST API Specification Reference

[![Build Status](https://img.shields.io/badge/Build-Passing-emerald.svg)](../README.md)
[![FastAPI](https://img.shields.io/badge/API%20Framework-FastAPI%200.110-blue.svg)](https://fastapi.tiangolo.com/)
[![OpenAPI Spec](https://img.shields.io/badge/OpenAPI-3.1.0-orange.svg)](#api-overview)
[![Endpoints Documented](https://img.shields.io/badge/Endpoints-25%20Active-purple.svg)](#endpoint-catalog)

Welcome to the comprehensive REST API specification for the **ApniHelp Core Platform**. This document provides detailed contract references, Pydantic schemas, HTTP status codes, JSON payload examples, and executable `curl` commands for all 25 active endpoints.

---

## Table of Contents

- [1. API Overview & Conventions](#1-api-overview-conventions)
  - [Base URL & Protocol](#base-url-protocol)
  - [Authentication & Rate Limiting](#authentication-rate-limiting)
  - [Standard HTTP Status Codes](#standard-http-status-codes)
  - [Global Error Response Schema](#global-error-response-schema)
- [2. Endpoint Catalog](#2-endpoint-catalog)
- [3. Learning Materials & Ingestion (`/api/v1/materials`)](#3-learning-materials-ingestion-apiv1materials)
  - [3.1 Upload Educational Material (`POST /api/v1/materials/upload`)](#31-upload-educational-material-post-apiv1materialsupload)
  - [3.2 Ingest Parametric Topic (`POST /api/v1/materials/topic`)](#32-ingest-parametric-topic-post-apiv1materialstopic)
  - [3.3 Query RAG Vector Store (`POST /api/v1/materials/query`)](#33-query-rag-vector-store-post-apiv1materialsquery)
  - [3.4 Get Material Metadata (`GET /api/v1/materials/{doc_id}`)](#34-get-material-metadata-get-apiv1materialsdoc_id)
  - [3.5 List All Materials (`GET /api/v1/materials`)](#35-list-all-materials-get-apiv1materials)
- [4. Lesson Planning & Review (`/api/v1/lessons`)](#4-lesson-planning-review-apiv1lessons)
  - [4.1 Generate Personalized Lesson Plan (`POST /api/v1/lessons/plan`)](#41-generate-personalized-lesson-plan-post-apiv1lessonsplan)
  - [4.2 Get Saved Lesson Plan (`GET /api/v1/lessons/{plan_id}`)](#42-get-saved-lesson-plan-get-apiv1lessonsplan_id)
  - [4.3 Update or Reorder Lesson Plan (`PUT /api/v1/lessons/{plan_id}`)](#43-update-or-reorder-lesson-plan-put-apiv1lessonsplan_id)
  - [4.4 List All Lesson Plans (`GET /api/v1/lessons`)](#44-list-all-lesson-plans-get-apiv1lessons)
- [5. Hybrid Video Generation & Streaming (`/api/v1/video`)](#5-hybrid-video-generation-streaming-apiv1video)
  - [5.1 Trigger Asynchronous Video Generation (`POST /api/v1/video/generate`)](#51-trigger-asynchronous-video-generation-post-apiv1videogenerate)
  - [5.2 Poll Video Generation Status (`GET /api/v1/video/status/{task_id}`)](#52-poll-video-generation-status-get-apiv1videostatustask_id)
  - [5.3 Get Video Manifest (`GET /api/v1/video/manifest/{video_id}`)](#53-get-video-manifest-get-apiv1videomanifestvideo_id)
  - [5.4 Stream Video with HTTP 206 Range (`GET /api/v1/video/stream/{video_id}`)](#54-stream-video-with-http-206-range-get-apiv1videostreamvideo_id)
- [6. Interactive Teaching Loop (`/api/v1/interactive`)](#6-interactive-teaching-loop-apiv1interactive)
  - [6.1 Evaluate Checkpoint Answer (`POST /api/v1/interactive/evaluate`)](#61-evaluate-checkpoint-answer-post-apiv1interactiveevaluate)
  - [6.2 Side-Panel AI Tutor Chat (`POST /api/v1/interactive/chat`)](#62-side-panel-ai-tutor-chat-post-apiv1interactivechat)
  - [6.3 Mid-Session Language Switch (`POST /api/v1/interactive/switch-language`)](#63-mid-session-language-switch-post-apiv1interactiveswitch-language)
  - [6.4 Get Interaction Session State (`GET /api/v1/interactive/session/{session_id}`)](#64-get-interaction-session-state-get-apiv1interactivesessionsession_id)
- [7. Assessment & Quizzes (`/api/v1/assessment`)](#7-assessment-quizzes-apiv1assessment)
  - [7.1 Generate Post-Lesson Quiz (`POST /api/v1/assessment/generate`)](#71-generate-post-lesson-quiz-post-apiv1assessmentgenerate)
  - [7.2 Submit Quiz for Rubric Grading (`POST /api/v1/assessment/submit`)](#72-submit-quiz-for-rubric-grading-post-apiv1assessmentsubmit)
  - [7.3 Get Learning Report (`GET /api/v1/assessment/report/{submission_id}`)](#73-get-learning-report-get-apiv1assessmentreportsubmission_id)
- [8. Learner Profile & Recommendations (`/api/v1/profile`)](#8-learner-profile-recommendations-apiv1profile)
  - [8.1 Get Student Profile (`GET /api/v1/profile/{student_id}`)](#81-get-student-profile-get-apiv1profilestudent_id)
  - [8.2 Update Student Profile (`PUT /api/v1/profile/{student_id}`)](#82-update-student-profile-put-apiv1profilestudent_id)
  - [8.3 Get Adaptive Topic Recommendations (`GET /api/v1/profile/{student_id}/recommendations`)](#83-get-adaptive-topic-recommendations-get-apiv1profilestudent_idrecommendations)
- [9. System Health & Diagnostics](#9-system-health-diagnostics)
  - [9.1 System Health Check (`GET /api/v1/health`)](#91-system-health-check-get-apiv1health)
  - [9.2 API Root Discovery (`GET /`)](#92-api-root-discovery-get)
- [10. Navigation & Related Documentation](#10-navigation-related-documentation)

---

## 1. API Overview & Conventions

### Base URL & Protocol
```http
http://localhost:8000
```
All API responses are formatted in UTF-8 JSON. Video streams support HTTP 206 Partial Content byte ranges.

### Authentication & Rate Limiting
The ApniHelp API operates in hackathon demo mode with no mandatory API keys for client endpoints. CORS is configured to accept requests from all origins (`allow_origins=["*"]`).

### Standard HTTP Status Codes

| Code | Meaning | Usage Scenario |
|---|---|---|
| `200 OK` | Success | Synchronous request fulfilled successfully. |
| `201 Created` | Created | Resource successfully created (e.g. Lesson Plan). |
| `202 Accepted` | Accepted | Asynchronous task queued (e.g. Video Generation). |
| `400 Bad Request` | Client Error | Invalid parameter, empty file, or malformed input. |
| `404 Not Found` | Not Found | Requested entity (document, plan, video, session) does not exist. |
| `413 Payload Too Large` | Entity Too Large | Uploaded file exceeds the 50 MB threshold. |
| `416 Range Not Satisfiable` | Range Error | Video byte-range request exceeds available file size. |
| `422 Unprocessable Entity` | Validation Error | Request body failed Pydantic field validation. |
| `500 Server Error` | Server Error | Internal processing or synthesis exception. |

### Global Error Response Schema
```json
{
  "detail": "Descriptive error message explaining the failure."
}
```

---

## 2. Endpoint Catalog

| Group | Method | Path | Summary |
|---|---|---|---|
| **Materials** | `POST` | `/api/v1/materials/upload` | Ingest and index PDF, DOCX, PPTX, TXT document |
| **Materials** | `POST` | `/api/v1/materials/topic` | Ingest plain-text topic into parametric seed |
| **Materials** | `POST` | `/api/v1/materials/query` | Query hybrid dense/BM25 vector store |
| **Materials** | `GET` | `/api/v1/materials/{doc_id}` | Retrieve document metadata and summary |
| **Materials** | `GET` | `/api/v1/materials` | List all ingested materials |
| **Lessons** | `POST` | `/api/v1/lessons/plan` | Synthesize personalized adaptive lesson plan |
| **Lessons** | `GET` | `/api/v1/lessons/{plan_id}` | Fetch saved lesson plan by ID |
| **Lessons** | `PUT` | `/api/v1/lessons/{plan_id}` | Update or reorder lesson plan modules |
| **Lessons** | `GET` | `/api/v1/lessons` | List all generated lesson plans |
| **Video** | `POST` | `/api/v1/video/generate` | Trigger async multi-stage video generation |
| **Video** | `GET` | `/api/v1/video/status/{task_id}` | Poll generation stage, progress, and URLs |
| **Video** | `GET` | `/api/v1/video/manifest/{video_id}` | Fetch playback manifest and pause checkpoints |
| **Video** | `GET` | `/api/v1/video/stream/{video_id}` | Stream MP4 video with HTTP 206 byte ranges |
| **Interactive**| `POST` | `/api/v1/interactive/evaluate` | Evaluate checkpoint answer & diagnose misconceptions |
| **Interactive**| `POST` | `/api/v1/interactive/chat` | Contextual RAG Q&A with side-panel AI tutor |
| **Interactive**| `POST` | `/api/v1/interactive/switch-language` | Switch active session language preserving context |
| **Interactive**| `GET` | `/api/v1/interactive/session/{session_id}` | Fetch active session history and misconception state |
| **Assessment** | `POST` | `/api/v1/assessment/generate` | Generate dynamic post-lesson diagnostic quiz |
| **Assessment** | `POST` | `/api/v1/assessment/submit` | Submit quiz answers for rubric grading |
| **Assessment** | `GET` | `/api/v1/assessment/report/{submission_id}` | Retrieve previously generated learning report |
| **Profile** | `GET` | `/api/v1/profile/{student_id}` | Fetch learner profile, mastery, and history |
| **Profile** | `PUT` | `/api/v1/profile/{student_id}` | Update learner preferences and target goals |
| **Profile** | `GET` | `/api/v1/profile/{student_id}/recommendations` | Get personalized next-topic study roadmap |
| **System** | `GET` | `/api/v1/health` | System health probe and component metrics |
| **System** | `GET` | `/` | API root discovery and documentation links |

---

## 3. Learning Materials & Ingestion (`/api/v1/materials`)

### 3.1 Upload Educational Material (`POST /api/v1/materials/upload`)
Ingests an educational file (PDF, DOCX, PPT, PPTX, TXT, MD), parses structure, chunks content with sliding overlap, and builds hybrid dense + BM25 vector indices.

- **Content-Type**: `multipart/form-data`
- **Request Form Fields**:
  - `file`: `UploadFile` (Required, binary educational document)
  - `metadata`: `string` (Optional, JSON string for custom tags)
- **Status Codes**: `200 OK`, `400 Bad Request`, `413 Payload Too Large`, `500 Internal Error`

#### Example Request (`curl`)
```bash
curl -X POST http://localhost:8000/api/v1/materials/upload \
  -F "file=@tests_e2e/fixtures/calculus_limits.pdf"
```

#### Example Response (`200 OK`)
```json
{
  "document_id": "doc_a1b2c3d4",
  "filename": "calculus_limits.pdf",
  "file_type": "application/pdf",
  "file_size_bytes": 24890,
  "total_pages": 4,
  "chunk_count": 8,
  "extracted_summary": "Calculus Limits and Continuity: Formal epsilon-delta definitions, one-sided limits, and difference quotients.",
  "created_at": "2026-09-01T12:00:00Z"
}
```

---

### 3.2 Ingest Parametric Topic (`POST /api/v1/materials/topic`)
Generates structured educational grounding from LLM parametric knowledge when no file is uploaded.

- **Content-Type**: `application/json`
- **Request Body**:
```json
{
  "topic": "Binary Search Trees",
  "domain": "Computer Science",
  "target_level": "intermediate"
}
```

#### Example Request (`curl`)
```bash
curl -X POST http://localhost:8000/api/v1/materials/topic \
  -H "Content-Type: application/json" \
  -d '{"topic": "Binary Search Trees", "domain": "Computer Science", "target_level": "intermediate"}'
```

#### Example Response (`200 OK`)
```json
{
  "topic_id": "topic_bst_987",
  "topic": "Binary Search Trees",
  "domain": "Computer Science",
  "seed_concepts": [
    "Tree Node Structure and Invariants",
    "Binary Search Traversal (Inorder, Preorder, Postorder)",
    "Insertion, Deletion, and Balancing (AVL / Red-Black)",
    "Time Complexity: O(log N) Average vs O(N) Worst Case"
  ],
  "chunk_count": 6,
  "summary": "Core structural and algorithmic principles of Binary Search Trees.",
  "created_at": "2026-09-01T12:05:00Z"
}
```

---

### 3.3 Query RAG Vector Store (`POST /api/v1/materials/query`)
Retrieves top-$k$ grounded chunks using dense cosine similarity and Okapi BM25 ranking.

- **Content-Type**: `application/json`
- **Request Body**:
```json
{
  "document_id": "doc_a1b2c3d4",
  "query": "What is the formal epsilon delta definition of a limit?",
  "top_k": 3
}
```

#### Example Response (`200 OK`)
```json
{
  "query": "What is the formal epsilon delta definition of a limit?",
  "results": [
    {
      "chunk_id": "chk_001",
      "text": "For every epsilon > 0, there exists a delta > 0 such that 0 < |x - c| < delta implies |f(x) - L| < epsilon.",
      "score": 0.942,
      "page_number": 1,
      "heading": "Formal Limit Definition"
    }
  ]
}
```

---

### 3.4 Get Material Metadata (`GET /api/v1/materials/{doc_id}`)
Retrieves metadata for an indexed document or parametric topic.

- **Path Parameter**: `doc_id` (`string`, e.g. `doc_a1b2c3d4`)
- **Example Request (`curl`)**:
```bash
curl -X GET http://localhost:8000/api/v1/materials/doc_a1b2c3d4
```

---

### 3.5 List All Materials (`GET /api/v1/materials`)
Returns a list of all indexed documents and topics available for lesson planning.

- **Example Request (`curl`)**:
```bash
curl -X GET http://localhost:8000/api/v1/materials
```

---

## 4. Lesson Planning & Review (`/api/v1/lessons`)

### 4.1 Generate Personalized Lesson Plan (`POST /api/v1/lessons/plan`)
Synthesizes a structured, adaptive lesson plan tailored to learner profile, time budget, and grounded content.

- **Content-Type**: `application/json`
- **Request Body**:
```json
{
  "document_id": "doc_a1b2c3d4",
  "topic": "Calculus Limits",
  "learner_profile": {
    "student_id": "stu_dev101",
    "level": "intermediate",
    "language": "en",
    "time_budget_min": 15,
    "prior_knowledge": "Basic Algebra",
    "learning_goal": "Master limits and continuity"
  }
}
```

#### Example Request (`curl`)
```bash
curl -X POST http://localhost:8000/api/v1/lessons/plan \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "doc_a1b2c3d4",
    "learner_profile": {
      "student_id": "stu_dev101",
      "level": "intermediate",
      "language": "en",
      "time_budget_min": 15
    }
  }'
```

#### Example Response (`201 Created`)
```json
{
  "plan_id": "plan_998877",
  "title": "Calculus Limits and Continuity",
  "target_duration_sec": 900,
  "level": "intermediate",
  "language": "en",
  "modules": [
    {
      "segment_id": "seg_1",
      "order": 1,
      "segment_type": "avatar_intro",
      "title": "Welcome & Motivation",
      "duration_sec": 20,
      "script": "Hello! Today we are exploring the foundational concept of limits in calculus.",
      "visual_spec": {
        "visual_type": "general_slide",
        "subject_domain": "Mathematics",
        "headline": "Limits & Continuity",
        "bullet_points": ["Intuitive approach", "One-sided limits", "Formal definition"]
      }
    },
    {
      "segment_id": "seg_2",
      "order": 2,
      "segment_type": "visual_concept",
      "title": "One-Sided Limits",
      "duration_sec": 45,
      "script": "A limit exists if and only if both left and right hand limits approach the same value.",
      "visual_spec": {
        "visual_type": "math_equation",
        "subject_domain": "Mathematics",
        "headline": "Left vs Right Hand Limits",
        "latex_equations": ["\\lim_{x \\to c^-} f(x) = L", "\\lim_{x \\to c^+} f(x) = L"]
      },
      "checkpoint_question": {
        "question_id": "chk_q1",
        "question_text": "What is required for a two-sided limit to exist at x = c?",
        "question_type": "multiple_choice",
        "options": ["Left and right limits must be equal", "f(c) must be defined", "Limit must be infinity"],
        "correct_answer": "Left and right limits must be equal"
      }
    }
  ]
}
```

---

### 4.2 Get Saved Lesson Plan (`GET /api/v1/lessons/{plan_id}`)
Fetches a previously synthesized lesson plan by ID.

- **Path Parameter**: `plan_id` (`string`, e.g. `plan_998877`)
- **Example Request (`curl`)**:
```bash
curl -X GET http://localhost:8000/api/v1/lessons/plan_998877
```

---

### 4.3 Update or Reorder Lesson Plan (`PUT /api/v1/lessons/{plan_id}`)
Enables learners and instructors to customize, reorder, or edit module scripts before video generation.

- **Content-Type**: `application/json`
- **Request Body**:
```json
{
  "title": "Customized Calculus Limits",
  "modules": [ ... ]
}
```

---

### 4.4 List All Lesson Plans (`GET /api/v1/lessons`)
Returns all synthesized lesson plans.

- **Example Request (`curl`)**:
```bash
curl -X GET http://localhost:8000/api/v1/lessons
```

---

## 5. Hybrid Video Generation & Streaming (`/api/v1/video`)

### 5.1 Trigger Asynchronous Video Generation (`POST /api/v1/video/generate`)
Queues multi-stage rendering of avatar clips, visual slide clips, and final FFmpeg concatenation.

- **Content-Type**: `application/json`
- **Request Body**:
```json
{
  "plan_id": "plan_998877",
  "voice_preference": "en-US-GuyNeural"
}
```

#### Example Request (`curl`)
```bash
curl -X POST http://localhost:8000/api/v1/video/generate \
  -H "Content-Type: application/json" \
  -d '{"plan_id": "plan_998877", "voice_preference": "en-US-GuyNeural"}'
```

#### Example Response (`202 Accepted`)
```json
{
  "task_id": "task_vid_88291a0b",
  "plan_id": "plan_998877",
  "status": "processing",
  "estimated_duration_sec": 12,
  "websocket_stream_url": "/ws/v1/lessons/video-progress/task_vid_88291a0b"
}
```

---

### 5.2 Poll Video Generation Status (`GET /api/v1/video/status/{task_id}`)
Polls the execution state, current stage, completion percentage, and output URLs.

- **Path Parameter**: `task_id` (`string`, e.g. `task_vid_88291a0b`)

#### Example Response (`200 OK`)
```json
{
  "task_id": "task_vid_88291a0b",
  "plan_id": "plan_998877",
  "lesson_id": "les_001",
  "status": "completed",
  "progress_percent": 100.0,
  "current_stage": "completed",
  "stages_completed": [
    "tts_audio_synthesis",
    "avatar_video_generation",
    "slide_visual_rendering",
    "ffmpeg_concatenation"
  ],
  "video_url": "/api/v1/video/stream/video_plan_998877",
  "manifest_url": "/api/v1/video/manifest/video_plan_998877"
}
```

---

### 5.3 Get Video Manifest (`GET /api/v1/video/manifest/{video_id}`)
Returns the chapter layout, continuous timeline, and pause checkpoint triggers for the interactive video player.

- **Path Parameter**: `video_id` (`string`, e.g. `video_plan_998877`)

#### Example Response (`200 OK`)
```json
{
  "video_id": "video_plan_998877",
  "plan_id": "plan_998877",
  "title": "Calculus Limits and Continuity",
  "total_duration_sec": 124.5,
  "video_url": "/api/v1/video/stream/video_plan_998877",
  "chapters": [
    {
      "chapter_id": "chap_1",
      "title": "Welcome & Motivation",
      "start_time_sec": 0.0,
      "end_time_sec": 20.0,
      "segment_type": "avatar_intro"
    },
    {
      "chapter_id": "chap_2",
      "title": "One-Sided Limits",
      "start_time_sec": 20.0,
      "end_time_sec": 65.0,
      "segment_type": "visual_concept"
    }
  ],
  "pause_checkpoints": [
    {
      "checkpoint_id": "chk_1",
      "timestamp_sec": 65.0,
      "concept": "One-Sided Limits",
      "question": {
        "question_id": "chk_q1",
        "question_text": "What is required for a two-sided limit to exist at x = c?",
        "question_type": "multiple_choice",
        "options": ["Left and right limits must be equal", "f(c) must be defined", "Limit must be infinity"],
        "correct_answer": "Left and right limits must be equal"
      }
    }
  ]
}
```

---

### 5.4 Stream Video with HTTP 206 Range (`GET /api/v1/video/stream/{video_id}`)
Streams the requested MP4 video file with support for HTTP 206 Partial Content byte ranges.

- **Path Parameter**: `video_id` (`string`, e.g. `video_plan_998877`)
- **Headers**: `Range: bytes=0-1048575` (Optional)

#### Example Request (`curl`)
```bash
curl -X GET "http://localhost:8000/api/v1/video/stream/video_plan_998877" \
  -H "Range: bytes=0-1000000" \
  --output partial_video.mp4
```

---

## 6. Interactive Teaching Loop (`/api/v1/interactive`)

### 6.1 Evaluate Checkpoint Answer (`POST /api/v1/interactive/evaluate`)
Evaluates a student's answer during a video pause, diagnoses misconceptions, and generates scaffolded analogies.

- **Content-Type**: `application/json`
- **Request Body**:
```json
{
  "session_id": "sess_calc_101",
  "question_id": "chk_q1",
  "student_answer": "The function must be continuous everywhere for the limit to exist.",
  "concept": "One-Sided Limits",
  "context": "Calculus limit definitions"
}
```

#### Example Response (`200 OK`)
```json
{
  "is_correct": false,
  "score": 0.35,
  "feedback": "Not quite! You are confusing continuity with the existence of a limit.",
  "misconception": "Confusing continuity with limit existence",
  "re_explanation": "Think of two friends walking along two paths towards a cafe. The limit exists if they both arrive at the same spot, even if the cafe door is locked (f(c) is undefined).",
  "follow_up_question": {
    "question_id": "fol_q1",
    "question_text": "If f(2) is undefined, can the limit as x approaches 2 still exist?",
    "question_type": "short_answer",
    "correct_answer": "Yes"
  },
  "can_proceed": false
}
```

---

### 6.2 Side-Panel AI Tutor Chat (`POST /api/v1/interactive/chat`)
Provides real-time RAG-grounded answers for unscripted student questions during video viewing.

- **Content-Type**: `application/json`
- **Request Body**:
```json
{
  "session_id": "sess_calc_101",
  "message": "Why do we use epsilon and delta instead of just small numbers?",
  "current_concept": "Formal Limit Definition"
}
```

#### Example Response (`200 OK`)
```json
{
  "reply": "Epsilon and delta give us mathematical rigor! They prove that no matter how arbitrarily small a distance (epsilon) you choose on the y-axis, we can always find a corresponding interval (delta) on the x-axis that keeps the function within that target.",
  "grounded_sources": ["calculus_limits.pdf (Page 1)"],
  "suggested_follow_ups": [
    "Show an example proof using epsilon = 0.01",
    "What is the difference between limit and asymptote?"
  ]
}
```

---

### 6.3 Mid-Session Language Switch (`POST /api/v1/interactive/switch-language`)
Switches instruction language on the fly (e.g. English to Hindi) while retaining session history and misconception logs.

- **Content-Type**: `application/json`
- **Request Body**:
```json
{
  "session_id": "sess_calc_101",
  "target_language": "hi",
  "current_concept_id": "One-Sided Limits"
}
```

#### Example Response (`200 OK`)
```json
{
  "language": "hi",
  "translated_summary": "अब हम सीमा (Limits) की अवधारणा को हिंदी में समझेंगे। यदि बायीं सीमा (Left-Hand Limit) और दायीं सीमा (Right-Hand Limit) समान हैं, तो सीमा मौजूद होती है।",
  "next_prompt": "क्या आप सीमा और सांतत्य (Continuity) के अंतर पर एक उदाहरण देखना चाहते हैं?"
}
```

---

### 6.4 Get Interaction Session State (`GET /api/v1/interactive/session/{session_id}`)
Retrieves interaction history and active misconception status for a session.

- **Path Parameter**: `session_id` (`string`, e.g. `sess_calc_101`)

---

## 7. Assessment & Quizzes (`/api/v1/assessment`)

### 7.1 Generate Post-Lesson Quiz (`POST /api/v1/assessment/generate`)
Dynamically synthesizes a diagnostic quiz covering concepts taught in the lesson.

- **Content-Type**: `application/json`
- **Request Body**:
```json
{
  "lesson_id": "plan_998877",
  "num_questions": 4,
  "level": "intermediate",
  "language": "en"
}
```

#### Example Response (`200 OK`)
```json
{
  "quiz_id": "quiz_554433",
  "lesson_id": "plan_998877",
  "title": "Limits & Continuity Diagnostic Quiz",
  "questions": [
    {
      "question_id": "qz_1",
      "concept": "One-Sided Limits",
      "question_text": "Evaluate the limit of f(x) = (x^2 - 4)/(x - 2) as x approaches 2.",
      "question_type": "multiple_choice",
      "options": ["0", "2", "4", "Undefined"],
      "correct_answer": "4"
    }
  ]
}
```

---

### 7.2 Submit Quiz for Rubric Grading (`POST /api/v1/assessment/submit`)
Grades submitted quiz answers against rubrics and produces a diagnostic learning report.

- **Content-Type**: `application/json`
- **Request Body**:
```json
{
  "quiz_id": "quiz_554433",
  "student_id": "stu_dev101",
  "answers": {
    "qz_1": "4",
    "qz_2": "Left limit equals right limit"
  }
}
```

#### Example Response (`200 OK`)
```json
{
  "report_id": "rep_991122",
  "student_id": "stu_dev101",
  "quiz_id": "quiz_554433",
  "score_percent": 100.0,
  "total_questions": 2,
  "strong_concepts": ["Algebraic Limit Evaluation", "One-Sided Limits"],
  "weak_concepts": [],
  "misconceptions_identified": [],
  "recommended_revision": ["Review Derivative Difference Quotients"],
  "suggested_next_topics": ["Derivatives from First Principles", "L'Hopital's Rule"]
}
```

---

### 7.3 Get Learning Report (`GET /api/v1/assessment/report/{submission_id}`)
Retrieves a previously generated learning report by ID.

- **Path Parameter**: `submission_id` (`string`, e.g. `rep_991122`)

---

## 8. Learner Profile & Recommendations (`/api/v1/profile`)

### 8.1 Get Student Profile (`GET /api/v1/profile/{student_id}`)
Retrieves persistent learning profile, mastery statistics, and weak areas.

- **Path Parameter**: `student_id` (`string`, e.g. `stu_dev101`)

#### Example Response (`200 OK`)
```json
{
  "student_id": "stu_dev101",
  "preferred_level": "intermediate",
  "preferred_language": "en",
  "completed_lessons": ["plan_998877"],
  "concept_mastery": {
    "Calculus Limits": 0.95,
    "One-Sided Limits": 1.0
  },
  "weak_areas": [],
  "total_time_spent_min": 15
}
```

---

### 8.2 Update Student Profile (`PUT /api/v1/profile/{student_id}`)
Updates learner preferences, level, and language.

- **Path Parameter**: `student_id` (`string`)
- **Content-Type**: `application/json`
- **Request Body**:
```json
{
  "preferred_level": "advanced",
  "preferred_language": "hi",
  "learning_goal": "Prepare for Advanced Placement Exams"
}
```

---

### 8.3 Get Adaptive Topic Recommendations (`GET /api/v1/profile/{student_id}/recommendations`)
Synthesizes personalized next-step study suggestions.

- **Path Parameter**: `student_id` (`string`)

#### Example Response (`200 OK`)
```json
[
  {
    "topic_id": "rec_01",
    "title": "Derivatives and Tangent Lines",
    "domain": "Mathematics",
    "difficulty": "intermediate",
    "reason": "Natural prerequisite continuation following mastery of limits.",
    "estimated_time_min": 20
  }
]
```

---

## 9. System Health & Diagnostics

### 9.1 System Health Check (`GET /api/v1/health`)
Returns real-time system status, LLM provider, vector index counts, and storage readiness.

#### Example Request (`curl`)
```bash
curl -X GET http://localhost:8000/api/v1/health
```

#### Example Response (`200 OK`)
```json
{
  "status": "healthy",
  "app_name": "ApniHelp Core Platform",
  "version": "1.0.0",
  "llm_provider": "offline_parametric",
  "tts_provider": "edge-tts",
  "avatar_engine": "viseme_2_5d",
  "ffmpeg_available": true,
  "indexed_documents_count": 4,
  "vector_store_active_indices": 4,
  "total_lesson_plans": 6,
  "total_video_manifests": 3,
  "timestamp": "2026-09-01T12:00:00Z"
}
```

---

### 9.2 API Root Discovery (`GET /`)
Root greeting and documentation discovery endpoint.

#### Example Response (`200 OK`)
```json
{
  "message": "Welcome to ApniHelp Core Server",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/api/v1/health"
}
```

---

## 10. Navigation & Related Documentation

| Document | Description |
|---|---|
| [System Architecture](architecture.md) | 5-tier architecture, pedagogical state machines, and ADRs |
| [Setup & Deployment Guide](setup_and_deployment.md) | Docker Compose, `./run.sh`, and local setup instructions |
| [User Guide & Demo Video Walkthrough](user_guide.md) | End-to-end user journey and demo video generation |
| [Multilingual Support Guide](multilingual_support.md) | English/Hindi neural voice mappings and Devanagari rendering |
| [Project Overview (README.md)](../README.md) | High-level project summary, features, and quickstart |
