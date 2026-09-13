"""Two-worker capacity + scope arbitration — feature_082.two_worker_capacity_scope_arbitration
(T5-4 2D, NEXT_STEP §10–§11 + Slice 2D, mh8 D8/D13 worker_slots=2 one-machine).

Goldens: A+T1 + B+T2 concurrent; T3 refused worker_capacity_exhausted;
scope overlap refused scope_conflict(blocking_task); component-aware
(src/foo vs src/foobar OK, vs src/foo/bar conflict); release frees a slot;
probe menu surfaces parallel choices.
Hermetic via OMT_NET_DIR / OMT_LEDGER_PATH / OMT_COORDINATION_ROOT (tmp_path).

Canary: new goldens for feature_082 only (scope: tests).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "scripts" / "omt"
sys.path.insert(0, str(SCRIPTS_DIR))


def _state():
    from net import state  # noqa: PLC0415 (lazy — runnable RED)

    return state


def _pool_bundle(base: Path, state, tasks: dict[str, list[str]]) -> None:
    """Pool net + one pending binding per task id with a scope list."""
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
        {"id": tid, "place": "work_pending", "generation": 0, "scope": list(scope)}
        for tid, scope in tasks.items()
    ]
    state.save(base, st)


@pytest.fixture()
def bundle(tmp_path, monkeypatch):
    state = _state()
    monkeypatch.setenv("OMT_NET_DIR", str(tmp_path))
    monkeypatch.setenv("OMT_LEDGER_PATH", str(tmp_path / "ledger.jsonl"))
    monkeypatch.setenv("OMT_COORDINATION_ROOT", str(tmp_path / "coord"))
    _pool_bundle(
        tmp_path,
        state,
        {
            "T1": ["src/agentx/agent/model"],
            "T2": ["src/agentx/ui/screens"],
            "T3": ["tests/agent/model"],
        },
    )
    return tmp_path


def _binding(state, base, task_id):
    st = state.load(base)
    return st, next(b for b in st.task_bindings if b["id"] == task_id)


class TestWorkerCapacity:
    def test_two_disjoint_claims_run_concurrent(self, bundle) -> None:
        state = _state()
        state.claim_task(bundle, "T1", owner="alice", session="w")
        state.claim_task(bundle, "T2", owner="bob", session="w")
        st = state.load(bundle)
        places = {b["id"]: b["place"] for b in st.task_bindings}
        assert places["T1"] == "work_active"
        assert places["T2"] == "work_active"
        assert st.live_marking["work_active"] == 2

    def test_third_claim_refused_capacity(self, bundle) -> None:
        state = _state()
        state.claim_task(bundle, "T1", owner="alice", session="w")
        state.claim_task(bundle, "T2", owner="bob", session="w")
        with pytest.raises(state.SpliceError) as exc:
            state.claim_task(bundle, "T3", owner="carol", session="w")
        assert exc.value.code == "worker_capacity_exhausted"

    def test_release_frees_a_slot(self, bundle) -> None:
        state = _state()
        state.claim_task(bundle, "T1", owner="alice", session="w")
        state.claim_task(bundle, "T2", owner="bob", session="w")
        state.release_task(bundle, "T1", owner="alice", session="w")
        st = state.claim_task(bundle, "T3", owner="carol", session="w")
        b = next(x for x in st.task_bindings if x["id"] == "T3")
        assert b["place"] == "work_active"
        assert b["owner"] == "carol"


class TestScopeArbitration:
    def test_overlapping_scope_refused(self, tmp_path, monkeypatch) -> None:
        state = _state()
        monkeypatch.setenv("OMT_NET_DIR", str(tmp_path))
        monkeypatch.setenv("OMT_LEDGER_PATH", str(tmp_path / "ledger.jsonl"))
        monkeypatch.setenv("OMT_COORDINATION_ROOT", str(tmp_path / "coord"))
        _pool_bundle(
            tmp_path,
            state,
            {"T1": ["src/agentx/agent/model"], "T2": ["src/agentx/agent/model/policy"]},
        )
        state.claim_task(tmp_path, "T1", owner="alice", session="w")
        with pytest.raises(state.SpliceError) as exc:
            state.claim_task(tmp_path, "T2", owner="bob", session="w")
        assert exc.value.code == "scope_conflict"
        assert "T1" in str(exc.value)

    def test_component_aware_sibling_prefix_is_not_a_conflict(
        self, tmp_path, monkeypatch
    ) -> None:
        """src/foo vs src/foobar share a string prefix but no path component."""
        state = _state()
        monkeypatch.setenv("OMT_NET_DIR", str(tmp_path))
        monkeypatch.setenv("OMT_LEDGER_PATH", str(tmp_path / "ledger.jsonl"))
        monkeypatch.setenv("OMT_COORDINATION_ROOT", str(tmp_path / "coord"))
        _pool_bundle(
            tmp_path, state, {"T1": ["src/foo"], "T2": ["src/foobar"]}
        )
        assert state.scopes_overlap(["src/foo"], ["src/foobar"]) is False
        assert state.scopes_overlap(["src/foo"], ["src/foo/bar"]) is True
        state.claim_task(tmp_path, "T1", owner="alice", session="w")
        st = state.claim_task(tmp_path, "T2", owner="bob", session="w")
        places = {b["id"]: b["place"] for b in st.task_bindings}
        assert places == {"T1": "work_active", "T2": "work_active"}

    def test_unscoped_tasks_never_conflict(self, tmp_path, monkeypatch) -> None:
        state = _state()
        monkeypatch.setenv("OMT_NET_DIR", str(tmp_path))
        monkeypatch.setenv("OMT_LEDGER_PATH", str(tmp_path / "ledger.jsonl"))
        monkeypatch.setenv("OMT_COORDINATION_ROOT", str(tmp_path / "coord"))
        _pool_bundle(tmp_path, state, {"T1": [], "T2": []})
        state.claim_task(tmp_path, "T1", owner="alice", session="w")
        st = state.claim_task(tmp_path, "T2", owner="bob", session="w")
        assert {b["id"]: b["place"] for b in st.task_bindings} == {
            "T1": "work_active",
            "T2": "work_active",
        }


class TestProbeParallelMenu:
    def test_probe_menu_shows_parallel_choices(self, bundle) -> None:
        from net import cli  # noqa: PLC0415

        st = _state().load(bundle)
        menu = cli._task_menu(st, list(st.task_bindings), ["work_start"])
        assert menu["capacity"] == {"workers_used": 0, "workers_total": 2, "free": 2}
        assert menu["parallel"] == ["T1", "T2"]
        # Claiming one shrinks the free count but keeps a parallel offer.
        _state().claim_task(bundle, "T1", owner="alice", session="w")
        st2 = _state().load(bundle)
        menu2 = cli._task_menu(st2, list(st2.task_bindings), ["work_start"])
        assert menu2["capacity"]["workers_used"] == 1
        assert "T2" in menu2["parallel"]
