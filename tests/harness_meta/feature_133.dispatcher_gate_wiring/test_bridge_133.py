"""Bridge — feature_133 dispatcher wiring (Programming→Testing gate)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SYS_PATH = str(ROOT / "scripts")
if SYS_PATH not in sys.path:
    sys.path.insert(0, SYS_PATH)


def test_run_stays_gated():
    from session_inspect import service
    r = service.dispatch("experiment", {"sub": "run", "manifest": json.dumps({"version": 1})})
    assert r["ok"] is False and r["reason"] == "no_safe_launch"
    assert r.get("executed", False) is False


def test_run_allowed_still_no_execute():
    from session_inspect import service
    m = {"version": 1, "experiment": "context_strategy", "run": "run_001",
         "cases": ["markdown-summary", "python-fix"], "variants": ["baseline", "candidate"],
         "reps": 3, "budgets": {"tokens": 1000, "time_s": 60, "concurrency": 1},
         "isolation": {"base": "/tmp/mh133-iso"}, "claims": {"held": 12}, "explicit_p": True}
    r = service.dispatch("experiment", {"sub": "run", "manifest": json.dumps(m)})
    assert r["ok"] is True and r["result"]["allowed"] is True
    assert r["result"]["n_trials"] == 12 and r["result"].get("executed", False) is False
