"""BM25 sparse index for lexical retrieval complementing the dense ChromaDB index.

Provides a ``SparseRetriever`` class that:

1. Builds a BM25 index from KB entry texts.
2. Supports incremental update when new entries are added.
3. Provides ``search()`` returning scored results compatible with the
   rest of the ``kb`` package.

Requires the ``bm25s`` optional dependency (``pip install knowledge-base[sparse]``).

Typical usage::

    from kb.sparse_index import SparseRetriever

    retriever = SparseRetriever()
    retriever.build_index(corpus, doc_ids)
    results = retriever.search("query text", top_k=5)
"""

import threading
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .logging import get_logger


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

BM25S_AVAILABLE: bool = False
try:
    import bm25s
    BM25S_AVAILABLE = True
except ImportError:
    bm25s = None  # type: ignore[assignment]


@dataclass
class SparseResult:
    """A single result from a sparse (BM25) search.

    Attributes:
        id: The KB entry ID.
        score: BM25 relevance score.
        metadata: Optional metadata dict carried from the corpus.
    """
    id: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Sparse retriever
# ---------------------------------------------------------------------------

class SparseRetriever:
    """BM25-based sparse retriever for lexical search.

    Thread-safe: all public methods acquire a reentrant lock so the index
    can be safely read while being rebuilt.

    Args:
        k1: BM25 k1 parameter (term saturation factor). Default 1.5.
        b: BM25 b parameter (document length normalization). Default 0.75.
        delta: BM25 delta parameter (for the ``lucene`` method). Default 0.5.
        method: BM25 scoring method (``"lucene"``, ``"atire"``, ``"bm25+"``,
                ``"bm25l"``). Default ``"lucene"``.
    """

    def __init__(
        self,
        k1: float = 1.5,
        b: float = 0.75,
        delta: float = 0.5,
        method: str = "lucene",
    ):
        if not BM25S_AVAILABLE:
            raise ImportError(
                "bm25s is required for sparse retrieval. "
                "Install it with: pip install knowledge-base[sparse]"
            )

        self._k1 = k1
        self._b = b
        self._delta = delta
        self._method = method
        self._lock = threading.RLock()

        # Internal state
        self._model: Any = None  # bm25s.BM25 instance
        self._doc_ids: List[str] = []
        self._corpus_texts: List[str] = []
        self._is_built: bool = False

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_built(self) -> bool:
        """Whether the index has been built at least once."""
        return self._is_built

    @property
    def size(self) -> int:
        """Number of documents in the index."""
        with self._lock:
            return len(self._doc_ids) if self._is_built else 0

    # ------------------------------------------------------------------
    # Index building
    # ------------------------------------------------------------------

    def build_index(
        self,
        corpus: List[str],
        doc_ids: List[str],
    ) -> None:
        """Build (or rebuild) the BM25 index from a corpus of texts.

        Args:
            corpus: List of document texts to index.
            doc_ids: Parallel list of entry IDs (same length as ``corpus``).
        """
        if len(corpus) != len(doc_ids):
            raise ValueError(
                f"corpus length ({len(corpus)}) must match "
                f"doc_ids length ({len(doc_ids)})"
            )
        if not corpus:
            get_logger().warning("SparseRetriever.build_index called with empty corpus")
            self._model = None
            self._doc_ids = []
            self._corpus_texts = []
            self._is_built = False
            return

        with self._lock:
            get_logger().info(
                "Building BM25 index with %d documents ...", len(corpus)
            )

            # Tokenize the corpus
            tokenized_corpus = bm25s.tokenize(corpus, show_progress=False)

            # Create and index
            self._model = bm25s.BM25(
                k1=self._k1,
                b=self._b,
                delta=self._delta,
                method=self._method,
            )
            self._model.index(tokenized_corpus, show_progress=False)

            # Store metadata
            self._doc_ids = list(doc_ids)
            self._corpus_texts = list(corpus)
            self._is_built = True

            get_logger().info(
                "BM25 index built: %d documents, %d unique terms",
                len(corpus),
                len(self._model.vocab_dict) if self._model.vocab_dict else 0,
            )

    def add_documents(
        self,
        texts: List[str],
        doc_ids: List[str],
    ) -> None:
        """Incrementally add new documents to the index.

        If the index has not been built yet, this calls ``build_index``
        with the provided documents. Otherwise it appends the new docs
        and triggers a full rebuild (BM25 requires global IDF).

        .. note::
            BM25 does not support truly incremental updates because IDF
            statistics are corpus-global. This method appends the new
            documents and rebuilds the index from scratch on the enlarged
            corpus.

        Args:
            texts: List of document texts to add.
            doc_ids: Parallel list of entry IDs.
        """
        if not texts:
            return
        if len(texts) != len(doc_ids):
            raise ValueError(
                f"texts length ({len(texts)}) must match "
                f"doc_ids length ({len(doc_ids)})"
            )

        with self._lock:
            if not self._is_built:
                self.build_index(texts, doc_ids)
                return

            # Append to existing corpus and rebuild
            self._corpus_texts.extend(texts)
            self._doc_ids.extend(doc_ids)

            get_logger().info(
                "Rebuilding BM25 index with %d documents (+%d new) ...",
                len(self._corpus_texts),
                len(texts),
            )

            tokenized_corpus = bm25s.tokenize(self._corpus_texts, show_progress=False)
            self._model = bm25s.BM25(
                k1=self._k1,
                b=self._b,
                delta=self._delta,
                method=self._method,
            )
            self._model.index(tokenized_corpus, show_progress=False)
            self._is_built = True

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        top_k: int = 10,
    ) -> List[SparseResult]:
        """Search the BM25 index for the given query.

        Args:
            query: Natural language query string.
            top_k: Maximum number of results to return.

        Returns:
            A list of ``SparseResult`` objects sorted by descending score.
            Empty if the index has not been built.
        """
        if not self._is_built or self._model is None:
            get_logger().warning("SparseRetriever.search called before index built")
            return []

        if not query or not query.strip():
            return []

        with self._lock:
            try:
                # Tokenize the query and retrieve
                tokenized_query = bm25s.tokenize([query], show_progress=False)
                results = self._model.retrieve(
                    tokenized_query,
                    k=top_k,
                    show_progress=False,
                )

                # The Results object has documents (indices) and scores
                doc_indices: List[int] = results.documents[0].tolist()
                doc_scores: List[float] = results.scores[0].tolist()

                # Build results, filtering zero-score entries
                sparse_results: List[SparseResult] = []
                for idx, score in zip(doc_indices, doc_scores):
                    if score <= 0.0:
                        continue  # No relevance
                    if idx < 0 or idx >= len(self._doc_ids):
                        continue

                    sparse_results.append(SparseResult(
                        id=self._doc_ids[idx],
                        score=float(score),
                        metadata={
                            "text": self._corpus_texts[idx][:200],
                            "index": int(idx),
                        },
                    ))

                return sparse_results

            except Exception as exc:
                get_logger().error("BM25 search error: %s", exc)
                return []

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """Clear the index and all stored data."""
        with self._lock:
            self._model = None
            self._doc_ids = []
            self._corpus_texts = []
            self._is_built = False
            get_logger().info("SparseRetriever cleared")


# ---------------------------------------------------------------------------
# Module-level default retriever (lazy, process-wide)
# ---------------------------------------------------------------------------

_default_retriever: Optional[SparseRetriever] = None
_default_retriever_lock = threading.Lock()


def get_default_retriever() -> Optional[SparseRetriever]:
    """Return the process-wide default ``SparseRetriever``.

    Returns ``None`` if ``bm25s`` is not available (optional dependency).
    """
    global _default_retriever
    if not BM25S_AVAILABLE:
        return None
    if _default_retriever is None:
        with _default_retriever_lock:
            if _default_retriever is None:
                _default_retriever = SparseRetriever()
    return _default_retriever


def set_default_retriever(retriever: Optional[SparseRetriever]) -> None:
    """Override the process-wide default retriever.

    Pass ``None`` to reset to lazy-initialised behaviour.
    """
    global _default_retriever
    _default_retriever = retriever
