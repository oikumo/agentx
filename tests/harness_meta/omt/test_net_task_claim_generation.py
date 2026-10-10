"""Task claim + generation fencing — feature_080.task_claim_generation
(T5-2 2B, mh8 D9 claim+generation, D10 lock-first, D14 idempotency).

Goldens: same-task claim race (exactly 1 winner), unrelated rev bump keeps
the held generation, stale generation cannot submit, release/reclaim
monotonicity, command_id replay/conflict, CLI round-trip.
Hermetic via OMT_NET_DIR / OMT_LEDGER_PATH / OMT_COORDINATION_ROOT (tmp_path).

Canary: new goldens for feature_080 only (scope: tests).
"""
from __future__ import annotations

import json
import multiprocessing as mp
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "scripts" / "omt"
sys.path.insert(0, str(SCRIPTS_DIR))


def _state():
    from net import state  # noqa: PLC0415  (lazy — runnable RED)

    return state


def _pool_bundle(base: Path, state, tasks=("T1",)) -> None:
    """Pool net (test_net_mine.py shape) + one pending binding per task id."""
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


def _claim_race_worker(base_str: str, barrier, queue, owner: str) -> None:
    """Forked worker: maximal overlap, then claim T1 from rev 0."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts" / "omt"))
    from net import state

    try:
        barrier.wait(timeout=30)
    except Exception:
        queue.put(("error", "barrier_timeout"))
        return
    try:
        st = state.claim_task(
            Path(base_str), "T1", owner=owner, session="w", expected_revision=0
        )
        b = next(x for x in st.task_bindings if x["id"] == "T1")
        queue.put(("ok", st.revision, b["owner"], b["generation"]))
    except state.SpliceError as exc:
        queue.put(("error", exc.code))


class TestSameTaskClaimRace:
    def test_two_procs_claiming_one_task_exactly_one_wins(self, bundle) -> None:
        """T5-2 acceptance: same-task race → 1 commit + 1 stale_revision.

        Both workers start from rev 0, so the in-lock authoritative revision
        check (D10, inherited from _transact) refuses the loser with
        stale_revision before it ever reaches the binding check — exactly one
        winner. (A re-claim at the fresh rev refuses task_not_pending;
        pinned sequentially in TestClaimRefusals.)
        """
        state = _state()
        ctx = mp.get_context("fork")
        barrier = ctx.Barrier(2)
        queue = ctx.Queue()
        procs = [
            ctx.Process(target=_claim_race_worker, args=(str(bundle), barrier, queue, o))
            for o in ("alice", "bob")
        ]
        for p in procs:
            p.start()
        for p in procs:
            p.join(60)
            assert p.exitcode == 0
        outcomes = sorted([queue.get(timeout=10), queue.get(timeout=10)])
        assert outcomes[0][0] == "error" and outcomes[0][1] == "stale_revision"
        assert outcomes[1][0] == "ok" and outcomes[1][1] == 1
        _, _, winner, gen = outcomes[1]
        assert winner in ("alice", "bob") and gen == 1
        st, b = _binding(state, bundle, "T1")
        assert st.revision == 1
        assert b["place"] == "work_active" and b["owner"] == winner
        assert st.live_marking["work_pending"] == 0
        assert st.live_marking["work_active"] == 1


class TestGenerationSurvivesRevisionBump:
    def test_unrelated_rev_bump_does_not_revoke_generation(self, bundle) -> None:
        """D9: revision is the short CAS token, generation the long fence."""
        state = _state()
        state.claim_task(bundle, "T1", owner="alice", session="s")
        # Unrelated structural mutation bumps the global revision twice.
        for name in ("extra_a", "extra_b"):
            state.splice(
                bundle, "add",
                mutation={"add_places": [{"name": name, "tokens": 0}],
                          "add_transitions": [], "add_arcs": []},
                reasoning="unrelated", session="other",
            )
        assert state.load(bundle).revision == 3
        # The held gen-1 checkpoint still submits.
        st = state.checkpoint_task(
            bundle, "T1", generation=1, checkpoint="cp1", session="s"
        )
        assert st.revision == 4
        _, b = _binding(state, bundle, "T1")
        assert b["generation"] == 1 and b["checkpoint"] == "cp1"


class TestStaleGenerationCannotSubmit:
    def test_transfer_revokes_old_owner(self, bundle) -> None:
        state = _state()
        state.claim_task(bundle, "T1", owner="alice", session="s")
        state.transfer_task(bundle, "T1", owner="bob", session="coord")
        with pytest.raises(state.SpliceError) as ei:
            state.checkpoint_task(bundle, "T1", generation=1, session="s")
        assert ei.value.code == "stale_generation"
        st = state.checkpoint_task(bundle, "T1", generation=2, session="s")
        assert st.revision == 3

    def test_release_reclaim_revokes_old_generation(self, bundle) -> None:
        state = _state()
        state.claim_task(bundle, "T1", owner="alice", session="s")
        state.release_task(bundle, "T1", owner="alice", session="s")
        state.claim_task(bundle, "T1", owner="bob", session="s")
        _, b = _binding(state, bundle, "T1")
        assert b["generation"] == 2  # monotonic: release keeps, reclaim bumps
        with pytest.raises(state.SpliceError) as ei:
            state.checkpoint_task(bundle, "T1", generation=1, session="s")
        assert ei.value.code == "stale_generation"


class TestClaimRefusals:
    def test_unknown_task(self, bundle) -> None:
        state = _state()
        with pytest.raises(state.SpliceError) as ei:
            state.claim_task(bundle, "NOPE", owner="x", session="s")
        assert ei.value.code == "task_not_found"
        assert state.load(bundle).revision == 0

    def test_double_claim_and_wrong_owner_release(self, bundle) -> None:
        state = _state()
        state.claim_task(bundle, "T1", owner="alice", session="s")
        with pytest.raises(state.SpliceError) as ei:
            state.claim_task(bundle, "T1", owner="bob", session="s")
        assert ei.value.code == "task_not_pending"
        with pytest.raises(state.SpliceError) as ei:
            state.release_task(bundle, "T1", owner="mallory", session="s")
        assert ei.value.code == "not_owner"
        # Owner cleared on release; binding+tokens back to pending.
        st = state.release_task(bundle, "T1", owner="alice", session="s")
        _, b = _binding(state, bundle, "T1")
        assert b["place"] == "work_pending" and "owner" not in b
        assert st.live_marking["work_pending"] == 1
        assert st.live_marking["work_active"] == 0


class TestClaimIdempotency:
    def test_same_command_id_replays_without_bump(self, bundle) -> None:
        state = _state()
        first = state.claim_task(
            bundle, "T1", owner="alice", session="s",
            expected_revision=0, command_id="k1",
        )
        assert first.revision == 1
        again = state.claim_task(
            bundle, "T1", owner="alice", session="s",
            expected_revision=0, command_id="k1",
        )
        assert again.revision == 1
        _, b = _binding(state, bundle, "T1")
        assert b["owner"] == "alice" and b["generation"] == 1

    def test_same_id_different_claim_conflicts(self, bundle) -> None:
        state = _state()
        state.claim_task(
            bundle, "T1", owner="alice", session="s",
            expected_revision=0, command_id="k1",
        )
        with pytest.raises(state.SpliceError) as ei:
            state.release_task(
                bundle, "T1", session="s",
                expected_revision=1, command_id="k1",
            )
        assert ei.value.code == "command_id_conflict"
        assert state.load(bundle).revision == 1


class TestCliRoundTrip:
    def test_claim_checkpoint_release_envelopes(self, bundle, capsys) -> None:
        from net import cli  # noqa: PLC0415

        assert cli.main(["claim", "--task-id", "T1", "--owner", "w",
                         "--reasoning", "r", "--session", "s"]) == 0
        env = json.loads(capsys.readouterr().out)
        assert env["ok"] is True and env["revision"] == 1
        assert env["task"]["id"] == "T1" and env["task"]["place"] == "work_active"
        assert env["task"]["owner"] == "w" and env["task"]["generation"] == 1
        # feature_081: claim envelope additionally carries the bootstrapped
        # workspace (additive — the 080 keys above stay byte-identical).
        assert env["task"]["workspace"]["id"] == "T1-g1"
        assert cli.main(["checkpoint", "--task-id", "T1", "--generation", "1",
                         "--mutation", '{"checkpoint": "cp"}',
                         "--reasoning", "r", "--session", "s"]) == 0
        env2 = json.loads(capsys.readouterr().out)
        assert env2["ok"] is True and env2["revision"] == 2
        assert cli.main(["release", "--task-id", "T1",
                         "--reasoning", "r", "--session", "s"]) == 0
        env3 = json.loads(capsys.readouterr().out)
        assert env3["task"]["place"] == "work_pending"

    def test_checkpoint_bad_json_refuses(self, bundle, capsys) -> None:
        from net import cli  # noqa: PLC0415

        assert cli.main(["claim", "--task-id", "T1",
                         "--reasoning", "r", "--session", "s"]) == 0
        capsys.readouterr()
        assert cli.main(["checkpoint", "--task-id", "T1", "--generation", "1",
                         "--mutation", "{nope",
                         "--reasoning", "r", "--session", "s"]) == 1
        env = json.loads(capsys.readouterr().out)
        assert env["ok"] is False and env["error"] == "invalid_mutation"
        assert env["op"] == "checkpoint"
