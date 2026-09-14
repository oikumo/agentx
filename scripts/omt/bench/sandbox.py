"""Benchmark sandbox setup (feature_093.task_cost_benchmark).

Real mode: pinned-rev `git worktree add --detach` under .sandbox/bench/ +
fault seeding + net-state copy (+ concurrent 3-binding injection) + resume
ledger seed + major pre-scaffold + uv.lock copy + `uv sync` pre-warm.
Fixture mode: hermetic mini-repo (real .opencode/ + compiled .meta/.omt/
projections copied, synthetic src/+tests/ targets) for goldens.

Setup edits are NOT counted — only probe steps are metered.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
BENCH_ROOT = REPO_ROOT / ".sandbox" / "bench"

MODEL_FILE = "src/agentx/model/chat/chat_history.py"
UI_FILE = "src/agentx/ui/screens/chat/chat_controller.py"
HARNESS_C = "scripts/omt/harnessc.py"

ORDER_ASC = "ORDER BY timestamp ASC"
ORDER_DESC = "ORDER BY id DESC"


def bench_root() -> Path:
    BENCH_ROOT.mkdir(parents=True, exist_ok=True)
    return BENCH_ROOT


def _run(cmd: list[str], cwd: Path, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout, check=False)


def pinned_revision() -> str:
    out = _run(["git", "rev-parse", "HEAD"], REPO_ROOT, timeout=30)
    return out.stdout.strip() if out.returncode == 0 else "HEAD"


def _copy_live_projections(dst: Path) -> None:
    src_omt = REPO_ROOT / ".meta" / ".omt"
    dst_omt = dst / ".meta" / ".omt"
    dst_omt.mkdir(parents=True, exist_ok=True)
    for name in ("harness.ir.json", "nav.index.jsonl"):
        src = src_omt / name
        if src.exists():
            shutil.copy2(src, dst_omt / name)
    # Net bundle: NOT committed — copy from live checkout (TA:115/118).
    for name in ("META_NET.petri.json", "net_state.sidecar.json", "supervisor.overlay.json"):
        src = src_omt / name
        if src.exists():
            shutil.copy2(src, dst_omt / name)


def _seed_bugfix_fault(root: Path) -> None:
    p = root / MODEL_FILE
    if not p.exists():
        return
    text = p.read_text(encoding="utf-8")
    if ORDER_ASC in text:
        p.write_text(text.replace(ORDER_ASC, ORDER_DESC, 1), encoding="utf-8")


def _seed_cross_layer_fault(root: Path) -> None:
    _seed_bugfix_fault(root)
    p = root / UI_FILE
    if not p.exists():
        return
    text = p.read_text(encoding="utf-8")
    anchor = '            for msg in messages:\n                if msg.role != "system":'
    if anchor in text:
        text = text.replace(
            anchor,
            '            for msg in reversed(messages):\n                if msg.role != "system":',
            1,
        )
        p.write_text(text, encoding="utf-8")


def _seed_harness_fault(root: Path) -> None:
    p = root / HARNESS_C
    if not p.exists():
        return
    text = p.read_text(encoding="utf-8")
    if "BUDGET_DIET_PROXIMITY = 64" in text:
        p.write_text(text.replace("BUDGET_DIET_PROXIMITY = 64", "BUDGET_DIET_PROXIMITY = 65", 1), encoding="utf-8")


def _seed_major_scaffold(root: Path) -> None:
    design = root / ".meta" / "software_development_process" / "4.design" / "features" / "feature_990.bench_major"
    design.mkdir(parents=True, exist_ok=True)
    (design / "design_001_bench.md").write_text(
        "# design_001 — bench major fixture\n\nPre-scaffolded by bench setup (TA:121).\n",
        encoding="utf-8",
    )
    stub = root / "src" / "agentx" / "bench_major_demo.py"
    stub.parent.mkdir(parents=True, exist_ok=True)
    stub.write_text("def bench_answer() -> int:\n    return 0\n", encoding="utf-8")


def _seed_resume_ledger(root: Path) -> None:
    base = datetime.now(timezone.utc) - timedelta(hours=1)
    ts = lambda m: (base + timedelta(minutes=m)).strftime("%Y-%m-%dT%H:%M:%SZ")
    records: list[dict[str, Any]] = [
        {"ts": ts(0), "kind": "phase", "session": "ses_bench_resume", "task_type": "minor_feature",
         "phase": "Programming", "scope": "bench resume continuation", "feature": "feature_991.bench_resume"},
        {"ts": ts(1), "kind": "project_link", "feature": "feature_991.bench_resume", "project": "bench_resume"},
        {"ts": ts(2), "kind": "project", "project": "bench_resume", "op": "create"},
    ]
    ledger = root / ".meta" / ".omt" / "ledger.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")
    home = root / ".projects" / "meta" / "bench_resume"
    home.mkdir(parents=True, exist_ok=True)
    (home / "PROJECT.md").write_text("# PROJECT bench_resume\n\n## New Session Quick Start\n\n**Next:** bench resume continuation\n", encoding="utf-8")
    (home / "CURRENT_STATE.md").write_text("# CURRENT_STATE bench_resume\n\n---\n\n## 2026-09-13 (seed)\n\n- seeded entry\n", encoding="utf-8")


def _inject_concurrent_bindings(bundle_dir: Path) -> str:
    """Inject 3 bindings (T-bench pending, one pre-claimed, one spare) via net.state.

    Returns the setup revision (for the B stale-rev claim placeholder).
    Driver runs with sys.path including scripts/omt (TA:118 pattern).
    """
    scripts_dir = str(REPO_ROOT / "scripts" / "omt")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    import os

    os.environ["OMT_NET_DIR"] = str(bundle_dir)
    ledger = bundle_dir / "ledger.jsonl"
    os.environ["OMT_LEDGER_PATH"] = str(ledger)
    os.environ["OMT_COORDINATION_ROOT"] = str(bundle_dir / "coord")
    from net import state as net_state  # type: ignore[import-not-found]

    st = net_state.load(bundle_dir)
    # Ensure pool places exist (live bundle already has them; be tolerant).
    try:
        names = {getattr(p, "name", "") for p in getattr(st.net, "places", [])}
    except Exception:
        names = set()
    _ = names
    # Three bindings: T-bench (claimable), T-bench-held (pre-claimed), T-bench-spare.
    st.task_bindings = [
        {"id": "T-bench", "place": "work_pending", "generation": 0},
        {"id": "T-bench-held", "place": "work_active", "generation": 1, "owner": "worker-2", "session": "ses_setup"},
        {"id": "T-bench-spare", "place": "work_pending", "generation": 0},
    ]
    marking = dict(getattr(st, "live_marking", {}) or {})
    marking["work_pending"] = int(marking.get("work_pending", 0) or 0) + 2
    marking["work_active"] = int(marking.get("work_active", 0) or 0) + 1
    if "agent_attention" not in marking:
        marking["agent_attention"] = 1
    if "feature_ready" not in marking:
        marking["feature_ready"] = 1
    st.live_marking = marking
    net_state.save(bundle_dir, st)
    # Pre-claimed binding needs no ledger claim (setup actor); revision is the anchor.
    for k in ("OMT_NET_DIR", "OMT_LEDGER_PATH", "OMT_COORDINATION_ROOT"):
        os.environ.pop(k, None)
    return str(getattr(st, "revision", 0))


def setup_real(task_id: str, pin_rev: str = "HEAD", prewarm: bool = True) -> dict[str, Any]:
    """Create a pinned-rev worktree sandbox for a real-mode task."""
    root = bench_root()
    rev = pinned_revision() if pin_rev == "HEAD" else pin_rev
    workdir = root / f"{task_id}-{rev[:12]}"
    if workdir.exists():
        shutil.rmtree(workdir, ignore_errors=True)
    out = _run(["git", "worktree", "add", "--detach", str(workdir), rev], REPO_ROOT, timeout=120)
    if out.returncode != 0:
        raise RuntimeError(f"git worktree add failed: {out.stdout}\n{out.stderr}")
    _copy_live_projections(workdir)
    # Fault seeding per task (setup, not counted).
    if task_id == "bugfix":
        _seed_bugfix_fault(workdir)
    elif task_id == "cross_layer":
        _seed_cross_layer_fault(workdir)
    elif task_id == "harness_repair":
        _seed_harness_fault(workdir)
    elif task_id == "major":
        _seed_major_scaffold(workdir)
    elif task_id == "resume":
        _seed_resume_ledger(workdir)
    setup_rev = rev
    if task_id == "concurrent_conflict":
        bundle_dir = workdir / ".meta" / ".omt"
        try:
            setup_rev = _inject_concurrent_bindings(bundle_dir)
        except Exception as exc:
            setup_rev = f"{rev}:inject_failed:{exc}"
    # uv.lock copy (gitignored, TA:125) + pre-warm (not counted).
    lock_src = REPO_ROOT / "uv.lock"
    if lock_src.exists():
        try:
            shutil.copy2(lock_src, workdir / "uv.lock")
        except Exception:
            pass
    if prewarm:
        try:
            _run(["uv", "sync", "--frozen"], workdir, timeout=180)
        except Exception:
            pass
    return {"sandbox": str(workdir), "revision": rev, "setup_revision": setup_rev, "task": task_id}


FIXTURE_APP_JS = 'export function add(a, b) {\n  return a + b + 1;\n}\n'

FIXTURE_TEST_JS = '''import { test, expect } from "bun:test";
import { add } from "../src/app.js";
test("add", () => {
  expect(add(1, 2)).toBe(3);
});
'''


def setup_fixture(task_id: str, base: Path) -> dict[str, Any]:
    """Hermetic mini-repo for golden fixture trials (bun-gated)."""
    sb = Path(base) / f"fixture-{task_id}"
    if sb.exists():
        shutil.rmtree(sb, ignore_errors=True)
    (sb / "src").mkdir(parents=True, exist_ok=True)
    (sb / "tests").mkdir(parents=True, exist_ok=True)
    _copy_live_projections(sb)
    # Empty ledger (clean session start).
    ledger = sb / ".meta" / ".omt" / "ledger.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text("", encoding="utf-8")
    (sb / "src" / "app.js").write_text(FIXTURE_APP_JS, encoding="utf-8")
    (sb / "tests" / "test_app.js").write_text(FIXTURE_TEST_JS, encoding="utf-8")
    (sb / "WORK.md").write_text("# WORK\n\n## Tasks\n\n- [ ] fixture\n", encoding="utf-8")
    return {"sandbox": str(sb), "revision": "fixture", "setup_revision": "0", "task": task_id}


def cleanup(sandbox: str) -> None:
    p = Path(sandbox)
    # Only remove sandboxes under .sandbox/bench or tmp fixture dirs.
    try:
        if str(p).startswith(str(BENCH_ROOT)):
            out = _run(["git", "worktree", "remove", "--force", str(p)], REPO_ROOT, timeout=60)
            if out.returncode != 0:
                shutil.rmtree(p, ignore_errors=True)
        else:
            shutil.rmtree(p, ignore_errors=True)
    except Exception:
        pass
