"""Integration tests for `KBStore` and the high-level `kb.api` functions.

These tests instantiate an isolated `KBStore` pointing at a `tmp_path`, so
they never touch the real persistence directory.
"""

import pytest

pytest.importorskip("chromadb", reason="chromadb is required for store tests")

from kb import (  # noqa: E402  (after importorskip)
    add_entry,
    ask,
    populate_workspace,
    reset,
    search,
    stats,
)
from kb.store import KBStore  # noqa: E402


@pytest.fixture
def store(tmp_path):
    """Fresh KBStore in an isolated directory for each test."""
    return KBStore(persist_directory=tmp_path / "chroma_db")


def test_empty_store_has_zero_entries(store):
    assert store.count() == 0


def test_add_then_stats_reflects_entry(store):
    r = add_entry(
        entry_type="pattern", category="class",
        title="Foo", finding="bar", solution="baz",
        confidence=0.95, store=store,
    )
    assert r.success
    assert r.entry_id is not None
    s = stats(store=store)
    assert s.success
    assert s.total_entries == 1
    assert s.by_type.get("pattern") == 1
    assert s.by_category.get("class") == 1
    assert s.confidence_distribution["high"] == 1


def test_add_then_search_finds_entry(store):
    add_entry(
        entry_type="pattern", category="class",
        title="UniqueWidget42", finding="x", solution="y",
        store=store,
    )
    r = search("UniqueWidget42", top_k=3, store=store)
    assert r.success
    assert any(e.title == "UniqueWidget42" for e in r.entries)


def test_search_with_category_filter(store):
    add_entry("pattern", "class", "ThingA", "fa", "sa", store=store)
    add_entry("pattern", "function", "ThingB", "fb", "sb", store=store)
    r = search("Thing", top_k=5, category="class", store=store)
    assert r.success
    assert all(e.category == "class" for e in r.entries)
    assert all(e.title != "ThingB" for e in r.entries)


def test_ask_returns_synthesized_answer_when_data_exists(store):
    add_entry("pattern", "class", "SynthMe",
              finding="this is the finding",
              solution="this is the solution",
              confidence=0.85, store=store)
    r = ask("SynthMe", top_k=3, store=store)
    assert r.success
    assert r.confidence > 0.0
    assert "SynthMe" in r.answer
    assert "You are an AI agent" not in r.answer  # no prompt template


def test_ask_with_no_data_returns_zero_confidence(store):
    r = ask("nothing here", top_k=3, store=store)
    assert r.success
    assert r.confidence == 0.0
    assert r.sources == []


def test_reset_clears_all_entries(store):
    add_entry("pattern", "class", "A", "fa", "sa", store=store)
    add_entry("finding", "function", "B", "fb", "sb", store=store)
    assert stats(store=store).total_entries == 2

    r = reset(store=store)
    assert r.success
    assert r.total_entries == 0
    assert stats(store=store).total_entries == 0


def test_populate_workspace_on_tiny_python_dir(tmp_path):
    """Walk a temp dir containing one .py file -> 1 class + 1 method + 1 function."""
    sample = tmp_path / "sample.py"
    sample.write_text(
        "class Widget:\n"
        "    def hello(self):\n"
        "        return 'hi'\n"
        "\n"
        "def standalone():\n"
        "    return 1\n"
    )
    store = KBStore(persist_directory=tmp_path / "chroma_db")
    r = populate_workspace(
        workspace_root=str(tmp_path),
        include_python=True,
        include_markdown=False,
        reset_first=True,
        store=store,
    )
    assert r.success
    assert r.files_processed == 1
    # Widget class + Widget.hello method + standalone function = 3 entries
    assert r.total_entries == 3
    assert r.by_pattern[".py"] == 3


def test_populate_workspace_rejects_missing_root(tmp_path):
    r = populate_workspace(
        workspace_root=str(tmp_path / "does-not-exist"),
        store=KBStore(persist_directory=tmp_path / "chroma_db"),
    )
    assert not r.success
    assert "does not exist" in (r.error or "")


def test_populate_workspace_requires_at_least_one_file_type(tmp_path):
    r = populate_workspace(
        workspace_root=str(tmp_path),
        include_python=False,
        include_markdown=False,
        reset_first=False,
        store=KBStore(persist_directory=tmp_path / "chroma_db"),
    )
    assert not r.success
    assert "file types" in (r.error or "")


def test_add_entry_with_invalid_confidence_via_api_still_succeeds(store):
    """`kb.api.add_entry` does not validate confidence; the MCP layer does."""
    r = add_entry("pattern", "class", "T", "f", "s", confidence=2.5, store=store)
    assert r.success  # api.add_entry is permissive; server.kb_add_tool is the gate


def test_iter_metadata_walks_entire_collection_across_pages(store):
    """`iter_metadata` must page past its batch_size.

    Regression guard: `stats()` previously read a 1000-row sample, so any KB with
    more than 1000 entries produced breakdowns that did not match the total.
    """
    n = 25
    for i in range(n):
        add_entry("finding", "method", f"Entry{i:03d}", f"f{i}", "s", store=store)

    assert store.count() == n
    # batch_size deliberately smaller than n -> forces multi-page traversal
    metas = list(store.iter_metadata(batch_size=10))
    assert len(metas) == n  # every row visited exactly once, across 3 pages


def test_stats_breakdowns_reconcile_with_total(store):
    """Regression: by_type / by_category / confidence buckets must sum to total."""
    for i in range(12):
        add_entry("pattern", "class", f"P{i:03d}", "f", "s",
                  confidence=0.95, store=store)
    for i in range(8):
        add_entry("finding", "method", f"M{i:03d}", "f", "s",
                  confidence=0.95, store=store)
    for i in range(5):
        add_entry("decision", "function", f"F{i:03d}", "f", "s",
                  confidence=0.5, store=store)

    s = stats(store=store)
    assert s.success
    assert s.total_entries == 25
    # The core invariant the old sampling-based stats violated:
    assert sum(s.by_type.values()) == s.total_entries
    assert sum(s.by_category.values()) == s.total_entries
    assert sum(s.confidence_distribution.values()) == s.total_entries
    # Exact distribution
    assert s.by_type == {"pattern": 12, "finding": 8, "decision": 5}
    assert s.by_category == {"class": 12, "method": 8, "function": 5}
    assert s.confidence_distribution["high"] == 20
    assert s.confidence_distribution["low"] == 5
