"""Verification + integration lane — feature_083.verification_integration_lane
(T5-5 3A, NEXT_STEP §13 + Slice 3A, mh8 strict order after 079/080/081/082).

Goldens: submit active→verifying (worker freed, test occupied, immutable ref);
second submit refused verification_busy (test_slots=1); verify requires
coordinator (worker refused not_coordinator); worker integrate refused even
for own result; integration serialized (second start → integration_busy);
integrate_fail returns to pending with evidence and objective unsatisfied;
stale generation cannot publish; CLI round-trip for submit.
Hermetic via OMT_NET_DIR / OMT_LEDGER_PATH / OMT_COORDINATION_ROOT (tmp_path).

Canary: new goldens for feature_083 only (scope: tests).
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
            "T1": ["src/a"],
            "T2": ["src/b"],
        },
    )
    return tmp_path


def _binding(state, base, task_id):
    st = state.load(base)
    return st, next(b for b in st.task_bindings if b["id"] == task_id)


def _claim(state, base, task_id, owner):
    st = state.claim_task(base, task_id, owner=owner, session="w")
    return next(b for b in st.task_bindings if b["id"] == task_id)


RESULT_T1 = {
    "head_commit": "def456",
    "patch_digest": "sha256:abc",
    "base_commit": "abc123",
    "local_checks": [{"name": "pytest focused", "result": "pass"}],
}


class TestSubmit:
    def test_submit_moves_active_to_verifying_with_immutable_ref(
        self, bundle
    ) -> None:
        state = _state()
        b = _claim(state, bundle, "T1", "alice")
        gen = b["generation"]
        st = state.submit_result(
            bundle, "T1", generation=gen, owner="alice",
            result=dict(RESULT_T1), session="w",
        )
        sub = next(x for x in st.task_bindings if x["id"] == "T1")
        assert sub["place"] == "work_verifying"
        assert sub["generation"] == gen
        assert sub["submission"]["head_commit"] == "def456"
        assert sub["submission"]["patch_digest"] == "sha256:abc"
        # worker slot freed (capacity), test slot occupied
        assert state._active_task_count(st) == 0

    def test_second_submit_refused_verification_busy(self, bundle) -> None:
        state = _state()
        b1 = _claim(state, bundle, "T1", "alice")
        _claim(state, bundle, "T2", "bob")
        state.submit_result(
            bundle, "T1", generation=b1["generation"], owner="alice",
            result=dict(RESULT_T1), session="w",
        )
        st, b2 = _binding(state, bundle, "T2")
        with pytest.raises(state.SpliceError) as exc:
            state.submit_result(
                bundle, "T2", generation=b2["generation"], owner="bob",
                result=dict(RESULT_T1), session="w",
            )
        assert exc.value.code == "verification_busy"

    def test_submit_requires_result(self, bundle) -> None:
        state = _state()
        b = _claim(state, bundle, "T1", "alice")
        with pytest.raises(state.SpliceError) as exc:
            state.submit_result(
                bundle, "T1", generation=b["generation"], owner="alice",
                result={}, session="w",
            )
        assert exc.value.code == "missing_result"


class TestVerifyCoordinatorOnly:
    def test_worker_verify_refused_not_coordinator(self, bundle) -> None:
        state = _state()
        b = _claim(state, bundle, "T1", "alice")
        state.submit_result(
            bundle, "T1", generation=b["generation"], owner="alice",
            result=dict(RESULT_T1), session="w",
        )
        with pytest.raises(state.SpliceError) as exc:
            state.verify_result(
                bundle, "T1", generation=b["generation"],
                verdict="pass", coordinator=False, session="w",
            )
        assert exc.value.code == "not_coordinator"

    def test_verify_pass_moves_to_integration_ready(self, bundle) -> None:
        state = _state()
        b = _claim(state, bundle, "T1", "alice")
        state.submit_result(
            bundle, "T1", generation=b["generation"], owner="alice",
            result=dict(RESULT_T1), session="w",
        )
        st = state.verify_result(
            bundle, "T1", generation=b["generation"],
            verdict="pass", coordinator=True, session="coord",
        )
        sub = next(x for x in st.task_bindings if x["id"] == "T1")
        assert sub["place"] == "work_integration_ready"
        # test slot freed — a second task can now submit
        b2 = next(x for x in st.task_bindings if x["id"] == "T2")
        assert b2["place"] == "work_pending"


class TestIntegrateSerialized:
    def _to_ready(self, state, base, task_id, owner):
        b = _claim(state, base, task_id, owner)
        state.submit_result(
            base, task_id, generation=b["generation"], owner=owner,
            result=dict(RESULT_T1), session="w",
        )
        st = state.verify_result(
            base, task_id, generation=b["generation"],
            verdict="pass", coordinator=True, session="coord",
        )
        return next(x for x in st.task_bindings if x["id"] == task_id)

    def test_worker_integrate_refused_even_own_result(self, bundle) -> None:
        state = _state()
        ready = self._to_ready(state, bundle, "T1", "alice")
        with pytest.raises(state.SpliceError) as exc:
            state.integrate_start(
                bundle, "T1", generation=ready["generation"],
                coordinator=False, session="alice",
            )
        assert exc.value.code == "not_coordinator"

    def test_integrate_serialized_second_start_busy(self, bundle) -> None:
        state = _state()
        r1 = self._to_ready(state, bundle, "T1", "alice")
        # free the test lane so T2 can also reach ready
        state.integrate_start(
            bundle, "T1", generation=r1["generation"],
            coordinator=True, session="coord",
        )
        # T2 path: claim→submit→verify needs test slot free (verify freed it? no —
        # T1 is integrating, test slot was freed at verify; submit T2 now OK)
        b2 = _claim(state, bundle, "T2", "bob")
        state.submit_result(
            bundle, "T2", generation=b2["generation"], owner="bob",
            result=dict(RESULT_T1), session="w",
        )
        state.verify_result(
            bundle, "T2", generation=b2["generation"],
            verdict="pass", coordinator=True, session="coord",
        )
        st, b2r = _binding(state, bundle, "T2")
        with pytest.raises(state.SpliceError) as exc:
            state.integrate_start(
                bundle, "T2", generation=b2r["generation"],
                coordinator=True, session="coord",
            )
        assert exc.value.code == "integration_busy"

    def test_integrate_fail_returns_to_pending_objective_unsatisfied(
        self, bundle
    ) -> None:
        state = _state()
        r1 = self._to_ready(state, bundle, "T1", "alice")
        state.integrate_start(
            bundle, "T1", generation=r1["generation"],
            coordinator=True, session="coord",
        )
        st = state.integrate_finish(
            bundle, "T1", generation=r1["generation"],
            verdict="fail", coordinator=True,
            detail="combined e2e fails with T2", session="coord",
        )
        sub = next(x for x in st.task_bindings if x["id"] == "T1")
        assert sub["place"] == "work_pending"
        assert "combined" in str(sub.get("block_reason", "")).lower() or sub.get(
            "block_reason"
        )
        # objective unsatisfied: nothing done
        assert st.live_marking.get("work_done", 0) == 0

    def test_stale_generation_cannot_publish(self, bundle) -> None:
        state = _state()
        b = _claim(state, bundle, "T1", "alice")
        gen1 = b["generation"]
        state.transfer_task(bundle, "T1", owner="bob", session="coord")
        _, moved = _binding(state, bundle, "T1")
        assert moved["generation"] == gen1 + 1
        with pytest.raises(state.SpliceError) as exc:
            state.submit_result(
                bundle, "T1", generation=gen1, owner="alice",
                result=dict(RESULT_T1), session="w",
            )
        assert exc.value.code == "stale_generation"


class TestCliRoundTrip:
    def test_cli_submit_envelope(self, bundle) -> None:
        from net import cli  # noqa: PLC0415

        state = _state()
        b = _claim(state, bundle, "T1", "alice")
        import argparse

        args = argparse.Namespace(
            task_id="T1",
            generation=b["generation"],
            owner="alice",
            mutation='{"head_commit": "def456", "patch_digest": "sha256:abc"}',
            reasoning="worker done",
            session="w",
            expected_revision=None,
            command_id=None,
        )
        env, code = cli._submit(bundle, args)
        assert code == 0
        assert env["task"]["place"] == "work_verifying"
