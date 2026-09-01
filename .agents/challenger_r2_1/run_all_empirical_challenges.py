"""
Master Empirical Challenge Suite Runner
Executes all 4 empirical challenge suites, aggregates metrics, verifies edge cases,
and writes structured validation results.
"""

import os
import sys
import json
import time
import asyncio
from pathlib import Path

PROJECT_ROOT = Path("/home/dev/Desktop/projects/AI-InnovationHackathon")
sys.path.insert(0, str(PROJECT_ROOT))
os.environ["MPLCONFIGDIR"] = "/tmp/mpl"

import test_multilingual_tts
import test_slide_devanagari
import test_video_pipeline_manifest
import test_interaction_language_switch
import test_api_adversarial


async def main():
    start_time = time.time()
    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "agent": "challenger_r2_1",
        "suites": {},
        "summary": {}
    }

    print("\n" + "#" * 80)
    print("STARTING FULL EMPIRICAL CHALLENGE SUITE (challenger_r2_1)")
    print("#" * 80 + "\n")

    # Suite 1: TTS
    t0 = time.time()
    tts_results = await test_multilingual_tts.run_tts_tests()
    report["suites"]["tts_synthesis"] = {
        "results": tts_results,
        "elapsed_sec": round(time.time() - t0, 2),
        "total": len(tts_results),
        "passed": sum(1 for r in tts_results if r["status"] == "PASS")
    }

    # Suite 2: Visual Slides & Devanagari
    t0 = time.time()
    slide_results = test_slide_devanagari.run_slide_tests()
    report["suites"]["visual_slides_hindi"] = {
        "results": slide_results,
        "elapsed_sec": round(time.time() - t0, 2),
        "total": len(slide_results),
        "passed": sum(1 for r in slide_results if r["status"] == "PASS")
    }

    # Suite 3: Video Pipeline & Manifest
    t0 = time.time()
    video_results = await test_video_pipeline_manifest.run_video_pipeline_tests()
    report["suites"]["video_pipeline_manifest"] = {
        "results": video_results,
        "elapsed_sec": round(time.time() - t0, 2),
        "total": len(video_results),
        "passed": sum(1 for r in video_results if r["status"] == "PASS")
    }

    # Suite 4: Interactive Loop & Language Switching
    t0 = time.time()
    inter_results = test_interaction_language_switch.run_interaction_tests()
    report["suites"]["interaction_language_switch"] = {
        "results": inter_results,
        "elapsed_sec": round(time.time() - t0, 2),
        "total": len(inter_results),
        "passed": sum(1 for r in inter_results if r["status"] == "PASS")
    }

    # Suite 5: REST API Adversarial Stress
    t0 = time.time()
    api_results = test_api_adversarial.run_api_adversarial_tests()
    report["suites"]["api_adversarial_stress"] = {
        "results": api_results,
        "elapsed_sec": round(time.time() - t0, 2),
        "total": len(api_results),
        "passed": sum(1 for r in api_results if r["status"] == "PASS")
    }

    # Compute Global Summary
    total_tests = sum(s["total"] for s in report["suites"].values())
    total_passed = sum(s["passed"] for s in report["suites"].values())
    total_failed = total_tests - total_passed
    total_elapsed = round(time.time() - start_time, 2)

    report["summary"] = {
        "total_tests": total_tests,
        "total_passed": total_passed,
        "total_failed": total_failed,
        "pass_rate_percent": round((total_passed / total_tests) * 100, 2) if total_tests > 0 else 0,
        "total_elapsed_sec": total_elapsed,
        "verdict": "APPROVE" if total_failed == 0 else "REQUEST_CHANGES"
    }

    print("\n" + "#" * 80)
    print(f"ALL EMPIRICAL CHALLENGES COMPLETE in {total_elapsed}s")
    print(f"Total Tests Executed: {total_tests}")
    print(f"Passed: {total_passed} | Failed: {total_failed} ({report['summary']['pass_rate_percent']}%)")
    print(f"Final Verdict: {report['summary']['verdict']}")
    print("#" * 80 + "\n")

    # Save to JSON
    out_json = Path("/home/dev/Desktop/projects/AI-InnovationHackathon/.agents/challenger_r2_1/test_outputs/summary_results.json")
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, indent=2))
    print(f"Saved test metrics to {out_json}")


if __name__ == "__main__":
    asyncio.run(main())
