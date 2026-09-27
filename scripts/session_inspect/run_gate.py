"""run_gate.py — guarded pre-checks for pilot launch (feature_132).

Stdlib-only, no launches, no tokens. All refusals are named findings.
"""
from __future__ import annotations

from typing import Any

from .manifest import expand_matrix, validate
from .schema import Finding, FindingError

_PROTECTED = (".env", "opencode.db", ".git/")


def check_manifest(mdoc: dict[str, Any]) -> dict[str, Any]:
    validate(mdoc)
    return {"ok": True}


def check_isolation(mdoc: dict[str, Any], base: str = "/tmp/mh132-iso",
                    dest: str = "", isolation: dict[str, Any] | None = None) -> dict[str, Any]:
    target = dest or (isolation or {}).get("base", base)
    low = str(target).replace("\\", "/")
    if any(p in low for p in _PROTECTED):
        raise FindingError(Finding("isolation_unavailable",
                                   {"dest": str(target), "reason": "protected_dest"}, None))
    return {"ok": True, "base": str(target)}


def check_budgets(mdoc: dict[str, Any], budgets: dict[str, Any] | None) -> dict[str, Any]:
    b = budgets or {}
    for field in ("tokens", "time_s", "concurrency"):
        if not b.get(field):
            raise FindingError(Finding("budget_missing", {"field": field}, None))
    return {"ok": True}


def gate_run(mdoc: dict[str, Any], isolation: dict[str, Any] | None = None,
             budgets: dict[str, Any] | None = None,
             claims: dict[str, Any] | None = None,
             explicit_p: bool = False) -> dict[str, Any]:
    try:
        check_manifest(mdoc)
    except Exception as exc:
        return {"allowed": False, "reason": "manifest_invalid", "executed": False,
                "detail": str(exc)[:200]}
    try:
        check_isolation(mdoc, isolation=isolation or {"base": "/tmp/mh132-iso"})
    except Exception as exc:
        return {"allowed": False, "reason": "isolation_unavailable", "executed": False,
                "detail": str(exc)[:200]}
    try:
        check_budgets(mdoc, budgets)
    except Exception as exc:
        return {"allowed": False, "reason": "budget_missing", "executed": False,
                "detail": str(exc)[:200]}
    if not claims or not explicit_p:
        reason = "no_safe_launch: claims_unavailable" if not claims else "no_safe_launch: explicit_p_required"
        return {"allowed": False, "reason": reason, "executed": False}
    try:
        n = len(expand_matrix(mdoc))
    except Exception as exc:
        return {"allowed": False, "reason": "manifest_invalid", "executed": False,
                "detail": str(exc)[:200]}
    return {"allowed": True, "n_trials": n, "executed": False}
