"""Promoted tool git.recent_log — scaffold test (T3 gate).

Hermetic (Tier-2): private per-module TOOLBOX_ROOT. No coverage loss.
"""
import json

from hermetic_toolbox import hermetic_cli  # noqa: F401  (pytest fixture)


def test_promoted_recent_log_runs(hermetic_cli):
    out = hermetic_cli("run", "git.recent_log")
    assert out.returncode == 0, out.stderr + out.stdout
    assert "ok" in out.stdout.lower()


def test_promoted_recent_log_queryable(hermetic_cli):
    out = hermetic_cli("query", "recent_log", "--format", "json")
    assert out.returncode == 0, out.stderr
    ids = [r["id"] for r in json.loads(out.stdout)["data"]]
    assert "git.recent_log" in ids
