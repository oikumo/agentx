"""trace.py — timeline from event seq (feature_131 S2) with bounded paging (feature_137).

Interleave messages/reasoning/tool/result/error/retry/compaction/model-switch
by recorded causal order (event seq); timestamp ties break by stable id,
never invented causality (A8).

Paging contract (mirrors detail.get_part): the default page is bounded
(~<=2KB JSON on real sessions; DEFAULT_PAGE_SIZE entries per list) so a bare
`trace` call can no longer dump ~100KB/350-entry skeletons (mh15 F3 evidence:
349/391/332-entry skeletons, 92-111KB per session). Totals, `truncated`, stable
(snapshot-order) paging and a digest-bound `detail_ref` keep every entry
retrievable and replay-stable; overflow is never silently truncated.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

DEFAULT_PAGE_SIZE = 10


def _digest(obj: Any) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:16]


def timeline(snapshot: dict[str, Any], session_id: str, *,
             page: int = 0, page_size: int = DEFAULT_PAGE_SIZE) -> dict[str, Any]:
    """Reconstruct the session timeline from the event stream + parts.

    Paged over snapshot order (adapter emits ORDER BY time_created, id, so
    pages are stable for a fixed snapshot). `page`/`page_size` mirror
    detail.get_part; non-positive page clamps to 0, non-positive page_size
    falls back to DEFAULT_PAGE_SIZE. `detail_ref` binds session + page/pages
    + content digest, so replays and cross-page drift are detectable.
    """
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
    # message/part skeleton in snapshot (time_created, id) order
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
    pg = max(0, int(page))
    ps = int(page_size) if int(page_size) > 0 else DEFAULT_PAGE_SIZE
    start, stop = pg * ps, (pg + 1) * ps
    total_e, total_s = len(out), len(skeleton)
    pages = max((total_e + ps - 1) // ps, (total_s + ps - 1) // ps, 1)
    digest = _digest({"session": session_id,
                      "events": [e.get("id") for e in out],
                      "skeleton": [(s.get("kind"), s.get("id"))
                                   for s in skeleton]})
    return {"session_id": session_id,
            "events": out[start:stop], "skeleton": skeleton[start:stop],
            "page": pg, "page_size": ps,
            "truncated": stop < total_e or stop < total_s,
            "coverage": {"n_events": total_e,
                         "n_messages_parts": total_s,
                         "pages": pages},
            "detail_ref": f"trace:{session_id}:p{pg}/{pages}:{digest}"}
