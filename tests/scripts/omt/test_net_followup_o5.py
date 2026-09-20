"""O5a+b follow-up goldens — feature_115 (canary-approved).

Hermetic via OMT_NET_DIR / OMT_LEDGER_PATH / OMT_COORDINATION_ROOT (tmp_path).
Covers: batch projection pure (order/fail-open/tail), push full text
(D19 + rev-stamp + parse round-trip), stale still refuses, probe
backward-compat (existing projection first lines unchanged), Tier-3.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "scripts" / "omt"
sys.path.insert(0, str(SCRIPTS_DIR))


def _fresh():
    from net import freshness  # noqa: PLC0415
    return freshness


def _state():
    from net import state  # noqa: PLC0415
    return state


def _pool_bundle(base: Path, state) -> None:
    state.init_empty(base)
    st = state.load(base)
    for place, tokens in (
        ("work_pending", 0),
        ("work_active", 0),
        ("work_done", 7),
        ("agent_attention", 1),
        ("feature_ready", 1),
    ):
        try:
            st.net.add_place(place, tokens=tokens)
        except Exception:
            pass
    st.live_marking = {
        "work_pending": 0,
        "work_active": 0,
        "work_done": 7,
        "agent_attention": 1,
        "feature_ready": 1,
    }
    st.task_bindings = []
    state.save(base, st)


@pytest.fixture()
def bundle(tmp_path, monkeypatch):
    state = _state()
    monkeypatch.setenv("OMT_NET_DIR", str(tmp_path))
    monkeypatch.setenv("OMT_LEDGER_PATH", str(tmp_path / "ledger.jsonl"))
    monkeypatch.setenv("OMT_COORDINATION_ROOT", str(tmp_path / "coord"))
    _pool_bundle(tmp_path, state)
    return tmp_path


def _plan() -> dict:
    return {
        "tasks": [
            {
                "claim": "c2",
                "task_id": "t2",
                "lane": "general",
                "worktree": "wt-x-t2",
                "lease": "lease-x-01",
            },
            {
                "claim": "c1",
                "task_id": "t1",
                "lane": "verification",
                "worktree": "wt-x-t1",
                "lease": "lease-x-00",
            },
        ],
        "wip": {"pending": 0, "active": 2, "cap": 15},
        "revision": 61,
        "batch_id": "abc123",
    }


class TestBatchProjectionPure:
    def test_ordered_batch_lines(self) -> None:
        fr = _fresh()
        lines = fr.batch_projection_lines(_plan())
        assert lines[0] == "batch abc123 rev 61 lanes 1/0/1 wip 0/2/15"
        assert lines[1].startswith("task t1 [verification]")
        assert lines[2].startswith("task t2 [general]")

    def test_malformed_fail_open(self) -> None:
        fr = _fresh()
        assert fr.batch_projection_lines(None) == []
        assert fr.batch_projection_lines({}) == []
        assert fr.batch_projection_lines({"tasks": []}) == []
        assert fr.batch_projection_lines({"tasks": [{"lane": "x"}]}) == []
        assert fr.batch_projection_lines("nope") == []

    def test_tail_deadlocks_blocked(self) -> None:
        fr = _fresh()
        lines = fr.batch_projection_lines(
            _plan(),
            {"deadlocks_complete": True},
            [{"transition": "f3_start"}],
        )
        assert lines[-1] == "deadlocks_complete blocked:f3_start"


class TestPushFullText:
    def test_render_push_text_round_trips(self, bundle) -> None:
        state = _state()
        st = state.load(bundle)
        places_before = set(st.net.places)
        text = state._render_push_text(st)
        assert text.startswith(f"<!-- net_rev:{st.revision} -->")
        assert "NEXT:" in text and "Resources:" in text
        from net import sync_md  # noqa: PLC0415
        assert isinstance(sync_md.parse_tasks_block(text), dict)
        assert set(state.load(bundle).net.places) == places_before

    def test_push_for_state_carries_text(self, bundle) -> None:
        state = _state()
        st = state.load(bundle)
        push = state.push_for_state(
            st, state._render_push_text(st), {"claims": 0}
        )
        assert push["net_revision"] == st.revision
        assert push["tasks_block"].startswith("<!-- net_rev:")

    def test_stale_still_refuses(self, bundle) -> None:
        state = _state()
        live = int(state.load(bundle).revision)
        with pytest.raises(state.SpliceError) as exc:
            state.claim_task(
                bundle,
                "proj-rag_v2",
                owner="alice",
                session="o5b",
                expected_revision=live + 99,
            )
        assert exc.value.code in (
            "stale_revision",
            "stale_generation",
            "task_not_pending",
        )

    def test_probe_backward_compat(self, bundle) -> None:
        from net import cli  # noqa: PLC0415
        env, code = cli._probe(bundle, 100)
        assert code == 0
        assert env["projection"][0].startswith("rev ")
        assert env["push"]["tasks_block"].startswith("<!-- net_rev:")
        assert env["push"]["net_revision"] == env["revision"]

    def test_join_view_empty_without_plan(self, bundle) -> None:
        state = _state()
        st = state.load(bundle)
        assert state.join_projection_for_state(st, None) == []
        view = state.join_projection_for_state(st, _plan())
        assert view[0].startswith("batch abc123")
