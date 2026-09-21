"""T1 query acceptance — ranked query, list/show, sync stale detection."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CLI = [sys.executable, str(ROOT / "scripts" / "toolbox" / "toolbox.py")]


def run_cli(*args):
    out = subprocess.run([*CLI, *args], capture_output=True, text=True, timeout=30)
    return out


def test_query_ranks_git_tool_first():
    out = run_cli("query", "git dirty status", "--format", "json")
    assert out.returncode == 0, out.stderr
    payload = json.loads(out.stdout)
    assert payload["ok"]
    assert payload["data"], "query returned no tools"
    assert payload["data"][0]["id"] == "git.status_summary"


def test_query_tdd_prose_finds_text_tool():
    out = run_cli("query", "tdd behaviors prose", "--format", "json")
    assert out.returncode == 0, out.stderr
    ids = [r["id"] for r in json.loads(out.stdout)["data"]]
    assert "text.json_split" in ids


def test_list_category_and_show():
    out = run_cli("list", "--category", "git", "--format", "json")
    assert out.returncode == 0, out.stderr
    ids = [r["id"] for r in json.loads(out.stdout)["data"]]
    assert "git.status_summary" in ids  # growth-compatible: T3+ may add git.* tools
    out = run_cli("show", "ledger.window_slice", "--format", "json")
    assert out.returncode == 0, out.stderr
    assert json.loads(out.stdout)["data"]["id"] == "ledger.window_slice"


def test_sync_check_fresh_and_stale(tmp_path=None):
    fresh = run_cli("sync", "--check")
    assert fresh.returncode == 0, fresh.stdout + fresh.stderr
    assert "fresh" in fresh.stdout
    # tamper a copy check: corrupt index.json rev in-memory by direct read/compare
    idx = ROOT / "toolbox" / "index.json"
    orig = idx.read_text()
    try:
        data = json.loads(orig)
        data["rev"] = "0-stale-test"
        idx.write_text(json.dumps(data))
        stale = run_cli("sync", "--check")
        assert stale.returncode == 2, stale.stdout + stale.stderr
        assert "STALE" in stale.stdout
    finally:
        idx.write_text(orig)
    assert run_cli("sync", "--check").returncode == 0
