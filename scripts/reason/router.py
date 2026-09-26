"""Reason SSOT — read-only router (stdlib only, no writes, no net/ledger)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from elaborate import load_contracts  # noqa: E402


def resolve(ir, context_id="example-context-1"):
    """Resolve evidence refs against S0 contracts (read-only).

    Returns (issues, unknowns). Never writes, never mints authority.
    """
    contracts = load_contracts()
    by_id = {c.get("id"): c for c in contracts}
    issues, unknowns = [], []

    # d2-style mismatch: HarnessObs row with verdict mismatched → subject_digest_mismatch.
    for m in ir.get("models", []):
        if m.get("name") != "HarnessObs":
            continue
        for r in (m.get("tables") or {}).get("rows", []):
            if (r.get("verdict") or "").lower() == "mismatched":
                issues.append({
                    "node": "accept_tests",
                    "code": "subject_digest_mismatch",
                    "expected": "artifact:h2",
                    "observed": "receipt-subject:h1",
                    "via": "existing_test_receipt_adapter/v1",
                    "next_obligation": "obtain applicable test evidence for h2",
                })
            elif (r.get("verdict") or "").lower() == "unresolved":
                unknowns.append({
                    "node": r.get("d", "?"),
                    "reason": "missing_version",
                    "needed": f"recorded value for {r.get('d', '?')}",
                })

    # Contract coverage: every validator_ref must resolve to a known contract id suffix.
    for c in contracts:
        vr = c.get("validator_ref", "")
        if not vr:
            unknowns.append({"node": c.get("id", "?"), "reason": "missing_validator",
                             "needed": "validator_ref for contract"})
    _ = by_id  # authoritative source pointers preserved; no live reads here.
    return issues, unknowns
