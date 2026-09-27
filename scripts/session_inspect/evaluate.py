"""evaluate.py — manifest-bound validation + quality-aware comparison (feature_131 S4).

Compares expected (manifest matrix) and observed (bound trials) sets;
classifies missing/incomplete/unbound trials with reasons. Quality-aware
comparison evaluates the predeclared decision rule only when its quality
and comparability requirements hold, else returns inconclusive. Trial
execution (`request_run`) is explicitly effectful: this core has no safe
OpenCode launch path, so it returns a named unavailable result and keeps
plan/collect/compare functional (PROJECT.md fallback clause).
"""
from __future__ import annotations

from typing import Any

from .manifest import expand_matrix


def validate_collection(manifest: dict[str, Any],
                        report: Any) -> dict[str, Any]:
    """Expected vs observed trial sets; independent N counts usable only."""
    expected = [t["trial"] for t in expand_matrix(manifest)]
    observed = report.trials or {}
    missing = sorted(set(expected) - set(observed))
    unbound = sorted(set(observed) - set(expected))
    incomplete = sorted(tid for tid, e in observed.items()
                        if "trial_incomplete" in (e.exclusions or ()))
    usable = sorted(tid for tid, e in observed.items() if e.usable)
    return {"n_expected": len(expected),
            "n_observed": len(observed),
            "n_usable": len(usable),
            "n_independent": len(usable),
            "missing": missing,
            "unbound": unbound,
            "incomplete": incomplete,
            "usable": usable}


def compare(manifest: dict[str, Any],
            metrics: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Paired per-case comparison under the predeclared decision rule.

    A case supports the candidate only when quality holds on every
    repetition of both variants AND the candidate costs less. A cheaper
    failed task can never win. Cases without full quality fail
    inconclusive with the missing evidence named.
    """
    cases = []
    for case in manifest.get("cases", ()):
        reps = [t for t in expand_matrix(manifest) if t["case"] == case]
        base = [metrics.get(t["trial"], {}) for t in reps
                if t["variant"] == "baseline"]
        cand = [t for t in reps if t["variant"] != "baseline"]
        cand_m = [metrics.get(t["trial"], {}) for t in cand]
        if not base or not cand_m:
            cases.append({"case": case, "decision": "inconclusive",
                          "reason": "missing_variant_reps"})
            continue
        if any(m.get("quality") != "pass" for m in base + cand_m):
            cases.append({"case": case, "decision": "inconclusive",
                          "reason": "quality_not_held"})
            continue
        b_in = sum(m.get("input", 0) or 0 for m in base)
        c_in = sum(m.get("input", 0) or 0 for m in cand_m)
        if c_in < b_in:
            cases.append({"case": case, "decision": "candidate_supported",
                          "reason": "quality_held_cheaper",
                          "delta_input": c_in - b_in})
        else:
            cases.append({"case": case, "decision": "baseline_held",
                          "reason": "quality_held_not_cheaper",
                          "delta_input": c_in - b_in})
    if cases and all(c["decision"] == "candidate_supported" for c in cases):
        decision: str = "candidate_supported"
    else:
        decision = "inconclusive"
    return {"cases": cases, "decision": decision,
            "rule": manifest.get("decision_rule")}


def request_run(manifest: dict[str, Any]) -> dict[str, Any]:
    """Guarded trial execution (PROJECT.md fallback: launch unavailable).

    Returns a named unavailable result; plan/collect/compare stay
    functional and `dry_run` shows exactly what would execute. Never
    launches model calls or invents trials as a side effect.
    """
    from .manifest import dry_run as _dry
    plan = _dry(manifest)
    return {"status": "unavailable",
            "reason": "no_safe_launch: no authorized OpenCode execution "
                      "path in this core; use dry_run plan + explicit "
                      "Tier-2 invocation",
            "executed": False, "n_trials_planned": plan["n_trials"]}


def replay_n(validation: dict[str, Any]) -> int:
    """Independent N recomputed from saved validation (never increases)."""
    return int(validation.get("n_independent", 0))
