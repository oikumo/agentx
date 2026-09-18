"""P2 slice-A managed-op map — feature_103.mh10_p2_global_gate (canary).

Read-only: pure classify/check_counts/check_fixture + live agree-shape.
No live-surface mutation; no src/agentx import.
"""
from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "scripts" / "omt"
sys.path.insert(0, str(SCRIPTS_DIR))

REPO_ROOT = Path(__file__).resolve().parents[3]


def _load():
    from net import managed_ops  # noqa: PLC0415

    return managed_ops


class TestManagedOpMap:
    def test_table_covers_all_managed_ops(self) -> None:
        mo = _load()
        ops = [r["op"] for r in mo.MANAGED_OPS]
        for expected in (
            "fire",
            "claim_task",
            "release_task",
            "submit_result",
            "verify_pass",
            "verify_fail",
            "integrate_start",
            "integrate_pass",
            "integrate_fail",
            "absent_lane_occupancy",
            "project_sync",
            "session_menu",
            "crash_window",
        ):
            assert expected in ops, f"managed op {expected!r} missing from map"
        # fire() fires; B2 lands literal claim/release firing on the happy path
        # (labeled fallback where the template cannot express the move).
        fired = [r["op"] for r in mo.MANAGED_OPS if r["fired_today"] == "yes"]
        assert fired == ["fire"]
        happy = [r["op"] for r in mo.MANAGED_OPS if r["fired_today"] == "yes-B2-happy-path"]
        assert happy == ["claim_task", "release_task"]
        # B3 wires lane edges through fire with labeled fallback (no template
        # landing yet — B3b needs a cap-safe migration).
        lane = [r["op"] for r in mo.MANAGED_OPS if r["fired_today"] == "no-B3-fallback"]
        assert lane == [
            "submit_result",
            "verify_pass",
            "verify_fail",
            "integrate_start",
            "integrate_pass",
            "integrate_fail",
        ]

    def test_agree_without_firing_is_omission(self) -> None:
        mo = _load()
        assert mo.classify(0, 0, False) == "OMISSION"
        assert mo.classify(7, 7, False) == "OMISSION"
        assert mo.classify(0, 0, True) == "FIRED"
        assert mo.classify(0, 1, False) == "DIVERGENCE"

    def test_live_shape_agrees_as_omissions(self) -> None:
        mo = _load()
        rows = mo.check_counts(
            {"pending": 0, "active": 0, "done": 7},
            {"work_pending": 0, "work_active": 0, "work_done": 7},
        )
        assert [r["class"] for r in rows] == ["OMISSION"] * 3

    def test_seeded_omissions_detected(self) -> None:
        mo = _load()
        # Claim path moves counts with no fired transition → must read OMISSION.
        res = mo.check_fixture(
            {
                "pool": {"pending": 0, "active": 1, "done": 7},
                "marking": {"work_pending": 0, "work_active": 1, "work_done": 7},
                "claimed_firing": True,
                "fired": False,
            }
        )
        assert res["missed"] == []
        assert "claimed_firing_as_omission" in res["detected"]
        # Disagreement must surface as DIVERGENCE, never silent agreement.
        res2 = mo.check_fixture(
            {
                "pool": {"pending": 1, "active": 0, "done": 7},
                "marking": {"work_pending": 0, "work_active": 0, "work_done": 7},
            }
        )
        by_key = {r["key"]: r["class"] for r in res2["rows"]}
        assert by_key["pending"] == "DIVERGENCE"

    def test_live_bundle_agrees(self) -> None:
        mo = _load()
        base = REPO_ROOT / ".meta" / ".omt"
        if not base.exists():
            import pytest

            pytest.skip("no live net bundle in this checkout")
        res = mo.check_live(base)
        if "_unknown" in res:
            import pytest

            pytest.skip(res["_unknown"])
        assert [r["class"] for r in res["rows"]] == ["OMISSION"] * 3
