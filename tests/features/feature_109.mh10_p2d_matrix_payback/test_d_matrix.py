"""Slice-D allow/deny matrix goldens — feature_109.mh10_p2d_matrix_payback.

V1–V5 valid controls ALLOW; I1–I8 seeded invalids DENY fail-closed.
Zero live-gate change (tests-only, rev stays 60).

Hermetic via OMT_NET_DIR / OMT_LEDGER_PATH / OMT_COORDINATION_ROOT.
Canary: new goldens for feature_109 only (scope: tests).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "scripts" / "omt"
sys.path.insert(0, str(SCRIPTS_DIR))

FEATURE = "feature_109.mh10_p2d_matrix_payback"

CONCURRENT = {"work_active": 2}
SOLO = {"work_active": 0}


def _gate():
    from net import gate  # noqa: PLC0415 (lazy — runnable RED)

    return gate


def _ops():
    from net import managed_ops  # noqa: PLC0415 (lazy — runnable RED)

    return managed_ops


def _state():
    from net import state  # noqa: PLC0415 (lazy — runnable RED)

    return state


def _lock():
    from net import lock  # noqa: PLC0415 (lazy — runnable RED)

    return lock


def _two_token_bundle(base: Path, state) -> None:
    state.init_empty(base)
    st = state.load(base)
    st.net.add_place("p", tokens=2)
    st.net.add_place("q", tokens=0)
    st.net.add_transition("t1")
    st.net.add_transition("t2")
    st.net.add_input("p", "t1")
    st.net.add_output("t1", "q")
    st.net.add_input("p", "t2")
    st.net.add_output("t2", "q")
    st.live_marking = {"p": 2, "q": 0}
    state.save(base, st)


@pytest.fixture()
def bundle(tmp_path, monkeypatch):
    state = _state()
    monkeypatch.setenv("OMT_NET_DIR", str(tmp_path))
    monkeypatch.setenv("OMT_LEDGER_PATH", str(tmp_path / "ledger.jsonl"))
    monkeypatch.setenv("OMT_COORDINATION_ROOT", str(tmp_path / "coord"))
    _two_token_bundle(tmp_path, state)
    return tmp_path


# ---------------------------------------------------------------------------
# V-controls (must ALLOW)
# ---------------------------------------------------------------------------


class TestValidControls:
    def test_v1_fire_receipt_allows_concurrent_edit(self) -> None:
        gate = _gate()
        out = gate.check_edit_allowed(
            has_fire_receipt=True, live_marking=dict(CONCURRENT)
        )
        assert out["allowed"] is True and out["code"] == "OK"

    def test_v2_derived_reads_stay_non_firing(self) -> None:
        ops = _ops()
        rows = {r["op"]: r for r in ops.MANAGED_OPS}
        for op in ("project_sync", "session_menu"):
            assert rows[op]["fired_today"] == "no"
            assert "derived read" in rows[op]["transition"]
        # B-vs-M agreement with fired=false reads OMISSION, never FIRED.
        assert ops.classify(3, 3, False) == "OMISSION"

    def test_v3_solo_path_unchanged(self, bundle) -> None:
        state = _state()
        lock = _lock()
        st = state.fire(bundle, "t1", reasoning="r", session="s", command_id=None)
        assert st.revision == 1
        coord = lock.coordination_root(bundle)
        assert lock.txn_pending_path(coord).exists() is False

    def test_v4_reconciled_retry_replays(self, bundle) -> None:
        state = _state()
        lock = _lock()
        st = state.fire(
            bundle, "t1", reasoning="r", session="s", command_id="D-v4"
        )
        assert st.revision == 1
        assert lock.lookup_command(lock.coordination_root(bundle), "D-v4") is not None
        st2 = state.fire(
            bundle, "t1", reasoning="r", session="s", command_id="D-v4"
        )
        assert st2.revision == 1  # replay, no second bump

    def test_v5_ledger_evidence_reader_accepts_shaped_rows(self) -> None:
        ops = _ops()
        recs = [
            {"kind": "net_claim", "transition": "work_start",
             "fired": True, "fire_fallback": None},
            {"kind": "net_submit", "transition": "work_submit",
             "fired": False, "fire_fallback": "no_slot"},
        ]
        out = ops.check_ledger_evidence(recs)
        assert out["ok"] is True and out["offenders"] == []
        assert out["fired"] == 1 and out["fallback"] == {"no_slot": 1}


# ---------------------------------------------------------------------------
# I-invalids (must DENY fail-closed)
# ---------------------------------------------------------------------------


class TestSeededInvalids:
    def test_i1_no_receipt_denies_concurrent_edit(self) -> None:
        gate = _gate()
        out = gate.check_edit_allowed(
            has_fire_receipt=False, live_marking=dict(CONCURRENT)
        )
        assert out == {"allowed": False, "code": "ERR_NET_NOT_ENABLED"}

    def test_i2_stale_rev_denies(self) -> None:
        gate = _gate()
        out = gate.check_edit_allowed(
            has_fire_receipt=True,
            live_marking=dict(CONCURRENT),
            expected_revision=60,
            live_revision=61,
        )
        assert out == {"allowed": False, "code": "ERR_NET_STALE_REV"}

    def test_i3_drift_denies(self) -> None:
        gate = _gate()
        out = gate.check_edit_allowed(
            has_fire_receipt=True,
            live_marking=dict(CONCURRENT),
            drifted=True,
        )
        assert out == {"allowed": False, "code": "ERR_NET_DRIFT_CONFLICT"}
        out2 = gate.check_edit_allowed(
            has_fire_receipt=True,
            live_marking=dict(CONCURRENT),
            conflicts=[{"place": "work_active"}],
        )
        assert out2 == {"allowed": False, "code": "ERR_NET_DRIFT_CONFLICT"}

    def test_i4_net_down_denies_without_breakglass(self) -> None:
        gate = _gate()
        out = gate.check_edit_allowed(
            has_fire_receipt=True,
            live_marking=dict(CONCURRENT),
            net_available=False,
        )
        assert out == {"allowed": False, "code": "ERR_NET_DOWN"}

    def test_i5_absent_breakglass_never_allows(self) -> None:
        gate = _gate()
        # No break-glass flag + concurrent + no receipt → deny (expired/absent
        # break-glass grants nothing; presence grants OK even when down).
        denied = gate.check_edit_allowed(
            has_fire_receipt=False,
            live_marking=dict(CONCURRENT),
            break_glass_scope_all=False,
        )
        assert denied["allowed"] is False
        allowed = gate.check_edit_allowed(
            has_fire_receipt=False,
            live_marking=dict(CONCURRENT),
            net_available=False,
            break_glass_scope_all=True,
        )
        assert allowed == {"allowed": True, "code": "OK", "break_glass": True}

    def test_i6_task_fence_fail_closed(self, tmp_path) -> None:
        gate = _gate()
        # Unreadable bundle → fail-closed ERR_NET_DOWN (never allow blind).
        out = gate.check_managed_edit_allowed(
            base=tmp_path / "no-such-bundle",
            task_id="t-1",
            generation=1,
            path="src/x.py",
        )
        assert out == {"allowed": False, "code": "ERR_NET_DOWN"}
        # Contract pins: generation/owner/workspace fences exist with these
        # codes (full claim-fence behavior covered by feature_080/081 suites).
        import re

        src = (SCRIPTS_DIR / "net" / "state.py").read_text(encoding="utf-8")
        for code in ("stale_generation", "not_owner", "workspace_mismatch"):
            assert re.search(rf'"{code}"', src) is not None

    def test_i7_lane_over_cap_never_silent(self) -> None:
        ops = _ops()
        rows = {r["op"]: r for r in ops.MANAGED_OPS}
        for op in ("submit_result", "verify_pass", "integrate_start"):
            assert "yes-B3b-template" in rows[op]["fired_today"]
        # A claim/lane row missing evidence keys is an offender (never silent).
        out = ops.check_ledger_evidence([{"kind": "net_claim"}])
        assert out["ok"] is False and out["offenders"] == [0]

    def test_i8_resultless_commit_diagnoses(self, bundle) -> None:
        state = _state()
        lock = _lock()
        coord = lock.coordination_root(bundle)
        # Plant old-shape marker: save landed (live==to), command_id present,
        # no carried result, no index → fail-closed diagnosis, marker left.
        st = state.load(bundle)
        to_rev = st.revision + 1
        lock.write_pending_txn(
            coord,
            {"txid": "tx-D-i8", "op": "fire", "command_id": "D-i8",
             "from_revision": st.revision, "to_revision": to_rev,
             "canonical": "fire:p->t1"},
        )
        st.live_marking = {"p": 1, "q": 1}
        st.revision = to_rev
        state.save(bundle, st)
        out = state.reconcile_transactions(bundle, session="s")
        assert out["status"] == "diagnosis" and out["code"] == "txn_unindexed_commit"
        assert lock.read_pending_txn(coord) is not None
