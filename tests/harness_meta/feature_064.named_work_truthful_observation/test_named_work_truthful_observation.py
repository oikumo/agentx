"""Wave focus / slice 1 named_work_truthful_observation — feature_064.

Contract (slice 1 = observation only; atomic claims + integration deferred):
- REGISTRY: task bindings persist in the sidecar (revision-coupled, atomic
  with the bundle); legacy bundles without the key load with [].
- VALIDATION: unique non-empty ids, place in pool places, bindings ⊆ live
  tokens per place (remainder reported as anonymous — no silent backfill).
- OBSERVATION: probe gains ADDITIVE tasks/observation/menu keys; existing
  keys byte-identical. One state with reason: inconsistent > executing >
  ready > awaiting_capacity > drained_complete > idle_empty. Analyzer output
  labeled by basis (live marking vs initial-marking analysis).
- MENU: NEXT/Other/Blocked/Resources order with task-bound actions, transition
  fallback when no bindings exist.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "scripts" / "omt"
sys.path.insert(0, str(SCRIPTS_DIR))


def _state():
    from net import state  # noqa: PLC0415

    return state


def _cli():
    from net import cli  # noqa: PLC0415

    return cli


def _binding(bid="task-a", place="work_pending", **kw):
    b = {"id": bid, "place": place}
    b.update(kw)
    return b


@pytest.fixture()
def pool(tmp_path, monkeypatch):
    st_mod = _state()
    monkeypatch.setenv("OMT_NET_DIR", str(tmp_path))
    monkeypatch.setenv("OMT_LEDGER_PATH", str(tmp_path / "ledger.jsonl"))
    st_mod.init_empty(tmp_path)
    st = st_mod.load(tmp_path)
    st.net.add_place("agent_attention", tokens=1)
    st.net.add_place("work_pending", tokens=0)
    st.net.add_place("work_active", tokens=0)
    st.net.add_place("work_done", tokens=0)
    st.net.add_transition("work_start")
    st.net.add_transition("work_complete")
    st.net.add_input("agent_attention", "work_start")
    st.net.add_input("work_pending", "work_start")
    st.net.add_output("work_start", "work_active")
    st.net.add_input("work_active", "work_complete")
    st.net.add_output("work_complete", "agent_attention")
    st.net.add_output("work_complete", "work_done")
    st.live_marking = {
        "agent_attention": 1,
        "work_pending": 0,
        "work_active": 0,
        "work_done": 0,
    }
    st_mod.save(tmp_path, st)
    return tmp_path


def _run_probe(pool, capsys, *argv):
    cli = _cli()
    code = cli.main(["probe", *argv])
    return code, json.loads(capsys.readouterr().out)


class TestRegistry:
    def test_legacy_bundle_loads_empty(self, pool) -> None:
        st = _state().load(pool)
        assert st.task_bindings == []

    def test_round_trip(self, pool) -> None:
        st_mod = _state()
        st = st_mod.load(pool)
        st.task_bindings = [_binding("task-a", "work_done", owner="worker-a")]
        st.live_marking["work_done"] = 1
        st_mod.save(pool, st)
        assert st_mod.load(pool).task_bindings == [
            _binding("task-a", "work_done", owner="worker-a")
        ]

    def test_sidecar_carries_key(self, pool) -> None:
        st_mod = _state()
        st = st_mod.load(pool)
        st.task_bindings = [_binding()]
        st_mod.save(pool, st)
        sidecar = json.loads((pool / "net_state.sidecar.json").read_text())
        assert [b["id"] for b in sidecar["task_bindings"]] == ["task-a"]


class TestValidation:
    def test_empty_ok(self) -> None:
        rep = _state().validate_task_bindings([], {"work_pending": 0})
        assert rep["ok"] and rep["errors"] == [] and rep["consistent"]

    def test_valid_binding_ok(self) -> None:
        rep = _state().validate_task_bindings(
            [_binding("a", "work_pending")], {"work_pending": 1}
        )
        assert rep["ok"], rep["errors"]
        assert rep["per_place"]["work_pending"] == {
            "bindings": 1,
            "tokens": 1,
            "anonymous": 0,
        }

    def test_anonymous_remainder_ok(self) -> None:
        rep = _state().validate_task_bindings([], {"work_done": 7})
        assert rep["ok"]
        assert rep["per_place"]["work_done"]["anonymous"] == 7

    def test_duplicate_id_rejected(self) -> None:
        rep = _state().validate_task_bindings(
            [_binding("a", "work_pending"), _binding("a", "work_done")],
            {"work_pending": 1, "work_done": 1},
        )
        assert not rep["ok"] and any("duplicate" in e for e in rep["errors"])

    def test_bad_place_rejected(self) -> None:
        rep = _state().validate_task_bindings(
            [_binding("a", "verifying")], {"work_pending": 1}
        )
        assert not rep["ok"] and any("place" in e for e in rep["errors"])

    def test_oversubscribed_rejected(self) -> None:
        rep = _state().validate_task_bindings(
            [_binding("a", "work_active"), _binding("b", "work_active")],
            {"work_active": 1},
        )
        assert not rep["ok"] and any("but only" in e for e in rep["errors"])

    def test_non_list_rejected(self) -> None:
        rep = _state().validate_task_bindings({"id": "a"}, {})
        assert not rep["ok"]


class TestProbeObservation:
    def test_additive_keys_idle(self, pool, capsys) -> None:
        code, out = _run_probe(pool, capsys)
        assert code == 0
        assert out["observation"]["state"] == "idle_empty"
        assert out["observation"]["basis"] == f"live_marking rev {out['revision']}"
        assert out["menu"]["next"] == "none"
        assert "marking" in out and "enabled" in out and "advice" in out

    def test_drained_complete(self, pool, capsys) -> None:
        st_mod = _state()
        st = st_mod.load(pool)
        st.live_marking["work_done"] = 7
        st_mod.save(pool, st)
        _, out = _run_probe(pool, capsys)
        assert out["observation"]["state"] == "drained_complete"
        assert "7" in out["observation"]["reason"]

    def test_ready_with_task_action(self, pool, capsys) -> None:
        st_mod = _state()
        st = st_mod.load(pool)
        st.live_marking["work_pending"] = 1
        st.task_bindings = [_binding("retrieval-progress", "work_pending")]
        st_mod.save(pool, st)
        _, out = _run_probe(pool, capsys)
        assert out["observation"]["state"] == "ready"
        assert "retrieval-progress" in out["menu"]["next"]

    def test_awaiting_capacity_names_blocker(self, pool, capsys) -> None:
        st_mod = _state()
        st = st_mod.load(pool)
        st.live_marking.update(
            {"agent_attention": 0, "work_pending": 1, "work_active": 0}
        )
        st_mod.save(pool, st)
        _, out = _run_probe(pool, capsys)
        assert out["observation"]["state"] == "awaiting_capacity"
        assert "agent_attention" in out["observation"]["reason"]

    def test_executing(self, pool, capsys) -> None:
        st_mod = _state()
        st = st_mod.load(pool)
        st.live_marking.update(
            {"agent_attention": 0, "work_active": 1, "work_done": 0}
        )
        st.task_bindings = [_binding("w", "work_active", owner="worker-a")]
        st_mod.save(pool, st)
        _, out = _run_probe(pool, capsys)
        assert out["observation"]["state"] == "executing"

    def test_inconsistent_on_bad_bindings(self, pool, capsys) -> None:
        st_mod = _state()
        st = st_mod.load(pool)
        st.task_bindings = [_binding("a", "nope")]
        st_mod.save(pool, st)
        _, out = _run_probe(pool, capsys)
        assert out["observation"]["state"] == "inconsistent"
        assert out["bindings_valid"] is False

    def test_analysis_basis_labeled(self, pool, capsys) -> None:
        _, out = _run_probe(pool, capsys)
        assert "initial-marking analysis" in out["advice"]["basis"]
