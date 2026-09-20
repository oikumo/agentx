"""O4 concurrent dispatch runtime — pure plan composer (feature_114).

Stdlib-only, no net/ledger I/O. `plan_dispatch` composes a deterministic,
ordered dispatch plan over O3 resolved claims + probe-time capacities
(worker_slots=2, verification/integration lanes 0/1, WIP pool places
cap 15); the caller (`state.dispatch_claims`) validates the plan at the
live revision and commits claims + join as ONE atomic transaction.

F7-revoked-lane (design_001 §1, locked 2026-09-19): fan-out ≤2 concurrent
worktrees/sub-agents under worker_slots=2 + lane leases; `src/` edit
serialism unchanged. No invented work (D19): empty claims + empty
enabled[] refuses `empty_plan`. Refuse codes are stable strings raised
pre-write via `PlanRefused`; `stale_revision` is the caller's gate
(`_require_revision` inside the held lock — planner takes R as given).
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass

__all__ = [
    "PlanRefused",
    "Plan",
    "Task",
    "LANES",
    "WIP_CAP",
    "WORKER_SLOTS_CAP",
    "plan_dispatch",
    "describe_plan",
    "plan_to_dict",
]

LANES = ("verification", "integration", "general")
WIP_CAP = 15  # feature_048 D20: pool places bound (MAX_PLACES)
WORKER_SLOTS_CAP = 2  # feature_082: one-machine worker capacity
_LANE_CAP = 1  # feature_083: verification/integration lanes are 0/1


class PlanRefused(ValueError):
    """Stable-code dispatch refusal (code + human detail)."""

    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(f"{code}{(': ' + detail) if detail else ''}")
        self.code = code
        self.detail = detail


@dataclass(frozen=True)
class Task:
    claim: str
    task_id: str
    lane: str
    worktree: str
    lease: str


@dataclass(frozen=True)
class Plan:
    tasks: tuple[Task, ...]
    wip: dict[str, int]
    revision: int
    batch_id: str


def _free(cap_view: object, default_cap: int) -> int:
    """Free capacity from a probe-style {used, cap, free} dict (pure).

    Malformed views fail closed to 0 — the planner refuses rather than
    overbook a lane it cannot read.
    """
    if not isinstance(cap_view, dict):
        return 0
    try:
        free = cap_view.get("free")
        if free is not None:
            return max(0, int(free))
        return max(0, int(cap_view.get("cap", default_cap)) - int(cap_view.get("used", 0)))
    except (TypeError, ValueError):
        return 0


def _batch_id(revision: int, task_ids: list[str]) -> str:
    """Deterministic batch id: sha1(revision | sorted task_ids)[:12].

    Pure-deterministic so identical inputs compose identical plans
    (golden-pinned); within one revision pending bindings are unique, so
    batch ids never collide across live commits, and command_id replays
    re-derive the SAME id (idempotent replay stays auditable).
    """
    h = hashlib.sha1(
        "|".join([str(int(revision)), *sorted(task_ids)]).encode("utf-8")
    )
    return h.hexdigest()[:12]


def plan_dispatch(
    *,
    claims: list[dict] | tuple[dict, ...],
    enabled: list[str] | tuple[str, ...],
    parallel: list[str] | tuple[str, ...],
    worker_slots: dict,
    verification: dict,
    integration: dict,
    work_pending: int,
    work_active: int,
    revision: int,
) -> Plan:
    """Compose the ordered dispatch plan (pure, deterministic, stdlib-only).

    Inputs come from the caller at live rev R: O3 resolved claim dicts
    `{claim, task_id, lane?}` + probe capacity views + pool counts.
    Ordering: verification-lane claims, integration-lane claims, then
    general by task_id code-point. Every claim takes one worker slot
    while active (claim_model), so the whole batch is worker-bounded.

    Refuses (stable codes, pre-write): `unknown_claim:{id}` |
    `dup_claim:{id}` | `empty_plan` | `worker_capacity_exhausted` |
    `verification_lane_busy` | `integration_lane_busy` |
    `wip_cap_exceeded`. `parallel` is the probe offer echo (additive
    audit input; the dispatch lane is claims-driven, never invented).
    """
    norm: list[dict[str, str]] = []
    seen: set[str] = set()
    for i, c in enumerate(claims or ()):
        if not isinstance(c, dict):
            raise PlanRefused(f"unknown_claim:{i}", "claim entry must be an object")
        claim = str(c.get("claim", "") or "")
        task_id = str(c.get("task_id", "") or "")
        if not claim or not task_id:
            raise PlanRefused(f"unknown_claim:{claim or i}", "claim needs claim+task_id")
        if task_id in seen:
            raise PlanRefused(f"dup_claim:{task_id}", "duplicate claim in batch")
        seen.add(task_id)
        lane = str(c.get("lane", "") or "")
        if lane not in LANES:
            lane = "general"
        norm.append({"claim": claim, "task_id": task_id, "lane": lane})
    if not norm and not (enabled or ()):
        raise PlanRefused(
            "empty_plan", "no claims and enabled[] empty — no invented work (D19)"
        )
    workers_free = _free(worker_slots, WORKER_SLOTS_CAP)
    if len(norm) > workers_free:
        raise PlanRefused(
            "worker_capacity_exhausted",
            f"{len(norm)} claims > {workers_free} free workers — "
            "re-render (sync net_to_md) for a fresh menu",
        )
    lane_free = {
        "verification": _free(verification, _LANE_CAP),
        "integration": _free(integration, _LANE_CAP),
    }
    lane_counts = {
        "verification": sum(1 for t in norm if t["lane"] == "verification"),
        "integration": sum(1 for t in norm if t["lane"] == "integration"),
    }
    if lane_counts["verification"] > lane_free["verification"]:
        raise PlanRefused(
            "verification_lane_busy",
            f"{lane_counts['verification']} verification claims > "
            f"{lane_free['verification']} free test slots",
        )
    if lane_counts["integration"] > lane_free["integration"]:
        raise PlanRefused(
            "integration_lane_busy",
            f"{lane_counts['integration']} integration claims > "
            f"{lane_free['integration']} free integration slots",
        )
    pending = int(work_pending or 0)
    active = int(work_active or 0)
    if pending + active + len(norm) > WIP_CAP:
        raise PlanRefused(
            "wip_cap_exceeded",
            f"pending {pending} + active {active} + batch {len(norm)} > "
            f"{WIP_CAP} pool places",
        )
    order = {"verification": 0, "integration": 1, "general": 2}
    ordered = sorted(norm, key=lambda t: (order[t["lane"]], t["task_id"]))
    batch_id = _batch_id(revision, [t["task_id"] for t in ordered])
    tasks = tuple(
        Task(
            claim=t["claim"],
            task_id=t["task_id"],
            lane=t["lane"],
            worktree=f"wt-{batch_id[:6]}-{t['task_id']}",
            lease=f"lease-{batch_id}-{n:02d}",
        )
        for n, t in enumerate(ordered)
    )
    return Plan(
        tasks=tasks,
        wip={"pending": pending, "active": active, "cap": WIP_CAP},
        revision=int(revision or 0),
        batch_id=batch_id,
    )


def describe_plan(plan: Plan) -> str:
    """One-line summary for the approval gate + ledger `reasoning`."""
    v = sum(1 for t in plan.tasks if t.lane == "verification")
    i = sum(1 for t in plan.tasks if t.lane == "integration")
    g = len(plan.tasks) - v - i
    return (
        f"dispatch {len(plan.tasks)} tasks rev {plan.revision} "
        f"batch {plan.batch_id} lanes {v}/{i}/{g}"
    )


def plan_to_dict(plan: Plan) -> dict:
    """JSON-shaped view of a Plan (CLI / report / ledger carrier)."""
    return {
        "tasks": [
            {
                "claim": t.claim,
                "task_id": t.task_id,
                "lane": t.lane,
                "worktree": t.worktree,
                "lease": t.lease,
            }
            for t in plan.tasks
        ],
        "wip": dict(plan.wip),
        "revision": plan.revision,
        "batch_id": plan.batch_id,
        "summary": describe_plan(plan),
    }
