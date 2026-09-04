# Dispatch: explorer_r3_branding_e2e

## Objective
Investigate project naming/branding and test infrastructure to satisfy:
- **R5. Project naming**: All branding, repository names, and displayed titles shall use the name 'ApniHelp'.
- Acceptance Criteria & E2E verification across R1, R2, R3, R4, R5.

## Working Directory
`/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_r3_branding_e2e`

## Scope & Tasks
1. Read `/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/ORIGINAL_REQUEST.md` (lines 81-120 specifically for the new ApniHelp requirements).
2. Scan the codebase for all occurrences of old project names (e.g. "AI Teacher", "AI-Teacher", "AI-InnovationHackathon", "Adaptive Educational Platform", etc.) across:
   - Frontend (`index.html`, `App.tsx`, `Header.tsx`, `package.json`, metadata, logos, titles)
   - Backend (`main.py`, FastAPI OpenAPI title, docs, config, logs)
   - Root documentation (`README.md`, `docs/*`, `docker-compose.yml`, `run.sh`, `package.json`)
   - Tests (`tests_e2e/*`, `backend/tests/*`)
3. Inspect `tests_e2e/test_runner.py` and existing test suites. Determine what tests exist and what new or updated test suites must be created to verify:
   - R1: Video generation speed benchmark test (asserting processing time ≤20s per minute of output for 5m and 10m scenarios)
   - R2: UI single 'Generate Video' button verification
   - R3: Light visual theme palette verification (white, yellow, gray, dark blue)
   - R4: Photorealistic AI teacher avatar image & sync verification
   - R5: Naming consistency verification (all branding, displayed titles, repo references are 'ApniHelp')
4. Write a comprehensive report in your working directory at `analysis.md` and a structured `handoff.md`.

## 2026-09-04T17:46:18Z
You are explorer_r3_branding_e2e, a specialized exploration agent.
Your working directory is: /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_r3_branding_e2e
Please read your assignment file: /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_r3_branding_e2e/DISPATCH.md
MANDATORY: Read /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/ORIGINAL_REQUEST.md before starting work. Do NOT summarize or filter it — read the authoritative user request directly, especially the ApniHelp requirements (lines 81-120).

Your investigation focus:
1. Project naming (R5): Scan the entire project (frontend, backend, docs, configs, scripts, tests) for all occurrences of old titles/names ("AI Teacher", "Adaptive Educational Platform", "AI-InnovationHackathon", etc.) and specify how all branding, repository names, and displayed titles will be updated to "ApniHelp".
2. E2E verification test suite: Investigate tests_e2e/ and backend/tests/ to design test suites verifying R1 (video speed <=20s/min for 5m & 10m), R2 (single 'Generate Video' button), R3 (light visual theme), R4 (photorealistic teacher avatar & sync), and R5 (ApniHelp naming across all visible components).

Deliver your findings in /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_r3_branding_e2e/analysis.md and write a structured handoff.md. Report back with send_message when done.

