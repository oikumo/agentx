"""Benchmark CLI (feature_093.task_cost_benchmark): list/run/removal/run-all.

list: pure task registry dump (no sandbox, no bun).
run: sandbox setup + bun probe trial + metrics.
removal: re-run trials with one gate filtered (probe irOverride).
run-all: all tasks + removal matrix + bench_first_numbers artifacts.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
BENCH_DIR = Path(__file__).resolve().parent
PROBE_TS = BENCH_DIR / "probe.ts"
SHIM_NOTE = "scripts/omt/task_cost_benchmark.py shim delegates here"

BUN = shutil.which("bun")


def _strip_jsonc_comments(text: str) -> str:
    """String-aware // comment stripper (TA:126: $schema URL contains //)."""
    out: list[str] = []
    in_str = False
    esc = False
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        nxt = text[i + 1] if i + 1 < n else ""
        if in_str:
            out.append(ch)
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            i += 1
            continue
        if ch == '"':
            in_str = True
            out.append(ch)
            i += 1
            continue
        if ch == "/" and nxt == "/":
            # line comment: skip to end of line (keep the newline).
            while i < n and text[i] != "\n":
                i += 1
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def parse_deny_rules(config_path: Path | None = None) -> dict[str, list[str]]:
    """Parse opencode.jsonc permission deny lists (bash + read)."""
    cfg = config_path or (REPO_ROOT / "opencode.jsonc")
    raw = cfg.read_text(encoding="utf-8")
    data = json.loads(_strip_jsonc_comments(raw))
    perm = data.get("permission", {}) if isinstance(data, dict) else {}
    bash = perm.get("bash", {}) if isinstance(perm, dict) else {}
    read = perm.get("read", {}) if isinstance(perm, dict) else {}
    bash_deny = sorted([k for k, v in bash.items() if v == "deny" and k != "*"])
    read_deny = sorted([k for k, v in read.items() if v == "deny" and k != "*"])
    return {"bash_deny": bash_deny, "read_deny": read_deny}


def _tasks() -> dict[str, Any]:
    sys.path.insert(0, str(REPO_ROOT / "scripts" / "omt"))
    from bench.model import validate_all  # type: ignore[import-not-found]
    from bench.tasks import TASKS  # type: ignore[import-not-found]

    errs = validate_all(list(TASKS))
    if errs:
        raise ValueError("invalid task registry: " + "; ".join(errs))
    return {t.id: t for t in TASKS}


def cmd_list() -> dict[str, Any]:
    reg = _tasks()
    return {
        "tasks": [
            {"id": t.id, "description": t.description, "mode": t.mode, "steps": len(t.steps)}
            for t in reg.values()
        ]
    }


def _spec_for(task_id: str, deny: dict[str, list[str]]) -> dict[str, Any]:
    reg = _tasks()
    task = reg[task_id]
    return {
        "task": task.to_spec(),
        "deny": deny,
    }


def run_trial(
    task_id: str,
    mode: str = "fixture",
    removal: str | None = None,
    keep: bool = False,
) -> dict[str, Any]:
    """Setup sandbox + run bun probe + compute metrics. Returns run record."""
    if BUN is None:
        raise RuntimeError("bun runtime required for probe trials")
    sys.path.insert(0, str(REPO_ROOT / "scripts" / "omt"))
    from bench import sandbox as bench_sandbox  # type: ignore[import-not-found]
    from bench.metrics import compute_metrics  # type: ignore[import-not-found]

    deny = parse_deny_rules()
    tmp_holder: tempfile.TemporaryDirectory[str] | None = None
    if mode == "fixture":
        tmp_holder = tempfile.TemporaryDirectory(prefix="bench-fixture-")
        setup = bench_sandbox.setup_fixture(task_id, Path(tmp_holder.name))
        sandbox_dir = setup["sandbox"]
        revision = "fixture"
    else:
        setup = bench_sandbox.setup_real(task_id, prewarm=True)
        sandbox_dir = setup["sandbox"]
        revision = str(setup.get("revision", ""))
    try:
        spec = _spec_for(task_id, deny)
        spec_path = Path(sandbox_dir) / "bench.spec.json"
        spec_path.write_text(json.dumps(spec), encoding="utf-8")
        cmd = [BUN, str(PROBE_TS), "--sandbox", sandbox_dir, "--spec", str(spec_path)]
        if removal:
            cmd += ["--remove", removal]
        probe_timeout = 600 if mode == "real" else 180
        out = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=probe_timeout, check=False)
        if out.returncode != 0:
            raise RuntimeError(f"probe failed rc={out.returncode}:\n{out.stdout}\n{out.stderr}")
        last_line = out.stdout.strip().splitlines()[-1] if out.stdout.strip() else "{}"
        transcript = json.loads(last_line)
        steps = transcript.get("steps", [])
        metrics = compute_metrics(steps)
        return {
            "task": task_id,
            "mode": mode,
            "removal": removal,
            "revision": revision,
            "sandbox": sandbox_dir,
            "transcript": transcript,
            "metrics": metrics,
        }
    finally:
        if not keep:
            try:
                if mode == "fixture" and tmp_holder is not None:
                    tmp_holder.cleanup()
                else:
                    bench_sandbox.cleanup(sandbox_dir)
            except Exception:
                pass
        else:
            if tmp_holder is not None:
                # Keep: do not cleanup tempdir (leaked by design for debugging).
                pass


def cmd_run(task_id: str, mode: str, removal: str | None = None) -> dict[str, Any]:
    rec = run_trial(task_id, mode=mode, removal=removal, keep=False)
    return {"task": rec["task"], "metrics": rec["metrics"], "transcript": rec["transcript"]}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="task_cost_benchmark", description="Task-cost benchmark driver")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="list benchmark tasks")
    p_run = sub.add_parser("run", help="run one trial")
    p_run.add_argument("--task", required=True)
    p_run.add_argument("--mode", default="fixture", choices=["fixture", "real"])
    p_run.add_argument("--remove", default=None, help="gate id to filter (removal experiment)")
    p_run.add_argument("--keep", action="store_true", help="keep sandbox dir")
    p_rem = sub.add_parser("removal", help="run removal variants for one task")
    p_rem.add_argument("--task", required=True)
    p_rem.add_argument("--mode", default="fixture", choices=["fixture", "real"])
    p_all = sub.add_parser("run-all", help="all tasks + removal matrix + artifacts")
    p_all.add_argument("--mode", default="fixture", choices=["fixture", "real"])
    p_all.add_argument("--out-dir", default=None)
    args = ap.parse_args(argv)
    if args.cmd == "list":
        print(json.dumps(cmd_list(), indent=2, sort_keys=True))
        return 0
    if args.cmd == "run":
        rec = run_trial(args.task, mode=args.mode, removal=args.remove, keep=args.keep)
        print(json.dumps({"task": rec["task"], "metrics": rec["metrics"]}, indent=2, sort_keys=True))
        return 0
    if args.cmd == "removal":
        from bench.model import KNOWN_REMOVAL_GATES  # type: ignore[import-not-found]

        out: dict[str, Any] = {"task": args.task, "variants": {}}
        base = run_trial(args.task, mode=args.mode, removal=None, keep=False)
        out["variants"]["baseline"] = base["metrics"]
        for gate in sorted(KNOWN_REMOVAL_GATES):
            rec = run_trial(args.task, mode=args.mode, removal=gate, keep=False)
            out["variants"][gate] = rec["metrics"]
        print(json.dumps(out, indent=2, sort_keys=True))
        return 0
    if args.cmd == "run-all":
        from bench.metrics import removal_delta  # type: ignore[import-not-found]
        from bench.report import render_json, render_markdown  # type: ignore[import-not-found]

        reg = _tasks()
        per_task: dict[str, Any] = {}
        transcripts: dict[str, Any] = {}
        revision = ""
        for tid, t in reg.items():
            if t.mode != args.mode and args.mode == "fixture":
                # run-all fixture mode runs fixture tasks only.
                continue
            if args.mode == "real" and t.mode != "real":
                continue
            rec = run_trial(tid, mode=args.mode, removal=None, keep=False)
            per_task[tid] = rec["metrics"]
            transcripts[tid] = rec["transcript"]
            revision = rec.get("revision", revision)
        # Removal matrix on fixture_nophase (attribution micro-task).
        removal: dict[str, Any] = {}
        if args.mode == "fixture" and "fixture_nophase" in transcripts:
            from bench.model import KNOWN_REMOVAL_GATES  # type: ignore[import-not-found]

            base_steps = transcripts["fixture_nophase"].get("steps", [])
            task_steps = [
                {"id": s.id, "gate": s.gate}
                for s in reg["fixture_nophase"].steps
            ]
            for gate in sorted(KNOWN_REMOVAL_GATES):
                rec = run_trial("fixture_nophase", mode="fixture", removal=gate, keep=False)
                delta = removal_delta(task_steps, rec["transcript"].get("steps", []), gate)
                removal[gate] = delta
            _ = base_steps
        doc = render_json(per_task, removal or None, None, revision, {"mode": args.mode})
        md = render_markdown(per_task, removal or None, None, revision)
        out_dir = Path(args.out_dir) if args.out_dir else REPO_ROOT / ".meta" / "software_development_process" / "6.testing" / "features" / "feature_093.task_cost_benchmark"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "bench_first_numbers.json").write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (out_dir / "bench_first_numbers.md").write_text(md, encoding="utf-8")
        print(json.dumps({"wrote": [str(out_dir / "bench_first_numbers.json"), str(out_dir / "bench_first_numbers.md")], "per_task": per_task}, indent=2, sort_keys=True))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
