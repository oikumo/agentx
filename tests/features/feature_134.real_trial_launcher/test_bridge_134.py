"""Bridge unit tests — feature_134 fake launcher (Programming→Testing gate).

Real suite lives in tests/scripts/session_inspect/test_fake_launcher.py (4 passed).
This bridge asserts plan + gated run from canonical tests/features location.
Unique basename test_bridge_134.py avoids 132/133 clash.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SYS_PATH = str(ROOT / "scripts")
if SYS_PATH not in sys.path:
    sys.path.insert(0, SYS_PATH)


def _manifest():
    from session_inspect import manifest
    return manifest.create(experiment="context_strategy", run="run_001",
                           cases=["markdown-summary", "python-fix"],
                           variants=["baseline", "candidate"], reps=3)


def test_fake_plans_12():
    from session_inspect import launcher
    trials = launcher.plan_trials(_manifest())
    assert len(trials) == 12
    assert len({t["trial"] for t in trials}) == 12


def test_run_fake_gated_no_execute():
    from session_inspect import launcher
    m = _manifest()
    refused = launcher.run_fake(m, executor=lambda t, isolation: {"trial": t["trial"], "outcome": "pass", "duration_s": 1, "attempt": 1},
                                claims=None, explicit_p=False)
    assert refused["allowed"] is False
    assert refused.get("executed", False) is False
    m2 = dict(m)
    m2["budgets"] = {"tokens": 1000, "time_s": 60, "concurrency": 1}
    allowed = launcher.run_fake(m2, executor=lambda t, isolation: {"trial": t["trial"], "outcome": "pass", "duration_s": 1, "attempt": 1},
                                claims={"held": 12}, explicit_p=True)
    assert allowed["allowed"] is True
    assert allowed["n_trials"] == 12 and allowed["fake_n"] == 12
    assert allowed.get("executed", False) is False
