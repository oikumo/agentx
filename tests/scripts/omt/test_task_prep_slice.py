"""T3-5 task-prep op slice (feature_073.task_prep_op_slice).

Golden: ONE bounded prep call covers a routine bugfix (identity + risk +
knowledge pointers + restrictions + evidence + next action); block ==
preflight decision (same dry chain); risk escalates on change
characteristics even for bug_fix; changed scope refreshes obligations; no
consultation/approval fabricated; T4-1 evaluator reused for g.net note.
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
PREP_MOD = REPO_ROOT / ".opencode" / "lib" / "enforcer" / "task_prep.ts"
PRE_MOD = REPO_ROOT / ".opencode" / "lib" / "enforcer" / "preflight.ts"

BUN = shutil.which("bun")

_PROBE_TEMPLATE = """
import { buildTaskPrep } from "%PREP%"
import { preflightProjection } from "%PRE%"
const input = %INPUT%
const prep: any = await buildTaskPrep(input)
const proj: any = await preflightProjection(input.path, input.tool || "edit", input.session)
console.log(JSON.stringify({ prep, summary: proj.summary, first: proj.summary.first_blocker }))
"""


def _probe(inp: dict, tmp_path: Path) -> dict:
    assert BUN is not None, "bun runtime required"
    probe = tmp_path / "probe_t35.ts"
    probe.write_text(
        _PROBE_TEMPLATE.replace("%PREP%", str(PREP_MOD)).replace(
            "%PRE%", str(PRE_MOD)).replace("%INPUT%", json.dumps(inp)),
        encoding="utf-8",
    )
    out = subprocess.run([BUN, str(probe)], capture_output=True, text=True,
                         timeout=60, cwd=str(REPO_ROOT))
    assert out.returncode == 0, f"bun probe failed:\n{out.stderr}\n---"
    return json.loads(out.stdout.strip().splitlines()[-1])


class TestTaskPrepSlice:
    """T3-5: one prep call, block==preflight, risk by characteristics."""

    @pytest.mark.skipif(BUN is None, reason="bun runtime not available")
    def test_routine_bugfix_one_call_bounded(self, tmp_path):
        inp = {"path": "src/agentx/foo.py", "tool": "edit",
               "session": "ses_probe", "feature": "feature_073.task_prep_op_slice",
               "task_type": "bug_fix", "description": "fix null check in foo handler return path"}
        r = _probe(inp, tmp_path)
        prep = r["prep"]
        # one call carries all five obligations
        for k in ("identity", "risk", "knowledge", "restrictions", "evidence", "next_action"):
            assert k in prep, f"missing {k}"
        assert prep["identity"]["path"] == inp["path"]
        assert prep["identity"]["task_type"] == "bug_fix"
        assert prep["knowledge"]["consulted"] is False
        assert prep["approved"] is False
        assert len(prep["evidence"]) >= 2
        assert prep["next_action"]
        # bounded (~2KB budget, hard cap 3KB for prose variance)
        assert len(json.dumps(prep)) <= 3072, f"prep not bounded: {len(json.dumps(prep))}B"
        # block == preflight decision (same dry chain)
        assert prep["blocked"] == (r["summary"]["would_block"] > 0)
        assert prep["first_blocker"] == r["first"]

    @pytest.mark.skipif(BUN is None, reason="bun runtime not available")
    def test_block_equals_preflight_on_blocker(self, tmp_path):
        # README.md needs scope=all; our tests-scope canary must NOT clear it
        inp = {"path": "README.md", "tool": "edit",
               "session": "ses_probe", "task_type": "bug_fix",
               "description": "fix typo in readme installation section"}
        r = _probe(inp, tmp_path)
        prep = r["prep"]
        assert prep["blocked"] == (r["summary"]["would_block"] > 0)
        assert prep["first_blocker"] == r["first"]
        assert prep["blocked"] is True
        assert prep["first_blocker"] == "g.protect"
        assert "all" in prep["next_action"]

    @pytest.mark.skipif(BUN is None, reason="bun runtime not available")
    def test_risk_escalates_on_characteristics(self, tmp_path):
        # small bugfix label, critical permission surface -> not low
        inp = {"path": "src/agentx/auth/policy.py", "tool": "edit",
               "session": "ses_probe", "task_type": "bug_fix",
               "description": "fix permission check bypass in auth gate"}
        r = _probe(inp, tmp_path)
        prep = r["prep"]
        assert prep["risk"]["level"] in ("medium", "high")
        assert prep["risk"]["signals"]["affectsContracts"] is True
        # high-risk evidence demands more than low-risk base
        assert len(prep["evidence"]) >= 2

    @pytest.mark.skipif(BUN is None, reason="bun runtime not available")
    def test_scope_change_refreshes_obligations(self, tmp_path):
        a = _probe({"path": "src/agentx/foo.py", "tool": "edit",
                    "session": "ses_probe", "task_type": "bug_fix",
                    "description": "fix null check in foo handler return path"}, tmp_path)["prep"]
        b = _probe({"path": "README.md", "tool": "edit",
                    "session": "ses_probe", "task_type": "bug_fix",
                    "description": "fix typo in readme installation section"}, tmp_path)["prep"]
        assert a["scope"] != b["scope"]
        assert (a["first_blocker"], a["blocked"]) != (b["first_blocker"], b["blocked"])
        assert "re-call prep" in a["note"]

    @pytest.mark.skipif(BUN is None, reason="bun runtime not available")
    def test_typed_policy_reused(self, tmp_path):
        inp = {"path": "src/agentx/foo.py", "tool": "edit",
               "session": "ses_probe", "task_type": "bug_fix",
               "description": "fix null check in foo handler return path"}
        r = _probe(inp, tmp_path)
        pol = r["prep"]["policy"]
        assert pol["via"] in ("activation_solo_skip", "exception_break_glass",
                              "deny_concurrent_no_grant", "defer_untyped")
        assert pol["explanation"]
