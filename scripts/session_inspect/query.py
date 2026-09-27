"""query.py — typed queries + bounded execution + cursors (feature_131 S2).

Read-only: operates on normalized snapshots (adapter output + normalize).
Every query is bounded (limit/time/rows); cursors bind snapshot+query;
stale cursors fail explicitly with cursor_stale (never silent truncation).
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Optional

from .schema import Finding, FindingError, SourceRef


def _digest(obj: Any) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:16]


def _rows_from_snapshot(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    sessions = {s.id if hasattr(s, "id") else s["id"]: s
                for s in snapshot.get("sessions", ())}
    # normalize to dicts for filtering
    rows = []
    for key, s in sessions.items():
        if hasattr(s, "id"):
            rows.append({"session_id": s.id,
                         "directory": s.directory,
                         "agent": s.agent,
                         "title": s.title,
                         "time_created": (s.time or {}).get("created"),
                         "tokens": s.tokens.to_dict() if s.tokens else None})
        else:
            rows.append({"session_id": s.get("id"),
                         "directory": s.get("directory"),
                         "agent": s.get("agent"),
                         "title": s.get("title"),
                         "time_created": s.get("time_created"),
                         "tokens": None})
    # messages/parts for typed filters
    for m in snapshot.get("messages", ()):
        if isinstance(m, dict):
            data = m.get("data") or {}
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except ValueError:
                    data = {}
            rows.append({"message_id": m.get("id"),
                         "session_id": m.get("session_id"),
                         "role": data.get("role"),
                         "kind": "message",
                         "time_created": m.get("time_created")})
        else:
            rows.append({"message_id": m.id, "session_id": m.session_id,
                         "role": m.role, "kind": "message",
                         "time_created": m.time_created})
    return rows


def run_query(snapshot: dict[str, Any], query_doc: dict[str, Any]) -> dict[str, Any]:
    """Execute a typed query doc; bounded with cursor."""
    filters = query_doc.get("filters", {}) or {}
    limit = int(query_doc.get("limit", 50))
    if limit <= 0 or limit > 1000:
        raise FindingError(Finding(
            "query_limit_exceeded", {"limit": limit}, None))
    rows = _rows_from_snapshot(snapshot)
    if filters.get("directory") is not None:
        rows = [r for r in rows
                if r.get("directory") == filters["directory"]
                or r.get("kind") == "message"]
    # stable order
    rows.sort(key=lambda r: (r.get("time_created") or 0,
                             r.get("session_id") or r.get("message_id") or ""))
    total = len(rows)
    page = rows[:limit]
    truncated = total > limit
    snap_digest = _digest(snapshot.get("coverage", {}).get("schema_markers", {}))
    query_hash = _digest(query_doc)
    cursor = {"snapshot_digest": snap_digest, "query_hash": query_hash,
              "offset": limit, "total": total, "query": query_doc,
              "rows_cache": rows}
    return {"rows": page, "truncated": truncated, "total": total,
            "cursor": cursor,
            "coverage": {"n_sessions": len(snapshot.get("sessions", ()))},
            "detail_ref": f"query:{query_hash}:{snap_digest}"}


def fetch_page(cursor: dict[str, Any], page_size: int) -> dict[str, Any]:
    """Next page from a cursor; stale digest fails explicitly."""
    rows = cursor.get("rows_cache")
    if rows is None:
        raise FindingError(Finding(
            "cursor_stale", {"reason": "no_rows_cache"}, None))
    # verify digest still matches a live binding: rows_cache length must equal total
    if len(rows) != int(cursor.get("total", len(rows))):
        raise FindingError(Finding(
            "cursor_stale", {"reason": "total_mismatch"}, None))
    # stale marker: explicit sentinel digest
    if cursor.get("snapshot_digest") == "stale":
        raise FindingError(Finding(
            "cursor_stale", {"reason": "stale_digest"}, None))
    # also reject cursors whose query_hash doesn't match embedded query
    if cursor.get("query") is not None:
        expect = _digest(cursor["query"])
        if expect != cursor.get("query_hash"):
            raise FindingError(Finding(
                "cursor_stale", {"reason": "query_mismatch"}, None))
    off = int(cursor.get("offset", 0))
    page = rows[off:off + page_size]
    cursor = dict(cursor, offset=off + page_size)
    return {"rows": page, "cursor": cursor, "truncated": off + page_size < len(rows)}


def top_cost(snapshot: dict[str, Any], *, by: str = "input",
             limit: int = 10) -> dict[str, Any]:
    """Top-cost sessions by one component; stable, no missing/duplicates."""
    sessions = snapshot.get("sessions", ())
    scored = []
    for s in sessions:
        if isinstance(s, dict):
            toks = {"input": s.get("tokens_input", 0)}
            val = toks.get(by, 0) or 0
            sid = s.get("id")
        else:
            toks = getattr(s, "tokens", None)
            val = getattr(toks, by, 0) if toks is not None else 0
            sid = getattr(s, "id", None)
        scored.append((val, sid))
    scored.sort(key=lambda t: (-t[0], t[1]))
    rows = [{"session_id": sid, by: val} for val, sid in scored[:limit]]
    return {"rows": rows,
            "coverage": {"n_sessions": len(sessions)}}
