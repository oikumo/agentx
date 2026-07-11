# Persistence

> **Scope:** the databases, their schemas, the no-ORM/DP convention, and the
> filesystem layout.

---

## 1. Convention: stdlib sqlite3, no ORM

agentx uses **only Python's stdlib `sqlite3`** for relational persistence. There
is **no SQLAlchemy, no Alembic, no migrations framework**. This is a deliberate
architectural decision (recorded in `WORK.md`):

- DDL is idempotent: `CREATE TABLE IF NOT EXISTS` (defined as string constants
  in `Table*` classes). Creating the DB on first use is enough.
- All SQL lives in `DP_*` / `*Database` classes (the Data Partner pattern) —
  never in controllers or views. Enforced by `mvc_check.py` (`SQL_OUTSIDE_DP`).
- Schemas are simple enough that versioned migrations are not needed; the
  `config_version` field on `SessionSnapshot` tracks agent config shape.

---

## 2. The three databases

| DB file | Created by | Lives under | Tables |
|---------|-----------|-------------|--------|
| `session.db` | `SessionDatabase` (`DP_Session`) | `<session_dir>/session.db` | `history`, `users` |
| `rag.db` | `RagDatabase` (`DP_Rag`) | `<session_dir>/rag/<repo_id>/rag.db` | `ingestion` |
| `agent_session.db` | `SessionDatabase` (agent) | `<session_dir>/agent_session.db` (or `./`) | `agents`, `session_snapshots`, `memory_entries`, `policy_rules`, `goals`, `reflection_entries` |

> **Naming collision note:** both the session subsystem and the agent subsystem
> define a class named `SessionDatabase`. They are distinct classes in
> different modules:
> - `model/session/session_db.py` → session history DB
> - `agent/persistence/agent_db.py` → agent snapshot/repo DB

---

## 3. Agent DB schema (`agent_session.db`)

Defined in `agent/persistence/schema_db.py` as `Table*` classes; repositories
in `agent/persistence/repositories_db.py`.

| Table | Purpose | Key columns |
|-------|---------|-------------|
| `agents` | one row per agent instance | `agent_id`, `name`, `autonomy_level`, `config_json`, `created_at` |
| `session_snapshots` | serialised `SessionSnapshot` rows | `snapshot_id`, `agent_id`, `config_version`, `volatility_data` (JSON), `policy_store` (JSON), `goal_tree` (JSON), `reflection_log_position`, `created_at` |
| `memory_entries` | persistent memory tier (volatile is in-memory) | `agent_id`, `entry_id`, `tier`, `content` (JSON), `metadata` (JSON) |
| `policy_rules` | policy rule store (N3: source of truth) | `agent_id`, `rule_id`, `condition_expr`, `action` (JSON), `priority`, `enabled`, `metadata` (JSON) |
| `goals` | goal tree nodes | `agent_id`, `goal_id`, `parent`, `description`, `type`, `status`, `priority`, `success_criteria` (JSON) |
| `reflection_entries` | reflection log | `agent_id`, `entry_id`, `trace` (JSON), `critique` (JSON), `proposals` (JSON), `created_at` |

**Snapshot model:** `Agent.persist()` writes a `SessionSnapshot` row capturing
the *full* volatile state (config, volatile memory, policy store, goal-tree
root, reflection-log position). `resume_session(id)` rebuilds in-memory state
from it. See [data_flow.md](data_flow.md) §9.

---

## 4. Session DB schema (`session.db`)

Defined in `model/session/session_db.py` (`TableHistory`, `TableUser`).

| Table | Purpose | Columns |
|-------|---------|---------|
| `history` | command history (per session) | `id` PK, `command`, `created_at` |
| `users` | (reserved/legacy) | `id` PK, `name`, `age` |

`SessionDatabase._select_all` is guarded by an allowlist `{history, users}`.

---

## 5. RAG DB schema (`rag.db`)

Defined in `model/rag/rag_db.py` (`TableIngestion`).

| Table | Purpose | Columns |
|-------|---------|---------|
| `ingestion` | ingestion records | `id` PK, `vector_db_path`, `created_at` |

The bulk of RAG data is **not** in sqlite — it's in the Chroma vector store
(`<repo>/db/`) and the JSONL document store (`<repo>/docs/`).

---

## 6. Filesystem layout

```
local_sessions/                       # SESSION_DEFAULT_BASE_DIRECTORY
└── current/                          # the active session (SESSION_CURRENT_NAME)
    ├── session.db                    # session history
    ├── agent_session.db              # agent snapshots + repos (if agent opened)
    ├── current_backup_<timestamp>/   # created on "new [name]"
    └── rag/
        └── <repo_id>/                # a RAG repository (RagProvider lists rag_* dirs)
            ├── rag.db                # ingestion records
            ├── db/                   # Chroma vector store
            └── docs/                 # ingested documents (JSONL)
```

- Session dirs may be timestamped (`<timestamp>_<name>`) or plain (`<name>`),
  via `utils.create_directory_{with,without}_timestamp`.
- Deletion is guarded by `DIRECTORIES_DELETION_ALLOWED = ["local_sessions"]`
  (`utils.is_directory_allowed_to_deletion`).
- The agent's `sandbox_root` (for `FileSystemTool`) defaults to the session
  directory.

---

## 7. DP class reference

| DP class | File | DB | Methods (representative) |
|----------|------|----|--------------------------|
| `SessionDatabase` (session) | `model/session/session_db.py` | `session.db` | `create_if_not_exists`, `insert_history_entry`, `select_history_entry` |
| `RagDatabase` | `model/rag/rag_db.py` | `rag.db` | `create_if_not_exists`, `insert_ingestion_entry`, `select_ingestion_entries` |
| `SessionDatabase` (agent) | `agent/persistence/agent_db.py` | `agent_session.db` | `save_snapshot_with_retry`, `load_snapshot`, `load_latest_snapshot`, `_persist_agent_row` |
| `GoalRepository` | `agent/persistence/repositories_db.py` | `agent_session.db` | `save`, `load_tree` |
| `MemoryRepository` | same | same | `save`, `load_recent` |
| `PolicyRepository` | same | same | `save`, `load_all` |
| `ReflectionRepository` | same | same | `save`, `load_recent_entries` |

All repositories take `(db_path, agent_id)` and use parameterised queries.
