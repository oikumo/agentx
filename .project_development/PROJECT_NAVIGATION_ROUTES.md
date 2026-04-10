# Project Navigation Routes - Agent-X

> **Last Updated**: April 10, 2026
> **Version**: 0.2.0
> **Python**: 3.14+
> **Package Manager**: uv

---

## Project Overview

Agent-X is a Python-based LLM agent framework with a REPL (Read-Eval-Print Loop) interface. It enables users to interact with various language models through command-line commands, supporting multiple interaction patterns: simple chat, function calling, RAG with PDFs, ReAct web search, and graph-based reasoning workflows.

---

## Module Index

| Module | Files | Description |
|--------|-------|-------------|
| [src/common/](#srccommon) | 4 | Shared utilities and security |
| [src/controllers/](#srccontrollers) | 2 | Command routing and controllers |
| [src/model/](#srcmodel) | 5 | Data persistence, SQLite, session management |
| [src/services/](#srcservices) | 3 | AI/LLM service layer with providers |
| [src/views/](#srcviews) | 3 | User interface components |

---

## src/common/

**Path**: `src/common/`

| File | Description |
|------|-------------|
| `utils.py` | General utilities, safe_int, console clearing, directory management |
| `security.py` | Security constants and deletion safeguards |
| `__init__.py` | Package initialization |

---

## src/controllers/

**Path**: `src/controllers/`

| Submodule | Description |
|-----------|-------------|
| `chat_controller/` | Handles chat-specific commands |
| `main_controller/` | Core command registry and REPL integration |
| `__init__.py` | Package initialization |

---

## src/model/

**Path**: `src/model/`

| Submodule | Description |
|----------|-------------|
| `db/` | SQLite session database implementation |
| `session/` | Session lifecycle management |
| `__init__.py` | Package initialization |

---

## src/services/

**Path**: `src/services/`

| Submodule | Description |
|-----------|-------------|
| `ai/` | LLM providers (OpenAI, OpenRouter, LlamaCpp) and vectorstore integrations |
| `__init__.py` | Package initialization |

---

## src/views/

**Path**: `src/views/`

| Submodule | Description |
|-----------|-------------|
| `chat_view/` | Chat UI and loop |
| `main_view/` | Main application UI |
| `common/` | Shared view utilities (console output) |
| `__init__.py` | Package initialization |

---

## Meta

**Path**: `/.project_development/`

| File | Description |
|------|-------------|
| `CORE_DIRECTIVES.md` | Non-negotiable system agent rules |
| `TOOL_USAGE.md` | Tool selection & usage guidelines |
| `CODING_STYLE.md` | Code conventions & naming |
| `TASK_WORKFLOW.md` | Step-by-step task process |
| `ENVIRONMENT.md` | Runtime & operational notes |
| `CURRENT_ISSUE.md` | Currently tracked issues |
| `PROJECT_ROADMAP.md` | Planned features |
| `PROJECT_TESTING_SANDBOX_RULES.md` | TDD strategy |
| `PROJECT_DOCUMENTATION.md` | Full documentation map |
| `PROJECT_NAVIGATION_ROUTES.md` | This file - project navigation routes |
| `USER_COMMAND_EXTENSION.md` | Extended user commands documentation |

---

## Architecture

**Current Version**: v0.2.0 - MVC Architecture (April 2026)

- **Model** (`src/model/`): Data persistence, SQLite, session management
- **View** (`src/views/`): User interface components (chat view, main view)
- **Controller** (`src/controllers/`): Business logic and command routing
- **Services** (`src/services/`): AI/LLM service layer with providers and vectorstores
- **Common** (`src/common/`): Shared utilities and security helpers
