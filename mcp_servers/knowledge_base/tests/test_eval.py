"""Tests for ``kb.eval`` — retrieval evaluation metrics and comparison."""

import pytest
from kb.eval import (
    RetrievalEvaluator,
    recall_at_k,
    precision_at_k,
    reciprocal_rank,
    ndcg_at_k,
    quick_eval,
    compare_configs,
    EvalResult,
    ComparisonResult,
)


# ---------------------------------------------------------------------------
# Unit tests for individual metric functions
# ---------------------------------------------------------------------------

class TestRecallAtK:
    def test_all_relevant_retrieved(self):
        retrieved = ["a", "b", "c", "d", "e"]
        relevant = {"a", "b"}
        assert recall_at_k(retrieved, relevant, 5) == 1.0

    def test_partial_recall(self):
        retrieved = ["a", "b", "c", "d", "e"]
        relevant = {"a", "x", "y"}
        assert recall_at_k(retrieved, relevant, 5) == pytest.approx(1.0 / 3)

    def test_no_relevant_retrieved(self):
        retrieved = ["a", "b", "c"]
        relevant = {"x", "y"}
        assert recall_at_k(retrieved, relevant, 3) == 0.0

    def test_empty_relevant_set(self):
        retrieved = ["a", "b", "c"]
        assert recall_at_k(retrieved, set(), 3) == 0.0

    def test_k_cutoff_limits_recall(self):
        retrieved = ["x", "y", "a", "b", "c"]
        relevant = {"a", "b"}
        # a and b are at positions 3 and 4, so recall@2 = 0
        assert recall_at_k(retrieved, relevant, 2) == 0.0
        # recall@4 = 2/2 = 1.0
        assert recall_at_k(retrieved, relevant, 4) == 1.0


class TestPrecisionAtK:
    def test_all_relevant(self):
        retrieved = ["a", "b", "c"]
        relevant = {"a", "b", "c"}
        assert precision_at_k(retrieved, relevant, 3) == 1.0

    def test_half_relevant(self):
        retrieved = ["a", "b", "c", "d"]
        relevant = {"a", "b"}
        assert precision_at_k(retrieved, relevant, 4) == 0.5

    def test_no_relevant(self):
        retrieved = ["a", "b", "c"]
        relevant = {"x"}
        assert precision_at_k(retrieved, relevant, 3) == 0.0

    def test_k_zero_returns_zero(self):
        retrieved = ["a"]
        relevant = {"a"}
        assert precision_at_k(retrieved, relevant, 0) == 0.0


class TestReciprocalRank:
    def test_first_result_is_relevant(self):
        retrieved = ["a", "b", "c"]
        relevant = {"a"}
        assert reciprocal_rank(retrieved, relevant) == 1.0

    def test_third_result_is_relevant(self):
        retrieved = ["x", "y", "a", "b"]
        relevant = {"a"}
        assert reciprocal_rank(retrieved, relevant) == pytest.approx(1.0 / 3)

    def test_no_relevant_returns_zero(self):
        retrieved = ["a", "b", "c"]
        relevant = {"z"}
        assert reciprocal_rank(retrieved, relevant) == 0.0

    def test_multiple_relevant_uses_first(self):
        retrieved = ["x", "a", "b", "c"]
        relevant = {"a", "b"}
        assert reciprocal_rank(retrieved, relevant) == 0.5  # 1/2


class TestNDCG:
    def test_perfect_ranking(self):
        retrieved = ["a", "b", "c"]
        relevant = {"a", "b", "c"}
        assert ndcg_at_k(retrieved, relevant, 3) == pytest.approx(1.0)

    def test_worst_ranking(self):
        retrieved = ["x", "y", "a"]
        relevant = {"a"}
        # NDCG@3: DCG = 1/log2(4) = 0.5, IDCG = 1/log2(2) = 1.0
        assert ndcg_at_k(retrieved, relevant, 3) == pytest.approx(0.5)

    def test_no_relevant_returns_zero(self):
        retrieved = ["a", "b", "c"]
        relevant = {"z"}
        assert ndcg_at_k(retrieved, relevant, 3) == 0.0

    def test_empty_relevant_returns_zero(self):
        retrieved = ["a", "b"]
        assert ndcg_at_k(retrieved, ["a"], 0) == 0.0


# ---------------------------------------------------------------------------
# RetrievalEvaluator
# ---------------------------------------------------------------------------

class TestRetrievalEvaluator:
    def test_evaluate_returns_expected_structure(self):
        def search_fn(query, top_k):
            return [{"id": f"doc-{i}"} for i in range(top_k)]

        test_set = [
            ("query1", {"doc-0", "doc-1"}),
            ("query2", {"doc-0"}),
        ]
        evaluator = RetrievalEvaluator(ks=[1, 5])
        result = evaluator.evaluate(test_set, search_fn)

        assert isinstance(result, EvalResult)
        assert result.total_queries == 2
        assert 1 in result.recall_at_k
        assert 5 in result.recall_at_k
        assert 1 in result.precision_at_k
        assert 1 in result.ndcg_at_k
        assert isinstance(result.mrr, float)
        assert len(result.per_query) == 2

    def test_evaluate_perfect_search(self):
        def perfect_search(query, top_k):
            relevant_map = {
                "find a": {"doc-0", "doc-1"},
                "find b": {"doc-2"},
            }
            ids = list(relevant_map.get(query, set()))
            return [{"id": rid} for rid in ids[:top_k]]

        test_set = [
            ("find a", {"doc-0", "doc-1"}),
            ("find b", {"doc-2"}),
        ]
        evaluator = RetrievalEvaluator(ks=[1, 2, 5])
        result = evaluator.evaluate(test_set, perfect_search)

        assert result.recall_at_k[5] == 1.0
        assert result.mrr == 1.0

    def test_evaluate_empty_test_set(self):
        evaluator = RetrievalEvaluator()
        result = evaluator.evaluate([], lambda q, k: [])
        assert result.total_queries == 0

    def test_evaluate_search_function_error(self):
        def failing_search(query, top_k):
            raise RuntimeError("search failed")

        test_set = [("query", {"doc-1"})]
        evaluator = RetrievalEvaluator(ks=[1])
        result = evaluator.evaluate(test_set, failing_search)
        assert result.total_queries == 1
        assert result.per_query[0].get("error") is not None

    def test_config_name_propagated(self):
        evaluator = RetrievalEvaluator()
        result = evaluator.evaluate([], lambda q, k: [], config_name="test-config")
        assert result.config_name == "test-config"

    def test_custom_ks_values(self):
        evaluator = RetrievalEvaluator(ks=[3, 7])
        result = evaluator.evaluate(
            [("q", {"doc-1"})],
            lambda q, k: [{"id": "doc-1"}],
        )
        assert 3 in result.recall_at_k
        assert 7 in result.recall_at_k
        assert 1 not in result.recall_at_k


# ---------------------------------------------------------------------------
# A/B comparison
# ---------------------------------------------------------------------------

class TestComparison:
    def test_config_b_wins_when_better(self):
        def bad_search(query, top_k):
            return [{"id": "wrong"}]

        def good_search(query, top_k):
            return [{"id": "doc-1"}]

        test_set = [("find doc-1", {"doc-1"})]
        evaluator = RetrievalEvaluator(ks=[1])
        result = evaluator.compare(
            test_set, bad_search, good_search,
            config_a_name="bad", config_b_name="good",
        )

        assert result.winner == "good"
        assert result.config_a is not None
        assert result.config_b is not None
        assert "recall@1" in result.improvements
        assert result.improvements["recall@1"] > 0

    def test_config_a_wins_when_better(self):
        def good_search(query, top_k):
            return [{"id": "doc-1"}]

        def bad_search(query, top_k):
            return [{"id": "wrong"}]

        test_set = [("find doc-1", {"doc-1"})]
        evaluator = RetrievalEvaluator(ks=[1])
        result = evaluator.compare(
            test_set, good_search, bad_search,
            config_a_name="good", config_b_name="bad",
        )

        assert result.winner == "good"

    def test_tie_when_equal(self):
        def same_search(query, top_k):
            return [{"id": "doc-1"}]

        test_set = [("find doc-1", {"doc-1"})]
        evaluator = RetrievalEvaluator(ks=[1])
        result = evaluator.compare(
            test_set, same_search, same_search,
        )

        assert result.winner == "tie"

    def test_comparison_result_structure(self):
        def search_a(q, k):
            return [{"id": f"a-{i}"} for i in range(k)]

        def search_b(q, k):
            return [{"id": f"b-{i}"} for i in range(k)]

        test_set = [("q", {"a-0", "b-0"})]
        evaluator = RetrievalEvaluator(ks=[1, 5])
        result = evaluator.compare(test_set, search_a, search_b)

        assert isinstance(result, ComparisonResult)
        assert isinstance(result.improvements, dict)
        assert isinstance(result.significance, dict)
        assert "recall@1" in result.improvements
        assert "mrr" in result.improvements
        assert "ndcg@1" in result.improvements


# ---------------------------------------------------------------------------
# Convenience functions
# ---------------------------------------------------------------------------

class TestQuickEval:
    def test_quick_eval_returns_eval_result(self):
        result = quick_eval(
            [("q", {"doc-1"})],
            lambda q, k: [{"id": "doc-1"}],
            ks=[1, 3],
        )
        assert isinstance(result, EvalResult)
        assert result.recall_at_k[1] == 1.0


class TestCompareConfigs:
    def test_compare_configs_returns_comparison(self):
        result = compare_configs(
            [("q", {"doc-1"})],
            lambda q, k: [{"id": "wrong"}],
            lambda q, k: [{"id": "doc-1"}],
            config_a_name="baseline",
            config_b_name="improved",
            ks=[1],
        )
        assert isinstance(result, ComparisonResult)
        assert result.winner == "improved"
