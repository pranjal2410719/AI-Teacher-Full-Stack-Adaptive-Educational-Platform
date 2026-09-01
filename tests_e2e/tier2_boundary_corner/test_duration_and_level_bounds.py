"""
Tier 2 Boundary & Corner Cases: Duration and Learner Level Bounds
Tests boundary constraints on session duration, time budgets, and pedagogical levels.
"""

import pytest
from tests_e2e.harness import E2ETestHarness

@pytest.fixture
def harness():
    return E2ETestHarness()

def test_ultra_short_1min_time_budget(harness):
    """Verifies planning handles minimal 1-minute time budget cleanly."""
    profile = {"student_id": "stu_min", "level": "beginner", "language": "en", "time_budget_min": 1}
    res = harness.create_lesson_plan(learner_profile=profile)
    assert res["status_code"] == 200
    assert res["data"]["target_duration_sec"] == 60
    assert len(res["data"]["modules"]) >= 1

def test_maximum_180min_time_budget(harness):
    """Verifies planning handles maximum allowable 180-minute time budget."""
    profile = {"student_id": "stu_max", "level": "advanced", "language": "en", "time_budget_min": 180}
    res = harness.create_lesson_plan(learner_profile=profile)
    assert res["status_code"] == 200
    assert res["data"]["target_duration_sec"] == 180 * 60

def test_zero_or_negative_duration_rejected(harness):
    """Verifies that 0 or negative time budgets return HTTP 422."""
    profile = {"student_id": "stu_err", "level": "intermediate", "language": "en", "time_budget_min": 0}
    res = harness.create_lesson_plan(learner_profile=profile)
    assert res["status_code"] == 422

def test_excessive_duration_rejected(harness):
    """Verifies that time budgets exceeding 180 minutes return HTTP 422."""
    profile = {"student_id": "stu_err2", "level": "intermediate", "language": "en", "time_budget_min": 240}
    res = harness.create_lesson_plan(learner_profile=profile)
    assert res["status_code"] == 422

def test_invalid_educational_level_rejected(harness):
    """Verifies that unsupported levels (e.g. 'postdoc_expert') return HTTP 422."""
    profile = {"student_id": "stu_err3", "level": "postdoc_expert", "language": "en", "time_budget_min": 15}
    res = harness.create_lesson_plan(learner_profile=profile)
    assert res["status_code"] == 422
