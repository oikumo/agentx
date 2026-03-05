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

### Testing

```bash
# Run all tests
pytest

# Run a single test file
pytest tests/app/

# Run a single test function (specify file::function)
pytest tests/app/test_file.py::test_function_name

# Run tests matching a pattern
pytest -k "test_pattern"

# Run with verbose output
pytest -v

# Run with coverage (if installed)
pytest --cov=agent_x --cov-report=html
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
│   │   └── web_ingestion_app/# Web ingestion
│   ├── common/               # Shared utilities
│   ├── llm_models/           # LLM integrations
│   ├── modules/              # Reusable modules
│   │   ├── data_stores/      # Data storage
│   │   ├── document_loaders/# Document handling
│   │   ├── llm/              # LLM utilities
│   │   └── vector_store/     # Vector stores
│   ├── user_sessions/        # Session management
│   └── utils/                # Utility functions
├── tests/                    # Test suite
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

- Managed via `pyproject.toml`
- Install dev dependencies: `pip install -e ".[dev]"` (if configured)
- Main deps: langchain, langgraph, langchain-community, streamlit, chromadb, pydantic

---

## IDE Integration

- VS Code tasks defined in `.vscode/tasks.json`
- Python interpreter: `./.venv/bin/python`
- Recommended extensions: Python, Pylance, Ruff (or Black/ISort)
