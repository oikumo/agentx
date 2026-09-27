"""manifest.py — experiment manifest contract (feature_131 S4).

A manifest declares intended trials: hypothesis, cases, baseline/variants,
real repetition counts, budgets, isolation, outcome checks, metrics, and the
predeclared decision rule. Validation is strict: problems raise a named
`manifest_invalid` finding error, never a silent default.
"""
from __future__ import annotations

from typing import Any, Optional

from .schema import Finding, FindingError

MANIFEST_VERSION = 1

_REQUIRED = ("experiment", "run", "cases", "variants", "reps")


def create(experiment: str, run: str, *, cases: list[str],
           variants: list[str], reps: int,
           hypothesis: str = "",
           budgets: Optional[dict[str, Any]] = None,
           decision_rule: str = "quality_gated_paired_compare") -> dict[str, Any]:
    """Build a versioned manifest dict (validated before return)."""
    m = {"version": MANIFEST_VERSION, "experiment": experiment, "run": run,
         "hypothesis": hypothesis, "cases": list(cases),
         "variants": list(variants), "reps": reps,
         "budgets": dict(budgets or {}), "decision_rule": decision_rule}
    validate(m)
    return m


def validate(m: dict[str, Any]) -> dict[str, Any]:
    """Validate a manifest; ok or FindingError(manifest_invalid)."""
    for key in _REQUIRED:
        if key not in m:
            raise FindingError(Finding(
                "manifest_invalid", {"missing": key}, None))
    if m.get("version") != MANIFEST_VERSION:
        raise FindingError(Finding(
            "manifest_invalid",
            {"reason": "version_mismatch",
             "version": m.get("version")}, None))
    if not m.get("cases") or not m.get("variants"):
        raise FindingError(Finding(
            "manifest_invalid",
            {"reason": "empty_cases_or_variants"}, None))
    if not isinstance(m.get("reps"), int) or m["reps"] < 1:
        raise FindingError(Finding(
            "manifest_invalid", {"reason": "bad_reps",
                                 "reps": m.get("reps")}, None))
    return {"ok": True}


def expand_matrix(m: dict[str, Any]) -> list[dict[str, Any]]:
    """Expand the exact trial matrix (dry-run basis, no execution)."""
    validate(m)
    trials = []
    for case in m["cases"]:
        for variant in m["variants"]:
            for rep in range(1, m["reps"] + 1):
                trials.append({
                    "trial": f"{case}_{variant}_rep{rep:02d}",
                    "case": case, "variant": variant, "rep": rep,
                    "experiment": m["experiment"], "run": m["run"],
                })
    return trials


def dry_run(m: dict[str, Any]) -> dict[str, Any]:
    """Expand the trial matrix with rendered labels/commands (no execution)."""
    import json as _json
    trials = expand_matrix(m)
    label_lines = []
    for t in trials:
        payload = {"v": 1, "experiment": t["experiment"], "run": t["run"],
                   "trial": t["trial"], "case": t["case"],
                   "variant": t["variant"], "rep": t["rep"], "attempt": 1,
                   "event": "trial_start"}
        label_lines.append("[mh13.experiment] " + _json.dumps(payload))
    return {"trials": trials, "n_trials": len(trials),
            "label_lines": label_lines, "executed": False,
            "isolation": "per-trial worktree/selector (planned, not launched)"}
