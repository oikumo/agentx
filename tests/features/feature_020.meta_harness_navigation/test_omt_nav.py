"""
Test suite for feature_020: Meta Harness Navigation Tools

Tests the omt_nav, omt_list_sections, omt_cross_ref, and omt_quick_ref
opencode plugin tools for structured documentation navigation.

Test Strategy:
  - Structural: verify grep patterns find expected tags; verify the plugin
    source exports the required tools.
  - Behavioral: invoke the REAL plugin tools (via the _nav_runner.mjs fixture
    + node) and assert on their JSON output. This catches broken regexes /
    runtime defects that source-string checks miss (regression for the
    `omt_list_sections` empty-results defect, C3).
  - Enforcer health: regression guard for the duplicate-`const` SyntaxError
    that prevented the enforcer plugin from loading (C1).
"""

import subprocess
import json
import re
import shutil
from collections import Counter
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
META_ROOT = REPO_ROOT / ".meta"
TEST_DIR = Path(__file__).parent
NAV_RUNNER = TEST_DIR / "_nav_runner.mjs"
PLUGIN_LOAD = TEST_DIR / "_plugin_load.mjs"
GATE_RUNNER = TEST_DIR / "_gate_runner.mjs"
NAV_SCHEMA_RUNNER = TEST_DIR / "_nav_schema_runner.mjs"

NODE = shutil.which("node")
needs_node = pytest.mark.skipif(not NODE, reason="node not available")


def _run_tool(tool_name: str, args: dict | None = None):
    """Invoke a real omt_nav plugin tool via node; return parsed JSON or None."""
    node = NODE
    if not node:
        return None
    proc = subprocess.run(
        [node, "--experimental-strip-types", str(NAV_RUNNER), tool_name, json.dumps(args or {})],
        capture_output=True, text=True, cwd=REPO_ROOT, timeout=30,
    )
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def _plugin_loads(abs_path: Path) -> bool:
    """Return True if the given .ts plugin imports without a SyntaxError."""
    node = NODE
    if not node:
        return False
    proc = subprocess.run(
        [node, "--experimental-strip-types", str(PLUGIN_LOAD), str(abs_path)],
        capture_output=True, text=True, cwd=REPO_ROOT, timeout=30,
    )
    return proc.returncode == 0


def _gate_decide(tool: str, targetRel, usedNav: bool, navUnlock: bool):
    """Invoke the real navGateDecision helper via node; return 'allow' or 'block'."""
    node = NODE
    if not node:
        return None
    opts = json.dumps({"tool": tool, "targetRel": targetRel,
                       "usedNav": usedNav, "navUnlock": navUnlock})
    proc = subprocess.run(
        [node, "--experimental-strip-types", str(GATE_RUNNER), "decide", opts],
        capture_output=True, text=True, cwd=REPO_ROOT, timeout=30,
    )
    if proc.returncode != 0:
        return None
    return json.loads(proc.stdout)["decision"]


# ---------------------------------------------------------------------------
# Structural: grep patterns work across META HARNESS documentation
# ---------------------------------------------------------------------------
class TestGrepPatterns:
    """Test that grep patterns work across META HARNESS documentation"""

    def test_section_headers_exist(self):
        """Verify SECTION: headers exist in all META HARNESS files"""
        result = subprocess.run(
            ["grep", "-r", "SECTION:", str(META_ROOT)],
            capture_output=True, text=True, cwd=REPO_ROOT,
        )
        assert result.returncode == 0, "SECTION: headers should exist"
        lines = result.stdout.strip().split("\n")
        assert len(lines) >= 10, f"Expected 10+ SECTION: headers, found {len(lines)}"

    def test_rule_codes_exist(self):
        """Verify RULE_ codes exist in META_HARNESS.md"""
        result = subprocess.run(
            ["grep", "^RULE_", str(META_ROOT / "META_HARNESS.md")],
            capture_output=True, text=True, cwd=REPO_ROOT,
        )
        assert result.returncode == 0, "RULE_ codes should exist"
        lines = result.stdout.strip().split("\n")
        assert len(lines) >= 3, f"Expected 3+ RULE_ codes, found {len(lines)}"

    def test_error_codes_exist(self):
        """Verify ERR_ codes exist in META_HARNESS.md"""
        result = subprocess.run(
            ["grep", "^ERR_", str(META_ROOT / "META_HARNESS.md")],
            capture_output=True, text=True, cwd=REPO_ROOT,
        )
        assert result.returncode == 0, "ERR_ codes should exist"
        lines = result.stdout.strip().split("\n")
        assert len(lines) >= 1, f"Expected ERR_ codes, found {len(lines)}"

    def test_cmd_codes_exist(self):
        """Verify CMD_ codes exist in META_HARNESS.md"""
        result = subprocess.run(
            ["grep", "^CMD_", str(META_ROOT / "META_HARNESS.md")],
            capture_output=True, text=True, cwd=REPO_ROOT,
        )
        assert result.returncode == 0, "CMD_ codes should exist"
        lines = result.stdout.strip().split("\n")
        assert len(lines) >= 4, f"Expected 4+ CMD_ codes, found {len(lines)}"

    def test_quick_patterns_exist(self):
        """Verify QUICK_ workflow patterns exist"""
        result = subprocess.run(
            ["grep", "^QUICK_", str(META_ROOT / "META_HARNESS.md")],
            capture_output=True, text=True, cwd=REPO_ROOT,
        )
        assert result.returncode == 0, "QUICK_ patterns should exist"
        lines = result.stdout.strip().split("\n")
        assert len(lines) >= 2, f"Expected 2+ QUICK_ patterns, found {len(lines)}"

    def test_xref_codes_exist(self):
        """Verify XREF_ cross-references exist"""
        result = subprocess.run(
            ["grep", "^XREF_", str(META_ROOT / "META_HARNESS.md")],
            capture_output=True, text=True, cwd=REPO_ROOT,
        )
        assert result.returncode == 0, "XREF_ codes should exist"
        lines = result.stdout.strip().split("\n")
        assert len(lines) >= 1, f"Expected XREF_ codes, found {len(lines)}"


# ---------------------------------------------------------------------------
# Structural: plugin source exports the required tools
# ---------------------------------------------------------------------------
class TestOmtNavTool:
    """Test omt_nav plugin tool source structure"""

    def test_omt_nav_tool_file_exists(self):
        nav_file = REPO_ROOT / ".opencode" / "plugin" / "omt_nav.ts"
        assert nav_file.exists(), "omt_nav.ts should exist"

    def test_omt_nav_exports_tools(self):
        """omt_nav.ts must export a default plugin function (opencode's loader
        requires all module exports to be functions; tool objects cannot be
        named-exported). The tools are registered via the default factory's
        `tool` property."""
        nav_file = REPO_ROOT / ".opencode" / "plugin" / "omt_nav.ts"
        content = nav_file.read_text()
        assert "export default async () => ({" in content, (
            "Should export a default async plugin function (opencode requirement)"
        )
        assert "tool: { omt_nav" in content, "Should register omt_nav via tool map"
        assert "omt_list_sections" in content, "Should register omt_list_sections"
        assert "omt_cross_ref" in content, "Should register omt_cross_ref"
        assert "omt_quick_ref" in content, "Should register omt_quick_ref"
        # Regression guard for DEFECT A: named tool-object exports break
        # opencode's plugin loader (sk/nk checks ALL exports must be functions).
        assert "export { omt_nav" not in content, (
            "Must NOT named-export tool objects (opencode loader rejects non-function exports)"
        )

    def test_omt_nav_uses_canonical_tool_api(self):
        """DEFECT C regression: opencode's tool() reads `args` (param-name ->
        tool.schema.X()) and threads resolved args into execute(args, context).
        The old `input:{type,properties,required}` + `execute(input)` shape is a
        raw JSON schema opencode does NOT understand — it registered each tool
        with no params, so real calls passed undefined args and crashed on
        .startsWith/.split. The function-level tests (calling execute(args)
        directly via _nav_runner.mjs) never exercised opencode's arg-binding,
        so the mismatch was invisible. The canonical shape (mirrors
        omt_status.ts / omt_enforcer.ts) is mandatory."""
        nav_file = REPO_ROOT / ".opencode" / "plugin" / "omt_nav.ts"
        content = nav_file.read_text()
        assert 'import { tool } from "@opencode-ai/plugin"' in content, "Should import tool"
        assert 'tool({' in content, "Should use tool() decorator"
        # Canonical API: args + tool.schema (NOT raw JSON-schema input:)
        assert "args:" in content, "Should use args: schema (DEFECT C)"
        assert "tool.schema.string()" in content, "Should use tool.schema.string (DEFECT C)"
        assert "tool.schema.boolean()" in content, "Should use tool.schema.boolean (DEFECT C)"
        assert "async execute(args, context)" in content, "Should use execute(args, context) (DEFECT C)"
        # The broken raw-JSON-schema shape must NOT be present
        assert 'type: "object"' not in content, \
            "Must NOT use raw JSON-schema input:{type:object} (DEFECT C regression)"
        assert 'name: "omt_nav"' not in content, \
            "Must NOT set name: (inferred from tool-map key, DEFECT C)"

    def test_omt_nav_uses_safe_exec(self):
        """Regression for H3: runGrep must use execFileSync (array args), not
        execSync with a shell string command (shell-injection risk)."""
        nav_file = REPO_ROOT / ".opencode" / "plugin" / "omt_nav.ts"
        content = nav_file.read_text()
        assert "execFileSync" in content, "Should import/use execFileSync"
        assert "execSync" not in content.replace("execFileSync", ""), \
            "execSync (shell string-cmd) must not be used"


class TestOmtListSections:
    """Test omt_list_sections tool source structure"""

    def test_function_exists(self):
        nav_file = REPO_ROOT / ".opencode" / "plugin" / "omt_nav.ts"
        content = nav_file.read_text()
        assert "const omt_list_sections = tool({" in content, "Should define omt_list_sections"
        # DEFECT C: no `name:` property — opencode infers the tool name from the
        # default-export tool-map key (verified in test_omt_nav_exports_tools).

    def test_uses_bre_safe_section_pattern(self):
        """Regression for C3: the SECTION grep pattern must be BRE-safe.
        `^##+` is wrong in BRE (`+` is literal) and even in ERE requires 2+
        hashes; the headers use a single `#`. Must be `^##*` (one-or-more)."""
        nav_file = REPO_ROOT / ".opencode" / "plugin" / "omt_nav.ts"
        content = nav_file.read_text()
        assert '"^##* SECTION:"' in content, \
            "omt_list_sections must use the BRE-safe '^##* SECTION:' pattern"
        assert '"^##+ SECTION:"' not in content, \
            "broken '^##+ SECTION:' pattern must not be present"


class TestOmtCrossRef:
    """Test omt_cross_ref tool source structure"""

    def test_function_exists(self):
        nav_file = REPO_ROOT / ".opencode" / "plugin" / "omt_nav.ts"
        content = nav_file.read_text()
        assert "const omt_cross_ref = tool({" in content, "Should define omt_cross_ref"
        # DEFECT C: no `name:` property — opencode infers the tool name from the
        # default-export tool-map key (verified in test_omt_nav_exports_tools).


class TestOmtQuickRef:
    """Test omt_quick_ref tool source structure"""

    def test_function_exists(self):
        nav_file = REPO_ROOT / ".opencode" / "plugin" / "omt_nav.ts"
        content = nav_file.read_text()
        assert "const omt_quick_ref = tool({" in content, "Should define omt_quick_ref"
        # DEFECT C: no `name:` property — opencode infers the tool name from the
        # default-export tool-map key (verified in test_omt_nav_exports_tools).


# ---------------------------------------------------------------------------
# Behavioral: invoke the REAL plugin tools (string output — DEFECT D)
# ---------------------------------------------------------------------------
@needs_node
class TestToolBehaviorReal:
    """Invoke the real omt_nav plugin tools via node and assert on the STRING
    output. Tools return plain strings (opencode ToolResult = string |
    {output:str}); a raw object without `output` crashes opencode (DEFECT D:
    result.output is undefined -> .split() -> 'u.split'). Assertions use
    substrings / line counts — no structured-field indexing."""

    def test_all_tools_return_strings(self):
        """DEFECT D regression: every tool must return a string, not a raw
        object. A raw object without `output` crashes opencode at call time."""
        cases = [
            ("omt_nav", {"query": "SECTION:"}),
            ("omt_list_sections", {}),
            ("omt_cross_ref", {"xref": "XREF_NAV"}),
            ("omt_quick_ref", {}),
        ]
        for name, args in cases:
            out = _run_tool(name, args)
            assert out is not None, f"{name} failed to run"
            assert isinstance(out, str), f"{name} must return a string (DEFECT D)"

    def test_omt_list_sections_returns_many(self):
        out = _run_tool("omt_list_sections")
        assert out is not None
        assert len(out.splitlines()) >= 10

    def test_omt_list_sections_includes_meta_harness(self):
        out = _run_tool("omt_list_sections")
        assert out is not None
        assert ".meta/META_HARNESS.md" in out

    def test_omt_list_sections_covers_omt_plus_plus(self):
        out = _run_tool("omt_list_sections")
        assert out is not None
        assert "doc/omt++/" in out

    def test_omt_nav_finds_cmd(self):
        out = _run_tool("omt_nav", {"query": "CMD_OMT_PHASE"})
        assert out is not None
        assert "omt_phase" in out

    def test_omt_nav_with_tag_type(self):
        out = _run_tool("omt_nav", {"query": "V2M", "tag_type": "ERR"})
        assert out is not None
        assert "ERR_" in out
        assert "V2M" in out

    def test_omt_nav_no_match_returns_message(self):
        out = _run_tool("omt_nav", {"query": "ZZZ_NOPE_NOTHING_XYZ_123"})
        assert out is not None
        assert "No results" in out

    def test_omt_nav_include_context_adds_lines(self):
        out = _run_tool("omt_nav", {"query": "RULE_R1", "include_context": True})
        assert out is not None
        # context renders surrounding lines, so output is more than one line
        assert len(out.splitlines()) > 1

    def test_omt_cross_ref_resolves(self):
        out = _run_tool("omt_cross_ref", {"xref": "XREF_NAV"})
        assert out is not None
        assert "XREF_" in out

    def test_omt_quick_ref_filtered(self):
        out = _run_tool("omt_quick_ref", {"workflow": "START_MAJOR"})
        assert out is not None
        assert "QUICK_" in out

    def test_omt_quick_ref_all(self):
        out = _run_tool("omt_quick_ref")
        assert out is not None
        assert len(out.splitlines()) >= 5


# ---------------------------------------------------------------------------
# Real-path schema: DEFECT C regression (opencode's actual arg-binding precondition)
# ---------------------------------------------------------------------------
@needs_node
class TestToolSchemaReal:
    """Inspect the REAL plugin tool objects (via opencode's actual `tool()`
    function) to verify each tool exposes a proper `args` Zod-schema.

    This is the test that DEFECT C slipped past. The behavioral tests above
    (_run_tool) call `tool.execute(args)` DIRECTLY, bypassing opencode's
    arg-binding entirely. An earlier omt_nav.ts used `input:{type,properties}`
    (a raw JSON schema) instead of `args`/`tool.schema`. opencode's `tool()`
    ignores `input` and registers the tool with NO parameters, so real calls
    passed undefined args and crashed on `.startsWith`/`.split`. Because
    _run_tool supplied args straight to execute, the broken schema was never
    exercised and every behavioral test passed — false confidence.

    opencode serve has no model-free direct-tool-call HTTP endpoint (`/tool*`
    return the SPA; `/session/{id}/message` requires an LLM to process parts),
    so a serve-based invocation test is impractical. Instead this test inspects
    the schema opencode actually USES to bind args (`args`): if it's missing or
    not Zod, opencode cannot bind args and the tool is non-functional in a real
    session. This is deterministic, fast, and directly targets DEFECT C."""

    def _schema(self):
        node = NODE
        if not node:
            return None
        proc = subprocess.run(
            [node, "--experimental-strip-types", str(NAV_SCHEMA_RUNNER)],
            capture_output=True, text=True, cwd=REPO_ROOT, timeout=30,
        )
        if proc.returncode != 0:
            return None
        try:
            return json.loads(proc.stdout)
        except json.JSONDecodeError:
            return None

    def test_plugin_loads_via_default_export(self):
        """The default plugin factory must load (DEFECT A regression: a missing
        default function means the tools are never registered at all)."""
        s = self._schema()
        assert s is not None, "plugin failed to load via default export (DEFECT A?)"

    def test_all_four_tools_registered(self):
        s = self._schema()
        assert s is not None
        for name in ["omt_nav", "omt_list_sections", "omt_cross_ref", "omt_quick_ref"]:
            assert name in s, f"{name} must be registered in the tool map"
            assert s[name]["loaded"] is True

    def test_all_tools_use_args_not_input(self):
        """DEFECT C core: each tool must expose `args` (Zod schemas) and must
        NOT carry the raw-JSON-schema `input` property. opencode binds args from
        `args` only; `input` is silently ignored."""
        s = self._schema()
        assert s is not None
        for name in ["omt_nav", "omt_list_sections", "omt_cross_ref", "omt_quick_ref"]:
            assert s[name]["hasArgs"] is True, (
                f"{name} must use args: schema (DEFECT C) — hasArgs=False, "
                f"hasInput={s[name].get('hasInput')}")
            assert s[name]["hasInput"] is False, (
                f"{name} must NOT use raw JSON-schema input: (DEFECT C)")
            assert s[name]["hasExecute"] is True, f"{name} must have an execute fn"

    def test_required_params_are_zod_and_required(self):
        """omt_nav.query and omt_cross_ref.xref are required string params: they
        must be Zod schemas with isOptional() == False. If `args` were absent
        (DEFECT C), these entries wouldn't exist."""
        s = self._schema()
        assert s is not None
        q = s["omt_nav"]["args"].get("query")
        assert q is not None, "omt_nav.args.query must exist (DEFECT C)"
        assert q["isZod"] is True, "query must be a Zod schema opencode can parse"
        assert q["isOptional"] is False, "query must be required"

        x = s["omt_cross_ref"]["args"].get("xref")
        assert x is not None, "omt_cross_ref.args.xref must exist (DEFECT C)"
        assert x["isZod"] is True, "xref must be a Zod schema opencode can parse"
        assert x["isOptional"] is False, "xref must be required"

    def test_optional_params_are_zod_and_optional(self):
        """Optional params (file, tag_type, include_context, workflow) must be
        Zod schemas with isOptional() == True."""
        s = self._schema()
        assert s is not None
        for opt in ["file", "tag_type", "include_context"]:
            a = s["omt_nav"]["args"].get(opt)
            assert a is not None, f"omt_nav.args.{opt} must be declared"
            assert a["isZod"] is True, f"{opt} must be a Zod schema"
            assert a["isOptional"] is True, f"{opt} must be optional"
        wf = s["omt_quick_ref"]["args"].get("workflow")
        assert wf is not None and wf["isZod"] is True and wf["isOptional"] is True
        lf = s["omt_list_sections"]["args"].get("file")
        assert lf is not None and lf["isZod"] is True and lf["isOptional"] is True


# ---------------------------------------------------------------------------
# Enforcer health: regression for C1 (duplicate const broke plugin loading)
# ---------------------------------------------------------------------------
class TestEnforcerHealth:
    """Regression guard for the duplicate-`const` SyntaxError (C1) that
    prevented .opencode/plugin/omt_enforcer.ts from loading — which silently
    disabled ALL OMT++ mechanical enforcement."""

    def test_no_duplicate_top_level_const(self):
        enforcer = REPO_ROOT / ".opencode" / "plugin" / "omt_enforcer.ts"
        content = enforcer.read_text()
        decls = re.findall(r"^const (\w+)", content, re.MULTILINE)
        dups = [k for k, v in Counter(decls).items() if v > 1]
        assert not dups, f"duplicate top-level const declarations: {dups}"

    @needs_node
    def test_enforcer_plugin_loads(self):
        """The enforcer must import without a SyntaxError (C1 regression)."""
        enforcer = REPO_ROOT / ".opencode" / "plugin" / "omt_enforcer.ts"
        assert _plugin_loads(enforcer), "omt_enforcer.ts failed to load (SyntaxError?)"

    @needs_node
    def test_nav_plugin_loads(self):
        """The nav plugin must import without a SyntaxError."""
        nav = REPO_ROOT / ".opencode" / "plugin" / "omt_nav.ts"
        assert _plugin_loads(nav), "omt_nav.ts failed to load (SyntaxError?)"


# ---------------------------------------------------------------------------
# M1/M2: scoped navigation gate (read & src/non-doc exempt; doc-grep gated)
# ---------------------------------------------------------------------------
@needs_node
class TestNavGateDecision:
    """Behavioral tests for the M1/M2 nav gate. Invokes the REAL
    navGateDecision helper exported from omt_enforcer.ts via node."""

    def test_read_is_always_allowed_m1(self):
        # read is never gated — even on doc paths with no nav used.
        assert _gate_decide("read", ".meta/META_HARNESS.md", False, False) == "allow"
        assert _gate_decide("read", None, False, False) == "allow"

    def test_src_search_is_exempt_m2(self):
        # grep/glob scoped to src/ are never gated (nav indexes docs, not code).
        assert _gate_decide("grep", "src/agentx/foo.py", False, False) == "allow"
        assert _gate_decide("glob", "src/", False, False) == "allow"

    def test_non_doc_search_is_exempt(self):
        # tests/, scripts/, configs — not docs → exempt.
        assert _gate_decide("grep", "tests/features/x.py", False, False) == "allow"
        assert _gate_decide("grep", "scripts/omt/mvc_check.py", False, False) == "allow"

    def test_doc_search_blocked_without_nav(self):
        # the MANDATORY gate still holds for doc-scoped searches.
        assert _gate_decide("grep", ".meta/META_HARNESS.md", False, False) == "block"
        assert _gate_decide("glob", "AGENTS.md", False, False) == "block"
        assert _gate_decide("grep", "WORK.md", False, False) == "block"

    def test_doc_search_allowed_after_nav(self):
        assert _gate_decide("grep", ".meta/META_HARNESS.md", True, False) == "allow"

    def test_doc_search_allowed_with_nav_unlock(self):
        # omt_skip{scope:"nav"} escape hatch (M1).
        assert _gate_decide("glob", "AGENTS.md", False, True) == "allow"

    def test_pathless_search_blocked_without_nav(self):
        # no path = whole repo (could hit docs) → conservative block.
        assert _gate_decide("grep", None, False, False) == "block"

    def test_pathless_search_allowed_with_nav(self):
        assert _gate_decide("grep", None, True, False) == "allow"


class TestNavGateEnforcement:
    """Source-level + docs guards for the M1/M2 scoped nav gate."""

    def test_enforcer_exports_gate_helpers(self):
        content = (REPO_ROOT / ".opencode" / "plugin" / "omt_enforcer.ts").read_text()
        assert "export function navGateDecision" in content, "navGateDecision must be exported"
        assert "export function isDocPath" in content, "isDocPath must be exported"
        assert "hasNavUnlock" in content, "hasNavUnlock escape helper must exist"

    def test_omt_skip_supports_nav_scope(self):
        content = (REPO_ROOT / ".opencode" / "plugin" / "omt_enforcer.ts").read_text()
        assert "src | tests | nav | all" in content, "omt_skip must document the nav scope"
        assert 'r.scope === "nav"' in content, "hasNavUnlock must recognize scope=nav"

    def test_agents_md_documents_scoped_gate_and_escape(self):
        content = (REPO_ROOT / "AGENTS.md").read_text()
        assert "Navigation Enforcement (feature_020)" in content
        assert 'scope:"nav"' in content, "AGENTS.md must document the nav escape hatch"
        # M2: src/ non-doc searches documented as not blocked
        assert "src/" in content, "AGENTS.md must mention src/ searches"
        assert "non-doc" in content.lower(), "AGENTS.md must note non-doc searches are not gated"

    def test_meta_harness_documents_nav_scope(self):
        content = (REPO_ROOT / ".meta" / "META_HARNESS.md").read_text()
        assert "ESC_SCOPE_NAV:" in content, "META_HARNESS must document ESC_SCOPE_NAV"
        assert "src|tests|nav|all" in content


# ---------------------------------------------------------------------------
# Documentation coverage
# ---------------------------------------------------------------------------
class TestDocumentationCoverage:
    """Test that all META HARNESS files have proper tags"""

    def test_meta_harness_has_all_tags(self):
        file_path = META_ROOT / "META_HARNESS.md"
        content = file_path.read_text()
        assert "SECTION:" in content, "Should have SECTION: headers"
        assert "RULE_" in content, "Should have RULE_ codes"
        assert "ERR_" in content, "Should have ERR_ codes"
        assert "CMD_" in content, "Should have CMD_ codes"
        assert "QUICK_" in content, "Should have QUICK_ patterns"
        assert "XREF_" in content, "Should have XREF_ references"

    def test_agents_md_has_tags(self):
        file_path = REPO_ROOT / "AGENTS.md"
        content = file_path.read_text()
        assert "SECTION:" in content or "##" in content, "Should have section headers"

    def test_omt_agent_guide_has_sections(self):
        file_path = META_ROOT / "software_development_process" / "omt_agent_guide.md"
        assert file_path.exists(), "omt_agent_guide.md should exist"
        content = file_path.read_text()
        # omt_agent_guide.md uses numbered sections (## 1., ## 2., etc.)
        assert "## " in content, "Should have section headers"
        section_count = content.count("## ")
        assert section_count >= 10, f"Should have 10+ sections, found {section_count}"

    def test_all_omt_plus_plus_files_have_sections(self):
        omt_pp_dir = META_ROOT / "doc" / "omt++"
        md_files = list(omt_pp_dir.glob("*.md"))
        assert len(md_files) >= 6, f"Expected 6+ omt++ files, found {len(md_files)}"
        for md_file in md_files:
            content = md_file.read_text()
            assert "SECTION:" in content, f"{md_file.name} should have SECTION: headers"


# ---------------------------------------------------------------------------
# Integration
# ---------------------------------------------------------------------------
class TestIntegration:
    """Integration tests for navigation system"""

    def test_grep_pattern_compatibility(self):
        patterns = ["SECTION:", "CMD_OMT", "ERR_", "QUICK_"]
        for pattern in patterns:
            result = subprocess.run(
                ["grep", "-r", pattern, str(META_ROOT)],
                capture_output=True, text=True, cwd=REPO_ROOT,
            )
            assert result.returncode == 0 or len(result.stdout) > 0, \
                f"Pattern '{pattern}' should find matches"

    def test_file_paths_resolvable(self):
        expected_files = [
            ".meta/META_HARNESS.md",
            ".meta/META.md",
            ".meta/software_development_process/META.md",
            ".meta/software_development_process/omt_agent_guide.md",
            "AGENTS.md",
            "WORK.md",
        ]
        for rel_path in expected_files:
            file_path = REPO_ROOT / rel_path
            assert file_path.exists(), f"{rel_path} should exist"
            assert file_path.stat().st_size > 0, f"{rel_path} should not be empty"


# ---------------------------------------------------------------------------
# Enforcement configuration
# ---------------------------------------------------------------------------
class TestEnforcement:
    """Test feature_020 enforcement configuration"""

    def test_opencode_jsonc_allows_nav_tools(self):
        config_file = REPO_ROOT / "opencode.jsonc"
        content = config_file.read_text()
        assert '"omt_nav": "allow"' in content, "omt_nav should be allowed"
        assert '"omt_list_sections": "allow"' in content, "omt_list_sections should be allowed"
        assert '"omt_cross_ref": "allow"' in content, "omt_cross_ref should be allowed"
        assert '"omt_quick_ref": "allow"' in content, "omt_quick_ref should be allowed"

    def test_agents_md_has_mandatory_section(self):
        agents_file = REPO_ROOT / "AGENTS.md"
        content = agents_file.read_text()
        assert "Navigation Enforcement (feature_020)" in content, "Should have enforcement section"
        assert "MANDATORY:" in content, "Should mark navigation as mandatory"
        assert "omt_nav" in content, "Should mention omt_nav tool"
        assert "omt_list_sections" in content, "Should mention omt_list_sections tool"
        assert "omt_cross_ref" in content, "Should mention omt_cross_ref tool"
        assert "omt_quick_ref" in content, "Should mention omt_quick_ref tool"

    def test_meta_harness_has_nav_section(self):
        meta_file = META_ROOT / "META_HARNESS.md"
        content = meta_file.read_text()
        assert "SECTION:NAV" in content, "Should have NAV section"
        assert "NAV_020:" in content, "Should document feature_020"
        assert "NAV_TOOLS:" in content, "Should list navigation tools"
        assert "QUICK_NAV_DOCS:" in content, "Should have navigation workflow"
        assert "XREF_NAV:" in content or "XREF_NAV_ENF:" in content, \
            "Should cross-reference nav tools"

    def test_enforcer_has_nav_reminder(self):
        enforcer_file = REPO_ROOT / ".opencode" / "plugin" / "omt_enforcer.ts"
        content = enforcer_file.read_text()
        assert "navReminderMsg" in content, "Should have navReminderMsg function"
        assert "feature_020" in content, "Should reference feature_020"
        assert "session.start" in content, "Should have session.start hook"
        assert "omt_nav" in content, "Should mention omt_nav"
        assert "omt_list_sections" in content, "Should mention omt_list_sections"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
