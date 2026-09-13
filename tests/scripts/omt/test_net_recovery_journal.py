"""Recovery + transaction journal — feature_084.recovery_and_transaction_journal
(T5-6 3B, mh8 strict slice order after 079/080/081/082/083; NEXT_STEP §14–§15).

Goldens: heartbeat stamps liveness (stale gen refuses), recovery
candidates (missing/fresh/stale), recover preserves checkpoint with gen+1
(old gen goes stale — the kill-worker handoff), WAL marker absent after a
clean commit and after a clean refusal, planted-marker reconcile
(aborted/committed/diverged), CLI round-trip.
Hermetic via OMT_NET_DIR / OMT_LEDGER_PATH / OMT_COORDINATION_ROOT (tmp_path).

Canary: new goldens for feature_084 only (scope: tests).
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "scripts" / "omt"
sys.path.insert(0, str(SCRIPTS_DIR))


def _state():
    from net import state  # noqa: PLC0415  (lazy — runnable RED)

    return state


def _lock():
    from net import lock  # noqa: PLC0415  (lazy — runnable RED)

    return lock


def _pool_bundle(base: Path, state, tasks=("T1",)) -> None:
    """Pool net (test_net_task_claim_generation.py shape) + pending bindings."""
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


def _binding(state, base, task_id):
    st = state.load(base)
    return st, next(b for b in st.task_bindings if b["id"] == task_id)


def _coord_root(bundle: Path) -> Path:
    coord = bundle / "coord"
    return coord if coord.exists() else bundle


def _pending_path(bundle: Path) -> Path:
    lock = _lock()
    return lock.txn_pending_path(lock.coordination_root(bundle))


class TestHeartbeat:
    def test_heartbeat_stamps_liveness(self, bundle) -> None:
        state = _state()
        state.claim_task(bundle, "T1", owner="worker-a", session="s")
        _, b = _binding(state, bundle, "T1")
        assert "liveness" not in b
        rev_before = state.load(bundle).revision
        st = state.heartbeat_task(bundle, "T1", generation=1, session="s")
        assert st.revision == rev_before + 1
        _, b = _binding(state, bundle, "T1")
        assert b["liveness"]["owner"] == "worker-a"
        assert b["liveness"]["session"] == "s"
        assert b["liveness"]["last_seen"]
        assert _pending_path(bundle).exists() is False

    def test_heartbeat_stale_generation_refuses(self, bundle) -> None:
        state = _state()
        state.claim_task(bundle, "T1", owner="worker-a", session="s")
        state.transfer_task(bundle, "T1", owner="worker-b", session="s")
        with pytest.raises(state.SpliceError) as ei:
            state.heartbeat_task(bundle, "T1", generation=1, session="s")
        assert ei.value.code == "stale_generation"
        assert _pending_path(bundle).exists() is False


class TestRecoveryCandidates:
    def test_missing_fresh_stale(self, bundle) -> None:
        state = _state()
        state.claim_task(bundle, "T1", owner="worker-a", session="s")
        cands = state.recovery_candidates(bundle)
        assert [c["id"] for c in cands] == ["T1"]
        assert cands[0]["reason"] == "no_heartbeat"
        state.heartbeat_task(bundle, "T1", generation=1, session="s")
        assert state.recovery_candidates(bundle) == []
        _, b = _binding(state, bundle, "T1")
        old_seen = datetime.fromisoformat(b["liveness"]["last_seen"])
        future = old_seen + timedelta(seconds=1000)
        cands = state.recovery_candidates(bundle, stale_after_s=300, now=future)
        assert [c["id"] for c in cands] == ["T1"]
        assert cands[0]["reason"] == "stale_heartbeat"


class TestRecoverHandoff:
    def test_kill_worker_mid_work_lossless_handoff(self, bundle) -> None:
        """T5-6 acceptance: kill worker mid-work → lossless handoff;
        stale submit = stale_generation."""
        state = _state()
        state.claim_task(bundle, "T1", owner="worker-a", session="coord")
        state.checkpoint_task(
            bundle, "T1", generation=1, checkpoint="step1-done", session="a"
        )
        state.heartbeat_task(bundle, "T1", generation=1, session="a")
        rev_before = state.load(bundle).revision
        st = state.recover_task(
            bundle, "T1", owner="worker-b", session="coord"
        )
        assert st.revision == rev_before + 1
        _, b = _binding(state, bundle, "T1")
        assert b["owner"] == "worker-b"
        assert b["generation"] == 2
        assert b["checkpoint"] == "step1-done"
        assert "liveness" not in b
        assert b["workspace"]["id"] == "T1-g2"
        with pytest.raises(state.SpliceError) as ei:
            state.checkpoint_task(
                bundle, "T1", generation=1, checkpoint="late", session="a"
            )
        assert ei.value.code == "stale_generation"
        kinds = [r.get("kind") for r in state.read_ledger_net_records()]
        assert "net_recover" in kinds

    def test_recover_inactive_refuses(self, bundle) -> None:
        state = _state()
        with pytest.raises(state.SpliceError) as ei:
            state.recover_task(bundle, "T1", owner="worker-b", session="s")
        assert ei.value.code == "task_not_active"


class TestJournalMarker:
    def test_clean_commit_leaves_no_marker(self, bundle) -> None:
        state = _state()
        state.claim_task(bundle, "T1", owner="w", session="s")
        assert _pending_path(bundle).exists() is False
        out = state.reconcile_transactions(bundle)
        assert out["status"] == "clean"

    def test_clean_refusal_leaves_no_marker(self, bundle) -> None:
        state = _state()
        with pytest.raises(state.SpliceError):
            state.fire(
                bundle, "work_start", reasoning="r", session="s",
                expected_revision=999,
            )
        assert _pending_path(bundle).exists() is False

    def test_reconcile_aborted_committed_diverged(self, bundle) -> None:
        state = _state()
        lock = _lock()
        root = lock.coordination_root(bundle)
        live = state.load(bundle).revision
        lock.write_pending_txn(root, {
            "txid": "t-abort", "ts": "x", "op": "claim",
            "command_id": None, "from_revision": live,
            "to_revision": live + 1, "task_id": "T1", "canonical": "c",
        })
        out = state.reconcile_transactions(bundle, session="s")
        assert out["status"] == "recovered_aborted"
        assert _pending_path(bundle).exists() is False
        state.claim_task(bundle, "T1", owner="w", session="s")
        live = state.load(bundle).revision
        lock.write_pending_txn(root, {
            "txid": "t-commit", "ts": "x", "op": "heartbeat",
            "command_id": None, "from_revision": live - 1,
            "to_revision": live, "task_id": "T1", "canonical": "c",
        })
        out = state.reconcile_transactions(bundle, session="s")
        assert out["status"] == "recovered_committed"
        assert _pending_path(bundle).exists() is False
        lock.write_pending_txn(root, {
            "txid": "t-div", "ts": "x", "op": "claim",
            "command_id": None, "from_revision": 111,
            "to_revision": 112, "task_id": "T9", "canonical": "c",
        })
        out = state.reconcile_transactions(bundle, session="s")
        assert out["status"] == "diagnosis"
        assert out["code"] == "txn_diverged"
        assert _pending_path(bundle).exists() is True


class TestCliRoundTrip:
    def test_heartbeat_recover_reconcile_cli(self, bundle, monkeypatch, capsys) -> None:
        from net import cli  # noqa: PLC0415  (lazy — runnable RED)

        monkeypatch.setenv("OMT_NET_DIR", str(bundle))
        assert cli.main(["claim", "--task-id", "T1", "--owner", "wa",
                         "--reasoning", "r", "--session", "s"]) == 0
        capsys.readouterr()
        assert cli.main(["heartbeat", "--task-id", "T1", "--generation", "1",
                         "--reasoning", "r", "--session", "s"]) == 0
        env = json.loads(capsys.readouterr().out)
        assert env["ok"] is True and env["op"] == "heartbeat"
        assert cli.main(["recover", "--task-id", "T1", "--owner", "wb",
                         "--reasoning", "r", "--session", "s"]) == 0
        env = json.loads(capsys.readouterr().out)
        assert env["ok"] is True and env["op"] == "recover"
        assert env["task"]["generation"] == 2
        assert cli.main(["reconcile", "--reasoning", "r",
                         "--session", "s"]) == 0
        env = json.loads(capsys.readouterr().out)
        assert env == {"ok": True, "op": "reconcile", "status": "clean"}
