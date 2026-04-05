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
├── test_commands.py                 # Command implementation tests
└── test_chat_loop.py                # ChatLoop TDD tests (38 tests)
```

## Rules

- Tests must use `unittest.TestCase` framework
- All tests must pass before committing
- Tests here are experimental and may change frequently
- Mature tests should eventually migrate to `tests/`

## ChatLoop Tests

### tests_sandbox/test_chat_loop.py

**Class**: `TestChatLoop`

Comprehensive TDD test suite for the `ChatLoop` class (38 tests). Covers initialization, history management, response generation, exit conditions, single-turn execution, interactive loop behavior, streaming, and factory creation.

**Test Categories**:
- **Initialization**: Default system prompt, custom system prompt
- **History Management**: Adding user/assistant messages, history grows correctly
- **Response Generation**: Mock LLM response, content extraction (string, list, None), error rollback
- **Exit Conditions**: quit, exit, case insensitive, normal input
- **Single-Turn Execution**: `run()` with valid input, empty input, exit input
- **Interactive Loop**: `start_interactive()` processes inputs and prints responses, exits on quit/exit
- **Streaming**: `get_streaming_response()` yields chunks, `run_streaming()` collects responses, `start_interactive_streaming()` prints live chunks with history management
- **Factory Creation**: `create_chat_loop_local()` returns ChatLoop instance
- **AIChat Command**: Verifies REPL command uses streaming methods

**Mocking Strategy**:
- Uses `unittest.mock.Mock` and `patch` to isolate `ChatLoop` from real LLM providers
- Mocks `BaseChatModel.invoke()` and `BaseChatModel.stream()` to return predictable responses
- Mocks `input()` for interactive loop testing
- Captures `print()` output via `StringIO` redirection
- Uses `_make_chunk()` helper to create mock streaming chunks with proper `.text` and `.content` attributes

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

- **Project Navigation**: See [_agent_rules/PROJECT_NAVIGATION_ROUTES.md](../_agent_rules/PROJECT_NAVIGATION_ROUTES.md) for module structure
- **Project Documentation**: See [_agent_rules/PROJECT_DOCUMENTATION.md](../_agent_rules/PROJECT_DOCUMENTATION.md) for full documentation map
