# App Security Module - Agent-X

**Path**: `/app/security/`

Security utilities for directory deletion safeguards.

---

## Module Structure

```
app/security/
├── security.py                # is_directory_allowed_to_deletion()
└── security_constants.py      # deletion constants
```

---

## Security Functions

### security.py

**Function**: `is_directory_allowed_to_deletion(directory_path: str) -> bool`

Validates that a directory path is:
1. Within the current working directory
2. Within one of the allowed deletion directories (`local_sessions`)

Raises `PermissionError` if validation fails.

### security_constants.py

**Constants**:
- `SESSION_DEFAULT_NAME = "default"`
- `SESSION_DEFAULT_BASE_DIRECTORY = "local_sessions"`
- `DIRECTORIES_DELETION_ALLOWED = ["local_sessions"]`
