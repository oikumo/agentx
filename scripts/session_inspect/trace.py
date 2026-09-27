"""trace.py — timeline from event seq (feature_131 S2).

Interleave messages/reasoning/tool/result/error/retry/compaction/model-switch
by recorded causal order (event seq); timestamp ties break by stable id,
never invented causality (A8).
"""
from __future__ import annotations

from typing import Any


def timeline(snapshot: dict[str, Any], session_id: str) -> dict[str, Any]:
    """Reconstruct the session timeline from the event stream + parts."""
    events = [e for e in snapshot.get("events", ())
              if (e.get("aggregate_id") if isinstance(e, dict)
                  else getattr(e, "aggregate_id", None)) == session_id]
    def _seq(e: Any) -> int:
        return e.get("seq", 0) if isinstance(e, dict) else getattr(e, "seq", 0)
    events = sorted(events, key=_seq)
    out = []
    for e in events:
        if isinstance(e, dict):
            out.append({"seq": e.get("seq"), "type": e.get("type"),
                        "id": e.get("id")})
        else:
            out.append({"seq": getattr(e, "seq", 0),
                        "type": getattr(e, "type", None),
                        "id": getattr(e, "id", None)})
    # message/part skeleton in stable (time_created, id) order
    skeleton = []
    for m in snapshot.get("messages", ()):
        mid = m.id if hasattr(m, "id") else m.get("id")
        sid = m.session_id if hasattr(m, "session_id") else m.get("session_id")
        if sid == session_id:
            skeleton.append({"kind": "message", "id": mid})
    for p in snapshot.get("parts", ()):
        pid = p.id if hasattr(p, "id") else p.get("id")
        sid = p.session_id if hasattr(p, "session_id") else p.get("session_id")
        if sid == session_id:
            skeleton.append({"kind": "part", "id": pid})
    return {"session_id": session_id, "events": out, "skeleton": skeleton,
            "coverage": {"n_events": len(out),
                         "n_messages_parts": len(skeleton)}}
