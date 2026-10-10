"""T4 docs+tiers acceptance — tier filtering, tiers map, docs gen/check, snippet budget.

Hermetic (Tier-2): private per-module TOOLBOX_ROOT — docs gen/tamper in tmp,
zero real-*.md writes. No coverage loss.
"""
import json

from hermetic_toolbox import hermetic_cli  # noqa: F401  (pytest fixture)

CORE5 = {
    "git.status_summary",
    "ledger.window_slice",
    "harness.budget_check",
    "text.json_split",
    "session.pause_note_append",
}


def test_list_tier1_is_core5_only(hermetic_cli):
    out = hermetic_cli("list", "--tier", "1", "--format", "json")
    assert out.returncode == 0, out.stderr + out.stdout
    ids = {r["id"] for r in json.loads(out.stdout)["data"]}
    assert ids == CORE5, f"tier1 must be core-5, got {ids}"


def test_list_tier2_is_full_superset(hermetic_cli):
    run_cli = hermetic_cli
    t1 = {r["id"] for r in json.loads(run_cli("list", "--tier", "1", "--format", "json").stdout)["data"]}
    out = run_cli("list", "--tier", "2", "--format", "json")
    assert out.returncode == 0, out.stderr + out.stdout
    ids = {r["id"] for r in json.loads(out.stdout)["data"]}
    assert t1 <= ids, "tier2 must include tier1 core"
    assert "git.recent_log" in ids, "tier2 full must include promoted pilot"
    # tier3 mirrors tier2 (receipt/MVC live in harness, not toolbox)
    out3 = run_cli("list", "--tier", "3", "--format", "json")
    assert out3.returncode == 0, out3.stderr + out3.stdout
    assert {r["id"] for r in json.loads(out3.stdout)["data"]} == ids


def test_query_tier_filter_restricts(hermetic_cli):
    out = hermetic_cli("query", "git", "--tier", "1", "--format", "json")
    assert out.returncode == 0, out.stderr + out.stdout
    ids = [r["id"] for r in json.loads(out.stdout)["data"]]
    assert ids, "tier1 git query must return core tool"
    assert "git.recent_log" not in ids, "tier1 must hide promoted git.recent_log"
    assert "git.status_summary" in ids


def test_tiers_command_mapping(hermetic_cli):
    out = hermetic_cli("tiers", "--format", "json")
    assert out.returncode == 0, out.stderr + out.stdout
    data = json.loads(out.stdout)["data"]
    assert set(data["tier1"]["tools"]) == CORE5
    assert set(data["tier1"]["tools"]) <= set(data["tier2"]["tools"])
    assert set(data["tier2"]["tools"]) == set(data["tier3"]["tools"])
    assert "git.recent_log" in data["tier2"]["tools"]


def test_docs_gen_check_and_stale(hermetic_cli):
    run_cli = hermetic_cli
    ROOT = hermetic_cli.root
    out = run_cli("docs", "--gen")
    assert out.returncode == 0, out.stderr + out.stdout
    assert "snippet=" in out.stdout
    for rel in ("toolbox/categories.md", "toolbox/tools.md",
                "toolbox/STARTUP_SNIPPET.txt", "toolbox/ONBOARDING.md"):
        p = ROOT / rel
        assert p.exists(), f"missing generated {rel}"
        assert p.read_text().strip(), f"empty generated {rel}"
    cats = (ROOT / "toolbox" / "categories.md").read_text()
    assert "Tier-1" in cats and "tier1" in cats.lower()
    assert "git.status_summary" in cats
    tools_md = (ROOT / "toolbox" / "tools.md").read_text()
    assert "git.recent_log" in tools_md and "uv run scripts/toolbox/toolbox.py run" in tools_md
    # fresh check passes
    assert run_cli("docs", "--check").returncode == 0
    # tamper one file -> STALE exit 2, then regen restores fresh
    target = ROOT / "toolbox" / "categories.md"
    orig = target.read_text()
    try:
        target.write_text(orig + "\n<!-- tamper -->\n")
        stale = run_cli("docs", "--check")
        assert stale.returncode == 2, stale.stdout + stale.stderr
        assert "STALE" in stale.stdout
    finally:
        assert run_cli("docs", "--gen").returncode == 0
    assert run_cli("docs", "--check").returncode == 0


def test_startup_snippet_budget(hermetic_cli):
    snippet = (hermetic_cli.root / "toolbox" / "STARTUP_SNIPPET.txt").read_text().strip()
    assert snippet, "snippet must be non-empty"
    assert len(snippet.encode()) <= 120, f"snippet {len(snippet.encode())}B > 120B: {snippet!r}"
    assert "toolbox:" in snippet and "query" in snippet
