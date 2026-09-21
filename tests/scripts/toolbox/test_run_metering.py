"""T2 run+metering acceptance — metered run, stats, lint."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CLI = [sys.executable, str(ROOT / "scripts" / "toolbox" / "toolbox.py")]


def run_cli(*args, env_extra=None):
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    out = subprocess.run([*CLI, *args], capture_output=True, text=True, timeout=120, env=env)
    return out


def stats_json():
    out = run_cli("stats", "--format", "json")
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)["data"]


def test_run_metered_increments_stats():
    before = stats_json()
    before_map = {t["id"]: (t["uses"], t["successes"]) for t in before["tools"]}
    before_runs = before["totals"]["runs"]
    out = run_cli(
        "run", "text.json_split", "--", "--text", '["a","b"]',
        env_extra={"TOOLBOX_SESSION": "test", "TOOLBOX_NOTE": "t2-meter-test"},
    )
    assert out.returncode == 0, out.stderr + out.stdout
    assert '"ok": true' in out.stdout.lower() or '"ok":true' in out.stdout.replace(" ", "")
    after = stats_json()
    after_map = {t["id"]: (t["uses"], t["successes"]) for t in after["tools"]}
    assert after_map["text.json_split"][0] == before_map["text.json_split"][0] + 1
    assert after_map["text.json_split"][1] == before_map["text.json_split"][1] + 1
    assert after["totals"]["runs"] == before_runs + 1


def test_run_all_seeds_ok():
    cases = [
        ("git.status_summary", []),
        ("ledger.window_slice", ["--", "--lines", "2"]),
        ("harness.budget_check", []),
        ("text.json_split", ["--", "--text", '["a"]']),
        ("session.pause_note_append", ["--", "--note", "t2-test"]),
    ]
    for tool_id, extra in cases:
        out = run_cli(
            "run", tool_id, *extra,
            env_extra={"TOOLBOX_SESSION": "test", "TOOLBOX_NOTE": "t2-all-seeds"},
        )
        assert out.returncode == 0, f"{tool_id} failed: {out.stdout} {out.stderr}"
        assert "ok" in out.stdout.lower()


def test_stats_shows_uses_and_totals():
    # ensure at least one run happened, then stats reflects it
    run_cli("run", "git.status_summary", env_extra={"TOOLBOX_SESSION": "test"})
    data = stats_json()
    ids = [t["id"] for t in data["tools"]]
    assert "git.status_summary" in ids
    git_row = next(t for t in data["tools"] if t["id"] == "git.status_summary")
    assert git_row["uses"] >= 1
    assert git_row["successes"] >= 1
    assert "success_rate" in git_row
    assert data["totals"]["runs"] >= 1


def test_lint_clean():
    out = run_cli("lint")
    assert out.returncode == 0, out.stdout + out.stderr
    assert "0 errors" in out.stdout
    out_j = run_cli("lint", "--format", "json")
    assert out_j.returncode == 0, out_j.stdout + out_j.stderr
    payload = json.loads(out_j.stdout)
    assert payload["ok"] is True
    assert payload["data"]["errors"] == []
