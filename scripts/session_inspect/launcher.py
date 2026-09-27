"""launcher.py — fake-executor trial launcher (feature_134, fake slice).

Stdlib-only, no subprocess, no tokens, no sleeps. Fake executor only;
`executed` stays False for fakes (live `executed:true` is a future slice).
Every failure is a named finding (closed vocabulary).

Design refs: design_001_real_trial_launcher.md §3,
operation_spec_001_fake_launcher.md.
"""
from __future__ import annotations

from typing import Any, Callable

from .manifest import expand_matrix
from .schema import Finding, FindingError

BUDGET_S = 300
ISOLATION_BASE = "/tmp/mh134-iso"


def plan_trials(mdoc: dict[str, Any]) -> list[dict[str, Any]]:
    """Expand the 12-trial matrix in deterministic order (seed 0 = in-order).

    Uses `manifest.expand_matrix` (validates, raises `manifest_invalid` on
    bad input). Order-seed shuffle is recorded as seed 0 for the fake slice
    so `test_fake_plans_12_in_order` holds; real shuffling is a future slice.
    """
    trials = expand_matrix(mdoc)
    return [dict(t) for t in trials]


def dispatch_fake(
    trial: dict[str, Any],
    *,
    executor: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]],
) -> dict[str, Any]:
    """Call the injected fake executor once (sequential, concurrency 1).

    Isolation is a `/tmp` per-trial stub (never created here; real creation
    uses `tmp_path` in tests or a future worktree slice).
    """
    isolation = {"base": f"/tmp/mh134-{trial.get('trial', 'unknown')}"}
    try:
        res = executor(dict(trial), dict(isolation))
    except Exception as exc:
        raise FindingError(
            Finding("trial_incomplete", {"trial": trial.get("trial"), "reason": str(exc)[:200]}, None)
        ) from exc
    out = dict(res)
    out.setdefault("trial", trial.get("trial"))
    out.setdefault("outcome", "pass")
    out.setdefault("attempt", 1)
    return out


def enforce_timeout(result: dict[str, Any], *, budget_s: int = BUDGET_S) -> dict[str, Any]:
    """Strict-once timeout: over-budget duration becomes failed trial, no retry."""
    out = dict(result)
    try:
        duration = float(out.get("duration_s", 0) or 0)
    except (TypeError, ValueError):
        duration = 0
    if duration > budget_s:
        out["outcome"] = "timeout_failed"
    out["attempt"] = 1
    return out


def collect_fake(results: list[dict[str, Any]], *, manifest: dict[str, Any]) -> dict[str, Any]:
    """Build a stub TrialReport: membership + stub usage, independent N = usable."""
    from .manifest import validate as _validate

    _validate(manifest)
    rows = [dict(r) for r in results]
    usable = sum(1 for r in rows if r.get("outcome") == "pass")
    return {
        "trials": rows,
        "n_trials": len(rows),
        "usable": usable,
        "independent_n": usable,
        "executed": False,
        "detail_ref": f"collect:{usable}/{len(rows)}",
    }


def run_fake(
    mdoc: dict[str, Any],
    *,
    executor: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]],
    claims: dict[str, Any] | None,
    explicit_p: bool,
) -> dict[str, Any]:
    """Gate via 132 `gate_run`, then run fakes sequentially (never live).

    Refusals map to the same `no_safe_launch` contract as the 133 dispatcher.
    Allowed returns `{allowed:True, n_trials, executed:False, fake_n}`.
    """
    from . import run_gate as _gate

    budgets = mdoc.get("budgets") if isinstance(mdoc.get("budgets"), dict) else None
    isolation = mdoc.get("isolation") if isinstance(mdoc.get("isolation"), dict) else {"base": ISOLATION_BASE}
    gate = _gate.gate_run(
        mdoc,
        isolation=isolation,
        budgets=budgets,
        claims=claims,
        explicit_p=bool(explicit_p),
    )
    if not gate.get("allowed"):
        reason = str(gate.get("reason", "no_safe_launch"))
        out: dict[str, Any] = {"allowed": False, "executed": False}
        # Preserve S5/S6 contract: top-level reason stays no_safe_launch detail.
        if reason.startswith("no_safe_launch"):
            out["reason"] = reason
        else:
            out["reason"] = f"no_safe_launch: {reason}"
            if gate.get("detail"):
                out["detail"] = str(gate["detail"])[:200]
            elif gate.get("reason"):
                out["detail"] = str(gate["reason"])[:200]
        return out
    trials = plan_trials(mdoc)
    results = [enforce_timeout(dispatch_fake(t, executor=executor)) for t in trials]
    return {
        "allowed": True,
        "n_trials": len(trials),
        "executed": False,
        "fake_n": len(results),
    }
