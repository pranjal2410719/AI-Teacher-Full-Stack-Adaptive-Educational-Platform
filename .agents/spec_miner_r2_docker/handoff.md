# Specification & Environment Handoff Report: Docker, Compose & Run Script

**Agent:** `spec_miner_r2_docker`  
**Date:** 2026-09-01  
**Milestone:** Docker & Environment Investigation  
**Working Directory:** `/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/spec_miner_r2_docker`

---

## 1. Observation

1. **`backend/Dockerfile` Inspection**:
   - `backend/Dockerfile` line 6: `RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*`
   - `backend/Dockerfile` line 12: `RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; else pip install --no-cache-dir fastapi uvicorn; fi`
   - `backend/Dockerfile` line 16: `CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]`
   - File search across repository confirmed **NO `requirements.txt` file exists** in `backend/` or root (`find_by_name` returned 0 results).
   - Python AST parse across `backend/` identified imports of 17 distinct packages: `fastapi`, `uvicorn`, `pydantic`, `python-multipart`, `pypdf`, `docx` (`python-docx`), `pptx` (`python-pptx`), `PIL` (`Pillow`), `matplotlib`, `pygments`, `edge_tts`, `gtts`, `httpx`, `dotenv` (`python-dotenv`), `numpy`, `pytest`, `pytest-asyncio`.

2. **`frontend/Dockerfile` & `package.json` Inspection**:
   - `frontend/Dockerfile` line 17: `RUN npm run build`
   - `frontend/Dockerfile` line 23: `CMD ["npm", "run", "start"]`
   - `frontend/package.json` lines 6-10:
     ```json
     "scripts": {
       "dev": "vite --port 3000 --host",
       "build": "tsc && vite build",
       "preview": "vite preview --port 3000 --host"
     }
     ```
   - Notice: `"start"` script does **not exist** in `frontend/package.json`. Running `npm run start` inside the container causes `npm ERR! Missing script: "start"`.

3. **`docker-compose.yml` Inspection**:
   - Lines 15-16: `backend` has `depends_on: - vectorstore`
   - Lines 30-39: `vectorstore` service uses `image: milvusdb/milvus:2.4.0` with `ports: - "19530:19530"`
   - `backend/app/services/vector_store.py` lines 391-470 implements `NumpyVectorStore` with `BM25Ranker` in pure Python, writing indices to `data/indices`. Grep for `milvus` across `backend/` returned **0 results**.
   - Standalone Milvus 2.4 image fails to start without bundled etcd and MinIO/local storage configuration, blocking `backend` due to `depends_on`.

4. **`run.sh` Implementation**:
   - Lines 17-29: Creates directories and verifies Python/FFmpeg and frontend `node_modules`.
   - Lines 32-39: Starts `python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 &` and `(cd frontend && npm run dev) &`.
   - Lines 42-60: Implements signal trapping (`SIGINT`, `SIGTERM`, `EXIT`) and waits.
   - Does not contain CLI argument parsing for `--sample` or `--demo` mode to generate a $\ge 2$-minute video on a sample topic with interactive checkpoints as required by acceptance criteria.

5. **2-Minute Video Generation Architecture**:
   - `backend/app/services/planner_service.py` line 278: 5-minute budget scales to 2 core concepts + intro + summary + checkpoint $\approx 300\text{s}$ ($\ge 120\text{s}$).
   - `backend/app/services/video_stitcher.py` lines 149-369: Multi-stage pipeline generates TTS audio, 2.5D avatar clips, visual concept slides, stitches via FFmpeg into 1280x720 30fps faststart MP4, and generates `VideoManifest` with `CheckpointPauseMarker` pause checkpoints.

---

## 2. Logic Chain

1. **Docker Build Failure Trace**:
   - `backend/Dockerfile` line 12 checks `[ -f requirements.txt ]`.
   - Observation 1 proves `requirements.txt` is missing.
   - Therefore, Docker falls back to `pip install fastapi uvicorn`.
   - `backend/app/main.py` imports `pydantic`, `numpy`, `edge_tts`, etc.
   - When the container starts, Python raises `ModuleNotFoundError` for missing packages, causing container crash.

2. **Backend Module Import Trace in Docker**:
   - In `docker-compose.yml`, backend context is `./backend`.
   - `backend/Dockerfile` copies `./backend` into `/app`.
   - `/app` now has `app/`, `tests/`, etc., but no `backend` folder.
   - Backend source code imports from `backend.app...`.
   - When Uvicorn executes `uvicorn backend.app.main:app`, Python searches `sys.path` (`/app`) for a package named `backend` and fails with `ModuleNotFoundError: No module named 'backend'`.

3. **Frontend Docker Container Crash Trace**:
   - `frontend/Dockerfile` line 23 specifies `CMD ["npm", "run", "start"]`.
   - Observation 2 proves `frontend/package.json` contains only `dev`, `build`, and `preview`.
   - Therefore, container startup executes non-existent script and fails with exit code 1.

4. **Compose Blocker Trace**:
   - `docker-compose.yml` makes `backend` depend on `vectorstore`.
   - `vectorstore` uses `milvusdb/milvus:2.4.0`.
   - Observation 3 proves backend uses `NumpyVectorStore` and has zero references to Milvus.
   - The unconfigured Milvus container fails to boot, which prevents backend from starting.

5. **Acceptance Criteria Gap in `run.sh`**:
   - Acceptance criteria explicitly states: *"Running `./run.sh` (or Docker) on a sample topic generates a video $\ge 2$ minutes with interactive checkpoints."*
   - Observation 4 proves `run.sh` currently only starts long-running web servers and does not support headless sample generation.
   - Adding a `--sample` CLI mode ensures 100% compliance with this acceptance criterion.

---

## 3. Caveats

1. **Host Python Environment vs Docker**:
   - On the host machine, Python 3.14 was present without global fastapi installed, while `worker_m3_video` previously verified in-tree tests via a local virtual environment. Docker and `run.sh` should be fully self-sufficient with explicit venv and `requirements.txt`.
2. **Wav2Lip vs 2.5D Viseme Avatar**:
   - `AVATAR_ENGINE` defaults to `viseme_2_5d`, which requires zero heavyweight model downloads and runs fast on CPU. Pluggable Wav2Lip support is available if model checkpoints are placed in `models/wav2lip/`.

---

## 4. Conclusion

The core backend video pipeline and frontend interfaces are robust and capable of generating $\ge 2$-minute videos with interactive checkpoints. However, **five concrete configuration and environment blockers** must be resolved for 100% acceptance compliance:
1. Create `backend/requirements.txt` with all 15 required dependencies.
2. Update `backend/Dockerfile` to copy to `/app/backend` and set `ENV PYTHONPATH=/app`.
3. Update `frontend/Dockerfile` to use `npm run preview -- --host 0.0.0.0 --port 3000` or multi-stage Nginx.
4. Remove `vectorstore` (Milvus) and its dependency from `docker-compose.yml`, and add `.env` environment loading.
5. Update `run.sh` to include a `--sample` / `--demo` flag that generates a $\ge 2$-minute video on a sample topic with interactive checkpoints and verifies its duration and markers.

---

## 5. Verification Method

To independently verify these findings:

1. **Verify Missing `requirements.txt`**:
   ```bash
   ls -la /home/dev/Desktop/projects/AI-InnovationHackathon/backend/requirements.txt
   # Returns: No such file or directory
   ```

2. **Verify Frontend Script Absence**:
   ```bash
   grep '"start"' /home/dev/Desktop/projects/AI-InnovationHackathon/frontend/package.json
   # Returns: 0 matches
   ```

3. **Verify Pure Python Vector Store & No Milvus Dependency**:
   ```bash
   grep -rn "milvus" /home/dev/Desktop/projects/AI-InnovationHackathon/backend/
   # Returns: 0 matches
   ```

4. **Verify Sample Video Generation Logic in Python**:
   ```bash
   python3 -c "
   from backend.app.services.planner_service import planner_service
   blueprint = planner_service._calculate_blueprint(5)
   print('5m Blueprint Concept Sec:', blueprint['concept_sec'], 'Checkpoints:', blueprint['num_checkpoints'])
   "
   ```

5. **Full Investigation Report**:
   Inspect `/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/spec_miner_r2_docker/report.md` for the complete analysis.
