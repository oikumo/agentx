# App - Model Module

## Overview
Data persistence and session management. Provides SQLite database per session, session lifecycle, and command history tracking.

## Structure

```
model/
├── model.py                       # Model class - session + DB facade
├── model_entities.py              # HistoryEntry dataclass
├── db/
│   ├── data_base.py               # SessionDatabase - SQLite wrapper per session
│   └── database_definition.py     # Table schemas (history, users)
└── user_sessions/
    └── session.py                 # Session lifecycle (create/destroy)
```

## Key Classes

| Class | File | Description |
|-------|------|-------------|
| `Model` | `model.py` | Orchestrates sessions and database; logs/retrieves command history |
| `HistoryEntry` | `model_entities.py` | Dataclass representing a command history entry |
| `SessionDatabase` | `db/data_base.py` | Per-session SQLite DB with `history` and `users` tables |
| `Session` | `user_sessions/session.py` | Creates timestamped directories under `local_sessions/` |

## Database Schema

```sql
CREATE TABLE IF NOT EXISTS history (
  id INTEGER PRIMARY KEY,
  command TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY,
  name TEXT,
  age INTEGER
);
```

## Session Lifecycle
1. `Session.create()` → creates timestamped dir → `SessionDatabase._create()` → creates tables
2. `Session.destroy()` → security-checked directory deletion
3. DB stored at `local_sessions/{session_name}_{timestamp}/{session_name}.db`
