"""Bridge unit tests — feature_132 run-gate (Programming→Testing gate).

Real suite lives in tests/scripts/session_inspect/test_run_gate.py (5 passed).
This bridge asserts gate refusal + allow paths from canonical tests/features location.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SYS_PATH = str(ROOT / "scripts")
if SYS_PATH not in sys.path:
    sys.path.insert(0, SYS_PATH)


def test_gate_refuses_without_p():
    from session_inspect import manifest, run_gate
    m = manifest.create(experiment="context_strategy", run="run_001",
                        cases=["markdown-summary", "python-fix"],
                        variants=["baseline", "candidate"], reps=3)
    res = run_gate.gate_run(m, isolation={"base": "/tmp/mh132-iso"},
                            budgets={"tokens": 1000, "time_s": 60, "concurrency": 1},
                            claims=None, explicit_p=False)
    assert res["allowed"] is False
    assert res.get("executed", False) is False


def test_gate_allows_with_claims_and_p():
    from session_inspect import manifest, run_gate
    m = manifest.create(experiment="context_strategy", run="run_001",
                        cases=["markdown-summary", "python-fix"],
                        variants=["baseline", "candidate"], reps=3)
    res = run_gate.gate_run(m, isolation={"base": "/tmp/mh132-iso"},
                            budgets={"tokens": 1000, "time_s": 60, "concurrency": 1},
                            claims={"held": 12}, explicit_p=True)
    assert res["allowed"] is True
    assert res["n_trials"] == 12
    assert res.get("executed", False) is False
