# persistence.md — Databases & Filesystem (compressed)

**SCOPE:** DBs, schemas, no-ORM/DP convention, filesystem layout.

---

## 1. Convention: stdlib sqlite3, No ORM
- **Only** Python stdlib `sqlite3`. No SQLAlchemy, Alembic, migrations framework. Architectural decision (in `WORK.md`).
- DDL = idempotent `CREATE TABLE IF NOT EXISTS` (string constants in `Table*` classes). DB created on first use.
- All SQL in `DP_*` / `*Database` classes — never in controllers/views. Enforced by `mvc_check.py` (`SQL_OUTSIDE_DP`).
- Schemas simple; versioned migrations not needed. `config_version` on `SessionSnapshot` tracks agent config shape.

---

## 2. The Three Databases

| DB file | Created by | Lives under | Tables |
|---------|-----------|-------------|--------|
| `session.db` | `SessionDatabase` (`DP_Session`) | `<session_dir>/session.db` | `history`, `users` |
| `rag.db` | `RagDatabase` (`DP_Rag`) | `<session_dir>/rag/<repo_id>/rag.db` | `ingestion` |
| `agent_session.db` | `SessionDatabase` (agent) | `<session_dir>/agent_session.db` (or `./`) | `agents`, `session_snapshots`, `memory_entries`, `policy_rules`, `goals`, `reflection_entries` |

> **Naming collision:** Both session and agent subsystems define `SessionDatabase` — distinct classes in different modules:
> - `model/session/session_db.py` → session history DB
> - `agent/persistence/agent_db.py` → agent snapshot/repo DB

---

## 3. Agent DB Schema (`agent_session.db`)

Defined in `agent/persistence/schema_db.py` (`Table*` classes); repos in `agent/persistence/repositories_db.py`.

| Table | Purpose | Key columns |
|-------|---------|-------------|
| `agents` | One row per agent instance | `agent_id`, `name`, `autonomy_level`, `config_json`, `created_at` |
| `session_snapshots` | Serialised `SessionSnapshot` rows | `snapshot_id`, `agent_id`, `config_version`, `volatility_data` (JSON), `policy_store` (JSON), `goal_tree` (JSON), `reflection_log_position`, `created_at` |
| `memory_entries` | Persistent memory tier (volatile = in-memory) | `agent_id`, `entry_id`, `tier`, `content` (JSON), `metadata` (JSON) |
| `policy_rules` | Policy rule store (N3: source of truth) | `agent_id`, `rule_id`, `condition_expr`, `action` (JSON), `priority`, `enabled`, `metadata` (JSON) |
| `goals` | Goal tree nodes | `agent_id`, `goal_id`, `parent`, `description`, `type`, `status`, `priority`, `success_criteria` (JSON) |
| `reflection_entries` | Reflection log | `agent_id`, `entry_id`, `trace` (JSON), `critique` (JSON), `proposals` (JSON), `created_at` |

**Snapshot model:** `Agent.persist()` writes `SessionSnapshot` capturing full volatile state (config, volatile memory, policy store, goal-tree root, reflection-log position). `resume_session(id)` rebuilds in-memory state from it. See data_flow.md §9.

---

## 4. Session DB Schema (`session.db`)

Defined in `model/session/session_db.py` (`TableHistory`, `TableUser`).

| Table | Purpose | Columns |
|-------|---------|---------|
| `history` | Command history (per session) | `id` PK, `command`, `created_at` |
| `users` | Reserved/legacy | `id` PK, `name`, `age` |

`SessionDatabase._select_all` guarded by allowlist `{history, users}`.

---

## 5. RAG DB Schema (`rag.db`)

Defined in `model/rag/rag_db.py` (`TableIngestion`).

| Table | Purpose | Columns |
|-------|---------|---------|
| `ingestion` | Ingestion records | `id` PK, `vector_db_path`, `created_at` |

**Bulk of RAG data NOT in sqlite** — it's in Chroma vector store (`<repo>/db/`) and JSONL document store (`<repo>/docs/`).

---

## 6. Filesystem Layout

```
local_sessions/                       # SESSION_DEFAULT_BASE_DIRECTORY
└── current/                          # active session (SESSION_CURRENT_NAME)
    ├── session.db                    # session history
    ├── agent_session.db              # agent snapshots + repos (if agent opened)
    ├── current_backup_<timestamp>/   # created on "new [name]"
    └── rag/
        └── <repo_id>/                # a RAG repository (RagProvider lists rag_* dirs)
            ├── rag.db                # ingestion records
            ├── db/                   # Chroma vector store
            └── docs/                 # ingested documents (JSONL)
```

- Session dirs: timestamped (`<timestamp>_<name>`) or plain (`<name>`), via `utils.create_directory_{with,without}_timestamp`.
- Deletion guarded by `DIRECTORIES_DELETION_ALLOWED = ["local_sessions"]` (`utils.is_directory_allowed_to_deletion`).
- Agent's `sandbox_root` (for `FileSystemTool`) defaults to session directory.

---

## 7. DP Class Reference

| DP class | File | DB | Representative methods |
|----------|------|----|------------------------|
| `SessionDatabase` (session) | `model/session/session_db.py` | `session.db` | `create_if_not_exists`, `insert_history_entry`, `select_history_entry` |
| `RagDatabase` | `model/rag/rag_db.py` | `rag.db` | `create_if_not_exists`, `insert_ingestion_entry`, `select_ingestion_entries` |
| `SessionDatabase` (agent) | `agent/persistence/agent_db.py` | `agent_session.db` | `save_snapshot_with_retry`, `load_snapshot`, `load_latest_snapshot`, `_persist_agent_row` |
| `GoalRepository` | `agent/persistence/repositories_db.py` | `agent_session.db` | `save`, `load_tree` |
| `MemoryRepository` | same | same | `save`, `load_recent` |
| `PolicyRepository` | same | same | `save`, `load_all` |
| `ReflectionRepository` | same | same | `save`, `load_recent_entries` |

All repositories take `(db_path, agent_id)` and use parameterised queries.