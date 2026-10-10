"""T2 run+metering acceptance — metered run, stats, lint.

Hermetic (Tier-2): runs against a private per-module TOOLBOX_ROOT
(``hermetic_cli`` fixture) — same seeds/assertions, zero real-DB writes,
xdist-safe. No coverage loss.
"""
import json

from hermetic_toolbox import hermetic_cli  # noqa: F401  (pytest fixture)


def stats_json(run_cli):
    out = run_cli("stats", "--format", "json")
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)["data"]


def test_run_metered_increments_stats(hermetic_cli):
    run_cli = hermetic_cli
    before = stats_json(run_cli)
    before_map = {t["id"]: (t["uses"], t["successes"]) for t in before["tools"]}
    before_runs = before["totals"]["runs"]
    out = run_cli(
        "run", "text.json_split", "--", "--text", '["a","b"]',
        env_extra={"TOOLBOX_SESSION": "test", "TOOLBOX_NOTE": "t2-meter-test"},
    )
    assert out.returncode == 0, out.stderr + out.stdout
    assert '"ok": true' in out.stdout.lower() or '"ok":true' in out.stdout.replace(" ", "")
    after = stats_json(run_cli)
    after_map = {t["id"]: (t["uses"], t["successes"]) for t in after["tools"]}
    assert after_map["text.json_split"][0] == before_map["text.json_split"][0] + 1
    assert after_map["text.json_split"][1] == before_map["text.json_split"][1] + 1
    assert after["totals"]["runs"] == before_runs + 1


def test_run_all_seeds_ok(hermetic_cli):
    run_cli = hermetic_cli
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


def test_stats_shows_uses_and_totals(hermetic_cli):
    run_cli = hermetic_cli
    # ensure at least one run happened, then stats reflects it
    run_cli("run", "git.status_summary", env_extra={"TOOLBOX_SESSION": "test"})
    data = stats_json(run_cli)
    ids = [t["id"] for t in data["tools"]]
    assert "git.status_summary" in ids
    git_row = next(t for t in data["tools"] if t["id"] == "git.status_summary")
    assert git_row["uses"] >= 1
    assert git_row["successes"] >= 1
    assert "success_rate" in git_row
    assert data["totals"]["runs"] >= 1


def test_lint_clean(hermetic_cli):
    run_cli = hermetic_cli
    out = run_cli("lint")
    assert out.returncode == 0, out.stdout + out.stderr
    assert "0 errors" in out.stdout
    out_j = run_cli("lint", "--format", "json")
    assert out_j.returncode == 0, out_j.stdout + out_j.stderr
    payload = json.loads(out_j.stdout)
    assert payload["ok"] is True
    assert payload["data"]["errors"] == []
