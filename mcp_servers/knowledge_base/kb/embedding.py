"""Configurable embedding models with lazy loading, registry, and caching.

Provides a registry of supported embedding models that can be used with
ChromaDB collections. Models are lazy-loaded on first use to avoid
unnecessary memory usage.

Supports:
    - ``miniLM-L6-v2`` (384-d, ONNX, fast, default)
    - ``bge-small-en`` (384-d, better quality/size trade-off)
    - ``bge-base-en`` (768-d, strong all-around)
    - ``bge-large-en`` (1024-d, high accuracy)
    - ``bge-m3`` (1024-d, multi-lingual SOTA)
    - ``gte-Qwen2-1.5B`` (1536-d, SOTA 2025)
"""

import functools
import threading
from typing import Any, Callable, Dict, List, Optional, Tuple

from .logging import get_logger


# ---------------------------------------------------------------------------
# LRU Embedding Cache
# ---------------------------------------------------------------------------

class LRUEmbeddingCache:
    """Thread-safe LRU cache for embedding vectors.

    Caches (model_name, text) → embedding_vector pairs to avoid redundant
    computation for frequently-queried text.

    Args:
        capacity: Maximum number of entries in the cache (default: 1000).
    """

    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self._cache: Dict[Tuple[str, str], List[float]] = {}
        self._order: List[Tuple[str, str]] = []
        self._lock = threading.Lock()

    def get(self, model_name: str, text: str) -> Optional[List[float]]:
        """Get a cached embedding."""
        key = (model_name, text)
        with self._lock:
            if key in self._cache:
                # Move to end (most recently used)
                self._order.remove(key)
                self._order.append(key)
                return self._cache[key]
            return None

    def put(self, model_name: str, text: str, vector: List[float]) -> None:
        """Cache an embedding vector."""
        key = (model_name, text)
        with self._lock:
            if key in self._cache:
                self._order.remove(key)
            elif len(self._cache) >= self.capacity:
                # Evict least recently used
                oldest = self._order.pop(0)
                del self._cache[oldest]
            self._cache[key] = vector
            self._order.append(key)

    def clear(self) -> None:
        """Clear the cache."""
        with self._lock:
            self._cache.clear()
            self._order.clear()

    @property
    def size(self) -> int:
        """Current number of cached entries."""
        with self._lock:
            return len(self._cache)


# Global embedding cache (process-wide)
_embedding_cache = LRUEmbeddingCache(capacity=2000)


# ---------------------------------------------------------------------------
# Model descriptors
# ---------------------------------------------------------------------------

class EmbeddingModelInfo:
    """Metadata about a supported embedding model."""

    def __init__(self, name: str, dim: int, model_class: str,
                 description: str = ""):
        self.name = name
        self.dim = dim
        self.model_class = model_class
        self.description = description


# ---------------------------------------------------------------------------
# Model registry
# ---------------------------------------------------------------------------

# Maps model name → dict with info and factory function
_model_registry: Dict[str, Dict[str, Any]] = {}
_model_instances: Dict[str, Any] = {}
_registry_lock = threading.RLock()


def _make_onnx_minilm() -> Any:
    """Create the default ONNX MiniLM-L6-v2 embedding function."""
    from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
    return ONNXMiniLM_L6_V2()


def _make_sentence_transformer(model_name: str) -> Any:
    """Create a SentenceTransformer embedding function.

    Args:
        model_name: HuggingFace model name or path
                    (e.g., ``BAAI/bge-small-en``).

    Returns:
        A ChromaDB-compatible embedding function.
    """
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
    get_logger().info("Loading sentence-transformer model: %s", model_name)
    return SentenceTransformerEmbeddingFunction(model_name=model_name)


def _make_huggingface(model_name: str) -> Any:
    """Create a HuggingFace embedding function.

    Args:
        model_name: HuggingFace model ID (e.g., ``BAAI/bge-m3``).

    Returns:
        A ChromaDB-compatible embedding function.
    """
    from chromadb.utils.embedding_functions import HuggingFaceEmbeddingFunction
    get_logger().info("Loading HuggingFace model: %s", model_name)
    # Use a dummy API key — the model is loaded locally
    return HuggingFaceEmbeddingFunction(model_name=model_name, api_key="")


def register_model(model_name: str, dim: int, factory: Callable[[], Any],
                   description: str = "") -> None:
    """Register an embedding model.

    Args:
        model_name: Identifier used in the ``embedding_model`` param.
        dim: Output dimension of the embedding vectors.
        factory: Zero-argument callable that returns a ChromaDB-compatible
                 embedding function.
        description: Human-readable description.
    """
    with _registry_lock:
        _model_registry[model_name] = {
            "dim": dim,
            "factory": factory,
            "description": description,
            "info": EmbeddingModelInfo(
                name=model_name, dim=dim,
                model_class=factory.__name__,
                description=description,
            ),
        }


def get_embedding_function(model_name: str) -> Any:
    """Get or create a lazy-loaded embedding function.

    Args:
        model_name: Model identifier (e.g., ``"bge-small-en"``).

    Returns:
        A ChromaDB-compatible embedding function.

    Raises:
        ValueError: If the model name is not registered.
    """
    with _registry_lock:
        if model_name in _model_instances:
            return _model_instances[model_name]

        if model_name not in _model_registry:
            raise ValueError(
                f"Unknown embedding model: {model_name!r}. "
                f"Available: {list_models()}"
            )

        info = _model_registry[model_name]
        try:
            instance = info["factory"]()
            _model_instances[model_name] = instance
            get_logger().info(
                "Loaded embedding model '%s' (dim=%d): %s",
                model_name, info["dim"], info["description"],
            )
            return instance
        except Exception as exc:
            get_logger().error(
                "Failed to load embedding model '%s': %s", model_name, exc
            )
            raise


def get_model_dim(model_name: str) -> int:
    """Get the embedding dimension for a registered model.

    Raises:
        ValueError: If the model name is not registered.
    """
    with _registry_lock:
        if model_name not in _model_registry:
            raise ValueError(
                f"Unknown embedding model: {model_name!r}. "
                f"Available: {list_models()}"
            )
        return _model_registry[model_name]["dim"]


def list_models() -> List[str]:
    """List all registered embedding model names."""
    with _registry_lock:
        return list(_model_registry.keys())


def get_model_info(model_name: str) -> EmbeddingModelInfo:
    """Get metadata for a registered model.

    Raises:
        ValueError: If the model name is not registered.
    """
    with _registry_lock:
        if model_name not in _model_registry:
            raise ValueError(
                f"Unknown embedding model: {model_name!r}. "
                f"Available: {list_models()}"
            )
        return _model_registry[model_name]["info"]


def clear_model_cache() -> None:
    """Clear all loaded model instances (forces re-load on next use)."""
    with _registry_lock:
        _model_instances.clear()
        _embedding_cache.clear()


# ---------------------------------------------------------------------------
# Embedding helper (with caching)
# ---------------------------------------------------------------------------

def embed_text(model_name: str, texts: List[str]) -> List[List[float]]:
    """Embed a list of texts using the specified model.

    Uses an LRU cache to avoid redundant computation.

    Args:
        model_name: Model identifier.
        texts: List of text strings to embed.

    Returns:
        List of embedding vectors.
    """
    ef = get_embedding_function(model_name)
    results: List[Optional[List[float]]] = [None] * len(texts)
    uncached_indices: List[int] = []
    uncached_texts: List[str] = []

    # Check cache first
    for i, text in enumerate(texts):
        cached = _embedding_cache.get(model_name, text)
        if cached is not None:
            results[i] = cached
        else:
            uncached_indices.append(i)
            uncached_texts.append(text)

    # Embed uncached texts
    if uncached_texts:
        vectors = ef(uncached_texts)
        for idx, vector in zip(uncached_indices, vectors):
            vec_list = list(vector) if hasattr(vector, '__iter__') else vector
            _embedding_cache.put(model_name, texts[idx], vec_list)
            results[idx] = vec_list

    return [r for r in results if r is not None]


# ---------------------------------------------------------------------------
# Register built-in models
# ---------------------------------------------------------------------------

register_model(
    "miniLM-L6-v2", 384,
    _make_onnx_minilm,
    "Default ONNX all-MiniLM-L6-v2 (384-d, fast)",
)

register_model(
    "bge-small-en", 384,
    lambda: _make_sentence_transformer("BAAI/bge-small-en"),
    "BAAI/bge-small-en (384-d, better quality/size trade-off)",
)

register_model(
    "bge-base-en", 768,
    lambda: _make_sentence_transformer("BAAI/bge-base-en"),
    "BAAI/bge-base-en (768-d, strong all-around)",
)

register_model(
    "bge-large-en", 1024,
    lambda: _make_sentence_transformer("BAAI/bge-large-en"),
    "BAAI/bge-large-en (1024-d, high accuracy)",
)

register_model(
    "bge-m3", 1024,
    lambda: _make_sentence_transformer("BAAI/bge-m3"),
    "BAAI/bge-m3 (1024-d, multi-lingual SOTA)",
)

# gte-Qwen2-1.5B requires a large model download — optional
register_model(
    "gte-Qwen2-1.5B", 1536,
    lambda: _make_huggingface("Alibaba-NLP/gte-Qwen2-1.5B-instruct"),
    "Alibaba-NLP/gte-Qwen2-1.5B-instruct (1536-d, SOTA 2025, large)",
)
