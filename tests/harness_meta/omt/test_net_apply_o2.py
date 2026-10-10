"""O2 multi-select + directive protocol goldens — feature_111.multi_select_directive_protocol.

Pure grammar/plan (net.apply_selection) + state.apply_selection threading:
M0 serial-atomic bound, stable refuse codes, stale-rev guard, annotate-only
report, single-fire commit with ledger-carried envelope, Tier-3 no-new-places.

Hermetic via OMT_NET_DIR / OMT_LEDGER_PATH (tmp_path).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "scripts" / "omt"
sys.path.insert(0, str(SCRIPTS_DIR))


def _pure():
    from net import apply_selection  # noqa: PLC0415

    return apply_selection


def _state():
    from net import state  # noqa: PLC0415

    return state


def _hello_bundle(base: Path, state) -> None:
    """p1=1 ->t1-> p2 bundle at revision 0 (via init + splice-free build)."""
    state.init_empty(base)
    st = state.load(base)
    st.net.add_place("p1", tokens=1)
    st.net.add_place("p2", tokens=0)
    st.net.add_transition("t1")
    st.net.add_input("p1", "t1")
    st.net.add_output("t1", "p2")
    st.live_marking = {"p1": 1, "p2": 0}
    state.save(base, st)


@pytest.fixture()
def bundle(tmp_path, monkeypatch):
    state = _state()
    monkeypatch.setenv("OMT_NET_DIR", str(tmp_path))
    monkeypatch.setenv("OMT_LEDGER_PATH", str(tmp_path / "ledger.jsonl"))
    _hello_bundle(tmp_path, state)
    return tmp_path


class TestGrammarAccept:
    def test_pick_two_ids_with_directive(self) -> None:
        m = _pure()
        sel = m.parse_selection('pick {proj:rag_v2, unscoped:001} + unscoped:001:"scope spike"')
        assert sel.ids == ("proj:rag_v2", "unscoped:001")
        assert sel.directives == {"unscoped:001": "scope spike"}

    def test_pick_single_pool_id(self) -> None:
        m = _pure()
        sel = m.parse_selection("pick {pool:t1}")
        assert sel.ids == ("pool:t1",)
        assert sel.directives == {}

    def test_pick_drift_id(self) -> None:
        m = _pure()
        sel = m.parse_selection("pick {drift:aging-draft:feature_kb_akb}")
        assert sel.ids == ("drift:aging-draft:feature_kb_akb",)


class TestGrammarRefuse:
    def test_unknown_id_refused_against_menu(self) -> None:
        m = _pure()
        sel = m.parse_selection("pick {proj:nope}")
        with pytest.raises(m.SelectionError) as e:
            m.validate_selection(sel, {"proj:rag_v2"})
        assert e.value.code == "unknown_id"

    def test_dup_id_refused(self) -> None:
        m = _pure()
        with pytest.raises(m.SelectionError) as e:
            m.parse_selection("pick {proj:a, proj:a}")
        assert e.value.code == "dup_id"

    def test_directive_without_id_refused(self) -> None:
        m = _pure()
        with pytest.raises(m.SelectionError) as e:
            m.parse_selection("pick {proj:a} + proj:b:\"x\"")
        assert e.value.code == "directive_without_id"

    def test_bad_syntax_refused(self) -> None:
        m = _pure()
        with pytest.raises(m.SelectionError) as e:
            m.parse_selection("do proj:a tomorrow")
        assert e.value.code == "bad_syntax"


class TestPlanBound:
    def test_multi_mutate_defers_o4(self) -> None:
        m = _pure()
        sel = m.parse_selection("pick {pool:t1, pool:t2}")
        with pytest.raises(m.SelectionError) as e:
            m.plan_selection(sel, valid_ids={"pool:t1", "pool:t2"}, enabled=["t1", "t2"])
        assert e.value.code == "multi_mutate_deferred_o4"

    def test_annotate_only_plan_shape(self) -> None:
        m = _pure()
        sel = m.parse_selection('pick {proj:rag_v2, unscoped:001} + unscoped:001:"spike"')
        plan = m.plan_selection(sel, valid_ids={"proj:rag_v2", "unscoped:001"}, enabled=[])
        assert plan.mutate == ()
        assert plan.annotations["unscoped:001"] == "spike"
        assert len(plan.proposals) == 2
        assert "annotate-only" in m.describe_plan(plan)


class TestThreading:
    def test_annotate_only_writes_nothing(self, bundle) -> None:
        state = _state()
        before = state.load(bundle).revision
        st, report = state.apply_selection(
            bundle,
            'pick {proj:rag_v2, unscoped:001} + unscoped:001:"spike"',
            {"proj:rag_v2", "unscoped:001"},
            [],
            reasoning="golden",
            session="golden",
            expected_revision=before,
        )
        assert report["mutated"] is False
        assert st.revision == before
        assert report["annotations"]["unscoped:001"] == "spike"

    def test_stale_rev_refuses(self, bundle) -> None:
        state = _state()
        with pytest.raises(state.SpliceError) as e:
            state.apply_selection(
                bundle, "pick {proj:rag_v2}", {"proj:rag_v2"}, [],
                reasoning="golden", session="golden", expected_revision=999,
            )
        assert e.value.code == "stale_revision"

    def test_single_fire_commit_carries_envelope(self, bundle) -> None:
        state = _state()
        places_before = set(state.load(bundle).net.places)
        st, report = state.apply_selection(
            bundle,
            'pick {pool:t1, proj:rag_v2} + proj:rag_v2:"after fire"',
            {"pool:t1", "proj:rag_v2"},
            ["t1"],
            reasoning="golden",
            session="golden",
            expected_revision=0,
            command_id="golden-o2-fire",
        )
        assert report["mutated"] is True
        assert st.revision == 1
        assert st.live_marking == {"p1": 0, "p2": 1}
        assert set(st.net.places) == places_before  # Tier-3: no new places
        recs = [json.loads(line) for line in (bundle / "ledger.jsonl").read_text().splitlines()]
        fires = [r for r in recs if r.get("kind") == "net_fire"]
        assert fires and fires[-1]["selection"] == ["pool:t1", "proj:rag_v2"]
        assert fires[-1]["directives"] == {"proj:rag_v2": "after fire"}
        assert fires[-1]["batch_id"] == report["batch_id"]
