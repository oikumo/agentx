"""adapter.py — read-only OpenCode SQLite source access (feature_131 §3).

Capture/evidence contract (design_001 §3, analysis_001 A5–A10):
- explicit source path only; `mode=ro` URI (never `immutable=1` on a live DB);
- one deferred read transaction per snapshot -> consistent main+WAL view (A10);
- capability discovery before extraction -> named `schema_unsupported` (A…);
- all ids retained; ties break by stable id, never invented causal order (A8);
- deletion coverage is unavailable in update-in-place storage -> reported (A6).
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional
from urllib.parse import quote

from .schema import Finding, FindingError, SourceRef

DEFAULT_DB_PATH = "~/.local/share/opencode/opencode.db"  # documented candidate

REQUIRED_TABLES: tuple[str, ...] = (
    "session", "message", "part", "event", "event_sequence",
    "__drizzle_migrations", "data_migration",
)
OPTIONAL_TABLES: tuple[str, ...] = (
    "session_input", "session_message", "project", "project_directory",
    "workspace", "todo", "migration",
)

_VAR_CHUNK = 900  # sqlite default max host parameters is 999


@dataclass
class SessionSelector:
    """Bounded selection over sessions (at least one bound is mandatory)."""

    directory: Optional[str] = None
    session_ids: Optional[list[str]] = None
    time_from_ms: Optional[int] = None
    time_to_ms: Optional[int] = None

    def is_bounded(self) -> bool:
        return any([
            self.directory is not None,
            bool(self.session_ids),
            self.time_from_ms is not None,
            self.time_to_ms is not None,
        ])


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table,)).fetchone()
    return row is not None


class OpenCodeSqliteAdapter:
    """Read-only adapter over one OpenCode session DB."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        if db_path is None:
            db_path = str(Path(DEFAULT_DB_PATH).expanduser())
        self.db_path = str(db_path)
        self._conn: Optional[sqlite3.Connection] = None

    # -- connection ---------------------------------------------------------
    def connect(self) -> sqlite3.Connection:
        """Open the source read-only. Errors raise FindingError(source_unreadable)."""
        if self._conn is not None:
            return self._conn
        path = Path(self.db_path)
        if not path.is_file():
            raise FindingError(Finding(
                "source_unreadable",
                {"path": self.db_path, "reason": "absent"},
                SourceRef(path=self.db_path)))
        try:
            conn = sqlite3.connect(
                f"file:{quote(str(path))}?mode=ro", uri=True, timeout=5.0)
        except sqlite3.Error as exc:
            raise FindingError(Finding(
                "source_unreadable",
                {"path": self.db_path, "reason": str(exc)},
                SourceRef(path=self.db_path))) from exc
        conn.row_factory = sqlite3.Row
        self._conn = conn
        return conn

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    # -- capability discovery -----------------------------------------------
    def capability_report(self) -> dict[str, Any]:
        """Schema markers + required-table check. Missing surface -> FindingError."""
        conn = self.connect()
        ref = SourceRef(path=self.db_path)
        required = {t: _table_exists(conn, t) for t in REQUIRED_TABLES}
        optional = {t: _table_exists(conn, t) for t in OPTIONAL_TABLES}
        missing = [t for t, ok in required.items() if not ok]
        if missing:
            raise FindingError(Finding(
                "schema_unsupported", {"missing": missing}, ref))
        markers: dict[str, Any] = {}
        try:
            markers["drizzle_count"] = conn.execute(
                "SELECT COUNT(*) FROM __drizzle_migrations").fetchone()[0]
            latest = conn.execute(
                "SELECT MAX(created_at) FROM __drizzle_migrations").fetchone()[0]
            markers["drizzle_latest_ms"] = int(latest) if latest is not None else 0
            markers["data_migrations"] = [r[0] for r in conn.execute(
                "SELECT name FROM data_migration ORDER BY name")]
        except sqlite3.Error as exc:
            raise FindingError(Finding(
                "schema_unsupported", {"reason": str(exc)}, ref)) from exc
        return {
            "ok": True,
            "required_tables": required,
            "optional_tables": optional,
            "schema_markers": markers,
            "db_path": self.db_path,
        }

    # -- snapshot ------------------------------------------------------------
    def snapshot(self, selector: SessionSelector) -> dict[str, Any]:
        """Consistent read-only snapshot of the bounded selection (one transaction)."""
        if not isinstance(selector, SessionSelector):
            raise TypeError("selector must be a SessionSelector")
        if not selector.is_bounded():
            raise ValueError("unbounded_selector")
        self.capability_report()  # schema gate before extraction
        conn = self.connect()
        where, args = self._selector_where(selector, col="s")
        subquery = f"SELECT s.id FROM session s WHERE {where}"
        try:
            conn.execute("BEGIN")  # one deferred transaction: consistent WAL view
            sessions = [dict(r) for r in conn.execute(
                f"SELECT s.* FROM session s WHERE {where} "
                "ORDER BY s.time_created, s.id", args)]
            messages = [dict(r) for r in conn.execute(
                f"SELECT m.* FROM message m WHERE m.session_id IN ({subquery}) "
                "ORDER BY m.time_created, m.id", args)]
            parts = [dict(r) for r in conn.execute(
                f"SELECT p.* FROM part p WHERE p.session_id IN ({subquery}) "
                "ORDER BY p.time_created, p.id", args)]
            events = [dict(r) for r in conn.execute(
                f"SELECT e.* FROM event e WHERE e.aggregate_id IN ({subquery}) "
                "ORDER BY e.aggregate_id, e.seq", args)]
        finally:
            conn.rollback()  # read-only: rollback ends the transaction cleanly
        markers = self.capability_report()["schema_markers"]
        coverage = {
            "n_sessions": len(sessions),
            "n_messages": len(messages),
            "n_parts": len(parts),
            "n_events": len(events),
            "schema_markers": markers,
            "warnings": ["deletion_coverage_unavailable"],  # A6: no tombstones
        }
        return {"sessions": sessions, "messages": messages, "parts": parts,
                "events": events, "coverage": coverage}

    @staticmethod
    def _selector_where(selector: SessionSelector, *, col: str) -> tuple[str, list]:
        clauses: list[str] = []
        args: list[Any] = []
        if selector.directory is not None:
            clauses.append(f"{col}.directory = ?")
            args.append(selector.directory)
        if selector.session_ids:
            ids = list(selector.session_ids)
            ors = []
            for i in range(0, len(ids), _VAR_CHUNK):
                chunk = ids[i:i + _VAR_CHUNK]
                ors.append(f"{col}.id IN ({','.join('?' * len(chunk))})")
                args.extend(chunk)
            clauses.append("(" + " OR ".join(ors) + ")")
        if selector.time_from_ms is not None:
            clauses.append(f"{col}.time_created >= ?")
            args.append(selector.time_from_ms)
        if selector.time_to_ms is not None:
            clauses.append(f"{col}.time_created <= ?")
            args.append(selector.time_to_ms)
        return " AND ".join(clauses), args

    # -- incremental cursor ---------------------------------------------------
    def event_cursor(self, session_id: str, after_seq: int = 0) -> list[dict[str, Any]]:
        """Rows with seq > after_seq for one session, ordered by seq (idempotent)."""
        conn = self.connect()
        return [dict(r) for r in conn.execute(
            "SELECT * FROM event WHERE aggregate_id = ? AND seq > ? "
            "ORDER BY seq", (session_id, after_seq))]
