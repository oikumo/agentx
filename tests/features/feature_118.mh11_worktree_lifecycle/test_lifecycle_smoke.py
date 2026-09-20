"""Feature-118 pointer smoke - exercises the public surface.

Canonical goldens live at tests/scripts/omt/test_net_worktree_lifecycle_b.py
(11/11, O4 precedent); this file keeps the coverage gate fed from the
feature-owned dir: every public worktree_lifecycle method is called here.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "scripts" / "omt"
sys.path.insert(0, str(SCRIPTS_DIR))


def _lifecycle():
    from net import worktree_lifecycle  # noqa: PLC0415
    return worktree_lifecycle


def test_resolve_both_lanes() -> None:
    lc = _lifecycle()
    b = lc.resolve_lane(task_id="T1", generation=1)
    assert b["branch"] == "feat/T1-g1"
    m = lc.resolve_lane(task_id="T1", generation=1, lane="managed")
    assert m["branch"] == "omt/T1/g1"


def test_compose_gate_and_status_closed() -> None:
    lc = _lifecycle()
    got = lc.compose_join(tasks=[
        {"task_id": "T1", "path": ".sandbox/bench/T1-g0",
         "branch": "feat/T1-g0", "head": "h"},
    ])
    assert got["commands"][0] == "git merge --no-ff feat/T1-g0"
    ok = {"clean": True, "branch_exists": True,
          "commits_since_claim": 1, "head": "h"}
    assert lc.gate_complete(status=ok, verify_ok=True,
                            expected_revision=60,
                            live_revision=60) is None
    with pytest.raises(lc.LifecycleRefused):
        lc.gate_complete(status=ok, verify_ok=False,
                         expected_revision=60, live_revision=60)
    closed = lc.status_checks(path="/nonexistent-ws", branch="b",
                              base_commit="unknown")
    assert closed["clean"] is False
