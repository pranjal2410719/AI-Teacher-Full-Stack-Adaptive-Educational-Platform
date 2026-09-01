"""
Tier 2 Boundary & Corner Cases: Multilingual and Unicode Handling
Tests unicode stability with Devanagari Hindi, mathematical symbols, and non-ASCII character sets.
"""

import pytest
from tests_e2e.harness import E2ETestHarness

@pytest.fixture
def harness():
    return E2ETestHarness()

def test_hindi_devanagari_topic_ingestion(harness):
    """Verifies topic ingestion handles pure Devanagari Hindi characters."""
    res = harness.ingest_topic(
        topic="कैलकुलस में सीमाएं और सातत्य (Limits and Continuity)",
        subject_category="गणित (Mathematics)"
    )
    assert res["status_code"] == 200
    assert "कैलकुलस" in res["data"]["topic"]

def test_hindi_answer_evaluation(harness):
    """Verifies student answer evaluation with Devanagari Hindi text."""
    res = harness.evaluate_answer(
        session_id="ses_hi_unicode_01",
        question_id="q_hi_01",
        student_answer="यदि बायीं सीमा और दायीं सीमा बराबर हैं, तो सीमा मौजूद है।",
        concept="Limits in Hindi",
        language="hi"
    )
    assert res["status_code"] == 200
    assert "is_correct" in res["data"]

def test_math_special_symbols_in_rag_query(harness, math_pdf_path):
    """Verifies RAG query handling complex mathematical LaTeX and unicode symbols."""
    upload_res = harness.upload_material(math_pdf_path)
    doc_id = upload_res["data"]["document_id"]

    query = r"lim_{x \to 0} \frac{\sin(x)}{x} = 1 and \forall \epsilon > 0, \exists \delta > 0, \infty"
    res = harness.query_rag(query=query, document_id=doc_id)
    assert res["status_code"] == 200
    assert res["data"]["total_results"] > 0
