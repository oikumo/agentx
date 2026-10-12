"""Verify-closeout pilot goldens (feature_158) — contracted skill, no LLM, hermetic."""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SKILL_CLI = REPO / "scripts" / "omt" / "skill.py"
SKILL_DIR = REPO / ".opencode" / "skills" / "omt-verify-closeout"
CHECKLIST = SKILL_DIR / "references" / "closeout_checklist.md"


def _validate_contract(contract, skill_dir="omt-verify-closeout"):
    sys.path.insert(0, str(REPO / "scripts" / "omt"))
    try:
        import skill as skill_mod
        return skill_mod.validate_contract(contract, skill_dir)
    finally:
        sys.path.pop(0)
        sys.modules.pop("skill", None)


class TestVerifyCloseout:
    def test_accepts_contract_valid(self):
        contract = json.loads((SKILL_DIR / "skill.contract.json").read_text(encoding="utf-8"))
        assert _validate_contract(contract) == []

    def test_doctor_greens_verify_closeout(self):
        r = subprocess.run(
            [sys.executable, str(SKILL_CLI), "doctor", "omt-verify-closeout"],
            capture_output=True, text=True, cwd=str(REPO),
        )
        assert r.returncode == 0, r.stdout + r.stderr
        assert "contract OK" in r.stdout

    def test_checklist_covers_evidence(self):
        text = CHECKLIST.read_text(encoding="utf-8").lower()
        for needle in ("docs", "doctor", "golden", "work", "tdd", "split_proof"):
            assert needle in text, needle

    def test_stop_when_maps_to_outcomes(self):
        sys.path.insert(0, str(REPO / "scripts" / "omt"))
        try:
            import skill_result as sr_mod
            cases = {
                "verified": sr_mod.make_succeeded("OK", ["closeout"]),
                "blocked": sr_mod.make_blocked(
                    "GATE_DENIED",
                    {"gate": "closeout", "code": "GATE_DENIED", "message": "x", "requiresApproval": False},
                    ["closeout"], False),
                "not_applicable": sr_mod.make_not_applicable("NOT_APPLICABLE", ["closeout"]),
                "inconclusive": sr_mod.make_inconclusive("INCONCLUSIVE", ["closeout"]),
            }
            expected = {"verified": "succeeded", "blocked": "blocked",
                        "not_applicable": "not_applicable", "inconclusive": "inconclusive"}
            for stop, env in cases.items():
                assert env["outcome"] == expected[stop], stop
                assert sr_mod.validate_envelope(env) == [], stop
        finally:
            sys.path.pop(0)
            sys.modules.pop("skill_result", None)

    def test_missing_slug_yields_not_applicable(self):
        sys.path.insert(0, str(REPO / "scripts" / "omt"))
        try:
            import skill_result as sr_mod
            bogus = "feature_999.nope_missing"
            assert not (REPO / ".meta" / "software_development_process" / "2.requirements" / "features" / bogus).exists()
            env = sr_mod.make_not_applicable("NOT_APPLICABLE", [bogus])
            assert env["outcome"] == "not_applicable" and env["ok"] is False
            assert sr_mod.validate_envelope(env) == []
        finally:
            sys.path.pop(0)
            sys.modules.pop("skill_result", None)

    def test_rejects_tampered_contract(self):
        contract = json.loads((SKILL_DIR / "skill.contract.json").read_text(encoding="utf-8"))
        bad = dict(contract, state_owner="skill")
        errs = _validate_contract(bad)
        assert any("state_owner" in e or "external" in e for e in errs)

    def test_verify_envelopes_obey_ok_rule(self):
        sys.path.insert(0, str(REPO / "scripts" / "omt"))
        try:
            import skill_result as sr_mod
            ok_env = sr_mod.make_succeeded("OK", ["e"])
            bad_env = sr_mod.make_blocked(
                "GATE_DENIED",
                {"gate": "g", "code": "GATE_DENIED", "message": "m", "requiresApproval": False},
                ["e"], False)
            assert ok_env["ok"] is True and sr_mod.validate_envelope(ok_env) == []
            assert bad_env["ok"] is False and sr_mod.validate_envelope(bad_env) == []
            mismatch = dict(ok_env, outcome="blocked", blocker=dict(bad_env["blocker"]))
            assert sr_mod.validate_envelope(mismatch) != []
        finally:
            sys.path.pop(0)
            sys.modules.pop("skill_result", None)
