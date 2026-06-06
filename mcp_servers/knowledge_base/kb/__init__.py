"""Knowledge Base — flat library used by the MCP server.

Public API (all return `kb.models` dataclasses):

    from kb import search, ask, add_entry, stats, reset, populate_workspace

The default `KBStore` is lazily created and persists at
`mcp_servers/knowledge_base/chroma_db/`. Tests instantiate their own `KBStore`
and pass it explicitly (`store=` keyword on every public call).
"""

from .api import (
    add_entry,
    ask,
    populate_workspace,
    reset,
    search,
    stats,
)
from .models import (
    AddResult,
    AskResult,
    AskSource,
    KBEntry,
    PopulateResult,
    ResetResult,
    SearchResult,
    StatsResult,
)
from .retrieval import (
    DenseRetriever,
    FusionRetriever,
    RetrievalResult,
    hybrid_retrieve,
)
from .sparse_index import SparseRetriever, get_default_retriever
from .store import KBStore, get_default_store, set_default_store
from .query_engine import QueryEngine
from .synthesis import LLMSynthesizer, llm_synthesize, synthesize
from .eval import RetrievalEvaluator, EvalResult, ComparisonResult, quick_eval, compare_configs
from .reranking import CrossEncoderReranker, RerankerResult

__all__ = [
    # functions
    "search", "ask", "add_entry", "stats", "reset", "populate_workspace",
    # store
    "KBStore", "get_default_store", "set_default_store",
    # retrieval
    "DenseRetriever", "FusionRetriever", "RetrievalResult", "hybrid_retrieve",
    # sparse
    "SparseRetriever", "get_default_retriever",
    # query engine
    "QueryEngine",
    # synthesis
    "LLMSynthesizer", "llm_synthesize", "synthesize",
    # reranking
    "CrossEncoderReranker", "RerankerResult",
    # evaluation
    "RetrievalEvaluator", "EvalResult", "ComparisonResult", "quick_eval", "compare_configs",
    # models
    "KBEntry", "SearchResult", "AskResult", "AskSource",
    "AddResult", "StatsResult", "ResetResult", "PopulateResult",
]
