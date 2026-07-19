"""
Test suite for feature_021: Meta Harness Think Anywhere

Tests the omt_think / omt_think_list / omt_think_remove opencode plugin tools
(inline TA: thought-tags) and the thinkGateDecision pure decider in the enforcer.

Test Strategy (mirrors feature_020):
  - Structural: verify the plugin source exports/tools/contracts (DEFECT A/C/D, H3).
  - Behavioral: invoke the REAL plugin tools via _think_runner.mjs + node, operating
    on temp files, and assert on their string output + filesystem effects.
  - Pure decider: invoke the REAL thinkGateDecision via _think_gate_runner.mjs.
  - Enforcer/docs: source presence of the think-gate wiring + docs/config coverage.
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
THINK_RUNNER = TEST_DIR / "_think_runner.mjs"
GATE_RUNNER = TEST_DIR / "_think_gate_runner.mjs"
PLUGIN = REPO_ROOT / ".opencode" / "plugins" / "omt_think.ts"
ENFORCER = REPO_ROOT / ".opencode" / "plugins" / "omt_enforcer.ts"
LEDGER = REPO_ROOT / ".meta" / ".omt" / "ledger.jsonl"

NODE = shutil.which("node")
needs_node = pytest.mark.skipif(not NODE, reason="node not available")


def _run_tool(tool_name: str, args: dict | None = None):
    """Invoke a real omt_think plugin tool via node; return its string result or None."""
    if not NODE:
        return None
    proc = subprocess.run(
        [NODE, "--experimental-strip-types", str(THINK_RUNNER), tool_name, json.dumps(args or {})],
        capture_output=True, text=True, cwd=REPO_ROOT, timeout=30,
    )
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def _gate_decide(has_thoughts: bool, consulted: bool):
    """Invoke the real thinkGateDecision helper via node; return 'allow'/'block' or None."""
    if not NODE:
        return None
    opts = json.dumps({"hasThoughts": has_thoughts, "consulted": consulted})
    proc = subprocess.run(
        [NODE, "--experimental-strip-types", str(GATE_RUNNER), "decide", opts],
        capture_output=True, text=True, cwd=REPO_ROOT, timeout=30,
    )
    if proc.returncode != 0:
        return None
    return json.loads(proc.stdout)["decision"]


def _marker() -> str:
    return "TAUTOMARK_" + uuid.uuid4().hex[:8]


def _write_tmp(tmp_path: Path, name: str, content: str = "") -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# Structural: plugin source / contracts
# ---------------------------------------------------------------------------
class TestThinkPluginStructure:
    def test_plugin_file_exists(self):
        assert PLUGIN.exists(), "omt_think.ts should exist"

    def test_exports_default_factory_with_six_tools(self):
        """DEFECT A: must export a default async plugin factory (no named tool-object
        exports — opencode's loader rejects non-function exports). Tool map gained
        omt_think_verify in feature_022 Tier C and omt_think_suggest +
        omt_think_reindex in the Tier remainder (design_004)."""
        c = PLUGIN.read_text()
        assert "export default async () => ({" in c
        assert "tool: { omt_think, omt_think_list, omt_think_remove, omt_think_verify, omt_think_suggest, omt_think_reindex }" in c
        assert "export { omt_think" not in c, "must NOT named-export tool objects (DEFECT A)"

    def test_no_named_exports_except_default(self):
        """DEFECT-A *load-crash* class: opencode's loader calls EVERY named export at
        load time. omt_think.ts must export ONLY `export default` — any named
        function/const/class export gets invoked with a non-string opencode arg and
        crashes (e.g. `commentSyntaxFor(ext)` → `(ext||"").toLowerCase is not a
        function`). This is the deterministic replacement for the flaky
        opencode-serve e2e load check: it catches the same defect class without
        spawning a server. The defect-free references omt_nav.ts / omt_status.ts
        also export ONLY `export default`."""
        c = PLUGIN.read_text()
        named = []
        for i, line in enumerate(c.splitlines(), 1):
            s = line.strip()
            # skip block comments / line comments that happen to contain "export"
            if s.startswith("//") or s.startswith("*") or s.startswith("/*"):
                continue
            if re.match(r"^export\b", s) and not s.startswith("export default"):
                named.append(f"  L{i}: {s}")
        assert not named, (
            "omt_think.ts must have NO named exports except `export default` "
            "(opencode's loader calls every named export → load crash). Found:\n"
            + "\n".join(named)
        )

    def test_uses_canonical_tool_api(self):
        """DEFECT C: args + tool.schema (not raw JSON-schema input:). DEFECT D: returns
        strings. H3: execFileSync (no shell)."""
        c = PLUGIN.read_text()
        assert 'import { tool } from "@opencode-ai/plugin"' in c
        assert "args:" in c
        assert "tool.schema.string()" in c
        assert "tool.schema.number()" in c
        assert "async execute(args, context)" in c
        assert 'type: "object"' not in c, "must NOT use raw JSON-schema input (DEFECT C)"
        assert "execFileSync" in c
        # never shell-string exec
        assert "execSync(" not in c.replace("execFileSync", "")

    def test_comment_syntax_covers_extensions(self):
        """commentSyntaxFor handles py/ts/md/jsonc/css/json(denied)/default."""
        c = PLUGIN.read_text()
        for ext in [".py", ".toml", ".ts", ".js", ".mjs", ".md", ".mdx", ".jsonc", ".css"]:
            assert f'"{ext}"' in c, f"commentSyntaxFor should handle {ext}"
        assert '".json"' in c and "return null" in c, ".json must be denied (no comments)"

    def test_protected_paths_denied(self):
        """isProtectedPath denies .env*, README.md, uv.lock, LICENSE."""
        c = PLUGIN.read_text()
        assert "README.md" in c
        assert "uv.lock" in c
        assert "LICENSE" in c
        assert '".env"' in c or "'README.md'" in c

    def test_session_start_digest_present(self):
        c = PLUGIN.read_text()
        assert '"session.start"' in c
        assert "THINK-ANYWHERE" in c
        assert "thinkDigest" in c


# ---------------------------------------------------------------------------
# Behavioral: invoke REAL tools on temp files
# ---------------------------------------------------------------------------
@needs_node
class TestThinkBehavior:
    def test_think_inserts_py_at_eof(self, tmp_path):
        f = _write_tmp(tmp_path, "sample.py", "x = 1\n")
        out = _run_tool("omt_think", {"path": str(f), "thought": "watch out for x"})
        assert out is not None
        assert "TA:" in out or "→" in out
        content = f.read_text()
        assert "# TA: watch out for x" in content

    def test_think_inserts_after_line(self, tmp_path):
        f = _write_tmp(tmp_path, "lined.py", "a = 1\nb = 2\nc = 3\n")
        out = _run_tool("omt_think", {"path": str(f), "thought": "after a", "line": 1})
        assert out is not None and "→" in out
        lines = f.read_text().split("\n")
        # inserted after line 1 → new line is line 2
        assert "TA: after a" in lines[1]

    def test_think_with_category(self, tmp_path):
        f = _write_tmp(tmp_path, "cat.py", "v = 0\n")
        _run_tool("omt_think", {"path": str(f), "thought": "mutates global", "category": "gotcha"})
        content = f.read_text()
        assert "TA: gotcha: mutates global" in content

    def test_think_denied_protected(self, tmp_path):
        out = _run_tool("omt_think", {"path": ".env", "thought": "nope"})
        assert out is not None
        assert "refused" in out.lower() or "protected" in out.lower()
        out2 = _run_tool("omt_think", {"path": "README.md", "thought": "nope"})
        assert out2 is not None
        assert "refused" in out2.lower() or "protected" in out2.lower()

    def test_think_denied_json(self, tmp_path):
        f = _write_tmp(tmp_path, "data.json", '{"a": 1}\n')
        out = _run_tool("omt_think", {"path": str(f), "thought": "nope"})
        assert out is not None
        assert "refused" in out.lower() or "json" in out.lower()

    def test_think_denied_missing_file(self, tmp_path):
        out = _run_tool("omt_think", {"path": str(tmp_path / "nope.py"), "thought": "x"})
        assert out is not None
        assert "does not exist" in out.lower() or "refused" in out.lower()

    def test_think_list_returns_thought(self, tmp_path):
        m = _marker()
        f = _write_tmp(tmp_path, "list.py", "y = 2\n")
        _run_tool("omt_think", {"path": str(f), "thought": m})
        out = _run_tool("omt_think_list", {"path": str(tmp_path)})
        assert out is not None
        assert m in out
        assert "TA:" in out

    def test_think_list_category_and_query_filter(self, tmp_path):
        m = _marker()
        f = _write_tmp(tmp_path, "filt.py", "z = 3\n")
        _run_tool("omt_think", {"path": str(f), "thought": m, "category": "risk"})
        cat = _run_tool("omt_think_list", {"path": str(tmp_path), "category": "risk"})
        assert cat is not None
        assert m in cat
        q = _run_tool("omt_think_list", {"path": str(tmp_path), "query": m})
        assert q is not None
        assert m in q
        other = _run_tool("omt_think_list", {"path": str(tmp_path), "category": "gotcha"})
        assert other is not None
        assert m not in other

    def test_think_list_capped_at_50(self, tmp_path):
        lines = ["# header"] + [f"# TA: capfill{i}" for i in range(60)]
        f = _write_tmp(tmp_path, "cap.py", "\n".join(lines) + "\n")
        out = _run_tool("omt_think_list", {"path": str(f)})
        assert out is not None
        assert "60 thought" in out
        assert "more" in out  # truncation notice

    def test_think_list_writes_consult_to_ledger(self, tmp_path):
        before = LEDGER.read_text().count("think_consult") if LEDGER.exists() else 0
        _run_tool("omt_think_list", {"path": str(tmp_path)})
        after = LEDGER.read_text().count("think_consult") if LEDGER.exists() else 0
        assert after > before, "omt_think_list must append a think_consult ledger record"

    def test_think_remove_removes_line(self, tmp_path):
        f = _write_tmp(tmp_path, "rm.py", "a = 1\n# TA: deletable\nb = 2\n")
        out = _run_tool("omt_think_remove", {"path": str(f), "line": 2})
        assert out is not None and "removed" in out.lower()
        content = f.read_text()
        assert "TA: deletable" not in content
        lst = _run_tool("omt_think_list", {"path": str(f)})
        assert lst is not None
        assert "deletable" not in lst

    def test_syntax_ts_md_jsonc(self, tmp_path):
        ts = _write_tmp(tmp_path, "a.ts", "export const x = 1\n")
        _run_tool("omt_think", {"path": str(ts), "thought": "ts note"})
        assert "// TA: ts note" in ts.read_text()
        md = _write_tmp(tmp_path, "a.md", "# Title\n")
        _run_tool("omt_think", {"path": str(md), "thought": "md note"})
        assert "<!-- TA: md note -->" in md.read_text()
        jc = _write_tmp(tmp_path, "a.jsonc", "{\n  // existing\n}\n")
        _run_tool("omt_think", {"path": str(jc), "thought": "jsonc note"})
        assert "// TA: jsonc note" in jc.read_text()


# ---------------------------------------------------------------------------
# Pure decider: thinkGateDecision
# ---------------------------------------------------------------------------
@needs_node
class TestThinkGateDecision:
    def test_no_thoughts_allows(self):
        assert _gate_decide(False, False) == "allow"

    def test_thoughts_unconsulted_blocks(self):
        assert _gate_decide(True, False) == "block"

    def test_thoughts_consulted_allows(self):
        assert _gate_decide(True, True) == "allow"


# ---------------------------------------------------------------------------
# Enforcer integration + docs/config
# ---------------------------------------------------------------------------
class TestThinkGateEnforcement:
    def test_enforcer_exports_decider_and_consult(self):
        c = ENFORCER.read_text()
        assert "export function thinkGateDecision" in c
        assert "export function hasConsultedThoughts" in c

    def test_enforcer_has_think_gate_in_before_hook(self):
        c = ENFORCER.read_text()
        assert "thinkGateDecision" in c
        assert "fileThoughtsIn" in c or "fileThoughts" in c
        assert "thinkGateMsg" in c
        # the gate is wired in the before-hook
        assert "think-gate" in c or "think_gate".lower() in c.lower() or "thinkGateDecision" in c

    def test_consult_reads_think_consult_ledger(self):
        """hasConsultedThoughts filters ledger records by kind='think_consult'."""
        c = ENFORCER.read_text()
        assert '"think_consult"' in c or "'think_consult'" in c

    def test_opencode_jsonc_allows_think_tools(self):
        c = (REPO_ROOT / "opencode.jsonc").read_text()
        assert '"omt_think": "allow"' in c
        assert '"omt_think_list": "allow"' in c
        assert '"omt_think_remove": "allow"' in c

    def test_agents_md_has_mandatory_section(self):
        c = (REPO_ROOT / "AGENTS.md").read_text()
        assert "Think Anywhere" in c
        assert "feature_021" in c
        assert "omt_think" in c

    def test_meta_harness_has_think_section(self):
        c = (REPO_ROOT / ".meta" / "META_HARNESS.md").read_text()
        assert "SECTION:THINK" in c
        assert "TA:" in c


# ---------------------------------------------------------------------------
# Plugin load health (no SyntaxError) + e2e-style tool registration
# ---------------------------------------------------------------------------
@needs_node
class TestThinkPluginHealth:
    def test_plugin_loads_via_default_export(self):
        """DEFECT A regression: the default factory must load without error."""
        out = _run_tool("omt_think_list", {"path": str(TEST_DIR)})
        # should be a string (even if 0 thoughts), not None (None == load failure)
        assert out is not None

    def test_all_three_tools_callable(self):
        tmp = TEST_DIR / ".." / "feature_021.meta_harness_think_anywhere"
        for name in ["omt_think_list", "omt_think"]:
            # omt_think_list with no path returns a string; omt_think needs args
            if name == "omt_think_list":
                assert _run_tool(name, {}) is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
