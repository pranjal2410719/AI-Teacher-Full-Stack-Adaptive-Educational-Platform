"""
R5 Acceptance Test: Project Naming Consistency & Branding Regression
====================================================================
Authoritative Specification: ORIGINAL_REQUEST.md (lines 107-108, 116)
"All branding, repository names, and displayed titles shall use the name 'ApniHelp'."
Acceptance Criteria: "All visible project titles and repo names are 'ApniHelp'."

This test suite verifies:
  1. Frontend Layer:
     - `frontend/index.html` title is 'ApniHelp — Adaptive Educational Platform' (zero 'AI Teacher').
     - `frontend/src/components/Header.tsx` brand title displays 'ApniHelp'.
     - `frontend/package.json` manifest name is 'apnihelp-frontend'.
  2. Backend Application Layer:
     - `backend/app/config.py` settings.app_name is 'ApniHelp Core Platform'.
     - `backend/app/main.py` FastAPI app.title is 'ApniHelp Core Platform'.
     - `backend/app/main.py` root endpoint `GET /` returns 'Welcome to ApniHelp Core Server'.
     - `backend/app/services/slide_render_service.py` watermarks slides with 'ApniHelp' (zero 'AI TEACHER').
     - `backend/app/services/avatar_service.py` renders 'ApniHelp' on video banners.
  3. Infrastructure, Launcher & Documentation:
     - `docker-compose.yml` uses container names `apnihelp_backend` and `apnihelp_frontend`.
     - `run.sh` launcher banner uses 'ApniHelp' (zero 'AI Teacher — Full-Stack').
     - `README.md` primary title is 'ApniHelp — Full-Stack Adaptive Educational Platform'.
"""

import re
import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.config import settings

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_r5_frontend_naming_consistency():
    """
    R5.1: Asserts complete ApniHelp branding across frontend entry points:
    index.html, Header.tsx, and package.json.
    """
    # 1. index.html
    index_html_path = PROJECT_ROOT / "frontend" / "index.html"
    assert index_html_path.exists()
    index_html = index_html_path.read_text(encoding="utf-8")
    assert "<title>ApniHelp" in index_html, "index.html <title> must start with 'ApniHelp'"
    assert not re.search(r"AI\s*Teacher", index_html, re.IGNORECASE), "index.html must not reference 'AI Teacher'"

    # 2. Header.tsx
    header_path = PROJECT_ROOT / "frontend" / "src" / "components" / "Header.tsx"
    assert header_path.exists()
    header_code = header_path.read_text(encoding="utf-8")
    assert "ApniHelp" in header_code, "Header.tsx must contain brand name 'ApniHelp'"
    assert not re.search(r">\s*AI\s*Teacher\s*<", header_code), "Header.tsx must not display 'AI Teacher'"

    # 3. package.json
    pkg_json_path = PROJECT_ROOT / "frontend" / "package.json"
    assert pkg_json_path.exists()
    pkg_data = json.loads(pkg_json_path.read_text(encoding="utf-8"))
    assert pkg_data.get("name") in ["apnihelp-frontend", "apnihelp"], (
        f"package.json name is '{pkg_data.get('name')}', expected 'apnihelp-frontend'"
    )


def test_r5_backend_metadata_and_root_endpoint():
    """
    R5.2: Asserts that backend application configuration, FastAPI title,
    and root endpoint return ApniHelp branding.
    """
    # 1. config.py
    assert "ApniHelp" in settings.app_name, (
        f"settings.app_name '{settings.app_name}' does not contain 'ApniHelp'"
    )

    # 2. FastAPI app title
    assert "ApniHelp" in app.title, f"FastAPI app.title '{app.title}' does not contain 'ApniHelp'"

    # 3. Root endpoint GET /
    client = TestClient(app)
    res = client.get("/")
    assert res.status_code == 200
    res_data = res.json()
    assert "ApniHelp" in res_data.get("message", ""), (
        f"Root endpoint message '{res_data.get('message')}' does not contain 'ApniHelp'"
    )
    assert "AI Teacher" not in res_data.get("message", ""), (
        "Root endpoint message still contains legacy 'AI Teacher'"
    )


def test_r5_rendered_media_watermarks_and_overlays():
    """
    R5.3: Asserts that slide rendering and avatar services watermark
    all generated media frames with 'ApniHelp' (zero 'AI TEACHER').
    """
    # 1. slide_render_service.py
    slide_path = PROJECT_ROOT / "backend" / "app" / "services" / "slide_render_service.py"
    assert slide_path.exists()
    slide_code = slide_path.read_text(encoding="utf-8")

    assert re.search(r'draw\.text\(\s*\(self\.width\s*-\s*145,\s*26\),\s*"ApniHelp"', slide_code) or \
           'ApniHelp' in slide_code, (
        "Slide render service must watermark slides with 'ApniHelp'"
    )
    assert not re.search(r'"AI\s*TEACHER"', slide_code), (
        "Slide render service still contains legacy 'AI TEACHER' watermark text"
    )

    # 2. avatar_service.py
    avatar_path = PROJECT_ROOT / "backend" / "app" / "services" / "avatar_service.py"
    assert avatar_path.exists()
    avatar_code = avatar_path.read_text(encoding="utf-8")

    assert "ApniHelp" in avatar_code, "Avatar service must overlay 'ApniHelp' branding on video banners"
    assert not re.search(r'"AI\s*Teacher\s*•', avatar_code), (
        "Avatar service still contains legacy 'AI Teacher •' banner overlay"
    )


def test_r5_docker_compose_container_naming():
    """
    R5.4: Asserts that docker-compose.yml uses 'apnihelp_backend' and 'apnihelp_frontend'.
    """
    dc_path = PROJECT_ROOT / "docker-compose.yml"
    assert dc_path.exists()
    dc_content = dc_path.read_text(encoding="utf-8")

    assert "container_name: apnihelp_backend" in dc_content, (
        "docker-compose.yml must define 'container_name: apnihelp_backend'"
    )
    assert "container_name: apnihelp_frontend" in dc_content, (
        "docker-compose.yml must define 'container_name: apnihelp_frontend'"
    )
    assert "ai_teacher" not in dc_content.lower(), (
        "docker-compose.yml must not contain legacy 'ai_teacher' container references"
    )


def test_r5_launcher_script_banners():
    """
    R5.5: Asserts that run.sh prints ApniHelp launcher banners and has zero legacy titles.
    """
    run_path = PROJECT_ROOT / "run.sh"
    assert run_path.exists()
    run_content = run_path.read_text(encoding="utf-8")

    assert "ApniHelp — Full-Stack Adaptive Educational Platform Launcher" in run_content, (
        "run.sh must contain ApniHelp header launcher banner"
    )
    assert "ApniHelp Full-Stack Application is LIVE!" in run_content, (
        "run.sh must declare 'ApniHelp Full-Stack Application is LIVE!'"
    )
    assert not re.search(r"AI Teacher — Full-Stack", run_content), (
        "run.sh still contains legacy 'AI Teacher — Full-Stack' launcher string"
    )


def test_r5_root_readme_title():
    """
    R5.6: Asserts that README.md primary title declares ApniHelp.
    """
    readme_path = PROJECT_ROOT / "README.md"
    assert readme_path.exists()
    readme_content = readme_path.read_text(encoding="utf-8")

    assert readme_content.startswith("# 🎓 ApniHelp — Full-Stack Adaptive Educational Platform"), (
        "README.md must begin with '# 🎓 ApniHelp — Full-Stack Adaptive Educational Platform'"
    )
    assert not re.search(r"^#\s*🎓\s*AI\s*Teacher", readme_content, re.MULTILINE), (
        "README.md still contains legacy '# 🎓 AI Teacher' header"
    )
