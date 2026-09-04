#!/usr/bin/env bash
# ==============================================================================
# ApniHelp — Full-Stack Adaptive Educational Platform Launcher
# Supports:
#   1. Web Server Mode:  FastAPI Core Server (8000) & Frontend UI (3000)
#   2. Demo / Sample:    Automated >= 2-min hybrid video generation with checkpoints
#   3. Test Suite:       Runs full backend & E2E test suites
# ==============================================================================

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Set environment
export PYTHONPATH="$PROJECT_ROOT:${PYTHONPATH:-}"
export MPLCONFIGDIR="/tmp/matplotlib_cache"
mkdir -p "$MPLCONFIGDIR"

# Resolve Python runtime
if [ -f "$PROJECT_ROOT/.venv/bin/python" ]; then
    PYTHON="$PROJECT_ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON="python3"
else
    echo "❌ Error: Python 3 runtime not found."
    exit 1
fi

# Ensure storage directories
mkdir -p data/uploads data/plans data/rendered_videos data/sessions data/quizzes data/reports data/profiles data/videos/clips data/videos/manifests data/videos/tasks

# Command-Line Dispatcher
MODE="${1:-start}"

show_help() {
    echo "======================================================================"
    echo " 🎓 ApniHelp — Full-Stack Adaptive Educational Platform"
    echo "======================================================================"
    echo "Usage:"
    echo "  ./run.sh                     Start FastAPI server (8000) and Frontend (3000)"
    echo "  ./run.sh start               Start web servers in foreground"
    echo "  ./run.sh --demo [opts]       Run sample pipeline generating >= 2-min video"
    echo "  ./run.sh demo [opts]         Alias for --demo"
    echo "  ./run.sh --sample [opts]     Alias for --demo"
    echo "  ./run.sh --test              Execute full unit and E2E test suites"
    echo "  ./run.sh --help              Show this help message"
    echo ""
    echo "Demo Options:"
    echo "  --topic <calculus|biology|cs>   Subject domain (default: calculus)"
    echo "  --language <en|hi>              Language code (default: en)"
    echo "  --dual-lang                     Generate both English and Hindi sample videos"
    echo "======================================================================"
}

run_demo() {
    echo "======================================================================"
    echo " 🎬 Launching ApniHelp Demo Video Generator (>= 2 Minutes)"
    echo "======================================================================"
    if [ "$1" = "--demo" ] || [ "$1" = "demo" ] || [ "$1" = "--sample" ] || [ "$1" = "sample" ]; then
        shift
    fi
    "$PYTHON" -m backend.app.demo_generator "$@"
}

run_tests() {
    echo "======================================================================"
    echo " 🧪 Running ApniHelp Backend & E2E Test Suite"
    echo "======================================================================"
    echo "[1/2] Running Backend Pytest Suite..."
    "$PYTHON" -m pytest backend/tests/ -v
    echo ""
    echo "[2/2] Running 4-Tier E2E Test Suite..."
    "$PYTHON" tests_e2e/test_runner.py
    echo ""
    echo "✅ All tests passed successfully!"
}

run_servers() {
    echo "======================================================================"
    echo " 🎓 ApniHelp — Full-Stack Educational Platform"
    echo "======================================================================"

    # 1. Environment Verification
    echo "[1/3] Checking Python and FFmpeg runtimes..."
    "$PYTHON" --version
    ffmpeg -version >/dev/null 2>&1 || echo "Warning: ffmpeg not detected in PATH, video generation fallback enabled."

    # 2. Check Frontend dependencies & static build
    echo "[2/3] Verifying Frontend Environment..."
    if [ ! -d "frontend/node_modules" ] && command -v npm >/dev/null 2>&1; then
        echo "Installing frontend dependencies..."
        (cd frontend && npm install)
    fi

    # 3. Start Backend & Frontend
    echo "[3/3] Starting Services..."
    echo "Starting FastAPI Core Server on http://0.0.0.0:8000..."
    "$PYTHON" -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!

    FRONTEND_PID=""
    if command -v npm >/dev/null 2>&1; then
        echo "Starting Frontend Web Application on http://0.0.0.0:3000..."
        (cd frontend && npm run dev) &
        FRONTEND_PID=$!
    elif [ -d "frontend/dist" ]; then
        echo "Serving compiled frontend dist on http://0.0.0.0:3000..."
        "$PYTHON" -m http.server 3000 --directory frontend/dist &
        FRONTEND_PID=$!
    fi

    # Trap signals for clean termination
    cleanup() {
        echo ""
        echo "Shutting down ApniHelp Platform..."
        kill "$BACKEND_PID" 2>/dev/null || true
        [ -n "$FRONTEND_PID" ] && kill "$FRONTEND_PID" 2>/dev/null || true
        exit 0
    }
    trap cleanup SIGINT SIGTERM EXIT

    echo ""
    echo "======================================================================"
    echo " ✅ ApniHelp Full-Stack Application is LIVE!"
    echo " 👉 Web Application: http://localhost:3000"
    echo " 👉 Backend API Docs: http://localhost:8000/docs"
    echo " 👉 Health Endpoint: http://localhost:8000/api/v1/health"
    echo "======================================================================"
    echo "Press Ctrl+C to stop all servers."

    wait
}

case "$MODE" in
    --demo|demo|--sample|sample)
        run_demo "$@"
        ;;
    --test|test)
        run_tests
        ;;
    --help|-h|help)
        show_help
        ;;
    start|server|"")
        run_servers
        ;;
    *)
        # If unknown argument starts with --, pass to demo runner
        if [[ "$MODE" == --* ]]; then
            run_demo "$@"
        else
            show_help
            exit 1
        fi
        ;;
esac
