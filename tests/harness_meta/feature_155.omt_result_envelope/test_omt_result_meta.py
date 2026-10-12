"""OmtResult envelope v1 goldens (feature_155) — validator behaviors, no LLM, hermetic."""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SKILL_RESULT_CLI = REPO / "scripts" / "omt" / "skill_result.py"

VALID_SUCCEEDED = {
    "ok": True,
    "outcome": "succeeded",
    "code": "OK",
    "evidence": ["doctor omt-recover-block"],
    "retryable": False,
}

VALID_BLOCKED = {
    "ok": False,
    "outcome": "blocked",
    "code": "RECEIPT_REQUIRED",
    "blocker": {
        "gate": "omt_complete",
        "code": "RECEIPT_REQUIRED",
        "message": "receipt required before complete",
        "requiresApproval": False,
    },
    "evidence": ["omt_status preflight"],
    "retryable": True,
}


def _validate(obj):
    sys.path.insert(0, str(REPO / "scripts" / "omt"))
    try:
        import skill_result as sr_mod
        return sr_mod.validate_envelope(obj)
    finally:
        sys.path.pop(0)
        sys.modules.pop("skill_result", None)


class TestOmtResult:
    def test_accepts_minimal_succeeded(self):
        assert _validate(dict(VALID_SUCCEEDED)) == []

    def test_rejects_ok_outcome_mismatch(self):
        bad = dict(VALID_SUCCEEDED, ok=True, outcome="blocked")
        bad["blocker"] = dict(VALID_BLOCKED["blocker"])
        errs = _validate(bad)
        assert any("ok" in e.lower() or "succeeded" in e.lower() for e in errs)

    def test_rejects_blocked_without_blocker(self):
        bad = dict(VALID_BLOCKED)
        bad.pop("blocker", None)
        errs = _validate(bad)
        assert any("blocker" in e.lower() for e in errs)

    def test_rejects_unknown_field(self):
        bad = dict(VALID_SUCCEEDED, extra_nope=1)
        errs = _validate(bad)
        assert any("extra_nope" in e or "unknown" in e.lower() for e in errs)

    def test_rejects_missing_code(self):
        bad = dict(VALID_SUCCEEDED)
        bad.pop("code", None)
        errs = _validate(bad)
        assert any("code" in e.lower() for e in errs)

    def test_validate_cli_greens_golden(self):
        golden = Path(__file__).with_name("golden_succeeded.json")
        golden.write_text(json.dumps(VALID_SUCCEEDED, indent=2) + "\n", encoding="utf-8")
        r = subprocess.run(
            [sys.executable, str(SKILL_RESULT_CLI), "validate", str(golden)],
            capture_output=True, text=True, cwd=str(REPO),
        )
        assert r.returncode == 0, r.stdout + r.stderr
        assert "OK" in r.stdout

    def test_stop_when_maps_to_outcomes(self):
        sys.path.insert(0, str(REPO / "scripts" / "omt"))
        try:
            import skill_result as sr_mod
            mapping = {
                "operation_succeeds": "succeeded",
                "same_blocker_survives_legitimate_clearance": "blocked",
                "authorization_is_required": "blocked",
                "failure_is_not_an_omt_block": "not_applicable",
            }
            for stop, outcome in mapping.items():
                env = sr_mod.from_stop_when(stop)
                assert env["outcome"] == outcome, stop
        finally:
            sys.path.pop(0)
            sys.modules.pop("skill_result", None)
