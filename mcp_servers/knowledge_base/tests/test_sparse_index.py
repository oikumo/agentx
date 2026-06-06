"""Tests for ``kb.sparse_index`` (BM25 sparse retrieval).

Requires the ``bm25s`` optional dependency.
"""

import pytest

pytest.importorskip("bm25s", reason="bm25s is required for sparse index tests")

from kb.sparse_index import (
    SparseRetriever,
    SparseResult,
    get_default_retriever,
    set_default_retriever,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def retriever():
    """A fresh ``SparseRetriever``."""
    return SparseRetriever()


@pytest.fixture
def sample_corpus():
    return [
        "The quick brown fox jumps over the lazy dog",
        "A quick brown rabbit jumps over the sleepy cat",
        "The lazy cat sleeps all day",
        "The dog barks at the mailman",
    ]


@pytest.fixture
def sample_ids():
    return ["ID-001", "ID-002", "ID-003", "ID-004"]


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

def test_bm25s_available():
    """The module correctly detects whether bm25s is installed."""
    from kb.sparse_index import BM25S_AVAILABLE
    assert BM25S_AVAILABLE is True


def test_retriever_initially_empty(retriever):
    assert retriever.is_built is False
    assert retriever.size == 0


def test_build_index_sets_state(retriever, sample_corpus, sample_ids):
    retriever.build_index(sample_corpus, sample_ids)
    assert retriever.is_built is True
    assert retriever.size == 4


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def test_search_returns_relevant_docs(retriever, sample_corpus, sample_ids):
    retriever.build_index(sample_corpus, sample_ids)
    results = retriever.search("quick brown fox", top_k=3)

    assert len(results) > 0
    # The best match should be ID-001 (contains "quick", "brown", "fox")
    assert results[0].id == "ID-001"
    assert results[0].score > 0


def test_search_before_build_returns_empty(retriever):
    results = retriever.search("anything")
    assert results == []


def test_search_empty_query_returns_empty(retriever, sample_corpus, sample_ids):
    retriever.build_index(sample_corpus, sample_ids)
    assert retriever.search("") == []
    assert retriever.search("   ") == []


def test_search_respects_top_k(retriever, sample_corpus, sample_ids):
    retriever.build_index(sample_corpus, sample_ids)
    results = retriever.search("dog", top_k=2)
    assert len(results) <= 2


def test_search_returns_sparseresult_objects(retriever, sample_corpus, sample_ids):
    retriever.build_index(sample_corpus, sample_ids)
    results = retriever.search("quick", top_k=3)
    for r in results:
        assert isinstance(r, SparseResult)
        assert isinstance(r.id, str)
        assert isinstance(r.score, float)
        assert isinstance(r.metadata, dict)


def test_search_lexical_exact_match_outranks_partial(retriever):
    """BM25 should rank documents containing all query terms higher."""
    corpus = [
        "Python is a programming language",
        "Java is also a programming language",
        "Python is the best language for data science",
    ]
    doc_ids = ["PY-01", "JV-01", "PY-02"]
    retriever.build_index(corpus, doc_ids)

    results = retriever.search("python language", top_k=3)
    assert len(results) >= 2
    # Both PY-01 and PY-02 should appear before JV-01
    py_results = [r for r in results if r.id.startswith("PY")]
    jv_results = [r for r in results if r.id.startswith("JV")]
    assert len(py_results) >= 2
    # All PY docs should rank above JV
    max_py_rank = max(results.index(r) for r in py_results)
    min_jv_rank = min(results.index(r) for r in jv_results) if jv_results else len(results)
    assert max_py_rank < min_jv_rank, "Python docs should rank above Java docs"


# ---------------------------------------------------------------------------
# Incremental add
# ---------------------------------------------------------------------------

def test_add_documents_on_empty_builds(retriever):
    retriever.add_documents(["single doc"], ["NEW-001"])
    assert retriever.is_built is True
    assert retriever.size == 1


def test_add_documents_appends_and_reranks(retriever, sample_corpus, sample_ids):
    retriever.build_index(sample_corpus, sample_ids)
    assert retriever.size == 4

    # Add a new document that should match "fox"
    retriever.add_documents(
        ["A fox and a dog are friends"],
        ["ID-005"],
    )
    assert retriever.size == 5

    results = retriever.search("fox", top_k=5)
    result_ids = [r.id for r in results]
    assert "ID-005" in result_ids  # new doc contains "fox"


def test_add_documents_empty_texts_does_nothing(retriever, sample_corpus, sample_ids):
    retriever.build_index(sample_corpus, sample_ids)
    retriever.add_documents([], [])
    assert retriever.size == 4


def test_add_documents_mismatched_length_raises(retriever):
    retriever.build_index(["doc1"], ["A"])
    with pytest.raises(ValueError, match="length"):
        retriever.add_documents(["doc2", "doc3"], ["B"])


# ---------------------------------------------------------------------------
# Build validation
# ---------------------------------------------------------------------------

def test_build_index_mismatched_length_raises(retriever):
    with pytest.raises(ValueError, match="length"):
        retriever.build_index(["doc1", "doc2"], ["A"])


def test_build_index_empty_corpus(retriever):
    """Rebuilding with empty corpus should clear the index."""
    retriever.build_index(["existing"], ["E-001"])
    assert retriever.is_built

    retriever.build_index([], [])
    assert retriever.is_built is False
    assert retriever.size == 0


# ---------------------------------------------------------------------------
# Clear
# ---------------------------------------------------------------------------

def test_clear_resets_index(retriever, sample_corpus, sample_ids):
    retriever.build_index(sample_corpus, sample_ids)
    assert retriever.is_built

    retriever.clear()
    assert retriever.is_built is False
    assert retriever.size == 0
    assert retriever.search("anything") == []


# ---------------------------------------------------------------------------
# Default retriever
# ---------------------------------------------------------------------------

def test_get_default_retriever_returns_instance():
    r = get_default_retriever()
    assert r is not None
    assert isinstance(r, SparseRetriever)


def test_set_default_retriever_overrides():
    custom = SparseRetriever()
    set_default_retriever(custom)
    try:
        assert get_default_retriever() is custom
    finally:
        set_default_retriever(None)
