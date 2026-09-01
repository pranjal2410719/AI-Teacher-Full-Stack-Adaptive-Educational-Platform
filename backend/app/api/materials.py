"""
REST Endpoints for Learning Material Ingestion and RAG Querying.
Routes:
- POST /api/v1/materials/upload
- POST /api/v1/materials/topic
- POST /api/v1/materials/query
- GET /api/v1/materials/{doc_id}
- GET /api/v1/materials
"""

import json
import logging
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status

from backend.app.models.ingestion import (
    DocumentMetadata,
    TopicIngestionRequest,
    TopicIngestionResponse,
    RAGQuery,
    RAGResponse
)
from backend.app.services.ingestion_service import ingestion_service

logger = logging.getLogger("ai_teacher.api.materials")
router = APIRouter(prefix="/api/v1/materials", tags=["Learning Materials & Ingestion"])


@router.post(
    "/upload",
    response_model=DocumentMetadata,
    status_code=status.HTTP_200_OK,
    summary="Upload educational file (PDF, DOCX, PPT, PPTX, TXT, MD)"
)
async def upload_material(
    file: UploadFile = File(..., description="Educational document file to upload and index"),
    metadata: Optional[str] = Form(default=None, description="Optional JSON metadata string")
) -> DocumentMetadata:
    """
    Accepts an uploaded educational document, extracts text, headings, and tables,
    chunks the content with structure awareness, embeds vectors, and indexes into the RAG vector store.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename must not be empty."
        )

    try:
        file_bytes = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read uploaded file: {str(e)}"
        )

    if not file_bytes or len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is empty (0 bytes). Please upload valid educational material."
        )

    try:
        doc_meta, _ = ingestion_service.ingest_document(
            file_bytes=file_bytes,
            filename=file.filename,
            content_type=file.content_type
        )
        return doc_meta
    except ValueError as ve:
        err_msg = str(ve)
        if "exceeds maximum limit" in err_msg:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=err_msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)
    except Exception as e:
        logger.exception(f"Unexpected error during document ingestion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal ingestion error: {str(e)}"
        )


@router.post(
    "/topic",
    response_model=TopicIngestionResponse,
    status_code=status.HTTP_200_OK,
    summary="Ingest plain-text topic for parametric knowledge generation"
)
async def ingest_topic(request: TopicIngestionRequest) -> TopicIngestionResponse:
    """
    Generates structured educational grounding from LLM parametric knowledge
    when no source file is uploaded, indexing seed concepts for grounded lesson planning.
    """
    try:
        response, _ = ingestion_service.ingest_topic(request)
        return response
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))
    except Exception as e:
        logger.exception(f"Error during topic parametric generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Topic generation failed: {str(e)}"
        )


@router.post(
    "/query",
    response_model=RAGResponse,
    status_code=status.HTTP_200_OK,
    summary="Query RAG vector store for grounded context chunks"
)
async def query_rag(query: RAGQuery) -> RAGResponse:
    """
    Retrieves top-k semantically and lexically relevant chunks from an indexed document or topic
    using hybrid dense cosine similarity and Okapi BM25 scoring.
    """
    try:
        rag_response = ingestion_service.query_rag(query)
        return rag_response
    except Exception as e:
        logger.exception(f"RAG query execution failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG retrieval error: {str(e)}"
        )


@router.get(
    "/{doc_id}",
    response_model=DocumentMetadata,
    status_code=status.HTTP_200_OK,
    summary="Retrieve metadata for an ingested document or topic"
)
async def get_material_metadata(doc_id: str) -> DocumentMetadata:
    """
    Returns metadata, page count, chunk stats, and extracted summary for a document or topic ID.
    """
    meta = ingestion_service.get_metadata(doc_id)
    if not meta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material with ID '{doc_id}' not found."
        )
    return meta


@router.get(
    "",
    response_model=List[DocumentMetadata],
    status_code=status.HTTP_200_OK,
    summary="List all ingested documents and topics"
)
async def list_all_materials() -> List[DocumentMetadata]:
    """
    Returns a list of all indexed documents and topics available for lesson planning.
    """
    return ingestion_service.list_all_materials()
