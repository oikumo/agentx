"""O3 identity-aware pool — derived handles (feature_112).

Stdlib-only, no net/ledger I/O. Maps O1 stable menu IDs to logical task_ids
and left-joins against sidecar task_bindings for a read-only holder view.
Overlay file stays derived (P10) — this is a probe-time view only.
"""
from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "Handle",
    "menu_id_to_task_id",
    "handles_for_menu",
    "describe_handles",
]


@dataclass(frozen=True)
class Handle:
    menu_id: str
    task_id: str
    place: str
    owner: str
    generation: int


def menu_id_to_task_id(menu_id: str) -> str:
    """Map O1 menu ID to logical task_id (pure, stable)."""
    if menu_id.startswith("proj:"):
        slug = menu_id[len("proj:"):]
        if not slug:
            raise ValueError(f"unknown_id:{menu_id}")
        return f"proj-{slug}"
    if menu_id.startswith("drift:"):
        rest = menu_id[len("drift:"):]
        # drift:<class>:<key> -> drift-<class>-<key> (key may contain colons/_)
        if ":" not in rest or not rest.strip(":"):
            raise ValueError(f"unknown_id:{menu_id}")
        cls, _, key = rest.partition(":")
        if not cls or not key:
            raise ValueError(f"unknown_id:{menu_id}")
        safe_key = key.replace(":", "-")
        return f"drift-{cls}-{safe_key}"
    if menu_id.startswith("unscoped:"):
        num = menu_id[len("unscoped:"):]
        if not num.isdigit():
            raise ValueError(f"unknown_id:{menu_id}")
        return f"unscoped-{num}"
    if menu_id.startswith("pool:"):
        trans = menu_id[len("pool:"):]
        if not trans:
            raise ValueError(f"unknown_id:{menu_id}")
        return trans
    raise ValueError(f"unknown_id:{menu_id}")


def handles_for_menu(
    menu_ids: list[str] | tuple[str, ...],
    bindings: list[dict] | tuple[dict, ...] | None = None,
) -> list[Handle]:
    """Left-join O1 menu IDs against task_bindings (pure)."""
    by_id: dict[str, dict] = {}
    for b in bindings or []:
        if isinstance(b, dict) and b.get("id"):
            by_id[str(b.get("id"))] = b
    out: list[Handle] = []
    for mid in menu_ids:
        tid = menu_id_to_task_id(mid)
        b = by_id.get(tid)
        if b is None:
            out.append(Handle(menu_id=mid, task_id=tid, place="pending", owner="none", generation=0))
        else:
            out.append(
                Handle(
                    menu_id=mid,
                    task_id=tid,
                    place=str(b.get("place", "pending")),
                    owner=str(b.get("owner", "none") or "none"),
                    generation=int(b.get("generation", 0) or 0),
                )
            )
    # Deterministic D19-ish: sorted by menu_id for stable render.
    return sorted(out, key=lambda h: h.menu_id)


def describe_handles(handles: list[Handle] | tuple[Handle, ...]) -> str:
    """One-line summary for menu Resources tail / ledger reasoning."""
    total = len(handles)
    claimed = sum(1 for h in handles if h.place == "work_active")
    free = sum(1 for h in handles if h.place == "pending")
    return f"claims {claimed}/{total}, free {free}"
