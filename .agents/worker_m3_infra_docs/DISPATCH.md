# Dispatch: worker_m3_infra_docs

## Objective
Implement Milestone 3: Infrastructure, Packaging & Documentation Re-Branding (R5-Infra/Docs) for ApniHelp.

## Working Directory
`/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/worker_m3_infra_docs`

## Exclusively Owned Files
- `docker-compose.yml`
- `run.sh`
- `README.md`
- `docs/*` (all documentation files under `docs/`)
- Root `package.json` (if present)

## Inputs & Context
1. Read `/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/ORIGINAL_REQUEST.md` (lines 81-120).
2. Read the investigation report from `explorer_r3_branding_e2e`:
   - `/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_r3_branding_e2e/analysis.md`
   - `/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_r3_branding_e2e/handoff.md`

## Specific Instructions
1. **Docker Compose & Launch Scripts**:
   - In `docker-compose.yml`: Update container names from `ai_teacher_backend` and `ai_teacher_frontend` to `apnihelp_backend` and `apnihelp_frontend`.
   - In `run.sh`: Update all echo banners, headers, and comments from "AI Teacher" to "ApniHelp".
2. **Project Documentation**:
   - In `README.md`: Update main titles, architecture headers, badges, feature descriptions, and demo instructions to "ApniHelp".
   - In `docs/architecture.md`, `docs/api_specification.md`, `docs/setup_and_deployment.md`, `docs/user_guide.md`, `docs/multilingual_support.md`: Update all titles, descriptions, and sample requests to reflect ApniHelp.
3. **Verification**:
   - Check that `docker-compose.yml` syntax is valid (`docker-compose config` or python yaml check).
   - Verify `run.sh` syntax with `bash -n run.sh`.
   - Check documentation links and search for any residual "AI Teacher" occurrences in the owned files.

## MANDATORY INTEGRITY WARNING
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Deliver your results in `handoff.md` and report back with `send_message`.

## 2026-09-04T17:57:42Z
You are worker_m3_infra_docs, a specialized implementation worker.
Your working directory is: /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/worker_m3_infra_docs
Please read your assignment file: /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/worker_m3_infra_docs/DISPATCH.md
MANDATORY: Read /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/ORIGINAL_REQUEST.md before starting work. Do NOT summarize or filter it — read lines 81-120 directly.

Your mission:
Implement Milestone 3 (Infrastructure, Packaging & Documentation Re-Branding).
- Update docker-compose.yml container names to apnihelp_backend and apnihelp_frontend.
- Update run.sh script banners, echoes, and comments to ApniHelp.
- Update README.md and all docs/* (architecture, api_specification, setup_and_deployment, user_guide, multilingual_support) to ApniHelp.
- Verify syntax of docker-compose.yml and run.sh, and ensure zero dead links.
- Write a thorough handoff.md in your working directory.
