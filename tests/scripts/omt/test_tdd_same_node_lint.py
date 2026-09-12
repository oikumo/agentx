#!/usr/bin/env python3
"""Golden tests for T2-2 same-node lint (feature_067, meta_harness_8).

Acceptance: green/refactor warns pre-toolchain when test_node != latest red node;
matched passes silent.

Hermetic: tmp ledger (state.LEDGER_PATH) + mocked cli.run_test — never touches
the real ledger. Targets use non-existent t.py nodes so no snapshot I/O.
"""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "omt"))

from tdd import cli, state  # noqa: E402

FEATURE = "feature_synth.tdd_same_node"


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


def _green_args(node: str):
    return SimpleNamespace(test_node=node, feature=FEATURE, session="s")


class TestSameNodeLint:
    def test_green_mismatched_warns(self, hermetic, monkeypatch):
        _red("t.py::test_a")
        monkeypatch.setattr(cli, "run_test", lambda node, timeout=30: (0, "", ""))
        res = cli.cmd_green(_green_args("t.py::test_b"))
        assert res["ok"] is True
        msg = res.get("message", "")
        assert "t.py::test_b" in msg and "t.py::test_a" in msg
        assert "SAME" in msg or "same" in msg.lower() or "mismatch" in msg.lower()

    def test_refactor_mismatched_warns(self, hermetic, monkeypatch):
        _red("t.py::test_a")
        monkeypatch.setattr(cli, "run_test", lambda node, timeout=30: (0, "", ""))
        args = SimpleNamespace(test_node="t.py::test_other", feature=FEATURE, session="s")
        res = cli.cmd_refactor(args)
        assert res["ok"] is True
        msg = res.get("message", "")
        assert "t.py::test_other" in msg and "t.py::test_a" in msg

    def test_matched_passes_silent(self, hermetic, monkeypatch):
        _red("t.py::test_a")
        monkeypatch.setattr(cli, "run_test", lambda node, timeout=30: (0, "", ""))
        res = cli.cmd_green(_green_args("t.py::test_a"))
        assert res["ok"] is True
        msg = res.get("message", "")
        assert "SAME" not in msg and "mismatch" not in msg.lower()
        assert "differs" not in msg.lower()

    def test_no_prior_red_silent(self, hermetic, monkeypatch):
        monkeypatch.setattr(cli, "run_test", lambda node, timeout=30: (0, "", ""))
        res = cli.cmd_green(_green_args("t.py::test_new"))
        assert res["ok"] is True
        msg = res.get("message", "")
        assert "SAME" not in msg and "mismatch" not in msg.lower()

    def test_warns_pre_toolchain_on_failure(self, hermetic, monkeypatch):
        _red("t.py::test_a")
        calls: list[str] = []

        def fake_run(node, timeout=30):
            calls.append(node)
            return (1, "", "fail")

        monkeypatch.setattr(cli, "run_test", fake_run)
        res = cli.cmd_green(_green_args("t.py::test_b"))
        assert res["ok"] is False
        msg = res.get("message", "")
        # warning present even though toolchain failed (pre-toolchain)
        assert "t.py::test_a" in msg
        assert calls == ["t.py::test_b"]
