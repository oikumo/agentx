"""Reason SSOT — pure kernel (stdlib only, no I/O, no harness writes)."""


def evaluate_obs(ir):
    """Compute Aligned/Mismatched/Unresolved from HarnessObs rows.

    Returns dict with three lists + verdict per row. Pure, idempotent.
    """
    aligned, mismatched, unresolved = [], [], []
    for m in ir.get("models", []):
        if m.get("name") != "HarnessObs":
            continue
        for r in (m.get("tables") or {}).get("rows", []):
            d = r.get("d", "?")
            v = (r.get("verdict") or "").lower()
            if v == "aligned":
                aligned.append(d)
            elif v == "mismatched":
                mismatched.append(d)
            else:
                unresolved.append(d)
    return {"Aligned": aligned, "Mismatched": mismatched, "Unresolved": unresolved}


def check_preserves(ir):
    """Verify F preserves list present (structural check only)."""
    for mp in ir.get("mappings", []):
        if "preserves" not in mp:
            return False, f"mapping {mp.get('name','?')} missing preserves"
    return True, "preserves ok"


def concretize(abstract_row, bound=8, vocab=("recorded", "perm", "cover")):
    """Bounded concretize ( §3 output contract, normative core).

    abstract_row: dict like {"row": "d3", "options": [...], "distinguishing": [...] posts?
    For the pilot, options are derived from vocab product capped by bound.
    Returns (realizations, distinguishing_info) or (None, unknown) on over-bound.
    """
    try:
        b = int(bound)
    except (TypeError, ValueError):
        b = 8
    opts = abstract_row.get("options") if isinstance(abstract_row, dict) else None
    if opts is None:
        # Default d3-style fiber: recorded x perm x cover, capped.
        opts = [
            {"recorded": f"v{i}", "perm": p, "cover": c}
            for i, (p, c) in enumerate([("ro", "full"), ("ro", "partial"), ("rw", "full"), ("rw", "partial")])
        ]
    if len(opts) > b:
        return None, {"code": "unknown", "reason": "bound_exceeded",
                      "needed": f"bound {b} < {len(opts)} options; narrow vocab or raise bound",
                      "bound": b}
    # distinguishing_info ordered: recorded before perm/cover (d3 rule).
    distinguishing = ["recorded", "perm", "cover"]
    distinguishing = [d for d in distinguishing if d in vocab]
    return opts[:b], distinguishing
