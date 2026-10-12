"""Phase4 validation helper (feature_160) — manifest factory, stdlib only."""
from __future__ import annotations

import sys
from pathlib import Path

CASES = [
    "recover-block-positive",
    "resume-work-reconcile",
    "verify-closeout-checklist",
    "session-compat-envelope",
]
VARIANTS = ["baseline", "treatment"]
REPS = 3
EXPERIMENT = "phase4_validation"
RUN = "smoke_24trial"
DECISION_RULE = "quality_gated_paired_compare"
BUDGETS = {"tokens": 50000, "time_s": 600, "concurrency": 1}


def phase4_manifest(experiment: str = EXPERIMENT, run: str = RUN):
    """Build the 24-trial validation manifest (4 cases x 2 variants x 3 reps)."""
    repo_scripts = Path(__file__).resolve().parents[2]
    if str(repo_scripts) not in sys.path:
        sys.path.insert(0, str(repo_scripts))
        added = True
    else:
        added = False
    try:
        from session_inspect.manifest import create
        return create(
            experiment, run,
            cases=list(CASES),
            variants=list(VARIANTS),
            reps=REPS,
            hypothesis="Manual-only pilots cut mistaken steps vs baseline with envelope evidence",
            budgets=dict(BUDGETS),
            decision_rule=DECISION_RULE,
        )
    finally:
        if added:
            sys.path.remove(str(repo_scripts))
