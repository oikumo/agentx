# AGENTS.md - Agent-X Development Guidelines

This file documents build, lint, and test commands for agentic coding agents working in the Agent-X repository, plus code style conventions and project-specific guidelines.

---

## Build, Lint, and Test Commands

- Install dependencies (local environment):
  - uv sync  # installs/updates project dependencies defined in pyproject.toml
  - python -m venv .venv
  - source .venv/bin/activate  # on Unix-like systems
  - pip install --upgrade pip
  - pip install .  # if packaging needed

- Basic verification (lint + tests):
  - black . && isort .
  - uv run pytest tests -v

- Linting and formatting (no auto-fix):
  - black --check .
  - isort --check .

- Auto-fix formatting (when allowed):
  - black .
  - isort .

- Run a single test (recommended pattern):
  - pytest tests/path/to/test_file.py::TestClass::test_function_name -q
  - pytest tests/path/to/test_file.py::TestClass -q  # all tests in class
  - pytest tests/path/to/test_file.py -k "pattern" -q  # subset by name

- Run unit tests only:  
  - pytest tests/unit -q

- Run integration tests only:
  - pytest tests/integration -q

- Run all tests with verbose output and HTML coverage report:
  - pytest tests --cov=agent_x --cov-report=html -v

- Build artifacts (distribution):
  - python -m build  # if python-build tool is configured

- Quick smoke check (no network calls):
  - pytest tests/unit -k smoke -q

---

## Code Style Guidelines

### General
- Language: Python 3.13+; type hints preferred where beneficial.
- Line length: 88 characters (Black default).
- Docstrings: Google-style for public functions/classes.
- Tests: mirror source structure; unit tests focus on pure logic; integration tests cover end-to-end flows.

### Imports
- Use isort for sorting and grouping:
  - Standard library imports
  - Third-party imports
  - Local/application imports
- Always import at module level; avoid shadowing built-ins.
- Prefer explicit relative imports within package boundaries where clear.

Example structure:

```
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
- Functions/variables: snake_case
- Classes: PascalCase
- Constants: UPPER_SNAKE_CASE
- Private members: _prefix
- Modules/files: snake_case.py

### Typing & API Boundaries
- Use TypeVar, Protocols, and typing where appropriate.
- Return types should be explicit; avoid `-> Any` unless necessary.
- Use Optional[T] for values that may be None; document non-None assumptions in docstrings.

### Error Handling
- Define domain-specific exceptions; catch specific exceptions, not bare except.
- Log errors before re-raising or returning error values.
- Use meaningful error messages that aid debugging; avoid leaking secrets.

Example:
```
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
- Prefer async/await for I/O-bound operations.
- Avoid blocking calls in async functions.
- Use asyncio.gather() for concurrent tasks when appropriate.

### LangChain/LangGraph Patterns
- Use langgraph for agent state management; prefer with_structured_output().
- Consider token and rate-limit handling; design for retries.
- Rely on LangChain retry mechanisms where available.

### Testing Guidelines
- Tests live under tests/ mirroring source layout.
- Use pytest with descriptive names: test_<behavior>_<condition>_<outcome>.
- Prefer fixtures for shared setup; avoid heavy per-test mocks.
- Mock external calls; minimize test fragility.
- Ensure tests are independent; avoid ordering dependencies.

---

## Cursor and Copilot Rules (If Present)

- Cursor rules: None detected under .cursor/rules/ or .cursorrules at this time.
- Copilot instructions: None detected in .github/copilot-instructions.md.

If these files are added later, include a short summary here and link to their rules.

---

## Configuration and Environment Conventions

- Environment variables should live in .env and not be committed.
- Use python-dotenv for loading env vars where applicable.
- Dependency management via pyproject.toml and uv tooling; avoid pin drift.
- Pre-commit hooks: consider enabling for consistent formatting and linting.

```
Notes:
- The repository currently relies on Black and isort for formatting. Other tools may be added; update AGENTS.md accordingly.
```
