# App Common Module - Agent-X

**Path**: `/app/common/`

Shared utilities: file operations, console helpers.

---

## Module Structure

```
app/common/
├── files/
│   └── file_utils.py          # save_to_output()
└── utils/
    ├── file_utils.py          # directory management
    └── utils.py               # safe_int(), clear_console()
```

---

## Utilities

### utils/utils.py

**Functions**:
- `safe_int(value: str) -> int | None` - safe integer conversion, returns None on failure
- `clear_console()` - clears terminal screen (cross-platform: `cls` for Windows, `clear` for others)

### utils/file_utils.py

**Functions**:
- `create_directory_with_timestamp(name: str, base_directory) -> str | None` - creates a timestamped directory (`{name}_{YYYY-MM-DD-HH-MM-SS}`), returns path or None on error
- `directory_exists(directory: str)` - checks if directory exists
- `dangerous_delete_directory(directory_path: str) -> bool` - deletes directory with security validation and warning

### files/file_utils.py

**Function**: `save_to_output(text: str)` - writes text to `local/output.txt`
