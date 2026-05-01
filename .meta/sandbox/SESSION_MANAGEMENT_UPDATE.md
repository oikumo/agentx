# Session Management Update - Always Current with Backup

## Summary

Updated the session management system to ensure:
1. A session named "current" **always exists** - created automatically if not present
2. When user creates a new session with the `new` command, the current session is **backed up with a timestamp**
3. All sessions are **preserved on disk** for data safety (never deleted)

## Changes Made

### 1. Session Manager (`src/agentx/model/session/session_manager.py`)

#### Key Changes:
- **Always maintains a "current" session**: The session name is now fixed as "current" instead of "default"
- **Automatic creation**: If no current session exists, one is created automatically on initialization
- **Backup on new session**: When `create_new_session()` is called:
  1. The current session directory is moved to a backup location with timestamp
  2. Format: `current_backup_YYYY-MM-DD-HH-MM-SS-microseconds`
  3. A fresh "current" session is created
  4. The new session becomes active

#### New Methods:
- `_ensure_current_session_exists()`: Ensures a "current" session always exists
- `_backup_current_session()`: Backs up current session with timestamp before creating new one

#### Modified Methods:
- `create_new_session()`: Now includes backup logic before creating new session
- `get_session_manager()`: Fixed to properly return singleton instance

### 2. Session Class (`src/agentx/model/session/session.py`)

No changes required - existing implementation supports the new behavior.

### 3. Commands (`src/agentx/controllers/main_controller/commands.py`)

No changes required - the existing `NewCommand` already calls `session_manager.create_new_session()`, which now includes backup functionality.

## Usage

### Command Line

```bash
# Create a new session (backs up current session automatically)
new

# Create a new session with custom name
new my_session
```

### Programmatic Usage

```python
from agentx.model.session.session_manager import get_session_manager

# Get session manager (creates 'current' session if needed)
manager = get_session_manager()

# Get current session
session = manager.get_current_session()
print(f"Current session: {session.name}")
print(f"Directory: {session.directory}")

# Create new session (backs up current automatically)
new_session = manager.create_new_session("my_session")

# Add data to session
db = manager.get_database()
if db:
    db.insert_history_entry("my_command")
```

## Directory Structure

After running the application and creating several sessions:

```
local_sessions/
├── current_2026-05-01-15-04-33/          # Active current session
│   └── current.db
├── current_backup_2026-05-01-15-04-33-724245/  # Backed up session
│   └── current.db
├── current_backup_2026-05-01-15-04-33-764445/  # Another backup
│   └── current.db
└── ...
```

## Key Features

### ✓ Always Current
- A session named "current" always exists
- Created automatically on first use
- Never leaves the user without an active session

### ✓ Automatic Backup
- Creating a new session automatically backs up the current one
- Backup includes timestamp with microseconds for uniqueness
- Format: `current_backup_YYYY-MM-DD-HH-MM-SS-microseconds`

### ✓ Data Safety
- Sessions are NEVER deleted
- All historical data is preserved
- Backups can be manually reviewed or restored if needed

### ✓ Unique Timestamps
- Uses microsecond precision to ensure unique backup names
- Prevents conflicts when creating multiple sessions rapidly

## Testing

Comprehensive tests are available in:
- `.meta/tests_sandbox/test_session_current.py`

Run tests:
```bash
PYTHONPATH=src python3 .meta/tests_sandbox/test_session_current.py
```

Demo script:
```bash
PYTHONPATH=src python3 .meta/tests_sandbox/demo_session_management.py
```

## Test Results

All tests passing:
- ✓ Session always exists
- ✓ New session creates backup
- ✓ Multiple new sessions work correctly
- ✓ Session data persists in backups

## Backward Compatibility

The changes are backward compatible:
- Existing sessions remain in their directories
- The `create_new_session()` API remains the same
- Existing code using the session manager continues to work

## Migration Notes

No migration needed. The system automatically:
1. Creates a "current" session if none exists
2. Backs up existing sessions when new ones are created
3. Preserves all historical session data

## Future Enhancements

Potential improvements:
- Session restore functionality
- Session listing command
- Session cleanup policies (with user confirmation)
- Session metadata (creation time, last modified, etc.)
