"""profile.py — usage hotspots + failure witnesses (feature_131 S3).

Read-only: operates on adapter snapshots (raw dict rows).
Hotspots rank message-incremental usage; failures surface error/retry
witnesses. Facts vs heuristic diagnoses stay separated.
"""
from __future__ import annotations

import json
from typing import Any


def _msg_tokens(msg: dict[str, Any]) -> dict[str, int]:
    data = msg.get("data") or {}
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except ValueError:
            data = {}
    toks = data.get("tokens") or {}
    cache = toks.get("cache") or {}
    return {
        "input": toks.get("input", 0) or 0,
        "output": toks.get("output", 0) or 0,
        "reasoning": toks.get("reasoning", 0) or 0,
        "cache_read": cache.get("read", 0) or 0,
        "cache_write": cache.get("write", 0) or 0,
    }


def hotspots(snapshot: dict[str, Any], *, by: str = "input",
             limit: int = 10) -> dict[str, Any]:
    """Top expensive messages by one usage component (message-incremental basis)."""
    messages = snapshot.get("messages", ())
    scored = []
    for m in messages:
        if isinstance(m, dict):
            mid = m.get("id")
            sid = m.get("session_id")
            toks = _msg_tokens(m)
            # user messages carry no tokens — skip zero-usage rows for hotspot ranking
            if sum(toks.values()) == 0:
                continue
            val = toks.get(by, 0) or 0
        else:
            mid = getattr(m, "id", None)
            sid = getattr(m, "session_id", None)
            tc = getattr(m, "tokens", None)
            if tc is None:
                continue
            val = getattr(tc, by, 0) or 0
        scored.append((val, mid, sid))
    scored.sort(key=lambda t: (-t[0], t[1] or ""))
    rows = [{"message_id": mid, "session_id": sid, by: val}
            for val, mid, sid in scored[:limit]]
    return {"rows": rows,
            "coverage": {"n_messages": len(messages),
                         "n_scored": len(scored),
                         "basis": "message_incremental"}}


def _part_tool_info(part: dict[str, Any]) -> tuple[str | None, str | None]:
    data = part.get("data") or {}
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except ValueError:
            data = {}
    if data.get("type") != "tool":
        return None, None
    tool = data.get("tool")
    state = data.get("state") or {}
    return tool, state.get("status")


def failures(snapshot: dict[str, Any], *,
             min_repeats: int = 2) -> dict[str, Any]:
    """Error/retry witnesses over tool parts (observed facts, not diagnoses).

    Groups error-status tool parts by tool name; tools with error counts
    >= min_repeats produce a repeat-error finding (heuristic retry-loop
    signal, labeled as such). Every finding carries witness part ids.
    """
    parts = snapshot.get("parts", ())
    errors: dict[str, list[str]] = {}
    n_error = 0
    for p in parts:
        if not isinstance(p, dict):
            continue
        tool, status = _part_tool_info(p)
        if status != "error" or tool is None:
            continue
        n_error += 1
        pid = p.get("id") or ""
        errors.setdefault(tool, []).append(pid)
    findings = []
    for tool, witnesses in sorted(errors.items()):
        if len(witnesses) >= min_repeats:
            findings.append({
                "kind": "repeat_tool_error",
                "tool": tool,
                "count": len(witnesses),
                "witnesses": witnesses,
                "diagnosis": "heuristic: repeated error-status calls "
                             "suggest a retry loop; confirm via trace",
            })
    return {"findings": findings,
            "coverage": {"n_error_parts": n_error,
                         "n_tools_with_errors": len(errors)}}
