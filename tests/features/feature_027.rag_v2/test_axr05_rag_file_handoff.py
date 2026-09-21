"""AXR-05 durable regression: RAG retrieve-offload-delegate file handoff (package 5).

Reconstructs the 8 inline regression scenarios from
``sandbox/consistency_enforcement/round_006_package_05_rag_file_handoff.md``
§Result as durable tests. Repair under test (D6 keep-delegate binding):

* ``_search_documents_impl`` mints a unique ``search_id`` per invocation and
  offloads to absolute ``/retrieval/<search_id>/chunk_<i>.txt`` keys, so the
  deepagents filesystem middleware (``validate_path``) passes them through
  UNCHANGED and sequential/parallel searches never overwrite each other;
* retriever-construction / retrieval / upload-raise failures return a
  structured ``error`` (never raise); per-file upload failures land in
  ``upload_errors`` and are NOT counted in ``chunks_uploaded``;
* ``error=None`` + empty ``hits`` is a successful EMPTY retrieval, distinct
  from offload failure; ``RagSearchHit.backend_path`` + ``SearchDocumentsResult.
  search_id``/``upload_errors`` keep the schema, analyst prompt, and citations
  in agreement; ``build_rag_v2_tools(path, backend=None)`` binds the backend
  and ``RagV2AgentService`` constructs it BEFORE the default tools.

Acceptance is the round_001 §AXR-05 Regression check: exercise the
service-created search tool in a local graph, read each returned path through
the analyst's actual filesystem path (``validate_path`` + ``backend.read``),
keep each retrieval's paths readable/unchanged until its analyst calls finish,
never overwrite across sequential/parallel searches in a turn, never count
failed uploads as successes, represent empty retrieval correctly, keep
citations mapped, and inject factory/upload/partial failures.

Probe-retired note (D4): this module REPLACES the AXR-05 assertions of
``sandbox/consistency_enforcement/round_001_review_probes.py``
(``test_axr05_service_tool_omits_backend``,
``test_axr05_failed_upload_reported_successfully``,
``test_axr05_setup_and_upload_exceptions_escape``,
``test_axr05_real_graph_path_normalization_and_overwrite``) — those
observation probes assert the faulty behavior and must fail post-repair; they
are never gated in CI. All fixtures hermetic (temp dirs, fake retrievers,
mocked/fake LLMs, no network).
"""

from __future__ import annotations

import os
import socket
import tempfile
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

os.environ["PYTHON_DOTENV_DISABLED"] = "1"
os.environ["LLAMA_CPP_MODELS_CACHE_PATH"] = tempfile.gettempdir()
os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def refused(*args, **kwargs):
        raise AssertionError("regression tests must not open network connections")

    monkeypatch.setattr(socket.socket, "connect", refused)
    monkeypatch.setattr(socket, "create_connection", refused)


def _run_in_filesystem_graph(probe_fn):
    """Run ``probe_fn(state)`` inside a real StateBackend graph.

    Mirrors the codebase's own graph harness (the retired
    ``test_axr05_real_graph_path_normalization_and_overwrite`` probe):
    ``StateGraph(FilesystemState)`` with a single ``probe`` node,
    ``START → probe → END``, invoked with ``{"messages": [], "files": {}}``.
    ``StateBackend`` requires this graph context — any ``upload_files``/``read``
    outside it raises ``RuntimeError`` — so every real-backend scenario runs
    through here and asserts on captured values AFTER ``invoke`` returns.
    """
    from deepagents.middleware.filesystem import FilesystemState
    from langgraph.graph import END, START, StateGraph

    graph = StateGraph(FilesystemState)
    graph.add_node("probe", probe_fn)
    graph.add_edge(START, "probe")
    graph.add_edge("probe", END)
    graph.compile().invoke({"messages": [], "files": {}})


def _two_hit_retriever(contents=("content of chunk 0", "content of chunk 1")):
    rows = [
        ("chunk_id_0", contents[0], 0.9, "doc0.md", None, 42),
        ("chunk_id_1", contents[1], 0.7, "doc1.pdf", 7, None),
    ]
    return lambda query, k: list(rows)


def test_axr05_analyst_reads_every_returned_path_in_graph(tmp_path):
    """Every ``backend_path`` reads through ``validate_path`` + ``backend.read``."""
    from deepagents.backends import StateBackend
    from deepagents.middleware.filesystem import validate_path
    from agentx.model.rag_v2.rag_v2_tools import _search_documents_impl

    backend = StateBackend()
    captured: dict = {}

    def probe(state):
        captured["result"] = _search_documents_impl(
            "q",
            str(tmp_path),
            k=2,
            backend=backend,
            _retriever=_two_hit_retriever(),
        )
        captured["reads"] = [
            backend.read(validate_path(hit.backend_path))
            for hit in captured["result"].hits
        ]
        captured["validated"] = [
            validate_path(hit.backend_path) for hit in captured["result"].hits
        ]
        return {}

    _run_in_filesystem_graph(probe)

    result = captured["result"]
    assert len(result.hits) == 2
    assert result.error is None and result.chunks_uploaded == 2
    for i, (hit, validated, read) in enumerate(
        zip(result.hits, captured["validated"], captured["reads"])
    ):
        # Absolute keys pass the middleware through UNCHANGED.
        assert validated == hit.backend_path
        assert hit.backend_path.startswith("/retrieval/")
        assert (
            hit.backend_path == f"/retrieval/{result.search_id}/chunk_{i}.txt"
        )
        assert read.error is None, (
            f"analyst read of {hit.backend_path} failed: {read.error}"
        )


def test_axr05_sequential_searches_never_overwrite(tmp_path):
    """First chunk stays readable + byte-identical after a second search."""
    from deepagents.backends import StateBackend
    from deepagents.middleware.filesystem import validate_path
    from agentx.model.rag_v2.rag_v2_tools import _search_documents_impl

    backend = StateBackend()
    captured: dict = {}

    def probe(state):
        first = _search_documents_impl(
            "q",
            str(tmp_path),
            backend=backend,
            _retriever=lambda q, k: [("c0", "first-search", 0.9)],
        )
        second = _search_documents_impl(
            "q",
            str(tmp_path),
            backend=backend,
            _retriever=lambda q, k: [("c0", "second-search", 0.9)],
        )
        captured["first"] = first
        captured["second"] = second
        # Read the FIRST search's chunk AFTER the second search uploaded.
        captured["first_download"] = backend.download_files(
            [first.hits[0].backend_path]
        )[0]
        captured["second_download"] = backend.download_files(
            [second.hits[0].backend_path]
        )[0]
        captured["first_read"] = backend.read(
            validate_path(first.hits[0].backend_path)
        )
        return {}

    _run_in_filesystem_graph(probe)

    first, second = captured["first"], captured["second"]
    assert first.search_id != second.search_id, "each search mints a unique search_id"
    assert first.hits[0].backend_path != second.hits[0].backend_path
    assert captured["first_read"].error is None
    assert captured["first_download"].error is None
    assert captured["first_download"].content == b"first-search"
    assert captured["second_download"].content == b"second-search"


def test_axr05_parallel_same_turn_searches_never_overwrite(tmp_path):
    """Two searches in one turn/graph node get unique ids; both stay readable."""
    from deepagents.backends import StateBackend
    from deepagents.middleware.filesystem import validate_path
    from agentx.model.rag_v2.rag_v2_tools import _search_documents_impl

    backend = StateBackend()
    captured: dict = {}

    def probe(state):
        # Models one turn's parallel tool calls: back-to-back invocations in a
        # single superstep — each must mint its own search_id, so the parallel
        # analysts never share a key.
        results = [
            _search_documents_impl(
                "q",
                str(tmp_path),
                backend=backend,
                _retriever=lambda q, k, c=c: [("c0", c, 0.9)],
            )
            for c in ("parallel-a", "parallel-b")
        ]
        captured["results"] = results
        captured["reads"] = [
            backend.read(validate_path(r.hits[0].backend_path)) for r in results
        ]
        captured["downloads"] = [
            backend.download_files([r.hits[0].backend_path])[0] for r in results
        ]
        return {}

    _run_in_filesystem_graph(probe)

    first, second = captured["results"]
    assert (
        first.search_id != second.search_id
    ), "parallel searches must not share a search_id"
    assert first.hits[0].backend_path != second.hits[0].backend_path
    for read in captured["reads"]:
        assert read.error is None
    assert {d.content for d in captured["downloads"]} == {b"parallel-a", b"parallel-b"}


def test_axr05_failed_upload_not_counted_as_success(tmp_path):
    """Per-file upload error → ``chunks_uploaded=0`` + ``upload_errors`` (no raise)."""
    from deepagents.backends.protocol import FileUploadResponse
    from agentx.model.rag_v2.rag_v2_tools import _search_documents_impl

    backend = Mock()
    backend.upload_files.return_value = [
        FileUploadResponse(path="chunk_0.txt", error="permission_denied"),
    ]

    result = _search_documents_impl(
        "q",
        str(tmp_path),
        backend=backend,
        _retriever=lambda q, k: [("c0", "content", 0.9)],
    )

    assert result.chunks_uploaded == 0, "failed uploads must NOT be counted"
    assert len(result.upload_errors) == 1
    assert "permission_denied" in result.upload_errors[0]
    # Per-file failure is reported, not a hard error; content kept for answers.
    assert result.error is None
    assert result.hits and result.hits[0].content == "content"


def test_axr05_partial_upload_reports_success_and_failure(tmp_path):
    """1 success + 1 failure → ``chunks_uploaded=1`` + one ``upload_errors`` entry."""
    from deepagents.backends.protocol import FileUploadResponse
    from agentx.model.rag_v2.rag_v2_tools import _search_documents_impl

    backend = Mock()
    backend.upload_files.return_value = [
        FileUploadResponse(path="/retrieval/x/chunk_0.txt", error=None),
        FileUploadResponse(path="/retrieval/x/chunk_1.txt", error="permission_denied"),
    ]

    result = _search_documents_impl(
        "q",
        str(tmp_path),
        k=2,
        backend=backend,
        _retriever=lambda q, k: [("c0", "a", 0.9), ("c1", "b", 0.8)],
    )

    assert result.chunks_uploaded == 1
    assert len(result.upload_errors) == 1
    assert "chunk_1" in result.upload_errors[0]
    assert result.error is None
    assert len(result.hits) == 2


def test_axr05_empty_retrieval_distinct_from_offload_failure(tmp_path):
    """``error=None`` + empty hits = successful EMPTY retrieval (no upload)."""
    from agentx.model.rag_v2.rag_v2_tools import _search_documents_impl

    backend = Mock()
    result = _search_documents_impl(
        "q", str(tmp_path), backend=backend, _retriever=lambda q, k: []
    )

    assert result.error is None
    assert result.hits == []
    assert result.chunks_uploaded == 0
    assert result.upload_errors == []
    backend.upload_files.assert_not_called()


def test_axr05_factory_and_upload_exceptions_are_structured_errors(
    tmp_path, monkeypatch
):
    """Factory/upload raises → structured ``error``, never raised (impl AND bound tool)."""
    from agentx.model.rag_v2 import rag_v2_tools as rag
    from agentx.model.rag_v2.query import rag_v2_retriever as retrieval

    rows = lambda q, k: [("c0", "content", 0.9)]  # noqa: E731

    # 7a. retriever-construction failure through the bare impl.
    monkeypatch.setattr(
        retrieval,
        "build_retriever",
        Mock(side_effect=RuntimeError("synthetic factory failure")),
    )
    impl_factory = rag._search_documents_impl("q", str(tmp_path), backend=Mock())
    assert impl_factory.error is not None
    assert "retriever construction failed" in impl_factory.error
    assert impl_factory.hits == [] and impl_factory.chunks_uploaded == 0

    # 7b. retriever-construction failure through the BOUND public tool.
    bound_factory = rag.build_rag_v2_tools(str(tmp_path))[0].invoke({"query": "q"})
    assert bound_factory.error is not None
    assert "retriever construction failed" in bound_factory.error

    # 7c. upload raise through the bare impl.
    monkeypatch.setattr(retrieval, "build_retriever", lambda path: rows)
    raising = SimpleNamespace(
        upload_files=Mock(side_effect=RuntimeError("synthetic upload failure"))
    )
    impl_upload = rag._search_documents_impl("q", str(tmp_path), backend=raising)
    assert impl_upload.error is not None
    assert "chunk upload failed" in impl_upload.error
    assert impl_upload.chunks_uploaded == 0
    assert any("upload raised" in e for e in impl_upload.upload_errors)

    # 7d. upload raise through the BOUND public tool (backend bound at build time).
    bound_tools = rag.build_rag_v2_tools(str(tmp_path), backend=raising)
    bound_upload = bound_tools[0].invoke({"query": "q"})
    assert bound_upload.error is not None
    assert "chunk upload failed" in bound_upload.error
    assert bound_upload.chunks_uploaded == 0


def test_axr05_service_tool_wired_to_service_backend_in_graph(tmp_path, monkeypatch):
    """Service-built search tool offloads into the service backend; analyst-readable."""
    from deepagents.backends import StateBackend
    from deepagents.middleware.filesystem import validate_path
    from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
    from agentx.model.rag_v2.query import rag_v2_retriever as retrieval
    from agentx.model.rag_v2.rag_v2_agent_service import RagV2AgentService

    # Fake retriever so no live ChromaDB store is needed.
    monkeypatch.setattr(
        retrieval,
        "build_retriever",
        lambda path: (lambda q, k: [("c0", "svc content", 0.9, "doc.md", None, 1)]),
    )

    backend = StateBackend()
    # GenericFakeChatModel needs an Iterator (pydantic validates isinstance);
    # a MagicMock LLM fails the summarization middleware's BaseChatModel check.
    service = RagV2AgentService(
        repository_path=str(tmp_path),
        llm=GenericFakeChatModel(messages=iter(["ok"])),
        backend=backend,
    )
    assert service._backend is backend, "service must bind the SAME backend"
    search = next(t for t in service._tools if t.name == "search_documents")
    captured: dict = {}

    def probe(state):
        result = search.invoke({"query": "q"})
        captured["result"] = result
        captured["analyst_read"] = backend.read(
            validate_path(result.hits[0].backend_path)
        )
        captured["service_read"] = service._backend.read(
            validate_path(result.hits[0].backend_path)
        )
        return {}

    _run_in_filesystem_graph(probe)

    result = captured["result"]
    assert result.error is None and result.chunks_uploaded == 1
    assert captured["analyst_read"].error is None
    assert captured["service_read"].error is None
