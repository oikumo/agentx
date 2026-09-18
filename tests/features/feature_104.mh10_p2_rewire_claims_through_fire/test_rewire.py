"""Slice-B rewire goldens — feature_104.mh10_p2_rewire_claims_through_fire.

claim_task/release_task route pool moves through _fire_pool_move:
template fire preferred, labeled fallback otherwise. Behavior preserved
(counts, guards, stable codes); ledger carries transition/fired evidence.

Hermetic via OMT_NET_DIR / OMT_LEDGER_PATH / OMT_COORDINATION_ROOT.
Canary: new goldens for feature_104 only (scope: tests).
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


def _pool_bundle(base: Path, state, tasks=("T1", "T2")) -> None:
    """Pool net with work_start/work_complete arcs + pending bindings."""
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
        {"id": tid, "place": "work_pending", "generation": 0} for tid in tasks
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


class TestFirePreferred:
    def test_first_claim_fires_work_start(self, bundle) -> None:
        state = _state()
        st = state.claim_task(bundle, "T1", owner="u1", session="s")
        assert (st.live_marking["work_pending"], st.live_marking["work_active"]) == (1, 1)
        # No resource leak: attention/feature_ready refunded to code management.
        assert st.live_marking["agent_attention"] == 1
        assert st.live_marking["feature_ready"] == 1
        claims = [r for r in _ledger_rows(bundle) if r.get("kind") == "net_claim"]
        assert len(claims) == 1
        assert claims[0]["transition"] == "work_start"
        assert claims[0]["fired"] is True
        assert claims[0]["fire_fallback"] is None

    def test_second_claim_falls_back_labeled_attention_held(self, bundle) -> None:
        state = _state()
        # Occupy agent_attention so work_start is not enabled; code guards pass.
        st = state.load(bundle)
        st.live_marking["agent_attention"] = 0
        state.save(bundle, st)
        st = state.claim_task(bundle, "T1", owner="u1", session="s")
        # Legacy acceptance preserved (2-worker model unaffected by attention).
        assert (st.live_marking["work_pending"], st.live_marking["work_active"]) == (1, 1)
        claims = [r for r in _ledger_rows(bundle) if r.get("kind") == "net_claim"]
        assert claims[0]["fired"] is False
        assert claims[0]["fire_fallback"] == "transition_not_enabled"


class TestReleaseFallbackLabeled:
    def test_release_names_missing_back_edge(self, bundle) -> None:
        state = _state()
        state.claim_task(bundle, "T1", owner="u1", session="s")
        st = state.release_task(bundle, "T1", session="s")
        assert (st.live_marking["work_pending"], st.live_marking["work_active"]) == (2, 0)
        releases = [r for r in _ledger_rows(bundle) if r.get("kind") == "net_release"]
        assert len(releases) == 1
        assert releases[0]["transition"] == "work_release"
        assert releases[0]["fired"] is False
        assert releases[0]["fire_fallback"] == "no_transition"


class TestStableBehaviorPreserved:
    def test_double_claim_still_refuses_task_not_pending(self, bundle) -> None:
        state = _state()
        state.claim_task(bundle, "T1", owner="u1", session="s")
        with pytest.raises(state.SpliceError) as exc:
            state.claim_task(bundle, "T1", owner="u2", session="s")
        assert exc.value.code == "task_not_pending"

    def test_unknown_task_still_refuses_task_not_found(self, bundle) -> None:
        state = _state()
        with pytest.raises(state.SpliceError) as exc:
            state.claim_task(bundle, "NOPE", owner="u1", session="s")
        assert exc.value.code == "task_not_found"


class TestFallbackBranches:
    def test_skeleton_bundle_reports_not_pool_net(self, tmp_path) -> None:
        state = _state()
        state.init_empty(tmp_path)
        st = state.load(tmp_path)
        fired, reason = state._fire_pool_move(
            st, "work_start", "work_pending", "work_active"
        )
        assert (fired, reason) == (False, "not_pool_net")

    def test_shape_mismatch_falls_back_with_legacy_move(self, bundle) -> None:
        state = _state()
        st = state.load(bundle)
        # Extra output arc: work_start now also mints work_done, so the
        # successor no longer expresses exactly pending→active.
        st.net.add_output("work_start", "work_done")
        state.save(bundle, st)
        st = state.load(bundle)
        fired, reason = state._fire_pool_move(
            st, "work_start", "work_pending", "work_active"
        )
        assert (fired, reason) == (False, "transition_shape_mismatch")
        assert (st.live_marking["work_pending"], st.live_marking["work_active"]) == (1, 1)
        assert st.live_marking["work_done"] == 0
        assert st.live_marking["agent_attention"] == 1
