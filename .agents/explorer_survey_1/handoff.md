# Technical Survey & Architectural Feasibility Report
**Author:** `explorer_survey_1`  
**Date:** 2026-09-01  
**Scope:** R1 (Learning Material Ingestion & RAG), R2 (Personalized Lesson Planning), R4 (Interactive & Adaptive Teaching Loop), R5 (Assessment & Student Profile Engine) + Host Environment Analysis

---

## 1. Observation

### 1.1 Host Environment & Hardware Capabilities
Direct inspection of the host system yielded the following concrete specifications:
- **Operating System:** Linux x86_64 (Ubuntu 24.04 / 25.04 base).
- **CPU:** Intel(R) Core(TM) i5-8350U CPU @ 1.70GHz (4 physical cores, 8 virtual threads).
- **Memory (RAM):** 7.6 GiB total (3.6 GiB available, 4.0 GiB swap).
- **GPU:** **No GPU available** (`nvidia-smi` not found; CPU-only execution environment).
- **Python Version:** Python 3.14.4 (`/usr/bin/python3`). Managed environment with PEP 668 active.
- **Node & NPM:** Node.js `v22.23.1`, npm `10.9.8` (`/snap/bin/node`, `/snap/bin/npm`).
- **Media Tools:** FFmpeg `8.0.1-3ubuntu2` installed at `/usr/bin/ffmpeg`.
- **Pre-installed Python Packages:**
  - `fastapi` (0.139.0), `uvicorn` (0.51.0), `starlette` (1.3.1)
  - `pydantic` (2.13.4), `pydantic_core` (2.46.4)
  - `openai` (2.45.0) — direct client for Groq and OpenAI-compatible endpoints
  - `numpy` (2.3.5), `pandas` (2.3.3)
  - `pillow` (12.1.1), `Pygments` (2.19.2)
  - `httpx` (0.28.1), `requests` (2.32.5), `aiohttp` (3.14.1), `websockets` (16.1)
  - `jinja2` (3.1.6), `beautifulsoup4` (4.15.0), `pytest` (9.0.2), `python-dotenv` (1.2.2)

### 1.2 User Constraints & Objectives (ORIGINAL_REQUEST.md)
1. **LLM Engine:** Free-tier cloud APIs only — **Groq Free Tier** (`llama-3.3-70b-versatile`, `llama-3.1-8b-instant`, `mixtral-8x7b-32768`) and/or **Google AI Studio (Gemini) Free Tier** (`gemini-2.0-flash`, `gemini-1.5-flash`, `text-embedding-004`).
2. **Audio/TTS:** `edge-tts` or `gTTS` (free, multilingual, high quality for English & Hindi).
3. **Core Loop:** Human teaching paradigm: **Understand → Plan → Explain → Demonstrate → Question → Evaluate → Adapt → Continue**.
4. **Key Modules Under Survey:**
   - **R1:** Ingestion of PDF, DOCX, PPT/PPTX, TXT + Vector Store / RAG + Topic-only mode.
   - **R2:** Personalized Lesson Planning (level, language, duration budget, concept sequencing, visual suggestions).
   - **R4:** Interactive & Adaptive Teaching Loop (in-lesson pausing, student evaluation, misconception diagnosis, difficulty adjustment, multilingual mid-session switching).
   - **R5:** Assessment & Student Profile Engine (quiz generation, scoring report, persistent profile storing weak/strong concepts, cross-session personalization).

---

## 2. Logic Chain

### 2.1 R1: Learning Material Ingestion & RAG Architecture

#### Parser Selection & Benchmark
| Format | Recommended Library | Fallback / Alternative | Rationale & Compatibility |
|---|---|---|---|
| **PDF** | `pypdf` (or `pdfplumber`) | `pypdf2` | Pure Python, zero C++ bindings, ultra-fast text extraction per page, Python 3.14 compatible. |
| **DOCX** | `python-docx` | `mammoth` | Pure Python, parses paragraphs, heading hierarchy (`Heading 1`, `Heading 2`), tables into Markdown format. |
| **PPT/PPTX**| `python-pptx` | Raw text extraction | Pure Python, parses slide titles, text frames, shape hierarchies, and presenter speaker notes. |
| **TXT / MD**| Native Python I/O | `chardet` | Zero overhead, robust UTF-8/Latin-1/CP1252 automatic decoding. |
| **Topic Only**| Synthetic Grounding | LLM Parametric Knowledge | When no file is uploaded (`has_document: false`), generates a structured knowledge syllabus using the LLM's parametric knowledge. |

#### Document Chunking Strategy
- **Structure-Aware Sliding Chunking:**
  - Standard sliding window: 500 tokens (~2,000 characters) with 100-token overlap.
  - Structure awareness: For PPTX, slide boundaries form atomic chunk boundaries. For PDF/DOCX, section headers (`#`, `##`, `Heading`) delimit chunk partitions.
  - Chunk Metadata:
    ```python
    class DocumentChunk(BaseModel):
        chunk_id: str
        source_id: str
        source_filename: str
        page_or_slide: Optional[int]
        section_title: Optional[str]
        text: str
        token_count: int
    ```

#### Vector Store & Embedding Selection (CPU & Free Tier Optimization)
- **Why NOT Heavy ChromaDB/Local PyTorch on Host?**
  - Host has 8 vCPUs (Intel i5), 7.6GB RAM, and Python 3.14. Running heavy PyTorch sentence-transformer models locally occupies ~1-2GB RAM and adds 100-300ms CPU latency per query. ChromaDB has C-extension compilation and SQLite version quirks on newer Python builds.
- **Recommended Architecture: In-Memory / SQLite Numpy Cosine Store + Cloud/BM25 Hybrid**
  1. **Primary Embedding Provider:** Google Gemini API `text-embedding-004` (free tier, 768 dimensions) or Groq/OpenAI embedding endpoint. Fast, zero local memory load, returns dense embeddings via `httpx`.
  2. **Vector Index:** `NumpyVectorStore` — stores normalized embeddings as a 2D float32 numpy matrix (`(N, 768)`). Cosine similarity computation across 1,000 chunks takes `< 0.2ms` in pure numpy.
  3. **Zero-API Offline / Fallback Ranker:** Pure-Python BM25 / TF-IDF ranker. If API keys are missing or rate limits occur, lexical BM25 retrieval grounds the lesson with zero external API calls.
  4. **Persistence:** Saved alongside session data in `data/sessions/{session_id}/vector_index.json` or `.npz`.

#### Grounding & Hallucination Prevention
- When RAG is active, retrieved chunks (top-k, k=4) are injected into the LLM context with explicit citation tags: `[Source: Slide 3 / Page 2]`.
- System prompt instructs: *"You are an expert tutor strictly grounded in the provided reference material. Derive definitions and facts from the excerpts. For supplemental pedagogical analogies, clarify that they are illustrative."*

---

### 2.2 R2: Personalized Lesson Planning Architecture

#### Pedagogical Flow & Taxonomy
The lesson planner translates user constraints and document chunks into an actionable structured lesson plan.

```
+-----------------------------------------------------------------------------------+
|                              Learner Profile Input                                |
|  Level: (Beginner/Intermediate/Advanced) | Language: (en/hi/...) | Time: (5m..60m)|
|  Learning Objective | Prior Knowledge | Known Weaknesses (from Student Profile)  |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                             Lesson Planner Engine                                 |
|  1. Scope concepts based on Time Budget (5m = 2 concepts; 60m = 8 concepts)       |
|  2. Calibrate depth & vocabulary to Learner Level                                 |
|  3. Inject prerequisite refresher if weak concept detected in Profile             |
|  4. Generate sequence of Pedagogical Segments (Intro -> Explain -> Q&A -> Wrap)  |
|  5. Assign Visual Slide Specifications for each concept segment                   |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                             Structured Lesson Plan                                |
|  - Title, Summary, Estimated Duration                                             |
|  - Ordered Segments (Avatar Intro, Visual Slides, Checkpoint, Demonstration, Wrap)|
+-----------------------------------------------------------------------------------+
```

#### Time Budget & Depth Calibration
| Time Budget | Number of Concepts | Typical Structure | Interactive Checkpoints | Depth Profile |
|---|---|---|---|---|
| **5 minutes** (Micro-lesson) | 2 key concepts | 1 Intro Avatar (30s) + 2 Slide Explanations (3.5m) + 1 Avatar Wrap (1m) | 1 quick check | High-level intuition, 1 concrete example, key takeaway |
| **15 minutes** (Standard) | 3-4 concepts | Intro (1m) + 3 Concepts (9m) + 2 Demos (3m) + Summary (2m) | 2 checkpoints | Rigorous explanation, trade-offs, standard formulas/code |
| **30 minutes** (Deep dive) | 5-6 concepts | Intro (2m) + Concepts (18m) + Demos (6m) + Assessment (4m) | 3 checkpoints | Deep mechanics, edge cases, step-by-step derivations |
| **60 minutes** (Masterclass) | 7-8 concepts | Comprehensive syllabus with worked examples & full quiz | 4-5 checkpoints | Advanced theory, architectural nuances, end-to-end problems |

#### Concrete Pydantic Schemas for Lesson Planning
```python
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class LearnerLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class VisualType(str, Enum):
    MATH_EQUATION = "math_equation"
    CODE_SNIPPET = "code_snippet"
    DIAGRAM = "diagram"
    TIMELINE = "timeline"
    COMPARISON_TABLE = "comparison_table"
    KEY_TAKEAWAYS = "key_takeaways"

class VisualSpec(BaseModel):
    visual_type: VisualType
    subject_domain: str = Field(..., description="math, computer_science, biology, history, physics, general")
    headline: str
    bullet_points: List[str] = Field(default_factory=list)
    code_content: Optional[str] = None
    code_language: Optional[str] = None
    latex_equations: List[str] = Field(default_factory=list)
    diagram_mermaid: Optional[str] = None
    table_headers: Optional[List[str]] = None
    table_rows: Optional[List[List[str]]] = None

class SegmentType(str, Enum):
    AVATAR_INTRO = "avatar_intro"
    CONCEPT_EXPLAIN = "concept_explain"
    INTERACTIVE_CHECKPOINT = "interactive_checkpoint"
    DEMONSTRATION = "demonstration"
    AVATAR_SUMMARY = "avatar_summary"

class InteractiveQuestion(BaseModel):
    question_id: str
    question_type: str = Field("mcq", description="mcq | short_answer")
    prompt: str
    options: Optional[List[str]] = None
    correct_answer: str
    concept_tested: str
    misconception_distractors: Optional[Dict[str, str]] = None
    explanation: str

class LessonSegment(BaseModel):
    segment_id: str
    sequence_order: int
    segment_type: SegmentType
    title: str
    target_duration_seconds: int
    narration_script: str = Field(..., description="Text for TTS narration in selected language")
    visual_spec: Optional[VisualSpec] = None
    checkpoint_question: Optional[InteractiveQuestion] = None
    grounding_citations: List[str] = Field(default_factory=list)

class LessonPlan(BaseModel):
    lesson_id: str
    topic: str
    learner_level: LearnerLevel
    language: str
    total_estimated_seconds: int
    prerequisite_refreshers: List[str] = Field(default_factory=list)
    segments: List[LessonSegment]
```

---

### 2.3 R4: Interactive & Adaptive Teaching Loop Architecture

#### In-Lesson Interaction Lifecycle
When playback reaches an `interactive_checkpoint` segment:
1. **Pause & Prompt:** Frontend pauses video stream and renders the question card with options or text input.
2. **Student Submission:** Student submits text answer or selects MCQ option.
3. **LLM Evaluation & Misconception Diagnosis:**
   - Evaluates correctness (0.0 to 1.0).
   - Identifies cognitive misconception (e.g., "Assumes array indices start at 1 instead of 0").
   - Decides pedagogical next step:
     - **If Correct:** Affirmation + optional challenge booster + resume next segment.
     - **If Incorrect:** Generate re-explanation using an alternate metaphor + generate a follow-up verification question.
4. **Adaptive Difficulty Adjustment:**
   - Tracks session score. If consecutive errors occur, adjusts subsequent segment narration to include extra scaffolding.
5. **Multilingual Mid-Session Switching:**
   - If the student submits a query in Hindi or requests a language change (e.g., *"Can you explain in Hindi?"*), the engine detects the intent, updates `session.language = "hi"`, and delivers the re-explanation and upcoming segment scripts in Hindi.

#### Evaluation Schema & Prompts
```python
class PedagogicalAction(str, Enum):
    AFFIRM_AND_ADVANCE = "affirm_and_advance"
    RE_EXPLAIN_ANALOGY = "re_explain_analogy"
    SIMPLIFY_AND_RETRY = "simplify_and_retry"
    CHALLENGE_EXTENSION = "challenge_extension"

class EvaluationResult(BaseModel):
    is_correct: bool
    score: float = Field(..., ge=0.0, le=1.0)
    student_response: str
    diagnosed_misconception: Optional[str] = None
    pedagogical_action: PedagogicalAction
    feedback_message: str
    re_explanation_script: Optional[str] = None
    follow_up_question: Optional[InteractiveQuestion] = None
    language_switched_to: Optional[str] = None
```

---

### 2.4 R5: Assessment & Student Profile Engine Architecture

#### Final Quiz Generation
- Post-lesson assessment contains 3 to 6 questions dynamically balanced:
  - 60% standard concept mastery checks.
  - 40% targeted reinforcement on concepts where the student made errors during the interactive checkpoints.

#### Learning Report Schema
```python
class ConceptMasteryLevel(str, Enum):
    MASTERED = "mastered"
    COMPETENT = "competent"
    NEEDS_REVIEW = "needs_review"

class ConceptScore(BaseModel):
    concept_name: str
    mastery_level: ConceptMasteryLevel
    score_percentage: float
    notes: str

class LearningReport(BaseModel):
    report_id: str
    lesson_id: str
    student_id: str
    overall_score_percentage: float
    total_questions: int
    correct_count: int
    concept_breakdown: List[ConceptScore]
    strong_concepts: List[str]
    weak_concepts: List[str]
    identified_misconceptions: List[str]
    recommended_revision_points: List[str]
    suggested_next_topics: List[str]
    summary_markdown: str
```

#### Persistent Student Profile Engine
- **Storage:** SQLite (`data/student_profiles.db`) or JSON database (`data/profiles/{student_id}.json`).
- **Profile Schema:**
```python
class StudentProfile(BaseModel):
    student_id: str
    display_name: str
    preferred_language: str = "en"
    default_level: LearnerLevel = LearnerLevel.BEGINNER
    completed_lessons: List[str] = Field(default_factory=list)
    mastered_concepts: List[str] = Field(default_factory=list)
    weak_concepts: List[str] = Field(default_factory=list)
    concept_history: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="concept_name -> {last_score: float, times_tested: int, last_seen_date: str}"
    )
    total_learning_time_seconds: int = 0
```
- **Cross-Session Personalization Mechanism:**
  - When starting a new lesson, the planner queries `StudentProfile.weak_concepts`.
  - If a weak concept is relevant to the new topic, the planner inserts a 30-second prerequisite refresher into `LessonSegment 1 (Intro)`.
  - Mastered concepts receive concise reviews rather than basic introductions.

---

### 2.5 Component Boundaries & REST API Design

```
+-----------------------------------------------------------------------------------+
|                                FASTAPI BACKEND                                    |
|                                                                                   |
|  [Ingestion & RAG]       --> /api/ingest (Upload PDF/DOCX/PPT/TXT)                |
|                              /api/documents/{doc_id}/query                        |
|                                                                                   |
|  [Lesson Planner]        --> /api/lesson/plan (Generate structured plan)          |
|                              /api/lesson/{lesson_id} (Retrieve/Update plan)       |
|                                                                                   |
|  [Interactive Loop]      --> /api/session/evaluate (Evaluate answer & adapt)      |
|                              /api/session/switch-language                         |
|                                                                                   |
|  [Assessment & Profile]  --> /api/quiz/generate (Generate post-lesson quiz)       |
|                              /api/quiz/submit (Submit answers & generate report)  |
|                              /api/profile/{student_id} (Get/Update profile)       |
+-----------------------------------------------------------------------------------+
```

---

## 3. Caveats

1. **Host CPU Limitations & Python 3.14:**
   - The host is CPU-only with Python 3.14. Heavy ML packages with uncompiled wheels for Python 3.14 (like some PyTorch/Torchvision builds or native C++ vector DBs) must be avoided in favor of pure-Python alternatives (`pypdf`, `python-docx`, `python-pptx`, `numpy`, `openai`, `fastapi`, `pillow`).
2. **Free-Tier API Rate Limits:**
   - Groq Free Tier (e.g. 30 RPM / 6,000 TPM for Llama 3.3 70B, higher on 8B instant) and Google Gemini Free Tier (15 RPM) require built-in exponential backoff, retry mechanisms, and fallback model chains (e.g. try `llama-3.3-70b-versatile` -> fallback to `llama-3.1-8b-instant` or Gemini Flash).
3. **Multilingual Visual Rendering:**
   - When generating visual slides with Hindi / Devanagari text using Pillow, standard Latin TrueType fonts will render boxes (tofu). The visual renderer must reference a Devanagari-compatible font (e.g. Google Noto Sans Devanagari, Lohit, or FreeSans) or fall back to clear Unicode rendering.
4. **Network Access for Cloud LLM APIs:**
   - Groq and Gemini APIs require outbound HTTPS internet access (`https://api.groq.com`, `https://generativelanguage.googleapis.com`). Mock/stub engines should be provided so tests and offline demos pass reliably even without external network connectivity.

---

## 4. Conclusion

- **R1 (Ingestion & RAG):** Fully feasible with `pypdf`, `python-docx`, `python-pptx`, structure-aware chunking, and a lightweight `NumpyVectorStore` (with BM25 fallback). Zero heavy dependencies needed.
- **R2 (Lesson Planning):** Fully feasible using structured Pydantic schema validation over Groq (`llama-3.3-70b-versatile`) and Gemini Flash (`gemini-2.0-flash`). Implements pedagogical sequence with visual slide specifications.
- **R4 (Adaptive Loop):** Fully feasible via stateless REST evaluation endpoint with misconception diagnosis, dynamic difficulty adjustment, and real-time multilingual switching.
- **R5 (Assessment & Profile):** Fully feasible via dynamic quiz generation, LLM/deterministic grading, comprehensive learning report generation, and SQLite/JSON student profile persistence.

---

## 5. Verification Method

### 5.1 Independent Verification Plan
1. **Schema & Model Validation:**
   - Run Pydantic model validation tests across `LessonPlan`, `LessonSegment`, `EvaluationResult`, `LearningReport`, and `StudentProfile`.
2. **Document Ingestion Test:**
   - Test extraction against synthetic PDF, DOCX, PPTX, and TXT files, verifying that text, headings, and metadata are parsed correctly.
3. **Vector Store & Similarity Test:**
   - Verify `NumpyVectorStore` indexing, cosine similarity scoring, and top-k retrieval latency (< 1ms for 1,000 chunks).
4. **Interactive Teaching & Misconception Test:**
   - Feed sample incorrect student answers (e.g. math sign error, programming 0-index error) and verify that `diagnosed_misconception` and `re_explanation_script` are populated.
5. **Persistent Profile Cross-Session Test:**
   - Create student profile with weak concept -> verify planner injects refresher in subsequent lesson plan.

### 5.2 Verification Commands
```bash
# Verify Python environment & core packages
python3 -c "import numpy, pydantic, fastapi, openai, PIL; print('All core libraries verified successfully!')"

# Run project unit tests once built
pytest tests/ -v
```
