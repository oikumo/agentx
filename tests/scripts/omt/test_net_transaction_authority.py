"""Two-process transaction authority — feature_079.net_transaction_authority
(T5-1 2A, mh8 D10 lock-first).

Goldens: same-revision race (exactly 1 commit + 1 stale_revision),
command_id replay (no double-fire), command_id conflict, solo-path freeze.
Hermetic via OMT_NET_DIR / OMT_LEDGER_PATH / OMT_COORDINATION_ROOT (tmp_path).
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


def _two_token_bundle(base: Path, state) -> None:
    """p=2 ->t1-> q, p=2 ->t2-> q at revision 0 (t1 still enabled after one fire)."""
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


def _race_worker(base_str: str, barrier, queue) -> None:
    """Forked worker: force maximal overlap, then fire from rev 0."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts" / "omt"))
    from net import state

    try:
        barrier.wait(timeout=30)
    except Exception:
        queue.put(("error", "barrier_timeout"))
        return
    try:
        st = state.fire(
            Path(base_str), "t1", reasoning="race", session="w", expected_revision=0
        )
        queue.put(("ok", st.revision, dict(st.live_marking)))
    except state.SpliceError as exc:
        queue.put(("error", exc.code))


class TestSoloPathFrozen:
    def test_plain_fire_commits_without_index(self, bundle) -> None:
        state = _state()
        st = state.fire(bundle, "t1", reasoning="r", session="s")
        assert st.revision == 1
        assert st.live_marking == {"p": 1, "q": 1}
        assert not (bundle / "coord" / "net_commands.json").exists()

    def test_stale_revision_still_refuses(self, bundle) -> None:
        state = _state()
        with pytest.raises(state.SpliceError) as ei:
            state.fire(bundle, "t1", reasoning="r", session="s", expected_revision=999)
        assert ei.value.code == "stale_revision"
        assert state.load(bundle).revision == 0


class TestSameRevisionRace:
    def test_two_procs_from_rev0_exactly_one_commits(self, bundle) -> None:
        """T5-1 acceptance: 2 procs from rev N → 1 commit + 1 stale_revision."""
        state = _state()
        ctx = mp.get_context("fork")
        barrier = ctx.Barrier(2)
        queue = ctx.Queue()
        procs = [
            ctx.Process(target=_race_worker, args=(str(bundle), barrier, queue))
            for _ in range(2)
        ]
        for p in procs:
            p.start()
        for p in procs:
            p.join(60)
            assert p.exitcode == 0
        outcomes = sorted([queue.get(timeout=10), queue.get(timeout=10)])
        assert outcomes[0][0] == "error" and outcomes[0][1] == "stale_revision"
        assert outcomes[1][0] == "ok" and outcomes[1][1] == 1
        final = state.load(bundle)
        assert final.revision == 1
        assert final.live_marking == {"p": 1, "q": 1}


class TestCommandIdempotency:
    def test_retry_same_command_replays_without_bump(self, bundle) -> None:
        state = _state()
        first = state.fire(
            bundle, "t1", reasoning="r", session="s",
            expected_revision=0, command_id="c1",
        )
        assert first.revision == 1
        # Retry carries the ORIGINAL expected rev — idempotency is checked first.
        again = state.fire(
            bundle, "t1", reasoning="r", session="s",
            expected_revision=0, command_id="c1",
        )
        assert again.revision == 1
        assert again.live_marking == {"p": 1, "q": 1}
        assert state.load(bundle).revision == 1

    def test_same_id_different_command_conflicts(self, bundle) -> None:
        state = _state()
        state.fire(
            bundle, "t1", reasoning="r", session="s",
            expected_revision=0, command_id="c1",
        )
        with pytest.raises(state.SpliceError) as ei:
            state.fire(
                bundle, "t2", reasoning="r", session="s",
                expected_revision=1, command_id="c1",
            )
        assert ei.value.code == "command_id_conflict"
        assert state.load(bundle).revision == 1

    def test_splice_replay_and_conflict(self, bundle) -> None:
        state = _state()
        mutation = {
            "add_places": [{"name": "extra", "tokens": 0}],
            "add_transitions": [],
            "add_arcs": [],
        }
        st, info = state.splice(
            bundle, "add", mutation=mutation, reasoning="r", session="s",
            expected_revision=0, command_id="s1",
        )
        assert st.revision == 1
        assert "replayed" not in info
        st2, info2 = state.splice(
            bundle, "add", mutation=mutation, reasoning="r", session="s",
            expected_revision=0, command_id="s1",
        )
        assert info2["replayed"] is True
        assert st2.revision == 1
        with pytest.raises(state.SpliceError) as ei:
            state.splice(
                bundle, "add",
                mutation={"add_places": [{"name": "other", "tokens": 0}],
                          "add_transitions": [], "add_arcs": []},
                reasoning="r", session="s", expected_revision=1, command_id="s1",
            )
        assert ei.value.code == "command_id_conflict"
        assert state.load(bundle).revision == 1

    def test_splice_stale_revision_refuses_inside_lock(self, bundle) -> None:
        state = _state()
        with pytest.raises(state.SpliceError) as ei:
            state.splice(
                bundle, "add",
                mutation={"add_places": [], "add_transitions": [], "add_arcs": []},
                reasoning="r", session="s", expected_revision=4242,
            )
        assert ei.value.code == "stale_revision"


class TestCliThreading:
    def test_fire_command_id_round_trip(self, bundle, capsys) -> None:
        from net import cli  # noqa: PLC0415

        argv = ["fire", "--transition", "t1", "--reasoning", "r",
                "--session", "s", "--command-id", "cli1"]
        assert cli.main(argv) == 0
        env = json.loads(capsys.readouterr().out)
        assert env["ok"] is True and env["revision"] == 1
        assert cli.main(argv) == 0
        env2 = json.loads(capsys.readouterr().out)
        assert env2["ok"] is True and env2["revision"] == 1
        state = _state()
        assert state.load(bundle).revision == 1
