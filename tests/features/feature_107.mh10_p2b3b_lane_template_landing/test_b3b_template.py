"""Slice-B3b lane-template goldens — feature_107.mh10_p2b3b_lane_template_landing.

Cap-safe landing: retire e2e_receipt (reroute to archive_pool) + reuse
tests_capacity/src_edit_capacity as the lane slots + add the 3 lane states +
6 lane transitions (19 arcs) = 15/15 places. Every lane edge becomes a checked
template firing with slot accounting; legacy bundles keep labeled fallbacks.

Hermetic via OMT_NET_DIR / OMT_LEDGER_PATH / OMT_COORDINATION_ROOT.
Canary: new goldens for feature_107 only (scope: tests).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "scripts" / "omt"
sys.path.insert(0, str(SCRIPTS_DIR))

FEATURE = "feature_107.mh10_p2b3b_lane_template_landing"

LIVE_PLACES = (
    ("work_pending", 2),
    ("work_active", 0),
    ("work_done", 0),
    ("worker_slots", 2),
    ("agent_attention", 1),
    ("feature_ready", 1),
    ("goal_satisfied", 0),
    ("resource_token", 1),
    ("archive_pool", 0),
    ("src_edit_capacity", 1),
    ("tests_capacity", 1),
    ("harness_surface_round", 1),
    ("e2e_receipt", 1),
)

LIVE_ARCS_IN = (
    ("agent_attention", "work_start"),
    ("feature_ready", "work_start"),
    ("work_pending", "work_start"),
    ("worker_slots", "work_start"),
    ("work_active", "work_complete"),
    ("work_active", "work_release"),
)
LIVE_ARCS_OUT = (
    ("work_start", "feature_ready"),
    ("work_start", "work_active"),
    ("work_complete", "agent_attention"),
    ("work_complete", "goal_satisfied"),
    ("work_complete", "work_done"),
    ("work_complete", "worker_slots"),
    ("work_release", "work_pending"),
    ("work_release", "worker_slots"),
)


def _state():
    from net import state  # noqa: PLC0415  (lazy — runnable RED)

    return state


def _managed():
    from net import managed_ops  # noqa: PLC0415

    return managed_ops


def _live_bundle(base: Path, state, tasks=("T1", "T2")) -> None:
    """Live-shaped rev-58 pool net: 13 places, 3 transitions (pre-B3b)."""
    state.init_empty(base)
    st = state.load(base)
    for place, tokens in LIVE_PLACES:
        st.net.add_place(place, tokens=tokens)
    st.net.add_transition("work_start")
    st.net.add_transition("work_release")
    st.net.add_transition("work_complete")
    for src, dst in LIVE_ARCS_IN:
        st.net.add_input(src, dst)
    for src, dst in LIVE_ARCS_OUT:
        st.net.add_output(src, dst)
    st.live_marking = {place: tokens for place, tokens in LIVE_PLACES}
    st.live_marking["work_pending"] = len(tasks)
    st.task_bindings = [
        {"id": tid, "place": "work_pending", "generation": 0, "scope": [f"src/{tid.lower()}"]}
        for tid in tasks
    ]
    state.save(base, st)


def _legacy_slot_bundle(base: Path, state) -> None:
    """Old slot names (test_slots/integration_slot) instead of capacities."""
    state.init_empty(base)
    st = state.load(base)
    renamed = [
        ("test_slots" if p == "tests_capacity" else "integration_slot" if p == "src_edit_capacity" else p, t)
        for p, t in LIVE_PLACES
    ]
    for place, tokens in renamed:
        st.net.add_place(place, tokens=tokens)
    st.net.add_transition("work_start")
    st.net.add_transition("work_complete")
    st.net.add_input("work_pending", "work_start")
    st.net.add_output("work_start", "work_active")
    st.net.add_input("work_active", "work_complete")
    st.net.add_output("work_complete", "work_done")
    st.live_marking = dict(renamed)
    st.live_marking["work_pending"] = 1
    st.task_bindings = [
        {"id": "T1", "place": "work_pending", "generation": 0, "scope": ["src/t1"]}
    ]
    state.save(base, st)


@pytest.fixture()
def bundle(tmp_path, monkeypatch):
    monkeypatch.setenv("OMT_NET_DIR", str(tmp_path))
    monkeypatch.setenv("OMT_LEDGER_PATH", str(tmp_path / "ledger.jsonl"))
    monkeypatch.setenv("OMT_COORDINATION_ROOT", str(tmp_path / "coord"))
    _live_bundle(tmp_path, _state())
    return tmp_path


@pytest.fixture()
def migrated(tmp_path, monkeypatch):
    state = _state()
    monkeypatch.setenv("OMT_NET_DIR", str(tmp_path))
    monkeypatch.setenv("OMT_LEDGER_PATH", str(tmp_path / "ledger.jsonl"))
    monkeypatch.setenv("OMT_COORDINATION_ROOT", str(tmp_path / "coord"))
    _live_bundle(tmp_path, state)
    state.ensure_pool_b3b(tmp_path, reasoning="test", session="t", feature=FEATURE)
    return tmp_path


def _ledger_rows(bundle):
    ledger = Path(str(bundle)) / "ledger.jsonl"
    if not ledger.exists():
        return []
    return [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()]


def _ledger_kind(rows, kind):
    return [r for r in rows if r.get("kind") == kind]


RESULT = {
    "head_commit": "def456",
    "patch_digest": "sha256:abc",
    "base_commit": "abc123",
    "local_checks": [{"name": "pytest focused", "result": "pass"}],
}


def _claim(state, base, tid="T1", owner="alice"):
    st = state.claim_task(base, tid, owner=owner, session="s")
    return next(b for b in st.task_bindings if b["id"] == tid)


def _walk_to_done(state, base, tid, owner, gen):
    state.submit_result(
        base, tid, generation=gen, owner=owner, result=dict(RESULT), session="s"
    )
    state.verify_result(
        base, tid, generation=gen, verdict="pass", coordinator=True, session="c"
    )
    state.integrate_start(base, tid, generation=gen, coordinator=True, session="c")
    return state.integrate_finish(
        base, tid, generation=gen, verdict="pass", coordinator=True, session="c"
    )


class TestB3bMigration:
    def test_retire_and_land_within_cap(self, bundle) -> None:
        state = _state()
        before = state.load(bundle)
        assert len(before.net.places) == 13
        st, info = state.ensure_pool_b3b(
            bundle, reasoning="test", session="t", feature=FEATURE
        )
        assert info["migrated"] is True
        assert len(st.net.places) == 15
        assert "e2e_receipt" not in st.net.places
        for place in ("work_verifying", "work_integration_ready", "work_integrating"):
            assert place in st.net.places
            assert st.live_marking[place] == 0
        for transition in state.LANE_TRANSITIONS:
            assert transition in st.net.transitions
        # retired token rerouted to the archive holder (history.py contract)
        assert st.live_marking["archive_pool"] == 1
        # reused capacities untouched by the migration itself
        assert st.live_marking["tests_capacity"] == 1
        assert st.live_marking["src_edit_capacity"] == 1
        assert st.live_marking["worker_slots"] == 2
        # 19 lane arcs land (inputs + outputs touching lane transitions)
        lane_arcs = sum(
            1
            for t in state.LANE_TRANSITIONS
            for _ in list(st.net.inputs.get(t, {})) + list(st.net.outputs.get(t, {}))
        )
        assert lane_arcs == 19

    def test_rerun_is_noop(self, migrated) -> None:
        state = _state()
        before = state.load(migrated)
        st, info = state.ensure_pool_b3b(
            migrated, reasoning="test", session="t", feature=FEATURE
        )
        assert info["migrated"] is False
        assert st.revision == before.revision
        assert len(st.net.places) == 15


class TestB3bFiredLane:
    def test_full_walk_fires_all_six_with_slot_accounting(self, migrated) -> None:
        state = _state()
        b = _claim(state, migrated, "T1", "alice")
        st = state.submit_result(
            migrated, "T1", generation=b["generation"], owner="alice",
            result=dict(RESULT), session="s",
        )
        assert st.live_marking["work_verifying"] == 1
        assert st.live_marking["tests_capacity"] == 0
        assert st.live_marking["worker_slots"] == 2
        st = state.verify_result(
            migrated, "T1", generation=b["generation"],
            verdict="pass", coordinator=True, session="c",
        )
        assert st.live_marking["work_integration_ready"] == 1
        assert st.live_marking["tests_capacity"] == 1
        st = state.integrate_start(
            migrated, "T1", generation=b["generation"], coordinator=True, session="c"
        )
        assert st.live_marking["work_integrating"] == 1
        assert st.live_marking["src_edit_capacity"] == 0
        st = state.integrate_finish(
            migrated, "T1", generation=b["generation"],
            verdict="pass", coordinator=True, session="c",
        )
        done = next(x for x in st.task_bindings if x["id"] == "T1")
        assert done["place"] == "work_done"
        assert st.live_marking["work_done"] == 1
        assert st.live_marking["src_edit_capacity"] == 1
        rows = _ledger_rows(migrated)
        for kind, transition in (
            ("net_submit", "work_submit"),
            ("net_verify_pass", "work_verify_pass"),
            ("net_integrate_start", "work_integrate_start"),
            ("net_integrate_pass", "work_integrate_pass"),
        ):
            got = _ledger_kind(rows, kind)
            assert len(got) == 1
            assert got[0]["transition"] == transition
            assert got[0]["fired"] is True
            assert got[0]["fire_fallback"] is None

    def test_fail_back_edges_fire_and_free_slots(self, migrated) -> None:
        state = _state()
        b = _claim(state, migrated, "T1", "alice")
        state.submit_result(
            migrated, "T1", generation=b["generation"], owner="alice",
            result=dict(RESULT), session="s",
        )
        st = state.verify_result(
            migrated, "T1", generation=b["generation"],
            verdict="fail", coordinator=True, detail="red", session="c",
        )
        back = next(x for x in st.task_bindings if x["id"] == "T1")
        assert back["place"] == "work_pending"
        assert "verify_fail" in str(back.get("block_reason", ""))
        assert st.live_marking["tests_capacity"] == 1
        rows = _ledger_kind(_ledger_rows(migrated), "net_verify_fail")
        assert rows[0]["fired"] is True
        # re-claim bumps the generation; walk to integrating, then fail there
        b2 = _claim(state, migrated, "T1", "alice")
        assert b2["generation"] == b["generation"] + 1
        state.submit_result(
            migrated, "T1", generation=b2["generation"], owner="alice",
            result=dict(RESULT), session="s",
        )
        state.verify_result(
            migrated, "T1", generation=b2["generation"],
            verdict="pass", coordinator=True, session="c",
        )
        state.integrate_start(
            migrated, "T1", generation=b2["generation"], coordinator=True, session="c"
        )
        st = state.integrate_finish(
            migrated, "T1", generation=b2["generation"],
            verdict="fail", coordinator=True, detail="clash", session="c",
        )
        back2 = next(x for x in st.task_bindings if x["id"] == "T1")
        assert back2["place"] == "work_pending"
        assert "integration_conflict" in str(back2.get("block_reason", ""))
        assert st.live_marking["work_done"] == 0
        assert st.live_marking["src_edit_capacity"] == 1
        rows = _ledger_kind(_ledger_rows(migrated), "net_integrate_fail")
        assert rows[0]["transition"] == "work_integrate_fail"
        assert rows[0]["fired"] is True

    def test_two_workers_still_fire_concurrently(self, migrated) -> None:
        state = _state()
        _claim(state, migrated, "T1", "alice")
        st = state.claim_task(migrated, "T2", owner="bob", session="s")
        assert st.live_marking["worker_slots"] == 0
        rows = _ledger_kind(_ledger_rows(migrated), "net_claim")
        assert [r["fired"] for r in rows] == [True, True]
        st = state.release_task(migrated, "T1", owner="alice", session="s")
        assert st.live_marking["worker_slots"] == 1
        assert _ledger_kind(_ledger_rows(migrated), "net_release")[0]["fired"] is True

    def test_slot_exhaustion_refuses(self, migrated) -> None:
        state = _state()
        b1 = _claim(state, migrated, "T1", "alice")
        b2 = _claim(state, migrated, "T2", "bob")
        state.submit_result(
            migrated, "T1", generation=b1["generation"], owner="alice",
            result=dict(RESULT), session="s",
        )
        with pytest.raises(state.SpliceError):
            state.submit_result(
                migrated, "T2", generation=b2["generation"], owner="bob",
                result=dict(RESULT), session="s",
            )
        state.verify_result(
            migrated, "T1", generation=b1["generation"],
            verdict="pass", coordinator=True, session="c",
        )
        st = state.submit_result(
            migrated, "T2", generation=b2["generation"], owner="bob",
            result=dict(RESULT), session="s",
        )
        assert next(x for x in st.task_bindings if x["id"] == "T2")["place"] == "work_verifying"
        state.integrate_start(
            migrated, "T1", generation=b1["generation"], coordinator=True, session="c"
        )
        state.verify_result(
            migrated, "T2", generation=b2["generation"],
            verdict="pass", coordinator=True, session="c",
        )
        with pytest.raises(state.SpliceError):
            state.integrate_start(
                migrated, "T2", generation=b2["generation"], coordinator=True, session="c"
            )

    def test_attention_ready_goal_archive_untouched(self, migrated) -> None:
        state = _state()
        b = _claim(state, migrated, "T1", "alice")
        st = _walk_to_done(state, migrated, "T1", "alice", b["generation"])
        assert st.live_marking["agent_attention"] == 1
        assert st.live_marking["feature_ready"] == 1
        assert st.live_marking["goal_satisfied"] == 0
        assert st.live_marking["archive_pool"] == 1
        assert st.live_marking["harness_surface_round"] == 1
        assert st.live_marking["resource_token"] == 1

    def test_managed_ops_lane_rows_flip_to_template(self, migrated) -> None:
        state = _state()
        managed = _managed()
        rows = {r["transition"]: r for r in managed.MANAGED_OPS}
        for transition in state.LANE_TRANSITIONS:
            assert rows[transition]["fired_today"] == "yes-B3b-template"
        b = _claim(state, migrated, "T1", "alice")
        _walk_to_done(state, migrated, "T1", "alice", b["generation"])
        report = managed.check_ledger_evidence(_ledger_rows(migrated))
        assert report["ok"] is True
        assert report["offenders"] == []
        assert report["fired"] == 5  # claim + 4 lane edges of the pass walk
        assert report["fallback"] == {}


class TestB3bLegacyFallbacks:
    def test_legacy_bundle_keeps_labeled_fallbacks(self, bundle) -> None:
        state = _state()
        b = _claim(state, bundle, "T1", "alice")
        st = state.submit_result(
            bundle, "T1", generation=b["generation"], owner="alice",
            result=dict(RESULT), session="s",
        )
        sub = next(x for x in st.task_bindings if x["id"] == "T1")
        assert sub["place"] == "work_verifying"
        # reused capacity is code-managed on the legacy template
        assert st.live_marking["tests_capacity"] == 0
        assert st.live_marking["worker_slots"] == 2
        rows = _ledger_kind(_ledger_rows(bundle), "net_submit")
        assert rows[0]["fired"] is False
        assert rows[0]["fire_fallback"] == "not_lane_net"

    def test_old_slot_names_still_honored(self, tmp_path, monkeypatch) -> None:
        state = _state()
        monkeypatch.setenv("OMT_NET_DIR", str(tmp_path))
        monkeypatch.setenv("OMT_LEDGER_PATH", str(tmp_path / "ledger.jsonl"))
        monkeypatch.setenv("OMT_COORDINATION_ROOT", str(tmp_path / "coord"))
        _legacy_slot_bundle(tmp_path, state)
        b = _claim(state, tmp_path, "T1", "alice")
        st = state.submit_result(
            tmp_path, "T1", generation=b["generation"], owner="alice",
            result=dict(RESULT), session="s",
        )
        assert st.live_marking["test_slots"] == 0
        rows = _ledger_kind(_ledger_rows(tmp_path), "net_submit")
        assert rows[0]["fired"] is False
        assert rows[0]["fire_fallback"] == "not_lane_net"
        st = state.verify_result(
            tmp_path, "T1", generation=b["generation"],
            verdict="pass", coordinator=True, session="c",
        )
        assert st.live_marking["test_slots"] == 1
