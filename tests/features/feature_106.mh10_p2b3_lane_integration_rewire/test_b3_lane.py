"""Slice-B3 lane goldens — feature_106.mh10_p2b3_lane_integration_rewire.

Evidence-carrying lane path: submit/verify/integrate_* go through
_fire_lane_move with transition/fired/fire_fallback ledger keys. On today's
pool template (no lane places/transitions) every lane edge takes a labeled
fallback (not_lane_net) while binding + slot behavior stays exactly legacy.

Hermetic via OMT_NET_DIR / OMT_LEDGER_PATH / OMT_COORDINATION_ROOT.
Canary: new goldens for feature_106 only (scope: tests).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "scripts" / "omt"
sys.path.insert(0, str(SCRIPTS_DIR))


def _state():
    from net import state  # noqa: PLC0415  (lazy — runnable RED)

    return state


def _managed():
    from net import managed_ops  # noqa: PLC0415

    return managed_ops


def _pool_bundle(base: Path, state, tasks=("T1", "T2")) -> None:
    """Pre-B3 pool net: no lane places, no lane transitions (today's shape)."""
    state.init_empty(base)
    st = state.load(base)
    for place, tokens in (
        ("work_pending", len(tasks)),
        ("work_active", 0),
        ("work_done", 0),
        ("agent_attention", 1),
        ("feature_ready", 1),
    ):
        st.net.add_place(place, tokens=tokens)
    st.net.add_transition("work_start")
    st.net.add_transition("work_complete")
    st.net.add_input("agent_attention", "work_start")
    st.net.add_input("feature_ready", "work_start")
    st.net.add_input("work_pending", "work_start")
    st.net.add_output("work_start", "feature_ready")
    st.net.add_output("work_start", "work_active")
    st.net.add_input("work_active", "work_complete")
    st.net.add_output("work_complete", "agent_attention")
    st.net.add_output("work_complete", "work_done")
    st.live_marking = {
        "work_pending": len(tasks),
        "work_active": 0,
        "work_done": 0,
        "agent_attention": 1,
        "feature_ready": 1,
    }
    st.task_bindings = [
        {"id": tid, "place": "work_pending", "generation": 0, "scope": [f"src/{tid.lower()}"]}
        for tid in tasks
    ]
    state.save(base, st)


@pytest.fixture()
def bundle(tmp_path, monkeypatch):
    state = _state()
    monkeypatch.setenv("OMT_NET_DIR", str(tmp_path))
    monkeypatch.setenv("OMT_LEDGER_PATH", str(tmp_path / "ledger.jsonl"))
    monkeypatch.setenv("OMT_COORDINATION_ROOT", str(tmp_path / "coord"))
    _pool_bundle(tmp_path, state)
    return tmp_path


def _ledger_rows(bundle):
    ledger = Path(str(bundle)) / "ledger.jsonl"
    if not ledger.exists():
        return []
    return [
        json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()
    ]


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


class TestLaneEvidence:
    def test_submit_labels_not_lane_net(self, bundle) -> None:
        state = _state()
        b = _claim(state, bundle, "T1", "alice")
        st = state.submit_result(
            bundle, "T1", generation=b["generation"], owner="alice",
            result=dict(RESULT), session="s",
        )
        sub = next(x for x in st.task_bindings if x["id"] == "T1")
        assert sub["place"] == "work_verifying"
        # worker freed (binding count), submission immutable ref kept
        assert state._active_task_count(st) == 0
        assert sub["submission"]["head_commit"] == "def456"
        rows = _ledger_kind(_ledger_rows(bundle), "net_submit")
        assert len(rows) == 1
        assert rows[0]["transition"] == "work_submit"
        assert rows[0]["fired"] is False
        assert rows[0]["fire_fallback"] == "not_lane_net"

    def test_verify_pass_labels_not_lane_net(self, bundle) -> None:
        state = _state()
        b = _claim(state, bundle, "T1", "alice")
        state.submit_result(
            bundle, "T1", generation=b["generation"], owner="alice",
            result=dict(RESULT), session="s",
        )
        st = state.verify_result(
            bundle, "T1", generation=b["generation"],
            verdict="pass", coordinator=True, session="c",
        )
        sub = next(x for x in st.task_bindings if x["id"] == "T1")
        assert sub["place"] == "work_integration_ready"
        rows = _ledger_kind(_ledger_rows(bundle), "net_verify_pass")
        assert len(rows) == 1
        assert rows[0]["transition"] == "work_verify_pass"
        assert rows[0]["fired"] is False
        assert rows[0]["fire_fallback"] == "not_lane_net"

    def test_verify_fail_returns_pending_labeled(self, bundle) -> None:
        state = _state()
        b = _claim(state, bundle, "T1", "alice")
        state.submit_result(
            bundle, "T1", generation=b["generation"], owner="alice",
            result=dict(RESULT), session="s",
        )
        st = state.verify_result(
            bundle, "T1", generation=b["generation"],
            verdict="fail", coordinator=True, detail="red", session="c",
        )
        sub = next(x for x in st.task_bindings if x["id"] == "T1")
        assert sub["place"] == "work_pending"
        assert "verify_fail" in str(sub.get("block_reason", ""))
        rows = _ledger_kind(_ledger_rows(bundle), "net_verify_fail")
        assert rows[0]["transition"] == "work_verify_fail"
        assert rows[0]["fired"] is False
        assert rows[0]["fire_fallback"] == "not_lane_net"

    def test_integrate_start_labels_not_lane_net(self, bundle) -> None:
        state = _state()
        b = _claim(state, bundle, "T1", "alice")
        state.submit_result(
            bundle, "T1", generation=b["generation"], owner="alice",
            result=dict(RESULT), session="s",
        )
        state.verify_result(
            bundle, "T1", generation=b["generation"],
            verdict="pass", coordinator=True, session="c",
        )
        st = state.integrate_start(
            bundle, "T1", generation=b["generation"],
            coordinator=True, session="c",
        )
        sub = next(x for x in st.task_bindings if x["id"] == "T1")
        assert sub["place"] == "work_integrating"
        rows = _ledger_kind(_ledger_rows(bundle), "net_integrate_start")
        assert rows[0]["transition"] == "work_integrate_start"
        assert rows[0]["fired"] is False
        assert rows[0]["fire_fallback"] == "not_lane_net"

    def test_integrate_pass_labels_not_lane_net(self, bundle) -> None:
        state = _state()
        b = _claim(state, bundle, "T1", "alice")
        state.submit_result(
            bundle, "T1", generation=b["generation"], owner="alice",
            result=dict(RESULT), session="s",
        )
        state.verify_result(
            bundle, "T1", generation=b["generation"],
            verdict="pass", coordinator=True, session="c",
        )
        state.integrate_start(
            bundle, "T1", generation=b["generation"],
            coordinator=True, session="c",
        )
        st = state.integrate_finish(
            bundle, "T1", generation=b["generation"],
            verdict="pass", coordinator=True, session="c",
        )
        sub = next(x for x in st.task_bindings if x["id"] == "T1")
        assert sub["place"] == "work_done"
        rows = _ledger_kind(_ledger_rows(bundle), "net_integrate_pass")
        assert rows[0]["transition"] == "work_integrate_pass"
        assert rows[0]["fired"] is False
        assert rows[0]["fire_fallback"] == "not_lane_net"

    def test_integrate_fail_returns_pending_labeled(self, bundle) -> None:
        state = _state()
        b = _claim(state, bundle, "T1", "alice")
        state.submit_result(
            bundle, "T1", generation=b["generation"], owner="alice",
            result=dict(RESULT), session="s",
        )
        state.verify_result(
            bundle, "T1", generation=b["generation"],
            verdict="pass", coordinator=True, session="c",
        )
        state.integrate_start(
            bundle, "T1", generation=b["generation"],
            coordinator=True, session="c",
        )
        st = state.integrate_finish(
            bundle, "T1", generation=b["generation"],
            verdict="fail", coordinator=True, detail="conflict", session="c",
        )
        sub = next(x for x in st.task_bindings if x["id"] == "T1")
        assert sub["place"] == "work_pending"
        assert "integration_conflict" in str(sub.get("block_reason", ""))
        assert st.live_marking.get("work_done", 0) == 0
        rows = _ledger_kind(_ledger_rows(bundle), "net_integrate_fail")
        assert rows[0]["transition"] == "work_integrate_fail"
        assert rows[0]["fired"] is False
        assert rows[0]["fire_fallback"] == "not_lane_net"


class TestHelperAndReader:
    def test_fire_lane_move_no_transition_when_places_present(self, tmp_path, monkeypatch) -> None:
        state = _state()
        monkeypatch.setenv("OMT_NET_DIR", str(tmp_path))
        monkeypatch.setenv("OMT_LEDGER_PATH", str(tmp_path / "ledger.jsonl"))
        monkeypatch.setenv("OMT_COORDINATION_ROOT", str(tmp_path / "coord"))
        _pool_bundle(tmp_path, state, tasks=("T1",))
        st = state.load(tmp_path)
        # Lane places present in marking but no lane transition in template:
        # deterministic no_transition fallback with legacy (no-op) move.
        st.net.add_place("work_verifying", 0)
        st.live_marking["work_verifying"] = 0
        st.live_marking["work_active"] = 1
        state.save(tmp_path, st)
        st = state.load(tmp_path)
        fired, reason = state._fire_lane_move(st, "work_submit", "work_active", "work_verifying")
        assert (fired, reason) == (False, "no_transition")

    def test_reader_covers_lane_kinds(self, bundle) -> None:
        state = _state()
        mo = _managed()
        b = _claim(state, bundle, "T1", "alice")
        state.submit_result(
            bundle, "T1", generation=b["generation"], owner="alice",
            result=dict(RESULT), session="s",
        )
        state.verify_result(
            bundle, "T1", generation=b["generation"],
            verdict="pass", coordinator=True, session="c",
        )
        state.integrate_start(
            bundle, "T1", generation=b["generation"],
            coordinator=True, session="c",
        )
        state.integrate_finish(
            bundle, "T1", generation=b["generation"],
            verdict="pass", coordinator=True, session="c",
        )
        res = mo.check_ledger_evidence(_ledger_rows(bundle))
        assert res["ok"] is True
        assert res["offenders"] == []
        # 1 claim (slice-B shape) + 4 lane rows, all fallback-labeled on pool net
        assert res["fired"] + sum(res["fallback"].values()) >= 5
        assert res["fallback"].get("not_lane_net", 0) == 4

    def test_reader_flags_lane_row_missing_keys(self) -> None:
        mo = _managed()
        res = mo.check_ledger_evidence(
            [
                {"kind": "net_submit", "transition": "work_submit"},
                {"kind": "net_verify_pass", "transition": "work_verify_pass",
                 "fired": False, "fire_fallback": "not_lane_net"},
                {"kind": "net_sync"},
            ]
        )
        assert res["ok"] is False
        assert res["offenders"] == [0]
        assert res["fallback"] == {"not_lane_net": 1}
