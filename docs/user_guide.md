# User Guide & Demo Walkthrough

[![Build Status](https://img.shields.io/badge/Build-Passing-emerald.svg)](../README.md)
[![User Journey](https://img.shields.io/badge/User%20Journey-8--Phase%20Teaching%20Loop-purple.svg)](#the-8-phase-human-teaching-loop-walkthrough)
[![Demo Video](https://img.shields.io/badge/Demo%20Video-%E2%89%A52%20Min%20with%20Checkpoints-rose.svg)](#generating-demo-videos--hackathon-evaluations)
[![Multilingual](https://img.shields.io/badge/Languages-English%20%7C%20Hindi-blue.svg)](multilingual_support.md)

Welcome to the **ApniHelp User Guide**. This document provides an end-to-end walkthrough of the complete learning journey, from document ingestion to personalized video playback, interactive checkpoint resolution, diagnostic quiz grading, and long-term profile analytics. It also includes comprehensive instructions for generating and evaluating demo videos.

---

## Table of Contents

- [1. User Journey Overview](#1-user-journey-overview)
- [2. The 8-Phase Human Teaching Loop Walkthrough](#2-the-8-phase-human-teaching-loop-walkthrough)
  - [Step 1: Upload Materials or Enter Topic](#step-1-upload-materials-or-enter-topic)
  - [Step 2: Configure Learner Profile](#step-2-configure-learner-profile)
  - [Step 3: Review and Customize Lesson Plan](#step-3-review-and-customize-lesson-plan)
  - [Step 4: Watch the Hybrid Neural Video](#step-4-watch-the-hybrid-neural-video)
  - [Step 5: Solve In-Video Checkpoint Questions](#step-5-solve-in-video-checkpoint-questions)
  - [Step 6: Resolve Misconceptions with AI Scaffolding](#step-6-resolve-misconceptions-with-ai-scaffolding)
  - [Step 7: Ask Real-Time Side-Panel Tutor Questions](#step-7-ask-real-time-side-panel-tutor-questions)
  - [Step 8: Complete Quiz & Review Diagnostic Report](#step-8-complete-quiz-review-diagnostic-report)
- [3. Generating Demo Videos & Hackathon Evaluations](#3-generating-demo-videos-hackathon-evaluations)
  - [3.1 Generating Standalone Lesson Videos (>= 2 Minutes)](#31-generating-standalone-lesson-videos-2-minutes)
  - [3.2 Pre-Configured Subject Demo Scenarios](#32-pre-configured-subject-demo-scenarios)
  - [3.3 Inspecting Video Files and Manifests](#33-inspecting-video-files-and-manifests)
  - [3.4 Video Recording Guidelines for Presentation Pitches](#34-video-recording-guidelines-for-presentation-pitches)
- [4. Navigation & Related Documentation](#4-navigation-related-documentation)

---

## 1. User Journey Overview

The ApniHelp platform replaces traditional passive video watching with an active, adaptive learning experience structured around the 8-phase human teaching loop:

```
[Upload / Topic] ──► [Profile Setup] ──► [Plan Review] ──► [Hybrid Video] ──► [In-Video Checkpoint]
                                                                                      │
                                  [Learning Report] ◄── [Post Quiz] ◄── [Resume / Tutor Chat]
```

---

## 2. The 8-Phase Human Teaching Loop Walkthrough

### Step 1: Upload Materials or Enter Topic
1. Open the web interface at `http://localhost:3000`.
2. Choose your ingestion mode:
   - **Document Mode**: Drag and drop course files (`PDF`, `DOCX`, `PPTX`, `TXT`, `MD`). The system parses tables, headings, and equations, chunking the content and indexing it into the vector store.
   - **Topic Mode**: Enter any topic (e.g., *"Calculus Limits"*, *"Binary Search Trees"*, *"Cellular Biology"*, *"The Industrial Revolution"*). The system uses LLM parametric knowledge to synthesize an authoritative curriculum foundation.

---

### Step 2: Configure Learner Profile
Customize the lesson parameters to match your current needs:
- **Knowledge Level**:
  - `Beginner`: Focuses on fundamental definitions, intuitive visual analogies, and foundational terminology.
  - `Intermediate`: Covers formal mathematical proofs, algorithms, code traces, and practical application.
  - `Advanced`: Emphasizes rigorous edge cases, asymptotic complexity, and multi-step derivations.
- **Language Selection**:
  - `English` (Default voice: `en-US-GuyNeural`)
  - `Hindi` (Default voice: `hi-IN-MadhurNeural`)
- **Time Budget**:
  - `5–10 min`: Concise summary covering essential concepts and 1 checkpoint question.
  - `15–25 min`: Balanced standard lesson with worked demonstrations and 2 checkpoint questions.
  - `30–60 min`: Deep-dive masterclass with multiple worked examples, code traces, and 3–4 checkpoint questions.

---

### Step 3: Review and Customize Lesson Plan
Before generating video assets, the **Visual Lesson Plan Reviewer** presents an editable sequence of pedagogical cards:
1. **Inspect Module Sequence**: View avatar introductions, visual concept slides, worked demonstrations, checkpoint questions, and summary segments.
2. **Review Visual Slide Specs**: Inspect LaTeX equation formulas, syntax-highlighted code snippets, or anatomical diagrams associated with each module.
3. **Customize or Reorder**: Adjust module durations, rewrite narration scripts, or reorder chapters to suit your preferences.
4. **Approve & Synthesize**: Click **"Generate Lesson Video"** to begin multi-stage background rendering.

---

### Step 4: Watch the Hybrid Neural Video
The synthesized lesson plays inside the custom interactive HTML5 video player:
- **Avatar Segments (Intro & Summary)**: The ApniHelp avatar appears with audio-synchronized lip-sync visemes, natural eye blinking, subtle breathing bobbing, and a live studio HUD.
- **Visual Slide Segments (Core Theory)**: High-resolution slides display domain-specific visuals (typeset LaTeX formulas, syntax-highlighted IDE windows with complexity badges, cellular diagrams, or timelines) synchronized with neural voice narration.
- **Timeline & Chapter Navigation**: Click chapter markers on the scrub bar to jump between topics with instant HTTP 206 byte-range seeking.

---

### Step 5: Solve In-Video Checkpoint Questions
As the video reaches designated pedagogical pause timestamps, the player automatically halts playback and presents an interactive checkpoint overlay:
- **Question Formats**: Multiple-choice conceptual questions, code output predictions, or open-ended short-answer explanations.
- **Active Engagement**: The video remains paused until the student submits a response, guaranteeing that prerequisite concepts are grasped before moving to advanced material.

---

### Step 6: Resolve Misconceptions with AI Scaffolding
When an answer is submitted, the evaluation engine provides immediate cognitive feedback:
- **If Correct**: Positive reinforcement is provided, key principles are reinforced, and the video resumes automatically.
- **If Incorrect (Misconception Diagnosis)**:
  1. The system identifies the specific cognitive flaw (e.g., *Confusing a discontinuous function with an asymptote*).
  2. The **Misconception Drawer** provides a real-world analogy to rebuild conceptual intuition.
  3. A targeted follow-up question is presented to verify comprehension before resuming the video.

---

### Step 7: Ask Real-Time Side-Panel Tutor Questions
At any point during video playback, open the **Side-Panel AI Tutor Chat**:
- Ask unscripted questions (e.g., *"Why does the denominator approaching zero cause an undefined value?"*).
- All answers are grounded in the uploaded course material using hybrid RAG retrieval.
- **Mid-Session Language Switch**: Type *"Explain this in Hindi"*, and the AI Tutor immediately transitions explanations, summaries, and subsequent quiz questions into Hindi.

---

### Step 8: Complete Quiz & Review Diagnostic Report
Following video completion, click **"Take Diagnostic Quiz"**:
1. **Dynamic Quiz**: Answer a balanced mix of MCQs and short-answer questions targeting the exact concepts covered in the lesson.
2. **Rubric-Based Grading**: The system grades each response against comprehensive pedagogical rubrics.
3. **Diagnostic Learning Report**:
   - **Mastery Score Percentage**
   - **Strong Concepts**: Mastered areas ($\ge 80\%$).
   - **Weak Concepts**: Areas requiring reinforcement ($< 60\%$).
   - **Misconceptions Encountered**: Summary of diagnostic findings.
   - **Recommended Next Topics**: Personalized study roadmap for subsequent sessions.
4. **Persistent Profile**: The student profile saves automatically to SQLite/JSON, tracking cumulative progress across visits.

---

## 3. Generating Demo Videos & Hackathon Evaluations

The platform includes built-in scripts to generate full-length ($\ge 2$ minutes) stitched MP4 lesson videos with embedded pause checkpoints for presentations and hackathon evaluation.

### 3.1 Generating Standalone Lesson Videos (>= 2 Minutes)
Run the automated video stitcher test script:
```bash
python3 test_scripts/test_stitcher.py
```
**Output Produced**:
- `test_scripts/complete_hybrid_lesson.mp4`: Complete stitched 720p 30fps MP4 video featuring talking avatar segments and subject-aware visual slides.
- `test_scripts/avatar_intro.mp4` & `avatar_outro.mp4`: Individual avatar video segments.
- `test_scripts/math_slide_segment.mp4` & `code_slide_segment.mp4`: Individual narrated slide segments.

---

### 3.2 Pre-Configured Subject Demo Scenarios

You can execute end-to-end persona journeys across 4 distinct subject domains using the E2E Tier 4 test harness:

```bash
# Run all 4 real-world persona scenarios
python3 tests_e2e/test_runner.py --tier 4
```

| Scenario | Subject | Language | Key Visual Features |
|---|---|---|---|
| **Scenario 1** | High School Math (Calculus Limits) | Hindi (`hi`) | Devanagari text, $\epsilon$-$\delta$ LaTeX equations, one-sided limit function curves, Hindi quiz grading. |
| **Scenario 2** | College Computer Science (BSTs) | English (`en`) | Pygments syntax-highlighted IDE window, $O(\log N)$ complexity watch, recursive traversal check. |
| **Scenario 3** | AP Biology (Cell Structure) | English (`en`) | Cellular membrane diagram with organelle callout pins, mitochondria ATP synthesis explanation. |
| **Scenario 4** | World History (Industrial Revolution) | English (`en`) | Horizontal chronological timeline, James Watt steam engine milestone card, AI tutor chat. |

---

### 3.3 Inspecting Video Files and Manifests

All generated video assets and playback manifests are stored in standard project directories:
- **Rendered MP4 Videos**: `data/rendered_videos/`
- **Video Manifest JSONs**: `data/rendered_videos/manifests/`
- **Audio Voice WAVs**: `data/rendered_videos/audio/`
- **Visual Slide Frames**: `data/rendered_videos/slides/`

---

### 3.4 Video Recording Guidelines for Presentation Pitches

When creating video pitches or demonstration screencasts:
1. **Show the Upload / Profile Step (0:00 – 0:30)**: Demonstrate uploading `calculus_limits.pdf` or entering `"Binary Search Trees"` and selecting the Intermediate level.
2. **Show the Visual Plan Editor (0:30 – 0:50)**: Highlight the modular cards, LaTeX formula preview, and duration budget.
3. **Show Hybrid Playback (0:50 – 1:30)**: Showcase the talking avatar teacher introducing the topic, followed by the seamless transition into the technical visual slide.
4. **Trigger Live In-Video Checkpoint (1:30 – 2:00)**: Show the video automatically pausing, enter a deliberately flawed answer, and demonstrate the AI diagnosing the misconception with a scaffolded analogy.
5. **Show Diagnostic Learning Report (2:00 – 2:30)**: Complete the post-quiz and display the mastery report with recommended next topics.

---

## 4. Navigation & Related Documentation

| Document | Description |
|---|---|
| [Project Overview (README.md)](../README.md) | High-level project summary, features, and quickstart |
| [System Architecture](architecture.md) | 5-tier architecture, pedagogical state machines, and ADRs |
| [API Specification](api_specification.md) | Comprehensive reference for all 25 REST endpoints |
| [Setup & Deployment Guide](setup_and_deployment.md) | Docker Compose, `./run.sh`, and local setup instructions |
| [Multilingual Support Guide](multilingual_support.md) | English/Hindi neural voice mappings and Devanagari rendering |
| [E2E Testing Readiness Declaration](../TEST_READY.md) | 56/56 test suite readiness verification report |
