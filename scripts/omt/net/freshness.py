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
