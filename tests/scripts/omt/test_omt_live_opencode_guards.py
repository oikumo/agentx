"""
LIVE end-to-end guard verification: drive the REAL opencode binary
(`opencode run --format json`, optionally --print-logs / --pure) and assert
the OMT harness hooks actually fire in the production runtime — the test that
would have caught BUG-A/BUG-B (see test_omt_enforcer_guard_source_pins.py),
because runner-based fixtures fabricate the shapes the buggy code expects and
stay green while the real runtime drifts (the F14 meta-lesson).

What this proves, live, per the OpenCode plugin architecture
(.meta/doc/opencode_plugins/OpenCode Plugin Creation Guide.md):

  1. Plugins auto-load from .opencode/plugins/ in a real run (plugin tools
     callable, hooks firing) — no npm distribution involved.
  2. tool.execute.after effects fire: the omt_enforcer nav reminder and the
     omt_think TA digest appear in the FIRST tool result of a session
     (feature_023 F14c live path), and NOT under --pure (A/B control).
  3. tool.execute.before edit guards fire: a direct edit attempt on a
     protected file (README.md — AGENTS.md NEVER list, no phase/skip declared)
     is blocked and the file stays byte-identical.
  4. The OMT-harness e2e receipt guard fires on the enforcement plugins
     themselves (BUG-B regression): editing .opencode/plugins/omt_status.ts
     with a stale receipt is blocked.
  5. Plugin loading produces no errors in --print-logs output.

Cost: each test is one real LLM round-trip (~15–40 s). Marked `opencode_live`;
skipped when the opencode binary is absent. Prompts forbid the agent from
declaring phases/skips so the guards — not agent compliance — decide.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
OPENCODE = shutil.which("opencode")
OPENCODE_BIN = OPENCODE or "opencode"  # skipif guards the None case
README = REPO_ROOT / "README.md"
STATUS_PLUGIN = REPO_ROOT / ".opencode" / "plugins" / "omt_status.ts"

pytestmark = [
    pytest.mark.skipif(not OPENCODE, reason="opencode binary not available"),
    pytest.mark.opencode_live,
]

TIMEOUT = 240


def _run_opencode(prompt: str, *extra: str) -> tuple[int, list[dict], str]:
    """One real headless run; returns (exit, parsed json events, stderr)."""
    proc = subprocess.run(
        [OPENCODE_BIN, "run", "--format", "json", *extra, prompt],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=TIMEOUT,
    )
    events = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return proc.returncode, events, proc.stderr


def _tool_uses(events: list[dict]) -> list[dict]:
    return [e["part"] for e in events
            if e.get("type") == "tool_use" and isinstance(e.get("part"), dict)]


def _tool_output(part: dict) -> str:
    state = part.get("state") or {}
    return str(state.get("output") or state.get("error") or "")


class TestLivePluginLoading:
    def test_plugin_tool_registered_and_callable(self):
        """Auto-loaded plugins expose their tools: omt_status executes and
        returns the real harness status (not an unknown-tool error)."""
        code, events, _ = _run_opencode(
            "Call the omt_status tool with no arguments, then reply DONE.")
        assert code == 0
        calls = [p for p in _tool_uses(events) if p.get("tool") == "omt_status"]
        assert calls, (
            "omt_status was never called — plugin tools not registered in the "
            f"real runtime? tools seen: {[p.get('tool') for p in _tool_uses(events)]}")
        out = _tool_output(calls[0])
        assert "OMT++ STATUS" in out, f"omt_status output wrong: {out[:200]!r}"

    def test_plugin_load_no_errors_in_logs(self):
        """--print-logs: no plugin load/resolution errors during bootstrap."""
        proc = subprocess.run(
            [OPENCODE_BIN, "run", "--print-logs", "--log-level", "DEBUG",
             "Reply with exactly: OK"],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=TIMEOUT,
        )
        assert proc.returncode == 0
        bad = [l for l in proc.stderr.splitlines()
               if "level=ERROR" in l and "plugin" in l.lower()]
        assert not bad, f"plugin errors in real bootstrap logs: {bad[:5]}"


class TestLiveAfterHookEffects:
    def test_nav_reminder_and_think_digest_on_first_tool_result(self):
        """F14c live path: the first tool result of a session carries the
        omt_enforcer NAVIGATION TIP and the omt_think THINK-ANYWHERE digest —
        appended by tool.execute.after hooks (args on INPUT per contract)."""
        code, events, _ = _run_opencode(
            "Use the read tool to read ONLY the first 3 lines of the file "
            "AGENTS.md, then reply DONE.")
        assert code == 0
        reads = [p for p in _tool_uses(events) if p.get("tool") == "read"]
        assert reads, "no read tool call happened"
        out = _tool_output(reads[0])
        assert "NAVIGATION TIP" in out, (
            f"omt_enforcer after-hook nav reminder missing from the first tool "
            f"result: {out[:300]!r}")
        assert "THINK-ANYWHERE" in out, (
            f"omt_think after-hook TA digest missing from the first tool "
            f"result: {out[:300]!r}")

    def test_pure_mode_disables_all_plugin_effects(self):
        """A/B control: --pure runs without external plugins — the same read
        produces NO injections (proves the effects above come from the
        plugins, not from opencode itself)."""
        code, events, _ = _run_opencode(
            "Use the read tool to read ONLY the first 3 lines of the file "
            "AGENTS.md, then reply DONE.", "--pure")
        assert code == 0
        reads = [p for p in _tool_uses(events) if p.get("tool") == "read"]
        assert reads, "no read tool call happened"
        out = _tool_output(reads[0])
        assert "NAVIGATION TIP" not in out and "THINK-ANYWHERE" not in out, (
            f"--pure must disable plugin hooks, got injections: {out[:300]!r}")


class TestLiveBeforeHookGuards:
    def test_protected_file_edit_blocked_without_unlock(self):
        """BUG-A regression (live): a direct edit of README.md — protected per
        AGENTS.md, no phase/skip declared, agent instructed not to declare
        any — must be blocked by the before-hook; file stays byte-identical.
        Red when the before-hook reads input?.args (contract violation:
        before-hook args live on output)."""
        before = README.read_bytes()
        try:
            code, events, _ = _run_opencode(
                "Use the edit tool on README.md: replace the string '# agentx' "
                "with '# agentx-probe'. Do NOT call omt_phase, omt_skip or any "
                "other omt tool — attempt the edit directly. Then report the "
                "exact tool result.")
            assert code == 0
            edits = [p for p in _tool_uses(events) if p.get("tool") == "edit"]
            assert README.read_bytes() == before, (
                "GUARD DEAD: README.md was modified without any phase/skip — "
                "the before-hook protected-file guard did not fire "
                f"(edit results: {[_tool_output(e)[:120] for e in edits]})")
            if edits:
                err = _tool_output(edits[0])
                assert "protected" in err.lower() or "OMT" in err, (
                    f"edit was rejected but not by the OMT guard: {err[:200]!r}")
        finally:
            README.write_bytes(before)

    def test_plugin_file_edit_blocked_by_e2e_receipt_guard(self):
        """BUG-B regression (live): the SECOND edit of a git-dirty enforcement
        plugin with a stale e2e receipt must be blocked (isOmtHarness →
        omtHarnessE2eStatus, enforcer :548-569). This is a SECOND-EDIT guard:
        `if (!isGitDirty(rel)) return ok` — content-based, so os.utime/touch
        alone can never engage it (that was the flawed pre-redesign probe).
        Design: dirty omt_status.ts with probe content written from THIS
        process (real content change ⇒ git-dirty; mtime=now ⇒ receipt stale),
        then attempt an edit of the probe marker via real opencode → expect
        blocked with "unverified changes"; file stays byte-identical to the
        probe content. Original content restored in finally (file returns to
        git-clean)."""
        before = STATUS_PLUGIN.read_bytes()
        probe = before + b"\n// OMT_LIVE_PROBE_MARKER safe to remove\n"
        STATUS_PLUGIN.write_bytes(probe)  # first "edit": git-dirty + stale mtime
        try:
            code, events, _ = _run_opencode(
                "Use the edit tool on .opencode/plugins/omt_status.ts: replace "
                "the string 'OMT_LIVE_PROBE_MARKER' with 'OMT_LIVE_PROBE_EDITED'. "
                "Do NOT call omt_phase, omt_skip or any other omt tool; do NOT "
                "use bash, git or any other tool to modify, restore or revert "
                "the file — attempt the edit exactly once, then report the "
                "exact tool result.")
            assert code == 0
            edits = [p for p in _tool_uses(events) if p.get("tool") == "edit"]
            assert STATUS_PLUGIN.read_bytes() == probe, (
                "GUARD DEAD: a git-dirty enforcement plugin was modified with "
                "a stale e2e receipt — isOmtHarness does not cover "
                ".opencode/plugins/ (singular/plural prefix drift, BUG-B) or "
                "omtHarnessE2eStatus is not firing "
                f"(edit results: {[_tool_output(e)[:120] for e in edits]})")
            if edits:
                err = _tool_output(edits[0])
                assert "unverified changes" in err or "OMT" in err, (
                    f"edit was rejected but not by the e2e receipt guard: "
                    f"{err[:200]!r}")
        finally:
            STATUS_PLUGIN.write_bytes(before)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
