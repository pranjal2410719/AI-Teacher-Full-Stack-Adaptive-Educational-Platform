# AI Teacher: E2E Test Infrastructure & Test Suite Specification (`TEST_INFRA.md`)

## 1. Overview & Testing Philosophy

The **AI Teacher** platform delivers a personalized, adaptive, multilingual educational experience structured around the human pedagogical loop:
$$\text{Understand} \longrightarrow \text{Plan} \longrightarrow \text{Explain} \longrightarrow \text{Demonstrate} \longrightarrow \text{Question} \longrightarrow \text{Evaluate} \longrightarrow \text{Adapt} \longrightarrow \text{Continue}$$

To guarantee high pedagogical quality, API contract adherence, multimedia pipeline stability, and error resilience, this end-to-end (E2E) testing framework implements a rigorous **4-Tier Testing Methodology**:

```
+---------------------------------------------------------------------------------------------------------+
|                                    4-Tier E2E Testing Architecture                                      |
+---------------------------------------------------------------------------------------------------------+
|  Tier 1: Feature Coverage            >= 5 tests per core feature (R1 Ingestion, R2 Planning,            |
|                                      R3 Video Pipeline, R4 Interactive Loop, R5 Assessment/Profile)     |
+---------------------------------------------------------------------------------------------------------+
|  Tier 2: Boundary & Corner Cases     0-byte files, password-locked PDFs, extreme durations (1m vs 180m),|
|                                      blank answers, Unicode/Devanagari text, prompt injection defenses  |
+---------------------------------------------------------------------------------------------------------+
|  Tier 3: Cross-Feature Combinations  Pairwise & composite multi-service flows: Ingestion -> Plan ->     |
|                                      Video Manifest -> Pause Checkpoints -> Re-explanation -> Profile   |
+---------------------------------------------------------------------------------------------------------+
|  Tier 4: Real-World Scenarios        Complete end-to-end learner persona journeys:                      |
|                                      - High School Math in Hindi (Calculus Limits)                      |
|                                      - College CS in English (Binary Search Trees)                      |
|                                      - High School Biology (Cell Structure & Diagrams)                  |
|                                      - AP History (Industrial Revolution & Timelines)                   |
+---------------------------------------------------------------------------------------------------------+
```

---

## 2. Directory Layout

The test suite resides in `/home/dev/Desktop/projects/AI-InnovationHackathon/tests_e2e/`:

```
tests_e2e/
├── fixtures/
│   ├── calculus_limits.pdf             # Real PDF with math definitions, limit theorems, LaTeX formulas
│   ├── binary_search_trees.docx        # Real DOCX with BST operations, pseudo-code, complexity analysis
│   ├── cell_biology.pptx               # Real PPTX with organelle descriptions, diagrams, cell theory
│   ├── industrial_revolution.txt       # Real TXT with steam engine, urbanization, factory history
│   ├── empty_document.pdf              # 0-byte / empty file for boundary testing
│   ├── corrupted_format.docx           # Corrupted / invalid binary header
│   └── large_syllabus.txt              # Large text payload for chunking stress test
├── test_runner.py                      # Unified Python CLI & programmatic test runner
├── conftest.py                         # Pytest configuration, fixtures, and app test harness
├── harness.py                          # Dual-mode test adapter (FastAPI TestClient & Live REST/WS)
├── tier1_feature_coverage/
│   ├── test_ingestion_feature.py       # R1: PDF/DOCX/PPTX/TXT upload, topic parametric mode, chunking, RAG
│   ├── test_planning_feature.py        # R2: Profile capture, duration scaling, visual specs, plan review
│   ├── test_video_pipeline_feature.py  # R3: Multilingual TTS, avatar visemes, slide renderers, video stitcher
│   ├── test_interactive_loop_feature.py# R4: Checkpoint markers, evaluation, misconception diagnosis, chat
│   └── test_assessment_profile_feature.py # R5: Dynamic quiz, grading, learning report, student profile
├── tier2_boundary_corner/
│   ├── test_corrupt_and_empty_inputs.py# 0-byte, invalid MIME, corrupt headers, unsupported types
│   ├── test_duration_and_level_bounds.py# Extreme durations (1m vs 180m), invalid learner levels
│   ├── test_multilingual_unicode.py    # Devanagari (Hindi), Tamil, German, special symbols
│   └── test_resilience_and_injection.py# Prompt injection resilience, empty answers, missing fields
├── tier3_cross_feature/
│   ├── test_doc_to_video_manifest_flow.py # Document upload -> Adaptive plan -> Stitched video manifest
│   ├── test_interactive_misconception_cycle.py # Pause marker -> Wrong answer -> Analogy -> Follow-up -> Resume
│   ├── test_topic_to_quiz_profile_cycle.py # Topic input -> Code lesson -> Quiz submission -> Profile update
│   └── test_multilingual_switch_flow.py   # English lesson -> Mid-session Hindi switch -> Hindi tutor chat
└── tier4_real_world_scenarios/
    ├── test_scenario_math_hindi.py     # High School Calculus in Hindi (15 min, Beginner, Equations)
    ├── test_scenario_cs_bst.py         # College CS Data Structures in English (10 min, Intermediate, Code)
    ├── test_scenario_biology_cells.py  # Biology Organelles with Diagrams (20 min, Intermediate)
    └── test_scenario_history_timeline.py # Industrial Revolution with Timelines (15 min, Advanced)
```

---

## 3. Educational Fixture Catalog

The test suite includes authentic, domain-rich educational documents:

| Fixture File | Format | Subject Domain | Core Content & Key Phrases |
|--------------|--------|----------------|----------------------------|
| `calculus_limits.pdf` | PDF | Mathematics | Limits, $\epsilon$-$\delta$ formal definition, one-sided limits, continuity, derivative as limit of difference quotient. |
| `binary_search_trees.docx` | DOCX | Computer Science | BST property, `TreeNode` structure, recursive `insert`, `search`, in-order traversal, $O(\log n)$ vs $O(n)$ complexity. |
| `cell_biology.pptx` | PPTX | Biology | Plasma membrane, mitochondria (ATP synthesis), nucleus, endoplasmic reticulum, plant vs animal cell comparisons. |
| `industrial_revolution.txt` | TXT | History | 18th century Britain, James Watt steam engine, textile mechanization, urbanization, factory working conditions. |
| `empty_document.pdf` | PDF | Edge Case | 0-byte empty file for validation error handling. |
| `corrupted_format.docx` | DOCX | Edge Case | Invalid bytes for parser resilience testing. |
| `large_syllabus.txt` | TXT | Stress Test | Extended multi-chapter curriculum for vector indexing and chunking performance. |

---

## 4. Test Runner Specifications

The test runner `/home/dev/Desktop/projects/AI-InnovationHackathon/tests_e2e/test_runner.py` provides both a standalone CLI and standard `pytest` integration.

### CLI Usage

```bash
# Run all tiers with colored console output
python3 tests_e2e/test_runner.py

# Run specific tier
python3 tests_e2e/test_runner.py --tier 1
python3 tests_e2e/test_runner.py --tier 2
python3 tests_e2e/test_runner.py --tier 3
python3 tests_e2e/test_runner.py --tier 4

# Run against a live running backend server
python3 tests_e2e/test_runner.py --base-url http://localhost:8000

# Generate structured JSON test report
python3 tests_e2e/test_runner.py --json-report test_report.json

# Run via standard pytest
pytest tests_e2e/ -v --tb=short
```

### Reporting Format
The runner outputs:
1. Real-time test progress with pass/fail indicators `[PASS]` / `[FAIL]`.
2. Execution time per test and tier summary.
3. Structured JSON summary containing total tests, passed, failed, skipped, and duration.

---

## 5. Dual-Mode Test Harness (In-Process & Live Server)

The test harness `/home/dev/Desktop/projects/AI-InnovationHackathon/tests_e2e/harness.py` provides a unified interface:
1. **In-Process Mode (`FastAPI TestClient`)**: Directly invokes FastAPI ASGI routes and services in-memory without requiring a separate server process. Ideal for rapid CI/CD and deterministic test runs.
2. **Live Server Mode (`HTTP / WebSocket Client`)**: Sends live HTTP/REST requests to a running backend server (e.g. `http://localhost:8000`).

The harness automatically selects In-Process mode by default, or switches to Live Server mode when `--base-url` is specified or `LIVE_BACKEND_URL` is set in the environment.

---

## 6. Tier Verification Matrix

| Tier | Category | Minimum Tests | Key Verification Target |
|------|----------|---------------|-------------------------|
| **Tier 1** | Ingestion & RAG | $\ge 5$ | PDF/DOCX/PPTX parsing, chunk extraction, BM25/vector retrieval, topic parametric mode. |
| **Tier 1** | Lesson Planning | $\ge 5$ | Profile validation, duration scaling (5m vs 60m), visual slide specs, plan CRUD. |
| **Tier 1** | Video Pipeline | $\ge 5$ | Neural TTS (English/Hindi), avatar visemes, Math LaTeX / Code / Diagram slide rendering, FFmpeg stitcher. |
| **Tier 1** | Interactive Loop | $\ge 5$ | Checkpoint pause markers, LLM rubric evaluation, misconception diagnosis, analogies, follow-up questions. |
| **Tier 1** | Assessment & Profile | $\ge 5$ | Dynamic quiz generation, grading engine, strong/weak analytics, SQLite/JSON profile persistence. |
| **Tier 2** | Boundary & Corner | $\ge 8$ | 0-byte upload, corrupt binary, prompt injection defense, blank student answer, extreme durations, Devanagari encoding. |
| **Tier 3** | Cross-Feature Flows | $\ge 4$ | Multi-service pipelines: Upload-to-Manifest, Interactive Misconception Cycle, Topic-to-Profile Cycle, Multilingual Switch. |
| **Tier 4** | Real-World Personas | 4 | Math (Calculus in Hindi), CS (BST in English), Biology (Cells with Diagrams), History (Industrial Revolution). |

---

## 7. Pass Criteria
- **100% of tests must pass** across all 4 tiers.
- Zero unhandled exceptions or memory leaks.
- All JSON schema contracts conform strictly to `PROJECT.md § Interface Contracts`.
