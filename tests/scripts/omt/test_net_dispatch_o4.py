"""O4 concurrent dispatch runtime goldens — feature_114.concurrent_dispatch_runtime.

Planner (dispatch_runtime.plan_dispatch: ordering, stable refusal codes,
deterministic worktree/lease/batch derivation, describe/plan_to_dict) +
state layer (plan_dispatch_view preview/fail-open + dispatch_claims atomic
join with ledger net_claim/net_fire). Hermetic via OMT_NET_DIR /
OMT_LEDGER_PATH / OMT_COORDINATION_ROOT (tmp_path); the live ledger is
never read (feature_051 isolation — a live scope=all omt_skip would flip
the planner matrix via the break-glass fallback only on the live path).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "scripts" / "omt"
sys.path.insert(0, str(SCRIPTS_DIR))

SLOTS = {"used": 0, "cap": 2, "free": 2}
LANE_FREE = {"used": 0, "cap": 1, "free": 1}


def _dispatch():
    from net import dispatch_runtime  # noqa: PLC0415
    return dispatch_runtime


def _state():
    from net import state  # noqa: PLC0415
    return state


def _seed_env(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("OMT_NET_DIR", str(tmp_path))
    monkeypatch.setenv("OMT_LEDGER_PATH", str(tmp_path / "ledger.jsonl"))
    monkeypatch.setenv("OMT_COORDINATION_ROOT", str(tmp_path / "coord"))


def _pool_bundle(base: Path, state, tasks=(("t-1", ["src/a.py"]),),
                 active=(), slots: int = 2) -> None:
    state.init_empty(base)
    st = state.load(base)
    for place, tokens in (
        ("work_pending", len(tasks)),
        ("work_active", len(active)),
        ("work_done", 0),
        ("agent_attention", 1),
        ("feature_ready", 1),
        # Real place (feature_082 pool template): the marking token
        # round-trips through save/load and the join enforces it. No arcs
        # here → _fire_pool_move takes the labeled code-managed fallback.
        ("worker_slots", slots),
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
        "work_active": len(active),
        "work_done": 0,
        "agent_attention": 1,
        "feature_ready": 1,
        "worker_slots": slots,
    }
    st.task_bindings = (
        [{"id": tid, "place": "work_pending", "generation": 0,
          "scope": list(scope)} for tid, scope in tasks]
        + [{"id": tid, "place": "work_active", "generation": 1,
            "owner": "o4", "scope": list(scope)} for tid, scope in active]
    )
    state.save(base, st)


@pytest.fixture()
def bundle(tmp_path, monkeypatch):
    _seed_env(monkeypatch, tmp_path)
    _pool_bundle(tmp_path, _state())
    return tmp_path


class TestPlanEmpty:
    def test_empty_refuses(self) -> None:
        dr = _dispatch()
        with pytest.raises(dr.PlanRefused, match="empty_plan"):
            dr.plan_dispatch(
                claims=[], enabled=[], parallel=[],
                worker_slots={"used": 0, "cap": 2, "free": 2},
                verification={"used": 0, "cap": 1, "free": 1},
                integration={"used": 0, "cap": 1, "free": 1},
                work_pending=0, work_active=0, revision=0,
            )


class TestPlanCompose:
    def test_orders_verification_integration_general(self) -> None:
        dr = _dispatch()
        plan = dr.plan_dispatch(
            claims=[
                {"claim": "c-g", "task_id": "t-g", "lane": "general"},
                {"claim": "c-i", "task_id": "t-i", "lane": "integration"},
                {"claim": "c-v", "task_id": "t-v", "lane": "verification"},
            ],
            enabled=[], parallel=[],
            worker_slots={"used": 0, "cap": 3, "free": 3},
            verification=dict(LANE_FREE), integration=dict(LANE_FREE),
            work_pending=0, work_active=0, revision=60,
        )
        assert [t.task_id for t in plan.tasks] == ["t-v", "t-i", "t-g"]
        assert [t.lane for t in plan.tasks] == ["verification", "integration", "general"]
        assert plan.revision == 60

    def test_orders_general_by_task_id(self) -> None:
        dr = _dispatch()
        plan = dr.plan_dispatch(
            claims=[
                {"claim": "c-b", "task_id": "t-b", "lane": "general"},
                {"claim": "c-a", "task_id": "t-a", "lane": "general"},
            ],
            enabled=[], parallel=[],
            worker_slots=dict(SLOTS),
            verification=dict(LANE_FREE), integration=dict(LANE_FREE),
            work_pending=0, work_active=0, revision=60,
        )
        assert [t.task_id for t in plan.tasks] == ["t-a", "t-b"]

    def test_unknown_lane_falls_back_general(self) -> None:
        dr = _dispatch()
        plan = dr.plan_dispatch(
            claims=[{"claim": "c-x", "task_id": "t-x", "lane": "nope"}],
            enabled=[], parallel=[],
            worker_slots=dict(SLOTS),
            verification=dict(LANE_FREE), integration=dict(LANE_FREE),
            work_pending=0, work_active=0, revision=60,
        )
        assert plan.tasks[0].lane == "general"


class TestPlanRefusals:
    def _kw(self, **over):
        kw = dict(
            enabled=[], parallel=[],
            worker_slots=dict(SLOTS),
            verification=dict(LANE_FREE), integration=dict(LANE_FREE),
            work_pending=0, work_active=0, revision=60,
        )
        kw.update(over)
        return kw

    def test_unknown_claim(self) -> None:
        dr = _dispatch()
        with pytest.raises(dr.PlanRefused, match="unknown_claim"):
            dr.plan_dispatch(
                claims=[{"task_id": "t-x"}], **self._kw())

    def test_dup_claim(self) -> None:
        dr = _dispatch()
        with pytest.raises(dr.PlanRefused, match="dup_claim:t-x"):
            dr.plan_dispatch(
                claims=[
                    {"claim": "c-1", "task_id": "t-x", "lane": "general"},
                    {"claim": "c-2", "task_id": "t-x", "lane": "general"},
                ],
                **self._kw())

    def test_worker_capacity_exhausted(self) -> None:
        dr = _dispatch()
        with pytest.raises(dr.PlanRefused, match="worker_capacity_exhausted"):
            dr.plan_dispatch(
                claims=[
                    {"claim": f"c-{n}", "task_id": f"t-{n}", "lane": "general"}
                    for n in range(3)
                ],
                **self._kw())

    def test_verification_lane_busy(self) -> None:
        dr = _dispatch()
        with pytest.raises(dr.PlanRefused, match="verification_lane_busy"):
            dr.plan_dispatch(
                claims=[
                    {"claim": "c-1", "task_id": "t-1", "lane": "verification"},
                    {"claim": "c-2", "task_id": "t-2", "lane": "verification"},
                ],
                **self._kw())

    def test_integration_lane_busy(self) -> None:
        dr = _dispatch()
        with pytest.raises(dr.PlanRefused, match="integration_lane_busy"):
            dr.plan_dispatch(
                claims=[
                    {"claim": "c-1", "task_id": "t-1", "lane": "integration"},
                    {"claim": "c-2", "task_id": "t-2", "lane": "integration"},
                ],
                **self._kw())

    def test_wip_cap_exceeded(self) -> None:
        dr = _dispatch()
        with pytest.raises(dr.PlanRefused, match="wip_cap_exceeded"):
            dr.plan_dispatch(
                claims=[
                    {"claim": "c-1", "task_id": "t-1", "lane": "general"},
                    {"claim": "c-2", "task_id": "t-2", "lane": "general"},
                ],
                **self._kw(work_pending=14, work_active=0))


class TestPlanDeterminism:
    def test_batch_id_stable_per_revision(self) -> None:
        dr = _dispatch()
        kw = dict(
            claims=[
                {"claim": "c-b", "task_id": "t-b", "lane": "general"},
                {"claim": "c-a", "task_id": "t-a", "lane": "verification"},
            ],
            enabled=[], parallel=[],
            worker_slots=dict(SLOTS),
            verification=dict(LANE_FREE), integration=dict(LANE_FREE),
            work_pending=0, work_active=0,
        )
        p60 = dr.plan_dispatch(revision=60, **kw)
        p60b = dr.plan_dispatch(revision=60, **kw)
        p61 = dr.plan_dispatch(revision=61, **kw)
        assert p60.batch_id == p60b.batch_id
        assert p60.batch_id != p61.batch_id
        assert len(p60.batch_id) == 12
        (first, second) = p60.tasks
        assert first.worktree == f"wt-{p60.batch_id[:6]}-t-a"
        assert first.lease == f"lease-{p60.batch_id}-00"
        assert second.lease == f"lease-{p60.batch_id}-01"

    def test_describe_and_plan_dict_shape(self) -> None:
        dr = _dispatch()
        plan = dr.plan_dispatch(
            claims=[
                {"claim": "c-v", "task_id": "t-v", "lane": "verification"},
                {"claim": "c-g", "task_id": "t-g", "lane": "general"},
            ],
            enabled=[], parallel=[],
            worker_slots=dict(SLOTS),
            verification=dict(LANE_FREE), integration=dict(LANE_FREE),
            work_pending=0, work_active=0, revision=60,
        )
        assert dr.describe_plan(plan) == (
            f"dispatch 2 tasks rev 60 batch {plan.batch_id} lanes 1/0/1")
        doc = dr.plan_to_dict(plan)
        assert set(doc) == {"tasks", "wip", "revision", "batch_id", "summary"}
        assert [t["task_id"] for t in doc["tasks"]] == ["t-v", "t-g"]
        assert set(doc["tasks"][0]) == {"claim", "task_id", "lane", "worktree", "lease"}
        assert doc["wip"] == {"pending": 0, "active": 0, "cap": 15}
        assert doc["summary"] == dr.describe_plan(plan)


class TestPreviewView:
    def test_resolves_pending_bindings(self, bundle) -> None:
        state = _state()
        view = state.plan_dispatch_view(bundle)
        assert [t["task_id"] for t in view["plan"]] == ["t-1"]
        task = view["plan"][0]
        assert task["lane"] == "general"
        assert task["worktree"].startswith("wt-")
        assert task["lease"].startswith(f"lease-{view['batch_id']}-")
        assert view["revision"] == 0
        assert view["summary"].startswith("dispatch 1 tasks rev 0 batch ")

    def test_caller_claims_lane_plan(self, bundle) -> None:
        state = _state()
        view = state.plan_dispatch_view(
            bundle,
            claims=[
                {"claim": "c-v", "task_id": "t-v", "lane": "verification"},
                {"claim": "c-i", "task_id": "t-i", "lane": "integration"},
            ],
        )
        assert [t["lane"] for t in view["plan"]] == ["verification", "integration"]

    def test_refused_stays_fail_open(self, tmp_path, monkeypatch) -> None:
        state = _state()
        _seed_env(monkeypatch, tmp_path)
        _pool_bundle(
            tmp_path, state,
            tasks=(("t-3", ["src/c.py"]),),
            active=(("t-1", ["src/a.py"]), ("t-2", ["src/b.py"])),
        )
        view = state.plan_dispatch_view(tmp_path)
        assert view["plan"] == []
        assert view["refused"] == "worker_capacity_exhausted"

    def test_stale_rev_raises(self, bundle) -> None:
        state = _state()
        with pytest.raises(state.SpliceError) as e:
            state.plan_dispatch_view(bundle, expected_revision=999)
        assert e.value.code == "stale_revision"
        assert "re-render" in str(e.value)


def _read_ledger(tmp_path: Path) -> list[dict]:
    rows = []
    ledger = tmp_path / "ledger.jsonl"
    if ledger.exists():
        for line in ledger.read_text(encoding="utf-8").strip().splitlines():
            if line.strip():
                rows.append(json.loads(line))
    return rows


class TestDispatchJoin:
    def test_join_commits_one_revision(self, bundle, tmp_path) -> None:
        state = _state()
        view = state.plan_dispatch_view(bundle)
        st, report = state.dispatch_claims(
            bundle, plan=view, reasoning="o4", session="o4",
            expected_revision=0,
        )
        assert st.revision == 1
        assert report["batch_id"] == view["batch_id"]
        (info,) = report["tasks"]
        assert info["task_id"] == "t-1"
        assert info["owner"] == "o4" and info["generation"] == 1
        assert info["worktree"].startswith("wt-")
        assert report["lanes"] == {"verification": 0, "integration": 0, "general": 1}
        assert report["wip"] == {"pending": 0, "active": 0, "cap": 15}
        live = state.load(bundle).live_marking
        assert (live["work_pending"], live["work_active"], live["work_done"]) == (0, 0, 1)
        assert live["worker_slots"] == 2
        b = next(x for x in state.load(bundle).task_bindings if x["id"] == "t-1")
        assert b["place"] == "work_done"
        assert b["workspace"]["worktree"] == info["worktree"]

    def test_ledger_carries_batch(self, bundle, tmp_path) -> None:
        state = _state()
        view = state.plan_dispatch_view(bundle)
        _, report = state.dispatch_claims(
            bundle, plan=view, reasoning="o4", session="o4",
            expected_revision=0,
        )
        rows = _read_ledger(tmp_path)
        claims = [r for r in rows if r.get("kind") == "net_claim"]
        fires = [r for r in rows if r.get("kind") == "net_fire"]
        assert len(claims) == 1 and len(fires) == 1
        assert claims[0]["task_id"] == "t-1"
        assert claims[0]["batch_id"] == report["batch_id"]
        assert claims[0]["transition"] == "work_start"
        (fire,) = fires
        assert fire["batch_id"] == report["batch_id"]
        assert fire["transition"] == "work_complete"
        assert fire["dispatch_plan"] == view["plan"]
        assert len(fire["progress"]) == 1
        prog = fire["progress"][0]
        assert prog["task_id"] == "t-1"
        assert {"push", "freshness", "projection"} <= set(prog)
        assert report["batch_id"] in fire["reasoning"]

    def test_stale_plan_refuses_atomically(self, bundle, tmp_path) -> None:
        state = _state()
        view = state.plan_dispatch_view(bundle)
        bad = dict(view, revision=999)
        with pytest.raises(state.SpliceError) as e:
            state.dispatch_claims(
                bundle, plan=bad, reasoning="o4", session="o4",
                expected_revision=0,
            )
        assert e.value.code == "stale_revision"
        st = state.load(bundle)
        assert st.revision == 0
        assert st.live_marking["work_pending"] == 1
        b = next(x for x in st.task_bindings if x["id"] == "t-1")
        assert b["place"] == "work_pending"

    def test_unknown_task_refuses_with_zero_partial_marks(self, bundle, tmp_path) -> None:
        state = _state()
        view = state.plan_dispatch_view(bundle)
        bad_tasks = list(view["plan"]) + [{
            "claim": "c-zz", "task_id": "nope", "lane": "general",
            "worktree": "wt-x-nope", "lease": "lease-x-01",
        }]
        bad = dict(view, tasks=bad_tasks)
        with pytest.raises(state.SpliceError) as e:
            state.dispatch_claims(
                bundle, plan=bad, reasoning="o4", session="o4",
                expected_revision=0,
            )
        assert e.value.code == "task_not_found"
        st = state.load(bundle)
        assert st.revision == 0
        assert st.live_marking["work_pending"] == 1
        b = next(x for x in st.task_bindings if x["id"] == "t-1")
        assert (b["place"], b["generation"]) == ("work_pending", 0)

    def test_second_dispatch_refuses_not_pending(self, bundle, tmp_path) -> None:
        state = _state()
        view = state.plan_dispatch_view(bundle)
        state.dispatch_claims(
            bundle, plan=view, reasoning="o4", session="o4",
            expected_revision=0,
        )
        # Re-plan at the new live revision so the join reaches task
        # validation (a stale plan would refuse stale_revision first).
        view2 = dict(view, revision=1)
        with pytest.raises(state.SpliceError) as e:
            state.dispatch_claims(
                bundle, plan=view2, reasoning="o4", session="o4",
                expected_revision=1,
            )
        assert e.value.code == "task_not_pending"

    def test_scope_conflict_refuses(self, tmp_path, monkeypatch) -> None:
        state = _state()
        _seed_env(monkeypatch, tmp_path)
        _pool_bundle(
            tmp_path, state,
            tasks=(("t-1", ["README.md"]), ("t-2", ["README.md"])),
        )
        view = state.plan_dispatch_view(
            tmp_path,
            claims=[
                {"claim": "c-1", "task_id": "t-1", "lane": "general"},
                {"claim": "c-2", "task_id": "t-2", "lane": "general"},
            ],
        )
        assert len(view["plan"]) == 2
        with pytest.raises(state.SpliceError) as e:
            state.dispatch_claims(
                tmp_path, plan=view, reasoning="o4", session="o4",
                expected_revision=0,
            )
        assert e.value.code == "scope_conflict"

    def test_slots_token_refuses(self, tmp_path, monkeypatch) -> None:
        state = _state()
        _seed_env(monkeypatch, tmp_path)
        _pool_bundle(tmp_path, state, slots=0)
        plan = {
            "tasks": [{
                "claim": "c-1", "task_id": "t-1", "lane": "general",
                "worktree": "wt-b-t-1", "lease": "lease-b-00",
            }],
            "batch_id": "b-slots",
            "revision": 0,
        }
        with pytest.raises(state.SpliceError) as e:
            state.dispatch_claims(
                tmp_path, plan=plan, reasoning="o4", session="o4",
                expected_revision=0,
            )
        assert e.value.code == "worker_capacity_exhausted"
