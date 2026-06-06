"""Hybrid retrieval orchestrator: dense (ChromaDB) + sparse (BM25) + RRF fusion.

Provides:

* ``DenseRetriever`` — queries a ChromaDB collection with the configured
  embedding model.
* ``FusionRetriever`` — combines dense + sparse results via Reciprocal
  Rank Fusion (RRF).
* ``RetrievalResult`` — a lightweight result dataclass used throughout the
  pipeline.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .embedding import get_embedding_function, get_model_dim, list_models
from .logging import get_logger
from .store import KBStore, get_default_store


# ---------------------------------------------------------------------------
# Unified result type
# ---------------------------------------------------------------------------

@dataclass
class RetrievalResult:
    """A single result from any retrieval step in the pipeline.

    Attributes:
        id: KB entry ID.
        score: Relevance score for this step.
        text: The document text (for reranking / synthesis).
        metadata: All metadata dict from ChromaDB.
        rank: Position of this result in the current ranking (0-based).
        source: Which retriever produced this result ("dense", "sparse",
                "fusion", "reranker").
    """
    id: str
    score: float = 0.0
    text: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    rank: int = 0
    source: str = "unknown"


# ---------------------------------------------------------------------------
# Dense Retriever
# ---------------------------------------------------------------------------

class DenseRetriever:
    """Configurable dense ANN search via ChromaDB.

    Uses the embedding model registry from ``kb.embedding`` and queries
    a dedicated ChromaDB collection per model.

    Args:
        model_name: Embedding model identifier (see ``kb.embedding.list_models()``).
        store: KBStore instance (uses default if None).
        collection_prefix: Prefix for the ChromaDB collection name.
        top_k_multiplier: How many times ``top_k`` to retrieve before scoring
                          (higher = more candidate diversity).
    """

    def __init__(
        self,
        model_name: str = "bge-small-en",
        store: Optional[KBStore] = None,
        collection_prefix: str = "kb_dense",
        top_k_multiplier: int = 3,
    ):
        self.model_name = model_name
        self.store = store or get_default_store()
        self.collection_prefix = collection_prefix
        self.top_k_multiplier = top_k_multiplier

        # Validate model exists
        try:
            self._dim = get_model_dim(model_name)
        except ValueError:
            available = list_models()
            raise ValueError(
                f"Unknown embedding model: {model_name!r}. "
                f"Available: {available}"
            )

        # Get or create the ChromaDB collection with the appropriate
        # embedding function (lazy-loaded by get_embedding_function)
        self._embedding_fn = get_embedding_function(model_name)
        self._collection_name = f"{collection_prefix}_{model_name}"
        self._collection = self.store.get_or_create_collection(
            name=self._collection_name,
            embedding_function=self._embedding_fn,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def collection_name(self) -> str:
        """The ChromaDB collection name for this retriever."""
        return self._collection_name

    @property
    def dimension(self) -> int:
        """Embedding dimension of the configured model."""
        return self._dim

    def search(
        self,
        query: str,
        top_k: int = 10,
        category: Optional[str] = None,
    ) -> List[RetrievalResult]:
        """Run a dense ANN search against ChromaDB.

        Args:
            query: The search query string.
            top_k: Number of results to return.
            category: Optional category filter (metadata field).

        Returns:
            A list of ``RetrievalResult`` sorted by ChromaDB distance
            (cosine), converted to similarity.
        """
        if not query or not query.strip():
            return []

        try:
            where_filter = {"category": category} if category else None

            results = self._collection.query(
                query_texts=[query],
                n_results=top_k * self.top_k_multiplier,
                where=where_filter,
                include=["documents", "metadatas", "distances"],
            )

            if not (results and results.get("ids") and results["ids"][0]):
                return []

            ids = results["ids"][0]
            documents = results.get("documents", [[]])[0] or []
            metadatas = results.get("metadatas", [[]])[0] or []
            distances = results.get("distances", [[]])[0] or []

            out: List[RetrievalResult] = []
            for i, doc_id in enumerate(ids):
                distance = distances[i] if i < len(distances) else 1.0
                similarity = 1.0 / (1.0 + distance) if distance else 1.0
                meta = metadatas[i] if i < len(metadatas) else {}
                doc_text = documents[i] if i < len(documents) else ""

                out.append(RetrievalResult(
                    id=meta.get("entry_id", doc_id),
                    score=similarity,
                    text=doc_text,
                    metadata=meta,
                    rank=i,
                    source="dense",
                ))

            return out

        except Exception as exc:
            get_logger().error("DenseRetriever search error: %s", exc)
            return []


# ---------------------------------------------------------------------------
# Fusion Retriever (RRF)
# ---------------------------------------------------------------------------

class FusionRetriever:
    """Combines dense + sparse results via Reciprocal Rank Fusion (RRF).

    RRF score = Σ 1 / (k + rank_i(result))

    where ``rank_i`` is the 0-based rank from each retriever and ``k`` is
    a smoothing constant (default 60, per the original RRF paper).
    """

    def __init__(self, k: int = 60):
        if k <= 0:
            raise ValueError("RRF constant k must be positive")
        self._k = k

    def fuse(
        self,
        dense_results: List[RetrievalResult],
        sparse_results: List[RetrievalResult],
        top_k: int = 10,
    ) -> List[RetrievalResult]:
        """Fuse dense and sparse result lists via RRF.

        Args:
            dense_results: Results from ``DenseRetriever.search()``.
            sparse_results: Results from a sparse retriever (converted to
                            ``RetrievalResult`` with ``source="sparse"``).
            top_k: Maximum number of fused results to return.

        Returns:
            A list of ``RetrievalResult`` sorted by descending RRF score.
        """
        if not dense_results and not sparse_results:
            return []

        # Accumulate RRF scores
        rrf_scores: Dict[str, float] = defaultdict(float)
        result_map: Dict[str, RetrievalResult] = {}

        for rank, r in enumerate(dense_results):
            rrf_scores[r.id] += 1.0 / (self._k + rank + 1)
            if r.id not in result_map:
                result_map[r.id] = r

        for rank, r in enumerate(sparse_results):
            rrf_scores[r.id] += 1.0 / (self._k + rank + 1)
            if r.id not in result_map:
                result_map[r.id] = r

        if not rrf_scores:
            return []

        # Sort by descending RRF score
        sorted_ids = sorted(rrf_scores.keys(), key=lambda x: -rrf_scores[x])

        out: List[RetrievalResult] = []
        for rank, doc_id in enumerate(sorted_ids[:top_k]):
            result = result_map[doc_id]
            out.append(RetrievalResult(
                id=doc_id,
                score=rrf_scores[doc_id],
                text=result.text,
                metadata=result.metadata,
                rank=rank,
                source="fusion",
            ))

        return out


# ---------------------------------------------------------------------------
# Convenience: run the full hybrid pipeline
# ---------------------------------------------------------------------------

def hybrid_retrieve(
    query: str,
    dense_retriever: DenseRetriever,
    sparse_retriever: Any,  # SparseRetriever from kb.sparse_index
    top_k: int = 10,
    dense_top_k: Optional[int] = None,
    sparse_top_k: Optional[int] = None,
    category: Optional[str] = None,
    fusion_k: int = 60,
) -> List[RetrievalResult]:
    """Run a complete hybrid retrieval (dense → sparse → RRF fusion).

    This is a convenience function that wires together the dense retriever,
    the sparse retriever, and RRF fusion in one call.

    Args:
        query: The search query.
        dense_retriever: A configured ``DenseRetriever`` instance.
        sparse_retriever: A ``SparseRetriever`` instance (from
                          ``kb.sparse_index``). Can be ``None`` to
                          skip sparse retrieval.
        top_k: Final number of results to return after fusion.
        dense_top_k: How many candidates to fetch from dense (default:
                     ``top_k * 2``).
        sparse_top_k: How many candidates to fetch from sparse (default:
                      ``top_k * 2``).
        category: Optional category filter for dense retrieval.
        fusion_k: RRF constant.

    Returns:
        Fused results sorted by descending RRF score.
    """
    dense_top_k = dense_top_k or top_k * 2
    sparse_top_k = sparse_top_k or top_k * 2

    # Dense retrieval
    dense_results = dense_retriever.search(
        query, top_k=dense_top_k, category=category,
    )

    # Sparse retrieval
    sparse_results: List[RetrievalResult] = []
    if sparse_retriever is not None:
        try:
            raw_sparse = sparse_retriever.search(query, top_k=sparse_top_k)
            for rank, sr in enumerate(raw_sparse):
                sparse_results.append(RetrievalResult(
                    id=sr.id,
                    score=sr.score,
                    text=sr.metadata.get("text", ""),
                    metadata=sr.metadata,
                    rank=rank,
                    source="sparse",
                ))
        except Exception as exc:
            get_logger().warning("Sparse retrieval error (skipping): %s", exc)

    # Fuse
    fusor = FusionRetriever(k=fusion_k)
    return fusor.fuse(dense_results, sparse_results, top_k=top_k)
