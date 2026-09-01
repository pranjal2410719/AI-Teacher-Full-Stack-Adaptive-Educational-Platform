"""
Tier 3 Cross-Feature Combination: Interactive Teaching Loop & Misconception Cycle
Pipeline: Video Pause Trigger (R3/R4) -> LLM Evaluation & Misconception Diagnosis (R4) -> Follow-up Verification -> Video Unlock.
"""

import pytest
from tests_e2e.harness import E2ETestHarness

@pytest.fixture
def harness():
    return E2ETestHarness()

def test_full_interactive_misconception_resolution_cycle(harness):
    """
    Executes full pedagogical interaction cycle:
    1. Student encounters pause checkpoint question on secant vs tangent slope.
    2. Student submits flawed answer confusing instantaneous speed with average rate.
    3. System diagnoses misconception, generates road trip analogy, and poses follow-up question.
    4. Student responds to follow-up with correct understanding.
    5. System marks concept mastered and unlocks video playback.
    """
    session_id = "ses_cycle_01"
    question_id = "q_secant_tangent_01"

    # 1. Step 1: Flawed Answer
    eval_1 = harness.evaluate_answer(
        session_id=session_id,
        question_id=question_id,
        student_answer="Secant line slope gives the exact speed at one instant.",
        concept="Secant Slope vs Derivative"
    )["data"]

    assert eval_1["is_correct"] is False
    assert eval_1["can_resume_video"] is False
    assert eval_1["misconception_detected"] is not None
    assert eval_1["pedagogical_re_explanation"] is not None
    assert eval_1["follow_up_question"] is not None

    follow_up_q = eval_1["follow_up_question"]
    follow_up_id = follow_up_q["question_id"]

    # 2. Step 2: Correct Follow-Up Answer
    eval_2 = harness.evaluate_answer(
        session_id=session_id,
        question_id=follow_up_id,
        student_answer="When delta t shrinks to zero, the secant line slope becomes the exact derivative (tangent slope).",
        concept="Instantaneous Rate of Change"
    )["data"]

    assert eval_2["is_correct"] is True
    assert eval_2["score"] >= 0.8
    assert eval_2["can_resume_video"] is True
