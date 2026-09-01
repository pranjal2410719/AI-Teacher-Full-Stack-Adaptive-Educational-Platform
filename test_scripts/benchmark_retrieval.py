"""
Adversarial Retrieval Quality & Performance Benchmark Suite for Milestone 1.
Challenger: challenger_m1_2

Benchmarks:
1. Vector Similarity vs BM25 Ranking vs Hybrid (alpha=0.6) on Multi-Paragraph Educational Texts.
2. Recall@k (k=1, 3, 5), MRR, Precision@k, and Distractor Chunk Filtering Rate.
3. Latency benchmarks (< 5ms per query requirement) across corpus sizes (10 to 1,000 chunks).
4. Memory efficiency and RSS footprint.
5. Multilingual and Adversarial Trap evaluation.
"""

import sys
import os
import time
import json
import math
import random
import tracemalloc
import resource
from typing import List, Dict, Any, Tuple
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.models.ingestion import DocumentChunk, ChunkMatch, RAGResponse
from backend.app.services.vector_store import (
    DocumentVectorIndex,
    NumpyVectorStore,
    BM25Ranker,
    chunk_text_sliding_window
)
from backend.app.services.llm_client import llm_client


# =============================================================================
# 1. BENCHMARK DATASET: MULTI-PARAGRAPH EDUCATIONAL CORPUS & ADVERSARIAL TRAPS
# =============================================================================

BENCHMARK_CORPUS = [
    # Domain: Physics - Quantum Mechanics
    {
        "id": "phys_photoelectric",
        "title": "Einstein Photoelectric Effect",
        "domain": "Physics",
        "text": (
            "The photoelectric effect is the emission of electrons when electromagnetic radiation, such as light, hits a material. "
            "Electrons emitted in this manner are called photoelectrons. Einstein explained this by postulating that light consists of discrete "
            "quanta called photons, each with energy E = h * nu, where h is Planck's constant and nu is the frequency of the light. "
            "A minimum threshold frequency nu_0 is required to liberate electrons from the metal surface, defined by the work function Phi = h * nu_0. "
            "Kinetic energy of emitted electrons depends solely on photon frequency, not intensity: K_max = h * nu - Phi."
        ),
        "is_distractor": False
    },
    {
        "id": "phys_heisenberg",
        "title": "Heisenberg Uncertainty Principle",
        "domain": "Physics",
        "text": (
            "The Heisenberg uncertainty principle states that there is a fundamental limit to the precision with which certain pairs of physical "
            "properties of a particle, known as complementary variables, such as position x and momentum p, can be known simultaneously. "
            "Mathematically, Delta x * Delta p >= h_bar / 2, where h_bar is the reduced Planck constant h / (2 * pi). "
            "This uncertainty is an intrinsic quantum mechanical wave property of matter and not a flaw in measurement instruments. "
            "Similarly, the energy-time uncertainty relation is expressed as Delta E * Delta t >= h_bar / 2."
        ),
        "is_distractor": False
    },
    {
        "id": "phys_double_slit",
        "title": "Young Double Slit Experiment & Wave-Particle Duality",
        "domain": "Physics",
        "text": (
            "The double-slit experiment demonstrates that light and matter can display characteristics of both classically defined waves and particles. "
            "When coherent light passes through two parallel slits, an alternating pattern of bright constructive interference fringes and dark "
            "destructive interference bands appears on a screen behind them. Even when photons or electrons are fired individually one at a time, "
            "the statistical buildup of detection points forms the interference pattern, indicating self-interference of the quantum probability wave function."
        ),
        "is_distractor": False
    },
    # Domain: Computer Science - Algorithms & Data Structures
    {
        "id": "cs_red_black_tree",
        "title": "Red-Black Tree Properties and Rotations",
        "domain": "Computer Science",
        "text": (
            "A red-black tree is a self-balancing binary search tree where each node has a color bit (red or black). "
            "It enforces five core invariants: 1. Every node is either red or black. 2. The root is always black. 3. Every leaf (NIL) is black. "
            "4. If a node is red, both its children must be black (no adjacent red nodes). 5. For each node, all simple paths from the node to "
            "descendant leaves contain the same number of black nodes (black-height). Rebalancing upon insertion or deletion is achieved in O(log n) "
            "time via left and right tree rotations and color flips."
        ),
        "is_distractor": False
    },
    {
        "id": "cs_dijkstra",
        "title": "Dijkstra Shortest Path Algorithm",
        "domain": "Computer Science",
        "text": (
            "Dijkstra's algorithm finds the shortest paths from a single source vertex to all other vertices in a weighted directed graph with non-negative edge weights. "
            "Using a min-priority queue (typically implemented with a binary heap or Fibonacci heap), it maintains tentative distances to all vertices, "
            "greedily extracting the unvisited vertex with the minimum distance and relaxing its outgoing edges: dist[v] = min(dist[v], dist[u] + weight(u, v)). "
            "With a binary min-heap, Dijkstra runs in O((V + E) log V) time."
        ),
        "is_distractor": False
    },
    {
        "id": "cs_transformer_attention",
        "title": "Transformer Scaled Dot-Product Self-Attention",
        "domain": "Computer Science",
        "text": (
            "The Transformer architecture replaces recurrent neural networks with multi-head self-attention mechanisms. "
            "Given input matrices for Queries Q, Keys K, and Values V with dimension d_k, the scaled dot-product attention is computed as: "
            "Attention(Q, K, V) = softmax((Q * K^T) / sqrt(d_k)) * V. "
            "Scaling by 1 / sqrt(d_k) prevents the dot products from growing excessively large for high dimensions, which would push the softmax function "
            "into regions with vanishingly small gradients. Multi-head attention projects Q, K, V into multiple representation subspaces."
        ),
        "is_distractor": False
    },
    # Domain: Biology - Molecular Biology & Genetics
    {
        "id": "bio_crispr",
        "title": "CRISPR-Cas9 Gene Editing System",
        "domain": "Biology",
        "text": (
            "CRISPR-Cas9 is a revolutionary RNA-guided genome engineering technology adapted from bacterial adaptive immune systems. "
            "The Cas9 endonuclease forms a ribonucleoprotein complex with a synthetic single guide RNA (sgRNA). "
            "The guide RNA directs Cas9 to a target genomic locus complementary to its 20-nucleotide spacer sequence, adjacent to a Protospacer Adjacent Motif (PAM, 5'-NGG-3'). "
            "Cas9 generates a site-specific double-strand break (DSB), which is repaired by cellular non-homologous end joining (NHEJ) causing gene knockout, "
            "or homology-directed repair (HDR) enabling precise gene insertion."
        ),
        "is_distractor": False
    },
    {
        "id": "bio_krebs_cycle",
        "title": "Citric Acid Cycle (Krebs Cycle) & ATP Synthesis",
        "domain": "Biology",
        "text": (
            "The citric acid cycle, also known as the Krebs cycle or TCA cycle, is a central metabolic pathway in the mitochondrial matrix of aerobic organisms. "
            "It oxidizes acetyl-CoA derived from carbohydrates, fats, and proteins into two molecules of CO2. "
            "In each turn of the cycle, one molecule of acetyl-CoA (2C) condenses with oxaloacetate (4C) to form citrate (6C). "
            "Through successive oxidation-reduction reactions, the cycle yields 3 NADH, 1 FADH2, and 1 GTP (or ATP) via substrate-level phosphorylation, "
            "delivering high-energy electrons to the mitochondrial electron transport chain."
        ),
        "is_distractor": False
    },
    # Domain: Mathematics - Analysis & Linear Algebra
    {
        "id": "math_taylor_series",
        "title": "Taylor Series Expansion and Remainder",
        "domain": "Mathematics",
        "text": (
            "The Taylor series of an infinitely differentiable real or complex function f(x) about a point x = a is given by the power series: "
            "f(x) = sum_{n=0}^{infinity} (f^{(n)}(a) / n!) * (x - a)^n. "
            "When expanded around a = 0, it is specifically called a Maclaurin series. "
            "Taylor's theorem with Lagrange remainder provides an explicit bound on the truncation error after k terms: "
            "R_k(x) = (f^{(k+1)}(c) / (k+1)!) * (x - a)^{k+1} for some real c strictly between a and x."
        ),
        "is_distractor": False
    },
    {
        "id": "math_eigenvalues",
        "title": "Eigenvalues, Eigenvectors and Characteristic Polynomial",
        "domain": "Mathematics",
        "text": (
            "For a square linear transformation matrix A of size n x n, a non-zero vector v is an eigenvector corresponding to scalar eigenvalue lambda if: "
            "A * v = lambda * v, or equivalently (A - lambda * I) * v = 0. "
            "Non-trivial solutions exist if and only if the determinant det(A - lambda * I) = 0, which defines the degree-n characteristic polynomial of A. "
            "The roots of this polynomial are the eigenvalues. If A has n linearly independent eigenvectors, it can be diagonalized as A = P * D * P^{-1}."
        ),
        "is_distractor": False
    },
    # Domain: Multilingual - Hindi Devanagari
    {
        "id": "hindi_photosynthesis",
        "title": "प्रकाश संश्लेषण और क्लोरोप्लास्ट",
        "domain": "Biology (Hindi)",
        "text": (
            "प्रकाश संश्लेषण (Photosynthesis) वह जैव रासायनिक प्रक्रिया है जिसके द्वारा हरे पौधे सूर्य के प्रकाश की ऊर्जा का उपयोग करके कार्बन डाइऑक्साइड (CO2) "
            "और पानी (H2O) को ग्लूकोज और ऑक्सीजन में परिवर्तित करते हैं। यह प्रक्रिया क्लोरोप्लास्ट में उपस्थित पर्णहरित (Chlorophyll) वर्णक द्वारा संपन्न होती है। "
            "प्रकाश अभिक्रियाएं थाइलाकोइड झिल्लियों में होती हैं जबकि अप्रकाशीय अभिक्रियाएं (केल्विन चक्र) स्ट्रोमा में होती हैं।"
        ),
        "is_distractor": False
    },

    # ADVERSARIAL DISTRACTOR CHUNKS
    {
        "id": "distractor_lexical_trap_dijkstra",
        "title": "Lexical Trap: Dijkstra Keyword Counter-Context",
        "domain": "Distractor",
        "text": (
            "This chapter does NOT discuss Dijkstra algorithm, shortest paths, or graph relaxation. "
            "For Dijkstra shortest path algorithm in weighted graphs, please refer to Volume 4. "
            "Here we study operating system memory segmentation, virtual memory paging, and page fault replacement algorithms."
        ),
        "is_distractor": True,
        "target_query_trap": "dijkstra algorithm shortest path"
    },
    {
        "id": "distractor_keyword_stuffing_crispr",
        "title": "Keyword Stuffing Trap: CRISPR Cas9 sgRNA PAM",
        "domain": "Distractor",
        "text": (
            "Index of terms: CRISPR, Cas9, sgRNA, PAM sequence, double-strand break, NHEJ, HDR, endonuclease, target genomic locus, spacer sequence. "
            "Page index: 45, 92, 110, 145, 203, 305. See glossary at the end of the manual for term definitions."
        ),
        "is_distractor": True,
        "target_query_trap": "crispr cas9 guide rna double strand break"
    },
    {
        "id": "distractor_negation_photoelectric",
        "title": "Negation Trap: Photoelectric vs Classical Wave Theory",
        "domain": "Distractor",
        "text": (
            "Classical electromagnetic wave theory completely failed to explain the photoelectric effect because it predicted that electron kinetic energy "
            "should increase with light wave intensity, not frequency, and that there should be a measurable time lag for low-intensity light. "
            "None of these classical wave predictions were observed experimentally."
        ),
        "is_distractor": True,
        "target_query_trap": "photoelectric work function threshold frequency planck"
    },
    {
        "id": "distractor_cross_domain_tree",
        "title": "Cross Domain Trap: Red-Black Botanical Trees",
        "domain": "Distractor",
        "text": (
            "In temperate forest ecology, red oak and black walnut trees demonstrate complex root branching and canopy rotation patterns. "
            "Each tree node in the forest network maintains balance by competing for sunlight, with leaves absorbing red and black spectrum wavelengths."
        ),
        "is_distractor": True,
        "target_query_trap": "red-black tree node rotations balance"
    },
    {
        "id": "distractor_taylor_swift",
        "title": "Pop Culture / False Cognate Trap: Taylor Expansion Tour",
        "domain": "Distractor",
        "text": (
            "The Taylor global tour series expanded across multiple stadiums in 2024, breaking attendance records. "
            "The concert series remainder of dates sold out in minutes with infinite power and high derivative demand."
        ),
        "is_distractor": True,
        "target_query_trap": "taylor series power expansion remainder"
    }
]

# Benchmark Queries
BENCHMARK_QUERIES = [
    # 1. Exact Lexical Queries
    {
        "query": "Einstein photoelectric effect threshold frequency work function Planck",
        "expected_chunk_id": "phys_photoelectric",
        "query_type": "exact_lexical"
    },
    {
        "query": "Heisenberg uncertainty principle position and momentum reduced Planck constant",
        "expected_chunk_id": "phys_heisenberg",
        "query_type": "exact_lexical"
    },
    {
        "query": "Red-black tree invariants root black node rotations color flips",
        "expected_chunk_id": "cs_red_black_tree",
        "query_type": "exact_lexical"
    },
    {
        "query": "Dijkstra algorithm min-priority queue edge relaxation non-negative weights",
        "expected_chunk_id": "cs_dijkstra",
        "query_type": "exact_lexical"
    },
    {
        "query": "Transformer scaled dot-product attention softmax Q K V",
        "expected_chunk_id": "cs_transformer_attention",
        "query_type": "exact_lexical"
    },
    {
        "query": "CRISPR Cas9 single guide RNA PAM sequence double-strand break",
        "expected_chunk_id": "bio_crispr",
        "query_type": "exact_lexical"
    },
    {
        "query": "Citric acid cycle Krebs mitochondrial matrix acetyl-CoA NADH ATP",
        "expected_chunk_id": "bio_krebs_cycle",
        "query_type": "exact_lexical"
    },
    {
        "query": "Taylor series expansion Lagrange remainder Maclaurin power series",
        "expected_chunk_id": "math_taylor_series",
        "query_type": "exact_lexical"
    },
    {
        "query": "Characteristic polynomial determinant eigenvalues and eigenvectors diagonalization",
        "expected_chunk_id": "math_eigenvalues",
        "query_type": "exact_lexical"
    },

    # 2. Paraphrased / Semantic Queries
    {
        "query": "How light quanta eject electrons from metallic surfaces depending on color rather than brightness",
        "expected_chunk_id": "phys_photoelectric",
        "query_type": "paraphrased_semantic"
    },
    {
        "query": "Fundamental quantum impossibility of simultaneously measuring where a particle is located and how fast it travels",
        "expected_chunk_id": "phys_heisenberg",
        "query_type": "paraphrased_semantic"
    },
    {
        "query": "Self-balancing hierarchical search structure with chromatic constraints ensuring logarithmic depth",
        "expected_chunk_id": "cs_red_black_tree",
        "query_type": "paraphrased_semantic"
    },
    {
        "query": "Greedy routing procedure finding least costly trajectories across network nodes without negative links",
        "expected_chunk_id": "cs_dijkstra",
        "query_type": "paraphrased_semantic"
    },
    {
        "query": "Neural mechanism calculating pairwise token relevance scores normalized by square root dimension",
        "expected_chunk_id": "cs_transformer_attention",
        "query_type": "paraphrased_semantic"
    },
    {
        "query": "Targeted molecular scissors cutting double-stranded cellular genetic code guided by synthetic sequences",
        "expected_chunk_id": "bio_crispr",
        "query_type": "paraphrased_semantic"
    },
    {
        "query": "Cellular respiration pathway turning acetate into carbon dioxide while generating reducing equivalents",
        "expected_chunk_id": "bio_krebs_cycle",
        "query_type": "paraphrased_semantic"
    },
    {
        "query": "Approximating smooth continuous mathematical curves through infinite polynomial summation around a baseline",
        "expected_chunk_id": "math_taylor_series",
        "query_type": "paraphrased_semantic"
    },

    # 3. Adversarial Distractor Trap Queries
    {
        "query": "dijkstra algorithm shortest path min-heap",
        "expected_chunk_id": "cs_dijkstra",
        "distractor_trap_id": "distractor_lexical_trap_dijkstra",
        "query_type": "adversarial_trap"
    },
    {
        "query": "crispr cas9 guide rna double strand break endonuclease",
        "expected_chunk_id": "bio_crispr",
        "distractor_trap_id": "distractor_keyword_stuffing_crispr",
        "query_type": "adversarial_trap"
    },
    {
        "query": "photoelectric effect work function frequency",
        "expected_chunk_id": "phys_photoelectric",
        "distractor_trap_id": "distractor_negation_photoelectric",
        "query_type": "adversarial_trap"
    },
    {
        "query": "red-black tree node rotations balance",
        "expected_chunk_id": "cs_red_black_tree",
        "distractor_trap_id": "distractor_cross_domain_tree",
        "query_type": "adversarial_trap"
    },
    {
        "query": "taylor series power expansion remainder polynomial",
        "expected_chunk_id": "math_taylor_series",
        "distractor_trap_id": "distractor_taylor_swift",
        "query_type": "adversarial_trap"
    },

    # 4. Multilingual Hindi Query
    {
        "query": "पौधों में प्रकाश संश्लेषण क्लोरोप्लास्ट और पर्णहरित",
        "expected_chunk_id": "hindi_photosynthesis",
        "query_type": "multilingual_hindi"
    }
]


# =============================================================================
# 2. BENCHMARK EXECUTION ENGINE
# =============================================================================

def run_retrieval_benchmarks() -> Dict[str, Any]:
    print("=" * 80)
    print("STARTING ADVERSARIAL RETRIEVAL & PERFORMANCE BENCHMARK (MILESTONE 1)")
    print("=" * 80)

    # 1. Build Index with the benchmark corpus
    chunks = [
        DocumentChunk(
            chunk_id=item["id"],
            document_id="doc_bench_001",
            source_filename=f"{item['title']}.txt",
            page_or_slide=i + 1,
            section_title=item["title"],
            text=item["text"],
            chunk_index=i
        )
        for i, item in enumerate(BENCHMARK_CORPUS)
    ]

    print(f"\n[1] Indexing {len(chunks)} multi-paragraph educational & distractor chunks...")
    index = DocumentVectorIndex(target_id="doc_bench_001")
    t0 = time.perf_counter()
    index.build_index(chunks)
    index_build_time_ms = (time.perf_counter() - t0) * 1000.0
    print(f"    Index build complete in {index_build_time_ms:.2f} ms.")

    # 2. Evaluate Retrieval Modes
    retrieval_modes = {
        "pure_vector_alpha_1.0": 1.0,
        "pure_bm25_alpha_0.0": 0.0,
        "hybrid_alpha_0.6": 0.6,
        "hybrid_alpha_0.75": 0.75,
        "hybrid_alpha_0.3": 0.3
    }

    mode_results: Dict[str, Any] = {}

    for mode_name, alpha in retrieval_modes.items():
        print(f"\n--- Evaluating Retrieval Mode: {mode_name} (alpha={alpha}) ---")
        
        recall_at_1 = 0
        recall_at_3 = 0
        recall_at_5 = 0
        mrr_sum = 0.0
        precision_at_3_sum = 0.0
        distractor_in_top_3_count = 0
        query_latencies_ms: List[float] = []

        query_details = []

        for q_item in BENCHMARK_QUERIES:
            q_text = q_item["query"]
            expected_id = q_item["expected_chunk_id"]
            q_type = q_item["query_type"]
            distractor_id = q_item.get("distractor_trap_id")

            t_start = time.perf_counter()
            results = index.search(query=q_text, top_k=5, alpha=alpha)
            t_elapsed_ms = (time.perf_counter() - t_start) * 1000.0
            query_latencies_ms.append(t_elapsed_ms)

            retrieved_ids = [r.chunk_id for r in results]
            
            # Recall@k
            r1 = 1 if expected_id in retrieved_ids[:1] else 0
            r3 = 1 if expected_id in retrieved_ids[:3] else 0
            r5 = 1 if expected_id in retrieved_ids[:5] else 0
            recall_at_1 += r1
            recall_at_3 += r3
            recall_at_5 += r5

            # MRR
            if expected_id in retrieved_ids:
                rank = retrieved_ids.index(expected_id) + 1
                mrr = 1.0 / rank
            else:
                mrr = 0.0
            mrr_sum += mrr

            # Precision@3
            p3 = 1.0 / 3.0 if expected_id in retrieved_ids[:3] else 0.0
            precision_at_3_sum += p3

            # Distractor intrusion in top 3
            distractor_in_top_3 = False
            if distractor_id and distractor_id in retrieved_ids[:3]:
                distractor_in_top_3 = True
                distractor_in_top_3_count += 1

            query_details.append({
                "query": q_text,
                "type": q_type,
                "expected": expected_id,
                "retrieved_top3": retrieved_ids[:3],
                "rank": (retrieved_ids.index(expected_id) + 1) if expected_id in retrieved_ids else -1,
                "latency_ms": round(t_elapsed_ms, 3),
                "distractor_trap_in_top3": distractor_in_top_3
            })

        n_q = len(BENCHMARK_QUERIES)
        avg_r1 = recall_at_1 / n_q
        avg_r3 = recall_at_3 / n_q
        avg_r5 = recall_at_5 / n_q
        avg_mrr = mrr_sum / n_q
        avg_p3 = precision_at_3_sum / n_q
        
        trap_queries_count = sum(1 for q in BENCHMARK_QUERIES if q.get("distractor_trap_id"))
        distractor_intrusion_rate = (distractor_in_top_3_count / max(1, trap_queries_count)) * 100.0

        lat_mean = float(np.mean(query_latencies_ms))
        lat_p50 = float(np.percentile(query_latencies_ms, 50))
        lat_p95 = float(np.percentile(query_latencies_ms, 95))
        lat_p99 = float(np.percentile(query_latencies_ms, 99))
        lat_max = float(np.max(query_latencies_ms))

        print(f"  Recall@1: {avg_r1*100:.1f}% ({recall_at_1}/{n_q})")
        print(f"  Recall@3: {avg_r3*100:.1f}% ({recall_at_3}/{n_q})")
        print(f"  Recall@5: {avg_r5*100:.1f}% ({recall_at_5}/{n_q})")
        print(f"  MRR (Mean Reciprocal Rank): {avg_mrr:.4f}")
        print(f"  Distractor Intrusion in Top-3: {distractor_intrusion_rate:.1f}% ({distractor_in_top_3_count}/{trap_queries_count})")
        print(f"  Latency: Mean={lat_mean:.3f}ms | P50={lat_p50:.3f}ms | P95={lat_p95:.3f}ms | P99={lat_p99:.3f}ms | Max={lat_max:.3f}ms")

        mode_results[mode_name] = {
            "alpha": alpha,
            "recall_at_1": round(avg_r1, 4),
            "recall_at_3": round(avg_r3, 4),
            "recall_at_5": round(avg_r5, 4),
            "mrr": round(avg_mrr, 4),
            "precision_at_3": round(avg_p3, 4),
            "distractor_intrusion_rate_percent": round(distractor_intrusion_rate, 2),
            "latency": {
                "mean_ms": round(lat_mean, 3),
                "p50_ms": round(lat_p50, 3),
                "p95_ms": round(lat_p95, 3),
                "p99_ms": round(lat_p99, 3),
                "max_ms": round(lat_max, 3)
            },
            "query_details": query_details
        }

    # 3. Query Type Breakdown (for hybrid alpha=0.6)
    print("\n" + "=" * 80)
    print("[2] PERFORMANCE BREAKDOWN BY QUERY CATEGORY (Hybrid alpha=0.6)")
    print("=" * 80)
    
    hybrid_details = mode_results["hybrid_alpha_0.6"]["query_details"]
    categories = ["exact_lexical", "paraphrased_semantic", "adversarial_trap", "multilingual_hindi"]
    category_summary = {}

    for cat in categories:
        cat_items = [q for q in hybrid_details if q["type"] == cat]
        if not cat_items:
            continue
        cat_r1 = sum(1 for q in cat_items if q["rank"] == 1)
        cat_r3 = sum(1 for q in cat_items if 1 <= q["rank"] <= 3)
        cat_mrr = sum(1.0 / q["rank"] if q["rank"] > 0 else 0.0 for q in cat_items) / len(cat_items)
        cat_lat = float(np.mean([q["latency_ms"] for q in cat_items]))
        print(f"  Category '{cat}': (N={len(cat_items)})")
        print(f"    Recall@1: {cat_r1/len(cat_items)*100:.1f}% | Recall@3: {cat_r3/len(cat_items)*100:.1f}% | MRR: {cat_mrr:.4f} | Avg Latency: {cat_lat:.3f}ms")
        category_summary[cat] = {
            "count": len(cat_items),
            "recall_at_1": round(cat_r1 / len(cat_items), 4),
            "recall_at_3": round(cat_r3 / len(cat_items), 4),
            "mrr": round(cat_mrr, 4),
            "avg_latency_ms": round(cat_lat, 3)
        }

    # 4. Latency Scaling & Stress Benchmarks across Corpus Sizes
    print("\n" + "=" * 80)
    print("[3] LATENCY & MEMORY SCALING BENCHMARKS (< 5ms SLA VERIFICATION)")
    print("=" * 80)

    corpus_sizes = [10, 50, 100, 250, 500, 1000]
    scaling_results = []

    for size in corpus_sizes:
        synth_chunks = []
        for i in range(size):
            domain_idx = i % 5
            domains = ["Calculus", "Photosynthesis", "Binary Trees", "Quantum Physics", "Renaissance"]
            synth_chunks.append(
                DocumentChunk(
                    chunk_id=f"chk_scale_{size}_{i:04d}",
                    document_id=f"doc_scale_{size}",
                    source_filename=f"doc_{domains[domain_idx]}.txt",
                    page_or_slide=(i // 5) + 1,
                    section_title=f"Section {i} on {domains[domain_idx]}",
                    text=f"Paragraph {i}: In the study of {domains[domain_idx]}, we analyze mathematical models, algorithmic complexity, and physiological equations.",
                    chunk_index=i
                )
            )

        tracemalloc.start()
        t_build_start = time.perf_counter()
        scale_index = DocumentVectorIndex(target_id=f"doc_scale_{size}")
        scale_index.build_index(synth_chunks)
        t_build_ms = (time.perf_counter() - t_build_start) * 1000.0
        current_mem, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        latencies_ms = []
        vec_component_latencies_ms = []
        bm25_component_latencies_ms = []
        dot_product_latencies_ms = []

        test_queries = [
            "mathematical models and algorithmic complexity in binary trees",
            "physiological equations in photosynthesis study",
            "properties of structured learning in quantum physics",
            "Renaissance historical analysis of educational concepts"
        ]

        for iter_idx in range(50):
            q = test_queries[iter_idx % len(test_queries)]
            
            t0 = time.perf_counter()
            # 1. Vector embedding
            t_v0 = time.perf_counter()
            q_emb = llm_client.generate_embeddings([q])[0]
            t_v1 = time.perf_counter()
            vec_component_latencies_ms.append((t_v1 - t_v0) * 1000.0)

            # 2. Dot product
            t_d0 = time.perf_counter()
            q_vec = np.array(q_emb, dtype=np.float32)
            q_norm = np.linalg.norm(q_vec)
            if q_norm > 0:
                q_vec = q_vec / q_norm
            cos_scores = np.dot(scale_index.embeddings, q_vec)
            vec_scores = np.clip((cos_scores + 1.0) / 2.0, 0.0, 1.0)
            t_d1 = time.perf_counter()
            dot_product_latencies_ms.append((t_d1 - t_d0) * 1000.0)

            # 3. BM25
            t_b0 = time.perf_counter()
            bm25_scores = np.array(scale_index.bm25.score(q), dtype=np.float32)
            t_b1 = time.perf_counter()
            bm25_component_latencies_ms.append((t_b1 - t_b0) * 1000.0)

            # 4. Hybrid & Top-k
            hybrid_scores = 0.6 * vec_scores + 0.4 * bm25_scores
            top_indices = np.argsort(hybrid_scores)[::-1][:4]
            t_end = time.perf_counter()

            total_ms = (t_end - t0) * 1000.0
            latencies_ms.append(total_ms)

        mean_lat = float(np.mean(latencies_ms))
        p50_lat = float(np.percentile(latencies_ms, 50))
        p95_lat = float(np.percentile(latencies_ms, 95))
        p99_lat = float(np.percentile(latencies_ms, 99))
        max_lat = float(np.max(latencies_ms))

        avg_vec_emb = float(np.mean(vec_component_latencies_ms))
        avg_dot_prod = float(np.mean(dot_product_latencies_ms))
        avg_bm25 = float(np.mean(bm25_component_latencies_ms))

        sla_pass = mean_lat < 5.0 and p95_lat < 5.0

        print(f"  Corpus Size: {size:4d} chunks | Build Time: {t_build_ms:6.2f}ms | Peak Mem: {peak_mem / 1024:.1f}KB")
        print(f"    Hybrid Latency: Mean={mean_lat:.3f}ms | P50={p50_lat:.3f}ms | P95={p95_lat:.3f}ms | P99={p99_lat:.3f}ms | Max={max_lat:.3f}ms")
        print(f"    Breakdown: Dense Projection={avg_vec_emb:.3f}ms | Matrix Dot-Prod={avg_dot_prod:.3f}ms | BM25 Score={avg_bm25:.3f}ms")
        print(f"    SLA Status (< 5.0ms): {'PASS [OK]' if sla_pass else 'FAIL [EXCEEDED]'}")

        scaling_results.append({
            "corpus_size": size,
            "build_time_ms": round(t_build_ms, 2),
            "peak_memory_kb": round(peak_mem / 1024, 2),
            "latency": {
                "mean_ms": round(mean_lat, 3),
                "p50_ms": round(p50_lat, 3),
                "p95_ms": round(p95_lat, 3),
                "p99_ms": round(p99_lat, 3),
                "max_ms": round(max_lat, 3)
            },
            "breakdown": {
                "dense_projection_ms": round(avg_vec_emb, 3),
                "matrix_dot_product_ms": round(avg_dot_prod, 3),
                "bm25_score_ms": round(avg_bm25, 3)
            },
            "sla_5ms_pass": sla_pass
        })

    # 5. Alpha Parameter Sensitivity Analysis
    print("\n" + "=" * 80)
    print("[4] ALPHA PARAMETER SENSITIVITY CURVE (Vector vs BM25 Weight)")
    print("=" * 80)
    
    alpha_steps = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    alpha_sensitivity = []

    for a_val in alpha_steps:
        r1_c = 0
        r3_c = 0
        mrr_c = 0.0
        for q_item in BENCHMARK_QUERIES:
            res = index.search(query=q_item["query"], top_k=3, alpha=a_val)
            r_ids = [r.chunk_id for r in res]
            expected = q_item["expected_chunk_id"]
            if expected in r_ids[:1]:
                r1_c += 1
            if expected in r_ids[:3]:
                r3_c += 1
            if expected in r_ids:
                mrr_c += 1.0 / (r_ids.index(expected) + 1)
        
        n_queries = len(BENCHMARK_QUERIES)
        a_r1 = r1_c / n_queries
        a_r3 = r3_c / n_queries
        a_mrr = mrr_c / n_queries
        print(f"  Alpha = {a_val:3.1f} | Recall@1: {a_r1*100:5.1f}% | Recall@3: {a_r3*100:5.1f}% | MRR: {a_mrr:.4f}")
        alpha_sensitivity.append({
            "alpha": a_val,
            "recall_at_1": round(a_r1, 4),
            "recall_at_3": round(a_r3, 4),
            "mrr": round(a_mrr, 4)
        })

    report_payload = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "milestone": "Milestone 1",
        "benchmark_modes": mode_results,
        "category_summary": category_summary,
        "scaling_benchmarks": scaling_results,
        "alpha_sensitivity": alpha_sensitivity,
        "verdict": "APPROVE" if all(s["sla_5ms_pass"] for s in scaling_results) and mode_results["hybrid_alpha_0.6"]["recall_at_3"] >= 0.80 else "REJECT"
    }

    return report_payload


if __name__ == "__main__":
    benchmark_data = run_retrieval_benchmarks()
    output_path = os.path.join(PROJECT_ROOT, "test_scripts", "retrieval_benchmark_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(benchmark_data, f, indent=2)
    print(f"\n[+] Benchmark complete. Saved full report to {output_path}")
    print(f"Verdict: {benchmark_data['verdict']}")
