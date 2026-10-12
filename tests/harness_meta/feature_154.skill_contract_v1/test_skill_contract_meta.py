"""Skill contract v1 goldens (feature_154) — validator behaviors, no LLM, hermetic."""

import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
SKILL_CLI = REPO / "scripts" / "omt" / "skill.py"

VALID = {
    "schema_version": "1",
    "id": "omt-recover-block",
    "version": "0.1.0",
    "mode": "procedural",
    "inputs": ["attempted_operation", "target_path", "observed_result"],
    "requires": ["omt_status.preflight"],
    "allowed_effects": ["read_harness_state", "invoke_existing_authorized_omt_tool", "retry_original_operation"],
    "forbidden_effects": ["weaken_gate", "forge_receipt", "expand_scope_without_authority"],
    "state_owner": "external",
    "result_schema": "omt-skill-result/v1",
    "stop_when": ["operation_succeeds", "authorization_is_required"],
}


def _validate(contract, skill_dir="omt-recover-block"):
    sys.path.insert(0, str(REPO / "scripts" / "omt"))
    try:
        import skill as skill_mod
        return skill_mod.validate_contract(contract, skill_dir)
    finally:
        sys.path.pop(0)
        sys.modules.pop("skill", None)


class TestSkillContract:
    def test_accepts_minimal_valid(self):
        assert _validate(dict(VALID)) == []

    def test_rejects_unknown_field(self):
        bad = dict(VALID, extra_nope=1)
        errs = _validate(bad)
        assert any("extra_nope" in e or "unknown" in e.lower() for e in errs)

    def test_rejects_name_mismatch(self):
        errs = _validate(dict(VALID), skill_dir="other-dir")
        assert any("omt-recover-block" in e or "mismatch" in e.lower() or "==" in e for e in errs)

    def test_rejects_missing_forbidden(self):
        bad = dict(VALID)
        bad["forbidden_effects"] = ["weaken_gate"]
        errs = _validate(bad)
        assert any("forge_receipt" in e or "forbidden" in e.lower() for e in errs)

    def test_rejects_empty_stop_when(self):
        bad = dict(VALID, stop_when=[])
        errs = _validate(bad)
        assert errs != []

    def test_doctor_greens_scaffolded_skill(self):
        r = subprocess.run(
            [sys.executable, str(SKILL_CLI), "doctor", "omt-recover-block"],
            capture_output=True, text=True, cwd=str(REPO),
        )
        assert r.returncode == 0, r.stdout + r.stderr
        assert "contract OK" in r.stdout

    def test_list_sorted_with_status(self):
        r = subprocess.run(
            [sys.executable, str(SKILL_CLI), "list"],
            capture_output=True, text=True, cwd=str(REPO),
        )
        assert r.returncode == 0, r.stdout + r.stderr
        lines = [ln for ln in r.stdout.splitlines() if ln.strip()]
        assert any(ln.startswith("omt-recover-block ") for ln in lines)
        assert lines == sorted(lines)
