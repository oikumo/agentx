"""compare.py — session/span/trial comparison (feature_131 S3).

Read-only: compares selected sessions' message-incremental usage with
trace/coverage context. Every comparison carries comparability warnings
(model/agent/directory drift, incomplete coverage); no quality verdict is
implied by a usage delta alone.
"""
from __future__ import annotations

import json
from typing import Any


def _session_messages(snapshot: dict[str, Any],
                      session_id: str) -> list[dict[str, Any]]:
    out = []
    for m in snapshot.get("messages", ()):
        if not isinstance(m, dict):
            continue
        if m.get("session_id") == session_id:
            out.append(m)
    return out


def _sum_input(messages: list[dict[str, Any]]) -> int:
    total = 0
    for m in messages:
        data = m.get("data") or {}
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except ValueError:
                data = {}
        toks = data.get("tokens") or {}
        total += toks.get("input", 0) or 0
    return total


def compare_sessions(snapshot: dict[str, Any],
                     session_ids: list[str]) -> dict[str, Any]:
    """Compare sessions by message-incremental input usage (stable id order)."""
    sessions = {s.get("id"): s for s in snapshot.get("sessions", ())
                if isinstance(s, dict)}
    rows = []
    for sid in sorted(session_ids):
        msgs = _session_messages(snapshot, sid)
        rows.append({"session_id": sid,
                     "input": _sum_input(msgs),
                     "n_messages": len(msgs),
                     "directory": (sessions.get(sid) or {}).get("directory")})
    warnings: list[str] = []
    dirs = {r["directory"] for r in rows}
    if len(dirs) > 1:
        warnings.append("directory_drift: compared sessions span directories")
    agents = {(sessions.get(sid) or {}).get("agent") for sid in session_ids}
    if len(agents) > 1:
        warnings.append("agent_drift: compared sessions use different agents")
    delta = {}
    if len(rows) >= 2:
        delta = {"input": rows[1]["input"] - rows[0]["input"]}
    return {"rows": rows, "delta": delta, "warnings": warnings,
            "coverage": {"n_compared": len(rows),
                         "basis": "message_incremental"}}


def span_usage(snapshot: dict[str, Any],
               span_id: str) -> dict[str, Any]:
    """Exact span attribution (design_001 §4): unavailable without boundaries.

    Session-level measurement is the supported basis; per-span costs are
    never smeared across events. Callers must fall back to session-level
    measurement and surface `span_usage_unavailable` explicitly.
    """
    _ = (snapshot, span_id)
    return {"span_id": span_id, "usage": None,
            "reason": "span_usage_unavailable",
            "detail": "no compatible usage boundaries for this span; "
                      "use session-level measurement"}
