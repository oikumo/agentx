# Tests Sandbox - Agent-X

> **Purpose**: Feature and integration testing sandbox for Agent-X development

## Overview

The `tests_sandbox/` directory is a dedicated space for experimental and feature-level testing. Unlike the `tests/` directory (which contains the official unit and integration test suite), this sandbox allows for:

- **Feature Testing**: Testing new features before they're mature enough for the official test suite
- **Integration Testing**: Cross-module integration tests
- **Exploratory Testing**: Quick validation of code changes
- **Development Iteration**: Rapid test creation during active development

## Structure

```
tests_sandbox/
├── README.md                        # This file
├── features/                        # Feature-level tests
│   └── test_controller.py           # MainController feature tests
├── test_command_parser.py           # CommandParser unit tests
└── test_commands.py                 # Command implementation tests
```

## Rules

- Tests must use `unittest.TestCase` framework
- All tests must pass before committing
- Tests here are experimental and may change frequently
- Mature tests should eventually migrate to `tests/`

## Running Tests

```bash
# Run all sandbox tests
uv run pytest tests_sandbox/ -v

# Run specific test file
uv run pytest tests_sandbox/features/test_controller.py -v

# Run specific test class
uv run pytest tests_sandbox/test_commands.py::TestSumCommand -v
```

## Integration Points

- **Project Navigation**: See [PROJECT_NAVIGATION_ROUTES.md](../PROJECT_NAVIGATION_ROUTES.md) for module structure
- **Project Documentation**: See [PROJECT_DOCUMENTATION.md](../PROJECT_DOCUMENTATION.md) for full documentation map
