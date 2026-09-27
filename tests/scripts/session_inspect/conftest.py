"""session_inspect test package — path bootstrap + sanitized fixture factory.

Fixture policy (design_001 §7): tests build tiny schema-faithful SQLite DBs in
tmp_path with SYNTHETIC content only; no raw transcript bodies. Live-DB tests
are opt-in via MH13_LIVE_DB=1 (+ MH13_DB_PATH override) and stay read-only.
"""
import json
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

# --- verified OpenCode DDL (analysis_001 §1), trimmed to required surface ---
SCHEMA_DDL = """
CREATE TABLE `session` (
  `id` text PRIMARY KEY, `project_id` text NOT NULL, `parent_id` text,
  `slug` text NOT NULL, `directory` text NOT NULL, `title` text NOT NULL,
  `version` text NOT NULL, `share_url` text, `summary_additions` integer,
  `summary_deletions` integer, `summary_files` integer, `summary_diffs` text,
  `revert` text, `permission` text, `time_created` integer NOT NULL,
  `time_updated` integer NOT NULL, `time_compacting` integer, `time_archived` integer,
  `workspace_id` text, `path` text, `agent` text, `model` text,
  `cost` real DEFAULT 0 NOT NULL,
  `tokens_input` integer DEFAULT 0 NOT NULL, `tokens_output` integer DEFAULT 0 NOT NULL,
  `tokens_reasoning` integer DEFAULT 0 NOT NULL, `tokens_cache_read` integer DEFAULT 0 NOT NULL,
  `tokens_cache_write` integer DEFAULT 0 NOT NULL, `metadata` text
);
CREATE TABLE `message` (
  `id` text PRIMARY KEY, `session_id` text NOT NULL,
  `time_created` integer NOT NULL, `time_updated` integer NOT NULL, `data` text NOT NULL
);
CREATE TABLE `part` (
  `id` text PRIMARY KEY, `message_id` text NOT NULL, `session_id` text NOT NULL,
  `time_created` integer NOT NULL, `time_updated` integer NOT NULL, `data` text NOT NULL
);
CREATE TABLE `session_message` (
  `id` text PRIMARY KEY, `session_id` text NOT NULL, `type` text NOT NULL,
  `time_created` integer NOT NULL, `time_updated` integer NOT NULL, `data` text NOT NULL,
  `seq` integer NOT NULL
);
CREATE TABLE `session_input` (
  `id` text PRIMARY KEY, `session_id` text NOT NULL, `prompt` text NOT NULL,
  `delivery` text NOT NULL, `admitted_seq` integer NOT NULL, `promoted_seq` integer,
  `time_created` integer NOT NULL
);
CREATE TABLE `event_sequence` (`aggregate_id` text PRIMARY KEY, `seq` integer NOT NULL, `owner_id` text);
CREATE TABLE `event` (
  `id` text PRIMARY KEY, `aggregate_id` text NOT NULL, `seq` integer NOT NULL,
  `type` text NOT NULL, `data` text NOT NULL
);
CREATE TABLE `project` (
  `id` text PRIMARY KEY, `worktree` text NOT NULL, `vcs` text, `name` text,
  `icon_url` text, `icon_color` text, `time_created` integer NOT NULL,
  `time_updated` integer NOT NULL, `time_initialized` integer, `sandboxes` text NOT NULL,
  `commands` text, `icon_url_override` text
);
CREATE TABLE `__drizzle_migrations` (`id` integer PRIMARY KEY, `hash` text, `created_at` integer);
CREATE TABLE `data_migration` (`name` text PRIMARY KEY, `time_completed` integer NOT NULL);
"""


def _enc(v):
    return json.dumps(v) if isinstance(v, dict) else v


def _insert(conn, table, row):
    cols = ", ".join(row.keys())
    ph = ", ".join("?" for _ in row)
    conn.execute(f"INSERT INTO {table} ({cols}) VALUES ({ph})", [_enc(v) for v in row.values()])


def build_db(path, *, sessions=(), messages=(), parts=(), events=(),
             session_messages=(),
             drizzle=((1, "h1", 1778000000000), (2, "h2", 1778520877000)),
             data_migrations=(("legacy_a", 1770000000000),),
             drop_tables=()):
    """Create a sanitized fixture DB at `path` (str/Path) with synthetic rows.

    Row dicts use column names; dict values are auto-JSON-encoded (the `data`
    columns). `drop_tables` omits named tables from the DDL (negative
    capability tests, e.g. missing `part` -> schema_unsupported).
    """
    path = Path(path)
    if path.exists():
        path.unlink()
    conn = sqlite3.connect(path)
    try:
        for stmt in SCHEMA_DDL.strip().split(";\n"):
            name = stmt.split("CREATE TABLE")[1].split("(")[0].strip().strip("` ")
            if name in drop_tables:
                continue
            conn.execute(stmt.strip().rstrip(";") + ";")
        for row in sessions:
            _insert(conn, "session", row)
        for row in messages:
            _insert(conn, "message", row)
        for row in parts:
            _insert(conn, "part", row)
        for row in events:
            _insert(conn, "event", row)
        for row in session_messages:
            _insert(conn, "session_message", row)
        conn.executemany("INSERT INTO __drizzle_migrations VALUES (?,?,?)", drizzle)
        conn.executemany("INSERT INTO data_migration VALUES (?,?)", data_migrations)
        conn.commit()
    finally:
        conn.close()
    return str(path)


def ses_row(sid, *, directory="/repo", title="t", parent_id=None, agent="build",
            model=None, time_created=1790000000000, time_updated=None,
            ti=0, to=0, tr=0, tcr=0, tcw=0, cost=0.0):
    return {
        "id": sid, "project_id": "prj_1", "parent_id": parent_id, "slug": "s",
        "directory": directory, "title": title, "version": "1", "time_created": time_created,
        "time_updated": time_updated if time_updated is not None else time_created + 1000,
        "agent": agent, "model": model, "cost": cost,
        "tokens_input": ti, "tokens_output": to, "tokens_reasoning": tr,
        "tokens_cache_read": tcr, "tokens_cache_write": tcw,
    }


def msg_row(mid, sid, *, role="assistant", parent_id=None, time_created=1790000000000,
            tokens=None, cost=0, model_id="m/1"):
    data = {"role": role, "path": {"cwd": "/repo", "root": "/repo"}, "cost": cost,
            "time": {"created": time_created}}
    if parent_id is not None:
        data["parentID"] = parent_id
    if tokens is not None:
        data["tokens"] = tokens
    if model_id is not None:
        data["modelID"] = model_id
        data["providerID"] = "p"
    return {"id": mid, "session_id": sid, "time_created": time_created,
            "time_updated": time_created, "data": json.dumps(data)}


def part_row(pid, mid, sid, *, ptype="text", payload=None, time_created=1790000000000):
    data = {"type": ptype}
    if payload:
        data.update(payload)
    return {"id": pid, "message_id": mid, "session_id": sid,
            "time_created": time_created, "time_updated": time_created,
            "data": json.dumps(data)}


def tok(total=None, input=0, output=0, reasoning=0, cache_read=0, cache_write=0):
    """Message/step tokens dict exactly as observed in real `message.data`."""
    d = {"input": input, "output": output, "reasoning": reasoning,
         "cache": {"read": cache_read, "write": cache_write}}
    if total is not None:
        d = {"total": total, **d}
    return d
