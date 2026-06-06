"""Hybrid retrieval and scoring against a ChromaDB collection.

This module provides the hybrid search pipeline for the Knowledge Base:

* tokenisation
* keyword scoring (`keyword_score`)
* semantic field-weighted boost (`semantic_boost`)
* the ``hybrid_search`` function (dense + sparse + RRF fusion + optional reranker)

All search operations use the v4 retrieval pipeline with hybrid scoring.
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from .logging import get_logger


# ---------------------------------------------------------------------------
# Tokenisation helpers
# ---------------------------------------------------------------------------

def simple_tokenize(text: str) -> List[str]:
    """Lowercase word-level tokeniser."""
    return re.findall(r"\b\w+\b", text.lower()) if text else []


def keyword_score(text: str, query: str) -> float:
    """Score how well `text` matches `query` using token overlap.

    Combines token coverage, specificity and an exact-substring bonus.
    Returns a value in [0, 1].
    """
    if not text or not query:
        return 0.0

    text_tokens = simple_tokenize(text)
    query_tokens = simple_tokenize(query)
    if not query_tokens or not text_tokens:
        return 0.0

    text_set = set(text_tokens)
    query_set = set(query_tokens)
    matches = len(text_set & query_set)

    exact_match_bonus = 0.2 if query.lower() in text.lower() else 0.0
    coverage = matches / len(query_set) if query_set else 0.0
    specificity = matches / len(text_set) if text_set else 0.0

    return min(1.0, 0.5 * coverage + 0.3 * specificity + 0.2 * exact_match_bonus)


def semantic_boost(entry: Dict, query: str) -> float:
    """Field-weighted semantic boost.

    Title matches count more than finding/solution matches, which count more
    than context matches. Returned value is in roughly [0.8, 1.2].
    """
    query_tokens = set(simple_tokenize(query))

    title = entry.get("title", "").lower()
    title_tokens = set(simple_tokenize(title))
    title_match = len(title_tokens & query_tokens) / max(1, len(query_tokens))

    core_text = f"{entry.get('finding', '')} {entry.get('solution', '')}".lower()
    core_tokens = set(simple_tokenize(core_text))
    core_match = len(core_tokens & query_tokens) / max(1, len(query_tokens))

    context = entry.get("context", "").lower()
    context_tokens = set(simple_tokenize(context))
    context_match = len(context_tokens & query_tokens) / max(1, len(query_tokens))

    semantic_score = 0.5 * title_match + 0.35 * core_match + 0.15 * context_match
    return 0.8 + (semantic_score * 0.4)


def _title_match_bonus(title: str, query: str) -> float:
    title = title.lower()
    if query.lower() in title:
        return 2.0
    tokens = simple_tokenize(query)
    matched = [t for t in tokens if t in title]
    if len(matched) >= 2:
        return 1.0
    if matched:
        return 0.5
    return 0.0


def _recency_bonus(created_at: str) -> float:
    try:
        created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        days_old = (datetime.now() - created).days
        return 1.0 / (1.0 + 0.01 * days_old)
    except Exception:
        return 1.0


# ---------------------------------------------------------------------------
# Hybrid search pipeline (v4)
# ---------------------------------------------------------------------------

def hybrid_search(
    query: str,
    dense_retriever: Any,  # DenseRetriever from kb.retrieval
    sparse_retriever: Any = None,  # SparseRetriever from kb.sparse_index
    reranker: Any = None,  # CrossEncoderReranker from kb.reranking
    top_k: int = 5,
    category: Optional[str] = None,
    dense_top_k: Optional[int] = None,
    sparse_top_k: Optional[int] = None,
    rerank: bool = True,
    fusion_k: int = 60,
) -> List[Dict]:
    """Hybrid search: dense → sparse → RRF fusion → optional reranker.

    This is the v4 search pipeline using hybrid retrieval with reciprocal
    rank fusion and optional cross-encoder reranking.

    Args:
        query: The search query.
        dense_retriever: A configured ``DenseRetriever`` instance.
        sparse_retriever: Optional ``SparseRetriever`` instance. If None,
                          only dense search is used.
        reranker: Optional ``CrossEncoderReranker`` instance. If None,
                  skipping reranking.
        top_k: Final number of results to return.
        category: Optional category filter for dense retrieval.
        dense_top_k: Candidates from dense (default: top_k * 2).
        sparse_top_k: Candidates from sparse (default: top_k * 2).
        rerank: Whether to apply reranking (if reranker is available).
        fusion_k: RRF constant.

    Returns:
        List of dicts with search results sorted by relevance.
    """
    from .retrieval import hybrid_retrieve

    try:
        # Step 1: Dense + sparse retrieval + RRF fusion
        fused = hybrid_retrieve(
            query=query,
            dense_retriever=dense_retriever,
            sparse_retriever=sparse_retriever,
            top_k=top_k,
            dense_top_k=dense_top_k or top_k * 2,
            sparse_top_k=sparse_top_k or top_k * 2,
            category=category,
            fusion_k=fusion_k,
        )

        if not fused:
            return []

        # Step 2: Optional reranking
        if rerank and reranker is not None:
            try:
                reranked = reranker.rerank(
                    query=query,
                    candidates=fused,
                    top_k=top_k,
                    text_fn=lambda r: r.text,
                )
                # Map reranked results back to our dict format
                result_map = {r.id: r for r in fused}
                final_results: List[Dict] = []
                seen_ids: set = set()

                for rr in reranked:
                    if rr.id in result_map:
                        final_results.append(
                            _retrieval_result_to_dict(result_map[rr.id], rr.score)
                        )
                        seen_ids.add(rr.id)

                # Fill any remaining slots from fused (non-reranked)
                for fr in fused:
                    if len(final_results) >= top_k:
                        break
                    if fr.id not in seen_ids:
                        final_results.append(
                            _retrieval_result_to_dict(fr, fr.score)
                        )
                        seen_ids.add(fr.id)

                return final_results

            except ImportError:
                get_logger().warning(
                    "Reranker not available (sentence-transformers missing). "
                    "Falling back to fused results."
                )
            except Exception as exc:
                get_logger().warning("Reranking failed (falling back): %s", exc)

        # Step 3: No reranking — return fused results as-is
        return [
            _retrieval_result_to_dict(r, r.score)
            for r in fused
        ]

    except Exception as exc:
        get_logger().error("hybrid_search failed: %s", exc)
        return []


# ---------------------------------------------------------------------------
# Result conversion helper
# ---------------------------------------------------------------------------

def _retrieval_result_to_dict(rr: Any, score: float) -> Dict[str, Any]:
    """Convert a ``RetrievalResult`` (or similar) to dict format."""
    meta = rr.metadata if hasattr(rr, 'metadata') else {}
    return {
        "id": rr.id if hasattr(rr, 'id') else "unknown",
        "type": meta.get("type", "unknown"),
        "category": meta.get("category", "general"),
        "title": meta.get("title", rr.id),
        "confidence": float(meta.get("confidence", 0.5)),
        "context": meta.get("context", ""),
        "finding": meta.get("finding", ""),
        "solution": meta.get("solution", ""),
        "example": meta.get("example", ""),
        "created_at": meta.get("created_at", datetime.now().isoformat()),
        "combined_score": score,
        "source": rr.source if hasattr(rr, 'source') else "hybrid",
    }