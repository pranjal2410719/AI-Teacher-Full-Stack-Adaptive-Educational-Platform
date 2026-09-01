"""
Pydantic Models for Document Ingestion, Topic Parametric Mode, and RAG Engine.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator


class DocumentMetadata(BaseModel):
    """Metadata describing an ingested educational document."""
    document_id: str = Field(..., description="Unique identifier for the document")
    filename: str = Field(..., description="Original name of the uploaded file")
    file_type: str = Field(..., description="File format extension (pdf, docx, pptx, txt, md)")
    file_size_bytes: int = Field(default=0, ge=0, description="Size of file in bytes")
    total_pages: int = Field(default=1, ge=1, description="Total pages, slides, or sections in document")
    chunk_count: int = Field(default=0, ge=0, description="Number of indexed semantic chunks")
    extracted_summary: str = Field(default="", description="High-level synopsis of the document content")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = Field(default="ready", description="Processing status: ready, processing, failed")
    metadata_extra: Dict[str, Any] = Field(default_factory=dict, description="Additional custom metadata")


class DocumentChunk(BaseModel):
    """A discrete, indexed segment of educational text with structural provenance."""
    chunk_id: str = Field(..., description="Unique chunk identifier, e.g. chk_doc123_001")
    document_id: str = Field(..., description="Foreign key linking to parent DocumentMetadata or Topic")
    source_filename: str = Field(..., description="Original filename or topic source")
    page_or_slide: Optional[int] = Field(default=None, description="1-indexed page number or slide index")
    section_title: Optional[str] = Field(default=None, description="Enclosing heading, title, or section name")
    text: str = Field(..., min_length=1, description="Raw textual content of the chunk")
    token_count: int = Field(default=0, ge=0, description="Estimated token count for RAG budgeting")
    chunk_index: int = Field(default=0, ge=0, description="Sequential index within document")
    embedding: Optional[List[float]] = Field(default=None, description="Dense vector embedding")


class TopicIngestionRequest(BaseModel):
    """Request to ingest a plain-text topic without an uploaded file."""
    topic: str = Field(..., min_length=2, max_length=500, description="Educational topic name or subject description")
    subject_category: Optional[str] = Field(default="General", description="Subject area (e.g. Mathematics, Computer Science, Biology, History)")
    additional_notes: Optional[str] = Field(default=None, description="Optional extra guidance or focus areas")
    language: Optional[str] = Field(default="en", description="Target language (e.g., en, hi)")

    @field_validator("topic")
    @classmethod
    def validate_topic_not_empty(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Topic must contain alphanumeric educational subject description and cannot be blank.")
        # Reject if only punctuation/emojis without alphanumeric characters
        if not any(c.isalnum() for c in cleaned):
            raise ValueError("Topic must contain alphanumeric educational subject description.")
        return cleaned


class TopicIngestionResponse(BaseModel):
    """Response returned upon generating parametric grounding for a topic."""
    topic_id: str = Field(..., description="Generated topic identifier")
    topic: str = Field(..., description="Sanitized topic title")
    subject_category: str = Field(..., description="Subject classification")
    seed_summary: str = Field(..., description="Parametric seed syllabus overview")
    generated_chunks_count: int = Field(default=0, ge=0, description="Number of knowledge chunks generated")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = Field(default="ready", description="Readiness status")


class RAGQuery(BaseModel):
    """Query payload for retrieving grounded reference material."""
    document_id: Optional[str] = Field(default=None, description="ID of document to search within")
    topic_id: Optional[str] = Field(default=None, description="ID of topic to search within")
    query: str = Field(..., min_length=1, description="Semantic or lexical search query")
    top_k: int = Field(default=4, ge=1, le=20, description="Number of relevant chunks to return")

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Query string cannot be empty or whitespace only.")
        return cleaned


class ChunkMatch(BaseModel):
    """A single chunk match retrieved via vector, BM25, or hybrid ranking."""
    chunk_id: str
    document_id: str
    source_filename: str
    page_or_slide: Optional[int] = None
    section_title: Optional[str] = None
    text: str
    similarity_score: float = Field(..., description="Normalized composite relevance score in [0.0, 1.0]")
    vector_score: Optional[float] = Field(default=None, description="Dense cosine similarity score")
    bm25_score: Optional[float] = Field(default=None, description="Lexical BM25 relevance score")
    retrieval_method: str = Field(default="hybrid", description="Method used: hybrid, vector, bm25")


class RAGResponse(BaseModel):
    """Aggregated response containing retrieved chunks and formatted grounded context."""
    query: str
    target_id: Optional[str] = Field(default=None, description="Queried document_id or topic_id")
    total_results: int = Field(default=0, ge=0)
    results: List[ChunkMatch] = Field(default_factory=list)
    grounded_context: str = Field(default="", description="Consolidated context string ready for LLM prompt injection")
