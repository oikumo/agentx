"""Task-cost benchmark goldens (feature_093.task_cost_benchmark, mh8 T3-4).

8 groups per analysis_001 §Goldens:
1. task-def validation, 2. metrics math, 3. removal accounting,
4. report render, 5. deny parsing, 6. bun-gated fixture trial,
7. bun-gated removal variants, 8. CLI list.

Canary: new goldens for feature_093 only (scope: tests).
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = REPO_ROOT / "scripts" / "omt"
sys.path.insert(0, str(SCRIPTS_DIR))

BUN = shutil.which("bun")


def _tasks():
    from bench.model import validate_all  # noqa: PLC0415
    from bench.tasks import TASKS  # noqa: PLC0415

    errs = validate_all(list(TASKS))
    assert errs == [], f"invalid registry: {errs}"
    return {t.id: t for t in TASKS}


class TestTaskDefValidation:
    def test_registry_valid(self):
        reg = _tasks()
        assert {"bugfix", "cross_layer", "major", "harness_repair", "resume", "concurrent_conflict",
                "fixture_bugfix", "fixture_nophase"} <= set(reg)

    def test_each_task_has_violation_verify_assert(self):
        reg = _tasks()
        for tid, t in reg.items():
            roles = [s.role for s in t.steps]
            kinds = [s.kind for s in t.steps]
            assert "violation" in roles, f"{tid}: needs a seeded violation"
            assert any(k in ("verify", "assert") for k in kinds) or "verify" in roles, (
                f"{tid}: needs verify/assert evidence"
            )

    def test_gate_annotations_valid(self):
        from bench.model import KNOWN_REMOVAL_GATES  # noqa: PLC0415

        reg = _tasks()
        for tid, t in reg.items():
            for s in t.steps:
                if s.gate is not None:
                    assert s.gate in KNOWN_REMOVAL_GATES, f"{tid}.{s.id}: bad gate {s.gate}"

    def test_concurrent_has_think_consults(self):
        reg = _tasks()
        conc = reg["concurrent_conflict"]
        thinks = [s for s in conc.steps if s.id in ("b_think_consult", "a_think_consult")]
        assert len(thinks) == 2, "TA:124 B+A think consults required"


class TestMetricsMath:
    def _steps(self):
        return [
            {"id": "w1", "kind": "omt", "role": "work", "expect": "ok", "refused": False,
             "blocked_by": [], "args_bytes": 10, "result_bytes": 20, "duration_ms": 0},
            {"id": "v1", "kind": "edit", "role": "violation", "expect": "blocked", "refused": True,
             "blocked_by": ["g.phase"], "args_bytes": 5, "result_bytes": 5, "duration_ms": 0},
            {"id": "v2", "kind": "write", "role": "violation", "expect": "blocked", "refused": False,
             "blocked_by": [], "args_bytes": 5, "result_bytes": 5, "duration_ms": 0},
            {"id": "fp", "kind": "edit", "role": "work", "expect": "ok", "refused": True,
             "blocked_by": ["g.net"], "args_bytes": 7, "result_bytes": 3, "duration_ms": 0},
            {"id": "iv", "kind": "omt", "role": "intervention", "expect": "ok", "refused": False,
             "blocked_by": [], "args_bytes": 4, "result_bytes": 6, "duration_ms": 0},
            {"id": "rec", "kind": "omt", "role": "recovery", "expect": "ok", "refused": False,
             "blocked_by": [], "args_bytes": 4, "result_bytes": 6, "duration_ms": 0},
            {"id": "ver", "kind": "verify", "role": "verify", "expect": "pass", "refused": False,
             "blocked_by": [], "args_bytes": 8, "result_bytes": 12, "duration_ms": 1500, "rc": 0, "ok": True},
            {"id": "a1", "kind": "assert", "role": "verify", "expect": "pass", "refused": False,
             "blocked_by": [], "args_bytes": 6, "result_bytes": 4, "duration_ms": 0, "rc": None, "ok": True},
        ]

    def test_exact_counts(self):
        from bench.metrics import compute_metrics  # noqa: PLC0415

        m = compute_metrics(self._steps())
        assert m["steps"] == 8
        assert m["harness_calls"] == 3
        assert m["blocks_tp"] == 1
        assert m["blocks_fp"] == 1
        assert m["violations_missed"] == 1
        assert m["interventions"] == 1
        assert m["recovery"] == 1
        assert m["verify_seconds"] == 1.5
        assert m["io_bytes"] == (10 + 20 + 5 + 5 + 5 + 5 + 7 + 3 + 4 + 6 + 4 + 6 + 8 + 12 + 6 + 4)
        assert m["tokens_est"] == m["io_bytes"] // 4
        assert m["success"] is True
        assert m["regressions"] == 0

    def test_success_false_when_verify_fails(self):
        from bench.metrics import compute_metrics  # noqa: PLC0415

        steps = self._steps()
        for s in steps:
            if s["id"] == "ver":
                s["rc"] = 1
                s["ok"] = False
        m = compute_metrics(steps)
        assert m["success"] is False
        assert m["regressions"] == 1

    def test_missed_does_not_flip_success(self):
        # TA:120 — removal runs stay "successful but leaking".
        from bench.metrics import compute_metrics  # noqa: PLC0415

        steps = [
            {"id": "v", "kind": "edit", "role": "violation", "expect": "blocked", "refused": False,
             "blocked_by": [], "args_bytes": 1, "result_bytes": 1, "duration_ms": 0},
            {"id": "ver", "kind": "verify", "role": "verify", "expect": "pass", "refused": False,
             "blocked_by": [], "args_bytes": 1, "result_bytes": 1, "duration_ms": 0, "rc": 0, "ok": True},
        ]
        m = compute_metrics(steps)
        assert m["violations_missed"] == 1
        assert m["success"] is True


class TestRemovalAccounting:
    def test_saved_calls_bytes(self):
        from bench.metrics import removal_delta  # noqa: PLC0415

        task_steps = [
            {"id": "declare", "gate": "g.phase"},
            {"id": "canary", "gate": "g.tests"},
            {"id": "fix", "gate": None},
        ]
        transcript = [
            {"id": "declare", "role": "recovery", "refused": False, "blocked_by": [],
             "args_bytes": 100, "result_bytes": 200, "duration_ms": 0},
            {"id": "canary", "role": "recovery", "refused": False, "blocked_by": [],
             "args_bytes": 50, "result_bytes": 50, "duration_ms": 0},
        ]
        d = removal_delta(task_steps, transcript, "g.phase")
        assert d["saved_calls"] == 1
        assert d["saved_bytes"] == 300

    def test_violations_slipped_counts_missed(self):
        from bench.metrics import removal_delta  # noqa: PLC0415

        task_steps = [{"id": "declare", "gate": "g.phase"}]
        transcript = [
            {"id": "v", "role": "violation", "refused": False, "blocked_by": [],
             "args_bytes": 1, "result_bytes": 1, "duration_ms": 0},
        ]
        d = removal_delta(task_steps, transcript, "g.phase")
        assert d["violations_slipped"] == 1


class TestReportRender:
    def test_markdown_and_json_schema(self):
        from bench.report import render_json, render_markdown  # noqa: PLC0415

        per = {
            "fixture_nophase": {"steps": 7, "harness_calls": 2, "blocks_tp": 2, "blocks_fp": 0,
                                "violations_missed": 0, "interventions": 0, "recovery": 2,
                                "verify_seconds": 0.02, "io_bytes": 1000, "tokens_est": 250,
                                "success": True, "regressions": 0, "orientation_bytes": 0,
                                "tool_calls": 7},
        }
        md = render_markdown(per, {"g.phase": {"saved_calls": 1, "saved_bytes": 100, "violations_slipped": 1}},
                             ["custom finding"], "abc123")
        assert "fixture_nophase" in md
        assert "TOTAL" in md
        assert "g.phase" in md
        assert "Assumptions" in md
        assert "FINDINGS" in md
        doc = render_json(per, None, None, "abc123", {"mode": "fixture"})
        assert doc["schema"] == "bench_first_numbers.v1"
        assert doc["revision"] == "abc123"
        assert "totals" in doc and "assumptions" in doc and "findings" in doc


class TestDenyParsing:
    def test_bash_and_read_denies(self):
        from bench.cli import parse_deny_rules  # noqa: PLC0415

        deny = parse_deny_rules()
        assert "git push *" in deny["bash_deny"]
        assert "python *" in deny["bash_deny"]
        assert "pytest *" in deny["bash_deny"]
        assert "*.env" in deny["read_deny"]

    def test_schema_url_with_slashes_survives(self):
        # TA:126 — string-aware stripper must not cut the $schema URL's //.
        from bench.cli import _strip_jsonc_comments  # noqa: PLC0415

        text = '{"$schema": "https://opencode.ai/config.json", // comment\n"a": 1}'
        data = json.loads(_strip_jsonc_comments(text))
        assert data["$schema"] == "https://opencode.ai/config.json"


@pytest.mark.skipif(BUN is None, reason="bun runtime not available")
class TestFixtureTrial:
    def test_fixture_nophase_all_caught(self, tmp_path):
        from bench import sandbox as bench_sandbox  # noqa: PLC0415
        from bench.cli import _spec_for, parse_deny_rules  # noqa: PLC0415
        from bench.metrics import compute_metrics  # noqa: PLC0415

        setup = bench_sandbox.setup_fixture("fixture_nophase", tmp_path)
        spec = _spec_for("fixture_nophase", parse_deny_rules())
        spec_path = Path(setup["sandbox"]) / "bench.spec.json"
        spec_path.write_text(json.dumps(spec), encoding="utf-8")
        out = subprocess.run([BUN, str(SCRIPTS_DIR / "bench" / "probe.ts"),
                              "--sandbox", setup["sandbox"], "--spec", str(spec_path)],
                             capture_output=True, text=True, timeout=120, cwd=str(REPO_ROOT))
        assert out.returncode == 0, f"probe failed:\n{out.stdout[-2000:]}\n{out.stderr[-2000:]}"
        tr = json.loads(out.stdout.strip().splitlines()[-1])
        m = compute_metrics(tr["steps"])
        assert m["violations_missed"] == 0
        assert m["blocks_fp"] == 0
        assert m["success"] is True

    def test_fixture_bugfix_green(self, tmp_path):
        from bench import sandbox as bench_sandbox  # noqa: PLC0415
        from bench.cli import _spec_for, parse_deny_rules  # noqa: PLC0415
        from bench.metrics import compute_metrics  # noqa: PLC0415

        setup = bench_sandbox.setup_fixture("fixture_bugfix", tmp_path)
        spec = _spec_for("fixture_bugfix", parse_deny_rules())
        spec_path = Path(setup["sandbox"]) / "bench.spec.json"
        spec_path.write_text(json.dumps(spec), encoding="utf-8")
        out = subprocess.run([BUN, str(SCRIPTS_DIR / "bench" / "probe.ts"),
                              "--sandbox", setup["sandbox"], "--spec", str(spec_path)],
                             capture_output=True, text=True, timeout=120, cwd=str(REPO_ROOT))
        assert out.returncode == 0, f"probe failed:\n{out.stdout[-2000:]}\n{out.stderr[-2000:]}"
        tr = json.loads(out.stdout.strip().splitlines()[-1])
        m = compute_metrics(tr["steps"])
        assert m["violations_missed"] == 0
        assert m["blocks_fp"] == 0
        assert m["success"] is True


@pytest.mark.skipif(BUN is None, reason="bun runtime not available")
class TestRemovalVariants:
    def _trial(self, task_id, removal, tmp_path):
        from bench import sandbox as bench_sandbox  # noqa: PLC0415
        from bench.cli import _spec_for, parse_deny_rules  # noqa: PLC0415
        from bench.metrics import compute_metrics, removal_delta  # noqa: PLC0415
        from bench.tasks import task_map  # noqa: PLC0415

        setup = bench_sandbox.setup_fixture(task_id, tmp_path)
        spec = _spec_for(task_id, parse_deny_rules())
        spec_path = Path(setup["sandbox"]) / "bench.spec.json"
        spec_path.write_text(json.dumps(spec), encoding="utf-8")
        cmd = [BUN, str(SCRIPTS_DIR / "bench" / "probe.ts"),
               "--sandbox", setup["sandbox"], "--spec", str(spec_path)]
        if removal:
            cmd += ["--remove", removal]
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=str(REPO_ROOT))
        assert out.returncode == 0, f"probe {removal} failed:\n{out.stderr[-2000:]}"
        tr = json.loads(out.stdout.strip().splitlines()[-1])
        task_steps = [{"id": s.id, "gate": s.gate} for s in task_map()[task_id].steps]
        delta = removal_delta(task_steps, tr["steps"], removal) if removal else None
        return compute_metrics(tr["steps"]), delta

    def test_remove_g_phase_slips_no_phase(self, tmp_path):
        m, delta = self._trial("fixture_nophase", "g.phase", tmp_path)
        assert m["violations_missed"] == 1
        assert delta is not None and delta["saved_calls"] == 1  # declare step saved

    def test_remove_g_tests_slips_canary(self, tmp_path):
        m, delta = self._trial("fixture_nophase", "g.tests", tmp_path)
        assert m["violations_missed"] == 1
        assert delta is not None and delta["saved_calls"] == 1  # canary step saved


class TestCliList:
    def test_list_has_8_tasks(self):
        out = subprocess.run([sys.executable, str(SCRIPTS_DIR / "task_cost_benchmark.py"), "list"],
                             capture_output=True, text=True, timeout=60, cwd=str(REPO_ROOT))
        assert out.returncode == 0, out.stderr[-1000:]
        data = json.loads(out.stdout)
        ids = {t["id"] for t in data["tasks"]}
        assert {"bugfix", "cross_layer", "major", "harness_repair", "resume",
                "concurrent_conflict", "fixture_bugfix", "fixture_nophase"} <= ids
