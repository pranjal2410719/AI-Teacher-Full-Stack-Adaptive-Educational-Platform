#!/usr/bin/env python3
"""
AI Teacher 4-Tier E2E Test Suite Runner.
Executes test cases across all tiers, validates responses, and generates structured JSON and terminal reports.
"""

import os
import sys
import time
import json
import argparse
import unittest
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TESTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
os.environ["PYTHONPATH"] = f"{ROOT_DIR}:{os.environ.get('PYTHONPATH', '')}"

# ANSI Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

TIER_MAP = {
    1: ("tier1_feature_coverage", "Tier 1: Feature Coverage (R1-R5 Unit & Component Level)"),
    2: ("tier2_boundary_corner", "Tier 2: Boundary & Corner Cases (Corrupt/Empty/Unicode/Injection)"),
    3: ("tier3_cross_feature", "Tier 3: Cross-Feature Combinations (Multi-Service Pipelines)"),
    4: ("tier4_real_world_scenarios", "Tier 4: Real-World Persona Scenarios (Math/CS/Bio/History)"),
    5: ("tier5_adversarial_hardening", "Tier 5: Adversarial Coverage Hardening (Fuzzing/Concurrency/Polyglot)")
}

class JsonReportCollector:
    """Collects structured test outcome metadata for JSON reporting."""
    def __init__(self):
        self.results = []
        self.start_time = time.time()
        self.end_time = None

    def pytest_runtest_logreport(self, report):
        if report.when == "call":
            outcome = report.outcome
            nodeid = report.nodeid
            duration = report.duration
            error_msg = None
            if report.failed:
                error_msg = str(report.longrepr)

            # Determine tier from nodeid
            tier_num = 0
            for t_num, (t_dir, _) in TIER_MAP.items():
                if t_dir in nodeid:
                    tier_num = t_num
                    break

            self.results.append({
                "test_id": nodeid,
                "tier": tier_num,
                "status": outcome.upper(),
                "duration_sec": round(duration, 4),
                "error": error_msg
            })

def run_tests(tier: int = None, base_url: str = None, json_report_path: str = None, verbose: bool = True) -> int:
    """Executes pytest suite and outputs structured summary."""
    if base_url:
        os.environ["LIVE_BACKEND_URL"] = base_url

    print(f"\n{BOLD}{CYAN}{'='*80}{RESET}")
    print(f"{BOLD}{CYAN} AI TEACHER 4-TIER E2E TEST SUITE RUNNER {RESET}")
    print(f"{BOLD}{CYAN}{'='*80}{RESET}")
    if base_url:
        print(f"{YELLOW}Target Backend Mode: Live Server ({base_url}){RESET}")
    else:
        print(f"{GREEN}Target Backend Mode: In-Process FastAPI TestClient{RESET}")

    selected_dirs = []
    if tier and tier in TIER_MAP:
        t_dir, t_name = TIER_MAP[tier]
        selected_dirs.append(os.path.join(TESTS_DIR, t_dir))
        print(f"{BOLD}Executing: {t_name}{RESET}\n")
    else:
        for t_num, (t_dir, t_name) in TIER_MAP.items():
            selected_dirs.append(os.path.join(TESTS_DIR, t_dir))
        print(f"{BOLD}Executing All 4 Tiers (Feature, Boundary, Combinations, Real-World){RESET}\n")

    collector = JsonReportCollector()
    
    pytest_args = [
        "-v" if verbose else "-q",
        "--tb=short"
    ] + selected_dirs

    exit_code = pytest.main(pytest_args, plugins=[collector])
    collector.end_time = time.time()

    # Generate Summary Table
    total_tests = len(collector.results)
    passed_tests = sum(1 for r in collector.results if r["status"] == "PASSED")
    failed_tests = sum(1 for r in collector.results if r["status"] == "FAILED")
    skipped_tests = sum(1 for r in collector.results if r["status"] == "SKIPPED")
    total_dur = round(collector.end_time - collector.start_time, 2)

    print(f"\n{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}TEST EXECUTION SUMMARY{RESET}")
    print(f"{BOLD}{'-'*80}{RESET}")
    
    for t_num, (t_dir, t_name) in TIER_MAP.items():
        tier_results = [r for r in collector.results if r["tier"] == t_num]
        if tier_results:
            t_pass = sum(1 for r in tier_results if r["status"] == "PASSED")
            t_fail = sum(1 for r in tier_results if r["status"] == "FAILED")
            color = GREEN if t_fail == 0 else RED
            print(f"{color}{t_name}: {t_pass}/{len(tier_results)} PASSED{RESET}")

    print(f"{BOLD}{'-'*80}{RESET}")
    status_color = GREEN if failed_tests == 0 else RED
    print(f"{status_color}{BOLD}TOTAL: {total_tests} Tests | {passed_tests} PASSED | {failed_tests} FAILED | {skipped_tests} SKIPPED ({total_dur}s){RESET}")
    print(f"{BOLD}{'='*80}{RESET}\n")

    # Write JSON report if requested
    if json_report_path:
        report_data = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "skipped": skipped_tests,
            "duration_sec": total_dur,
            "all_passed": failed_tests == 0,
            "results": collector.results
        }
        with open(json_report_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)
        print(f"{CYAN}Structured JSON test report written to: {json_report_path}{RESET}\n")

    return 0 if failed_tests == 0 else 1

def main():
    parser = argparse.ArgumentParser(description="AI Teacher 5-Tier E2E Test Suite Runner")
    parser.add_argument("--tier", type=int, choices=[1, 2, 3, 4, 5], help="Run a specific test tier (1, 2, 3, 4, or 5)")
    parser.add_argument("--base-url", type=str, default=None, help="Live FastAPI backend base URL (e.g. http://localhost:8000)")
    parser.add_argument("--json-report", type=str, default=None, help="Path to write structured JSON test results")
    parser.add_argument("--quiet", action="store_true", help="Run with minimal output")

    args = parser.parse_args()
    code = run_tests(
        tier=args.tier,
        base_url=args.base_url,
        json_report_path=args.json_report,
        verbose=not args.quiet
    )
    sys.exit(code)

if __name__ == "__main__":
    main()
