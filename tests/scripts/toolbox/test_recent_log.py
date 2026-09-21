"""Promoted tool git.recent_log — scaffold test (T3 gate)."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CLI = [sys.executable, str(ROOT / "scripts" / "toolbox" / "toolbox.py")]


def test_promoted_recent_log_runs():
    out = subprocess.run([*CLI, "run", "git.recent_log"], capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stderr + out.stdout
    assert "ok" in out.stdout.lower()


def test_promoted_recent_log_queryable():
    out = subprocess.run([*CLI, "query", "recent_log", "--format", "json"], capture_output=True, text=True, timeout=30)
    assert out.returncode == 0, out.stderr
    ids = [r["id"] for r in json.loads(out.stdout)["data"]]
    assert "git.recent_log" in ids
