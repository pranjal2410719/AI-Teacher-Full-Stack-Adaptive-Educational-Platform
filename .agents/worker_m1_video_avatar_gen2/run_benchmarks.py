"""
Empirical Performance Benchmark for Video Generation (Requirement R1).
Tests representative 5-minute (300s) and 10-minute (600s) workloads
verifying that total processing time is <= 20s per minute of final video.
"""

import os
import sys
import time
import asyncio
import subprocess
from pathlib import Path
from typing import List

# Ensure backend can be imported
sys.path.insert(0, "/home/dev/Desktop/projects/AI-InnovationHackathon")

from backend.app.config import settings
from backend.app.models.lesson_plan import (
    LessonPlan,
    LessonSegmentPlan,
    VisualSpec,
    VisualType,
    CheckpointQuestion,
    SegmentType,
)
from backend.app.models.video import VideoGenerationRequest
from backend.app.services.video_stitcher import video_stitcher
from backend.app.services.tts_service import tts_service


def create_representative_plan(plan_id: str, title: str, num_segments: int, target_total_sec: float) -> LessonPlan:
    """Creates a realistic multi-segment lesson plan with avatar intro/outro and diverse visual slides."""
    avatar_intro_dur = 30.0
    avatar_outro_dur = 30.0
    remaining_dur = target_total_sec - (avatar_intro_dur + avatar_outro_dur)
    num_slide_segments = num_segments - 2
    slide_dur = remaining_dur / max(1, num_slide_segments)

    # Realistic educational scripts scaled to target duration (~2.5 words per second)
    def make_script(base_text: str, duration_sec: float) -> str:
        words = base_text.split()
        target_words = int(duration_sec * 2.2)
        repeated = []
        while len(repeated) < target_words:
            repeated.extend(words)
        return " ".join(repeated[:target_words])

    modules: List[LessonSegmentPlan] = []

    # Segment 1: Avatar Intro
    modules.append(
        LessonSegmentPlan(
            segment_id=f"{plan_id}_seg_01",
            order=1,
            segment_type=SegmentType.AVATAR_INTRO,
            title="Course Introduction & Overview",
            duration_sec=int(avatar_intro_dur),
            script=make_script("Welcome students! Today we explore advanced concepts in computing, calculus, and biology.", avatar_intro_dur),
            visual_spec=VisualSpec(
                visual_type=VisualType.GENERAL_SLIDE,
                subject_domain="general",
                headline="Course Overview",
                bullet_points=["Course objectives and scope", "Fundamental theorems", "Practical applications"],
            ),
        )
    )

    # Slide Specs
    slide_specs = [
        (
            VisualType.MATH_EQUATION,
            "math",
            "Calculus Differential Calculus",
            VisualSpec(
                visual_type=VisualType.MATH_EQUATION,
                subject_domain="math",
                headline="Differential Calculus Formulation",
                latex_equations=[r"\frac{df}{dx} = \lim_{h \to 0} \frac{f(x+h) - f(x)}{h}", r"\int x^n dx = \frac{x^{n+1}}{n+1} + C"],
                bullet_points=["First principles derivative definition", "Polynomial power integration rule"],
            ),
        ),
        (
            VisualType.CODE_SNIPPET,
            "computer_science",
            "Algorithms Binary Search & Complexity",
            VisualSpec(
                visual_type=VisualType.CODE_SNIPPET,
                subject_domain="computer_science",
                headline="Logarithmic Divide and Conquer",
                code_language="python",
                code_content="def binary_search(arr, target):\n    low, high = 0, len(arr) - 1\n    while low <= high:\n        mid = (low + high) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            low = mid + 1\n        else:\n            high = mid - 1\n    return -1",
                bullet_points=["Requires sorted input array", "O(log n) time complexity", "O(1) space complexity"],
            ),
        ),
        (
            VisualType.DIAGRAM,
            "biology",
            "Cellular Morphology & Mitochondria",
            VisualSpec(
                visual_type=VisualType.DIAGRAM,
                subject_domain="biology",
                headline="Eukaryotic Organelle Function",
                bullet_points=["Mitochondria ATP energy synthesis", "Nucleus genetic transcription control"],
                callout_box="Mitochondria are the primary ATP synthesis powerhouses of the cell.",
            ),
        ),
        (
            VisualType.TIMELINE,
            "history",
            "Industrial Revolution Technological Evolution",
            VisualSpec(
                visual_type=VisualType.TIMELINE,
                subject_domain="history",
                headline="Historical Progression of Industry",
                timeline_events=[
                    {"year": "1769", "title": "Watt Steam Engine", "description": "Condenser steam engine patent."},
                    {"year": "1804", "title": "Steam Locomotive", "description": "Trevithick engine runs on iron rails."},
                    {"year": "1830", "title": "Liverpool Railway", "description": "First twin-track inter-city rail line."},
                ],
                bullet_points=["Transition from agrarian to mechanized industrial manufacturing."],
            ),
        ),
    ]

    for idx in range(num_slide_segments):
        spec_tuple = slide_specs[idx % len(slide_specs)]
        seg_num = idx + 2
        modules.append(
            LessonSegmentPlan(
                segment_id=f"{plan_id}_seg_{seg_num:02d}",
                order=seg_num,
                segment_type=SegmentType.VISUAL_CONCEPT,
                title=spec_tuple[2],
                duration_sec=int(slide_dur),
                script=make_script(f"Let us examine {spec_tuple[2]}. The analytical foundation relies on rigorous formulation and step-by-step reasoning.", slide_dur),
                visual_spec=spec_tuple[3],
                checkpoint_question=CheckpointQuestion(
                    question_id=f"q_{plan_id}_{seg_num}",
                    question_text=f"What is the key principle of {spec_tuple[2]}?",
                    prompt=f"What is the key principle of {spec_tuple[2]}?",
                    question_type="mcq",
                    options=["Principle A", "Principle B", "Principle C", "Principle D"],
                    correct_answer="Principle A",
                    explanation=f"Principle A is the core invariant of {spec_tuple[2]}.",
                    concept=spec_tuple[2],
                ) if idx % 2 == 0 else None,
            )
        )

    # Final Segment: Avatar Summary
    modules.append(
        LessonSegmentPlan(
            segment_id=f"{plan_id}_seg_{num_segments:02d}",
            order=num_segments,
            segment_type=SegmentType.AVATAR_SUMMARY,
            title="Lesson Synthesis & Core Takeaways",
            duration_sec=int(avatar_outro_dur),
            script=make_script("To summarize, we have covered limits, binary search algorithms, cellular structures, and industrial milestones. Excellent effort today!", avatar_outro_dur),
            visual_spec=VisualSpec(
                visual_type=VisualType.GENERAL_SLIDE,
                subject_domain="general",
                headline="Synthesis & Key Takeaways",
                bullet_points=["Review definitions and edge cases", "Complete the adaptive checkpoint quiz"],
            ),
        )
    )

    plan = LessonPlan(
        plan_id=plan_id,
        title=title,
        target_duration_sec=int(target_total_sec),
        total_actual_duration_sec=int(target_total_sec),
        level="intermediate",
        language="en",
        subject_domain="general",
        topic=title,
        modules=modules,
    )
    return plan


def verify_mp4_file(path: Path) -> dict:
    """Extracts duration, video codec, audio codec, and resolution using ffprobe."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration:stream=codec_name,width,height,r_frame_rate",
        "-of", "json",
        str(path),
    ]
    res = subprocess.check_output(cmd).decode()
    import json
    data = json.loads(res)
    duration = float(data["format"]["duration"])
    streams = data.get("streams", [])
    v_stream = next((s for s in streams if "width" in s and s["width"] is not None), {})
    a_stream = next((s for s in streams if s.get("codec_name") == "aac"), {})
    return {
        "duration": duration,
        "width": v_stream.get("width"),
        "height": v_stream.get("height"),
        "video_codec": v_stream.get("codec_name"),
        "audio_codec": a_stream.get("codec_name"),
        "fps": v_stream.get("r_frame_rate"),
        "size_bytes": path.stat().st_size,
    }


async def run_benchmark():
    print("=" * 80)
    print("APNIHELP R1 PERFORMANCE BENCHMARK: VIDEO GENERATION PIPELINE")
    print("Threshold: <= 20.0 seconds of processing per minute of final video length")
    print("=" * 80)

    workloads = [
        ("5-Minute Workload", "plan_bench_5min", "5-Minute Comprehensive STEM Masterclass", 6, 300.0, 100.0),
        ("10-Minute Workload", "plan_bench_10min", "10-Minute Full-Length University Lecture", 10, 600.0, 200.0),
    ]

    all_results = []

    for name, plan_id, title, num_segments, target_sec, sla_sec in workloads:
        print(f"\n>>> Starting Benchmark: {name}")
        print(f"    Target Duration: {target_sec}s ({target_sec/60:.1f} min)")
        print(f"    R1 SLA Limit: <= {sla_sec}s ({target_sec/60:.1f} min * 20s/min)")
        print(f"    Number of Segments: {num_segments} (Avatar Intro, Slides, Avatar Outro)")

        plan = create_representative_plan(plan_id, title, num_segments, target_sec)
        req = VideoGenerationRequest(plan_id=plan.plan_id, resolution="720p")

        t0 = time.perf_counter()
        manifest, video_path = await video_stitcher.generate_lesson_video(
            plan=plan,
            request=req,
            task_id=f"task_{plan_id}",
        )
        elapsed = time.perf_counter() - t0

        probe = verify_mp4_file(video_path)
        actual_dur = probe["duration"]
        rate = elapsed / (actual_dur / 60.0)
        safety_margin = ((sla_sec - elapsed) / sla_sec) * 100.0
        passed = elapsed <= sla_sec and rate <= 20.0

        res = {
            "name": name,
            "target_sec": target_sec,
            "actual_dur": round(actual_dur, 2),
            "elapsed_sec": round(elapsed, 2),
            "sla_sec": sla_sec,
            "rate_sec_per_min": round(rate, 2),
            "safety_margin_pct": round(safety_margin, 1),
            "passed": passed,
            "video_path": str(video_path),
            "size_mb": round(probe["size_bytes"] / (1024 * 1024), 2),
            "resolution": f"{probe['width']}x{probe['height']}",
            "codecs": f"{probe['video_codec']}/{probe['audio_codec']}",
        }
        all_results.append(res)

        print(f"    RESULT for {name}:")
        print(f"    - Actual Video Duration: {res['actual_dur']}s ({res['actual_dur']/60:.2f} min)")
        print(f"    - Total Processing Time: {res['elapsed_sec']}s")
        print(f"    - Rate: {res['rate_sec_per_min']}s per minute of output video")
        print(f"    - SLA Limit: {sla_sec}s (Safety Margin: {res['safety_margin_pct']}%)")
        print(f"    - Video File: {res['video_path']} ({res['size_mb']} MB, {res['resolution']}, {res['codecs']})")
        print(f"    - Status: {'PASSED [OK]' if passed else 'FAILED [FAIL]'}")

    print("\n" + "=" * 80)
    print("BENCHMARK SUMMARY TABLE")
    print("=" * 80)
    print(f"{'Workload':<20} | {'Video Dur':<10} | {'Processing':<12} | {'Rate (s/min)':<14} | {'Limit (s)':<10} | {'Margin':<8} | {'Status'}")
    print("-" * 80)
    for r in all_results:
        print(f"{r['name']:<20} | {r['actual_dur']:>8.1f}s | {r['elapsed_sec']:>10.2f}s | {r['rate_sec_per_min']:>12.2f} | {r['sla_sec']:>8.1f}s | {r['safety_margin_pct']:>6.1f}% | {'PASSED' if r['passed'] else 'FAILED'}")
    print("=" * 80)

    # Save benchmark results to JSON in agent directory
    out_json = Path("/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/worker_m1_video_avatar_gen2/benchmark_results.json")
    import json
    out_json.write_text(json.dumps(all_results, indent=2))
    print(f"Saved benchmark results to {out_json}")

    for r in all_results:
        assert r["passed"], f"Workload {r['name']} failed R1 SLA: {r['elapsed_sec']}s > {r['sla_sec']}s"


if __name__ == "__main__":
    asyncio.run(run_benchmark())
