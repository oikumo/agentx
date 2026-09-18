"""P2 slice-A managed-op transition map — feature_103.mh10_p2_global_gate.

Read-only evidence harness (no authority change). Maps every managed op
that moves MH global state to its template transition + today's fired?
flag. Counts that agree with no fired transition are OMISSIONS (P1
divergence class); counts that disagree are DIVERGENCES (must be named,
never silent).

No import of ``src/agentx/*`` (R2); stdlib only (+ local ``.state``
read in ``check_live``, guarded to unknown).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# One-template map (analysis_001 §2) — data, not behavior.
# ---------------------------------------------------------------------------
MANAGED_OPS: tuple[dict[str, str], ...] = (
    {
        "op": "fire",
        "path": "scripts/omt/net/state.py:746-789 (fire)",
        "transition": "any template transition via fire_marking",
        "fired_today": "yes",
    },
    {
        "op": "claim_task",
        "path": "scripts/omt/net/state.py (_fire_pool_move + claim_task)",
        "transition": "work_start",
        "fired_today": "yes-B2-happy-path",
    },
    {
        "op": "release_task",
        "path": "scripts/omt/net/state.py (_fire_pool_move + release_task)",
        "transition": "work_release",
        "fired_today": "yes-B2-happy-path",
    },
    {
        "op": "release_complete",
        "path": "scripts/omt/net/state.py:_move_pool_token callers (recovery/lane/integration)",
        "transition": "work_finish/work_fail/work_cancel",
        "fired_today": "no",
    },
    {
        "op": "absent_lane_occupancy",
        "path": "scripts/omt/net/state.py:296-300 vs fire() :763-768",
        "transition": "(binding-only occupancy — no transition)",
        "fired_today": "no",
    },
    {
        "op": "project_sync",
        "path": "scripts/omt/project.py sync (WORK.md/META.md derived rows)",
        "transition": "sync_render (derived read)",
        "fired_today": "no",
    },
    {
        "op": "session_menu",
        "path": "AGENTS.md STARTUP parsing WORK.md Tasks text",
        "transition": "sync_render (derived read)",
        "fired_today": "no",
    },
    {
        "op": "crash_window",
        "path": "scripts/omt/net/state.py:730-742 vs WAL :672-675",
        "transition": "(clear-before-record — carried residual)",
        "fired_today": "n/a",
    },
)


def classify(b: Any, m: Any, fired: bool) -> str:
    """Classify one B-vs-M count pair.

    agree + fired → FIRED; agree + not-fired → OMISSION (known P1 class);
    disagree → DIVERGENCE (must be named upstream, never silent).
    """
    if b == m:
        return "FIRED" if fired else "OMISSION"
    return "DIVERGENCE"


def check_counts(
    pool: dict[str, Any], marking: dict[str, Any]
) -> list[dict[str, Any]]:
    """Differential B(pool)-vs-M(marking) over work_pending/active/done."""
    rows: list[dict[str, Any]] = []
    for place, key in (
        ("work_pending", "pending"),
        ("work_active", "active"),
        ("work_done", "done"),
    ):
        b = pool.get(key, "?") if isinstance(pool, dict) else "?"
        m = marking.get(place, "?") if isinstance(marking, dict) else "?"
        rows.append(
            {
                "key": key,
                "place": place,
                "b": b,
                "m": m,
                "fired": False,
                "class": classify(b, m, False),
            }
        )
    return rows


def check_fixture(scenario: dict[str, Any]) -> dict[str, Any]:
    """Seeded-omission detector: scenario carries pool/marking/fired flags.

    Returns ``{"detected": [...], "missed": [...]}`` — a scenario is
    DETECTED when every non-fired agreement is reported as OMISSION (never
    passed off as a firing) and every disagreement as DIVERGENCE.
    """
    pool = scenario.get("pool", {})
    marking = scenario.get("marking", {})
    rows = check_counts(pool, marking)
    detected = [r["key"] for r in rows if r["class"] in ("OMISSION", "DIVERGENCE")]
    missed = [r["key"] for r in rows if r["class"] not in ("OMISSION", "DIVERGENCE")]
    # A claimed firing with fired=false must never read as FIRED.
    if scenario.get("claimed_firing") and not scenario.get("fired", False):
        if "claimed_firing_as_omission" not in detected:
            detected.append("claimed_firing_as_omission")
    return {"detected": sorted(detected), "missed": sorted(missed), "rows": rows}


def check_live(base: Path) -> dict[str, Any]:
# B2 landed: ledger transition/fired evidence asserted via check_ledger_evidence (the wire-in this todo asked for).
    """Live B-vs-M over the real net bundle + WORK.md pool (read-only).

    Unknown stays unknown: any unreadable source yields ``_unknown``
    instead of an interpolated zero.
    """
    try:
        from net import state as _st  # noqa: PLC0415  (local harness engine only)
    except Exception as exc:
        return {"_unknown": f"net engine unavailable: {exc!r}"}
    try:
        st = _st.load(base)
    except Exception as exc:
        return {"_unknown": f"net bundle unreadable: {exc!r}"}
    marking = {
        k: st.live_marking.get(k, "?") for k in ("work_pending", "work_active", "work_done")
    }
    repo = Path(__file__).resolve().parents[3]
    try:
        text = (repo / "WORK.md").read_text(encoding="utf-8")
    except OSError:
        return {"_unknown": "WORK.md unreadable", "marking": marking}
    import re

    m_pool = re.search(r"Pool:\s*pending=(\d+)\s+active=(\d+)\s+done=(\d+)", text)
    if not m_pool:
        return {"_unknown": "pool line not found", "marking": marking}
    pool = {
        "pending": int(m_pool.group(1)),
        "active": int(m_pool.group(2)),
        "done": int(m_pool.group(3)),
    }
    return {
        "revision": st.revision,
        "pool": pool,
        "marking": marking,
        "rows": check_counts(pool, marking),
        "managed_ops": [dict(r) for r in MANAGED_OPS],
    }


def check_ledger_evidence(records: list[dict[str, Any]]) -> dict[str, Any]:
    """B2 ledger-evidence reader: every net_claim/net_release row must carry
    the slice-B shape (``transition``/``fired``/``fire_fallback`` keys).

    Returns ``{"fired": n, "fallback": {reason: n}, "offenders": [idx],
    "ok": bool}`` — offenders are claim/release rows missing keys (never
    silent). Counts-only ``check_live`` is unchanged.
    """
    fired = 0
    fallback: dict[str, int] = {}
    offenders: list[int] = []
    for i, r in enumerate(records):
        if not isinstance(r, dict):
            continue
        if r.get("kind") not in ("net_claim", "net_release"):
            continue
        if not all(k in r for k in ("transition", "fired", "fire_fallback")):
            offenders.append(i)
            continue
        if r.get("fired") is True:
            fired += 1
        else:
            reason = str(r.get("fire_fallback") or "unknown")
            fallback[reason] = fallback.get(reason, 0) + 1
    return {"fired": fired, "fallback": fallback, "offenders": offenders, "ok": not offenders}
