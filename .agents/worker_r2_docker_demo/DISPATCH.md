## 2026-09-01T10:23:45Z
You are worker_r2_docker_demo, an implementation and verification worker.
Your working directory is: /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/worker_r2_docker_demo
Workspace root: /home/dev/Desktop/projects/AI-InnovationHackathon

Read /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/ORIGINAL_REQUEST.md, /home/dev/Desktop/projects/AI-InnovationHackathon/PROJECT.md, and the findings in:
- /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/spec_miner_r2_docker/report.md
- /home/dev/Desktop/projects/AI-InnovationHackathon/.agents/explorer_r2_status/report.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Exclusive File Ownership:
- backend/requirements.txt
- backend/Dockerfile
- frontend/Dockerfile
- docker-compose.yml
- run.sh
- Any minor test fix in backend/tests/ (e.g. relaxing microsecond timing SLA in benchmark test)

Tasks:
1. Create `backend/requirements.txt` with all needed backend packages: `fastapi`, `uvicorn`, `pydantic`, `numpy`, `python-multipart`, `pypdf`, `python-docx`, `python-pptx`, `Pillow`, `matplotlib`, `pygments`, `edge-tts`, `gTTS`, `httpx`, `python-dotenv`, `pytest`, `pytest-asyncio`.
2. Update `backend/Dockerfile` ensuring `PYTHONPATH` and file structure allows `python3 -m uvicorn backend.app.main:app` or `uvicorn app.main:app` to run properly, with system dependencies including ffmpeg and fonts.
3. Update `frontend/Dockerfile` to build Vite app and serve via preview (`npm run preview -- --host 0.0.0.0 --port 3000`) or standard server.
4. Clean `docker-compose.yml` to remove any broken Milvus dependencies and cleanly expose backend on port 8000 and frontend on port 3000.
5. Enhance `run.sh` so that:
   - It can start the servers in the background or foreground.
   - It supports `./run.sh --demo` or `./run.sh demo` or sample generation mode that executes a full pipeline generating a complete video >= 2 minutes with interactive checkpoints on a sample educational topic (e.g. Calculus or Biology, in English and Hindi), printing the video path and duration.
6. If needed, adjust the microsecond timing SLA in backend benchmark test to prevent transient timing failures.
7. Run tests (`pytest backend/tests/ -v` and `python3 tests_e2e/test_runner.py`) and test running `./run.sh --demo` or sample generation to verify that a >= 2 min video is generated and all tests pass.
8. Document all changes and verification commands in `/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/worker_r2_docker_demo/changes.md` and write `handoff.md`.
9. Send a completion message back to parent using send_message.
