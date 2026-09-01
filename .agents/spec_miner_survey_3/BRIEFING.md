# BRIEFING — 2026-09-01T00:44:50+05:30

## Mission
Extract complete, precise feature specifications, API contracts, E2E acceptance criteria mapping, and Full-Stack Frontend/Testing Architecture for AI Teacher web application.

## 🔒 My Identity
- Archetype: specification_miner
- Roles: Teamwork specialist, Specification Mining, API Design, Frontend/Test Architecture
- Working directory: /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/spec_miner_survey_3
- Original parent: fc5ec816-363d-4758-bedc-768c5eec30a9
- Milestone: Survey & Specification Mining

## 🔒 Key Constraints
- Free-tier cloud APIs only (Groq free tier / Google Gemini free tier)
- TTS: gTTS / edge-tts (multilingual, open-source/free)
- Talking Avatar: Local open-source lip-sync model (SadTalker / Wav2Lip / LatentSync or lightweight fallback)
- Frontend: React / Next.js
- Backend: Python FastAPI
- Hackathon demo quality: Impressive working prototype
- Multi-component project: R1 (Ingestion/RAG), R2 (Lesson Planning), R3 (Video Generation), R4 (Interactive Loop), R5 (Assessment/Profile)

## Current Parent
- Conversation ID: fc5ec816-363d-4758-bedc-768c5eec30a9
- Updated: 2026-09-01T00:44:50+05:30

## Task Summary
- **What to build**: Full specification mining report covering all features, edge cases, REST/WebSocket API endpoints, Next.js frontend UI layouts/components, and 4-tier E2E test suite.
- **Success criteria**: Exhaustive, production-ready specification document allowing parallel implementation of backend, frontend, video pipeline, and testing suites.
- **Interface contracts**: REST/WebSocket API schema definitions between Next.js frontend and FastAPI backend in handoff.md.
- **Code layout**: Frontend in `frontend/` (Next.js/React), Backend in `backend/` (FastAPI), Tests in `tests/`.

## Key Decisions Made
- Discovered and specified 20 core features across R1-R5 and mapped 20 edge cases with resilience fallbacks.
- Formulated REST and WebSocket API schemas including video manifest with timestamped pause markers.
- Designed Next.js modern component hierarchy with in-video interactive question overlays and re-explanation drawers.
- Architected 4-Tier E2E test suite with Tier 1 Feature, Tier 2 Boundary, Tier 3 Cross-Feature, and Tier 4 Real-World Scenario suites.

## Artifact Index
- `.agents/spec_miner_survey_3/handoff.md` — Complete specification mining & architecture report
- `.agents/spec_miner_survey_3/progress.md` — Progress tracker and heartbeat
- `.agents/spec_miner_survey_3/DISPATCH.md` — Dispatch record
