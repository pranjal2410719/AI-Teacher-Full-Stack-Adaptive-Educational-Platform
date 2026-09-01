"""
Empirical Challenge Harness 2: Visual Slide & Hindi Devanagari Rendering
Tests rendering of Math LaTeX, CS Pygments IDE, Biology diagrams, History timelines,
and General slides with English & Hindi Devanagari text, plus MP4 video clip synthesis.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path("/home/dev/Desktop/projects/AI-InnovationHackathon")
sys.path.insert(0, str(PROJECT_ROOT))
os.environ["MPLCONFIGDIR"] = "/tmp/mpl"

from backend.app.models.lesson_plan import VisualSpec, VisualType
from backend.app.services.slide_render_service import SlideRenderService
from backend.app.services.tts_service import TTSService

OUTPUT_DIR = Path("/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/challenger_r2_1/test_outputs/slides")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def run_slide_tests():
    slide_service = SlideRenderService(slides_dir=OUTPUT_DIR)
    tts_service = TTSService(audio_dir=OUTPUT_DIR / "audio")
    results = []

    print("=" * 70)
    print("RUNNING EMPIRICAL CHALLENGE 2: VISUAL SLIDES & HINDI RENDERING")
    print("=" * 70)

    test_specs = [
        {
            "name": "Math Slide with LaTeX & Devanagari Hindi Text",
            "title": "कलन और सीमाएं: मूलभूत परिभाषाएं",
            "spec": VisualSpec(
                visual_type=VisualType.MATH_EQUATION,
                subject_domain="Mathematics",
                headline="कलन के आधारभूत सूत्र (Calculus Foundations)",
                latex_equations=[
                    r"\lim_{x \to 0} \frac{\sin(x)}{x} = 1",
                    r"f'(x) = \lim_{\Delta x \to 0} \frac{f(x+\Delta x) - f(x)}{\Delta x}",
                    r"\int_a^b f(x)\,dx = F(b) - F(a)"
                ],
                bullet_points=[
                    "सीमा (Limit): जब चर x किसी विशिष्ट मान c की ओर अग्रसर होता है।",
                    "सीकेंट रेखा (Secant Line): दो बिंदुओं को मिलाने वाली रेखा की ढलान।",
                    "स्पर्शरेखा (Tangent Line): तात्कालिक परिवर्तन दर (Instantaneous Rate of Change)।"
                ],
                callout_box="कलन परिवर्तन और गतिकी का गणितीय अध्ययन है।"
            )
        },
        {
            "name": "Computer Science Slide with Code & Hindi Comments",
            "title": "बाइनरी सर्च एल्गोरिथम (Binary Search)",
            "spec": VisualSpec(
                visual_type=VisualType.CODE_SNIPPET,
                subject_domain="Computer Science",
                headline="Binary Search Algorithm Implementation",
                code_language="python",
                code_content=(
                    "# बाइनरी सर्च: क्रमबद्ध सूची में O(log n) खोज\n"
                    "def binary_search(arr: list[int], target: int) -> int:\n"
                    "    low, high = 0, len(arr) - 1\n"
                    "    while low <= high:\n"
                    "        mid = (low + high) // 2  # मध्य बिंदु की गणना\n"
                    "        if arr[mid] == target:\n"
                    "            return mid  # लक्ष्य मिल गया\n"
                    "        elif arr[mid] < target:\n"
                    "            low = mid + 1  # दाएँ भाग में खोजें\n"
                    "        else:\n"
                    "            high = mid - 1  # बाएँ भाग में खोजें\n"
                    "    return -1  # तत्व उपस्थित नहीं है"
                ),
                bullet_points=[
                    "इनपुट ऐरे अनिवार्य रूप से आरोही क्रम (Ascending Order) में होना चाहिए।",
                    "प्रत्येक तुलना के बाद खोज का दायरा आधा (50%) हो जाता है।",
                    "समय जटिलता: सर्वश्रेष्ठ O(1), औसत एवं निकृष्टतम O(log n)।"
                ]
            )
        },
        {
            "name": "Biology Cellular Diagram with Hindi Callouts",
            "title": "कोशिका संरचना एवं कार्यप्रणाली",
            "spec": VisualSpec(
                visual_type=VisualType.DIAGRAM,
                subject_domain="Biology",
                headline="Cellular Morphology & Organelle Mechanisms",
                bullet_points=[
                    "माइटोकॉन्ड्रिया: कोशिकीय श्वसन द्वारा ATP ऊर्जा का संश्लेषण।",
                    "केंद्रक (Nucleus): आनुवंशिक DNA सामग्री का नियंत्रण केंद्र।",
                    "प्लाज्मा झिल्ली (Plasma Membrane): चयनात्मक पारगम्यता (Selective Permeability)।",
                    "राइबोसोम: प्रोटीन संश्लेषण के प्राथमिक घटक।"
                ]
            )
        },
        {
            "name": "History Chronological Timeline with Hindi Milestones",
            "title": "औद्योगिक क्रांति के प्रमुख मील के पत्थर",
            "spec": VisualSpec(
                visual_type=VisualType.TIMELINE,
                subject_domain="History",
                headline="Historical Milestones of Industrial Revolution",
                timeline_events=[
                    {"year": "1769", "title": "स्टीम इंजन", "description": "जेम्स वाट द्वारा कंडेनसर स्टीम इंजन का पेटेंट।"},
                    {"year": "1784", "title": "पुडलिंग प्रक्रिया", "description": "हेनरी कॉर्ट द्वारा लोहा प्रगलन क्रांति।"},
                    {"year": "1804", "title": "स्टीम लोकोमोटिव", "description": "रिचर्ड ट्रेविथिक का प्रथम रेल इंजन।"},
                    {"year": "1830", "title": "लिवरपूल रेलवे", "description": "प्रथम अंतर-शहरी यात्री रेलमार्ग का उद्घाटन।"},
                    {"year": "1851", "title": "ग्रेट एग्जिबिशन", "description": "क्रिस्टल पैलेस में वैश्विक औद्योगिक प्रदर्शनी।"}
                ],
                bullet_points=[
                    "हस्तशिल्प और कृषि आधारित अर्थव्यवस्था का औद्योगीकरण में रूपांतरण।",
                    "कोयला खनन और रेलवे नेटवर्क का तीव्र विस्तार।"
                ]
            )
        },
        {
            "name": "Extreme Boundary: Super Long Text & Special Characters",
            "title": "Extreme Boundary & Unicode Stress: <script>alert('test')</script> $&%*#",
            "spec": VisualSpec(
                visual_type=VisualType.GENERAL_SLIDE,
                subject_domain="Adversarial Testing",
                headline="Extreme Text Boundary & Malformed Inputs Handling 🚀🔥💯",
                bullet_points=[
                    "A" * 300,  # 300 character single line
                    "Special characters: <>&\"'\\/|;:!@#$%^&*()_+=-~`",
                    "Devanagari conjuncts: क्ष, त्र, ज्ञ, श्र, द्ध, ष्ट्र, द्व, ङ्क, ङ्ख",
                    "Math formula with missing delimiters: lim x->0 sin(x)/x = 1 & sqrt(a^2 + b^2)",
                ],
                callout_box="Boundary validation test: " + "Unicode & long text resilience. " * 5
            )
        }
    ]

    for idx, tc in enumerate(test_specs, 1):
        print(f"\n[Test 2.{idx}] Rendering {tc['name']}...")
        try:
            # 1. Render Slide Image
            img = slide_service.render_slide_image(tc["spec"], tc["title"])
            assert isinstance(img, Image.Image), "Result is not a PIL Image"
            assert img.size == (1280, 720), f"Incorrect dimensions: {img.size} (expected 1280x720)"
            assert img.mode == "RGB", f"Incorrect image mode: {img.mode} (expected RGB)"

            img_path = OUTPUT_DIR / f"slide_test_{idx}.png"
            img.save(str(img_path))
            assert img_path.exists() and os.path.getsize(img_path) > 10000

            # 2. Render Slide Video with Audio Sync
            # Synthesize 3-second narration
            narration_text = f"यह व्याख्यान {tc['title']} के बारे में है। कृपया ध्यान से समझें।"
            audio_path, duration = tts_service.synthesize_sync(narration_text, language="hi")
            video_out_path = OUTPUT_DIR / f"slide_clip_test_{idx}.mp4"

            slide_service.render_slide_video(
                spec=tc["spec"],
                title=tc["title"],
                audio_path=audio_path,
                output_video_path=video_out_path,
                duration_sec=duration
            )

            assert video_out_path.exists(), f"Video clip not created: {video_out_path}"
            assert os.path.getsize(video_out_path) > 10000, "Video clip is too small"

            # 3. FFprobe Verification of Video Clip
            probe_cmd = [
                slide_service.ffprobe_path,
                "-v", "error",
                "-show_entries", "format=duration,size:stream=codec_name,width,height,r_frame_rate,pix_fmt",
                "-of", "json",
                str(video_out_path)
            ]
            probe_proc = subprocess.run(probe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            probe_data = json.loads(probe_proc.stdout)

            v_stream = next((s for s in probe_data["streams"] if s.get("width")), None)
            a_stream = next((s for s in probe_data["streams"] if s.get("codec_name") in ["aac", "mp3"]), None)

            assert v_stream is not None, "No video stream found in MP4"
            assert v_stream["width"] == 1280 and v_stream["height"] == 720, f"Bad resolution: {v_stream['width']}x{v_stream['height']}"
            assert v_stream["pix_fmt"] == "yuv420p", f"Non-web pix_fmt: {v_stream['pix_fmt']}"
            assert a_stream is not None, "No audio stream found in MP4"

            actual_dur = float(probe_data["format"]["duration"])
            print(f"  ✓ Success: Image={img_path.name} ({img.size}), Video={video_out_path.name} ({v_stream['width']}x{v_stream['height']} @ {v_stream['r_frame_rate']}fps, dur={actual_dur:.2f}s, pix={v_stream['pix_fmt']})")
            results.append({
                "test": tc["name"],
                "status": "PASS",
                "image_path": str(img_path),
                "video_path": str(video_out_path),
                "duration": actual_dur,
                "resolution": f"{v_stream['width']}x{v_stream['height']}",
            })
        except Exception as e:
            print(f"  ✗ FAILED: {e}")
            results.append({
                "test": tc["name"],
                "status": "FAIL",
                "error": str(e)
            })

    print("\n" + "=" * 70)
    print("SLIDE & HINDI RENDERING CHALLENGE SUMMARY:")
    passed = sum(1 for r in results if r["status"] == "PASS")
    total = len(results)
    print(f"Passed: {passed}/{total} ({passed/total*100:.1f}%)")
    print("=" * 70)
    return results


if __name__ == "__main__":
    run_slide_tests()
