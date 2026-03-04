# AGENTS.md - Agent-X Development Guide

## Overview

Agent-X is a Python app for assisting with programming, built on LangChain and LangGraph.

## Project Structure

```
agent-x/
├── agent_x/           # Main application code
├── tests/            # Test suite
├── main.py           # Entry point
└── pyproject.toml    # Project configuration
```

## Build, Lint, and Test Commands

### Package Management (uv)

```bash
# Install dependencies
uv sync

# Add dependencies
uv add <package>

# Add dev dependencies
uv add --group dev <package>
```

### Running the Application

```bash
# Run main application
python main.py

# Or via uv
uv run python main.py
```

### Testing

Run all tests:
```bash
pytest
```

Run a single test:
```bash
pytest tests/app/agent_x_test.py::AgentXTest::test_run
pytest tests/app/agent_x_test.py -k "test_run"
```

### Code Formatting

Format all (black + isort):
```bash
isort . && black .
```

### Type Checking

Python 3.13+ with type hints. No explicit type checker configured.

---

## Code Style Guidelines

### General Principles

- **Python Version**: Requires Python >= 3.13
- **Type Hints**: Use type hints for all function parameters and return types
- **Documentation**: Use docstrings for public functions and classes

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `AgentX`, `ReplApp`)
- **Functions/Variables**: `snake_case` (e.g., `run()`, `llms`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `COLORS`)
- **Files**: `snake_case.py`

### Imports

- Use absolute imports from the `agent_x` package
- Group imports: standard library, third-party, local application
- Use `isort` for automatic import sorting

### Formatting

- **Line Length**: Default (88 characters via black)
- Run `isort . && black .` before committing

### Error Handling

- Use appropriate exception types
- Provide meaningful error messages
- Use the logging utilities in `agent_x/common/logger.py`:
  - `log_info()` - General information
  - `log_success()` - Success messages
  - `log_error()` - Error messages
  - `log_warning()` - Warning messages
  - `log_header()` - Section headers

### Data Classes

Use `@dataclasses.dataclass` for simple data containers:

```python
import dataclasses

@dataclasses.dataclass
class Config:
    api_key: str
    model: str = "gpt-4"
```

### Testing

- Use `unittest.TestCase` for test classes
- Place tests in the `tests/` directory mirroring the source structure
- Test file naming: `<module>_test.py`

Example:
```python
import unittest

from agent_x.app.agent_x import AgentX

class AgentXTest(unittest.TestCase):
    def test_run(self):
        agentx = AgentX()
        agentx.run()
```

### LangChain/LangGraph Patterns

Use the `@tool` decorator for custom tools:
```python
from langchain.tools import tool

@tool
def get_text_length(text: str) -> int:
    """Return the length of a text by characters."""
    return len(text)
```

### Environment Variables

- Use `python-dotenv` for loading `.env` files
- Never commit secrets; use `.env` files (already gitignored)
- Required variables: `OPENAI_API_KEY`, `TAVILY_API_KEY`, `PINECONE_API_KEY`

### Dependencies

- Add production dependencies to `dependencies` in `pyproject.toml`
- Add dev dependencies (like pytest) to the `dev` dependency group

---

## Development Workflow

1. Activate the virtual environment: `source .venv/bin/activate`
2. Make changes to code
3. Run formatting: `isort . && black .`
4. Run tests: `pytest`
5. Test manually: `python main.py`
