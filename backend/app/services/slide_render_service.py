"""
Subject-Aware Visual Slide Rendering Service.
Renders Mathematics LaTeX/graphs, Computer Science IDE code frames with Pygments,
Biology cellular diagrams with callouts, and History milestone timelines into
1280x720 30fps synchronized video clips.
"""

import os
import io
import math
import logging
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Tuple
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import matplotlib
matplotlib.use("Agg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import pygments
from pygments.lexers import get_lexer_by_name, PythonLexer, guess_lexer
from pygments.token import Token

from backend.app.config import settings
from backend.app.models.lesson_plan import VisualSpec, VisualType

logger = logging.getLogger(__name__)


# Token Color Palette for Pygments IDE Rendering (OneDark / Modern Dark)
TOKEN_COLORS = {
    Token.Keyword: (198, 120, 221),       # Purple / Magenta
    Token.Keyword.Constant: (209, 154, 102),# Orange
    Token.Keyword.Declaration: (198, 120, 221),
    Token.Keyword.Namespace: (198, 120, 221),
    Token.Keyword.Type: (229, 192, 123),   # Yellow
    Token.Name.Function: (97, 175, 239),   # Blue
    Token.Name.Class: (229, 192, 123),     # Yellow
    Token.Name.Builtin: (86, 182, 194),    # Cyan
    Token.String: (152, 195, 121),         # Green
    Token.Number: (209, 154, 102),         # Orange
    Token.Comment: (127, 132, 142),        # Gray
    Token.Operator: (86, 182, 194),        # Cyan
    Token.Punctuation: (171, 178, 191),    # Light Gray
    Token.Name: (224, 108, 117),           # Coral / Red
    Token.Text: (209, 213, 220),           # Off-white
}


class SlideRenderService:
    """Enterprise-grade subject-aware visual slide generator."""

    def __init__(self, slides_dir: Optional[Path] = None):
        self.slides_dir = Path(slides_dir) if slides_dir else settings.slides_dir
        self.slides_dir.mkdir(parents=True, exist_ok=True)
        self.ffmpeg_path = settings.ffmpeg_path
        self.ffprobe_path = settings.ffprobe_path
        self.width = 1280
        self.height = 720
        self.fps = 30

    def _draw_base_canvas(self, title: str, domain_badge: str = "Concept Explanation") -> Tuple[Image.Image, ImageDraw.ImageDraw]:
        """Creates standard 1280x720 high-definition dark canvas with header bar."""
        img = Image.new("RGB", (self.width, self.height), (15, 20, 30))
        draw = ImageDraw.Draw(img)

        # Subtle dark gradient background
        for y in range(0, self.height, 6):
            r = int(15 + 10 * (y / self.height))
            g = int(20 + 12 * (y / self.height))
            b = int(32 + 16 * (y / self.height))
            draw.line([(0, y), (self.width, y)], fill=(r, g, b), width=6)

        # Top Header Bar
        draw.rectangle([0, 0, self.width, 70], fill=(22, 30, 46))
        draw.line([(0, 70), (self.width, 70)], fill=(50, 70, 105), width=2)

        # Domain Badge
        draw.rounded_rectangle([30, 18, 190, 52], radius=6, fill=(38, 55, 88), outline=(75, 110, 175), width=1)
        draw.text((42, 26), f"● {domain_badge.upper()}", fill=(130, 190, 255))

        # Title
        draw.text((215, 23), title[:65], fill=(255, 255, 255))

        # ApniHelp Logo / Watermark
        draw.rounded_rectangle([self.width - 165, 18, self.width - 30, 52], radius=6, fill=(28, 38, 60))
        draw.text((self.width - 145, 26), "ApniHelp", fill=(100, 210, 170))

        return img, draw

    def _clean_latex_for_mathtext(self, eq: str) -> str:
        """Cleans and formats LaTeX expressions for Matplotlib mathtext compatibility."""
        clean = eq.strip()
        if clean.startswith("$") and clean.endswith("$"):
            clean = clean[1:-1].strip()
        # Handle unescaped control chars if any
        clean = clean.replace("\t", r"\to ").replace("\f", r"\frac").replace("\r", "")
        # Ensure common symbols are mathtext compatible
        clean = clean.replace(r"\implies", r"\Rightarrow").replace(r"\iff", r"\Leftrightarrow")
        if not clean:
            clean = r"f(x) = y"
        return f"${clean}$"

    def render_math_slide(self, spec: VisualSpec, title: str) -> Image.Image:
        """Renders mathematical derivations, LaTeX formulas, and 2D function graphs."""
        img, draw = self._draw_base_canvas(title, domain_badge="Mathematics")

        # Left Column: Step-by-Step Derivation & LaTeX Formulas (Width: 680px)
        left_box = [30, 95, 680, 685]
        draw.rounded_rectangle(left_box, radius=12, fill=(20, 28, 44), outline=(45, 65, 100), width=2)

        # Headline
        draw.text((50, 115), spec.headline or "Mathematical Foundation & Derivation", fill=(255, 215, 0))
        draw.line([(50, 145), (660, 145)], fill=(45, 65, 100), width=1)

        # LaTeX Equation Cards
        eqs = spec.latex_equations or ["\\lim_{x \\to 0} \\frac{\\sin(x)}{x} = 1", "f'(x) = \\lim_{h \\to 0} \\frac{f(x+h) - f(x)}{h}"]
        curr_y = 160

        for i, eq in enumerate(eqs[:3]):
            # Render LaTeX equation as an image with Matplotlib
            try:
                fig = Figure(figsize=(6.0, 0.9), dpi=100)
                canvas = FigureCanvasAgg(fig)
                fig.patch.set_facecolor("#182236")
                ax = fig.add_axes([0, 0, 1, 1])
                ax.set_facecolor("#182236")
                ax.axis("off")
                math_text = self._clean_latex_for_mathtext(eq)
                ax.text(0.5, 0.5, math_text, color="#38bdf8", fontsize=18, ha="center", va="center", weight="bold")
                buf = io.BytesIO()
                canvas.print_figure(buf, format="png", bbox_inches="tight", pad_inches=0.08, facecolor=fig.get_facecolor())
                buf.seek(0)
                eq_img = Image.open(buf)

                # Paste equation card
                eq_box = [50, curr_y, 660, curr_y + eq_img.height + 10]
                draw.rounded_rectangle(eq_box, radius=8, fill=(24, 34, 54), outline=(56, 189, 248), width=1)
                img.paste(eq_img, (58, curr_y + 5))
                curr_y += eq_img.height + 22
            except Exception as e:
                logger.warning(f"Matplotlib LaTeX rendering error: {e}")
                draw.rounded_rectangle([50, curr_y, 660, curr_y + 45], radius=8, fill=(24, 34, 54))
                draw.text((65, curr_y + 12), f"Formula: {eq}", fill=(56, 189, 248))
                curr_y += 58

        # Bullet points / Step explanations
        curr_y = max(curr_y + 10, 360)
        draw.text((50, curr_y), "Key Analytical Steps:", fill=(220, 230, 245))
        curr_y += 30

        bullets = spec.bullet_points or [
            "Evaluate direct substitution to detect indeterminate forms (0/0).",
            "Apply algebraic simplification or L'Hôpital's rule.",
            "Verify left-hand and right-hand limits converge to the same finite value.",
        ]
        for bullet in bullets[:4]:
            draw.text((55, curr_y), f"• {bullet[:65]}", fill=(185, 200, 225))
            curr_y += 28

        # Right Column: Matplotlib Function Graph Plot (Width: 520px)
        right_box = [710, 95, 1250, 685]
        draw.rounded_rectangle(right_box, radius=12, fill=(20, 28, 44), outline=(45, 65, 100), width=2)

        try:
            fig = Figure(figsize=(5.0, 5.2), dpi=100)
            canvas = FigureCanvasAgg(fig)
            fig.patch.set_facecolor("#141c2c")
            ax = fig.add_subplot(111)
            ax.set_facecolor("#0f172a")

            # Plot function curve
            x = np.linspace(-4, 4, 200)
            if "sin" in str(eqs).lower():
                y = np.sin(x) / np.where(x == 0, 1e-5, x)
                label = r"$f(x) = \frac{\sin(x)}{x}$"
            elif "derivative" in title.lower() or "limit" in title.lower():
                y = x**2 - 2
                label = r"$f(x) = x^2 - 2$"
                # Tangent line at x=1
                tangent_x = np.linspace(-1, 3, 50)
                tangent_y = 2 * (tangent_x - 1) - 1
                ax.plot(tangent_x, tangent_y, color="#f59e0b", linestyle="--", linewidth=2.0, label="Tangent $f'(1)=2$")
                ax.scatter([1], [-1], color="#ef4444", s=80, zorder=5)
            else:
                y = x**3 - 3*x
                label = r"$f(x) = x^3 - 3x$"

            ax.plot(x, y, color="#38bdf8", linewidth=2.8, label=label)
            ax.axhline(0, color="#64748b", linestyle=":", linewidth=1.0)
            ax.axvline(0, color="#64748b", linestyle=":", linewidth=1.0)
            ax.grid(True, color="#1e293b", linestyle="--", alpha=0.8)
            ax.set_title("Function Behavior & Trajectory", color="#f8fafc", fontsize=12, pad=10)
            ax.tick_params(colors="#94a3b8", labelsize=9)
            ax.legend(facecolor="#1e293b", edgecolor="#475569", labelcolor="#f1f5f9", fontsize=9, loc="upper right")

            buf = io.BytesIO()
            canvas.print_figure(buf, format="png", bbox_inches="tight", pad_inches=0.1, facecolor=fig.get_facecolor())
            buf.seek(0)
            plot_img = Image.open(buf)
            img.paste(plot_img, (725, 115))
        except Exception as e:
            logger.warning(f"Matplotlib graph generation failed: {e}")
            draw.text((750, 300), "Graph visualization available in full session.", fill=(160, 190, 230))

        return img

    def render_code_slide(self, spec: VisualSpec, title: str) -> Image.Image:
        """Renders syntax-highlighted code inside modern IDE window frame with execution trace."""
        img, draw = self._draw_base_canvas(title, domain_badge="Computer Science")

        # Left/Center: IDE Window Card (Width: 800px)
        ide_box = [30, 95, 840, 685]
        draw.rounded_rectangle(ide_box, radius=10, fill=(22, 27, 34), outline=(48, 54, 61), width=2)

        # IDE Window Titlebar
        draw.rectangle([30, 95, 840, 135], fill=(30, 36, 48))
        draw.line([(30, 135), (840, 135)], fill=(48, 54, 61), width=1)

        # MacOS Window Control Traffic Lights
        draw.ellipse([46, 109, 58, 121], fill=(255, 95, 86))   # Red
        draw.ellipse([64, 109, 76, 121], fill=(255, 189, 46))  # Yellow
        draw.ellipse([82, 109, 94, 121], fill=(39, 201, 63))   # Green

        # Tab File Badge
        filename = "solution.py" if (spec.code_language or "").lower() in ["python", "py", ""] else f"solution.{spec.code_language}"
        draw.rounded_rectangle([120, 103, 260, 135], radius=5, fill=(22, 27, 34))
        draw.text((135, 110), f"📄 {filename}", fill=(200, 215, 235))

        # Code Content & Syntax Highlighting
        raw_code = spec.code_content or (
            "def binary_search(arr: list[int], target: int) -> int:\n"
            "    low, high = 0, len(arr) - 1\n"
            "    while low <= high:\n"
            "        mid = (low + high) // 2\n"
            "        if arr[mid] == target:\n"
            "            return mid  # Target found\n"
            "        elif arr[mid] < target:\n"
            "            low = mid + 1\n"
            "        else:\n"
            "            high = mid - 1\n"
            "    return -1  # Not present"
        )

        lexer = PythonLexer()
        try:
            tokens = list(pygments.lex(raw_code, lexer))
        except Exception:
            tokens = [(Token.Text, raw_code)]

        # Render Lines with Line Numbers
        line_num = 1
        curr_x = 90
        curr_y = 155
        line_height = 24

        # Draw Line Number 1
        draw.text((45, curr_y), f"{line_num:2d}", fill=(90, 100, 115))

        for ttype, val in tokens:
            color = TOKEN_COLORS.get(ttype, (209, 213, 220))
            # Check for specific token parent mappings
            if ttype not in TOKEN_COLORS:
                for parent_t, pcol in TOKEN_COLORS.items():
                    if ttype in parent_t:
                        color = pcol
                        break

            lines = val.split("\n")
            for i, line_chunk in enumerate(lines):
                if i > 0:
                    line_num += 1
                    curr_y += line_height
                    curr_x = 90
                    if curr_y > 650:
                        break
                    draw.text((45, curr_y), f"{line_num:2d}", fill=(90, 100, 115))

                if line_chunk:
                    draw.text((curr_x, curr_y), line_chunk, fill=color)
                    curr_x += len(line_chunk) * 9

        # Right Panel: Runtime Trace & Complexity Watch (Width: 380px)
        trace_box = [860, 95, 1250, 685]
        draw.rounded_rectangle(trace_box, radius=10, fill=(20, 28, 44), outline=(45, 65, 100), width=2)

        draw.text((880, 115), "RUNTIME EXECUTION TRACE", fill=(255, 215, 0))
        draw.line([(880, 145), (1230, 145)], fill=(45, 65, 100), width=1)

        # Variable Watch Table
        trace_items = [
            ("Time Complexity", "O(log n) logarithmic"),
            ("Space Complexity", "O(1) auxiliary auxiliary"),
            ("Search Space", "Halved every iteration"),
            ("Loop Invariant", "target in arr[low..high]"),
            ("Base Condition", "low > high terminates"),
        ]
        curr_trace_y = 165
        for label, val in trace_items:
            draw.text((880, curr_trace_y), label, fill=(130, 190, 255))
            draw.rounded_rectangle([880, curr_trace_y + 22, 1230, curr_trace_y + 54], radius=6, fill=(26, 38, 62))
            draw.text((895, curr_trace_y + 29), val, fill=(240, 245, 255))
            curr_trace_y += 66

        # Step Key Takeaways
        bullets = spec.bullet_points or [
            "Input array must be sorted in ascending order.",
            "Avoid integer overflow with mid = low + (high-low)//2.",
        ]
        curr_trace_y += 10
        draw.text((880, curr_trace_y), "Key Implementation Rules:", fill=(220, 230, 245))
        curr_trace_y += 28
        for b in bullets[:3]:
            draw.text((885, curr_trace_y), f"• {b[:42]}", fill=(185, 200, 225))
            curr_trace_y += 24

        return img

    def render_diagram_slide(self, spec: VisualSpec, title: str) -> Image.Image:
        """Renders biological anatomical diagrams with clear pointer callouts."""
        img, draw = self._draw_base_canvas(title, domain_badge="Biology & Life Sciences")

        # Left Column: Cellular Anatomical Illustration
        diag_box = [30, 95, 680, 685]
        draw.rounded_rectangle(diag_box, radius=12, fill=(18, 26, 42), outline=(45, 70, 110), width=2)

        cx, cy = 355, 390
        # 1. Plasma Membrane & Cytoplasm
        draw.ellipse([cx - 280, cy - 240, cx + 280, cy + 240], fill=(24, 45, 75), outline=(56, 189, 248), width=4)
        draw.ellipse([cx - 270, cy - 230, cx + 270, cy + 230], fill=(28, 52, 88))

        # 2. Nucleus & Nucleolus
        draw.ellipse([cx - 110, cy - 100, cx + 110, cy + 100], fill=(76, 29, 149), outline=(168, 85, 247), width=3)
        draw.ellipse([cx - 40, cy - 35, cx + 40, cy + 35], fill=(192, 132, 252))

        # 3. Mitochondria (Oval with inner cristae folds)
        # Mito 1 (Top Right)
        mx1, my1 = cx + 140, cy - 130
        draw.ellipse([mx1 - 65, my1 - 35, mx1 + 65, my1 + 35], fill=(180, 83, 9), outline=(245, 158, 11), width=2)
        draw.arc([mx1 - 45, my1 - 20, mx1 + 45, my1 + 20], start=30, end=150, fill=(253, 230, 138), width=2)
        # Mito 2 (Bottom Left)
        mx2, my2 = cx - 150, cy + 120
        draw.ellipse([mx2 - 65, my2 - 35, mx2 + 65, my2 + 35], fill=(180, 83, 9), outline=(245, 158, 11), width=2)

        # 4. Golgi Apparatus & Endoplasmic Reticulum
        draw.arc([cx - 180, cy - 120, cx - 100, cy - 40], start=180, end=360, fill=(52, 211, 153), width=4)
        draw.arc([cx - 190, cy - 105, cx - 90, cy - 25], start=180, end=360, fill=(52, 211, 153), width=4)

        # Structure Callout Pointers & Lines
        callouts = [
            ((cx, cy - 35), (cx + 20, cy - 90), "Nucleus: Genetic DNA Control"),
            ((mx1, my1), (mx1 + 40, my1 - 50), "Mitochondria: ATP Energy Synthesis"),
            ((cx - 140, cy - 80), (cx - 220, cy - 140), "Endoplasmic Reticulum"),
            ((cx + 240, cy + 80), (cx + 170, cy + 180), "Plasma Membrane: Selective Barrier"),
        ]
        for start_pt, end_pt, label in callouts:
            draw.line([start_pt, end_pt], fill=(255, 255, 255), width=2)
            draw.ellipse([start_pt[0] - 4, start_pt[1] - 4, start_pt[0] + 4, start_pt[1] + 4], fill=(239, 68, 68))
            draw.rounded_rectangle([end_pt[0] - 10, end_pt[1] - 14, end_pt[0] + len(label) * 8 + 10, end_pt[1] + 16], radius=5, fill=(15, 23, 42), outline=(56, 189, 248), width=1)
            draw.text((end_pt[0], end_pt[1] - 7), label, fill=(240, 245, 255))

        # Right Column: Organelle Functions & Biological Mechanisms (Width: 520px)
        info_box = [710, 95, 1250, 685]
        draw.rounded_rectangle(info_box, radius=12, fill=(20, 28, 44), outline=(45, 65, 100), width=2)

        draw.text((735, 115), spec.headline or "CELLULAR MORPHOLOGY & FUNCTION", fill=(255, 215, 0))
        draw.line([(735, 145), (1225, 145)], fill=(45, 65, 100), width=1)

        bullets = spec.bullet_points or [
            "Mitochondria generate cellular ATP through oxidative phosphorylation.",
            "The nucleus houses chromatin and directs protein transcription.",
            "Phospholipid bilayer maintains cellular homeostasis via active transport.",
            "Ribosomes on the rough ER synthesize polypeptide chains.",
        ]
        curr_y = 165
        for i, bullet in enumerate(bullets[:5]):
            draw.rounded_rectangle([735, curr_y, 1225, curr_y + 80], radius=8, fill=(26, 38, 60))
            draw.text((750, curr_y + 12), f"Organelle System {i+1}:", fill=(56, 189, 248))
            draw.text((750, curr_y + 38), f"• {bullet[:52]}", fill=(225, 235, 250))
            curr_y += 95

        return img

    def render_timeline_slide(self, spec: VisualSpec, title: str) -> Image.Image:
        """Renders historical chronological timeline with milestone cards."""
        img, draw = self._draw_base_canvas(title, domain_badge="History & Social Sciences")

        # Main Timeline Card Container
        container_box = [30, 95, 1250, 685]
        draw.rounded_rectangle(container_box, radius=12, fill=(20, 28, 44), outline=(45, 65, 100), width=2)

        # Headline
        draw.text((55, 115), spec.headline or "CHRONOLOGICAL MILESTONES & HISTORICAL PROGRESSION", fill=(255, 215, 0))
        draw.line([(55, 145), (1225, 145)], fill=(45, 65, 100), width=1)

        # Central Horizontal Progression Bar
        axis_y = 380
        draw.line([(80, axis_y), (1200, axis_y)], fill=(75, 110, 170), width=6)
        # Arrowhead
        draw.polygon([(1200, axis_y - 12), (1225, axis_y), (1200, axis_y + 12)], fill=(75, 110, 170))

        # Default Historical Timeline Events
        events = spec.timeline_events or [
            {"year": "1769", "title": "Watt's Steam Engine", "description": "James Watt patents condenser steam engine."},
            {"year": "1784", "title": "Puddling Process", "description": "Henry Cort revolutionizes wrought iron smelting."},
            {"year": "1804", "title": "Steam Locomotive", "description": "Trevithick builds first railway locomotive."},
            {"year": "1830", "title": "Liverpool Railway", "description": "First inter-city twin-track passenger line."},
            {"year": "1851", "title": "Great Exhibition", "description": "Crystal Palace showcases global manufacturing."},
        ]

        num_events = len(events)
        spacing = (1120 - 100) / max(1, num_events - 1)

        for i, ev in enumerate(events[:5]):
            nx = int(100 + i * spacing)
            year = ev.get("year", f"Period {i+1}")
            ev_title = ev.get("title", f"Milestone {i+1}")
            ev_desc = ev.get("description", "")

            # Milestone Node Circle
            draw.ellipse([nx - 14, axis_y - 14, nx + 14, axis_y + 14], fill=(56, 189, 248), outline=(255, 255, 255), width=3)

            # Alternate top and bottom cards
            is_top = (i % 2 == 0)
            if is_top:
                card_box = [nx - 100, axis_y - 190, nx + 100, axis_y - 35]
                stem_line = [(nx, axis_y - 14), (nx, axis_y - 35)]
            else:
                card_box = [nx - 100, axis_y + 35, nx + 100, axis_y + 190]
                stem_line = [(nx, axis_y + 14), (nx, axis_y + 35)]

            # Connecting stem line
            draw.line(stem_line, fill=(56, 189, 248), width=2)

            # Milestone Event Card
            draw.rounded_rectangle(card_box, radius=8, fill=(28, 40, 64), outline=(56, 189, 248), width=1)
            # Year Badge
            draw.rounded_rectangle([card_box[0] + 10, card_box[1] + 10, card_box[0] + 80, card_box[1] + 34], radius=4, fill=(38, 60, 95))
            draw.text((card_box[0] + 16, card_box[1] + 14), year, fill=(255, 215, 0))
            # Title & Description
            draw.text((card_box[0] + 12, card_box[1] + 42), ev_title[:20], fill=(255, 255, 255))
            draw.text((card_box[0] + 12, card_box[1] + 68), ev_desc[:38], fill=(185, 200, 225))

        # Bottom / Top Summary Bullet Points
        bullets = spec.bullet_points or [
            "Mechanization replaced manual agrarian labor with high-throughput factories.",
            "Urban migration concentrated labor in manufacturing hubs across Britain.",
        ]
        curr_b_y = 610
        draw.text((55, curr_b_y), "Socio-Economic Impact & Long-Term Outcomes:", fill=(220, 230, 245))
        for b in bullets[:2]:
            curr_b_y += 24
            draw.text((65, curr_b_y), f"• {b[:90]}", fill=(185, 200, 225))

        return img

    def render_general_slide(self, spec: VisualSpec, title: str) -> Image.Image:
        """Renders versatile conceptual summary card slide with callouts and structured cards."""
        img, draw = self._draw_base_canvas(title, domain_badge="Core Concepts")

        # Container Box
        container_box = [30, 95, 1250, 685]
        draw.rounded_rectangle(container_box, radius=12, fill=(20, 28, 44), outline=(45, 65, 100), width=2)

        # Headline
        draw.text((55, 115), spec.headline or title.upper(), fill=(255, 215, 0))
        draw.line([(55, 145), (1225, 145)], fill=(45, 65, 100), width=1)

        # Render 3 Conceptual Cards
        bullets = spec.bullet_points or [
            "Core theoretical formulation and structural properties.",
            "Systematic procedural methodology and proof mechanisms.",
            "Practical real-world applications and edge-case invariants.",
        ]
        card_w = 365
        for i, bullet in enumerate(bullets[:3]):
            bx = 55 + i * (card_w + 35)
            card_box = [bx, 175, bx + card_w, 480]
            draw.rounded_rectangle(card_box, radius=10, fill=(28, 38, 62), outline=(56, 189, 248), width=1)

            # Card Header Badge
            draw.rounded_rectangle([bx + 15, 195, bx + 120, 225], radius=5, fill=(38, 55, 88))
            draw.text((bx + 25, 202), f"PILLAR 0{i+1}", fill=(56, 189, 248))

            # Pillar Title
            draw.text((bx + 15, 245), f"Core Principle {i+1}", fill=(255, 255, 255))
            draw.line([(bx + 15, 275), (bx + card_w - 15, 275)], fill=(45, 65, 100), width=1)

            # Description
            draw.text((bx + 15, 290), bullet[:120], fill=(200, 215, 240))

        # Bottom Callout Box
        callout_box = [55, 515, 1225, 655]
        draw.rounded_rectangle(callout_box, radius=10, fill=(25, 34, 52), outline=(234, 179, 8), width=1)
        draw.text((75, 530), "💡 PEDAGOGICAL TAKEAWAY & FORMULATION:", fill=(234, 179, 8))
        draw.text((75, 565), (spec.callout_box or "Mastery requires active synthesis of definitions, rigorous worked verification, and continuous formative assessment."), fill=(230, 240, 255))

        return img

    def render_slide_image(self, spec: Optional[VisualSpec], title: str) -> Image.Image:
        """Dispatches to the appropriate subject-aware slide renderer."""
        if not spec:
            spec = VisualSpec(visual_type=VisualType.GENERAL_SLIDE, subject_domain="General", headline=title)

        vtype = spec.visual_type
        if isinstance(vtype, str):
            vtype_str = vtype.lower()
        else:
            vtype_str = vtype.value.lower() if vtype else "general_slide"

        if "math" in vtype_str or "equation" in vtype_str:
            return self.render_math_slide(spec, title)
        elif "code" in vtype_str or "programming" in vtype_str:
            return self.render_code_slide(spec, title)
        elif "diagram" in vtype_str or "biology" in vtype_str or "science" in vtype_str:
            return self.render_diagram_slide(spec, title)
        elif "timeline" in vtype_str or "history" in vtype_str:
            return self.render_timeline_slide(spec, title)
        else:
            return self.render_general_slide(spec, title)

    def render_slide_video(
        self,
        spec: Optional[VisualSpec],
        title: str,
        audio_path: Path,
        output_video_path: Path,
        duration_sec: float,
    ) -> Path:
        """
        Renders the subject-aware visual slide as a continuous 30fps MP4 video clip
        synchronized with the TTS audio narration narration.
        """
        output_video_path = Path(output_video_path)
        output_video_path.parent.mkdir(parents=True, exist_ok=True)

        # 1. Render high-resolution slide image
        slide_img = self.render_slide_image(spec, title)
        temp_img_path = self.slides_dir / f"slide_frame_{output_video_path.stem}.png"
        slide_img.save(str(temp_img_path))

        # 2. Encode to 30fps H.264/AAC MP4 matching exact audio duration
        cmd = [
            self.ffmpeg_path,
            "-y",
            "-loop", "1",
            "-i", str(temp_img_path),
            "-i", str(audio_path),
            "-c:v", "libx264",
            "-t", str(duration_sec),
            "-pix_fmt", "yuv420p",
            "-r", str(self.fps),
            "-preset", "ultrafast",
            "-tune", "stillimage",
            "-crf", "26",
            "-threads", "2",
            "-g", "120",
            "-c:a", "aac",
            "-ar", "44100",
            "-ac", "2",
            "-b:a", "128k",
            "-shortest",
            "-movflags", "+faststart",
            str(output_video_path),
        ]

        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        temp_img_path.unlink(missing_ok=True)

        if proc.returncode != 0:
            err = proc.stderr.decode(errors="ignore")
            logger.error(f"FFmpeg slide video rendering failed ({proc.returncode}): {err}")
            raise RuntimeError(f"FFmpeg slide rendering failed: {err}")

        return output_video_path


slide_render_service = SlideRenderService()
