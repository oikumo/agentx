"""Hybrid retrieval and scoring against a ChromaDB collection.

This module owns the single copy of:

* tokenisation
* keyword scoring (`keyword_score`)
* semantic field-weighted boost (`semantic_boost`)
* the final `hybrid_search` combination

These functions are pure (collection in, list-of-dicts out) so they are
straightforward to unit-test without touching ChromaDB internals.
"""

import re
from datetime import datetime
from typing import List, Dict, Optional


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


def hybrid_search(collection, query: str, category: Optional[str] = None,
                  top_k: int = 5) -> List[Dict]:
    """Run a hybrid vector + lexical search against a Chroma collection.

    Returns a list of plain dicts already sorted by descending combined score.
    Errors are swallowed and logged through `kb.logging` (Phase 5); a search
    failure returns an empty list so callers can degrade gracefully.
    """
    from .logging import get_logger
    logger = get_logger()

    try:
        where_filter = {"category": category} if category else None

        results = collection.query(
            query_texts=[query],
            n_results=top_k * 3,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        if not (results and results["ids"] and results["ids"][0]):
            return []

        ids = results["ids"][0]
        documents = results["documents"][0] if results["documents"] else []
        metadatas = results["metadatas"][0] if results["metadatas"] else []
        distances = results["distances"][0] if results["distances"] else []

        scored = []
        for i, doc_id in enumerate(ids):
            if i >= len(documents):
                continue
            metadata = metadatas[i] if i < len(metadatas) else {}
            distance = distances[i] if i < len(distances) else 1.0
            similarity_score = 1.0 / (1.0 + distance) if distance else 1.0
            doc_text = documents[i]
            kw = keyword_score(doc_text, query)

            entry = {
                "id": metadata.get("entry_id", doc_id),
                "type": metadata.get("type", "unknown"),
                "category": metadata.get("category", "general"),
                "title": metadata.get("title", doc_id),
                "confidence": float(metadata.get("confidence", 0.5)),
                "context": metadata.get("context", ""),
                "finding": metadata.get("finding", ""),
                "solution": metadata.get("solution", ""),
                "example": metadata.get("example", ""),
                "created_at": metadata.get("created_at", datetime.now().isoformat()),
            }

            sem = semantic_boost(entry, query)
            recency = _recency_bonus(entry["created_at"])
            tmb = _title_match_bonus(entry["title"], query)

            combined = (
                0.30 * similarity_score
                + 0.20 * kw
                + 0.15 * sem
                + 0.15 * entry["confidence"]
                + 0.10 * recency
                + 0.10 * tmb
            )
            entry["combined_score"] = combined
            scored.append((combined, entry))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [e for _, e in scored[:top_k]]
    except Exception as exc:
        logger.error("ChromaDB search error: %s", exc)
        return []
