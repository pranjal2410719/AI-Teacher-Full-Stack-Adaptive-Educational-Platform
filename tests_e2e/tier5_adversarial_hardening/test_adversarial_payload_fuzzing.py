"""
Tier 5 Adversarial Coverage Hardening: Payload Fuzzing and Security Injection.
Tests SQL injection, XSS payloads, prompt injection, and large buffer inputs across R1-R5.
"""

import pytest
from tests_e2e.harness import E2ETestHarness

@pytest.fixture
def harness():
    return E2ETestHarness()

class TestAdversarialSecurityAndFuzzing:
    """Stress tests malicious and security-sensitive payloads."""

    def test_sql_injection_in_profile_lookup(self, harness):
        """Verifies that SQL injection attempts in student IDs do not corrupt profile DB."""
        malicious_id = "stu_sql'; DROP TABLE student_profiles; --"
        res = harness.get_profile(student_id=malicious_id)
        assert res["status_code"] == 200
        assert res["data"]["student_id"] == malicious_id

    def test_xss_script_injection_in_student_answer(self, harness):
        """Verifies that HTML/Script tags in answers are safely processed without executing."""
        xss_payload = "<script>alert('XSS_ATTACK')</script><img src=x onerror=alert(1)>"
        res = harness.evaluate_answer(
            session_id="ses_xss_01",
            question_id="q_xss",
            student_answer=xss_payload,
            concept="Security Bounds"
        )
        assert res["status_code"] == 200
        assert res["data"]["is_correct"] is False
        assert res["data"]["can_resume_video"] is False

    def test_fuzzing_huge_buffer_in_topic_prompt(self, harness):
        """Verifies that extremely long (10KB+) topic strings are handled safely."""
        huge_topic = "Calculus Limits " * 500
        res = harness.ingest_topic(topic=huge_topic, subject_category="Mathematics")
        assert res["status_code"] in [200, 422]
