"""SQLite schema descriptors (stdlib ``sqlite3`` — no ORM, no migrations).

Mirrors the existing :class:`SessionDatabase` convention: each table is a
``Table*`` descriptor class exposing ``TABLE_QUERY`` (idempotent
``CREATE TABLE IF NOT EXISTS``) and prepared statements as string constants.

Persistence strategy (design_001 §5.3):
  * stdlib ``sqlite3`` only
  * idempotent DDL on first connection
  * parameterized queries (no f-string SQL for values)
  * JSON-serialized blobs for complex nested objects
"""

from __future__ import annotations


class TableAgents:
    TABLE_NAME = "agents"

    TABLE_QUERY = f"""\
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
      id TEXT PRIMARY KEY,
      name TEXT,
      version INTEGER,
      autonomy_level TEXT,
      config_json TEXT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """

    INSERT = (
        f"INSERT OR REPLACE INTO {TABLE_NAME} "
        f"(id, name, version, autonomy_level, config_json, created_at) "
        f"VALUES (?, ?, ?, ?, ?, ?)"
    )
    SELECT_BY_ID = f"SELECT * FROM {TABLE_NAME} WHERE id = ?"


class TableSessionSnapshots:
    TABLE_NAME = "session_snapshots"

    TABLE_QUERY = f"""\
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
      snapshot_id TEXT PRIMARY KEY,
      agent_id TEXT NOT NULL,
      timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      config_version INTEGER,
      volatility_data TEXT,
      policy_store TEXT,
      goal_tree TEXT,
      reflection_log_position INTEGER
    )
    """

    INSERT = (
        f"INSERT INTO {TABLE_NAME} "
        f"(snapshot_id, agent_id, timestamp, config_version, "
        f"volatility_data, policy_store, goal_tree, reflection_log_position) "
        f"VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
    )
    SELECT_LATEST_BY_AGENT = (
        f"SELECT * FROM {TABLE_NAME} WHERE agent_id = ? "
        f"ORDER BY timestamp DESC LIMIT 1"
    )
    SELECT_BY_ID = f"SELECT * FROM {TABLE_NAME} WHERE snapshot_id = ?"


class TableMemoryEntries:
    TABLE_NAME = "memory_entries"

    TABLE_QUERY = f"""\
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
      id TEXT PRIMARY KEY,
      agent_id TEXT,
      tier TEXT,
      source TEXT,
      content TEXT,
      tags TEXT,
      importance REAL,
      created_at TIMESTAMP,
      last_accessed TIMESTAMP,
      access_count INTEGER DEFAULT 0
    )
    """

    INSERT = (
        f"INSERT OR REPLACE INTO {TABLE_NAME} "
        f"(id, agent_id, tier, source, content, tags, importance, "
        f"created_at, last_accessed, access_count) "
        f"VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    )
    SELECT_BY_AGENT = (
        f"SELECT * FROM {TABLE_NAME} WHERE agent_id = ? ORDER BY created_at DESC"
    )
    SELECT_BY_AGENT_TIER = (
        f"SELECT * FROM {TABLE_NAME} WHERE agent_id = ? AND tier = ? "
        f"ORDER BY created_at DESC"
    )
    DELETE_BY_ID = f"DELETE FROM {TABLE_NAME} WHERE id = ?"


class TablePolicyRules:
    TABLE_NAME = "policy_rules"

    TABLE_QUERY = f"""\
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
      id TEXT PRIMARY KEY,
      agent_id TEXT,
      condition_expr TEXT,
      action_json TEXT,
      priority INTEGER,
      enabled INTEGER DEFAULT 1,
      source TEXT,
      created_by TEXT,
      version INTEGER DEFAULT 1,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """

    INSERT = (
        f"INSERT OR REPLACE INTO {TABLE_NAME} "
        f"(id, agent_id, condition_expr, action_json, priority, enabled, "
        f"source, created_by, version, created_at) "
        f"VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    )
    SELECT_BY_AGENT = f"SELECT * FROM {TABLE_NAME} WHERE agent_id = ?"
    DELETE_BY_ID = f"DELETE FROM {TABLE_NAME} WHERE id = ?"


class TableGoals:
    TABLE_NAME = "goals"

    TABLE_QUERY = f"""\
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
      id TEXT PRIMARY KEY,
      agent_id TEXT,
      description TEXT,
      type TEXT,
      parent TEXT,
      children TEXT,
      status TEXT,
      priority INTEGER,
      success_criteria TEXT,
      created_at TIMESTAMP,
      updated_at TIMESTAMP
    )
    """

    INSERT = (
        f"INSERT OR REPLACE INTO {TABLE_NAME} "
        f"(id, agent_id, description, type, parent, children, status, "
        f"priority, success_criteria, created_at, updated_at) "
        f"VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    )
    SELECT_BY_AGENT = f"SELECT * FROM {TABLE_NAME} WHERE agent_id = ? ORDER BY created_at ASC"
    DELETE_BY_ID = f"DELETE FROM {TABLE_NAME} WHERE id = ?"


class TableReflectionEntries:
    TABLE_NAME = "reflection_entries"

    TABLE_QUERY = f"""\
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
      id TEXT PRIMARY KEY,
      agent_id TEXT,
      trace_json TEXT,
      critique_json TEXT,
      proposals_json TEXT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """

    INSERT = (
        f"INSERT INTO {TABLE_NAME} "
        f"(id, agent_id, trace_json, critique_json, proposals_json, created_at) "
        f"VALUES (?, ?, ?, ?, ?, ?)"
    )
    SELECT_BY_AGENT = (
        f"SELECT * FROM {TABLE_NAME} WHERE agent_id = ? "
        f"ORDER BY created_at DESC LIMIT ?"
    )


#: All table descriptor classes — used by ``SessionDatabase._ensure_schema``.
ALL_TABLES = (
    TableAgents,
    TableSessionSnapshots,
    TableMemoryEntries,
    TablePolicyRules,
    TableGoals,
    TableReflectionEntries,
)
