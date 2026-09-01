"""
Tier 5 Adversarial Coverage Hardening: Concurrency and Race Resilience.
Tests parallel generation, simultaneous evaluations, and concurrent profile writes.
"""

import pytest
import concurrent.futures
from tests_e2e.harness import E2ETestHarness

@pytest.fixture
def harness():
    return E2ETestHarness()

class TestAdversarialConcurrencyAndRace:
    """Tests race conditions and multi-threaded throughput across APIs."""

    def test_concurrent_answer_evaluations(self, harness):
        """Executes 10 parallel evaluation requests simultaneously."""
        def evaluate_one(idx):
            return harness.evaluate_answer(
                session_id=f"ses_conc_{idx}",
                question_id=f"q_{idx}",
                student_answer=f"Correct limit definition property {idx}",
                concept="Limits"
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(evaluate_one, i) for i in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        assert len(results) == 10
        assert all(r["status_code"] == 200 for r in results)

    def test_concurrent_quiz_submissions_same_student(self, harness):
        """Simultaneous submissions for same student profile execute atomically."""
        def submit_one(idx):
            return harness.submit_quiz(
                quiz_id=f"quiz_conc_{idx}",
                student_id="stu_conc_shared",
                lesson_id=f"les_conc_{idx}",
                answers=[{"question_id": "q1", "student_answer": 0}]
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(submit_one, i) for i in range(4)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        assert len(results) == 4
        assert all(r["status_code"] == 200 for r in results)
        
        prof = harness.get_profile("stu_conc_shared")
        assert prof["status_code"] == 200
        assert prof["data"]["total_lessons_completed"] >= 4
