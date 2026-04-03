# App Model Module - Agent-X

**Path**: `/app/model/`

Data persistence layer: session management, SQLite database, command history.

---

## Module Structure

```
app/model/
├── __init__.py                # Public API exports (Model, HistoryEntry)
├── model.py                   # Model facade
├── model_entities.py          # HistoryEntry dataclass
├── db/
│   ├── __init__.py            # Public API exports (SessionDatabase, TableHistory, TableUser)
│   ├── data_base.py           # SessionDatabase
│   └── database_definition.py # Table schemas
└── user_sessions/
    ├── __init__.py            # Public API exports (Session)
    └── session.py             # Session lifecycle
```

---

## Model Facade

### model.py

**Class**: `Model`

Session + DB facade for logging and retrieving command history.

**Methods**:
- `__init__(session_name: str) -> None` - creates `Session` and `SessionDatabase`, raises `Exception` if session creation fails
- `log_command(entry: HistoryEntry) -> bool` - inserts history entry into DB, returns success status
- `get_command_history() -> list[HistoryEntry]` - retrieves all history entries with full metadata

### model_entities.py

**Class**: `HistoryEntry(dataclass)` - `id: int`, `command: str`, `created_at: str`

---

## Database Layer

### db/data_base.py

**Class**: `SessionDatabase`

Per-session SQLite database with `history` and `users` tables.

**Methods**:
- `__init__(session: Session)` - creates DB tables
- `_create()` - creates tables via SQLite with explicit commit
- `_get_session_path()` - constructs DB file path from session directory
- `insert_history_entry(info: str) -> bool` - inserts a history row with UTC timestamp
- `select_history_entry() -> list[TableHistory.History] | None` - retrieves all history rows
- `_insert(query, parameters: list[Any]) -> bool` - generic insert (returns True on success, False on error)
- `_select_all(table) -> list[Any] | None` - generic select with table name validation against allowed tables

### db/database_definition.py

**Classes**:
- `TableHistory` - constants and schema for history table
  - `TABLE_NAME = "history"`
  - `TABLE_HISTORY` - CREATE SQL with `id`, `command`, `created_at`
  - `INSERT_HISTORY` - INSERT SQL
  - `History(dataclass)` - `id: int`, `command: str`, `created_at: str`
- `TableUser` - constants and schema for users table
  - `TABLE_NAME = "users"`
  - `TABLE_USER` - CREATE SQL with `id`, `name`, `age`
  - `INSERT_USER` - INSERT SQL

**Database Schema**:
```sql
CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY, command TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER);
```

---

## Session Management

### user_sessions/session.py

**Class**: `Session`

Session lifecycle management (create/destroy session directories). All state is instance-scoped (no class-level mutable attributes).

**Methods**:
- `__init__(name: str)` - initializes instance state, sanitizes session name (replaces spaces with underscores, lowercases)
- `name` (property) -> `str` - returns session name
- `directory` (property) -> `str | None` - returns session directory path
- `create()` - creates timestamped directory, returns success boolean
- `is_created()` - checks if directory exists
- `destroy() -> bool` - deletes session directory with security validation
