"""117 verify dispatch exploitation — pure batch composer + report join.

Stdlib-only, no net/ledger I/O. Splits two independent harness verify
batches (verification/integration lanes) for the O4 dispatch lane
(feature_114 `dispatch_runtime.plan_dispatch`) and joins wall/token
reports with the O6c bench transcript shape.

F7 lane-only held: at most two batches → two worker slots, two 0/1
lanes. `src/agentx/` untouched (no D1 revisit). No new places,
transitions, or ledger kinds — the caller feeds `compose_verify_claims`
into `plan_dispatch`; this module never mutates live state.
"""
from __future__ import annotations

__all__ = [
    "EMPTY_PLAN",
    "compose_verify_batches",
    "compose_verify_claims",
    "join_verify_reports",
]

EMPTY_PLAN = "empty_plan"


def compose_verify_batches(
    test_nodes: list[str] | tuple[str, ...],
) -> tuple[list[str], list[str]]:
    """Split verify nodes into two deterministic disjoint batches.

    Dedupe + sort code-point, then round-robin by sorted index
    (even → A/verification, odd → B/integration). Empty input refuses
    `empty_plan` (D19 — no invented work).
    """
    nodes = sorted({str(n) for n in (test_nodes or ()) if str(n)})
    if not nodes:
        raise ValueError(f"{EMPTY_PLAN}: no verify nodes — no invented work (D19)")
    batch_a = [n for i, n in enumerate(nodes) if i % 2 == 0]
    batch_b = [n for i, n in enumerate(nodes) if i % 2 == 1]
    return batch_a, batch_b


def compose_verify_claims(
    batch_a: list[str] | tuple[str, ...],
    batch_b: list[str] | tuple[str, ...],
    revision: int,
) -> tuple[list[dict[str, str]], dict[str, dict[str, int]]]:
    """Map batches to O4 claim dicts + probe capacity views.

    A → lane verification / task verify-a; B → lane integration /
    task verify-b. Returns (claims, capacities) where capacities holds
    the probe-style views the caller passes to `plan_dispatch`
    alongside the claims (worker_slots 0/2 free, each lane 0/1 free).
    Pure dict assembly — no plan validation here (planner owns refusals).
    """
    _ = revision  # threading parity: caller passes live rev R through.
    claims: list[dict[str, str]] = []
    if list(batch_a or ()):
        claims.append(
            {"claim": "c-verify-a", "task_id": "verify-a", "lane": "verification"}
        )
    if list(batch_b or ()):
        claims.append(
            {"claim": "c-verify-b", "task_id": "verify-b", "lane": "integration"}
        )
    capacities = {
        "worker_slots": {"used": 0, "cap": 2, "free": 2},
        "verification": {"used": 0, "cap": 1, "free": 1},
        "integration": {"used": 0, "cap": 1, "free": 1},
    }
    return claims, capacities


def join_verify_reports(a: dict, b: dict) -> dict:
    """Join two verify batch reports (pure, golden-pinned).

    Inputs: {wall, tokens, success} each (wall seconds float, tokens
    int, success bool). Output: {serial_wall, dispatch_wall,
    wall_saving, tokens_saving, success, green}.

    dispatch_wall = max(wall_a, wall_b) (parallel fan-out ≤2);
    serial_wall = wall_a + wall_b; wall_saving = 1 - dispatch/serial
    (0 when serial == 0). tokens_saving is 0.0 structural — parallelism
    runs the same work (d1–d3 evidence), pinned not asserted positive.
    """
    wall_a = max(0.0, float((a or {}).get("wall", 0.0) or 0.0))
    wall_b = max(0.0, float((b or {}).get("wall", 0.0) or 0.0))
    serial_wall = wall_a + wall_b
    dispatch_wall = max(wall_a, wall_b)
    wall_saving = (1.0 - dispatch_wall / serial_wall) if serial_wall > 0 else 0.0
    success = bool((a or {}).get("success", False)) and bool(
        (b or {}).get("success", False)
    )
    return {
        "serial_wall": serial_wall,
        "dispatch_wall": dispatch_wall,
        "wall_saving": wall_saving,
        "tokens_saving": 0.0,
        "success": success,
        "green": success,
    }
