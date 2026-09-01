"""
Vector Store, Structure-Aware Chunker, and Pure-Python BM25 Lexical Ranker.
Provides hybrid semantic and lexical retrieval for RAG grounding.
"""

import os
import re
import json
import math
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

from backend.app.config import settings
from backend.app.models.ingestion import DocumentChunk, ChunkMatch, RAGResponse
from backend.app.services.llm_client import llm_client

logger = logging.getLogger("ai_teacher.vector_store")


# -----------------------------------------------------------------------------
# Pure-Python BM25 Okapi Ranker
# -----------------------------------------------------------------------------

class BM25Ranker:
    """
    Pure-Python Okapi BM25 ranking algorithm with score normalization.
    Parameters: k1=1.5, b=0.75.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = 0
        self.avg_doc_len = 0.0
        self.doc_lengths: List[int] = []
        self.doc_freqs: Dict[str, int] = {}  # term -> number of docs containing term
        self.term_freqs: List[Dict[str, int]] = []  # doc_idx -> (term -> count)
        self.idf: Dict[str, float] = {}

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Lowercase and extract alphanumeric tokens."""
        return re.findall(r"\b[a-zA-Z0-9_]{2,}\b", text.lower())

    def fit(self, documents: List[str]) -> None:
        """Indexes a collection of document texts."""
        self.corpus_size = len(documents)
        if self.corpus_size == 0:
            self.avg_doc_len = 0.0
            return

        self.doc_lengths = []
        self.term_freqs = []
        self.doc_freqs = {}
        total_len = 0

        for doc in documents:
            tokens = self.tokenize(doc)
            doc_len = len(tokens)
            self.doc_lengths.append(doc_len)
            total_len += doc_len

            tf: Dict[str, int] = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1
            self.term_freqs.append(tf)

            for t in tf.keys():
                self.doc_freqs[t] = self.doc_freqs.get(t, 0) + 1

        self.avg_doc_len = total_len / max(1, self.corpus_size)

        # Compute IDF with standard smoothing: ln((N - n + 0.5) / (n + 0.5) + 1)
        self.idf = {}
        for term, n_docs in self.doc_freqs.items():
            val = (self.corpus_size - n_docs + 0.5) / (n_docs + 0.5) + 1.0
            self.idf[term] = math.log(max(val, 1.01))

    def score(self, query: str) -> List[float]:
        """Calculates BM25 score for all indexed documents against query."""
        if self.corpus_size == 0:
            return []

        query_tokens = self.tokenize(query)
        if not query_tokens:
            return [0.0] * self.corpus_size

        scores = np.zeros(self.corpus_size, dtype=np.float32)

        for token in query_tokens:
            if token not in self.idf:
                continue
            idf_val = self.idf[token]

            for i in range(self.corpus_size):
                tf_val = self.term_freqs[i].get(token, 0)
                if tf_val == 0:
                    continue
                doc_len = self.doc_lengths[i]
                numerator = tf_val * (self.k1 + 1.0)
                denominator = tf_val + self.k1 * (1.0 - self.b + self.b * (doc_len / max(1.0, self.avg_doc_len)))
                scores[i] += idf_val * (numerator / max(1e-6, denominator))

        # Normalize BM25 scores to [0.0, 1.0] range
        max_score = float(np.max(scores))
        if max_score > 0:
            scores = scores / max_score

        return scores.tolist()


# -----------------------------------------------------------------------------
# Structure-Aware Semantic Chunker
# -----------------------------------------------------------------------------

def chunk_text_sliding_window(
    text: str,
    chunk_size: int = 500,
    overlap: int = 100,
    source_filename: str = "",
    document_id: str = "",
    page_or_slide: Optional[int] = None,
    section_title: Optional[str] = None,
    start_chunk_index: int = 0
) -> List[DocumentChunk]:
    """
    Chunks a block of text using sentence/paragraph boundaries with overlap.
    """
    clean_text = text.strip()
    if not clean_text:
        return []

    # If text is already short enough, return single chunk
    if len(clean_text) <= chunk_size:
        token_count = max(1, len(clean_text.split()))
        return [
            DocumentChunk(
                chunk_id=f"chk_{document_id}_{start_chunk_index:04d}",
                document_id=document_id,
                source_filename=source_filename,
                page_or_slide=page_or_slide,
                section_title=section_title,
                text=clean_text,
                token_count=token_count,
                chunk_index=start_chunk_index
            )
        ]

    # Split along paragraphs or sentences
    paragraphs = [p.strip() for p in clean_text.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [clean_text]

    chunks: List[DocumentChunk] = []
    current_text = ""
    chunk_idx = start_chunk_index

    for p in paragraphs:
        if len(current_text) + len(p) + 2 <= chunk_size:
            current_text = f"{current_text}\n\n{p}".strip()
        else:
            if current_text:
                token_count = max(1, len(current_text.split()))
                chunks.append(
                    DocumentChunk(
                        chunk_id=f"chk_{document_id}_{chunk_idx:04d}",
                        document_id=document_id,
                        source_filename=source_filename,
                        page_or_slide=page_or_slide,
                        section_title=section_title,
                        text=current_text,
                        token_count=token_count,
                        chunk_index=chunk_idx
                    )
                )
                chunk_idx += 1
                # Sliding overlap: keep last N characters
                overlap_text = current_text[-overlap:] if len(current_text) > overlap else ""
                current_text = f"{overlap_text}\n\n{p}".strip()
            else:
                # Paragraph itself exceeds chunk_size: split by sentences
                sentences = re.split(r"(?<=[.!?])\s+", p)
                sub_text = ""
                for s in sentences:
                    if len(sub_text) + len(s) + 1 <= chunk_size:
                        sub_text = f"{sub_text} {s}".strip()
                    else:
                        if sub_text:
                            token_count = max(1, len(sub_text.split()))
                            chunks.append(
                                DocumentChunk(
                                    chunk_id=f"chk_{document_id}_{chunk_idx:04d}",
                                    document_id=document_id,
                                    source_filename=source_filename,
                                    page_or_slide=page_or_slide,
                                    section_title=section_title,
                                    text=sub_text,
                                    token_count=token_count,
                                    chunk_index=chunk_idx
                                )
                            )
                            chunk_idx += 1
                            overlap_sub = sub_text[-overlap:] if len(sub_text) > overlap else ""
                            sub_text = f"{overlap_sub} {s}".strip()
                        else:
                            # Hard character split for extremely long single strings (e.g. code/dna)
                            for sub_part in [s[i:i+chunk_size] for i in range(0, len(s), chunk_size - overlap)]:
                                token_count = max(1, len(sub_part.split()))
                                chunks.append(
                                    DocumentChunk(
                                        chunk_id=f"chk_{document_id}_{chunk_idx:04d}",
                                        document_id=document_id,
                                        source_filename=source_filename,
                                        page_or_slide=page_or_slide,
                                        section_title=section_title,
                                        text=sub_part,
                                        token_count=token_count,
                                        chunk_index=chunk_idx
                                    )
                                )
                                chunk_idx += 1
                current_text = sub_text

    if current_text:
        token_count = max(1, len(current_text.split()))
        chunks.append(
            DocumentChunk(
                chunk_id=f"chk_{document_id}_{chunk_idx:04d}",
                document_id=document_id,
                source_filename=source_filename,
                page_or_slide=page_or_slide,
                section_title=section_title,
                text=current_text,
                token_count=token_count,
                chunk_index=chunk_idx
            )
        )

    return chunks


# -----------------------------------------------------------------------------
# Numpy Vector Store with BM25 Hybrid Index
# -----------------------------------------------------------------------------

class DocumentVectorIndex:
    """
    In-memory and persisted dense vector + lexical index for a single document or topic.
    """

    def __init__(self, target_id: str):
        self.target_id = target_id
        self.chunks: List[DocumentChunk] = []
        self.embeddings: Optional[np.ndarray] = None  # Float32 matrix (N, Dim)
        self.bm25 = BM25Ranker()

    def build_index(self, chunks: List[DocumentChunk]) -> None:
        """Embeds and indexes chunks."""
        self.chunks = chunks
        if not chunks:
            self.embeddings = np.zeros((0, settings.vector_dim), dtype=np.float32)
            self.bm25.fit([])
            return

        texts = [c.text for c in chunks]

        # Extract embeddings if already attached or generate new ones
        emb_list = []
        texts_to_embed = []
        indices_to_embed = []

        for i, c in enumerate(chunks):
            if c.embedding and len(c.embedding) == settings.vector_dim:
                emb_list.append(c.embedding)
            else:
                texts_to_embed.append(c.text)
                indices_to_embed.append(i)

        if texts_to_embed:
            generated_embs = llm_client.generate_embeddings(texts_to_embed)
            for idx, emb in zip(indices_to_embed, generated_embs):
                self.chunks[idx].embedding = emb

        final_matrix = np.array([c.embedding for c in self.chunks], dtype=np.float32)
        # Normalize rows to unit L2 norm for exact cosine similarity via dot product
        norms = np.linalg.norm(final_matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.embeddings = final_matrix / norms

        # Build BM25 index
        self.bm25.fit(texts)

    def search(
        self,
        query: str,
        top_k: int = 4,
        alpha: float = 0.6
    ) -> List[ChunkMatch]:
        """
        Hybrid search combining dense cosine similarity and lexical BM25 ranking.
        Score = alpha * vector_score + (1 - alpha) * bm25_score.
        """
        if not self.chunks or self.embeddings is None or len(self.chunks) == 0:
            return []

        # 1. Vector Cosine Similarity
        query_emb = llm_client.generate_embeddings([query])[0]
        q_vec = np.array(query_emb, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 0:
            q_vec = q_vec / q_norm

        # Dot product with normalized matrix gives cosine similarities in [-1, 1]
        cosine_scores = np.dot(self.embeddings, q_vec)
        # Shift and scale cosine to [0, 1]
        vec_scores = np.clip((cosine_scores + 1.0) / 2.0, 0.0, 1.0)

        # 2. BM25 Lexical Score in [0, 1]
        bm25_scores = np.array(self.bm25.score(query), dtype=np.float32)

        # 3. Hybrid Combination
        hybrid_scores = alpha * vec_scores + (1.0 - alpha) * bm25_scores

        # 4. Top-K Selection
        top_indices = np.argsort(hybrid_scores)[::-1][:top_k]

        matches: List[ChunkMatch] = []
        for rank, idx in enumerate(top_indices):
            chunk = self.chunks[idx]
            match = ChunkMatch(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                source_filename=chunk.source_filename,
                page_or_slide=chunk.page_or_slide,
                section_title=chunk.section_title,
                text=chunk.text,
                similarity_score=round(float(hybrid_scores[idx]), 4),
                vector_score=round(float(vec_scores[idx]), 4),
                bm25_score=round(float(bm25_scores[idx]), 4),
                retrieval_method="hybrid"
            )
            matches.append(match)

        return matches

    def save_to_disk(self, directory: Path) -> None:
        """Persists index metadata and chunks to disk."""
        target_dir = directory / self.target_id
        target_dir.mkdir(parents=True, exist_ok=True)

        # Save chunks JSON
        chunks_data = [c.model_dump() for c in self.chunks]
        with open(target_dir / "chunks.json", "w", encoding="utf-8") as f:
            json.dump(chunks_data, f, indent=2)

        # Save embeddings matrix
        if self.embeddings is not None:
            np.save(target_dir / "embeddings.npy", self.embeddings)

    @classmethod
    def load_from_disk(cls, directory: Path, target_id: str) -> Optional["DocumentVectorIndex"]:
        """Loads index from disk if present."""
        target_dir = directory / target_id
        chunks_file = target_dir / "chunks.json"
        emb_file = target_dir / "embeddings.npy"

        if not chunks_file.exists():
            return None

        with open(chunks_file, "r", encoding="utf-8") as f:
            chunks_raw = json.load(f)
        chunks = [DocumentChunk(**item) for item in chunks_raw]

        index = cls(target_id=target_id)
        index.chunks = chunks
        if emb_file.exists():
            index.embeddings = np.load(emb_file)
        else:
            index.build_index(chunks)

        index.bm25.fit([c.text for c in chunks])
        return index


# -----------------------------------------------------------------------------
# Global Vector Store Manager
# -----------------------------------------------------------------------------

class NumpyVectorStore:
    """
    Global vector store registry managing active document/topic indices with disk persistence.
    """

    def __init__(self):
        self.indices: Dict[str, DocumentVectorIndex] = {}
        self.storage_dir = settings.vector_index_dir

    def add_document(self, target_id: str, chunks: List[DocumentChunk]) -> DocumentVectorIndex:
        """Builds and caches index for target_id, persisting to disk."""
        index = DocumentVectorIndex(target_id=target_id)
        index.build_index(chunks)
        index.save_to_disk(self.storage_dir)
        self.indices[target_id] = index
        return index

    def get_index(self, target_id: str) -> Optional[DocumentVectorIndex]:
        """Retrieves index from memory or loads from disk."""
        if target_id in self.indices:
            return self.indices[target_id]

        loaded = DocumentVectorIndex.load_from_disk(self.storage_dir, target_id)
        if loaded:
            self.indices[target_id] = loaded
            return loaded

        return None

    def query(
        self,
        query: str,
        target_id: Optional[str] = None,
        top_k: int = 4,
        alpha: float = 0.6
    ) -> RAGResponse:
        """
        Executes hybrid retrieval across specified document or all active indices.
        """
        all_matches: List[ChunkMatch] = []

        if target_id:
            index = self.get_index(target_id)
            if index:
                all_matches.extend(index.search(query, top_k=top_k, alpha=alpha))
        else:
            # Query across all loaded and on-disk indices
            for tid in list(self.indices.keys()):
                idx = self.indices[tid]
                all_matches.extend(idx.search(query, top_k=top_k, alpha=alpha))

        # Re-sort all matches and take top_k
        all_matches.sort(key=lambda m: m.similarity_score, reverse=True)
        top_matches = all_matches[:top_k]

        # Format grounded context string
        context_parts = []
        for i, match in enumerate(top_matches, start=1):
            source_tag = f"[Source: {match.source_filename}"
            if match.page_or_slide is not None:
                source_tag += f" | Page/Slide {match.page_or_slide}"
            if match.section_title:
                source_tag += f" | Section: '{match.section_title}'"
            source_tag += "]"
            context_parts.append(f"{i}. {source_tag}\n{match.text}")

        grounded_context = "\n\n---\n\n".join(context_parts) if context_parts else ""

        return RAGResponse(
            query=query,
            target_id=target_id,
            total_results=len(top_matches),
            results=top_matches,
            grounded_context=grounded_context
        )


# Global shared singleton
vector_store = NumpyVectorStore()
