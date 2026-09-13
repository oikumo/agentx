"""Evidence + dependency completion — feature_085.evidence_dependency_completion
(T5-7 3C, NEXT_STEP §12, mh8 strict order after 079/080/081/082/083/084).

Goldens: declare_deps stamps pinned upstream versions (gen-fenced);
verify pass with satisfied deps → integration_ready; verify with upstream
pending → dependency_unsatisfied; verify with upstream done but head
mismatch → dependency_stale; upstream repair between verify and integrate
→ integrate_finish dependency_stale (the §12.2 race); evidence_digest
mismatch → stale even when head matches (digest is the fence); fail
verdicts bypass dep checks; objective_status accepted only when all done
+ satisfied; CLI round-trip; stale_generation on declare after transfer.

Hermetic via OMT_NET_DIR / OMT_LEDGER_PATH / OMT_COORDINATION_ROOT (tmp_path).

Canary: new goldens for feature_085 only (scope: tests).
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
            "T4": ["src/up"],
            "T9": ["src/down"],
        },
    )
    return tmp_path


def _binding(state, base, task_id):
    st = state.load(base)
    return st, next(b for b in st.task_bindings if b["id"] == task_id)


def _claim(state, base, task_id, owner):
    st = state.claim_task(base, task_id, owner=owner, session="w")
    return next(b for b in st.task_bindings if b["id"] == task_id)


def _full_integrate_upstream(state, base, task_id, owner, head, patch, base_c="abc123"):
    """Claim → submit → verify → integrate_start → integrate_finish(pass)."""
    b = _claim(state, base, task_id, owner)
    gen = b["generation"]
    state.submit_result(
        base, task_id, generation=gen, owner=owner,
        result={"head_commit": head, "patch_digest": patch, "base_commit": base_c,
                "local_checks": [{"name": "pytest", "result": "pass"}]},
        session="w",
    )
    state.verify_result(base, task_id, generation=gen, verdict="pass",
                        coordinator=True, session="c")
    state.integrate_start(base, task_id, generation=gen, coordinator=True, session="c")
    st = state.integrate_finish(base, task_id, generation=gen, verdict="pass",
                                coordinator=True, session="c")
    done = next(x for x in st.task_bindings if x["id"] == task_id)
    return done


RESULT_T9 = {
    "head_commit": "t9head",
    "patch_digest": "sha256:t9",
    "base_commit": "abc123",
    "local_checks": [{"name": "pytest focused", "result": "pass"}],
}


class TestDeclareDeps:
    def test_declare_stamps_pinned_versions(self, bundle) -> None:
        state = _state()
        b = _claim(state, bundle, "T9", "bob")
        gen = b["generation"]
        deps = [{"need": "policy-contract", "task_id": "T4",
                 "head_commit": "def456", "evidence_digest": "sha256:ev4"}]
        st = state.declare_dependencies(bundle, "T9", generation=gen, deps=deps, session="w")
        got = next(x for x in st.task_bindings if x["id"] == "T9")
        assert got["deps"] == deps

    def test_declare_wrong_generation_refuses(self, bundle) -> None:
        state = _state()
        b = _claim(state, bundle, "T9", "bob")
        with pytest.raises(state.SpliceError) as exc:
            state.declare_dependencies(bundle, "T9", generation=int(b["generation"]) + 99,
                                       deps=[{"need": "x", "task_id": "T4"}],
                                       session="w")
        assert exc.value.code == "stale_generation"

    def test_declare_malformed_refuses(self, bundle) -> None:
        state = _state()
        b = _claim(state, bundle, "T9", "bob")
        with pytest.raises(state.SpliceError) as exc:
            state.declare_dependencies(bundle, "T9", generation=b["generation"],
                                       deps=[{"need": "x"}], session="w")
        assert exc.value.code == "invalid_deps"


class TestVerifyGates:
    def test_verify_pass_satisfied_goes_ready(self, bundle) -> None:
        state = _state()
        done4 = _full_integrate_upstream(state, bundle, "T4", "alice", "def456", "sha256:abc")
        ev4 = done4["submission"]["evidence_digest"]
        b9 = _claim(state, bundle, "T9", "bob")
        state.declare_dependencies(
            bundle, "T9", generation=b9["generation"],
            deps=[{"need": "policy-contract", "task_id": "T4",
                   "head_commit": "def456", "evidence_digest": ev4}],
            session="w",
        )
        state.submit_result(bundle, "T9", generation=b9["generation"], owner="bob",
                            result=dict(RESULT_T9), session="w")
        st = state.verify_result(bundle, "T9", generation=b9["generation"],
                                 verdict="pass", coordinator=True, session="c")
        got = next(x for x in st.task_bindings if x["id"] == "T9")
        assert got["place"] == "work_integration_ready"

    def test_verify_pass_upstream_pending_unsatisfied(self, bundle) -> None:
        state = _state()
        b9 = _claim(state, bundle, "T9", "bob")
        state.declare_dependencies(
            bundle, "T9", generation=b9["generation"],
            deps=[{"need": "policy-contract", "task_id": "T4",
                   "head_commit": "def456", "evidence_digest": "sha256:ev4"}],
            session="w",
        )
        state.submit_result(bundle, "T9", generation=b9["generation"], owner="bob",
                            result=dict(RESULT_T9), session="w")
        with pytest.raises(state.SpliceError) as exc:
            state.verify_result(bundle, "T9", generation=b9["generation"],
                                verdict="pass", coordinator=True, session="c")
        assert exc.value.code == "dependency_unsatisfied"
        # no state move — still verifying
        _, still = _binding(state, bundle, "T9")
        assert still["place"] == "work_verifying"

    def test_verify_pass_head_mismatch_stale(self, bundle) -> None:
        state = _state()
        done4 = _full_integrate_upstream(state, bundle, "T4", "alice", "def456", "sha256:abc")
        ev4 = done4["submission"]["evidence_digest"]
        assert ev4  # pinned, must exist
        b9 = _claim(state, bundle, "T9", "bob")
        state.declare_dependencies(
            bundle, "T9", generation=b9["generation"],
            deps=[{"need": "policy-contract", "task_id": "T4",
                   "head_commit": "STALE-HEAD", "evidence_digest": ev4}],
            session="w",
        )
        state.submit_result(bundle, "T9", generation=b9["generation"], owner="bob",
                            result=dict(RESULT_T9), session="w")
        with pytest.raises(state.SpliceError) as exc:
            state.verify_result(bundle, "T9", generation=b9["generation"],
                                verdict="pass", coordinator=True, session="c")
        assert exc.value.code == "dependency_stale"
        assert "STALE-HEAD" in str(exc.value) or "def456" in str(exc.value)

    def test_verify_pass_digest_mismatch_stale_even_when_head_matches(self, bundle) -> None:
        state = _state()
        _full_integrate_upstream(state, bundle, "T4", "alice", "def456", "sha256:abc")
        b9 = _claim(state, bundle, "T9", "bob")
        state.declare_dependencies(
            bundle, "T9", generation=b9["generation"],
            deps=[{"need": "policy-contract", "task_id": "T4",
                   "head_commit": "def456", "evidence_digest": "sha256:WRONG"}],
            session="w",
        )
        state.submit_result(bundle, "T9", generation=b9["generation"], owner="bob",
                            result=dict(RESULT_T9), session="w")
        with pytest.raises(state.SpliceError) as exc:
            state.verify_result(bundle, "T9", generation=b9["generation"],
                                verdict="pass", coordinator=True, session="c")
        assert exc.value.code == "dependency_stale"

    def test_verify_fail_bypasses_dep_checks(self, bundle) -> None:
        state = _state()
        b9 = _claim(state, bundle, "T9", "bob")
        state.declare_dependencies(
            bundle, "T9", generation=b9["generation"],
            deps=[{"need": "policy-contract", "task_id": "T4",
                   "head_commit": "def456", "evidence_digest": "sha256:ev4"}],
            session="w",
        )
        state.submit_result(bundle, "T9", generation=b9["generation"], owner="bob",
                            result=dict(RESULT_T9), session="w")
        st = state.verify_result(bundle, "T9", generation=b9["generation"],
                                 verdict="fail", coordinator=True,
                                 detail="local checks failed", session="c")
        got = next(x for x in st.task_bindings if x["id"] == "T9")
        assert got["place"] == "work_pending"


class TestIntegrateRace:
    def test_integrate_finish_stale_after_upstream_repair(self, bundle) -> None:
        """§12.2 race: T9 verified vs T4@abc, T4 repairs to def, T9 integrate → stale."""
        state = _state()
                # T4 v1 done
        done_v1 = _full_integrate_upstream(state, bundle, "T4", "alice", "aaa111", "sha256:v1")
        ev_v1 = done_v1["submission"]["evidence_digest"]
        # T9 declares against v1, submits, verifies (satisfied at verify time)
        b9 = _claim(state, bundle, "T9", "bob")
        state.declare_dependencies(
            bundle, "T9", generation=b9["generation"],
            deps=[{"need": "policy-contract", "task_id": "T4",
                   "head_commit": "aaa111", "evidence_digest": ev_v1}],
            session="w",
        )
        state.submit_result(bundle, "T9", generation=b9["generation"], owner="bob",
                            result=dict(RESULT_T9), session="w")
        state.verify_result(bundle, "T9", generation=b9["generation"],
                            verdict="pass", coordinator=True, session="c")
        # Upstream repair BEFORE T9 enters the serialized lane (T9 holds no
        # integration slot while integration_ready, so T4 can re-integrate).→active→lane again. Simulate a
        # second generation by resetting the done binding to pending (test-only
        # reset keeps the hermetic bundle small; production repair is re-claim).
        st = state.load(bundle)
        idx = next(i for i, x in enumerate(st.task_bindings) if x["id"] == "T4")
        repaired = dict(st.task_bindings[idx])
        repaired["place"] = "work_pending"
        repaired.pop("owner", None)
        st.task_bindings[idx] = repaired
        st.live_marking["work_done"] -= 1
        st.live_marking["work_pending"] = st.live_marking.get("work_pending", 0) + 1
        state.save(bundle, st)
        _full_integrate_upstream(state, bundle, "T4", "alice", "bbb222", "sha256:v2")
        state.integrate_start(bundle, "T9", generation=b9["generation"],
                              coordinator=True, session="c")
        # T9 integrate now sees a newer accepted T4 → stale, stays integrating
        with pytest.raises(state.SpliceError) as exc:
            state.integrate_finish(bundle, "T9", generation=b9["generation"],
                                   verdict="pass", coordinator=True, session="c")
        assert exc.value.code == "dependency_stale"
        _, still = _binding(state, bundle, "T9")
        assert still["place"] == "work_integrating"

    def test_integrate_fail_bypasses_dep_checks(self, bundle) -> None:
        state = _state()
        done4 = _full_integrate_upstream(state, bundle, "T4", "alice", "def456", "sha256:abc")
        ev4 = done4["submission"]["evidence_digest"]
        b9 = _claim(state, bundle, "T9", "bob")
        state.declare_dependencies(
            bundle, "T9", generation=b9["generation"],
            deps=[{"need": "x", "task_id": "T4",
                   "head_commit": "def456", "evidence_digest": ev4}],
            session="w",
        )
        state.submit_result(bundle, "T9", generation=b9["generation"], owner="bob",
                            result=dict(RESULT_T9), session="w")
        state.verify_result(bundle, "T9", generation=b9["generation"],
                            verdict="pass", coordinator=True, session="c")
        state.integrate_start(bundle, "T9", generation=b9["generation"],
                              coordinator=True, session="c")
        st = state.integrate_finish(bundle, "T9", generation=b9["generation"],
                                    verdict="fail", coordinator=True,
                                    detail="combined acceptance failed", session="c")
        got = next(x for x in st.task_bindings if x["id"] == "T9")
        assert got["place"] == "work_pending"


class TestStatusReads:
    def test_dependency_status_reports_satisfied_stale_unsatisfied(self, bundle) -> None:
        state = _state()
        # unsatisfied: T4 still pending
        b9 = _claim(state, bundle, "T9", "bob")
        state.declare_dependencies(
            bundle, "T9", generation=b9["generation"],
            deps=[{"need": "policy-contract", "task_id": "T4",
                   "head_commit": "def456", "evidence_digest": "sha256:ev4"}],
            session="w",
        )
        rep = state.dependency_status(bundle, "T9")
        assert rep["deps"][0]["status"] == "unsatisfied"
        # (integrate T4 now — T9 stays active, no conflict: disjoint scopes)
        # T4 is still pending here (never claimed), so claim it.
        b4 = _claim(state, bundle, "T4", "alice")
        state.submit_result(bundle, "T4", generation=b4["generation"], owner="alice",
                            result={"head_commit": "def456", "patch_digest": "sha256:abc",
                                    "base_commit": "abc123",
                                    "local_checks": [{"name": "pytest", "result": "pass"}]},
                            session="w")
        state.verify_result(bundle, "T4", generation=b4["generation"],
                            verdict="pass", coordinator=True, session="c")
        state.integrate_start(bundle, "T4", generation=b4["generation"],
                              coordinator=True, session="c")
        state.integrate_finish(bundle, "T4", generation=b4["generation"],
                               verdict="pass", coordinator=True, session="c")
        st4, b4done = _binding(state, bundle, "T4")
        ev_now = b4done["submission"]["evidence_digest"]
        # re-pin T9 to the now-current versions → satisfied
        state.declare_dependencies(
            bundle, "T9", generation=b9["generation"],
            deps=[{"need": "policy-contract", "task_id": "T4",
                   "head_commit": "def456", "evidence_digest": ev_now}],
            session="w",
        )
        rep2 = state.dependency_status(bundle, "T9")
        assert rep2["deps"][0]["status"] == "satisfied"

    def test_objective_status_accepted_only_when_all_done_satisfied(self, bundle) -> None:
        state = _state()
        _full_integrate_upstream(state, bundle, "T4", "alice", "def456", "sha256:abc")
        st4, b4done = _binding(state, bundle, "T4")
        ev4 = b4done["submission"]["evidence_digest"]
        b9 = _claim(state, bundle, "T9", "bob")
        state.declare_dependencies(
            bundle, "T9", generation=b9["generation"],
            deps=[{"need": "policy-contract", "task_id": "T4",
                   "head_commit": "def456", "evidence_digest": ev4}],
            session="w",
        )
        # T9 not done yet → objective not accepted
        rep = state.objective_status(bundle, ["T4", "T9"])
        assert rep["accepted"] is False
        # finish T9 through the lane with satisfied deps
        state.submit_result(bundle, "T9", generation=b9["generation"], owner="bob",
                            result=dict(RESULT_T9), session="w")
        state.verify_result(bundle, "T9", generation=b9["generation"],
                            verdict="pass", coordinator=True, session="c")
        state.integrate_start(bundle, "T9", generation=b9["generation"],
                              coordinator=True, session="c")
        state.integrate_finish(bundle, "T9", generation=b9["generation"],
                               verdict="pass", coordinator=True, session="c")
        rep2 = state.objective_status(bundle, ["T4", "T9"])
        assert rep2["accepted"] is True
        assert rep2["tasks"]["T4"]["place"] == "work_done"
        assert rep2["tasks"]["T9"]["place"] == "work_done"


class TestFencingAndCli:
    def test_declare_after_transfer_refuses_stale(self, bundle) -> None:
        state = _state()
        b9 = _claim(state, bundle, "T9", "bob")
        old_gen = b9["generation"]
        state.transfer_task(bundle, "T9", owner="carol", session="c")
        with pytest.raises(state.SpliceError) as exc:
            state.declare_dependencies(bundle, "T9", generation=old_gen,
                                       deps=[{"need": "x", "task_id": "T4"}],
                                       session="w")
        assert exc.value.code == "stale_generation"

    def test_cli_round_trip_with_deps(self, bundle, monkeypatch, capsys) -> None:
        import json

        state = _state()
        from net import cli

        done4 = _full_integrate_upstream(state, bundle, "T4", "alice", "def456", "sha256:abc")
        ev4 = done4["submission"]["evidence_digest"]
        b9 = _claim(state, bundle, "T9", "bob")
        gen = b9["generation"]

        def _run(argv):
            monkeypatch.setattr(sys, "argv", ["omt_net", *argv])
            rc = cli.main()
            out = capsys.readouterr().out.strip().splitlines()[-1]
            return rc, json.loads(out)

        rc, env = _run(["declare-deps", "--task-id", "T9", "--generation", str(gen),
                        "--mutation", json.dumps([{"need": "policy-contract", "task_id": "T4",
                                                   "head_commit": "def456",
                                                   "evidence_digest": ev4}]),
                        "--reasoning", "t", "--session", "w"])
        assert rc == 0 and env["ok"] is True
        rc, env = _run(["submit", "--task-id", "T9", "--generation", str(gen),
                        "--owner", "bob", "--mutation", json.dumps(dict(RESULT_T9)),
                        "--reasoning", "t", "--session", "w"])
        assert rc == 0
        rc, env = _run(["verify", "--task-id", "T9", "--generation", str(gen),
                        "--verdict", "pass", "--coordinator",
                        "--reasoning", "t", "--session", "c"])
        assert rc == 0 and env["ok"] is True
        rc, env = _run(["deps", "--task-id", "T9",
                        "--reasoning", "t", "--session", "c"])
        assert rc == 0 and env["deps"][0]["status"] == "satisfied"
