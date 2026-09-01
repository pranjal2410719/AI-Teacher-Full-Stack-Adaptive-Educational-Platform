# Original User Request

## 2026-08-31T19:12:07Z

Build a full-stack **AI Teacher** web application for the AI Innovation Hackathon 2026. The system ingests uploaded educational materials (PDF, DOCX, PPT, TXT, etc.) or accepts a free-text topic, then delivers personalized, adaptive, multilingual lessons through an AI-generated hybrid video experience — following a genuine human teaching loop: **Understand → Plan → Explain → Demonstrate → Question → Evaluate → Adapt → Continue**.

Working directory: /home/dev/Desktop/projects/AI-InnovationHackathon
Integrity mode: demo

### Stack Constraints (explicitly requested)
- **LLM**: Free-tier cloud APIs only — Groq free tier and/or Google AI Studio (Gemini) free tier. No paid APIs.
- **TTS / Voice**: gTTS or edge-tts (multilingual, open-source/free).
- **Talking Avatar**: Local open-source lip-sync model — SadTalker, Wav2Lip, or LatentSync (image + audio → talking head video).
- **Avatar format**: Hybrid — talking avatar for lesson intro and summary segments; rich AI-generated visual slides (diagrams, equations, code, timelines, images) for concept explanation segments.
- **Frontend**: React / Next.js.
- **Backend**: Python (FastAPI or similar).
- **Quality bar**: Hackathon demo quality — impressive, working prototype; minor rough edges acceptable.

---

## Requirements

### R1. Learning Material Ingestion & RAG
The system must accept uploaded educational files (PDF, DOCX, PPT/PPTX, TXT) and plain-text topic inputs. When material is uploaded, the system must parse and chunk it, embed it into a vector store, and use RAG to ground all lesson content in the uploaded source — minimizing hallucination. When no file is uploaded, the system generates lesson content from the LLM's parametric knowledge for the stated topic.

### R2. Personalized Lesson Planning
Before generating any video, the system must collect a learner profile: educational level (beginner / intermediate / advanced), preferred language, available time, and optionally prior knowledge or learning objective. From this profile and the source material, the system must generate a structured lesson plan — covering which concepts to teach, in what order, at what depth, with what examples and visuals — adapted to the time budget (e.g., 5 min → key concepts only; 60 min → full lesson with examples, questions, assessment).

### R3. AI Teaching Video Generation (Hybrid)
The system must produce a teaching video composed of:
- **Talking avatar segments**: A local lip-sync model (SadTalker / Wav2Lip / LatentSync) applied to a static avatar image + TTS audio, used for the lesson intro, concept transitions, and summary.
- **Visual explanation slides**: AI-generated subject-aware visuals rendered as video frames — e.g., equations + step-by-step solutions for math, labeled diagrams for biology, code blocks + execution flow for programming, timelines for history. These slides are narrated by TTS voice.
- Video segments are stitched together (e.g., via MoviePy or FFmpeg) into a single downloadable/streamable lesson video.
- The system must support multilingual TTS (at minimum English and Hindi) using gTTS or edge-tts, matching the learner's chosen language.

### R4. Interactive & Adaptive Teaching Loop
The system must not simply play a video and stop. During or after lesson segments, it must:
- Ask the student conceptual, MCQ, short-answer, or problem-solving questions at appropriate points.
- Evaluate the student's text response using the LLM.
- Detect incorrect answers and misconceptions, and generate a re-explanation (different analogy or example) rather than just marking wrong.
- Adapt the next lesson segment's difficulty and depth based on the student's performance so far.
- Maintain full lesson context across the interaction (language switches, follow-up questions, re-explanations).
- Support multilingual interaction: student can switch language mid-lesson (e.g., "explain this in Hindi") and the system must continue in the new language.

### R5. Assessment, Learning Profile & Next-Step Recommendation
After completing a lesson, the system must:
- Conduct a final quiz (mix of MCQ and short-answer).
- Generate a learning report: score, strong concepts, weak concepts, misconceptions identified, recommended revision, and suggested next topic.
- Persist a student learning profile (local storage or simple DB) containing topics studied, scores, weak areas, and learning history.
- Use the profile to personalize future sessions (e.g., skip already-mastered concepts, flag previously weak areas for reinforcement).

---

## Acceptance Criteria

### Document Ingestion & RAG
- [ ] Uploading a PDF/DOCX/PPT file results in a lesson grounded in that document's content, not fabricated facts.
- [ ] A question about uploaded material returns an answer sourced from the document (verifiable by checking against the file).
- [ ] Topic-only mode (no file) produces a structured lesson without errors.

### Lesson Planning & Personalization
- [ ] Selecting "beginner" vs "advanced" produces visibly different lesson depth and vocabulary.
- [ ] A 5-minute time budget produces a shorter, narrower lesson than a 60-minute budget on the same topic.
- [ ] The lesson plan (concept list, order, depth) is shown to the user before video generation begins.

### Video Generation
- [ ] The system produces a complete stitched video file for a lesson (no broken segments, no silent audio).
- [ ] The video contains at least one talking-avatar segment and at least one visual-slide segment.
- [ ] The TTS audio is intelligible and in the selected language (English and Hindi at minimum).
- [ ] Subject-aware visuals are used: math lessons include rendered equations; code lessons include syntax-highlighted code blocks; at least 2 different subject types are demonstrated.

### Interactive Teaching Loop
- [ ] The system pauses at least once during a lesson to ask the student a question.
- [ ] A deliberately wrong answer triggers a re-explanation, not just "incorrect."
- [ ] Switching language mid-session (e.g., typing "explain in Hindi") results in the next response in Hindi.
- [ ] After a wrong answer followed by re-explanation, the system asks a follow-up question to re-evaluate understanding.

### Assessment & Profile
- [ ] A final quiz is generated after lesson completion.
- [ ] A learning report is displayed with score, strong/weak concepts, and a next-topic recommendation.
- [ ] The student profile is saved and loaded correctly across sessions (revisiting the app shows past topics/scores).

### End-to-End Demo Flow
- [ ] The full journey works without errors: upload/topic → learner profile → lesson plan → video → interaction → assessment → report.
- [ ] The application runs locally with a single setup command (e.g., `docker-compose up` or documented `pip install` + `npm install` + run script).

---

*Expecting this to run as a full team build — a multi-component project (ingestion, planning, video pipeline, interactive loop, profile) that benefits from parallel work across components.*

---

## 2026-09-01T10:07:31Z

# Teamwork Project Prompt — Draft

> Status: Step 1 — Eliciting project idea
> Goal: Craft prompt → get user approval → delegate to teamwork_preview
> Requested team: [none — teamwork routes from the description]

[Project description — 1-2 sentences]

Working directory: [TBD]

## Requirements

### R1. [TBD]

### R2. [TBD]

## Acceptance Criteria

### [TBD]
- [ ] [TBD]

---
*Next: when approved → delegate via invoke_subagent (see Delegation Protocol)*

---

## 2026-09-01T10:12:52Z

# Teamwork Project Prompt — Draft

> Status: Step 1 — Eliciting project idea
> Goal: Craft prompt → get user approval → delegate to teamwork_preview
> Requested team: [none — teamwork routes from the description]

An AI Teacher platform that ingests educational materials or topics, creates personalized lesson plans, generates multilingual AI‑avatar video lessons, interacts with the student, and provides assessment and learning‑path recommendations.

Working directory: /home/dev/teamwork_projects/ai_teacher

## Requirements

### R1. Ingest uploaded material (PDF, DOCX, PPTX, TXT) or a user‑provided topic, and generate a structured lesson plan respecting learner level, available time, and selected language.

### R2. Produce a human‑like AI‑avatar video that includes synthesized speech, on‑screen text, diagrams, and pause points for interactive questions; support multiple languages via TTS.

### R3. Provide comprehensive, readable documentation covering project overview, architecture diagram, API specification, setup and deployment instructions, usage examples, and guidelines for generating demo videos. Documentation must be in Markdown, include a `README.md` and a `docs/` folder with separate sections, and be formatted for easy navigation (TOC, headings, code snippets).

## Acceptance Criteria

### Verification

- [ ] All unit and end‑to‑end tests pass inside the Docker environment.
- [ ] Backend and frontend Dockerfiles exist and `docker‑compose up` launches the full system without errors.
- [ ] Running `./run.sh` (or Docker) on a sample topic generates a video ≥2 minutes with interactive checkpoints.
- [ ] README includes clear setup, deployment, and demo‑video generation steps, and passes a spell‑check.
- [ ] `docs/` contains an architecture diagram (PNG/SVG) and API reference, and all internal links work.
- [ ] Multilingual video generation works for at least English and Hindi.

---
*Next: when approved → delegate via invoke_subagent (see Delegation Protocol)*

