"""Tests for ``kb.reranking`` — CrossEncoderReranker."""

import pytest

from kb.reranking import (
    CrossEncoderReranker,
    RerankerResult,
    SENTENCE_TRANSFORMERS_AVAILABLE,
)


# ---------------------------------------------------------------------------
# Module-level detection
# ---------------------------------------------------------------------------

def test_sentence_transformers_detection():
    """The module correctly reports availability."""
    # This test just verifies the boolean exists
    assert isinstance(SENTENCE_TRANSFORMERS_AVAILABLE, bool)


# ---------------------------------------------------------------------------
# CrossEncoderReranker — construction
# ---------------------------------------------------------------------------

def test_reranker_init_default():
    r = CrossEncoderReranker()
    assert r.model_name == "ms-marco-MiniLM-L6-v2"
    assert not r.is_loaded  # lazy


def test_reranker_init_known_models():
    for model_name in CrossEncoderReranker.MODELS:
        r = CrossEncoderReranker(model_name=model_name)
        assert r.model_name == model_name


def test_reranker_init_unknown_model():
    with pytest.raises(ValueError, match="Unknown reranker model"):
        CrossEncoderReranker(model_name="nonexistent")


def test_reranker_init_custom_batch_size():
    r = CrossEncoderReranker(batch_size=32, verbose=True)
    assert r.batch_size == 32
    assert r.verbose is True


# ---------------------------------------------------------------------------
# RerankerResult
# ---------------------------------------------------------------------------

def test_reranker_result_defaults():
    r = RerankerResult(id="TEST-001")
    assert r.id == "TEST-001"
    assert r.score == 0.0
    assert r.text == ""
    assert r.metadata == {}
    assert r.diversity_penalty == 0.0


# ---------------------------------------------------------------------------
# Reranking — requires sentence-transformers
# ---------------------------------------------------------------------------

@pytest.mark.skipif(
    not SENTENCE_TRANSFORMERS_AVAILABLE,
    reason="sentence-transformers not installed",
)
class TestRerankerWithModel:
    """Tests that actually load a cross-encoder model.

    These are gated on ``sentence-transformers`` being available.
    """

    @pytest.fixture
    def reranker(self):
        return CrossEncoderReranker(
            model_name="ms-marco-MiniLM-L6-v2",
            verbose=False,
        )

    def test_rerank_returns_results(self, reranker):
        candidates = [
            {"id": "A", "text": "Python is a programming language"},
            {"id": "B", "text": "Java is also a programming language"},
            {"id": "C", "text": "The weather is nice today"},
        ]
        results = reranker.rerank("programming languages", candidates, top_k=3)
        assert len(results) == 3
        for r in results:
            assert isinstance(r, RerankerResult)
            assert isinstance(r.score, float)
        # Cross-encoder raw logits can be negative; verify ordering instead
        assert results[0].score >= results[1].score >= results[2].score

    def test_rerank_orders_by_relevance(self, reranker):
        candidates = [
            {"id": "A", "text": "Python programming language"},
            {"id": "B", "text": "Quantum physics theory"},
            {"id": "C", "text": "Weather forecast for tomorrow"},
        ]
        results = reranker.rerank("python coding", candidates, top_k=3)
        # A should be most relevant
        assert results[0].id == "A"

    def test_rerank_empty_candidates(self, reranker):
        results = reranker.rerank("test", [])
        assert results == []

    def test_rerank_single_candidate(self, reranker):
        candidates = [{"id": "X", "text": "Single document here"}]
        results = reranker.rerank("test", candidates, top_k=5)
        assert len(results) == 1

    def test_rerank_respects_top_k(self, reranker):
        candidates = [
            {"id": str(i), "text": f"Document number {i}"}
            for i in range(20)
        ]
        results = reranker.rerank("document number", candidates, top_k=5)
        assert len(results) == 5

    def test_rerank_with_text_fn(self, reranker):
        class Custom:
            def __init__(self, id_, content):
                self.id = id_
                self.content = content

        candidates = [
            Custom("A", "Python programming"),
            Custom("B", "Weather report"),
        ]
        results = reranker.rerank(
            "python",
            candidates,
            top_k=2,
            text_fn=lambda c: c.content,
        )
        assert len(results) == 2
        assert results[0].id == "A"

    def test_rerank_with_mmr_diversity(self, reranker):
        candidates = [
            {"id": "A", "text": "Python is a great programming language"},
            {"id": "B", "text": "Python can be used for web development"},
            {"id": "C", "text": "Python has excellent libraries for data science"},
        ]
        results = reranker.rerank_with_mmr(
            "python programming",
            candidates,
            top_k=3,
            lambda_param=0.5,
        )
        assert len(results) == 3
        # With MMR, we should have diverse results
        ids = [r.id for r in results]
        assert len(ids) == len(set(ids))  # no duplicates

    def test_mmr_lambda_one_is_pure_relevance(self, reranker):
        """lambda_param=1.0 should produce same ranking as plain rerank."""
        candidates = [
            {"id": "A", "text": "Python programming language"},
            {"id": "B", "text": "Weather forecast today"},
            {"id": "C", "text": "Java programming language"},
        ]
        mmr_results = reranker.rerank_with_mmr(
            "python coding", candidates, top_k=3, lambda_param=1.0,
        )
        plain_results = reranker.rerank("python coding", candidates, top_k=3)
        assert [r.id for r in mmr_results] == [r.id for r in plain_results]


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

def test_reranker_raises_without_model():
    """If sentence-transformers is not installed, rerank should raise."""
    r = CrossEncoderReranker()
    # Force load attempt
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        with pytest.raises(ImportError, match="sentence-transformers"):
            r.rerank("test", [{"id": "A", "text": "doc"}])
    else:
        # If it IS installed, this should just work
        results = r.rerank("test", [{"id": "A", "text": "doc"}])
        assert len(results) == 1
