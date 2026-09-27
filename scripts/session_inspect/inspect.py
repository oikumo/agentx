"""inspect.py — deep drill-down with addressable pages (feature_131 S2).

Retrieve exact session/message/part/call with full selected content.
Large bodies return pages + total_chars; overflow never silently truncated.
"""
from __future__ import annotations

from typing import Any


def _parts(snapshot: dict[str, Any]) -> list[Any]:
    return list(snapshot.get("parts", ()))


def get_part(snapshot: dict[str, Any], part_id: str, *,
             page: int = 0, page_size: int = 2000) -> dict[str, Any]:
    """One part with paged text content."""
    for p in _parts(snapshot):
        pid = p.id if hasattr(p, "id") else p.get("id")
        if pid != part_id:
            continue
        payload = p.payload if hasattr(p, "payload") else {}
        if isinstance(p, dict):
            import json as _j
            data = p.get("data") or {}
            if isinstance(data, str):
                try:
                    data = _j.loads(data)
                except ValueError:
                    data = {}
            payload = {k: v for k, v in data.items() if k != "type"}
            ptype = data.get("type")
            mid = p.get("message_id")
            sid = p.get("session_id")
        else:
            ptype = p.type
            mid = p.message_id
            sid = p.session_id
        text = payload.get("text") if isinstance(payload.get("text"), str) else None
        if text is None:
            return {"part_id": pid, "type": ptype, "message_id": mid,
                    "session_id": sid, "payload": payload,
                    "truncated": False}
        total = len(text)
        chunk = text[page * page_size:(page + 1) * page_size]
        return {"part_id": pid, "type": ptype, "message_id": mid,
                "session_id": sid, "text": chunk, "page": page,
                "page_size": page_size, "total_chars": total,
                "truncated": total > (page + 1) * page_size}
    raise KeyError(f"part_not_found:{part_id}")


def get_session(snapshot: dict[str, Any], session_id: str) -> dict[str, Any]:
    """Exact session record with source IDs."""
    for s in snapshot.get("sessions", ()):
        sid = s.id if hasattr(s, "id") else s.get("id")
        if sid == session_id:
            if hasattr(s, "id"):
                return {"session_id": s.id, "directory": s.directory,
                        "title": s.title, "agent": s.agent,
                        "parent_id": s.parent_id,
                        "time": dict(s.time),
                        "tokens": s.tokens.to_dict() if s.tokens else None}
            return dict(s)
    raise KeyError(f"session_not_found:{session_id}")
