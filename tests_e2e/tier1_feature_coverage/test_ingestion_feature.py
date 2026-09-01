"""
Tier 1 Feature Coverage: R1 Ingestion & RAG
Covers >= 5 discrete tests:
1. test_pdf_document_upload
2. test_docx_document_upload
3. test_pptx_document_upload
4. test_txt_document_upload
5. test_topic_parametric_ingestion
6. test_rag_semantic_query_grounding
"""

import pytest
from tests_e2e.harness import E2ETestHarness

@pytest.fixture
def harness():
    return E2ETestHarness()

def test_pdf_document_upload(harness, math_pdf_path):
    """Verifies that uploading a PDF returns valid document metadata and extracted summary."""
    res = harness.upload_material(math_pdf_path)
    assert res["status_code"] == 200, f"Upload failed: {res['data']}"
    data = res["data"]
    assert "document_id" in data
    assert data["file_type"] == "pdf"
    assert data["chunk_count"] > 0
    assert "calculus" in data["extracted_summary"].lower() or "limit" in data["extracted_summary"].lower()
    assert data["status"] == "ready"

def test_docx_document_upload(harness, cs_docx_path):
    """Verifies that uploading a DOCX file processes binary search tree data structures."""
    res = harness.upload_material(cs_docx_path)
    assert res["status_code"] == 200, f"Upload failed: {res['data']}"
    data = res["data"]
    assert "document_id" in data
    assert data["file_type"] == "docx"
    assert data["chunk_count"] > 0
    assert "bst" in data["extracted_summary"].lower() or "tree" in data["extracted_summary"].lower()

def test_pptx_document_upload(harness, bio_pptx_path):
    """Verifies that uploading a PPTX presentation extracts slide chunks and metadata."""
    res = harness.upload_material(bio_pptx_path)
    assert res["status_code"] == 200, f"Upload failed: {res['data']}"
    data = res["data"]
    assert "document_id" in data
    assert data["file_type"] == "pptx"
    assert data["total_pages"] >= 1
    assert "cell" in data["extracted_summary"].lower() or "bio" in data["extracted_summary"].lower()

def test_txt_document_upload(harness, history_txt_path):
    """Verifies that uploading a TXT document parses history text content."""
    res = harness.upload_material(history_txt_path)
    assert res["status_code"] == 200, f"Upload failed: {res['data']}"
    data = res["data"]
    assert "document_id" in data
    assert data["file_type"] == "txt"
    assert "revolution" in data["extracted_summary"].lower() or "history" in data["extracted_summary"].lower()

def test_topic_parametric_ingestion(harness):
    """Verifies topic-only mode without file upload produces parametric seed summary."""
    res = harness.ingest_topic(
        topic="Photosynthesis and Calvin Cycle",
        subject_category="Biology",
        additional_notes="Focus on Light-Dependent Reactions and ATP production"
    )
    assert res["status_code"] == 200, f"Topic ingestion failed: {res['data']}"
    data = res["data"]
    assert "topic_id" in data
    assert data["topic"] == "Photosynthesis and Calvin Cycle"
    assert data["subject_category"] == "Biology"
    assert data["generated_chunks_count"] > 0
    assert data["status"] == "ready"

def test_rag_semantic_query_grounding(harness, math_pdf_path):
    """Verifies RAG retrieval against uploaded material returns grounded context."""
    upload_res = harness.upload_material(math_pdf_path)
    assert upload_res["status_code"] == 200
    doc_id = upload_res["data"]["document_id"]

    query_res = harness.query_rag(
        query="What is the formal epsilon-delta definition of a limit?",
        document_id=doc_id,
        top_k=3
    )
    assert query_res["status_code"] == 200, f"RAG query failed: {query_res['data']}"
    data = query_res["data"]
    assert data["total_results"] > 0
    assert len(data["results"]) >= 1
    assert "grounded_context" in data
    first_match = data["results"][0]
    assert "chunk_id" in first_match
    assert first_match["document_id"] == doc_id
    assert first_match["similarity_score"] >= 0.5
