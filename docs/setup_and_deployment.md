# Setup and Deployment Guide

[![Build Status](https://img.shields.io/badge/Build-Passing-emerald.svg)](../README.md)
[![Docker Ready](https://img.shields.io/badge/Docker-Compose%20Ready-blue.svg)](#method-2-multi-container-docker-compose)
[![Python Version](https://img.shields.io/badge/Python-3.11%2B-yellow.svg)](https://www.python.org/)
[![Node Version](https://img.shields.io/badge/Node.js-18%2B-green.svg)](https://nodejs.org/)

This guide provides step-by-step instructions for launching, configuring, and deploying the **ApniHelp** platform across multiple environments: single-command development scripts, multi-container Docker Compose stacks, and manual local development.

---

## Table of Contents

- [1. System Prerequisites](#1-system-prerequisites)
- [2. Method 1: Single-Command Quickstart (`./run.sh`)](#2-method-1-single-command-quickstart-runsh)
- [3. Method 2: Multi-Container Docker Compose](#3-method-2-multi-container-docker-compose)
- [4. Method 3: Manual Local Development](#4-method-3-manual-local-development)
  - [Backend Setup (FastAPI)](#backend-setup-fastapi)
  - [Frontend Setup (React / Vite)](#frontend-setup-react-vite)
- [5. Environment Variables & Configuration](#5-environment-variables-configuration)
- [6. Health Verification & Smoke Testing](#6-health-verification-smoke-testing)
- [7. Automated E2E Test Suite Execution](#7-automated-e2e-test-suite-execution)
- [8. Troubleshooting & FAQ](#8-troubleshooting-faq)
- [9. Navigation & Related Documentation](#9-navigation-related-documentation)

---

## 1. System Prerequisites

Ensure your host machine satisfies the following minimum system requirements:

| Component | Minimum Version | Recommended | Notes |
|---|---|---|---|
| **Operating System** | Linux (Ubuntu 20.04+), macOS 12+, or Windows WSL2 | Ubuntu 22.04 LTS | Native Linux or WSL2 recommended for best FFmpeg performance. |
| **Python** | `3.10+` | `3.11+` | Core backend runtime. |
| **Node.js** | `18.0+` | `20.x LTS` | Frontend runtime with `npm` (v9+). |
| **FFmpeg** | `4.4+` | `5.1+` with `libx264` & `libmp3lame` | Required for 720p MP4 encoding and video concat. |
| **Docker** (Optional) | `20.10+` | `24.0+` with Docker Compose v2 | Required only for containerized deployment. |

### Installing Prerequisites (Ubuntu / Debian Linux)
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv ffmpeg git curl nodejs npm
```

---

## 2. Method 1: Single-Command Quickstart (`./run.sh`)

The fastest way to run the entire full-stack application on a developer workstation is using the unified launch script `run.sh`.

### Execution Steps
```bash
# 1. Clone or navigate to the repository root
cd /home/dev/Desktop/projects/AI-InnovationHackathon

# 2. Grant executable permissions
chmod +x run.sh

# 3. Launch the full stack
./run.sh
```

### What `run.sh` Does Automatically:
1. **Directory Structure Initialization**: Ensures all persistent data directories (`data/uploads`, `data/plans`, `data/rendered_videos`, `data/sessions`, `data/quizzes`, `data/reports`, `data/profiles`) exist.
2. **Runtime Verification**: Checks for `python3` and `ffmpeg` in system PATH.
3. **Frontend Dependency Management**: Automatically runs `npm install` inside `frontend/` if `node_modules` is not detected.
4. **FastAPI Core Server Launch**: Starts backend on `http://0.0.0.0:8000` in the background.
5. **Vite Frontend Dev Server Launch**: Starts React UI on `http://0.0.0.0:3000` in the background.
6. **Graceful Shutdown Trap**: Captures `Ctrl+C` (`SIGINT`/`SIGTERM`) and cleanly terminates both backend and frontend processes.

---

## 3. Method 2: Multi-Container Docker Compose

For completely isolated, reproducible container deployment, use Docker Compose.

```
+-------------------------------------------------------------------------------+
|                             DOCKER COMPOSE TOPOLOGY                           |
+-------------------------------------------------------------------------------+
|  • apnihelp_frontend    ──► Port 3000 (React / Vite Web UI)                  |
|  • apnihelp_backend     ──► Port 8000 (FastAPI Core Server + FFmpeg Runtime)  |
|  • apnihelp_vectorstore ──► Port 19530 (Milvus 2.4.0 Vector Database)       |
+-------------------------------------------------------------------------------+
```

### Execution Steps
```bash
# 1. Build and launch all containers
docker-compose up --build

# 2. Run in detached background mode (optional)
docker-compose up -d --build

# 3. View live container logs
docker-compose logs -f

# 4. Stop and remove containers
docker-compose down
```

### Container Services

| Service Name | Container Name | Port Mapping | Description |
|---|---|---|---|
| `backend` | `apnihelp_backend` | `8000:8000` | Python 3.11 FastAPI server with system FFmpeg and mounted `/app/data` volume. |
| `frontend` | `apnihelp_frontend` | `3000:3000` | Node 18 production runtime serving React UI. |
| `vectorstore` | `apnihelp_vectorstore` | `19530:19530` | Milvus 2.4.0 standalone vector database. |

---

## 4. Method 3: Manual Local Development

For developers actively modifying backend services or frontend components, manual execution allows independent live reloading.

### Backend Setup (FastAPI)
```bash
# 1. Create and activate a Python virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate

# 2. Install backend dependencies
pip install -r backend/requirements.txt

# 3. Create required data folders
mkdir -p data/uploads data/plans data/rendered_videos data/sessions data/quizzes data/reports data/profiles

# 4. Start FastAPI server with live hot-reloading
python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup (React / Vite)
```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install npm dependencies
npm install

# 3. Start Vite development server
npm run dev
```

---

## 5. Environment Variables & Configuration

The application is designed to operate out of the box with zero required environment variables (using offline parametric knowledge and local in-memory vector indexing). To connect free-tier cloud LLMs or customize runtime behavior, create a `.env` file in the project root:

```ini
# ==============================================================================
# ApniHelp Platform Configuration (.env)
# ==============================================================================

# Free-Tier LLM Cloud Providers (Optional)
GROQ_API_KEY="gsk_your_groq_free_tier_key_here"
GROQ_MODEL="llama-3-70b-versatile"

GEMINI_API_KEY="AIzaSy_your_gemini_api_key_here"
GEMINI_MODEL="gemini-1.5-flash"

# Server Host & Port
HOST="0.0.0.0"
PORT=8000

# Multilingual Neural TTS Default Voice Mappings
TTS_DEFAULT_VOICE_EN="en-US-GuyNeural"
TTS_DEFAULT_VOICE_HI="hi-IN-MadhurNeural"

# Talking Avatar Engine ("viseme_2_5d" or "wav2lip")
AVATAR_ENGINE="viseme_2_5d"

# Storage Directories
DATA_DIR="data"
UPLOAD_DIR="data/uploads"
PLAN_DIR="data/plans"
VIDEO_DIR="data/rendered_videos"
PROFILE_DIR="data/profiles"
```

---

## 6. Health Verification & Smoke Testing

After launching the application, verify that all core subsystems are active:

### 1. Probe Backend Health Endpoint
```bash
curl -s http://localhost:8000/api/v1/health | python3 -m json.tool
```
**Expected Output**:
```json
{
  "status": "healthy",
  "app_name": "ApniHelp Core Platform",
  "version": "1.0.0",
  "llm_provider": "offline_parametric",
  "tts_provider": "edge-tts",
  "avatar_engine": "viseme_2_5d",
  "ffmpeg_available": true,
  "indexed_documents_count": 0,
  "vector_store_active_indices": 0,
  "total_lesson_plans": 0,
  "total_video_manifests": 0,
  "timestamp": "2026-09-01T12:00:00Z"
}
```

### 2. Verify Frontend Accessibility
Open your browser and navigate to:
```
http://localhost:3000
```
Confirm that the ApniHelp web application interface loads with the Document Dropzone, Learner Profile Setup, and Topic Ingest forms.

### 3. Verify Interactive OpenAPI Documentation
Interactive Swagger UI documentation is available at:
```
http://localhost:8000/docs
```

---

## 7. Automated E2E Test Suite Execution

The repository includes a comprehensive 4-Tier Opaque-Box E2E Testing Suite covering all 5 core milestones (R1–R5).

```bash
# Run all 4 tiers (56 tests) with structured CLI summary
python3 tests_e2e/test_runner.py

# Run specific tiers
python3 tests_e2e/test_runner.py --tier 1  # Tier 1: Feature Coverage (30 tests)
python3 tests_e2e/test_runner.py --tier 2  # Tier 2: Boundary & Corner Cases (18 tests)
python3 tests_e2e/test_runner.py --tier 3  # Tier 3: Cross-Feature Combinations (4 tests)
python3 tests_e2e/test_runner.py --tier 4  # Tier 4: Real-World Scenarios (4 tests)

# Run with standard Pytest runner
pytest tests_e2e/ -v --tb=short
```

---

## 8. Troubleshooting & FAQ

### Issue 1: `ffmpeg: command not found`
- **Symptom**: Video generation fails or falls back to static placeholder.
- **Cause**: FFmpeg is not installed or not in system PATH.
- **Solution**: Install FFmpeg using your package manager:
  ```bash
  sudo apt-get install -y ffmpeg   # Ubuntu/Debian
  brew install ffmpeg              # macOS
  ```

### Issue 2: `Address already in use` (Port 8000 or 3000)
- **Symptom**: `run.sh` or `uvicorn` fails with `[Errno 98] Address already in use`.
- **Cause**: An orphan background process is holding port 8000 or 3000.
- **Solution**: Locate and terminate the orphan process:
  ```bash
  # Check PID on port 8000
  lsof -ti:8000 | xargs kill -9 2>/dev/null || true
  
  # Check PID on port 3000
  lsof -ti:3000 | xargs kill -9 2>/dev/null || true
  ```

### Issue 3: Edge-TTS Connection Timeout in Restricted Networks
- **Symptom**: `edge-tts` warns of WebSocket connection timeout.
- **Cause**: Outbound WebSocket connections to Microsoft Edge endpoints are blocked by firewall/proxy.
- **Solution**: The platform automatically handles this gracefully by cascading to Google Translate TTS (`gTTS`) and then to the local offline harmonic PCM audio synthesizer. No manual action is required.

### Issue 4: HTML5 Video Seeking Stalls
- **Symptom**: Fast-forwarding in the video player does not buffer smoothly.
- **Cause**: Video streaming server does not support HTTP 206 Partial Content byte ranges.
- **Solution**: Ensure video streaming is queried through `/api/v1/video/stream/{video_id}`, which natively parses `Range: bytes=start-end` headers and sends streaming chunk responses with `Content-Range`.

---

## 9. Navigation & Related Documentation

| Document | Description |
|---|---|
| [Project Overview (README.md)](../README.md) | High-level project summary, features, and quickstart |
| [System Architecture](architecture.md) | 5-tier architecture, pedagogical state machines, and ADRs |
| [API Specification](api_specification.md) | Comprehensive reference for all 25 REST endpoints |
| [User Guide & Demo Video Walkthrough](user_guide.md) | End-to-end user journey and demo video generation |
| [Multilingual Support Guide](multilingual_support.md) | English/Hindi neural voice mappings and Devanagari rendering |
| [E2E Testing Readiness Declaration](../TEST_READY.md) | 56/56 test suite readiness verification report |
