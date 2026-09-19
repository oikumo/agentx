"""Slice-C crash-reorder goldens — feature_108.mh10_p2c_crash_reorder.

Record-before-clear + reconcile backfill: every crash point between
save/clear/record reconciles deterministically with idempotent replay.

Hermetic via OMT_NET_DIR / OMT_LEDGER_PATH / OMT_COORDINATION_ROOT.
Canary: new goldens for feature_108 only (scope: tests).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "scripts" / "omt"
sys.path.insert(0, str(SCRIPTS_DIR))

FEATURE = "feature_108.mh10_p2c_crash_reorder"


def _state():
    from net import state  # noqa: PLC0415  (lazy — runnable RED)

    return state


def _lock():
    from net import lock  # noqa: PLC0415  (lazy — runnable RED)

    return lock


def _two_token_bundle(base: Path, state) -> None:
    """p=2 ->t1-> q, p=2 ->t2-> q at revision 0."""
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


def _coord(bundle: Path):
    lock = _lock()
    return lock.coordination_root(bundle)


def _pending_path(bundle: Path) -> Path:
    lock = _lock()
    return lock.txn_pending_path(lock.coordination_root(bundle))


class TestHappyPath:
    def test_record_then_clear_replay_no_bump(self, bundle) -> None:
        state = _state()
        lock = _lock()
        st = state.fire(bundle, "t1", reasoning="r", session="s", command_id="C-happy")
        assert st.revision == 1
        assert _pending_path(bundle).exists() is False
        assert lock.lookup_command(_coord(bundle), "C-happy") is not None
        # Retry replays without a second fire.
        st2 = state.fire(bundle, "t1", reasoning="r", session="s", command_id="C-happy")
        assert st2.revision == 1
        assert st2.live_marking == {"p": 1, "q": 1}

    def test_solo_path_unchanged(self, bundle) -> None:
        state = _state()
        lock = _lock()
        st = state.fire(bundle, "t1", reasoning="r", session="s")
        assert st.revision == 1
        assert _pending_path(bundle).exists() is False
        assert not (_coord(bundle) / "net_commands.json").exists()


class TestCrashWindows:
    def test_w1_crash_before_record_backfills_and_replays(self, bundle, monkeypatch) -> None:
        """Save landed, crash before record_command: marker carries result,
        reconcile backfills the index, retry replays (exactly 1 bump)."""
        state = _state()
        lock = _lock()
        calls = {"n": 0}
        real_record = state.record_command

        def _raise_once(*a, **k):
            calls["n"] += 1
            if calls["n"] == 1:
                raise RuntimeError("crash-before-record")
            return real_record(*a, **k)

        monkeypatch.setattr(state, "record_command", _raise_once)
        with pytest.raises(RuntimeError, match="crash-before-record"):
            state.fire(bundle, "t1", reasoning="r", session="s", command_id="C-w1")
        assert state.load(bundle).revision == 1
        pending = lock.read_pending_txn(_coord(bundle))
        assert pending is not None and pending.get("command_id") == "C-w1"
        out = state.reconcile_transactions(bundle, session="s")
        assert out["status"] in ("recovered_committed", "recovered_committed_backfilled")
        assert _pending_path(bundle).exists() is False
        assert lock.lookup_command(_coord(bundle), "C-w1") is not None
        st2 = state.fire(bundle, "t1", reasoning="r", session="s", command_id="C-w1")
        assert st2.revision == 1
        assert st2.live_marking == {"p": 1, "q": 1}

    def test_w2_crash_between_record_and_clear_replays(self, bundle, monkeypatch) -> None:
        """Record landed, crash before clear: marker + index present,
        reconcile commits, retry replays. Marker carries the result
        (new order) so reconcile can audit exactly."""
        state = _state()
        lock = _lock()
        # clear becomes a no-op during the fire only: marker stays, index lands.
        calls = {"n": 0}
        real_clear = state.clear_pending_txn

        def _skip_once(*a, **k):
            calls["n"] += 1
            if calls["n"] == 1:
                return None
            return real_clear(*a, **k)

        monkeypatch.setattr(state, "clear_pending_txn", _skip_once)
        st = state.fire(bundle, "t1", reasoning="r", session="s", command_id="C-w2")
        assert st.revision == 1
        assert lock.lookup_command(_coord(bundle), "C-w2") is not None
        assert _pending_path(bundle).exists() is True
        pending = lock.read_pending_txn(_coord(bundle))
        # New order carries the commit result in the marker for backfill/audit.
        assert pending is not None and "result" in pending
        out = state.reconcile_transactions(bundle, session="s")
        assert out["status"] in ("recovered_committed", "recovered_committed_backfilled")
        assert _pending_path(bundle).exists() is False
        st2 = state.fire(bundle, "t1", reasoning="r", session="s", command_id="C-w2")
        assert st2.revision == 1

    def test_resultless_marker_diagnoses_not_silent(self, bundle) -> None:
        """Old-shape marker (no result) with live==to and no index:
        fail-closed diagnosis, marker left, never synthesized."""
        state = _state()
        lock = _lock()
        state.fire(bundle, "t1", reasoning="r", session="s", command_id="C-keep")
        live = state.load(bundle).revision
        assert live == 1
        lock.write_pending_txn(_coord(bundle), {
            "txid": "t-noresult", "ts": "x", "op": "fire",
            "command_id": "C-noresult", "from_revision": 0,
            "to_revision": 1, "task_id": None, "canonical": "c",
        })
        out = state.reconcile_transactions(bundle, session="s")
        assert out["status"] == "diagnosis"
        assert _pending_path(bundle).exists() is True
        assert lock.lookup_command(_coord(bundle), "C-noresult") is None

    def test_exception_after_save_leaves_marker(self, bundle, monkeypatch) -> None:
        """append_ledger fails after save: marker left for reconcile,
        fail-closed diagnosis (no result to backfill), never clean."""
        state = _state()
        calls = {"n": 0}
        real_append = state.append_ledger

        def _once(*a, **k):
            calls["n"] += 1
            if calls["n"] == 1:
                raise RuntimeError("crash-after-save")
            return real_append(*a, **k)

        monkeypatch.setattr(state, "append_ledger", _once)
        with pytest.raises(RuntimeError, match="crash-after-save"):
            state.fire(bundle, "t1", reasoning="r", session="s", command_id="C-exc")
        assert state.load(bundle).revision == 1
        assert _pending_path(bundle).exists() is True
        out = state.reconcile_transactions(bundle, session="s")
        # No result was ever committed (apply raised) — honest diagnosis, marker left.
        assert out["status"] == "diagnosis"
        assert _pending_path(bundle).exists() is True
