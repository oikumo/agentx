"""
Test suite for feature_023: Meta Harness Improvement.

Covers design_001_contract_pinning.md §6 behaviors 2–5 and 8–13 (each test
cites its behavior; behavior 1's carriers are the migrated feature_022 tier_bd
D1 tests, behaviors 6–7 live in tests/scripts/omt/test_opencode_sdk_contract.py):

  2   F14b: after-hook EDIT path reads input.args — a src .py edit introducing
      a NEW mvc_check hard error throws OmtBlock naming the rel path; zero
      errors / warnings-only do not throw (canned-mvc runner mode).
  3   F14c: omt_think tool.execute.after appends the TA digest to the FIRST
      tool result per session only (session.start registration retained —
      asserted by behavior 13's wiring test).
  4   F14c: omt_enforcer after-hook appends the feature_020 nav reminder to
      the FIRST tool result per session only.
  5   Doc claims: AGENTS.md + META_HARNESS.md describe digest/reminder as
      first-tool-result emission (no live "session.start greps" claim).
  8   Default-only named-export guard over omt_nav.ts, omt_status.ts,
      omt_think.ts (regex scan, mirrors feature_021).
  9   omt_enforcer named exports == sanctioned allowlist exactly.
  10  Load-safety: enforcer helper exports invoked with garbage
      plugin-context args ({client…}, undefined, {}) never throw.
  11  Anchored-TA census over the 4 plugins == exactly 2 genuine thoughts
      (enforcer F14 gotcha; think xref).
  12  Runner cwd isolation (F17): feature_022 _run_tool helpers accept a cwd
      parameter; an omt_think call with a tmp cwd writes the index under tmp
      and leaves the repo index byte-unchanged.
  13  Hook wiring: registered hook keys ⊆ sanctioned set; enforcer ⊇
      {tool.execute.before, tool.execute.after}; think ⊇ {tool.execute.after,
      session.start} (session.start = documented INERT allowlist entry — the
      opencode 1.18.3 binary never dispatches it; kept for future SDKs).

Strategy mirrors feature_022: drive the REAL plugins via node runners
(--experimental-strip-types) — _think_gate_runner.mjs after-hook /
after-hook-edit modes, _think_runner.mjs after-hook mode, and the feature_023
_plugin_surface_runner.mjs — no opencode server, no reimplementation.
"""

import json
import re
import shutil
import subprocess
import uuid
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
TEST_DIR = Path(__file__).parent
FEATURE_022 = REPO_ROOT / "tests" / "features" / "feature_022.meta_harness_think_anywhere_v2"
GATE_RUNNER = FEATURE_022 / "_think_gate_runner.mjs"
THINK_RUNNER = FEATURE_022 / "_think_runner.mjs"
SURFACE_RUNNER = TEST_DIR / "_plugin_surface_runner.mjs"
PLUGIN_DIR = REPO_ROOT / ".opencode" / "plugin"
ENFORCER = PLUGIN_DIR / "omt_enforcer.ts"
THINK = PLUGIN_DIR / "omt_think.ts"
NAV = PLUGIN_DIR / "omt_nav.ts"
STATUS = PLUGIN_DIR / "omt_status.ts"
AGENTS_MD = REPO_ROOT / "AGENTS.md"
META_HARNESS = REPO_ROOT / ".meta" / "META_HARNESS.md"
REPO_THOUGHTS_INDEX = REPO_ROOT / ".meta" / ".omt" / "thoughts.jsonl"

NODE = shutil.which("node")
needs_node = pytest.mark.skipif(not NODE, reason="node not available")

# Anchored TA: thought pattern — byte-identical to the plugins' THOUGHT_PATTERN.
THOUGHT_PATTERN = re.compile(r"^\s*(#|//|/\*|<!--|--)\s*TA:")

# Sanctioned named exports of omt_enforcer.ts (feature_023 §4): any NEW named
# export fails the allowlist (un-exporting breaks 3 runner fixtures + the
# lifecycle e2e, so the pin is sanctioned-export + load-safety).
SANCTIONED_ENFORCER_EXPORTS = {
    "isDocPath", "navGateDecision", "thinkGateDecision",
    "hasConsultedThoughts", "fileThoughtsIn", "OmtEnforcer",
}

# Sanctioned registered-hook keys across all 4 plugins. session.start is the
# documented INERT entry (opencode 1.18.3 never dispatches it — binary audit,
# analysis_001 addendum; registrations retained for future SDKs). event is a
# typed SDK hook (session.idle MVC++ sweep — feature_006, out of F14c scope).
SANCTIONED_HOOK_KEYS = {
    "tool", "tool.execute.before", "tool.execute.after", "session.start", "event",
}


def _marker() -> str:
    return "TAUTOMARK_" + uuid.uuid4().hex[:8]


def _write_tmp(tmp_path: Path, name: str, content: str = "") -> Path:
    p = tmp_path / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


def _read_call(path: Path, session: str, tool: str = "read") -> dict:
    """Fake after-hook invocation, REAL SDK shape (args on input — F14)."""
    return {
        "input": {"tool": tool, "sessionID": session, "callID": "c1",
                  "args": {"filePath": str(path)}},
        "output": {"title": tool, "output": "ORIG", "metadata": {}},
    }


def _after_hook_batch(directory: Path, calls: list[dict]):
    """Drive the REAL OmtEnforcer tool.execute.after through a batch on ONE
    plugin instance; return the mutated output dicts or None."""
    if not NODE:
        return None
    proc = subprocess.run(
        [NODE, "--experimental-strip-types", str(GATE_RUNNER), "after-hook",
         str(directory), json.dumps(calls)],
        capture_output=True, text=True, cwd=REPO_ROOT, timeout=30,
    )
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def _after_hook_edit_batch(directory: Path, findings: list[dict], calls: list[dict]):
    """Drive the REAL OmtEnforcer after-hook EDIT path with canned mvc findings;
    return [{blocked:bool, message?}] or None."""
    if not NODE:
        return None
    proc = subprocess.run(
        [NODE, "--experimental-strip-types", str(GATE_RUNNER), "after-hook-edit",
         str(directory), json.dumps({"findings": findings, "calls": calls})],
        capture_output=True, text=True, cwd=REPO_ROOT, timeout=30,
    )
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def _think_after_hook_batch(cwd: Path, calls: list[dict]):
    """Drive the REAL omt_think tool.execute.after through a batch on ONE plugin
    instance (cwd isolates the digest grep + index); return outputs or None."""
    if not NODE:
        return None
    proc = subprocess.run(
        [NODE, "--experimental-strip-types", str(THINK_RUNNER), "after-hook",
         json.dumps(calls)],
        capture_output=True, text=True, cwd=cwd, timeout=60,
    )
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def _surface(mode: str, *args: str):
    """Run the plugin-surface runner; return parsed JSON or None."""
    if not NODE:
        return None
    proc = subprocess.run(
        [NODE, "--experimental-strip-types", str(SURFACE_RUNNER), mode, *args],
        capture_output=True, text=True, cwd=REPO_ROOT, timeout=30,
    )
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


# ---------------------------------------------------------------------------
# Behavior 2 — F14b: after-hook edit path reads input.args (canned mvc)
# ---------------------------------------------------------------------------
@needs_node
class TestF14bEditPathGate:
    def test_new_hard_error_blocks_naming_rel(self, tmp_path):
        """design §6.2a — src .py edit with 1 NEW canned mvc error finding →
        OmtBlock thrown naming the rel path (hardSnapshot empty → any error
        counts as introduced — correct for the test)."""
        target = tmp_path / "src" / "x.py"
        findings = [{"severity": "error", "rule": "ERR_M2V",
                     "file": "src/x.py", "line": 1, "message": "model imports view"}]
        results = _after_hook_edit_batch(tmp_path, findings, [_read_call(target, "s1", tool="edit")])
        assert results is not None, "after-hook-edit runner failed"
        assert results[0]["blocked"], f"new hard error must block: {results[0]}"
        assert "src/x.py" in results[0]["message"], (
            f"block must name the rel path: {results[0]['message']!r}")
        assert "ERR_M2V" in results[0]["message"], (
            f"block must name the rule: {results[0]['message']!r}")

    def test_zero_errors_no_throw(self, tmp_path):
        """design §6.2b — 0 error findings → no throw."""
        target = tmp_path / "src" / "x.py"
        results = _after_hook_edit_batch(tmp_path, [], [_read_call(target, "s1", tool="edit")])
        assert results is not None, "after-hook-edit runner failed"
        assert results[0]["blocked"] is False, f"zero errors must not block: {results[0]}"

    def test_warnings_only_no_throw(self, tmp_path):
        """design §6.2c — warnings-only findings → no throw (advisory notify
        is client-null-safe)."""
        target = tmp_path / "src" / "x.py"
        findings = [{"severity": "warning", "rule": "WRN_GOD_CTL",
                     "file": "src/x.py", "line": 3, "message": "controller too large"}]
        results = _after_hook_edit_batch(tmp_path, findings, [_read_call(target, "s1", tool="edit")])
        assert results is not None, "after-hook-edit runner failed"
        assert results[0]["blocked"] is False, f"warnings-only must not block: {results[0]}"


# ---------------------------------------------------------------------------
# Behavior 3 — F14c: omt_think after-hook carries the TA digest (live path)
# ---------------------------------------------------------------------------
@needs_node
class TestThinkAfterHookDigest:
    def test_digest_first_tool_result_per_session_only(self, tmp_path):
        """design §6.3 — first tool.execute.after per session appends
        thinkDigest() to output.output (same mutation channel as D1 —
        guaranteed agent-visible); second call same session does not; a new
        session does. Digest greps the cwd → seeded thought inside tmp cwd."""
        m = _marker()
        _write_tmp(tmp_path, "t.py", f"# TA: gotcha: {m}\nx = 1\n")
        calls = [_read_call(tmp_path / "t.py", "s1"),
                 _read_call(tmp_path / "t.py", "s1"),
                 _read_call(tmp_path / "t.py", "s2")]
        results = _think_after_hook_batch(tmp_path, calls)
        assert results is not None, "think after-hook runner failed (hook missing?)"
        out0 = results[0]["output"]
        assert out0.startswith("ORIG"), f"original output must be preserved: {out0!r}"
        assert "THINK-ANYWHERE" in out0, f"digest missing on first call: {out0!r}"
        assert m in out0, f"digest must surface the seeded thought: {out0!r}"
        assert "THINK-ANYWHERE" not in results[1]["output"], (
            f"same session must not re-digest: {results[1]['output']!r}")
        assert m not in results[1]["output"], (
            f"same session must not re-digest: {results[1]['output']!r}")
        assert m in results[2]["output"], "new session must get the digest"


# ---------------------------------------------------------------------------
# Behavior 4 — F14c: omt_enforcer after-hook carries the nav reminder (live)
# ---------------------------------------------------------------------------
@needs_node
class TestEnforcerNavReminderLive:
    def test_nav_reminder_first_tool_result_per_session_only(self, tmp_path):
        """design §6.4 — first after-hook call per session appends
        navReminderMsg() to output.output (any tool, before the read/edit
        branches); second call same session does not; a new session does."""
        clean = _write_tmp(tmp_path, "clean.py", "y = 2\n")
        calls = [_read_call(clean, "s1"), _read_call(clean, "s1"), _read_call(clean, "s2")]
        results = _after_hook_batch(tmp_path, calls)
        assert results is not None, "after-hook runner failed"
        assert "NAVIGATION TIP" in results[0]["output"], (
            f"first call must carry the nav reminder: {results[0]['output']!r}")
        assert "NAVIGATION TIP" not in results[1]["output"], (
            f"same session must not re-remind: {results[1]['output']!r}")
        assert "NAVIGATION TIP" in results[2]["output"], (
            "new session must get the nav reminder")


# ---------------------------------------------------------------------------
# Behavior 5 — doc claims describe the live first-tool-result path
# ---------------------------------------------------------------------------
class TestDocClaimsLivePath:
    def test_agents_md_digest_claim_is_live_path(self):
        """design §6.5 — AGENTS.md must NOT claim 'every session.start greps'
        (never dispatched — F14c); it must describe first-tool-result emission."""
        text = AGENTS_MD.read_text(encoding="utf-8")
        assert "every session.start greps" not in text, (
            "AGENTS.md still claims the dead session.start path")
        digest_lines = [l for l in text.splitlines()
                        if "digest" in l.lower() and "TA:" in l]
        assert any("first tool result" in l for l in digest_lines), (
            f"AGENTS.md must describe first-tool-result emission: {digest_lines!r}")

    def test_meta_harness_digest_and_nav_claims_are_live_path(self):
        """design §6.5 — META_HARNESS.md THINK_DIGEST + XREF_NAV_ENF lines
        describe the live path (first tool result), not session.start."""
        lines = META_HARNESS.read_text(encoding="utf-8").splitlines()
        digest = next((l for l in lines if l.startswith("THINK_DIGEST:")), "")
        assert digest, "THINK_DIGEST line missing from META_HARNESS.md"
        assert "session.start greps" not in digest, (
            f"THINK_DIGEST still claims the dead session.start path: {digest!r}")
        assert "first tool result" in digest, (
            f"THINK_DIGEST must describe first-tool-result emission: {digest!r}")
        nav = next((l for l in lines if l.startswith("XREF_NAV_ENF:")), "")
        assert nav, "XREF_NAV_ENF line missing from META_HARNESS.md"
        assert "session.start reminder" not in nav, (
            f"XREF_NAV_ENF still claims the dead session.start path: {nav!r}")
        assert "first tool result" in nav or "first-tool-result" in nav, (
            f"XREF_NAV_ENF must describe first-tool-result emission: {nav!r}")


# ---------------------------------------------------------------------------
# Behavior 8 — default-only named-export guard (regex scan, 3 plugins)
# ---------------------------------------------------------------------------
class TestDefaultOnlyExports:
    @pytest.mark.parametrize("plugin", [NAV, STATUS, THINK],
                             ids=["omt_nav", "omt_status", "omt_think"])
    def test_no_named_exports_except_default(self, plugin: Path):
        """design §6.8 — DEFECT-A load-crash class: opencode's loader calls
        EVERY named export at load time; these 3 plugins must export ONLY
        `export default` (mirrors feature_021's guard over omt_think)."""
        named = []
        for i, line in enumerate(plugin.read_text(encoding="utf-8").splitlines(), 1):
            s = line.strip()
            if s.startswith("//") or s.startswith("*") or s.startswith("/*"):
                continue
            if re.match(r"^export\b", s) and not s.startswith("export default"):
                named.append(f"  L{i}: {s}")
        assert not named, (
            f"{plugin.name} must have NO named exports except `export default` "
            "(opencode's loader calls every named export → load crash). Found:\n"
            + "\n".join(named))


# ---------------------------------------------------------------------------
# Behaviors 9+10 — enforcer export allowlist + load-safety
# ---------------------------------------------------------------------------
@needs_node
class TestEnforcerExportSurface:
    def test_named_exports_equal_sanctioned_allowlist(self):
        """design §6.9 — omt_enforcer named exports == sanctioned set exactly;
        any NEW named export fails (each is load-crash surface)."""
        result = _surface("exports", str(ENFORCER))
        assert result is not None, "surface runner failed (plugin load error?)"
        assert set(result["named"]) == SANCTIONED_ENFORCER_EXPORTS, (
            f"export drift: {sorted(result['named'])} != sanctioned "
            f"{sorted(SANCTIONED_ENFORCER_EXPORTS)}")

    def test_load_safety_garbage_args_never_throw(self):
        """design §6.10 — every named FUNCTION export (except the OmtEnforcer
        factory) invoked with the plugin-context-shaped garbage arg, undefined,
        and {} must not throw (the property the opencode loader relies on)."""
        result = _surface("exports", str(ENFORCER))
        assert result is not None, "surface runner failed (plugin load error?)"
        failures = {
            name: calls for name, calls in result["calls"].items()
            if any(v != "ok" for v in calls.values())
        }
        assert not failures, f"load-safety violations (must never throw): {failures}"


# ---------------------------------------------------------------------------
# Behavior 11 — anchored-TA census over the 4 plugins
# ---------------------------------------------------------------------------
class TestTACensus:
    def test_exactly_two_genuine_thoughts(self):
        """design §6.11 — exactly 2 anchored TA: hits across the 4 plugins:
        the genuine F14 gotcha in omt_enforcer.ts and the xref in omt_think.ts
        (drift-resistant: pinned by file+substring, not line)."""
        hits = []
        for plugin in (ENFORCER, THINK, NAV, STATUS):
            for i, line in enumerate(plugin.read_text(encoding="utf-8").splitlines(), 1):
                if THOUGHT_PATTERN.match(line):
                    hits.append((plugin.name, i, line.strip()))
        assert len(hits) == 2, (
            f"expected exactly 2 anchored TA: thoughts across the 4 plugins, "
            f"got {len(hits)}: {hits}")
        enforcer_hits = [h for h in hits if h[0] == "omt_enforcer.ts"]
        think_hits = [h for h in hits if h[0] == "omt_think.ts"]
        assert len(enforcer_hits) == 1 and "F14" in enforcer_hits[0][2], (
            f"the enforcer hit must be the genuine F14 gotcha: {enforcer_hits}")
        assert len(think_hits) == 1 and "xref" in think_hits[0][2], (
            f"the think hit must be the genuine feature_022 xref: {think_hits}")


# ---------------------------------------------------------------------------
# Behavior 12 — runner cwd isolation (F17)
# ---------------------------------------------------------------------------
@needs_node
class TestRunnerCwdIsolation:
    @pytest.mark.parametrize("test_file", [
        "test_omt_think_v2.py",
        "test_omt_think_v2_tier_bd.py",
        "test_omt_think_v2_tier_c.py",
        "test_omt_think_v2_tier_remainder.py",
    ])
    def test_feature_022_run_tool_accepts_cwd(self, test_file: str):
        """design §6.12 — all 4 feature_022 _run_tool helpers gain a cwd
        parameter (F17 fix channel: call sites pass the per-test tmp_path so
        tool calls never touch the repo index/ledger)."""
        src = (FEATURE_022 / test_file).read_text(encoding="utf-8")
        m = re.search(r"def _run_tool\(([^)]*)\)", src, re.DOTALL)
        assert m, f"_run_tool not found in {test_file}"
        assert "cwd" in m.group(1), (
            f"{test_file}::_run_tool must accept a cwd parameter (F17 isolation)")

    def test_tool_call_with_tmp_cwd_leaves_repo_index_untouched(self, tmp_path):
        """design §6.12 — invoke the REAL omt_think via the runner with
        cwd=tmp_path: the index is written under tmp and the repo
        .meta/.omt/thoughts.jsonl is byte-unchanged."""
        before = (REPO_THOUGHTS_INDEX.read_bytes()
                  if REPO_THOUGHTS_INDEX.exists() else None)
        f = _write_tmp(tmp_path, "iso.py", "x = 1\n")
        assert NODE, "node not available"
        proc = subprocess.run(
            [NODE, "--experimental-strip-types", str(THINK_RUNNER), "omt_think",
             json.dumps({"path": str(f), "thought": f"m {_marker()}"})],
            capture_output=True, text=True, cwd=tmp_path, timeout=30,
        )
        assert proc.returncode == 0, f"runner failed: {proc.stderr!r}"
        tmp_index = tmp_path / ".meta" / ".omt" / "thoughts.jsonl"
        assert tmp_index.exists(), (
            "tmp-cwd tool call must write the index under the tmp cwd")
        after = (REPO_THOUGHTS_INDEX.read_bytes()
                 if REPO_THOUGHTS_INDEX.exists() else None)
        assert after == before, "repo thoughts.jsonl must be byte-unchanged"


# ---------------------------------------------------------------------------
# Behavior 13 — hook wiring (registered keys vs sanctioned set)
# ---------------------------------------------------------------------------
@needs_node
class TestHookWiring:
    def test_enforcer_hooks(self, tmp_path):
        """design §6.13 — enforcer registers ⊇ {tool.execute.before,
        tool.execute.after}; every registered key ∈ sanctioned set."""
        result = _surface("hooks", str(ENFORCER), "OmtEnforcer", str(tmp_path))
        assert result is not None, "surface runner failed (plugin load error?)"
        hooks = set(result["hooks"])
        assert {"tool.execute.before", "tool.execute.after"} <= hooks, (
            f"enforcer missing required hooks: {sorted(hooks)}")
        assert hooks <= SANCTIONED_HOOK_KEYS, (
            f"enforcer registers unsanctioned hooks: {sorted(hooks - SANCTIONED_HOOK_KEYS)}")

    def test_think_hooks(self, tmp_path):
        """design §6.13 (+§6.3 retention) — think registers ⊇
        {tool.execute.after (live digest path), session.start (retained,
        inert)}; every registered key ∈ sanctioned set."""
        result = _surface("hooks", str(THINK), "default", str(tmp_path))
        assert result is not None, "surface runner failed (plugin load error?)"
        hooks = set(result["hooks"])
        assert {"tool.execute.after", "session.start"} <= hooks, (
            f"think missing required hooks (after-hook digest + retained "
            f"session.start): {sorted(hooks)}")
        assert hooks <= SANCTIONED_HOOK_KEYS, (
            f"think registers unsanctioned hooks: {sorted(hooks - SANCTIONED_HOOK_KEYS)}")

    @pytest.mark.parametrize("plugin", [NAV, STATUS], ids=["omt_nav", "omt_status"])
    def test_nav_status_hooks_sanctioned(self, plugin: Path, tmp_path):
        """design §6.13 — every key registered by the remaining plugins is in
        the sanctioned set (renamed/typo'd hooks fail here)."""
        result = _surface("hooks", str(plugin), "default", str(tmp_path))
        assert result is not None, f"surface runner failed for {plugin.name}"
        hooks = set(result["hooks"])
        assert hooks <= SANCTIONED_HOOK_KEYS, (
            f"{plugin.name} registers unsanctioned hooks: "
            f"{sorted(hooks - SANCTIONED_HOOK_KEYS)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
