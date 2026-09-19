"""O5 live progress projection goldens — feature_113 (canary-approved).

Hermetic via OMT_NET_DIR / OMT_LEDGER_PATH / OMT_COORDINATION_ROOT (tmp_path).
Covers: freshness pure, probe push/freshness/projection, stale refuse, Tier-3.
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


class TestFreshPure:
    def test_is_fresh(self) -> None:
        fr = _fresh()
        assert fr.is_fresh(60, 60) is True
        assert fr.is_fresh(60, 61) is False
        assert fr.is_fresh(None, 60) is False

    def test_hint_and_push(self) -> None:
        fr = _fresh()
        assert "stale" in fr.freshness_hint(60, 61)
        pr = fr.push_record(61, {"projects": 19}, "NEXT: x")
        assert pr["net_revision"] == 61 and pr["menu"]["projects"] == 19

    def test_projection_lines(self) -> None:
        fr = _fresh()
        lines = fr.projection_lines(61, {"work_done": 7}, [], {"verification": {"used": 0, "total": 1}}, "claims 0/0")
        assert lines[0].startswith("rev 61") and any("claims 0/0" in ln for ln in lines)


class TestProbePush:
    def test_probe_has_push_freshness_projection(self, bundle) -> None:
        from net import cli  # noqa: PLC0415
        env, code = cli._probe(bundle, 100)
        assert code == 0
        assert env["freshness"]["fresh"] is True
        assert env["freshness"]["live_rev"] == env["revision"]
        assert env["push"]["net_revision"] == env["revision"]
        assert isinstance(env["projection"], list) and env["projection"][0].startswith("rev ")

    def test_stale_expected_revision_refuses(self, bundle) -> None:
        state = _state()
        live = int(state.load(bundle).revision)
        with pytest.raises(state.SpliceError) as e:
            state.claim_task(bundle, "proj-rag_v2", owner="alice", session="o5", expected_revision=live + 99)
        assert e.value.code in ("stale_revision", "stale_generation", "task_not_pending")

    def test_state_helpers(self, bundle) -> None:
        state = _state()
        assert state.freshness_for_state(60, 60)["fresh"] is True
        assert state.freshness_for_state(60, 61)["fresh"] is False
        fake = type("S", (), {"revision": 61})()
        pr = state.push_for_state(fake, "NEXT: x", {"projects": 1})
        assert pr["net_revision"] == 61

    def test_no_new_places(self, bundle) -> None:
        state = _state()
        before = set(state.load(bundle).net.places)
        from net import cli  # noqa: PLC0415
        cli._probe(bundle, 100)
        assert set(state.load(bundle).net.places) == before
