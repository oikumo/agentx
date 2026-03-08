# AGENTS.md - Agent-X Development Guide

## Project Overview

Agent-X is a Python project using LangChain, LangGraph, and various LLM integrations. It requires Python 3.13+.

---

## Commands

### Running the Application

```bash
# Run main.py
python main.py

# Or using the virtual environment
./.venv/bin/python main.py
```

### Application Types

Agent-X supports three application modes defined in `AppType`:

| Type | Description |
|------|-------------|
| `REPL` | Interactive command-line interface (default) |
| `CHAT` | Streamlit-based chat UI |
| `WEB_INGESTION` | Web document ingestion pipeline |

**Currently in `AgentX.run()`:** The app type is hardcoded to `ReplApp()`. To select different apps, configure `AgentXConfiguration` and update `run()`:

```python
# In agent_x/app/agent_x.py
from agent_x.applications.repl_app.replapp import ReplApp
from agent_x.applications.chat_app.chat_app import ChatApp
from agent_x.applications.web_ingestion_app.web_ingestion_app import WebIngestionApp

def run(self):
    match self.configuration.app:
        case AppType.REPL:
            app = ReplApp()
        case AppType.CHAT:
            app = ChatApp()
        case AppType.WEB_INGESTION:
            # Requires vectorstore and tav setup
            app = WebIngestionApp(vectorstore=..., tav=...)
    app.run()
```

### Testing

```bash
# Run all tests
uv run pytest tests/ -v

# Run unit tests only
uv run pytest tests/unit/ -v

# Run integration tests only
uv run pytest tests/integration/ -v

# Run a single test file
uv run pytest tests/path/to/test_file.py -v

# Run a single test function (specify file::function)
uv run pytest tests/path/to/test_file.py::TestClass::test_function_name -v

# Run tests matching a pattern
uv run pytest tests/ -k "test_pattern" -v

# Run with coverage
uv run pytest tests/ --cov=agent_x --cov-report=html
```

### Linting & Formatting

```bash
# Run all linters and formatters
black .
isort .

# Check formatting without applying changes
black --check .
isort --check .

# Sort imports only
isort .
```

---

## Code Style Guidelines

### General Rules

- **Python version**: 3.13+
- **Type hints**: Always use type hints for function signatures and variables when beneficial
- **Docstrings**: Use Google-style docstrings for public functions
- **Line length**: 88 characters (Black default)

### Imports

- Use `isort` for automatic import sorting
- Order: stdlib → third-party → local/application
- Group: imports → from imports → explicit re-exports
- Example:
  ```python
  import os
  import sys
  from pathlib import Path
  from typing import Any, Optional
  
  import pytest
  from langchain_core.messages import BaseMessage
  
  from agent_x.app import some_module
  from agent_x.common import utils
  ```

### Naming Conventions

- **Functions/variables**: `snake_case` (e.g., `get_user_data`, `max_retries`)
- **Classes**: `PascalCase` (e.g., `AgentRunner`, `SessionManager`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_TOKENS`, `DEFAULT_TIMEOUT`)
- **Private members**: Prefix with underscore (e.g., `_internal_method`)
- **Files**: `snake_case.py`

### Error Handling

- Use custom exceptions for domain-specific errors
- Catch specific exceptions, avoid bare `except:`
- Always log errors before re-raising or returning error values
- Example:
  ```python
  try:
      result = await agent.run(input_data)
  except ValidationError as e:
      logger.warning(f"Invalid input: {e}")
      raise
  except APIError as e:
      logger.error(f"API failed: {e}")
      raise AgentError(f"Agent execution failed: {e}") from e
  ```

### Async Code

- Use `async`/`await` for I/O-bound operations
- Avoid blocking calls in async functions
- Use `asyncio.gather()` for concurrent operations when appropriate

### LangChain/LangGraph Patterns

- Use `langgraph` for agent state management and workflows
- Prefer structured output with `with_structured_output()`
- Handle token limits and API rate limits gracefully
- Use langchain's built-in retry mechanisms

### Testing Guidelines

- Place tests in `tests/` directory mirroring the source structure
- Use `pytest` with descriptive test names: `test_<function>_<expected_behavior>`
- Use fixtures for shared test setup
- Mock external API calls; use `pytest-mock` or `unittest.mock`
- Keep tests independent; avoid test order dependencies

---

## Configuration System

The project uses a configuration system located in `agent_x/app/configuration/`.

### AgentXConfiguration

```python
from agent_x.app.agent_x import AgentX
from agent_x.app.configuration.configuration import (
    AgentXConfiguration,
    AppType,
    LLMProvider,
    configure_agentx,
)

# Create configuration
config = AgentXConfiguration(
    app=AppType.CHAT,           # REPL, CHAT, WEB_INGESTION
    default_model="gpt-4",
    debug=True,
    session_directory="sessions"
)

# Add models
config.add_model("gpt-4", LLMProvider.OPENAI, temperature=0.7)
config.add_model("llama-3", LLMProvider.OLLAMA, temperature=0.5)

# Get models
model = config.get_model("gpt-4")
default = config.get_default_model()

# Configure AgentX
agentx = AgentX()
configure_agentx(config, agentx)
```

### Enums

- **AppType**: `REPL`, `CHAT`, `WEB_INGESTION`
- **LLMProvider**: `OPENAI`, `OLLAMA`, `ANTHROPIC`

### LLMModel Settings

- `name`: Model name
- `provider`: LLM provider enum
- `temperature`: 0.0 to 2.0 (default 0.7)
- `max_tokens`: Maximum tokens (default 2048)

---

## Project Structure

```
agent-x/
├── agent_x/                  # Main application code
│   ├── app/                  # Core app components
│   │   ├── agent_x.py        # Main AgentX class
│   │   └── configuration/    # Configuration system
│   ├── applications/         # App implementations
│   │   ├── chat_app/         # Chat UI
│   │   ├── repl_app/         # REPL interface
│   │   │   ├── command_line_controller/  # Command parsing and dispatch
│   │   │   ├── commands/                 # Command implementations
│   │   │   └── tui/                      # Textual TUI implementation
│   │   │       ├── app.py                # TextualReplApp main app
│   │   │       ├── output_writer.py      # TuiOutputWriter callback
│   │   │       └── widgets/              # CommandInput, OutputPane, StatusBar
│   │   └── web_ingestion_app/# Web ingestion
│   ├── common/               # Shared utilities (incl. logger with handler indirection)
│   ├── llm_models/           # LLM integrations
│   ├── modules/              # Reusable modules
│   │   ├── data_stores/      # Data storage
│   │   ├── document_loaders/# Document handling
│   │   ├── llm/              # LLM utilities
│   │   └── vector_store/     # Vector stores
│   ├── user_sessions/        # Session management
│   └── utils/                # Utility functions
├── tests/                    # Test suite
│   ├── unit/                 # 208 unit tests (all passing)
│   └── integration/          # Integration tests
├── scripts/                  # Helper scripts
├── resources/                # Static resources
├── local/                    # Local development files
└── .venv/                    # Virtual environment
```

---

## Environment

- Environment variables are stored in `.env` (do not commit secrets)
- Use `python-dotenv` for loading environment variables
- Required variables: API keys for LLM providers (OpenAI, Ollama, Tavily, Pinecone, etc.)

---

## Dependencies

- Managed via `pyproject.toml` and `uv.lock`
- Install dependencies: `uv sync`
- Main deps: langchain, langgraph, langchain-community, textual, streamlit, chromadb, pydantic

---

## Textual TUI (REPL)

The REPL application uses the [Textual](https://textual.textualize.io/) framework
for a full-screen terminal UI. The implementation lives in
`agent_x/applications/repl_app/tui/`.

### Components

| Component | File | Purpose |
|-----------|------|---------|
| `TextualReplApp` | `tui/app.py` | Main Textual app; orchestrates layout and worker threads |
| `CommandInput` | `tui/widgets/command_input.py` | Input field with autocomplete and command history |
| `OutputPane` | `tui/widgets/output_pane.py` | Scrollable RichLog for command output |
| `StatusBar` | `tui/widgets/status_bar.py` | Displays current command status |
| `TuiOutputWriter` | `tui/output_writer.py` | Callback that redirects logger output to the TUI |

### Key design decisions

- **Worker threads** — Commands run in Textual workers so the UI never blocks.
- **Logger handler indirection** — `logger.py` exposes `get_handler()` /
  `set_handler()` so the TUI can redirect output without monkey-patching.
- **ASCII-only icons** — No emoji; all icons use ASCII characters for broad
  terminal compatibility.

---

## IDE Integration

- VS Code tasks defined in `.vscode/tasks.json`
- Python interpreter: `./.venv/bin/python`
- Recommended extensions: Python, Pylance, Ruff (or Black/ISort)

---

## Unit Testing — Learned Knowledge and Forward Strategy

> "The goal of testing is not to show that tests pass. The goal is to have tests
> that give you the confidence to change the code." — Kent Beck

This section captures concrete lessons learned while building the 208-test suite
for Agent-X, and a forward strategy for the rest of the project.
Read it before writing a new test. Read it again when a test feels hard to write —
that difficulty is a design signal.

---

### Part 1: What We Learned (Lessons from the REPL test sprint)

#### 1.1 Tests reveal bugs that reviews miss

Writing tests is not a verification step after coding — it is a second reading
of the code that catches things the first reading missed. During this sprint,
tests uncovered two real production bugs:

- **`CommandLine.run()` — unbound local after mocked exit.**
  The exception handlers called `exit()` but did not `return`. In production
  `exit()` raises `SystemExit`, so execution never continued. When `exit` is
  mocked (as in every test), execution fell through to `command_entry`, which
  was unbound. The fix (`return` after each `exit()` call) makes the code
  correct in both contexts. The test did not introduce the requirement — it
  revealed an existing fragility.

- **`SumCommand` — zero is falsy.**
  `if safe_int(x) and safe_int(y)` silently rejects `"0"` as an operand
  because `int("0") == 0` is falsy. The guard should be
  `if safe_int(x) is not None and safe_int(y) is not None`. The bug is
  documented in `math_commands_test.py` with explicit regression tests so it
  cannot be fixed without the tests being updated intentionally.

- **`CommandsController` — shared class-level dict.**
  An earlier bug had commands stored at the class level (shared across all
  instances). A test that creates two controllers and asserts their independence
  catches this immediately and cheaply. The fix is one line; the test is
  permanent protection.

**Rule:** When a test is hard to write because of a mocking gymnastics problem,
stop and ask whether the production code is making untestable assumptions.
Often, fixing the code is the right answer.

#### 1.2 Patch at the import site, not the definition site

When mocking, always patch the name as it is seen by the module under test,
not where it is originally defined.

```python
# WRONG — patches the logger module, not the reference in cli_commands
patch("agent_x.common.logger.log_info")

# CORRECT — patches the name that cli_commands.py actually calls
patch("agent_x.applications.repl_app.commands.cli_commands.log_info")
```

Every mock target in this project follows the pattern:
`"<dotted.path.to.module.under.test>.<name_used_in_that_module>"`.

#### 1.3 Infinite loops must be broken, not avoided

`ReplApp.run()` contains `while True: loop.run()`. The test cannot skip it.
The clean solution is to make the mock raise a sentinel exception after N calls:

```python
mock_loop.run.side_effect = StopIteration
with self.assertRaises(StopIteration):
    app.run()
```

This approach also lets you assert how many iterations ran — which is itself
a behavioural claim worth making.

#### 1.4 Stub helpers belong at the top of the test file

Every test file that exercises an abstract class needs a concrete stub
(`FakeCommand`, `ConcreteController`, etc.). These stubs:

- Live at module level, above the test class.
- Have a docstring explaining *why* they exist (not just what they are).
- Do the minimum necessary to satisfy the ABC — no extra logic.
- Are never shared across test files (copy the stub if you need it elsewhere;
  shared stubs create hidden coupling between test files).

#### 1.5 `setUp` is for state, not for decisions

`setUp` creates the object under test. It does not decide which mock to use,
which path to exercise, or what arguments to pass. Those are test-method
responsibilities. A `setUp` that is getting complex is a sign the test class
is testing too many things at once — split it.

#### 1.6 Document known bugs as first-class tests

When a known bug cannot be fixed immediately (e.g., the `SumCommand` zero
bug), write a test that asserts the current broken behaviour and name it
explicitly:

```python
def test_run_zero_as_first_argument_is_treated_as_invalid_due_to_bug(self):
    # BUG: safe_int("0") returns 0 (falsy). Guard should use `is not None`.
    # This test documents the existing behaviour. Update it when the bug is fixed.
    ...
```

This is far better than leaving the test out. It means the bug cannot be
accidentally "fixed" by an unrelated change that restores the wrong behaviour,
and it gives the next developer immediate context.

#### 1.7 LLM wrapper commands are not worth unit-testing

Classes like `AIChat`, `AITools`, `AISearch`, etc. are single-line delegations
to LangChain/LangGraph. Testing them at the unit level would test only Python's
import system and LangChain's own internals — neither of which is our
responsibility. Skip them. Cover them at the integration/e2e level when LLM
calls are exercised end-to-end with real or recorded responses.

#### 1.8 The test structure mirrors the source structure

```
agent_x/applications/repl_app/commands/cli_commands.py
→ tests/app/cli_commands_test.py

agent_x/applications/repl_app/command_line_controller/command_parser.py
→ tests/app/command_parser_test.py
```

This 1:1 mapping means any developer can find the tests for a file instantly.
Do not create "mega test files" that cover multiple source modules.

---

### Part 2: Forward Strategy

#### 2.1 The testing pyramid for Agent-X

```
         /\
        /  \   E2E / Integration
       /    \  (LLM calls, Streamlit UI, vector DB)
      /------\
     /        \ Component tests
    /          \ (REPL loop, session lifecycle, config pipeline)
   /------------\
  /              \ Unit tests  ← where we are now
 /________________\ (pure logic, no I/O, fully mocked)
```

The bulk of the test suite must live at the bottom. Unit tests are cheap,
fast, and precise. Integration tests are valuable but expensive. E2E tests
catch what nothing else does, but they are slow and brittle — keep them few.

#### 2.2 The three questions before writing any test

1. **What behaviour am I specifying?**
   Name the test after the behaviour, not the method.
   `test_run_warns_on_no_arguments` is better than `test_run_with_empty_list`.

2. **What is the smallest unit that exhibits this behaviour?**
   If the answer involves more than one real class, consider a narrower test
   or a dedicated component test.

3. **How will this test fail?**
   Write the assertion first (even if the code does not exist yet). A test
   that cannot fail in a meaningful way is not a test — it is a comment.

#### 2.3 Coverage targets by layer

| Layer | Target | Notes |
|---|---|---|
| Pure logic (utils, parsers, dataclasses) | 100% branch | No excuse to miss any branch here |
| Command classes (non-LLM) | 100% line | Mock I/O, assert on logger calls |
| Controller / dispatcher classes | 90%+ | Focus on dispatch table correctness |
| LLM wrapper commands | 0% unit | Covered at integration level only |
| UI / Streamlit | 0% unit | Snapshot/e2e only |
| TUI / Textual widgets | 0% unit | Covered at integration/e2e level via Textual's pilot API |
| Configuration system | 100% line | Already achieved; maintain it |

#### 2.4 What to write next (priority order)

The following areas have no unit tests yet. Tackle them in this order:

1. ✅ **`WebIngestionApp` pipeline** — DONE (39 tests covering helpers,
   documents, tavily, and web_ingestion_app modules)

2. ✅ **`Session.create()` error path** — DONE (covers post-mkdir failure branch)

3. ✅ **`AgentXConfiguration` edge cases** — DONE (get_default_model returns None
   when model not added)

4. ✅ **`configure_agentx()` failure paths** — DONE (None agentx raises
   AttributeError, empty config returns True)

5. ❌ **`CommandParser._tokenize_arguments()`** — Currently dead code (never
   called). Write a test that calls it directly to confirm its output, then
   decide whether to integrate or delete it.

6. **LLM module integration tests** — Once a test fixture exists that can
   replay recorded LangChain responses (via `langsmith` or a cassette library),
   add integration tests for `AIChat`, `AITools`, and `RagPDF`. Do not write
   these as unit tests.

7. **App type selection** — Document and test the `AgentX.run()` method's
   ability to dispatch to different app types (REPL, CHAT, WEB_INGESTION)
   based on `configuration.app`.

8. **TUI integration tests** — Use Textual's `App.run_test()` pilot API to
   drive the TUI headlessly. Verify that typing a command produces expected
   output in the OutputPane, and that autocomplete/history work.

9. **TUI widget unit tests** — Lightweight tests for `CommandInput`,
   `OutputPane`, `StatusBar` in isolation if complex logic is added to them.

#### 2.5 Test naming convention (canonical form)

```
test_<method_or_behaviour>_<condition>_<expected_outcome>
```

Wrap tests in `<ClassName>Test` classes using `unittest.TestCase`:

```python
class SessionTest(unittest.TestCase):
    def test_create_raises_exception_when_directory_not_found_after_mkdir(self):
        ...
```

Examples from this codebase:
- `test_run_warns_on_no_arguments` ✓
- `test_find_command_returns_none_for_unknown_key` ✓
- `test_two_instances_do_not_share_state` ✓
- `test_run` ✗ (too vague — says nothing about condition or outcome)
- `test_it_works` ✗ (communicates nothing)

#### 2.6 The mock budget rule

A test that needs more than **3 mocks** is testing too large a unit or the
production code has too many direct dependencies. When you reach for a fourth
mock, stop. Either:

- Break the production class into smaller pieces (prefer this), or
- Write a component test that uses real collaborators instead.

The REPL tests in this project consistently use 1–2 mocks per test. That is
the target.

#### 2.7 Red–Green–Refactor in the context of an existing codebase

For new features, always follow the cycle strictly:

1. **Red** — Write a failing test first. Commit it if working with a team.
2. **Green** — Write the minimum code to make it pass. No extra logic.
3. **Refactor** — Clean up both the test and the production code under green.

For existing untested code (legacy), use a lighter variant:

1. Read the code and form a hypothesis about its intended behaviour.
2. Write a test that encodes the hypothesis.
3. Run it. If it passes, the hypothesis is confirmed. If it fails, you found
   a bug or a misread — investigate before writing more tests.

Never write tests and production code simultaneously when adding new
functionality. The cognitive load of holding both in mind at once leads to
tests that are not independent specifications — they are just transcriptions
of the code you just wrote.

#### 2.8 Fixtures and helpers — shared vs. local

| Scope | Mechanism | When to use |
|---|---|---|
| Single test method | Local variable | Default choice |
| All methods in one test class | `setUp` | State shared by all cases in the class |
| All tests in one file | Module-level helper function | Stub factories, `_make_*` helpers |
| Across multiple test files | `conftest.py` fixture | Only when duplication is painful AND the fixture is stable |

There is currently no `conftest.py` in this project. Do not create one
until at least three test files share the same setup logic. Premature
`conftest.py` entries become invisible dependencies that surprise readers.

#### 2.9 Regression tests are permanent

When a bug is fixed, the test that caught it stays forever. Never delete a
regression test because "we fixed the bug." The test is now protection against
the bug returning. If the test name makes the original bug clear
(`test_run_zero_as_first_argument_is_treated_as_invalid_due_to_bug`), update
the name when the fix is applied — but keep the test.

#### 2.10 The confidence check

Before committing, ask: "If I deleted this feature entirely, would at least
one test fail?" If the answer is no, the feature is untested regardless of
how many green tests exist. This is the simplest way to audit a test suite
without coverage tooling.
