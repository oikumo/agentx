"""Agent session database (stdlib ``sqlite3``).

Owns the connection and runs the idempotent DDL on first use.  All SQL lives
here and in :mod:`agentx.agent.persistence.schema_db` — never in controllers or
the Agent facade (MVC++: SQL only inside DP/persistence classes).
"""

from __future__ import annotations

import json
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agentx.agent.persistence.schema_db import ALL_TABLES, INDEXES, TableAgents, TableSessionSnapshots
from agentx.agent.types import SessionSnapshot


AGENT_DATABASE_FILENAME = "agent_session.db"

#: M14 (feature_015): maximum snapshots retained per agent.
_MAX_SNAPSHOTS_PER_AGENT: int = 50


class SessionDatabase:
    """SQLite-backed persistence (stdlib sqlite3; no ORM, no migrations).

    Mirrors the existing :class:`agentx.model.session.session_db.SessionDatabase`
    convention: schema is created idempotently via ``CREATE TABLE IF NOT EXISTS``
    on first connection.
    """

    def __init__(self, db_path: str) -> None:
        self.path = db_path
        self._ensure_schema()

    # ------------------------------------------------------------------ schema

    def _ensure_schema(self) -> None:
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as conn:
            # L14 (feature_015): enable FK enforcement.  Existing databases
            # created before this change won't have FK constraints in their
            # table definitions (CREATE TABLE IF NOT EXISTS is a no-op), but
            # new databases will if the schema is updated.  Enabling the PRAGMA
            # is safe — it's a no-op on tables without FK declarations.
            conn.execute("PRAGMA foreign_keys = ON")
            for table in ALL_TABLES:
                conn.execute(table.TABLE_QUERY)
            # L13 (feature_015): create indexes for agent_id lookups.
            for index_sql in INDEXES:
                conn.execute(index_sql)
            conn.commit()

    # ------------------------------------------------------------------ agents

    def upsert_agent(
        self,
        agent_id: str,
        name: str,
        version: int,
        autonomy_level: str,
        config_json: str,
    ) -> bool:
        with sqlite3.connect(self.path) as conn:
            # L11 (feature_015): use INSERT OR IGNORE + UPDATE so created_at
            # is preserved on re-save (previously INSERT OR REPLACE overwrote it).
            conn.execute(
                TableAgents.INSERT_OR_IGNORE,
                (agent_id, name, version, autonomy_level, config_json, _now_iso()),
            )
            conn.execute(
                TableAgents.UPDATE,
                (name, version, autonomy_level, config_json, agent_id),
            )
            conn.commit()
        return True

    # ----------------------------------------------------------- snapshots CRUD

    def save_snapshot(self, snapshot: SessionSnapshot) -> bool:
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                TableSessionSnapshots.INSERT,
                (
                    snapshot.snapshot_id,
                    snapshot.agent_id,
                    _to_iso(snapshot.timestamp),
                    snapshot.config_version,
                    json.dumps(snapshot.volatility_data, default=_json_default),
                    json.dumps(snapshot.policy_store, default=_json_default),
                    json.dumps(snapshot.goal_tree, default=_json_default),
                    snapshot.reflection_log_position,
                ),
            )
            # M14 (feature_015): retain only the last N snapshots per agent.
            conn.execute(
                TableSessionSnapshots.DELETE_OLD_BY_AGENT,
                (snapshot.agent_id, snapshot.agent_id, _MAX_SNAPSHOTS_PER_AGENT),
            )
            conn.commit()
        return True

    def save_snapshot_with_retry(
        self, snapshot: SessionSnapshot, max_retries: int = 3
    ) -> bool:
        """Persist with bounded retry (design §11.2)."""
        for attempt in range(max_retries):
            try:
                return self.save_snapshot(snapshot)
            except sqlite3.OperationalError:
                # L12 (feature_015): only retry on OperationalError ("database
                # is locked"); other sqlite3.Errors (IntegrityError, etc.) are
                # not transient and should not be retried.
                if attempt == max_retries - 1:
                    return False
                time.sleep(1)
            except sqlite3.Error:
                return False
        return False

    def load_snapshot(self, snapshot_id: str) -> SessionSnapshot | None:
        with sqlite3.connect(self.path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                TableSessionSnapshots.SELECT_BY_ID, (snapshot_id,)
            ).fetchone()
        if row is None:
            return None
        return _row_to_snapshot(row)

    def load_latest_snapshot(self, agent_id: str) -> SessionSnapshot | None:
        with sqlite3.connect(self.path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                TableSessionSnapshots.SELECT_LATEST_BY_AGENT, (agent_id,)
            ).fetchone()
        if row is None:
            return None
        return _row_to_snapshot(row)


# ---------------------------------------------------------------------------
# Row → dataclass helpers
# ---------------------------------------------------------------------------


def _row_to_snapshot(row: sqlite3.Row) -> SessionSnapshot:
    return SessionSnapshot(
        snapshot_id=row["snapshot_id"],
        agent_id=row["agent_id"],
        timestamp=_from_iso(row["timestamp"]),
        config_version=row["config_version"],
        volatility_data=json.loads(row["volatility_data"] or "{}"),
        policy_store=json.loads(row["policy_store"] or "[]"),
        goal_tree=json.loads(row["goal_tree"] or "{}"),
        reflection_log_position=row["reflection_log_position"] or 0,
    )


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _to_iso(dt: datetime) -> str:
    return dt.isoformat()


def _from_iso(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return datetime.now(timezone.utc)


def _json_default(obj: Any) -> Any:
    """JSON fallback for dataclasses / datetimes / enums."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if hasattr(obj, "value") and hasattr(obj, "name"):
        return obj.value
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    return str(obj)
