"""Slice-B2 template goldens — feature_105.mh10_p2b2_template_fix_work_release.

B2 bundle: worker_slots(2) + work_release back-edge on the pool template
(attention arcs KEPT — refunded by the helper, never serializing). Claims and
releases fire literally on the happy path, incl. 2-concurrent both fired;
old-shape bundles keep slice-B labeled fallbacks; ensure_pool_b2 migration is
idempotent; managed_ops.check_ledger_evidence reads the ledger shape.

Hermetic via OMT_NET_DIR / OMT_LEDGER_PATH / OMT_COORDINATION_ROOT.
Canary: new goldens for feature_105 only (scope: tests).
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


def _b2_bundle(base: Path, state, tasks=("T1", "T2", "T3")) -> None:
    """B2 pool net: slots + release edge + (kept) attention arcs."""
    state.init_empty(base)
    st = state.load(base)
    for place, tokens in (
        ("work_pending", len(tasks)),
        ("work_active", 0),
        ("work_done", 0),
        ("agent_attention", 1),
        ("feature_ready", 1),
        ("worker_slots", 2),
    ):
        st.net.add_place(place, tokens=tokens)
    for t in ("work_start", "work_complete", "work_release"):
        st.net.add_transition(t)
    st.net.add_input("agent_attention", "work_start")
    st.net.add_input("feature_ready", "work_start")
    st.net.add_input("work_pending", "work_start")
    st.net.add_input("worker_slots", "work_start")
    st.net.add_output("work_start", "feature_ready")
    st.net.add_output("work_start", "work_active")
    st.net.add_input("work_active", "work_complete")
    st.net.add_output("work_complete", "agent_attention")
    st.net.add_output("work_complete", "work_done")
    st.net.add_output("work_complete", "worker_slots")
    st.net.add_input("work_active", "work_release")
    st.net.add_output("work_release", "work_pending")
    st.net.add_output("work_release", "worker_slots")
    st.live_marking = {
        "work_pending": len(tasks),
        "work_active": 0,
        "work_done": 0,
        "agent_attention": 1,
        "feature_ready": 1,
        "worker_slots": 2,
    }
    st.task_bindings = [
        {"id": tid, "place": "work_pending", "generation": 0} for tid in tasks
    ]
    state.save(base, st)


def _old_bundle(base: Path, state, tasks=("T1", "T2")) -> None:
    """Pre-B2 pool net: attention arcs, no slots, no release (slice-B shape)."""
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
def b2(tmp_path, monkeypatch):
    state = _state()
    monkeypatch.setenv("OMT_NET_DIR", str(tmp_path))
    monkeypatch.setenv("OMT_LEDGER_PATH", str(tmp_path / "ledger.jsonl"))
    monkeypatch.setenv("OMT_COORDINATION_ROOT", str(tmp_path / "coord"))
    _b2_bundle(tmp_path, state)
    return tmp_path


@pytest.fixture()
def old(tmp_path, monkeypatch):
    state = _state()
    monkeypatch.setenv("OMT_NET_DIR", str(tmp_path))
    monkeypatch.setenv("OMT_LEDGER_PATH", str(tmp_path / "ledger.jsonl"))
    monkeypatch.setenv("OMT_COORDINATION_ROOT", str(tmp_path / "coord"))
    _old_bundle(tmp_path, state)
    return tmp_path


def _ledger_rows(bundle):
    ledger = Path(str(bundle)) / "ledger.jsonl"
    if not ledger.exists():
        return []
    return [
        json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()
    ]


class TestB2HappyPath:
    def test_claim_fires_with_slot_adopted(self, b2) -> None:
        state = _state()
        st = state.claim_task(b2, "T1", owner="u1", session="s")
        assert (st.live_marking["work_pending"], st.live_marking["work_active"]) == (2, 1)
        assert st.live_marking["worker_slots"] == 1
        # Attention refunded — never leaks, never serializes.
        assert st.live_marking["agent_attention"] == 1
        assert st.live_marking["feature_ready"] == 1
        claims = [r for r in _ledger_rows(b2) if r.get("kind") == "net_claim"]
        assert len(claims) == 1
        assert claims[0]["transition"] == "work_start"
        assert claims[0]["fired"] is True
        assert claims[0]["fire_fallback"] is None

    def test_two_concurrent_claims_both_fire(self, b2) -> None:
        state = _state()
        state.claim_task(b2, "T1", owner="u1", session="s")
        st = state.claim_task(b2, "T2", owner="u2", session="s")
        assert (st.live_marking["work_pending"], st.live_marking["work_active"]) == (1, 2)
        assert st.live_marking["worker_slots"] == 0
        assert st.live_marking["agent_attention"] == 1
        claims = [r for r in _ledger_rows(b2) if r.get("kind") == "net_claim"]
        assert [c["fired"] for c in claims] == [True, True]
        assert {c["fire_fallback"] for c in claims} == {None}

    def test_third_claim_refused_capacity(self, b2) -> None:
        state = _state()
        state.claim_task(b2, "T1", owner="u1", session="s")
        state.claim_task(b2, "T2", owner="u2", session="s")
        with pytest.raises(state.SpliceError) as exc:
            state.claim_task(b2, "T3", owner="u3", session="s")
        assert exc.value.code == "worker_capacity_exhausted"

    def test_release_fires_back_edge(self, b2) -> None:
        state = _state()
        state.claim_task(b2, "T1", owner="u1", session="s")
        st = state.release_task(b2, "T1", session="s")
        assert (st.live_marking["work_pending"], st.live_marking["work_active"]) == (3, 0)
        assert st.live_marking["worker_slots"] == 2
        releases = [r for r in _ledger_rows(b2) if r.get("kind") == "net_release"]
        assert len(releases) == 1
        assert releases[0]["transition"] == "work_release"
        assert releases[0]["fired"] is True
        assert releases[0]["fire_fallback"] is None

    def test_release_then_reclaim_fires(self, b2) -> None:
        state = _state()
        state.claim_task(b2, "T1", owner="u1", session="s")
        state.claim_task(b2, "T2", owner="u2", session="s")
        state.release_task(b2, "T1", session="s")
        st = state.claim_task(b2, "T3", owner="u3", session="s")
        assert (st.live_marking["work_pending"], st.live_marking["work_active"]) == (1, 2)
        assert st.live_marking["worker_slots"] == 0
        claims = [r for r in _ledger_rows(b2) if r.get("kind") == "net_claim"]
        assert [c["fired"] for c in claims] == [True, True, True]


class TestOldShapeFallbacksKept:
    def test_old_release_still_no_transition(self, old) -> None:
        state = _state()
        state.claim_task(old, "T1", owner="u1", session="s")
        st = state.release_task(old, "T1", session="s")
        assert (st.live_marking["work_pending"], st.live_marking["work_active"]) == (2, 0)
        releases = [r for r in _ledger_rows(old) if r.get("kind") == "net_release"]
        assert releases[0]["transition"] == "work_release"
        assert releases[0]["fired"] is False
        assert releases[0]["fire_fallback"] == "no_transition"

    def test_old_attention_held_still_labeled(self, old) -> None:
        state = _state()
        st = state.load(old)
        st.live_marking["agent_attention"] = 0
        state.save(old, st)
        st = state.claim_task(old, "T1", owner="u1", session="s")
        assert (st.live_marking["work_pending"], st.live_marking["work_active"]) == (1, 1)
        claims = [r for r in _ledger_rows(old) if r.get("kind") == "net_claim"]
        assert claims[0]["fired"] is False
        assert claims[0]["fire_fallback"] == "transition_not_enabled"

    def test_slot_place_without_arcs_shape_mismatch(self, tmp_path, monkeypatch) -> None:
        state = _state()
        monkeypatch.setenv("OMT_NET_DIR", str(tmp_path))
        monkeypatch.setenv("OMT_LEDGER_PATH", str(tmp_path / "ledger.jsonl"))
        monkeypatch.setenv("OMT_COORDINATION_ROOT", str(tmp_path / "coord"))
        _old_bundle(tmp_path, state, tasks=("T1",))
        st = state.load(tmp_path)
        # Slot place exists in marking but the template has no slot arcs:
        # the firing cannot express the slot move → labeled fallback.
        st.net.add_place("worker_slots", 2)
        st.live_marking["worker_slots"] = 2
        state.save(tmp_path, st)
        st = state.claim_task(tmp_path, "T1", owner="u1", session="s")
        assert (st.live_marking["work_pending"], st.live_marking["work_active"]) == (0, 1)
        assert st.live_marking["worker_slots"] == 1
        claims = [r for r in _ledger_rows(tmp_path) if r.get("kind") == "net_claim"]
        assert claims[0]["fired"] is False
        assert claims[0]["fire_fallback"] == "transition_shape_mismatch"


class TestMigration:
    def test_ensure_pool_b2_migrates_then_noop(self, old) -> None:
        state = _state()
        st0 = state.load(old)
        rev0 = st0.revision
        st, info = state.ensure_pool_b2(old, session="b2-test")
        assert info["migrated"] is True
        assert st.revision == rev0 + 1
        assert "worker_slots" in st.net.places
        assert "work_release" in st.net.transitions
        assert st.live_marking["worker_slots"] == 2
        assert "worker_slots" in st.net.inputs.get("work_start", {})
        assert "work_active" in st.net.inputs.get("work_release", {})
        # Claim on the migrated bundle fires with the slot adopted.
        st = state.claim_task(old, "T1", owner="u1", session="s")
        assert st.live_marking["worker_slots"] == 1
        claims = [r for r in _ledger_rows(old) if r.get("kind") == "net_claim"]
        assert claims[-1]["fired"] is True
        # Rerun is a no-op: same revision, no new ledger row.
        rows_before = len(_ledger_rows(old))
        st2, info2 = state.ensure_pool_b2(old, session="b2-test")
        assert info2["migrated"] is False
        assert st2.revision == st.revision
        assert len(_ledger_rows(old)) == rows_before

    def test_migration_slot_m0_accounts_active(self, tmp_path, monkeypatch) -> None:
        state = _state()
        monkeypatch.setenv("OMT_NET_DIR", str(tmp_path))
        monkeypatch.setenv("OMT_LEDGER_PATH", str(tmp_path / "ledger.jsonl"))
        monkeypatch.setenv("OMT_COORDINATION_ROOT", str(tmp_path / "coord"))
        _old_bundle(tmp_path, state, tasks=("T1", "T2"))
        state.claim_task(tmp_path, "T1", owner="u1", session="s")
        st, info = state.ensure_pool_b2(tmp_path, session="b2-test")
        assert info["migrated"] is True
        assert st.live_marking["worker_slots"] == 1


class TestLedgerEvidence:
    def test_reader_counts_fired_and_fallbacks(self, b2) -> None:
        state = _state()
        mo = _managed()
        state.claim_task(b2, "T1", owner="u1", session="s")
        state.release_task(b2, "T1", session="s")
        res = mo.check_ledger_evidence(_ledger_rows(b2))
        assert res == {"fired": 2, "fallback": {}, "offenders": [], "ok": True}

    def test_reader_flags_rows_missing_keys(self) -> None:
        mo = _managed()
        res = mo.check_ledger_evidence(
            [
                {"kind": "net_claim", "transition": "work_start"},
                {"kind": "net_claim", "transition": "work_start", "fired": False,
                 "fire_fallback": "no_transition"},
                {"kind": "net_sync"},
            ]
        )
        assert res["ok"] is False
        assert res["offenders"] == [0]
        assert res["fallback"] == {"no_transition": 1}
