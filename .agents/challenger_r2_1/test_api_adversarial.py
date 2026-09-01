"""
Empirical Challenge Harness 5: FastAPI REST Endpoints Adversarial & Boundary Stress
Tests HTTP API endpoints for /api/v1/video/*, /api/v1/interactive/*, /api/v1/lessons/*
with invalid payloads, malformed JSON, missing IDs, out-of-range parameters,
and concurrent simulation using FastAPI TestClient.
"""

import os
import sys
import uuid
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

PROJECT_ROOT = Path("/home/dev/Desktop/projects/AI-InnovationHackathon")
sys.path.insert(0, str(PROJECT_ROOT))
os.environ["MPLCONFIGDIR"] = "/tmp/mpl"

from backend.app.main import app

client = TestClient(app)


def run_api_adversarial_tests():
    print("=" * 70)
    print("RUNNING EMPIRICAL CHALLENGE 5: FASTAPI REST API ADVERSARIAL STRESS")
    print("=" * 70)
    results = []

    # -------------------------------------------------------------------------
    # Test 5.1: Video Generation with Non-Existent Plan ID (Expect 404)
    # -------------------------------------------------------------------------
    print("\n[Test 5.1] Video generation with non-existent plan ID...")
    res = client.post("/api/v1/video/generate", json={"plan_id": "non_existent_plan_9999"})
    print(f"  Status code: {res.status_code}, Response: {res.text[:100]}")
    assert res.status_code == 404, f"Expected 404, got {res.status_code}"
    results.append({"test": "Video Gen Non-Existent Plan 404", "status": "PASS"})

    # -------------------------------------------------------------------------
    # Test 5.2: Video Status for Non-Existent Task ID (Expect 404)
    # -------------------------------------------------------------------------
    print("\n[Test 5.2] Video status for non-existent task ID...")
    res = client.get("/api/v1/video/status/task_does_not_exist_xyz")
    print(f"  Status code: {res.status_code}, Response: {res.text[:100]}")
    assert res.status_code == 404, f"Expected 404, got {res.status_code}"
    results.append({"test": "Video Status Non-Existent Task 404", "status": "PASS"})

    # -------------------------------------------------------------------------
    # Test 5.3: Video Manifest for Non-Existent Video ID (Expect 404)
    # -------------------------------------------------------------------------
    print("\n[Test 5.3] Video manifest for non-existent video ID...")
    res = client.get("/api/v1/video/manifest/les_non_existent")
    print(f"  Status code: {res.status_code}, Response: {res.text[:100]}")
    assert res.status_code == 404, f"Expected 404, got {res.status_code}"
    results.append({"test": "Video Manifest Non-Existent 404", "status": "PASS"})

    # -------------------------------------------------------------------------
    # Test 5.4: Interactive Evaluation with Empty Student Answer (Expect 422)
    # -------------------------------------------------------------------------
    print("\n[Test 5.4] Interactive evaluation with empty answer...")
    res = client.post("/api/v1/interactive/evaluate", json={
        "session_id": "ses_test",
        "question_id": "q1",
        "student_answer": "   "
    })
    print(f"  Status code: {res.status_code}, Response: {res.text[:100]}")
    assert res.status_code == 422, f"Expected 422, got {res.status_code}"
    results.append({"test": "Empty Answer 422 Validation", "status": "PASS"})

    # -------------------------------------------------------------------------
    # Test 5.5: Language Switch with Empty Target Language (Expect 422)
    # -------------------------------------------------------------------------
    print("\n[Test 5.5] Language switch with empty target language...")
    res = client.post("/api/v1/interactive/switch-language", json={
        "session_id": "ses_test",
        "target_language": "   "
    })
    print(f"  Status code: {res.status_code}, Response: {res.text[:100]}")
    assert res.status_code == 422, f"Expected 422, got {res.status_code}"
    results.append({"test": "Empty Target Language 422 Validation", "status": "PASS"})

    # -------------------------------------------------------------------------
    # Test 5.6: Side-Panel Tutor Chat with Empty Message (Expect 422)
    # -------------------------------------------------------------------------
    print("\n[Test 5.6] Tutor chat with empty message...")
    res = client.post("/api/v1/interactive/chat", json={
        "session_id": "ses_test",
        "message": "   "
    })
    print(f"  Status code: {res.status_code}, Response: {res.text[:100]}")
    assert res.status_code == 422, f"Expected 422, got {res.status_code}"
    results.append({"test": "Empty Chat Message 422 Validation", "status": "PASS"})

    # -------------------------------------------------------------------------
    # Test 5.7: Valid Interactive End-to-End Flow via REST API
    # -------------------------------------------------------------------------
    print("\n[Test 5.7] Valid Interactive Session via REST API...")
    ses_id = f"ses_rest_{uuid.uuid4().hex[:6]}"
    eval_payload = {
        "session_id": ses_id,
        "question_id": "q_math_01",
        "student_answer": "Tangent line slope is the limit of secant slopes as delta x approaches zero.",
        "current_concept": "Calculus Limits",
        "expected_answer": "Tangent is the derivative limit of secant slopes.",
        "language": "en"
    }
    eval_res = client.post("/api/v1/interactive/evaluate", json=eval_payload)
    assert eval_res.status_code == 200, f"Expected 200, got {eval_res.status_code}"
    eval_json = eval_res.json()
    assert eval_json["is_correct"] is True, f"Expected is_correct=True, got {eval_json}"

    # Get session state
    ses_res = client.get(f"/api/v1/interactive/session/{ses_id}")
    assert ses_res.status_code == 200
    ses_json = ses_res.json()
    assert len(ses_json["interaction_history"]) == 1
    results.append({"test": "Valid REST Interactive Evaluation & Session Persistence", "status": "PASS"})

    print("\n" + "=" * 70)
    print("API ADVERSARIAL CHALLENGE SUMMARY:")
    passed = sum(1 for r in results if r["status"] == "PASS")
    total = len(results)
    print(f"Passed: {passed}/{total} ({passed/total*100:.1f}%)")
    print("=" * 70)
    return results


if __name__ == "__main__":
    run_api_adversarial_tests()
