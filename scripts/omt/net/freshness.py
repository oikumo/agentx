"""O5 live progress projection — freshness + push (feature_113).

Stdlib-only, no net/ledger I/O. Menu-time freshness check plus
re-render push record composer and minimal text projection.
"""
from __future__ import annotations

from typing import Any

__all__ = [
    "is_fresh",
    "freshness_hint",
    "push_record",
    "projection_lines",
    "batch_projection_lines",
]


def is_fresh(stamped_rev: int | None, live_rev: int | None) -> bool:
    """True iff stamped WORK.md rev equals live net rev."""
    if stamped_rev is None or live_rev is None:
        return False
    try:
        return int(stamped_rev) == int(live_rev)
    except (TypeError, ValueError):
        return False


def freshness_hint(stamped_rev: int | None, live_rev: int | None) -> str:
    """Stable stale-revision hint reusing _require_revision wording."""
    return (
        f"D19 stale menu: expected rev {stamped_rev} != live rev "
        f"{live_rev} — re-render (sync net_to_md) before presenting"
    )


def push_record(
    live_rev: int,
    menu: dict[str, Any] | None = None,
    rendered: str = "",
) -> dict[str, Any]:
    """Derived re-render push record (no new net kinds)."""
    return {
        "net_revision": int(live_rev),
        "menu": dict(menu or {}),
        "tasks_block": str(rendered),
    }


def projection_lines(
    live_rev: int,
    marking: dict[str, int] | None = None,
    enabled: list[str] | None = None,
    lanes: dict[str, Any] | None = None,
    claims_summary: str = "",
) -> list[str]:
    """Minimal read-only live view lines (pure, deterministic)."""
    mark = dict(marking or {})
    en = sorted(enabled or [])
    lines = [
        f"rev {int(live_rev)} | marking {mark} | enabled {en}",
    ]
    if lanes:
        ver = lanes.get("verification", {})
        integ = lanes.get("integration", {})
        parts = []
        if ver:
            parts.append(f"verification {ver.get('used', 0)}/{ver.get('total', 1)}")
        if integ:
            parts.append(f"integration {integ.get('used', 0)}/{integ.get('total', 1)}")
        if lanes.get("deadlocks_complete") is True:
            parts.append("deadlocks_complete")
        if parts:
            lines.append("lanes " + " ".join(parts))
    if claims_summary:
        lines.append(str(claims_summary))
    return lines


_LANE_ORDER = {"verification": 0, "integration": 1, "general": 2}


def batch_projection_lines(
    plan: dict[str, Any] | None,
    lanes: dict[str, Any] | None = None,
    conflicts: list[dict[str, Any]] | None = None,
) -> list[str]:
    """O5b join/batch progress view (pure, deterministic, read-only).

    Input is the `dispatch_runtime.plan_to_dict` shape
    (`{tasks:[{claim,task_id,lane,worktree,lease}], wip:{pending,active,cap},
    revision, batch_id, summary}`). Renders one batch line plus one line
    per task in planner order (verification, integration, general by
    `task_id` code-point) plus an optional deadlocks/blocked tail.
    Malformed/empty plans render `[]` (fail-open — never break probe).
    """
    try:
        p: dict[str, Any] = plan if isinstance(plan, dict) else {}
        tasks = p.get("tasks") or []
        if not isinstance(tasks, list) or not tasks:
            return []
        norm: list[dict[str, str]] = []
        for t in tasks:
            if not isinstance(t, dict):
                return []
            task_id = str(t.get("task_id", "") or "")
            if not task_id:
                return []
            lane = str(t.get("lane", "") or "")
            if lane not in _LANE_ORDER:
                lane = "general"
            norm.append(
                {
                    "task_id": task_id,
                    "lane": lane,
                    "worktree": str(t.get("worktree", "") or ""),
                    "lease": str(t.get("lease", "") or ""),
                }
            )
        ordered = sorted(
            norm, key=lambda t: (_LANE_ORDER[t["lane"]], t["task_id"])
        )
        v = sum(1 for t in ordered if t["lane"] == "verification")
        i = sum(1 for t in ordered if t["lane"] == "integration")
        g = len(ordered) - v - i
        wip_raw = p.get("wip")
        wip: dict[str, Any] = wip_raw if isinstance(wip_raw, dict) else {}
        try:
            wip_part = (
                f"{int(wip.get('pending', 0))}/"
                f"{int(wip.get('active', 0))}/"
                f"{int(wip.get('cap', 15))}"
            )
        except (TypeError, ValueError):
            wip_part = "0/0/15"
        lines = [
            f"batch {p.get('batch_id', '?')} rev "
            f"{p.get('revision', '?')} lanes {v}/{i}/{g} "
            f"wip {wip_part}",
        ]
        for t in ordered:
            lines.append(
                f"task {t['task_id']} [{t['lane']}] "
                f"{t['worktree']} {t['lease']}".rstrip()
            )
        tail: list[str] = []
        if isinstance(lanes, dict) and lanes.get("deadlocks_complete") is True:
            tail.append("deadlocks_complete")
        blocked: list[str] = []
        for c in conflicts or []:
            if isinstance(c, dict):
                name = str(c.get("transition", c.get("subnet", "")) or "")
                if name:
                    blocked.append(name)
        if blocked:
            tail.append(f"blocked:{','.join(sorted(blocked))}")
        if tail:
            lines.append(" ".join(tail))
        return lines
    except Exception:
        return []
