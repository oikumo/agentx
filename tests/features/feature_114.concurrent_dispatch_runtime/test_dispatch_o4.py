"""Feature pointer tests for O4 concurrent dispatch runtime (feature_114).

Canonical goldens (23/23) live at tests/scripts/omt/test_net_dispatch_o4.py
(planner + preview + join, hermetic). This pointer satisfies the
Programming→Testing §12 unit-test path (tests/features/<feature>/...) with
a hermetic smoke over the same contract — no live net touch.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "scripts" / "omt"
sys.path.insert(0, str(SCRIPTS_DIR))


def _dispatch():
    from net import dispatch_runtime  # noqa: PLC0415
    return dispatch_runtime


def test_empty_plan_refuses() -> None:
    dr = _dispatch()
    with pytest.raises(dr.PlanRefused, match="empty_plan"):
        dr.plan_dispatch(
            claims=[], enabled=[], parallel=[],
            worker_slots={"used": 0, "cap": 2, "free": 2},
            verification={"used": 0, "cap": 1, "free": 1},
            integration={"used": 0, "cap": 1, "free": 1},
            work_pending=0, work_active=0, revision=60,
        )


def test_single_general_claim_composes() -> None:
    dr = _dispatch()
    plan = dr.plan_dispatch(
        claims=[{"claim": "c-1", "task_id": "t-1", "lane": "general"}],
        enabled=[], parallel=[],
        worker_slots={"used": 0, "cap": 2, "free": 2},
        verification={"used": 0, "cap": 1, "free": 1},
        integration={"used": 0, "cap": 1, "free": 1},
        work_pending=0, work_active=0, revision=60,
    )
    assert [t.task_id for t in plan.tasks] == ["t-1"]
    assert plan.revision == 60
