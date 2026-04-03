# App - Common Module

## Overview
Shared utilities used across the application for file operations, directory management, and general helpers.

## Structure

```
common/
├── files/
│   └── file_utils.py              # save_to_output() - writes text to local/output.txt
└── utils/
    ├── file_utils.py              # create_directory_with_timestamp(), dangerous_delete_directory()
    └── utils.py                   # safe_int(), clear_console()
```

## Key Functions

| Function | File | Description |
|----------|------|-------------|
| `safe_int(value)` | `utils/utils.py` | Safely parses integer from string |
| `clear_console()` | `utils/utils.py` | Cross-platform console clearing |
| `create_directory_with_timestamp()` | `utils/file_utils.py` | Creates timestamped session directories |
| `dangerous_delete_directory()` | `utils/file_utils.py` | Deletes directories with security validation |
| `save_to_output(text)` | `files/file_utils.py` | Writes text to `local/output.txt` |
