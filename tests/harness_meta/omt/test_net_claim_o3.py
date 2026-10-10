"""O3 identity-aware pool goldens — feature_112.identity_aware_pool.

Derived handles (net.claim_handles) + state.apply_selection handles view +
cli probe menu.claims additive + claim_task reservation (gen-fenced).
Hermetic via OMT_NET_DIR / OMT_LEDGER_PATH / OMT_COORDINATION_ROOT (tmp_path).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "scripts" / "omt"
sys.path.insert(0, str(SCRIPTS_DIR))


def _handles():
    from net import claim_handles  # noqa: PLC0415
    return claim_handles


def _state():
    from net import state  # noqa: PLC0415
    return state


def _pool_bundle(base: Path, state, tasks=("proj-rag_v2",)) -> None:
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


class TestMapStable:
    def test_proj_map(self) -> None:
        ch = _handles()
        assert ch.menu_id_to_task_id("proj:rag_v2") == "proj-rag_v2"

    def test_drift_unscoped_pool_map(self) -> None:
        ch = _handles()
        assert ch.menu_id_to_task_id("drift:aging-draft:feature_kb_akb") == "drift-aging-draft-feature_kb_akb"
        assert ch.menu_id_to_task_id("unscoped:001") == "unscoped-001"
        assert ch.menu_id_to_task_id("pool:t1") == "t1"

    def test_unknown_refuses(self) -> None:
        ch = _handles()
        with pytest.raises(ValueError, match="unknown_id"):
            ch.menu_id_to_task_id("nope:rag_v2")


class TestHandlesView:
    def test_missing_binding_is_pending(self) -> None:
        ch = _handles()
        (h,) = ch.handles_for_menu(["proj:rag_v2"], [])
        assert (h.task_id, h.place, h.owner, h.generation) == ("proj-rag_v2", "pending", "none", 0)

    def test_existing_binding_joins(self, bundle) -> None:
        ch, state = _handles(), _state()
        st = state.load(bundle)
        hs = ch.handles_for_menu(["proj:rag_v2"], list(st.task_bindings))
        assert hs[0].place == "work_pending"
        assert "claims 0/1" in ch.describe_handles(hs)


class TestClaimReserves:
    def test_claim_holds_generation(self, bundle) -> None:
        state = _state()
        st = state.claim_task(bundle, "proj-rag_v2", owner="alice", session="o3", expected_revision=0)
        b = next(x for x in st.task_bindings if x["id"] == "proj-rag_v2")
        assert (b["place"], b["owner"], b["generation"]) == ("work_active", "alice", 1)

    def test_second_session_refuses_not_pending(self, bundle) -> None:
        state = _state()
        state.claim_task(bundle, "proj-rag_v2", owner="alice", session="o3", expected_revision=0)
        with pytest.raises(state.SpliceError) as e:
            state.claim_task(bundle, "proj-rag_v2", owner="bob", session="o3", expected_revision=1)
        assert e.value.code == "task_not_pending"

    def test_coverage_deanonymized_after_claim(self, bundle) -> None:
        state = _state()
        state.claim_task(bundle, "proj-rag_v2", owner="alice", session="o3", expected_revision=0)
        st = state.load(bundle)
        rep = state.validate_task_bindings(list(st.task_bindings), dict(st.live_marking))
        assert rep["per_place"]["work_active"]["bindings"] == 1
        assert rep["per_place"]["work_active"]["anonymous"] == 0


class TestApplyHandlesView:
    def test_annotate_report_carries_handles(self, bundle) -> None:
        state = _state()
        st, report = state.apply_selection(
            bundle, "pick {proj:rag_v2}", {"proj:rag_v2"}, [],
            reasoning="o3", session="o3", expected_revision=0,
        )
        assert report["mutated"] is False
        assert report["handles"][0]["task_id"] == "proj-rag_v2"
        assert "claims" in report["handles_summary"]

    def test_stale_rev_refuses(self, bundle) -> None:
        state = _state()
        with pytest.raises(state.SpliceError) as e:
            state.apply_selection(
                bundle, "pick {proj:rag_v2}", {"proj:rag_v2"}, [],
                reasoning="o3", session="o3", expected_revision=999,
            )
        assert e.value.code == "stale_revision"

    def test_no_new_places(self, bundle) -> None:
        state = _state()
        before = set(state.load(bundle).net.places)
        state.apply_selection(
            bundle, "pick {proj:rag_v2}", {"proj:rag_v2"}, [],
            reasoning="o3", session="o3", expected_revision=0,
        )
        assert set(state.load(bundle).net.places) == before


class TestMenuClaims:
    def test_probe_menu_claims_additive(self, bundle) -> None:
        from net import cli  # noqa: PLC0415
        env, code = cli._probe(bundle, 100)
        assert code == 0
        assert "claims" in env["menu"]
        assert env["menu"]["claims"][0]["task_id"] == "proj-rag_v2"
