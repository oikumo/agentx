#!/usr/bin/env python3
"""Golden tests for T2-1 sync-closer (feature_065, meta_harness_8).

Acceptance: 3 stranded REDs now-passing close in 1 call; still-failing node writes nothing.
Hermetic: tmp ledger (state.LEDGER_PATH) + mocked cli.run_test — never touches the real ledger.
"""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "omt"))

from tdd import cli, gates, state  # noqa: E402

FEATURE = "feature_synth.tdd_sync"


@pytest.fixture()
def hermetic(tmp_path, monkeypatch):
    monkeypatch.setattr(state, "LEDGER_PATH", tmp_path / "ledger.jsonl")
    monkeypatch.setattr(state, "SNAPSHOT_DIR", tmp_path / "snapshots")
    return tmp_path


def _red(node: str):
    state.write_ledger({
        "kind": "tdd", "session": "s", "state": "red",
        "test_node": node, "target_src": [], "verified": True,
        "exit_code": 1, "feature": FEATURE,
    })


def _green(node: str):
    state.write_ledger({
        "kind": "tdd", "session": "s", "state": "green",
        "test_node": node, "verified": True, "exit_code": 0,
        "feature": FEATURE,
    })


class TestGetDanglingReds:
    def test_reuses_same_node_granularity(self, hermetic):
        _red("t.py::test_a")
        _red("t.py::test_b")
        _green("t.py::test_a")
        _red("t.py::test_c")
        assert gates.get_dangling_reds(FEATURE) == ["t.py::test_b", "t.py::test_c"]

    def test_unverified_red_not_dangling(self, hermetic):
        state.write_ledger({
            "kind": "tdd", "session": "s", "state": "red",
            "test_node": "t.py::test_x", "verified": False, "feature": FEATURE,
        })
        assert gates.get_dangling_reds(FEATURE) == []


class TestCmdSync:
    def test_three_stranded_now_passing_close_in_one_call(self, hermetic, monkeypatch):
        nodes = ["t.py::test_one", "t.py::test_two", "t.py::test_three"]
        for n in nodes:
            _red(n)
        monkeypatch.setattr(cli, "run_test", lambda node, timeout=30: (0, "", ""))
        args = SimpleNamespace(feature=FEATURE, session="s")
        res = cli.cmd_sync(args)
        assert res["ok"] is True
        assert sorted(res["closed"]) == sorted(nodes)
        assert res["still_failing"] == []
        # cycles now closed — no dangling left
        assert gates.get_dangling_reds(FEATURE) == []

    def test_still_failing_writes_nothing(self, hermetic, monkeypatch):
        _red("t.py::test_bad")
        monkeypatch.setattr(cli, "run_test", lambda node, timeout=30: (1, "", "fail"))
        before = list(state.read_ledger())
        args = SimpleNamespace(feature=FEATURE, session="s")
        res = cli.cmd_sync(args)
        assert res["ok"] is False
        assert res["closed"] == []
        assert res["still_failing"] == ["t.py::test_bad"]
        after = list(state.read_ledger())
        assert len(after) == len(before), "failing node must write NOTHING"
        assert gates.get_dangling_reds(FEATURE) == ["t.py::test_bad"]

    def test_mixed_close_and_failing(self, hermetic, monkeypatch):
        _red("t.py::test_ok")
        _red("t.py::test_bad")
        def fake_run(node, timeout=30):
            return (0, "", "") if node.endswith("ok") else (1, "", "fail")
        monkeypatch.setattr(cli, "run_test", fake_run)
        args = SimpleNamespace(feature=FEATURE, session="s")
        res = cli.cmd_sync(args)
        assert res["ok"] is False
        assert res["closed"] == ["t.py::test_ok"]
        assert res["still_failing"] == ["t.py::test_bad"]

    def test_no_stranded_ok(self, hermetic):
        args = SimpleNamespace(feature=FEATURE, session="s")
        res = cli.cmd_sync(args)
        assert res["ok"] is True
        assert res["closed"] == []
