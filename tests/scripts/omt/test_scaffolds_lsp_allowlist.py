# tests/scripts/omt/test_scaffolds_lsp_allowlist.py — feature_090.scaffolds_and_lsp_allowlist goldens (mh8 T2-7).
#
# Covers BOTH halves of the feature:
#   (a) new_feature.py testing/implementation subcommands (hermetic, constants
#       monkeypatched per the test_project_lifecycle.py _mod idiom);
#   (b) bun probes on the lsp_filter.ts pure functions using RECORDED output
#       shapes — fixtures pinned from live opencode.db samples (pyright
#       1.1.408): sample A = main_controller.py this-file edit (4 errors,
#       multi-line messages); sample B = write with provider.py (5) +
#       main_controller.py (4) + rag_v2_tools.py control (1), the full live
#       noise cluster + an unrelated survivor;
#   (c) source pins (registration + HARNESS_FILES + allowlist seed).
#
# Acceptance (analysis_001 §Acceptance): the 9 seeded errors no longer appear
# in post-edit reports; a planted new error (different code) does; any
# surprise fails OPEN (result untouched).
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = REPO_ROOT / "scripts" / "omt"
BUN = shutil.which("bun")
LSP_FILTER = REPO_ROOT / ".opencode" / "lib" / "enforcer" / "lsp_filter.ts"

# --- recorded live paths (repo-relative keys of the seeded allowlist) --------
MAIN = str(REPO_ROOT / "src/agentx/ui/screens/main/main_controller.py")
PROV = str(REPO_ROOT / "src/agentx/ui/tui/provider.py")
RAG = str(REPO_ROOT / "src/agentx/model/rag_v2/rag_v2_tools.py")

SEED_ALLOWLIST = {
    "src/agentx/ui/screens/main/main_controller.py": [
        "reportArgumentType", "reportAttributeAccessIssue"],
    "src/agentx/ui/tui/provider.py": ["reportMissingImports"],
}

NBSP = " "  # pyright indents multi-line message continuations with U+00A0


def _e(line: int, char: int, code: str, message: str) -> dict:
    """A metadata diagnostic entry (shape pinned from opencode.db)."""
    return {
        "range": {"start": {"line": line, "character": char},
                  "end": {"line": line, "character": char + 8}},
        "message": message, "severity": 1, "code": code, "source": "Pyright",
    }


_MSG_AGENT_VIEW = (
    'Argument of type "AgentController" cannot be assigned to parameter '
    '"controller" of type "IConsoleAgentViewPartner" in function "create_agent_view"'
    f'\n{NBSP}{NBSP}"AgentController" is not assignable to "IConsoleAgentViewPartner"')
_MSG_FAST_VIEW = (
    'Argument of type "AgentController" cannot be assigned to parameter '
    '"controller" of type "IConsoleFastAgentViewPartner" in function "create_fast_agent_view"'
    f'\n{NBSP}{NBSP}"AgentController" is not assignable to "IConsoleFastAgentViewPartner"')
_MSG_MODELS_VIEW = (
    'Argument of type "ModelsController" cannot be assigned to parameter '
    '"controller" of type "IModelsViewPartner" in function "create_models_view"'
    f'\n{NBSP}{NBSP}"ModelsController" is not assignable to "IModelsViewPartner"')
_MSG_VIEW_ATTR = (
    'Cannot assign to attribute "view" for class "ModelsController"'
    f'\n{NBSP}{NBSP}Attribute "view" is unknown')


def _main_entries(l1: int, l2: int, l3: int, l4: int) -> list[dict]:
    """main_controller.py noise cluster at a given line-offset (two live
    recordings differ by +1 line — both variants are pinned here)."""
    return [
        _e(l1, 54, "reportArgumentType", _MSG_AGENT_VIEW),
        _e(l2, 64, "reportArgumentType", _MSG_FAST_VIEW),
        _e(l3, 60, "reportArgumentType", _MSG_MODELS_VIEW),
        _e(l4, 30, "reportAttributeAccessIssue", _MSG_VIEW_ATTR),
    ]


def _main_block(path: str, p1: int, p2: int, p3: int, p4: int, this_file: bool) -> str:
    header = ("LSP errors detected in this file, please fix:" if this_file
              else "LSP errors detected in other files:")
    return (
        f"{header}\n<diagnostics file=\"{path}\">\n"
        f"ERROR [{p1}:55] {_MSG_AGENT_VIEW}\n"
        f"ERROR [{p2}:65] {_MSG_FAST_VIEW}\n"
        f"ERROR [{p3}:61] {_MSG_MODELS_VIEW}\n"
        f"ERROR [{p4}:31] {_MSG_VIEW_ATTR}\n"
        "</diagnostics>")


# Sample A — live edit of main_controller.py (this-file, 4 errors).
A_DIAGS = {MAIN: _main_entries(199, 244, 268, 269)}
A_TEXT = "Edit applied successfully.\n\n" + _main_block(MAIN, 200, 245, 269, 270, True)

# Sample B — live write (other-files): provider.py 5 + main_controller.py 4
# (line-offset +1 vs A) + rag_v2_tools.py control 1.
_PROV_IMPORTS = [
    "agentx.ui.tui.adapters.react_adapter",
    "agentx.ui.tui.adapters.coding_adapter",
    "agentx.ui.tui.adapters.models_adapter",
    "agentx.ui.tui.adapters.agent_adapter",
    "agentx.ui.tui.adapters.fast_agent_adapter",
]
_PROV_LINES = [77, 89, 101, 113, 125]
B_PROV_ENTRIES = [
    _e(l - 1, 13, "reportMissingImports", f'Import "{m}" could not be resolved')
    for l, m in zip(_PROV_LINES, _PROV_IMPORTS)
]
B_PROV_BLOCK = (
    "LSP errors detected in other files:\n"
    f'<diagnostics file="{PROV}">\n'
    + "".join(f'ERROR [{l}:14] Import "{m}" could not be resolved\n'
              for l, m in zip(_PROV_LINES, _PROV_IMPORTS))
    + "</diagnostics>")
B_MAIN_ENTRIES = _main_entries(200, 245, 269, 270)
B_MAIN_BLOCK = _main_block(MAIN, 201, 246, 270, 271, False)
B_RAG_ENTRY = _e(18, 5, "reportMissingImports",
                 'Import "langchain.tools" could not be resolved')
B_RAG_BLOCK = (
    "LSP errors detected in other files:\n"
    f'<diagnostics file="{RAG}">\n'
    'ERROR [19:6] Import "langchain.tools" could not be resolved\n'
    "</diagnostics>")
B_DIAGS = {PROV: B_PROV_ENTRIES, MAIN: B_MAIN_ENTRIES, RAG: [B_RAG_ENTRY]}
B_TEXT = ("Wrote file successfully.\n\n" + B_PROV_BLOCK + "\n\n"
          + B_MAIN_BLOCK + "\n\n" + B_RAG_BLOCK)


# --- (a) new_feature.py phase-artifact subcommands ----------------------------

def _load_new_feature():
    spec = importlib.util.spec_from_file_location(
        "new_feature_f090_goldens", SCRIPT_DIR / "new_feature.py")
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def scaffold_env(tmp_path, monkeypatch):
    mod = _load_new_feature()
    features = tmp_path / ".meta" / "software_development_process" / "2.requirements" / "features"
    process = tmp_path / ".meta" / "software_development_process"
    templates = tmp_path / ".meta" / "templates"
    (features / "feature_007.modern_ui").mkdir(parents=True)
    templates.mkdir(parents=True)
    (templates / "test_plan.md").write_text(
        "# Test Report: {{TITLE}}\n\n> Feature: {{SLUG}}\n", encoding="utf-8")
    (templates / "feature.md").write_text(
        "# {{TITLE}} ({{NUM}})\n> {{SLUG}} {{DATE}}\n", encoding="utf-8")
    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(mod, "FEATURES_DIR", features)
    monkeypatch.setattr(mod, "PROCESS_ROOT", process)
    monkeypatch.setattr(mod, "TEMPLATES_DIR", templates)
    return {"mod": mod, "root": tmp_path, "process": process, "slug": "feature_007.modern_ui"}


class TestNewFeatureSubcommands:
    """P3-10: testing/implementation scaffold the later-phase artifact paths."""

    def test_testing_creates_test_report(self, scaffold_env, capsys):
        rc = scaffold_env["mod"].main(["testing", "--feature", scaffold_env["slug"]])
        out = capsys.readouterr().out
        assert rc == 0 and "created" in out
        target = (scaffold_env["process"] / "6.testing" / "features"
                  / scaffold_env["slug"] / "test_report.md")
        text = target.read_text(encoding="utf-8")
        assert "Modern Ui" in text and scaffold_env["slug"] in text

    def test_implementation_creates_impl_notes(self, scaffold_env, capsys):
        rc = scaffold_env["mod"].main(
            ["implementation", "--feature", scaffold_env["slug"], "--date", "2026-09-13"])
        assert rc == 0
        target = (scaffold_env["process"] / "5.implementation" / "features"
                  / scaffold_env["slug"] / "impl_notes.md")
        text = target.read_text(encoding="utf-8")
        assert f"Implementation notes — {scaffold_env['slug']}" in text
        assert "2026-09-13" in text

    def test_refuses_overwrite(self, scaffold_env, capsys):
        mod, slug = scaffold_env["mod"], scaffold_env["slug"]
        assert mod.main(["testing", "--feature", slug]) == 0
        target = (scaffold_env["process"] / "6.testing" / "features" / slug / "test_report.md")
        before = target.read_text(encoding="utf-8")
        rc = mod.main(["testing", "--feature", slug])
        err = capsys.readouterr().err
        assert rc == 2 and "already exists" in err
        assert target.read_text(encoding="utf-8") == before  # untouched

    def test_unknown_slug_errors(self, scaffold_env, capsys):
        rc = scaffold_env["mod"].main(["testing", "--feature", "feature_999.ghost"])
        err = capsys.readouterr().err
        assert rc == 2 and "unknown feature" in err

    def test_dry_run_creates_nothing(self, scaffold_env, capsys):
        rc = scaffold_env["mod"].main(
            ["testing", "--feature", scaffold_env["slug"], "--dry-run"])
        out = capsys.readouterr().out
        assert rc == 0 and "[dry-run] would create" in out
        assert not (scaffold_env["process"] / "6.testing").exists()

    def test_paths_derive_from_process_root(self, scaffold_env):
        """§3.11 mis-creation class: repo-root artifacts are impossible by
        construction — targets derive from PROCESS_ROOT, never cwd."""
        assert scaffold_env["mod"].main(["implementation", "--feature", scaffold_env["slug"]]) == 0
        created = list((scaffold_env["process"] / "5.implementation").rglob("impl_notes.md"))
        assert len(created) == 1
        assert created[0].relative_to(scaffold_env["process"]).as_posix() == (
            "5.implementation/features/feature_007.modern_ui/impl_notes.md")

    def test_legacy_positional_path_unchanged(self, scaffold_env, capsys):
        rc = scaffold_env["mod"].main(["brand new widget", "--dry-run"])
        out = capsys.readouterr().out
        assert rc == 0 and "feature_008.brand_new_widget" in out

    def test_prescan_is_exact_match_only(self, scaffold_env, capsys):
        """A legacy NAME that merely STARTS with a subcommand word stays on
        the positional path (pre-scan matches argv[0] exactly)."""
        rc = scaffold_env["mod"].main(["testing framework", "--dry-run"])
        out = capsys.readouterr().out
        assert rc == 0 and "feature_008.testing_framework" in out


# --- (b) bun probes on lsp_filter.ts pure functions ---------------------------

_PROBE_TEMPLATE = """
import { applyLspAllowlist, parseAllowlist, loadAllowlist } from %FILTER%
const res = %CALL%
console.log(JSON.stringify(res ?? null))
"""


def _probe(call: str, tmp_path: Path):
    assert BUN is not None, "bun runtime required (guard against skipif bypass)"
    probe = tmp_path / "probe.ts"
    probe.write_text(
        _PROBE_TEMPLATE.replace("%FILTER%", json.dumps(str(LSP_FILTER)))
        .replace("%CALL%", call),
        encoding="utf-8")
    out = subprocess.run([BUN, str(probe)], capture_output=True, text=True,
                         timeout=60, cwd=tmp_path)
    assert out.returncode == 0, f"bun probe failed:\n{out.stderr}\n---"
    return json.loads(out.stdout.strip().splitlines()[-1])


def _apply_call(text: str, diags: dict, allowlist: dict, root: Path) -> str:
    return (f"applyLspAllowlist({json.dumps(text)}, {json.dumps(diags)}, "
            f"{json.dumps(allowlist)}, {json.dumps(str(root))})")


@pytest.mark.skipif(BUN is None, reason="bun runtime not available")
class TestLspFilterPureCore:
    """P3-11: allowlisted (file, code) pairs vanish; new errors surface."""

    def test_sample_a_all_four_suppressed(self, tmp_path):
        res = _probe(_apply_call(A_TEXT, A_DIAGS, SEED_ALLOWLIST, REPO_ROOT), tmp_path)
        assert res == {"text": "Edit applied successfully.", "diags": {}, "dropped": 4}

    def test_planted_new_error_surfaces(self, tmp_path):
        """Acceptance: a NEW error with a different code in the same file
        still appears (static-allowlist tradeoff documented)."""
        planted = _e(300, 9, "reportGeneralTypeIssues",
                     "Planted golden error (reportGeneralTypeIssues)")
        diags = {MAIN: A_DIAGS[MAIN] + [planted]}
        text = A_TEXT.replace(
            "</diagnostics>",
            "ERROR [301:10] Planted golden error (reportGeneralTypeIssues)\n</diagnostics>")
        res = _probe(_apply_call(text, diags, SEED_ALLOWLIST, REPO_ROOT), tmp_path)
        expected_text = (
            "Edit applied successfully.\n\n"
            "LSP errors detected in this file, please fix:\n"
            f'<diagnostics file="{MAIN}">\n'
            "ERROR [301:10] Planted golden error (reportGeneralTypeIssues)\n"
            "</diagnostics>")
        assert res == {"text": expected_text, "diags": {MAIN: [planted]}, "dropped": 4}
        # trailing-newline variant: byte-preserved on the survivor block
        res_nl = _probe(_apply_call(text + "\n", diags, SEED_ALLOWLIST, REPO_ROOT), tmp_path)
        assert res_nl["text"] == expected_text + "\n"

    def test_sample_b_full_cluster_plus_control(self, tmp_path):
        """The 9 live noise entries vanish; the unrelated rag_v2_tools error
        survives with its block byte-identical."""
        res = _probe(_apply_call(B_TEXT, B_DIAGS, SEED_ALLOWLIST, REPO_ROOT), tmp_path)
        assert res["dropped"] == 9
        assert res["text"] == "Wrote file successfully.\n\n" + B_RAG_BLOCK
        assert res["diags"] == {RAG: [B_RAG_ENTRY]}

    def test_sample_b_partial_allowlist_byte_preserves_survivors(self, tmp_path):
        partial = {"src/agentx/ui/tui/provider.py": ["reportMissingImports"]}
        res = _probe(_apply_call(B_TEXT, B_DIAGS, partial, REPO_ROOT), tmp_path)
        assert res["dropped"] == 5
        assert res["text"] == ("Wrote file successfully.\n\n" + B_MAIN_BLOCK
                               + "\n\n" + B_RAG_BLOCK)
        assert res["diags"] == {MAIN: B_MAIN_ENTRIES, RAG: [B_RAG_ENTRY]}

    def test_no_allowlist_match_is_noop(self, tmp_path):
        res = _probe(_apply_call(B_TEXT, B_DIAGS, {"src/nope.py": ["x"]}, REPO_ROOT), tmp_path)
        assert res is None

    def test_warning_severity_never_suppressed(self, tmp_path):
        entry = dict(B_RAG_ENTRY)
        entry["severity"] = 2
        res = _probe(_apply_call(B_TEXT, {RAG: [entry]}, SEED_ALLOWLIST, REPO_ROOT), tmp_path)
        assert res is None  # nothing suppressible → no-op (and no text mangling)

    def test_desync_between_text_and_metadata_fails_open(self, tmp_path):
        desync = B_TEXT.replace("ERROR [19:6]", "ERROR [99:6]")
        res = _probe(_apply_call(desync, B_DIAGS, SEED_ALLOWLIST, REPO_ROOT), tmp_path)
        assert res is None

    def test_unrecognized_severity_render_fails_open(self, tmp_path):
        warn = B_TEXT.replace("ERROR [77:14]", "WARNING [77:14]")
        res = _probe(_apply_call(warn, B_DIAGS, SEED_ALLOWLIST, REPO_ROOT), tmp_path)
        assert res is None

    def test_missing_header_fails_open(self, tmp_path):
        nohdr = B_TEXT.replace("LSP errors detected in other files:\n", "")
        res = _probe(_apply_call(nohdr, B_DIAGS, SEED_ALLOWLIST, REPO_ROOT), tmp_path)
        assert res is None

    def test_missing_separator_fails_open(self, tmp_path):
        nosep = B_TEXT.replace("\n\nLSP errors detected", "\nLSP errors detected")
        res = _probe(_apply_call(nosep, B_DIAGS, SEED_ALLOWLIST, REPO_ROOT), tmp_path)
        assert res is None


@pytest.mark.skipif(BUN is None, reason="bun runtime not available")
class TestLspFilterAllowlistIO:
    def test_parse_allowlist_valid(self, tmp_path):
        got = _probe(f"parseAllowlist({json.dumps(json.dumps(SEED_ALLOWLIST))})", tmp_path)
        assert got == SEED_ALLOWLIST

    def test_parse_allowlist_rejects_surprises(self, tmp_path):
        assert _probe('parseAllowlist("not json")', tmp_path) is None
        assert _probe('parseAllowlist({"a.py": "x"})', tmp_path) is None
        assert _probe('parseAllowlist({"a.py": [1]})', tmp_path) is None
        assert _probe("parseAllowlist([])", tmp_path) is None
        assert _probe("parseAllowlist(42)", tmp_path) is None

    def test_load_allowlist_reads_root_data_file(self, tmp_path):
        (tmp_path / ".meta").mkdir()
        (tmp_path / ".meta" / "lsp_allowlist.json").write_text(
            json.dumps(SEED_ALLOWLIST), encoding="utf-8")
        got = _probe(f"loadAllowlist({json.dumps(str(tmp_path))})", tmp_path)
        assert got == SEED_ALLOWLIST
        empty_root = tmp_path / "empty"
        empty_root.mkdir()
        assert _probe(f"loadAllowlist({json.dumps(str(empty_root))})", tmp_path) is None


# --- (c) source pins -----------------------------------------------------------

class TestSourcePins:
    def test_registration_wired_in_enforcer(self):
        enforcer = (REPO_ROOT / ".opencode" / "plugins" / "omt_enforcer.ts").read_text(
            encoding="utf-8")
        assert 'from "../lib/enforcer/lsp_filter"' in enforcer
        assert "await lspAfterEdit(env, input, output)" in enforcer

    def test_harness_files_covers_lsp_filter(self):
        e2e = (REPO_ROOT / "tests" / "scripts" / "omt" / "test_omt_harness_e2e.py").read_text(
            encoding="utf-8")
        assert '".opencode/lib/enforcer/lsp_filter.ts"' in e2e

    def test_allowlist_seed_matches_live_noise(self):
        data = json.loads((REPO_ROOT / ".meta" / "lsp_allowlist.json").read_text(
            encoding="utf-8"))
        assert data == SEED_ALLOWLIST

    def test_lsp_filter_module_surface(self):
        src = LSP_FILTER.read_text(encoding="utf-8")
        assert "export async function lspAfterEdit" in src
        assert "export function applyLspAllowlist" in src
        assert "export function parseAllowlist" in src
        assert "export function loadAllowlist" in src
