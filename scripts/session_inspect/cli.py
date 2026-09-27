"""cli.py — local dev surface for M1–M3 (feature_131 S2).

Read-only inspection against a fixture/real DB; bounded output with
digest-bound detail_ref. Tier-2 plugin reuses the core (not this CLI).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SYS_ROOT = Path(__file__).resolve().parents[2]
if str(SYS_ROOT) not in sys.path:
    sys.path.insert(0, str(SYS_ROOT))

from session_inspect.adapter import OpenCodeSqliteAdapter, SessionSelector
from session_inspect.normalize import normalize_snapshot


def cmd_sessions(db: str, directory: str, limit: int = 20) -> dict:
    ad = OpenCodeSqliteAdapter(db)
    snap = ad.snapshot(SessionSelector(directory=directory))
    norm = normalize_snapshot(snap)
    rows = [{"session_id": s.id, "title": s.title, "agent": s.agent}
            for s in norm["sessions"][:limit]]
    return {"rows": rows, "total": len(norm["sessions"]),
            "detail_ref": f"sessions:{len(rows)}/{len(norm['sessions'])}"}


def cmd_trace(db: str, session_id: str) -> dict:
    """Timeline trace for one session (dev surface over trace.timeline)."""
    from session_inspect.trace import timeline
    ad = OpenCodeSqliteAdapter(db)
    snap = ad.snapshot(SessionSelector(session_ids=[session_id]))
    return timeline(snap, session_id)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="session_inspect")
    ap.add_argument("--db", required=True)
    ap.add_argument("--directory", default="/repo")
    ap.add_argument("--limit", type=int, default=20)
    args = ap.parse_args(argv)
    print(json.dumps(cmd_sessions(args.db, args.directory, args.limit),
                     indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
