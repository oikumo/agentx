"""pytest configuration: put the package root on sys.path so `import kb` works.

Also provides shared fixtures used across multiple test files.
"""

import sys
from pathlib import Path

import pytest

# Repo layout: mcp_servers/knowledge_base/tests/conftest.py
# Parent of `tests/` holds both `kb/` and `server.py`.
PACKAGE_ROOT = Path(__file__).resolve().parent.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def store(tmp_path):
    """Isolated KBStore per test."""
    from kb.store import KBStore
    return KBStore(persist_directory=tmp_path / "chroma_db")


@pytest.fixture
def dense_retriever(store):
    """DenseRetriever with the default model (miniLM-L6-v2, no download needed)."""
    from kb.retrieval import DenseRetriever
    return DenseRetriever(model_name="miniLM-L6-v2", store=store)


@pytest.fixture
def sparse_retriever():
    """Fresh SparseRetriever per test."""
    from kb.sparse_index import SparseRetriever
    return SparseRetriever()


@pytest.fixture
def populated_store(store):
    """Store populated with entries directly via the DenseRetriever's collection."""
    from kb.retrieval import DenseRetriever
    dr = DenseRetriever(model_name="miniLM-L6-v2", store=store)
    col = dr._collection

    entries_data = [
        ("PAT-001", "KBStore class for ChromaDB persistence",
         {"entry_id": "PAT-001", "type": "pattern", "category": "class",
          "title": "KBStore", "finding": "ChromaDB wrapper class",
          "solution": "use KBStore for persistence", "confidence": 0.95}),
        ("FIND-001", "BM25 search for lexical retrieval",
         {"entry_id": "FIND-001", "type": "finding", "category": "method",
          "title": "BM25 Search", "finding": "lexical search using BM25",
          "solution": "BM25 complements dense retrieval", "confidence": 0.90}),
        ("PAT-002", "Tokenize utility for text processing",
         {"entry_id": "PAT-002", "type": "pattern", "category": "function",
          "title": "Tokenize", "finding": "text tokenization utility",
          "solution": "use simple_tokenize for keyword scoring", "confidence": 0.85}),
    ]

    for eid, doc_text, meta in entries_data:
        col.add(documents=[doc_text], metadatas=[meta], ids=[eid])

    return store


@pytest.fixture
def reranker():
    """CrossEncoderReranker (no model loaded — lazy)."""
    from kb.reranking import CrossEncoderReranker
    return CrossEncoderReranker()
