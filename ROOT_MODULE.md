# Root Module - Agent-X

## Overview
Entry point for the Agent-X application. Contains the main executable and package initialization.

## Key Files

| File | Description |
|------|-------------|
| `main.py` | Application entry point. Creates `MainController`, registers all commands, and launches `ReplApp`. |
| `__init__.py` | Package initialization (empty). |
| `pyproject.toml` | Project configuration, dependencies, and metadata. |

## Application Flow
```
main.py → create_controller() → register commands → ReplApp(controller).run()
```

## Registered Commands
- **CLI**: `quit`, `clear`, `help`, `read`
- **Math**: `sum`
- **LLM Chat**: `chat`, `router`, `react`, `search`, `function`, `rag`
- **LLM Graph**: `graph`, `chains`, `reflex`
