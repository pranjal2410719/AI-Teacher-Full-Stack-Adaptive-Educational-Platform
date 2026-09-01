"""
Tier 5 Adversarial Coverage Hardening: Multilingual Polyglot and Special Unicode Resilience.
"""

import pytest
from tests_e2e.harness import E2ETestHarness

@pytest.fixture
def harness():
    return E2ETestHarness()

class TestAdversarialUnicodePolyglot:
    """Tests diverse international scripts, emojis, and math Unicode."""

    def test_hindi_devanagari_flow(self, harness):
        """Tests complete Devanagari Hindi evaluation and tutor chat."""
        eval_res = harness.evaluate_answer(
            session_id="ses_poly_hi",
            question_id="q_hi",
            student_answer="सीमा का अस्तित्व तभी होता है जब दोनों पक्ष बराबर हों।",
            concept="Limits",
            language="hi"
        )
        assert eval_res["status_code"] == 200
        assert eval_res["data"]["is_correct"] is True

        chat_res = harness.tutor_chat(
            message="नमस्ते, कृपया मुझे अवकलन (Differentiation) के बारे में समझाएं।",
            session_id="ses_poly_hi"
        )
        assert chat_res["status_code"] == 200
        assert len(chat_res["data"]["reply"]) > 10

    def test_mathematical_latex_symbols_in_chat(self, harness):
        """Tests complex LaTeX formulas in side-panel chat."""
        msg = "How do we evaluate \\int_0^\\infty e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}?"
        res = harness.tutor_chat(message=msg, session_id="ses_poly_math")
        assert res["status_code"] == 200
        assert len(res["data"]["reply"]) > 10
