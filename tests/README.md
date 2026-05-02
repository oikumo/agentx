# Test Directory Structure

**Status**: Consolidated and documented

## Structure

```
tests/
├── unit/              # Unit tests for src/agentx/ modules
├── integration/       # Integration tests
└── README.md          # This file
```

## Usage

- **Unit tests**: `pytest tests/unit/`
- **Integration tests**: `pytest tests/integration/`
- **Test development**: Work in `.meta/tests_sandbox/` then move here

## Legacy Locations (Deprecated)

- `.meta/tests_sandbox/` - TDD workspace only
- `.meta/tests_automated/` - Reflection tests
- `test_automated/` - Legacy tests

