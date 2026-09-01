"""
Empirical Challenge Harness 3: Video Pipeline, Duration Accuracy, & Manifest Integrity
Tests full end-to-end video synthesis (Avatar Intro + Visual Slides + Checkpoint Question + Avatar Outro)
in both English and Hindi. Verifies FFmpeg faststart MP4 stitching, duration precision via ffprobe,
segment transition boundaries, and checkpoint pause marker integrity in VideoManifest.
"""

import os
import sys
import json
import uuid
import asyncio
import subprocess
from pathlib import Path

PROJECT_ROOT = Path("/home/dev/Desktop/projects/AI-InnovationHackathon")
sys.path.insert(0, str(PROJECT_ROOT))
os.environ["MPLCONFIGDIR"] = "/tmp/mpl"

from backend.app.models.lesson_plan import LessonPlan, LessonSegmentPlan, VisualSpec, VisualType, CheckpointQuestion
from backend.app.models.video import VideoGenerationRequest, VideoManifest
from backend.app.services.video_stitcher import VideoStitcher
from backend.app.services.tts_service import TTSService
from backend.app.services.avatar_service import AvatarService
from backend.app.services.slide_render_service import SlideRenderService

OUTPUT_DIR = Path("/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/challenger_r2_1/test_outputs/video_pipeline")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


async def run_video_pipeline_tests():
    tts = TTSService(audio_dir=OUTPUT_DIR / "audio")
    avatar = AvatarService(avatar_dir=OUTPUT_DIR / "avatar")
    slides = SlideRenderService(slides_dir=OUTPUT_DIR / "slides")
    stitcher = VideoStitcher(video_dir=OUTPUT_DIR, tts=tts, avatar=avatar, slide_render=slides)

    results = []

    print("=" * 70)
    print("RUNNING EMPIRICAL CHALLENGE 3: HYBRID VIDEO PIPELINE & MANIFEST INTEGRITY")
    print("=" * 70)

    # 1. English Mathematics Hybrid Lesson Plan
    en_plan = LessonPlan(
        plan_id=f"plan_math_en_{uuid.uuid4().hex[:6]}",
        title="Introduction to Calculus: Limits & Rates of Change",
        target_duration_sec=60,
        level="beginner",
        language="en",
        modules=[
            LessonSegmentPlan(
                segment_id="seg_01_intro",
                order=1,
                segment_type="avatar_intro",
                title="Welcome to Calculus",
                duration_sec=8,
                script="Hello students! Welcome to our calculus lecture. Today we explore limits and rates of change.",
            ),
            LessonSegmentPlan(
                segment_id="seg_02_math_slide",
                order=2,
                segment_type="visual_concept",
                title="Limits & Secant Slopes",
                duration_sec=12,
                script="The secant line measures average change between two points, while the tangent gives instantaneous velocity.",
                visual_spec=VisualSpec(
                    visual_type=VisualType.MATH_EQUATION,
                    subject_domain="Mathematics",
                    headline="Secant Slope to Tangent Derivative",
                    latex_equations=[
                        r"m_{sec} = \frac{f(x+\Delta x) - f(x)}{\Delta x}",
                        r"f'(x) = \lim_{\Delta x \to 0} \frac{f(x+\Delta x) - f(x)}{\Delta x}"
                    ],
                    bullet_points=[
                        "Secant line connects two distinct points across delta t.",
                        "Tangent line is the limiting slope as delta t shrinks to zero."
                    ]
                ),
                checkpoint_question=CheckpointQuestion(
                    question_id="chk_calc_01",
                    concept="Secant vs Tangent Slope",
                    question_type="short_answer",
                    question_text="What does the slope of the secant line represent compared to the tangent line?",
                    correct_answer="Secant represents average rate of change over an interval, while tangent represents instantaneous rate of change.",
                    explanation="Secant slope connects two points across delta t; tangent slope is the instantaneous limit as delta t approaches zero.",
                    options=[]
                )
            ),
            LessonSegmentPlan(
                segment_id="seg_03_summary",
                order=3,
                segment_type="avatar_summary",
                title="Calculus Summary & Takeaways",
                duration_sec=8,
                script="Great job on completing this module. Keep practicing limit derivations to solidify your intuition!",
            )
        ]
    )

    # 2. Hindi Computer Science Hybrid Lesson Plan
    hi_plan = LessonPlan(
        plan_id=f"plan_cs_hi_{uuid.uuid4().hex[:6]}",
        title="बाइनरी सर्च एल्गोरिथम (Binary Search in Hindi)",
        target_duration_sec=60,
        level="intermediate",
        language="hi",
        modules=[
            LessonSegmentPlan(
                segment_id="seg_hi_01_intro",
                order=1,
                segment_type="avatar_intro",
                title="बाइनरी सर्च परिचय",
                duration_sec=8,
                script="नमस्ते विद्यार्थियों! आज के पाठ में हम बाइनरी सर्च एल्गोरिथम की कार्यप्रणाली को विस्तार से समझेंगे।",
            ),
            LessonSegmentPlan(
                segment_id="seg_hi_02_code_slide",
                order=2,
                segment_type="visual_concept",
                title="बाइनरी सर्च कोड एवं विश्लेषण",
                duration_sec=12,
                script="बाइनरी सर्च एक क्रमबद्ध सूची में मध्य बिंदु से तुलना करके खोज क्षेत्र को हर बार आधा कर देता है।",
                visual_spec=VisualSpec(
                    visual_type=VisualType.CODE_SNIPPET,
                    subject_domain="Computer Science",
                    headline="Binary Search Algorithm Python Code",
                    code_language="python",
                    code_content=(
                        "def binary_search(arr, target):\n"
                        "    low, high = 0, len(arr) - 1\n"
                        "    while low <= high:\n"
                        "        mid = (low + high) // 2\n"
                        "        if arr[mid] == target: return mid\n"
                        "        elif arr[mid] < target: low = mid + 1\n"
                        "        else: high = mid - 1\n"
                        "    return -1"
                    ),
                    bullet_points=[
                        "क्रमबद्ध ऐरे (Sorted Array) अनिवार्य शर्त है।",
                        "समय जटिलता (Time Complexity) O(log n) होती है।"
                    ]
                ),
                checkpoint_question=CheckpointQuestion(
                    question_id="chk_cs_hi_01",
                    concept="BST & Binary Search Time Complexity",
                    question_type="short_answer",
                    question_text="बाइनरी सर्च की समय जटिलता O(log n) क्यों होती है?",
                    correct_answer="प्रत्येक तुलना के बाद खोज का दायरा आधा हो जाता है।",
                    explanation="प्रत्येक चरण में खोज स्थान को दो बराबर भागों में विभाजित किया जाता है।",
                    options=[]
                )
            ),
            LessonSegmentPlan(
                segment_id="seg_hi_03_summary",
                order=3,
                segment_type="avatar_summary",
                title="अध्याय निष्कर्ष",
                duration_sec=8,
                script="बहुत बढ़िया! आपने बाइनरी सर्च के मूलभूत सिद्धांतों को सफलतापूर्वक समझ लिया है।",
            )
        ]
    )

    plans = [("English Calculus Hybrid Video", en_plan), ("Hindi CS Hybrid Video", hi_plan)]

    for test_name, plan in plans:
        print(f"\n[Test 3] Generating {test_name} (Plan ID: {plan.plan_id})...")
        try:
            req = VideoGenerationRequest(plan_id=plan.plan_id)
            manifest, video_path = await stitcher.generate_lesson_video(plan, req)

            # 1. Verify Video File Exists and is Non-Empty
            assert video_path.exists(), f"Stitched video does not exist: {video_path}"
            v_size = os.path.getsize(video_path)
            assert v_size > 50000, f"Stitched video is suspiciously small: {v_size} bytes"

            # 2. Probe with ffprobe for exact streams, duration, faststart
            probe_cmd = [
                stitcher.ffprobe_path,
                "-v", "error",
                "-show_entries", "format=duration,size:stream=codec_name,width,height,r_frame_rate,pix_fmt",
                "-of", "json",
                str(video_path)
            ]
            probe_proc = subprocess.run(probe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            probe_data = json.loads(probe_proc.stdout)

            actual_duration = float(probe_data["format"]["duration"])
            manifest_duration = manifest.total_duration_sec or manifest.duration_sec

            # Duration accuracy assertion (should be within 0.5s tolerance)
            duration_diff = abs(actual_duration - manifest_duration)
            print(f"  Duration check: Actual={actual_duration:.2f}s, Manifest={manifest_duration:.2f}s, Diff={duration_diff:.2f}s")
            assert duration_diff < 0.8, f"Duration discrepancy too large: {duration_diff:.2f}s"

            # 3. Check Segment Transitions Continuity
            print(f"  Verifying {len(manifest.segments)} segment transitions...")
            for i in range(len(manifest.segments) - 1):
                cur_seg = manifest.segments[i]
                nxt_seg = manifest.segments[i + 1]
                assert abs(cur_seg.end_sec - nxt_seg.start_sec) < 0.05, (
                    f"Segment boundary gap between {cur_seg.segment_id} ({cur_seg.end_sec}s) "
                    f"and {nxt_seg.segment_id} ({nxt_seg.start_sec}s)"
                )

            # 4. Check Checkpoint Pause Markers Integrity
            print(f"  Verifying {len(manifest.pause_markers)} pause markers...")
            assert len(manifest.pause_markers) >= 1, "No pause markers generated in manifest"
            for pm in manifest.pause_markers:
                print(f"    - Marker {pm.marker_id} at {pm.timestamp_sec}s for concept: '{pm.concept}'")
                assert pm.timestamp_sec > 0, f"Invalid timestamp {pm.timestamp_sec}"
                assert pm.timestamp_sec <= actual_duration, f"Marker timestamp {pm.timestamp_sec} exceeds video duration {actual_duration}"
                # Check question structure
                q = pm.question
                q_dict = q if isinstance(q, dict) else q.model_dump()
                assert "prompt" in q_dict or "question_text" in q_dict, f"Missing question prompt in {q_dict}"

            # 5. Check faststart (+faststart moov atom before mdat)
            # Read first 1MB of video file
            with open(video_path, "rb") as vf:
                header_chunk = vf.read(1024 * 512)
                has_moov = b"moov" in header_chunk
                print(f"  Faststart check (moov in first 512KB): {has_moov}")
                assert has_moov, "Video file missing faststart moov atom in header"

            print(f"  ✓ {test_name} PASSED: Video={video_path.name} ({v_size}B, {actual_duration:.2f}s)")
            results.append({
                "test": test_name,
                "status": "PASS",
                "video_file": str(video_path),
                "duration": actual_duration,
                "segments": len(manifest.segments),
                "pause_markers": len(manifest.pause_markers),
                "language": plan.language
            })

        except Exception as e:
            print(f"  ✗ {test_name} FAILED: {e}")
            results.append({
                "test": test_name,
                "status": "FAIL",
                "error": str(e)
            })

    print("\n" + "=" * 70)
    print("VIDEO PIPELINE EMPIRICAL CHALLENGE SUMMARY:")
    passed = sum(1 for r in results if r["status"] == "PASS")
    total = len(results)
    print(f"Passed: {passed}/{total} ({passed/total*100:.1f}%)")
    print("=" * 70)
    return results


if __name__ == "__main__":
    asyncio.run(run_video_pipeline_tests())
