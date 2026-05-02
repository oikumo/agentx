# Project Overview - Agent-X

> **Version**: 0.2.0  
> **Last Updated**: April 2026  
> **Python**: 3.14+  
> **Package Manager**: uv

---

## What is Agent-X?

Agent-X is a Python-based LLM agent framework with a REPL (Read-Eval-Print Loop) interface. It enables users to interact with various language models through command-line commands, supporting multiple interaction patterns:

- **Simple Chat**: Basic conversational interface
- **RAG with PDFs**: Document retrieval and question answering
- **ReAct Web Search**: Reasoning and acting with web search capabilities
- **Graph-based Workflows**: Complex multi-step reasoning workflows

---

## Architecture

Agent-X follows the **MVC (Model-View-Controller)** architectural pattern:

### Model Layer (`src/model/`)
- Data persistence with SQLite
- Session lifecycle management
- Command history tracking

### View Layer (`src/views/`)
- Chat interface with streaming support
- Main application UI
- Shared console utilities

### Controller Layer (`src/controllers/`)
- Command routing and parsing
- Business logic implementation
- REPL integration

### Service Layer (`src/services/`)
- AI/LLM service orchestration
- Provider strategy pattern (OpenAI, Google, Ollama, LlamaCpp)
- Vector store integrations (ChromaDB, Pinecone)

### Common (`src/common/`)
- Shared utilities
- Security constants
- Helper functions

---

## Application Flow

```
User Input (REPL)
    ↓
Command Parser (Controller)
    ↓
Command Handler (Controller)
    ↓
Service Layer (AI/LLM)
    ↓
LLM Provider (Strategy Pattern)
    ↓
Response → View Layer → User
```

---

## Design Patterns

### Strategy Pattern
Used for LLM provider selection, allowing runtime switching between different model providers (OpenAI, Google, Ollama, etc.) without changing the application logic.

### Factory Pattern
LLM provider factory creates appropriate provider instances based on configuration.

### Singleton Pattern
Session management and database connections use singleton patterns for resource efficiency.

---

## Key Decisions

1. **MVC Architecture**: Chosen for clear separation of concerns and testability
2. **SQLite for Persistence**: Lightweight, file-based, no external dependencies
3. **Strategy Pattern for LLM Providers**: Enables easy provider switching
4. **uv as Package Manager**: Fast, modern Python package management
5. **Tests Sandbox**: Isolated environment for feature testing before migration to main test suite

---

## Project Structure

```
agent-x/
├── main.py                 # Application entry point
├── pyproject.toml          # Project configuration
├── .project_development/   # Meta documentation
├── src/                    # Source code (MVC)
├── tests/                  # Unit tests (read-only)
├── tests_sandbox/          # Feature tests
├── doc/                    # Documentation
└── _resources/             # Sample data files
```
