#!/usr/bin/env python3
"""Tasks Options vs Projects active drift pin (startup-menu staleness bug).

Symptom: the session-startup TASKS menu listed complete `harness_reason`
while missing active `meta_harness_14`/`meta_harness_15` — the `## Tasks`
`Options:` block had not been resynced after the `## Projects` table moved
on, and `harnessc check` stayed green because `check_work_tasks_canonical`
(pool branch) only verified Pool counts, never `Options:`.

Pins:
1. `_tasks_options_proj_drift` pure helper: stale Options → missing+extra;
   fresh Options → [].
2. `check_work_tasks_canonical` wiring: stale WORK.md → error mentioning
   `Options proj drift`; fresh WORK.md → no such error (live-net faked).

Run with:
    uv run pytest tests/scripts/omt/test_tasks_options_drift.py -q
"""
from __future__ import annotations

import sys
import types
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "omt"))

import harnessc  # noqa: E402


STALE_TASKS = """## Tasks
<!-- net_rev:60 -->
NEXT: proj:alpha (recommended)
Other enabled: none
Blocked: none
Resources: 4/4 free
Pool: pending=0 active=0 done=7 (places 15/15)
Options: proj:alpha, proj:stale_complete, unscoped:001
Lanes: verification 0/1 free 1, integration 0/1 free 1
"""

FRESH_TASKS = """## Tasks
<!-- net_rev:60 -->
NEXT: proj:alpha (recommended)
Other enabled: none
Blocked: none
Resources: 4/4 free
Pool: pending=0 active=0 done=7 (places 15/15)
Options: proj:alpha, proj:beta, unscoped:001
Lanes: verification 0/1 free 1, integration 0/1 free 1
"""

PROJECTS = """## Projects (synced — do not hand-edit)

| project | state | features |
|---|---|---|
| alpha | active | feature_001.x |
| beta | active | feature_002.y |
| stale_complete | complete | feature_003.z |
"""


def test_helper_flags_stale_options() -> None:
    drift = harnessc._tasks_options_proj_drift(STALE_TASKS, PROJECTS)
    assert "missing:beta" in drift
    assert "extra:stale_complete" in drift


def test_helper_clean_on_fresh_options() -> None:
    assert harnessc._tasks_options_proj_drift(FRESH_TASKS, PROJECTS) == []


def _install_fake_net(monkeypatch, marking: dict) -> None:
    """Fake the live pool net behind check_work_tasks_canonical (no disk net)."""
    pkg = types.ModuleType("net")
    pkg.__path__ = []  # mark as package so `from net import state` resolves
    fake_state = types.ModuleType("net.state")

    class _Net:
        pass

    fake_state.net_dir = lambda: Path("/nonexistent")
    fake_state.is_bootstrapped = lambda _base: True
    fake_state.load = lambda _base: types.SimpleNamespace(net=_Net(), live_marking=dict(marking))
    fake_sync_md = types.ModuleType("net.sync_md")
    fake_sync_md.render_tasks_block = lambda *a, **k: ""
    fake_sync_md.parse_tasks_block = lambda _t: {}
    fake_sync_md.pool_counts = lambda _m: {
        "work_pending": 0, "work_active": 0, "work_done": 7}
    fake_sync_md.is_pool_net = lambda _net: True
    pkg.state = fake_state  # noqa: SLF001
    pkg.sync_md = fake_sync_md  # noqa: SLF001
    monkeypatch.setitem(sys.modules, "net", pkg)
    monkeypatch.setitem(sys.modules, "net.state", fake_state)
    monkeypatch.setitem(sys.modules, "net.sync_md", fake_sync_md)


def _write_work(tmp_path: Path, tasks: str) -> None:
    (tmp_path / "WORK.md").write_text(
        "# WORK\n\n" + tasks + "\n" + PROJECTS + "\n## Paused\n", encoding="utf-8")


def test_check_flags_stale_options(tmp_path, monkeypatch) -> None:
    _write_work(tmp_path, STALE_TASKS)
    _install_fake_net(monkeypatch, {"work_pending": 0, "work_active": 0, "work_done": 7})
    monkeypatch.setattr(harnessc, "REPO_ROOT", tmp_path)
    c = harnessc.Corpus([])
    harnessc.check_work_tasks_canonical(c)
    assert any("Options proj drift" in e for e in c.errors), c.errors
    assert any("missing:beta" in e for e in c.errors), c.errors
    assert any("extra:stale_complete" in e for e in c.errors), c.errors


def test_check_clean_on_fresh_options(tmp_path, monkeypatch) -> None:
    _write_work(tmp_path, FRESH_TASKS)
    _install_fake_net(monkeypatch, {"work_pending": 0, "work_active": 0, "work_done": 7})
    monkeypatch.setattr(harnessc, "REPO_ROOT", tmp_path)
    c = harnessc.Corpus([])
    harnessc.check_work_tasks_canonical(c)
    assert c.errors == [], c.errors
