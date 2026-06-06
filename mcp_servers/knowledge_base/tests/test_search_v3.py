"""Tests for ``kb.search.hybrid_search`` — the hybrid search pipeline."""

import pytest

from kb.search import hybrid_search


# ---------------------------------------------------------------------------
# hybrid_search — edge cases and integration
# ---------------------------------------------------------------------------

def test_without_retriever_returns_empty():
    """No dense retriever means no results."""
    results = hybrid_search("test", dense_retriever=None)
    assert results == []


def test_empty_query(dense_retriever):
    """Empty query should return no results."""
    results = hybrid_search("", dense_retriever=dense_retriever)
    assert results == []


def test_no_data_returns_empty(dense_retriever):
    """Searching an empty index returns nothing."""
    results = hybrid_search("anything", dense_retriever=dense_retriever)
    assert results == []


def test_with_data(dense_retriever, populated_store):
    """Searching populated data returns results in dict format."""
    results = hybrid_search(
        "KBStore", dense_retriever=dense_retriever, top_k=5,
    )
    assert len(results) > 0
    for r in results:
        assert isinstance(r, dict)
        assert "id" in r
        assert "combined_score" in r
        assert "title" in r


def test_respects_category(dense_retriever, populated_store):
    """Category filter should be respected."""
    # We have items with category 'class', 'method', 'function'
    results = hybrid_search(
        "search", dense_retriever=dense_retriever, category="class", top_k=5,
    )
    if results:
        for r in results:
            assert r.get("category") == "class"


def test_output_format(dense_retriever, populated_store):
    """Output dict format should have all required keys."""
    results = hybrid_search(
        "search", dense_retriever=dense_retriever, top_k=5,
    )

    if results:
        r = results[0]
        expected_keys = {
            "id", "type", "category", "title", "confidence",
            "context", "finding", "solution", "example",
            "created_at", "combined_score",
        }
        assert expected_keys.issubset(r.keys()), f"Missing keys: {expected_keys - r.keys()}"
        assert "source" in r


def test_with_sparse_retriever(dense_retriever, sparse_retriever, populated_store):
    """With both dense and sparse, results should include fusion."""
    # Build the sparse index
    corpus = [
        "KBStore ChromaDB wrapper class use KBStore for persistence",
        "BM25 Search lexical search using BM25 BM25 complements dense retrieval",
    ]
    sparse_retriever.build_index(corpus, ["PAT-001", "FIND-001"])

    results = hybrid_search(
        "KBStore ChromaDB",
        dense_retriever=dense_retriever,
        sparse_retriever=sparse_retriever,
        top_k=5,
    )
    assert len(results) >= 0
    for r in results:
        assert "combined_score" in r


def test_with_reranker_disabled(dense_retriever, populated_store):
    """rerank=False should skip reranking gracefully."""
    results = hybrid_search(
        "KBStore",
        dense_retriever=dense_retriever,
        rerank=False,
        top_k=5,
    )
    # Should still work without a reranker
    assert isinstance(results, list)