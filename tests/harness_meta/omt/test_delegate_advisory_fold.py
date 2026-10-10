"""T3-2 delegate-advisory fold (feature_071.delegate_advisory_fold).

Golden: research-heavy resume (session with >=1 complete re-deriving KB/nav,
or fresh feature resume) and research-shaped op:plan (grep|glob|rg|find)
emit advisory delegate_hint {subagent_type, suggested_prompt}; advisory-only
(agent free to ignore, never blocks).
"""

import json
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
OMT_Q_PLUGIN = REPO_ROOT / ".opencode" / "plugins" / "omt_q.ts"
SHARED_LIB = REPO_ROOT / ".opencode" / "lib" / "omt_shared.ts"

BUN = shutil.which("bun")


def _copy_real_ir(tmp_path: Path) -> None:
    ir_dst = tmp_path / ".meta" / ".omt"
    ir_dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(
        REPO_ROOT / ".meta" / ".omt" / "harness.ir.json",
        ir_dst / "harness.ir.json",
    )


def _write_ledger(tmp_path: Path, records: list[dict]) -> None:
    p = tmp_path / ".meta" / ".omt" / "ledger.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")


_q_probe_template = """
import { initOmtShared } from "%LIB%"
initOmtShared(process.argv[2])
const mod = await import("%PLUGIN%")
const { tool } = await mod.default({ directory: process.argv[2], worktree: process.argv[2] })
const args = %ARGS%
const result = await tool.omt_q.execute(args, { sessionID: "%SESSION%" })
console.log(result)
"""


def _q_probe(args_str: str, session: str, tmp_path: Path) -> dict:
    assert BUN is not None, "bun runtime required"
    probe = tmp_path / "probe_t32.ts"
    probe.write_text(
        _q_probe_template
        .replace("%LIB%", str(SHARED_LIB))
        .replace("%PLUGIN%", str(OMT_Q_PLUGIN))
        .replace("%ARGS%", args_str)
        .replace("%SESSION%", session),
        encoding="utf-8",
    )
    out = subprocess.run([BUN, str(probe), str(tmp_path)],
                         capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, f"bun probe failed:\n{out.stderr}\n---"
    return json.loads(out.stdout.strip().splitlines()[-1])


class TestDelegateAdvisoryFold:
    """T3-2: research-heavy resume + research-shaped plan emit advisory hint."""

    @pytest.mark.skipif(BUN is None, reason="bun runtime not available")
    def test_research_heavy_resume_emits_hint(self, tmp_path):
        _copy_real_ir(tmp_path)
        base = datetime.now(timezone.utc) - timedelta(hours=1)
        ts = lambda m: (base + timedelta(minutes=m)).strftime("%Y-%m-%dT%H:%M:%SZ")
        _write_ledger(tmp_path, [
            {"ts": ts(0), "kind": "think_consult", "session": "ses_t32a",
             "files": ["src/x.py"], "category": "gotcha",
             "feature": "feature_071.delegate_advisory_fold"},
            {"ts": ts(5), "kind": "complete", "session": "ses_t32a",
             "feature": "feature_071.delegate_advisory_fold",
             "phase": "Testing",
             "checklist": {"suite_passes": True, "refactor_recorded": True,
                           "naming_ok": True}},
        ])
        out = _q_probe(
            json.dumps({"op": "state",
                        "feature": "feature_071.delegate_advisory_fold",
                        "session": "ses_t32a"}),
            session="ses_t32a", tmp_path=tmp_path)
        assert out["op"] == "state"
        assert "delegate_hint" in out, f"research-heavy resume must emit hint: {out}"
        hint = out["delegate_hint"]
        assert hint["subagent_type"] in ("explore", "general"), f"hint type: {hint}"
        prompt = hint["suggested_prompt"]
        assert "ses_t32a" in prompt, f"prompt must scope to session: {prompt}"
        # loop recipe explore -> propose -> approval -> execute
        assert "explore" in prompt and "approval" in prompt, f"recipe: {prompt}"
        assert "Advisory" in prompt or "advisory" in prompt, f"advisory-only: {prompt}"

    @pytest.mark.skipif(BUN is None, reason="bun runtime not available")
    def test_research_shaped_plan_emits_hint(self, tmp_path):
        _copy_real_ir(tmp_path)
        out = _q_probe(
            json.dumps({"op": "plan", "path": "WORK.md",
                        "tool": "grep", "session": "ses_t32b"}),
            session="ses_t32b", tmp_path=tmp_path)
        assert out["op"] == "plan"
        assert "delegate_hint" in out, f"research-shaped plan must emit hint: {out}"
        hint = out["delegate_hint"]
        assert hint["subagent_type"] == "explore", f"research tool -> explore: {hint}"
        assert "WORK.md" in hint["suggested_prompt"] or "grep" in hint["suggested_prompt"], (
            f"prompt must name path/tool: {hint}")

    @pytest.mark.skipif(BUN is None, reason="bun runtime not available")
    def test_fresh_non_research_emits_no_hint(self, tmp_path):
        _copy_real_ir(tmp_path)
        # fresh state: empty ledger, no session completes -> no hint
        _write_ledger(tmp_path, [])
        out = _q_probe(
            json.dumps({"op": "state", "session": "ses_fresh_xyz"}),
            session="ses_fresh_xyz", tmp_path=tmp_path)
        assert out["op"] == "state"
        assert "delegate_hint" not in out, (
            f"fresh non-research state must NOT emit hint: {out}")
        # fresh non-research plan (edit, no session history) -> no hint,
        # advisory-only: delegate never blocks
        out2 = _q_probe(
            json.dumps({"op": "plan", "path": "src/agentx/ui/screens/main/main_controller.py",
                        "tool": "edit", "session": "ses_fresh_xyz"}),
            session="ses_fresh_xyz", tmp_path=tmp_path)
        assert out2["op"] == "plan"
        assert "delegate_hint" not in out2, (
            f"fresh non-research edit plan must NOT emit hint: {out2}")
