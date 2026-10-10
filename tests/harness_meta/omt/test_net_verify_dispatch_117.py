"""117 verify dispatch exploitation goldens — feature_117.

Pure composer (verify_dispatch: split/claims/join) + one O4
end-to-end (compose → plan_dispatch → plan_to_dict). Hermetic:
no OMT_NET_DIR / ledger / live-net access; stdlib + planner only.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "scripts" / "omt"
sys.path.insert(0, str(SCRIPTS_DIR))


def _vd():
    from net import verify_dispatch  # noqa: PLC0415
    return verify_dispatch


def _dr():
    from net import dispatch_runtime  # noqa: PLC0415
    return dispatch_runtime


class TestSplit:
    def test_split_deterministic(self) -> None:
        vd = _vd()
        nodes = ["t3", "t1", "t2", "t1"]
        assert vd.compose_verify_batches(nodes) == vd.compose_verify_batches(nodes)

    def test_split_disjoint_cover(self) -> None:
        vd = _vd()
        nodes = ["b", "a", "c", "d"]
        a, b = vd.compose_verify_batches(nodes)
        assert set(a) & set(b) == set()
        assert sorted([*a, *b]) == sorted(set(nodes))

    def test_split_even_odd(self) -> None:
        vd = _vd()
        a, b = vd.compose_verify_batches(["d", "c", "b", "a"])
        # sorted [a,b,c,d] → even idx a,c → A; odd idx b,d → B
        assert a == ["a", "c"]
        assert b == ["b", "d"]

    def test_empty_refuses(self) -> None:
        vd = _vd()
        with pytest.raises(ValueError, match="empty_plan"):
            vd.compose_verify_batches([])


class TestClaims:
    def test_claims_lane_map(self) -> None:
        vd = _vd()
        claims, caps = vd.compose_verify_claims(["x"], ["y"], 60)
        assert claims == [
            {"claim": "c-verify-a", "task_id": "verify-a", "lane": "verification"},
            {"claim": "c-verify-b", "task_id": "verify-b", "lane": "integration"},
        ]
        assert caps["worker_slots"] == {"used": 0, "cap": 2, "free": 2}

    def test_plan_dispatch_accepts(self) -> None:
        vd, dr = _vd(), _dr()
        a, b = vd.compose_verify_batches(["n2", "n1", "n3", "n4"])
        claims, caps = vd.compose_verify_claims(a, b, 60)
        plan = dr.plan_dispatch(
            claims=claims, enabled=[], parallel=[],
            worker_slots=dict(caps["worker_slots"]),
            verification=dict(caps["verification"]),
            integration=dict(caps["integration"]),
            work_pending=0, work_active=0, revision=60,
        )
        assert [t.task_id for t in plan.tasks] == ["verify-a", "verify-b"]
        d = dr.plan_to_dict(plan)
        assert d["revision"] == 60 and len(d["tasks"]) == 2


class TestJoin:
    def test_join_wall_saving(self) -> None:
        vd = _vd()
        # Model: serial = sum, dispatch = max. d2 banked 51% (21.752s →
        # 10.667s wall) is the live reference; here pin model semantics
        # with a ~50% pair: walls 11.0 + 10.667 → serial 21.667,
        # dispatch 11.0, saving ≈ 0.492.
        rep = vd.join_verify_reports(
            {"wall": 11.0, "tokens": 7483, "success": True},
            {"wall": 10.667, "tokens": 19553, "success": True},
        )
        assert rep["serial_wall"] == pytest.approx(21.667)
        assert rep["dispatch_wall"] == pytest.approx(11.0)
        assert rep["wall_saving"] == pytest.approx(1 - 11.0 / 21.667, abs=0.01)
        assert rep["tokens_saving"] == 0.0

    def test_join_success_and(self) -> None:
        vd = _vd()
        assert vd.join_verify_reports(
            {"wall": 1.0, "tokens": 1, "success": True},
            {"wall": 2.0, "tokens": 2, "success": False},
        )["success"] is False
        zero = vd.join_verify_reports(
            {"wall": 0.0, "tokens": 0, "success": True},
            {"wall": 0.0, "tokens": 0, "success": True},
        )
        assert zero["wall_saving"] == 0.0 and zero["success"] is True
