"""Cross-encoder reranking for precision improvement on retrieved candidates.

Provides a ``CrossEncoderReranker`` that re-scores candidate documents
with a cross-encoder model. Supports multiple model sizes:

* ``"ms-marco-MiniLM-L6-v2"`` — fast, ~50ms per query-candidate pair
* ``"bge-reranker-v2-m3"`` — SOTA multilingual, ~200ms per pair
* ``"ce-esci-mpnet-base"`` — domain-specific (e-commerce)

Supports MMR (Maximal Marginal Relevance) diversity post-processing to
avoid returning near-duplicate results.

.. note::
    Requires the ``sentence-transformers`` optional dependency
    (``pip install knowledge-base[rerank]``).
"""

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from .logging import get_logger


# ---------------------------------------------------------------------------
# Feature detection
# ---------------------------------------------------------------------------

SENTENCE_TRANSFORMERS_AVAILABLE: bool = False
try:
    import sentence_transformers
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    sentence_transformers = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass
class RerankerResult:
    """A single result from the reranker.

    Attributes:
        id: KB entry ID.
        score: Relevance score from the cross-encoder (0.0 to 1.0-ish).
        text: The document text that was scored.
        metadata: Original metadata from retrieval.
        diversity_penalty: MMR penalty applied (0 if MMR not used).
    """
    id: str
    score: float = 0.0
    text: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    diversity_penalty: float = 0.0


# ---------------------------------------------------------------------------
# Cross-Encoder Reranker
# ---------------------------------------------------------------------------

class CrossEncoderReranker:
    """Re-rank candidates with a cross-encoder for precision.

    Models are lazy-loaded on first call to ``rerank()``. The default model
    is ``"ms-marco-MiniLM-L6-v2"`` which offers a good speed/quality trade-off.

    Args:
        model_name: Cross-encoder model identifier. One of:
            - ``"ms-marco-MiniLM-L6-v2"`` (fast, default)
            - ``"bge-reranker-v2-m3"`` (SOTA, slower)
            - ``"ce-esci-mpnet-base"`` (domain-specific)
        batch_size: Batch size for cross-encoder scoring (default: 16).
        verbose: Whether to show progress bars from the cross-encoder.
    """

    MODELS = {
        "ms-marco-MiniLM-L6-v2": "cross-encoder/ms-marco-MiniLM-L6-v2",
        "bge-reranker-v2-m3": "BAAI/bge-reranker-v2-m3",
        "ce-esci-mpnet-base": "cross-encoder/esci-mpnet-base",
    }

    def __init__(
        self,
        model_name: str = "ms-marco-MiniLM-L6-v2",
        batch_size: int = 16,
        verbose: bool = False,
    ):
        if model_name not in self.MODELS:
            raise ValueError(
                f"Unknown reranker model: {model_name!r}. "
                f"Available: {list(self.MODELS.keys())}"
            )
        self.model_name = model_name
        self._hf_model_name = self.MODELS[model_name]
        self.batch_size = batch_size
        self.verbose = verbose
        self._model: Any = None  # lazy-loaded

    # ------------------------------------------------------------------
    # Model loading (lazy)
    # ------------------------------------------------------------------

    def _load_model(self) -> None:
        """Lazy-load the cross-encoder model."""
        if self._model is not None:
            return
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence-transformers is required for reranking. "
                "Install it with: pip install knowledge-base[rerank]"
            )
        get_logger().info(
            "Loading cross-encoder model: %s", self._hf_model_name
        )
        self._model = sentence_transformers.CrossEncoder(
            self._hf_model_name,
            max_length=512,
        )

    @property
    def is_loaded(self) -> bool:
        """Whether the model has been loaded."""
        return self._model is not None

    # ------------------------------------------------------------------
    # Reranking
    # ------------------------------------------------------------------

    def rerank(
        self,
        query: str,
        candidates: List[Any],
        top_k: int = 5,
        text_fn: Optional[Callable[[Any], str]] = None,
    ) -> List[RerankerResult]:
        """Re-rank a list of candidate results.

        Args:
            query: The original search query.
            candidates: List of candidate objects (dicts, dataclasses, etc.).
            top_k: Number of results to return after reranking.
            text_fn: Optional function to extract text from a candidate.
                     If None, tries ``candidate.text``, then
                     ``candidate.get("text", "")``, then ``str(candidate)``.

        Returns:
            A list of ``RerankerResult`` sorted by descending relevance score.
        """
        if not candidates:
            return []

        self._load_model()
        text_fn = text_fn or self._default_text_fn

        # Build (query, candidate_text) pairs
        pairs: List[Tuple[str, str]] = []
        for c in candidates:
            try:
                text = text_fn(c)
                pairs.append((query, text))
            except Exception:
                pairs.append((query, ""))

        if not pairs:
            return []

        # Score all pairs in batches
        try:
            scores = self._model.predict(
                pairs,
                batch_size=self.batch_size,
                show_progress_bar=self.verbose,
            )
        except Exception as exc:
            get_logger().error("Cross-encoder scoring failed: %s", exc)
            return []

        # Scores may be returned as a list or numpy array
        score_list: List[float] = [
            float(s) if not isinstance(s, (list, tuple)) else float(s[0])
            for s in (scores.tolist() if hasattr(scores, 'tolist') else scores)
        ]

        # Build results sorted by score
        results: List[RerankerResult] = []
        for idx, (candidate, score) in enumerate(zip(candidates, score_list)):
            cid = self._extract_id(candidate)
            ctext = text_fn(candidate)
            cmeta = self._extract_metadata(candidate)
            results.append(RerankerResult(
                id=cid,
                score=score,
                text=ctext,
                metadata=cmeta,
            ))

        # Sort by descending score
        results.sort(key=lambda x: -x.score)

        # Assign ranks and trim
        for rank, r in enumerate(results[:top_k]):
            r.metadata["rerank_score"] = r.score
            r.metadata["rerank_rank"] = rank

        return results[:top_k]

    # ------------------------------------------------------------------
    # MMR (Maximal Marginal Relevance) diversity
    # ------------------------------------------------------------------

    def rerank_with_mmr(
        self,
        query: str,
        candidates: List[Any],
        top_k: int = 5,
        lambda_param: float = 0.7,
        text_fn: Optional[Callable[[Any], str]] = None,
    ) -> List[RerankerResult]:
        """Re-rank with MMR diversity post-processing.

        MMR balances relevance (cross-encoder score) and diversity
        (novelty against already-selected results).

        Args:
            query: The original search query.
            candidates: List of candidate objects.
            top_k: Number of results to return.
            lambda_param: MMR lambda (0 = max diversity, 1 = max relevance).
            text_fn: Function to extract text from a candidate.

        Returns:
            Diverse re-ranked results.
        """
        if not candidates:
            return []

        self._load_model()
        text_fn = text_fn or self._default_text_fn

        # Step 1: get relevance scores
        relevance = self.rerank(query, candidates, top_k=len(candidates))
        if not relevance:
            return []

        # If only 1 result or lambda_param=1, skip diversity
        if len(relevance) <= 1 or lambda_param >= 1.0:
            return relevance[:top_k]

        # Step 2: MMR selection
        # We need pairwise similarity among candidate texts.
        # Use a simple TF-IDF / token-overlap approximation to avoid
        # loading another model.
        selected: List[RerankerResult] = [relevance[0]]
        remaining = relevance[1:]

        # Pre-compute candidate text token sets for similarity
        token_sets: List[Tuple[RerankerResult, set]] = []
        for r in remaining:
            tokens = set(r.text.lower().split())
            token_sets.append((r, tokens))

        selected_token_sets: List[set] = [
            set(selected[0].text.lower().split())
        ]

        while len(selected) < top_k and token_sets:
            best_mmr = -1.0
            best_idx = -1

            for i, (cand, cand_tokens) in enumerate(token_sets):
                # Relevance score (normalized to 0-1)
                rel = cand.score

                # Diversity: max similarity to any selected result
                max_sim = 0.0
                for sel_tokens in selected_token_sets:
                    if not cand_tokens or not sel_tokens:
                        continue
                    intersection = len(cand_tokens & sel_tokens)
                    union = len(cand_tokens | sel_tokens)
                    sim = intersection / union if union > 0 else 0.0
                    max_sim = max(max_sim, sim)

                # MMR score
                mmr = lambda_param * rel - (1 - lambda_param) * max_sim

                if mmr > best_mmr:
                    best_mmr = mmr
                    best_idx = i

            if best_idx < 0:
                break

            selected.append(token_sets[best_idx][0])
            selected_token_sets.append(token_sets[best_idx][1])
            token_sets.pop(best_idx)

        # Assign diversity penalties and ranks
        for rank, r in enumerate(selected[:top_k]):
            r.diversity_penalty = (1 - lambda_param) * (
                1 - r.score if r.score < 1 else 0
            )
            r.metadata["rerank_rank"] = rank
            r.metadata["rerank_mmr_score"] = r.score - r.diversity_penalty

        return selected[:top_k]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _default_text_fn(candidate: Any) -> str:
        if hasattr(candidate, "text") and candidate.text:
            return candidate.text
        if isinstance(candidate, dict):
            return candidate.get("text", candidate.get("finding", str(candidate)))
        return str(candidate)

    @staticmethod
    def _extract_id(candidate: Any) -> str:
        if hasattr(candidate, "id"):
            return candidate.id
        if isinstance(candidate, dict):
            return candidate.get("id", candidate.get("entry_id", "unknown"))
        return "unknown"

    @staticmethod
    def _extract_metadata(candidate: Any) -> Dict[str, Any]:
        if hasattr(candidate, "metadata") and candidate.metadata:
            return dict(candidate.metadata)
        if isinstance(candidate, dict):
            return {k: v for k, v in candidate.items()
                    if k not in ("id", "text")}
        return {}
