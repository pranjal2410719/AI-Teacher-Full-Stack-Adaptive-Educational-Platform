import sys
import os
sys.path.insert(0, os.path.abspath("venv_test/lib/python3.11/site-packages"))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import pygments
from pygments.lexers import PythonLexer
from pygments.formatters import ImageFormatter, SvgFormatter
import io

def generate_math_slide(output_path="test_scripts/math_slide.png"):
    """Render a subject-aware Mathematics slide with equations, graph, and step-by-step breakdown."""
    fig = plt.figure(figsize=(16, 9), dpi=100, facecolor='#0F172A')
    
    # 1. Slide Header
    fig.text(0.05, 0.92, "MATHEMATICS: CALCULUS & OPTIMIZATION", fontsize=16, fontweight='bold', color='#38BDF8', fontfamily='sans-serif')
    fig.text(0.05, 0.85, "Gradient Descent & Quadratic Convergence", fontsize=24, fontweight='bold', color='#F8FAFC', fontfamily='sans-serif')
    
    # 2. Left Column: Step-by-Step Derivations & LaTeX formulas
    ax_left = fig.add_axes([0.05, 0.1, 0.45, 0.7])
    ax_left.axis('off')
    
    formula_1 = r"Objective Function:  $f(x) = \frac{1}{2} x^T A x - b^T x$"
    formula_2 = r"Gradient:  $\nabla f(x) = A x - b$"
    formula_3 = r"Update Rule:  $x_{k+1} = x_k - \alpha \nabla f(x_k)$"
    formula_4 = r"Optimal Step Size:  $\alpha^* = \frac{r_k^T r_k}{r_k^T A r_k}$"
    
    ax_left.text(0.02, 0.85, "1. Objective Formulation", fontsize=18, fontweight='bold', color='#E2E8F0')
    ax_left.text(0.05, 0.73, formula_1, fontsize=16, color='#93C5FD')
    
    ax_left.text(0.02, 0.58, "2. First-Order Necessary Condition", fontsize=18, fontweight='bold', color='#E2E8F0')
    ax_left.text(0.05, 0.46, formula_2, fontsize=16, color='#93C5FD')
    
    ax_left.text(0.02, 0.31, "3. Iterative Descent Step", fontsize=18, fontweight='bold', color='#E2E8F0')
    ax_left.text(0.05, 0.19, formula_3, fontsize=16, color='#34D399')
    ax_left.text(0.05, 0.07, formula_4, fontsize=16, color='#FBBF24')
    
    # 3. Right Column: Dynamic Plot / Curve
    ax_right = fig.add_axes([0.55, 0.15, 0.4, 0.65], facecolor='#1E293B')
    ax_right.grid(True, linestyle='--', alpha=0.3, color='#64748B')
    for spine in ax_right.spines.values():
        spine.set_color('#475569')
    ax_right.tick_params(colors='#94A3B8')
    
    x = np.linspace(-3, 3, 200)
    y = x**2 + 0.5*np.sin(3*x)
    ax_right.plot(x, y, color='#38BDF8', linewidth=3, label=r'$f(x) = x^2 + 0.5\sin(3x)$')
    
    # Trajectory of gradient descent
    steps_x = [2.6, 1.8, 1.1, 0.4, 0.05]
    steps_y = [s**2 + 0.5*np.sin(3*s) for s in steps_x]
    ax_right.plot(steps_x, steps_y, 'ro--', markersize=8, color='#F43F5E', linewidth=2, label='Descent Path ($x_k$)')
    ax_right.annotate('Start ($x_0$)', xy=(steps_x[0], steps_y[0]), xytext=(steps_x[0]-0.8, steps_y[0]+1.5),
                     color='#F43F5E', fontsize=12, fontweight='bold',
                     arrowprops=dict(facecolor='#F43F5E', shrink=0.05, width=1, headwidth=6))
    ax_right.annotate('Minimum ($x^*$)', xy=(steps_x[-1], steps_y[-1]), xytext=(steps_x[-1]-1.5, steps_y[-1]+2.5),
                     color='#34D399', fontsize=12, fontweight='bold',
                     arrowprops=dict(facecolor='#34D399', shrink=0.05, width=1, headwidth=6))
    
    ax_right.set_title("Loss Surface & Convergence Trajectory", color='#F8FAFC', fontsize=14, pad=12)
    ax_right.legend(facecolor='#0F172A', edgecolor='#334155', labelcolor='#F8FAFC', loc='upper center')
    
    plt.savefig(output_path, dpi=100, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close()
    print(f"Generated Math slide at {output_path}")

def generate_code_slide(output_path="test_scripts/code_slide.png"):
    """Render a subject-aware Computer Science / Programming slide with Pygments syntax highlighting."""
    code = '''# Binary Search Algorithm: O(log N) Time Complexity
def binary_search(arr: list[int], target: int) -> int:
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = left + (right - left) // 2
        print(f"Checking mid={mid}, value={arr[mid]}")
        
        if arr[mid] == target:
            return mid  # Target found!
        elif arr[mid] < target:
            left = mid + 1  # Search right half
        else:
            right = mid - 1 # Search left half
            
    return -1  # Target not in list'''

    # Pygments syntax highlight to image
    formatter = ImageFormatter(font_size=20, line_numbers=True, style="monokai")
    code_img_bytes = pygments.highlight(code, PythonLexer(), formatter)
    code_img = Image.open(io.BytesIO(code_img_bytes))
    
    # Composite into 16:9 1280x720 canvas
    canvas = Image.new("RGBA", (1280, 720), "#0B0F19")
    draw = ImageDraw.Draw(canvas)
    
    # Title / Header
    draw.rectangle([(0, 0), (1280, 80)], fill="#111827")
    draw.text((40, 25), "COMPUTER SCIENCE: ALGORITHMS & DATA STRUCTURES", fill="#60A5FA")
    draw.text((800, 25), "Topic: Divide & Conquer", fill="#9CA3AF")
    
    # Code Card frame (IDE Style)
    card_x, card_y = 50, 110
    card_w, card_h = 750, 560
    draw.rectangle([(card_x, card_y), (card_x + card_w, card_y + card_h)], fill="#1E1E1E", outline="#374151", width=2)
    # Window buttons (Mac style)
    draw.ellipse([(card_x + 15, card_y + 12), (card_x + 27, card_y + 24)], fill="#EF4444")
    draw.ellipse([(card_x + 35, card_y + 12), (card_x + 47, card_y + 24)], fill="#F59E0B")
    draw.ellipse([(card_x + 55, card_y + 12), (card_x + 67, card_y + 24)], fill="#10B981")
    draw.text((card_x + 90, card_y + 10), "binary_search.py", fill="#9CA3AF")
    
    # Paste Pygments rendered code
    code_resized = code_img.resize((card_w - 20, card_h - 60))
    canvas.paste(code_resized, (card_x + 10, card_y + 45))
    
    # Right Side: Execution State & Complexity Analysis Card
    right_x, right_y = 830, 110
    right_w, right_h = 400, 560
    draw.rectangle([(right_x, right_y), (right_x + right_w, right_y + right_h)], fill="#1F2937", outline="#374151", width=2)
    draw.text((right_x + 20, right_y + 20), "Execution Trace (arr=[2,5,8,12,16], target=12)", fill="#F3F4F6")
    
    # Trace steps
    steps = [
        ("Step 1", "L=0, R=4 -> Mid=2 (arr[2]=8)", "8 < 12 => L=3", "#93C5FD"),
        ("Step 2", "L=3, R=4 -> Mid=3 (arr[3]=12)", "12 == 12 => MATCH!", "#34D399"),
        ("Complexity", "Time: O(log N) | Space: O(1)", "Logarithmic reduction", "#FBBF24")
    ]
    
    sy = right_y + 70
    for title, line1, line2, col in steps:
        draw.rectangle([(right_x + 15, sy), (right_x + right_w - 15, sy + 110)], fill="#111827", outline=col, width=2)
        draw.text((right_x + 25, sy + 10), title, fill=col)
        draw.text((right_x + 25, sy + 40), line1, fill="#E5E7EB")
        draw.text((right_x + 25, sy + 70), line2, fill="#9CA3AF")
        sy += 130
        
    canvas.save(output_path)
    print(f"Generated Code slide at {output_path}")

def generate_biology_diagram_slide(output_path="test_scripts/diagram_slide.png"):
    """Render a subject-aware Biology / Science diagram with callouts, components, and flow."""
    fig = plt.figure(figsize=(16, 9), dpi=100, facecolor='#090D16')
    
    # Header
    fig.text(0.05, 0.92, "BIOLOGY & PHYSIOLOGY: CELLULAR BIOLOGY", fontsize=16, fontweight='bold', color='#34D399', fontfamily='sans-serif')
    fig.text(0.05, 0.85, "Structure of Mitochondria: The Powerhouse of the Cell", fontsize=24, fontweight='bold', color='#F8FAFC', fontfamily='sans-serif')
    
    ax = fig.add_axes([0.05, 0.08, 0.9, 0.74], facecolor='#131D2E')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    # Draw Outer Membrane
    from matplotlib.patches import Ellipse, FancyBboxPatch, ArrowStyle
    outer = Ellipse((50, 50), 60, 40, angle=-10, edgecolor='#10B981', facecolor='#064E3B', linewidth=4, alpha=0.8)
    ax.add_patch(outer)
    
    # Draw Inner Membrane with Cristae folds
    inner = Ellipse((50, 50), 52, 32, angle=-10, edgecolor='#F59E0B', facecolor='#78350F', linewidth=3, linestyle='--', alpha=0.8)
    ax.add_patch(inner)
    
    # Labels & Callouts with arrows
    callouts = [
        ("Outer Membrane", "Porin channels & permeability barrier", (25, 68), (15, 80), '#10B981'),
        ("Intermembrane Space", "Proton accumulation ($H^+$ gradient)", (45, 68), (35, 88), '#38BDF8'),
        ("Cristae Folds", "Maximizes surface area for ATP Synthase", (65, 45), (82, 60), '#F59E0B'),
        ("Mitochondrial Matrix", "Krebs / Citric Acid Cycle & mtDNA", (50, 42), (50, 15), '#EC4899'),
        ("ATP Synthase Complexes", "Rotary motor generating ATP from ADP", (60, 32), (80, 20), '#A855F7')
    ]
    
    for label, desc, target, pos, color in callouts:
        ax.annotate(f"{label}\n({desc})", xy=target, xytext=pos,
                    fontsize=12, fontweight='bold', color='#F8FAFC',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='#1E293B', edgecolor=color, linewidth=2),
                    arrowprops=dict(facecolor=color, edgecolor=color, shrink=0.08, width=2, headwidth=8))
        
    plt.savefig(output_path, dpi=100, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close()
    print(f"Generated Diagram slide at {output_path}")

def generate_timeline_slide(output_path="test_scripts/timeline_slide.png"):
    """Render a subject-aware History / Evolution timeline with milestones and cards."""
    fig = plt.figure(figsize=(16, 9), dpi=100, facecolor='#0B1120')
    
    # Header
    fig.text(0.05, 0.92, "HISTORY & TECHNOLOGY: EVOLUTION OF ARTIFICIAL INTELLIGENCE", fontsize=16, fontweight='bold', color='#F43F5E', fontfamily='sans-serif')
    fig.text(0.05, 0.85, "From Dartmouth Conference to Large Language Models (1956 - 2026)", fontsize=24, fontweight='bold', color='#F8FAFC', fontfamily='sans-serif')
    
    ax = fig.add_axes([0.05, 0.1, 0.9, 0.7], facecolor='#0B1120')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    # Main timeline axis
    ax.plot([5, 95], [50, 50], color='#475569', linewidth=4, zorder=1)
    
    milestones = [
        ("1956", "Birth of AI", "Dartmouth Workshop\nTuring Test & Symbolic AI", 12, 1, '#38BDF8'),
        ("1986", "Backpropagation", "Rumelhart, Hinton & Williams\nMulti-layer Perceptrons", 32, -1, '#818CF8'),
        ("2012", "AlexNet / Deep Learning", "ImageNet breakthrough\nGPU acceleration era", 52, 1, '#34D399'),
        ("2017", "Transformer Architecture", "'Attention Is All You Need'\nSelf-attention mechanism", 72, -1, '#FBBF24'),
        ("2026", "Autonomous AI Agents", "Interactive Teaching Loops\nMultimodal Reasoning", 90, 1, '#F43F5E'),
    ]
    
    for year, title, desc, x_pos, direction, color in milestones:
        # Timeline Node
        ax.scatter([x_pos], [50], s=250, color=color, edgecolors='#FFFFFF', linewidth=3, zorder=3)
        
        # Stem
        y_card = 68 if direction == 1 else 32
        ax.plot([x_pos, x_pos], [50, y_card - (8 * direction)], color=color, linestyle=':', linewidth=2, zorder=2)
        
        # Card Box
        card_text = f"★ {year} — {title}\n{desc}"
        ax.text(x_pos, y_card, card_text, ha='center', va='center', fontsize=11, fontweight='bold', color='#F8FAFC',
                bbox=dict(boxstyle='round,pad=0.6', facecolor='#1E293B', edgecolor=color, linewidth=2))
        
    plt.savefig(output_path, dpi=100, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close()
    print(f"Generated Timeline slide at {output_path}")

if __name__ == "__main__":
    generate_math_slide()
    generate_code_slide()
    generate_biology_diagram_slide()
    generate_timeline_slide()
