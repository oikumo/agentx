"""Resume-work pilot goldens (feature_157) — contracted skill, no LLM, hermetic."""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SKILL_CLI = REPO / "scripts" / "omt" / "skill.py"
SKILL_DIR = REPO / ".opencode" / "skills" / "omt-resume-work"
CHECKLIST = SKILL_DIR / "references" / "resume_checklist.md"


def _validate_contract(contract, skill_dir="omt-resume-work"):
    sys.path.insert(0, str(REPO / "scripts" / "omt"))
    try:
        import skill as skill_mod
        return skill_mod.validate_contract(contract, skill_dir)
    finally:
        sys.path.pop(0)
        sys.modules.pop("skill", None)


def _envelope():
    sys.path.insert(0, str(REPO / "scripts" / "omt"))
    try:
        import skill_result as sr_mod
        return sr_mod
    finally:
        sys.path.pop(0)


class TestResumePilot:
    def test_accepts_contract_valid(self):
        contract = json.loads((SKILL_DIR / "skill.contract.json").read_text(encoding="utf-8"))
        assert _validate_contract(contract) == []

    def test_doctor_greens_resume_work(self):
        r = subprocess.run(
            [sys.executable, str(SKILL_CLI), "doctor", "omt-resume-work"],
            capture_output=True, text=True, cwd=str(REPO),
        )
        assert r.returncode == 0, r.stdout + r.stderr
        assert "contract OK" in r.stdout

    def test_checklist_covers_owners(self):
        text = CHECKLIST.read_text(encoding="utf-8").lower()
        for needle in ("pause", "head", "status", "current_state", "project", "feature", "work"):
            assert needle in text, needle

    def test_stop_when_maps_to_outcomes(self):
        sys.path.insert(0, str(REPO / "scripts" / "omt"))
        try:
            import skill_result as sr_mod
            cases = {
                "reconciled": sr_mod.make_succeeded("OK", ["pause"]),
                "blocker_found": sr_mod.make_blocked(
                    "GATE_DENIED",
                    {"gate": "omt", "code": "GATE_DENIED", "message": "mismatch", "requiresApproval": False},
                    ["pause"], True),
                "authorization_required": sr_mod.make_blocked(
                    "GATE_DENIED",
                    {"gate": "omt", "code": "GATE_DENIED", "message": "auth", "requiresApproval": True},
                    ["pause"], False),
                "not_resumable": sr_mod.make_not_applicable("NOT_APPLICABLE", ["pause"]),
            }
            expected = {"reconciled": "succeeded", "blocker_found": "blocked",
                        "authorization_required": "blocked", "not_resumable": "not_applicable"}
            for stop, env in cases.items():
                assert env["outcome"] == expected[stop], stop
                assert sr_mod.validate_envelope(env) == [], stop
        finally:
            sys.path.pop(0)
            sys.modules.pop("skill_result", None)

    def test_stale_pause_yields_blocked(self):
        sys.path.insert(0, str(REPO / "scripts" / "omt"))
        try:
            import skill_result as sr_mod
            r = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                               capture_output=True, text=True, cwd=str(REPO))
            real_head = r.stdout.strip()
            assert real_head and real_head != "deadbeef"
            env = sr_mod.make_blocked(
                "GATE_DENIED",
                {"gate": "resume", "code": "GATE_DENIED",
                 "message": f"expected_head deadbeef != {real_head}", "requiresApproval": False},
                ["pause"], False)
            assert env["ok"] is False and env["outcome"] == "blocked"
            assert sr_mod.validate_envelope(env) == []
        finally:
            sys.path.pop(0)
            sys.modules.pop("skill_result", None)

    def test_rejects_unknown_field(self):
        contract = json.loads((SKILL_DIR / "skill.contract.json").read_text(encoding="utf-8"))
        bad = dict(contract, extra_nope=1)
        errs = _validate_contract(bad)
        assert any("extra_nope" in e or "unknown" in e.lower() for e in errs)

    def test_rejects_short_stop_when(self):
        contract = json.loads((SKILL_DIR / "skill.contract.json").read_text(encoding="utf-8"))
        bad = dict(contract, stop_when=["only_one"])
        errs = _validate_contract(bad)
        assert errs != []
