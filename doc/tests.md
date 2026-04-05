# Tests - Agent-X

**Path**: `/tests/` (read-only) and `/tests_sandbox/` (writable)

Unit tests using `unittest` framework.

---

## Module Structure

```
tests/
├── integration/
│   └── __init__.py
└── unit/
    └── app/
        └── __init__.py
```

---

## Tests Sandbox

**Path**: `/tests_sandbox/`

Feature and integration testing sandbox. Uses `unittest.TestCase` framework.

### Structure

```
tests_sandbox/
├── features/
│   └── test_controller.py           # MainController feature tests (6 tests)
├── test_agent_streaming.py          # Agent streaming methods (6 tests)
├── test_argument_parser.py          # --model flag argument parsing (14 tests)
├── test_benchmark_navigation.py     # AGENTS.md navigation benchmark (12 tests)
├── test_chat_command.py             # AIChat command with --model flag (6 tests)
├── test_chat_loop.py                # ChatLoop TDD tests (40+ tests)
├── test_command_parser.py           # CommandParser unit tests
├── test_commands.py                 # Command implementation tests
├── test_factory_refactor.py         # AgentFactory unified API tests
├── test_llm_managers.py             # LLM manager tests
├── test_llm_providers.py            # LLM provider tests
├── test_model_selection.py          # Model selection + streaming metrics (8 tests)
└── test_streaming_metrics.py        # StreamingMetrics tok/s tracking (14 tests)
```

---

## Test Commands

```bash
# Run all tests
uv run pytest tests/ tests_sandbox/ -v

# Run sandbox tests only
uv run pytest tests_sandbox/ -v

# Run unit tests only
uv run pytest tests/unit -q

# Run integration tests only
uv run pytest tests/integration -q

# Run specific test
uv run pytest tests_sandbox/test_chat_loop.py::TestChatLoopInitialization -v

# Run tests matching pattern
uv run pytest tests_sandbox/ -k "streaming" -v
```
