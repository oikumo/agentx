# AgentX Unit Tests

Comprehensive unit test suite for the AgentX project, covering all core modules with isolated tests.

## Test Results

**Total Tests**: 205  
**Status**: ✅ All Passing  
**Coverage**: Core modules (common, model, controllers, views, db)

## Test Organization

Tests are organized by module structure mirroring `src/agentx/`:

```.
```

## Running Tests

```bash
# Run all tests
uv run pytest tests/unit/ -v

# Run specific test file
uv run pytest tests/unit/common/test_utils.py -v

# Run with coverage (if pytest-cov installed)
uv run pytest tests/unit/ --cov=agentx --cov-report=html
```

