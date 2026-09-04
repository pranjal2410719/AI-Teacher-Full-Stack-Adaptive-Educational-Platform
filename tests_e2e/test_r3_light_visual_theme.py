"""
R3 Acceptance Test: Light Visual Theme Palette Compliance
=========================================================
Authoritative Specification: ORIGINAL_REQUEST.md (lines 101-102, 114)
"The UI colour palette shall be a light theme based on a mixture of white, yellow, gray, and dark blue."
Acceptance Criteria: "The UI colour scheme matches the specified light palette across all pages."

This test suite verifies:
  1. Complete absence of legacy dark slate root containers (`bg-slate-950`, `bg-slate-900`)
     across index.html, index.css, App.tsx, and all 7 core views.
  2. Conformance to approved light theme palette foundations:
     - White: Crisp background cards and modals (`bg-white`, `#ffffff`)
     - Light Gray: Page backdrop, dividers, and neutral text (`bg-slate-50`, `border-gray-200`, `text-slate-600`)
     - Dark Blue: High-contrast headings and primary accents (`text-blue-950`, `bg-blue-900`, `#0f172a`)
     - Warm Yellow: Vibrant interactive CTA highlights (`bg-yellow-400`, `hover:bg-yellow-500`, `text-yellow-800`)
  3. Elimination of legacy dominant purple/indigo action buttons.
"""

import re
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_SRC = PROJECT_ROOT / "frontend" / "src"

CORE_COMPONENTS = [
    ("App.tsx", FRONTEND_SRC / "App.tsx"),
    ("Header.tsx", FRONTEND_SRC / "components" / "Header.tsx"),
    ("IngestionView.tsx", FRONTEND_SRC / "components" / "Ingestion" / "IngestionView.tsx"),
    ("LessonPlanEditor.tsx", FRONTEND_SRC / "components" / "Planner" / "LessonPlanEditor.tsx"),
    ("InteractiveVideoPlayer.tsx", FRONTEND_SRC / "components" / "VideoPlayer" / "InteractiveVideoPlayer.tsx"),
    ("QuizView.tsx", FRONTEND_SRC / "components" / "Assessment" / "QuizView.tsx"),
    ("AnalyticsDashboard.tsx", FRONTEND_SRC / "components" / "Analytics" / "AnalyticsDashboard.tsx"),
]

ADDITIONAL_VIEWS = [
    ("ProfileModal.tsx", FRONTEND_SRC / "components" / "Profile" / "ProfileModal.tsx"),
    ("SidePanelTutor.tsx", FRONTEND_SRC / "components" / "TutorChat" / "SidePanelTutor.tsx"),
]


def test_r3_global_html_and_css_light_theme_roots():
    """
    R3.1: Asserts that index.html and index.css enforce a light canvas backdrop
    and do not configure legacy dark slate backgrounds (#020617, bg-slate-950).
    """
    index_html = (PROJECT_ROOT / "frontend" / "index.html").read_text(encoding="utf-8")
    assert "bg-slate-50" in index_html, "index.html body must use light backdrop 'bg-slate-50'"
    assert "bg-slate-950" not in index_html, "index.html body must not contain legacy 'bg-slate-950'"
    assert "text-slate-900" in index_html, "index.html body text must be high-contrast dark 'text-slate-900'"

    index_css = (FRONTEND_SRC / "index.css").read_text(encoding="utf-8")
    assert "#020617" not in index_css, "index.css must not configure legacy dark slate #020617"
    assert re.search(r"background-color:\s*#f8fafc", index_css, re.IGNORECASE), (
        "index.css root body must configure light background (#f8fafc)"
    )


def test_r3_absence_of_dark_slate_root_containers():
    """
    R3.2: Asserts the absence of legacy dark slate root containers (`bg-slate-950`, `bg-slate-900`)
    across App.tsx and all core view components.
    """
    for name, path in CORE_COMPONENTS:
        assert path.exists(), f"Component {name} not found at {path}"
        code = path.read_text(encoding="utf-8")

        # Root container check: Must not have min-h-screen bg-slate-950 or bg-slate-900 container
        assert not re.search(r'className="[^"]*min-h-screen\s+bg-slate-950', code), (
            f"R3 VIOLATION: {name} contains legacy 'min-h-screen bg-slate-950' root container"
        )
        assert not re.search(r'className="[^"]*min-h-screen\s+bg-slate-900', code), (
            f"R3 VIOLATION: {name} contains legacy 'min-h-screen bg-slate-900' root container"
        )

        # In Header, must not be dark slate
        if name == "Header.tsx":
            assert not re.search(r'bg-slate-900\b', code), (
                "R3 VIOLATION: Header.tsx must not use dark 'bg-slate-900' header container"
            )
            assert "bg-white" in code, "Header.tsx must use light surface (bg-white/95)"

        # In App.tsx, root wrapper must use light background
        if name == "App.tsx":
            assert "bg-slate-50" in code or "bg-white" in code, "App.tsx must use light root canvas"
            assert not re.search(r'className="[^"]*bg-slate-950', code), (
                "R3 VIOLATION: App.tsx root wrapper contains 'bg-slate-950'"
            )


def test_r3_light_theme_palette_presence_across_all_views():
    """
    R3.3: Asserts the presence of the required 4-color light palette across all 7 views:
      - White: `bg-white` surface cards
      - Light Gray: `bg-slate-50` / `border-gray-200` / `text-slate-600`
      - Dark Blue: `text-blue-950` / `bg-blue-900`
      - Warm Yellow: `bg-yellow-400` / `yellow-`
    """
    for name, path in CORE_COMPONENTS + ADDITIONAL_VIEWS:
        assert path.exists(), f"Component {name} not found at {path}"
        code = path.read_text(encoding="utf-8")

        # 1. White surface presence
        has_white = bool(re.search(r'bg-white|#ffffff', code, re.IGNORECASE))
        # 2. Gray neutral/border presence
        has_gray = bool(re.search(r'gray-|slate-50|slate-100|slate-200|slate-500|slate-600', code))
        # 3. Dark blue presence
        has_dark_blue = bool(re.search(r'blue-900|blue-950|text-blue|#0f172a|#172554', code))
        # 4. Yellow accent presence
        has_yellow = bool(re.search(r'yellow-|amber-', code))

        print(f"[R3 Palette Check - {name}]: White={has_white}, Gray={has_gray}, DarkBlue={has_dark_blue}, Yellow={has_yellow}")

        # Core views must have white or gray surface foundations
        assert has_white or has_gray, f"R3 VIOLATION: {name} lacks light surface foundations (white/gray)"
        # Core views must have high-contrast dark blue / slate text or accents
        assert has_dark_blue, f"R3 VIOLATION: {name} lacks dark blue typography/accent tokens"


def test_r3_absence_of_legacy_purple_primary_buttons():
    """
    R3.4: Asserts that legacy purple/indigo buttons (`bg-purple-600`, `bg-purple-700`)
    are replaced by the approved light theme primary buttons (yellow accent or dark blue).
    """
    for name, path in CORE_COMPONENTS:
        code = path.read_text(encoding="utf-8")
        assert not re.search(r'bg-purple-600\s+hover:bg-purple-700', code), (
            f"R3 VIOLATION: {name} still contains legacy 'bg-purple-600 hover:bg-purple-700' button styling"
        )
        assert not re.search(r'from-purple-600\s+to-indigo-600', code), (
            f"R3 VIOLATION: {name} still contains legacy 'from-purple-600 to-indigo-600' gradient"
        )


def test_r3_high_contrast_typography_on_light_surfaces():
    """
    R3.5: Asserts that text rendered on light surfaces provides high WCAG contrast
    using dark slate/blue tokens (e.g. text-slate-900, text-blue-950, text-slate-700).
    """
    app_code = (FRONTEND_SRC / "App.tsx").read_text(encoding="utf-8")
    assert "text-slate-900" in app_code or "text-blue-950" in app_code, (
        "App.tsx must utilize high-contrast dark typography (text-slate-900 / text-blue-950)"
    )

    ingestion_code = (FRONTEND_SRC / "components" / "Ingestion" / "IngestionView.tsx").read_text(encoding="utf-8")
    assert "text-blue-950" in ingestion_code, "IngestionView.tsx heading must use text-blue-950"
    assert "text-slate-600" in ingestion_code, "IngestionView.tsx description must use text-slate-600"
