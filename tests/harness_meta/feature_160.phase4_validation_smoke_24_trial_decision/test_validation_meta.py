"""Phase4 validation goldens (feature_160) — smoke + 24-trial dry_run, fake executor only."""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]

CASES = [
    "recover-block-positive",
    "resume-work-reconcile",
    "verify-closeout-checklist",
    "session-compat-envelope",
]
VARIANTS = ["baseline", "treatment"]
REPS = 3


def _validation():
    sys.path.insert(0, str(REPO / "scripts" / "omt" / "bench"))
    try:
        import validation as v
        return v
    finally:
        sys.path.pop(0)


class TestValidation:
    def test_manifest_valid(self):
        v = _validation()
        m = v.phase4_manifest()
        assert m.get("version") == 1
        assert m["experiment"] == "phase4_validation"
        assert m["decision_rule"] == "quality_gated_paired_compare"
        assert m["cases"] == CASES
        assert m["variants"] == VARIANTS
        assert m["reps"] == REPS

    def test_matrix_24_no_exec(self):
        sys.path.insert(0, str(REPO / "scripts"))
        try:
            from session_inspect.manifest import expand_matrix
            v = _validation()
            m = v.phase4_manifest()
            trials = expand_matrix(m)
            assert len(trials) == 24
            assert len({t["trial"] for t in trials}) == 24
            for t in trials:
                assert t["case"] in CASES and t["variant"] in VARIANTS
        finally:
            sys.path.pop(0)
            for mod in list(sys.modules):
                if mod.startswith("session_inspect"):
                    sys.modules.pop(mod, None)

    def test_budgets_gate_refuses(self):
        sys.path.insert(0, str(REPO / "scripts"))
        try:
            from session_inspect import run_gate
            v = _validation()
            m = v.phase4_manifest()
            r1 = run_gate.gate_run(m, isolation={"base": "/tmp/mh160-iso"}, budgets=None, claims=None, explicit_p=False)
            assert r1["allowed"] is False and r1["executed"] is False
            r2 = run_gate.gate_run(m, isolation={"base": "/tmp/mh160-iso"},
                                   budgets={"tokens": 1, "time_s": 1, "concurrency": 1},
                                   claims=None, explicit_p=False)
            assert r2["allowed"] is False and "no_safe_launch" in r2["reason"]
        finally:
            sys.path.pop(0)
            for mod in list(sys.modules):
                if mod.startswith("session_inspect"):
                    sys.modules.pop(mod, None)

    def test_isolation_guard(self):
        sys.path.insert(0, str(REPO / "scripts"))
        try:
            from session_inspect import run_gate
            v = _validation()
            m = v.phase4_manifest()
            ok = run_gate.check_isolation(m, dest="/tmp/mh160-iso")
            assert ok["ok"] is True
            for bad in ("/tmp/x.opencode.db/y", "/tmp/x.env/y", "/tmp/x.git/y"):
                try:
                    run_gate.check_isolation(m, dest=bad)
                    guarded = False
                except Exception:
                    guarded = True
                assert guarded is True
        finally:
            sys.path.pop(0)
            for mod in list(sys.modules):
                if mod.startswith("session_inspect"):
                    sys.modules.pop(mod, None)

    def test_smoke_doctor(self):
        r = subprocess.run([sys.executable, "scripts/omt/skill.py", "list"],
                           capture_output=True, text=True, cwd=str(REPO), timeout=30)
        out = (r.stdout or "") + (r.stderr or "")
        assert "omt-recover-block" in out and "omt-resume-work" in out and "omt-verify-closeout" in out
        for sid in ("omt-recover-block", "omt-resume-work", "omt-verify-closeout"):
            d = subprocess.run([sys.executable, "scripts/omt/skill.py", "doctor", sid],
                               capture_output=True, text=True, cwd=str(REPO), timeout=30)
            dout = (d.stdout or "") + (d.stderr or "")
            assert "contract-ok" in dout or "OK" in dout, sid

    def test_compare_quality_gated(self):
        sys.path.insert(0, str(REPO / "scripts"))
        try:
            from session_inspect.manifest import expand_matrix
            from session_inspect import evaluate
            v = _validation()
            m = v.phase4_manifest()
            trials = expand_matrix(m)
            bad_metrics = {t["trial"]: {"quality": "pass", "cost": 10} for t in trials}
            one = trials[0]["trial"]
            bad_metrics[one] = {"quality": "fail", "cost": 1}
            comp = evaluate.compare(m, bad_metrics)
            assert "inconclusive" in str(comp).lower()
            good_metrics = {t["trial"]: {"quality": "pass", "cost": 5 if t["variant"] == "treatment" else 10} for t in trials}
            comp2 = evaluate.compare(m, good_metrics)
            assert comp2 is not None
        finally:
            sys.path.pop(0)
            for mod in list(sys.modules):
                if mod.startswith("session_inspect"):
                    sys.modules.pop(mod, None)

    def test_envelope_mapping(self):
        sys.path.insert(0, str(REPO / "scripts" / "omt"))
        try:
            import skill_result as sr
            assert hasattr(sr, "from_session")
            shapes = [
                {"ok": False, "version": 1, "error": "manifest_invalid", "code": "MANIFEST_INVALID", "detail": "x", "retryable": False},
                {"ok": False, "version": 1, "error": "missing_db", "code": "MISSING_DB", "detail": "x", "detail_ref": "sessions:missing", "retryable": True},
            ]
            for shape in shapes:
                env = sr.from_session(shape)
                assert sr.validate_envelope(env) == [], shape
                assert env["outcome"] in ("blocked", "failed")
        finally:
            sys.path.pop(0)
            sys.modules.pop("skill_result", None)
