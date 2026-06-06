"""Evaluation framework for retrieval quality assessment.

Provides metrics to measure and compare retrieval pipeline quality:

- ``Recall@k``: Fraction of relevant documents in top-k results.
- ``Precision@k``: Fraction of top-k results that are relevant.
- ``MRR`` (Mean Reciprocal Rank): Reciprocal rank of the first relevant result.
- ``NDCG@k`` (Normalized Discounted Cumulative Gain): Position-aware ranking
  quality with graded relevance.
- ``RetrievalEvaluator``: Computes all metrics from test queries + ground truth.
- ``compare_configs``: A/B comparison between two retrieval configurations.

Usage::

    from kb.eval import RetrievalEvaluator, compare_configs

    test_set = [
        ("what is RAG", {"PAT-001", "PAT-002"}),
        ("how to chunk", {"PAT-003"}),
    ]

    evaluator = RetrievalEvaluator()
    results = evaluator.evaluate(test_set, my_search_function)
    print(results["recall@5"])  # → 0.85

    # A/B comparison
    comparison = compare_configs(test_set, config_a_fn, config_b_fn)
    print(comparison["winner"])  # → "config_a" or "config_b"
"""

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

#: A test query: (query_string, set_of_relevant_entry_ids)
TestQuery = Tuple[str, Set[str]]

#: Signature for a search function used in evaluation.
#: Takes (query, top_k) and returns a list of result dicts with "id" keys.
SearchFn = Callable[[str, int], List[Dict[str, Any]]]


# ---------------------------------------------------------------------------
# Evaluation Result
# ---------------------------------------------------------------------------

@dataclass
class EvalResult:
    """Result of evaluating a retrieval configuration on a test set.

    Attributes:
        recall_at_k: Recall@k for each k.
        precision_at_k: Precision@k for each k.
        mrr: Mean Reciprocal Rank.
        ndcg_at_k: NDCG@k for each k.
        total_queries: Number of queries evaluated.
        per_query: Individual query results for detailed analysis.
        config_name: Optional label for the evaluated configuration.
    """
    recall_at_k: Dict[int, float] = field(default_factory=dict)
    precision_at_k: Dict[int, float] = field(default_factory=dict)
    mrr: float = 0.0
    ndcg_at_k: Dict[int, float] = field(default_factory=dict)
    total_queries: int = 0
    per_query: List[Dict[str, Any]] = field(default_factory=list)
    config_name: str = ""


@dataclass
class ComparisonResult:
    """Result of comparing two retrieval configurations.

    Attributes:
        winner: Name of the winning configuration ("config_a", "config_b",
                or "tie").
        improvements: Dict of metric → delta (positive means config_b wins).
        config_a: EvalResult for configuration A (baseline).
        config_b: EvalResult for configuration B (candidate).
        significance: Statistical significance indicators (simplified).
    """
    winner: str = "tie"
    improvements: Dict[str, float] = field(default_factory=dict)
    config_a: Optional[EvalResult] = None
    config_b: Optional[EvalResult] = None
    significance: Dict[str, str] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Metric computation helpers
# ---------------------------------------------------------------------------

def recall_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
    """Compute Recall@k.

    Args:
        retrieved: List of retrieved item IDs (in rank order).
        relevant: Set of relevant item IDs.
        k: Cutoff rank.

    Returns:
        Recall@k in [0, 1].
    """
    if not relevant:
        return 0.0
    retrieved_top_k = set(retrieved[:k])
    hits = len(retrieved_top_k & relevant)
    return hits / len(relevant)


def precision_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
    """Compute Precision@k.

    Args:
        retrieved: List of retrieved item IDs (in rank order).
        relevant: Set of relevant item IDs.
        k: Cutoff rank.

    Returns:
        Precision@k in [0, 1].
    """
    if k == 0:
        return 0.0
    retrieved_top_k = set(retrieved[:k])
    hits = len(retrieved_top_k & relevant)
    return hits / k


def reciprocal_rank(retrieved: List[str], relevant: Set[str]) -> float:
    """Compute the reciprocal rank of the first relevant result.

    Args:
        retrieved: List of retrieved item IDs (in rank order).
        relevant: Set of relevant item IDs.

    Returns:
        Reciprocal rank in [0, 1]. 0 if no relevant result found.
    """
    for rank, doc_id in enumerate(retrieved, 1):
        if doc_id in relevant:
            return 1.0 / rank
    return 0.0


def dcg_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
    """Compute Discounted Cumulative Gain @k.

    Uses binary relevance (1 if relevant, 0 otherwise).

    Args:
        retrieved: List of retrieved item IDs (in rank order).
        relevant: Set of relevant item IDs.
        k: Cutoff rank.

    Returns:
        DCG@k.
    """
    dcg = 0.0
    for rank, doc_id in enumerate(retrieved[:k], 1):
        if doc_id in relevant:
            # Binary relevance: rel_i = 1
            dcg += 1.0 / math.log2(rank + 1)
    return dcg


def ndcg_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
    """Compute Normalized DCG @k.

    Args:
        retrieved: List of retrieved item IDs (in rank order).
        relevant: Set of relevant item IDs.
        k: Cutoff rank.

    Returns:
        NDCG@k in [0, 1]. Returns 0 if there are no relevant items or
        the ideal DCG is 0.
    """
    dcg = dcg_at_k(retrieved, relevant, k)
    # Ideal DCG: all relevant items at the top
    ideal_relevant = min(len(relevant), k)
    if ideal_relevant == 0:
        return 0.0
    idcg = sum(1.0 / math.log2(pos + 2) for pos in range(ideal_relevant))
    return dcg / idcg if idcg > 0 else 0.0


# ---------------------------------------------------------------------------
# RetrievalEvaluator
# ---------------------------------------------------------------------------

class RetrievalEvaluator:
    """Evaluate retrieval quality with standard IR metrics.

    Args:
        ks: List of cutoff values to report (default: ``[1, 3, 5, 10]``).
    """

    def __init__(self, ks: Optional[List[int]] = None):
        self._ks = sorted(ks or [1, 3, 5, 10])

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def evaluate(
        self,
        test_queries: List[TestQuery],
        search_fn: SearchFn,
        config_name: str = "",
    ) -> EvalResult:
        """Evaluate a search function against a labeled test set.

        Args:
            test_queries: List of ``(query_string, set_of_relevant_ids)``.
            search_fn: A callable ``(query, top_k) → list_of_result_dicts``.
                       Each dict must have an ``"id"`` key.
            config_name: Optional label for this configuration.

        Returns:
            An ``EvalResult`` with aggregate and per-query metrics.
        """
        if not test_queries:
            return EvalResult(config_name=config_name)

        max_k = max(self._ks)
        recall_sums: Dict[int, float] = {k: 0.0 for k in self._ks}
        precision_sums: Dict[int, float] = {k: 0.0 for k in self._ks}
        ndcg_sums: Dict[int, float] = {k: 0.0 for k in self._ks}
        rr_sum = 0.0
        per_query: List[Dict[str, Any]] = []

        for query, relevant in test_queries:
            try:
                results = search_fn(query, max_k)
            except Exception as exc:
                # Search function failed — treat as empty results
                results = []
                per_query.append({
                    "query": query,
                    "error": str(exc),
                    "retrieved": [],
                    "relevant": list(relevant),
                })
                continue

            retrieved_ids = [r.get("id", "") for r in results]

            q_metrics: Dict[str, Any] = {
                "query": query,
                "relevant_count": len(relevant),
                "retrieved_ids": retrieved_ids,
            }

            for k in self._ks:
                q_metrics[f"recall@{k}"] = recall_at_k(retrieved_ids, relevant, k)
                q_metrics[f"precision@{k}"] = precision_at_k(retrieved_ids, relevant, k)
                q_metrics[f"ndcg@{k}"] = ndcg_at_k(retrieved_ids, relevant, k)

                recall_sums[k] += q_metrics[f"recall@{k}"]
                precision_sums[k] += q_metrics[f"precision@{k}"]
                ndcg_sums[k] += q_metrics[f"ndcg@{k}"]

            q_metrics["reciprocal_rank"] = reciprocal_rank(retrieved_ids, relevant)
            rr_sum += q_metrics["reciprocal_rank"]

            per_query.append(q_metrics)

        n = len(test_queries)

        return EvalResult(
            recall_at_k={k: recall_sums[k] / n for k in self._ks},
            precision_at_k={k: precision_sums[k] / n for k in self._ks},
            mrr=rr_sum / n,
            ndcg_at_k={k: ndcg_sums[k] / n for k in self._ks},
            total_queries=n,
            per_query=per_query,
            config_name=config_name,
        )

    # ------------------------------------------------------------------
    # Batch comparison
    # ------------------------------------------------------------------

    def compare(
        self,
        test_queries: List[TestQuery],
        config_a_fn: SearchFn,
        config_b_fn: SearchFn,
        config_a_name: str = "baseline",
        config_b_name: str = "candidate",
    ) -> ComparisonResult:
        """Compare two retrieval configurations on the same test set.

        Args:
            test_queries: Test queries with ground truth.
            config_a_fn: Baseline search function.
            config_b_fn: Candidate search function.
            config_a_name: Label for config A (default: "baseline").
            config_b_name: Label for config B (default: "candidate").

        Returns:
            A ``ComparisonResult`` with winner and delta metrics.
        """
        result_a = self.evaluate(test_queries, config_a_fn, config_a_name)
        result_b = self.evaluate(test_queries, config_b_fn, config_b_name)

        improvements: Dict[str, float] = {}
        significance: Dict[str, str] = {}

        # Compare recall@k
        all_ks = sorted(
            set(result_a.recall_at_k.keys()) | set(result_b.recall_at_k.keys())
        )
        for k in all_ks:
            a_val = result_a.recall_at_k.get(k, 0.0)
            b_val = result_b.recall_at_k.get(k, 0.0)
            delta = b_val - a_val
            improvements[f"recall@{k}"] = round(delta, 4)
            significance[f"recall@{k}"] = (
                "improved" if delta > 0.01 else
                "degraded" if delta < -0.01 else
                "unchanged"
            )

        # Compare MRR
        mrr_delta = result_b.mrr - result_a.mrr
        improvements["mrr"] = round(mrr_delta, 4)
        significance["mrr"] = (
            "improved" if mrr_delta > 0.01 else
            "degraded" if mrr_delta < -0.01 else
            "unchanged"
        )

        # Compare NDCG@k
        for k in all_ks:
            a_val = result_a.ndcg_at_k.get(k, 0.0)
            b_val = result_b.ndcg_at_k.get(k, 0.0)
            delta = b_val - a_val
            improvements[f"ndcg@{k}"] = round(delta, 4)
            significance[f"ndcg@{k}"] = (
                "improved" if delta > 0.01 else
                "degraded" if delta < -0.01 else
                "unchanged"
            )

        # Determine overall winner
        improved_count = sum(1 for v in significance.values() if v == "improved")
        degraded_count = sum(1 for v in significance.values() if v == "degraded")

        if improved_count > degraded_count:
            winner = config_b_name
        elif degraded_count > improved_count:
            winner = config_a_name
        else:
            winner = "tie"

        return ComparisonResult(
            winner=winner,
            improvements=improvements,
            config_a=result_a,
            config_b=result_b,
            significance=significance,
        )


# ---------------------------------------------------------------------------
# Convenience: evaluate on a single function
# ---------------------------------------------------------------------------

def quick_eval(
    test_queries: List[TestQuery],
    search_fn: SearchFn,
    ks: Optional[List[int]] = None,
) -> EvalResult:
    """Quick one-shot evaluation of a search function.

    Args:
        test_queries: ``[(query, {relevant_ids}), ...]``.
        search_fn: Search function ``(query, top_k) → results``.
        ks: Cutoff values (default: ``[1, 3, 5, 10]``).

    Returns:
        ``EvalResult`` with aggregate metrics.
    """
    evaluator = RetrievalEvaluator(ks=ks)
    return evaluator.evaluate(test_queries, search_fn)


def compare_configs(
    test_queries: List[TestQuery],
    config_a_fn: SearchFn,
    config_b_fn: SearchFn,
    config_a_name: str = "baseline",
    config_b_name: str = "candidate",
    ks: Optional[List[int]] = None,
) -> ComparisonResult:
    """Compare two retrieval configurations (convenience wrapper).

    Args:
        test_queries: ``[(query, {relevant_ids}), ...]``.
        config_a_fn: Baseline search function.
        config_b_fn: Candidate search function.
        config_a_name: Label for baseline.
        config_b_name: Label for candidate.
        ks: Cutoff values.

    Returns:
        ``ComparisonResult`` with winner and per-metric deltas.
    """
    evaluator = RetrievalEvaluator(ks=ks)
    return evaluator.compare(
        test_queries, config_a_fn, config_b_fn,
        config_a_name=config_a_name,
        config_b_name=config_b_name,
    )
