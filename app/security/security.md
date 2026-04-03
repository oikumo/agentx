# App - Security Module

## Overview
Directory deletion safeguards to prevent accidental deletion of important directories.

## Key Files

| File | Description |
|------|-------------|
| `security.py` | `is_directory_allowed_to_deletion()` - validates paths are within allowed dirs |
| `security_constants.py` | Constants: `SESSION_DEFAULT_NAME`, `SESSION_DEFAULT_BASE_DIRECTORY`, `DIRECTORIES_DELETION_ALLOWED` |

## Constants
- `SESSION_DEFAULT_NAME = "default"`
- `SESSION_DEFAULT_BASE_DIRECTORY = "local_sessions"`
- `DIRECTORIES_DELETION_ALLOWED = ["local_sessions"]`

## Security Check
Only directories within `local_sessions/` are allowed to be deleted, preventing accidental deletion of important project files.
