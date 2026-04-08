# Project Documentation - Agent-X

> **Last Updated**: April 8, 2026
> **Version**: 0.2.0
> **Python**: >=3.14
> **Package Manager**: uv

Agent-X is a Python‑based LLM application framework with an MVC architecture. This file serves as a **navigation map** to the detailed documentation stored in the `doc/` folder, and to auxiliary reference files such as command guides and testing rules.

---

## Documentation Index

_This section lists the primary documentation files. Click a link to open the detailed markdown for that area._

| File | Domain | Description |
|------|--------|-------------|
| [doc/overview.md](doc/overview.md) | Project | Overview, architecture, application flow, design patterns, key decisions |
| [doc/root_module.md](doc/root_module.md) | Root | `main.py`, `pyproject.toml`, `README.md` |
| [doc/model.md](doc/model.md) | Model | Data persistence, sessions, SQLite database, command history |
| [doc/views.md](doc/views.md) | Views | View layer: chat interface, main application view |
| [doc/controllers.md](doc/controllers.md) | Controllers | Business logic and command routing |
| [doc/services.md](doc/services.md) | Services | Service layer: AI/LLM services |
| [doc/common.md](doc/common.md) | Common | Shared utilities across the application |
| [doc/tests.md](doc/tests.md) | Tests | Unit test suite, test commands |
| [tests_sandbox/tests_sandbox.md](tests_sandbox/tests_sandbox.md) | Tests Sandbox | Feature and integration testing sandbox documentation |
| [.project_development/CORE_DIRECTIVES.md](.project_development/CORE_DIRECTIVES.md) | Core Rules | Non-negotiable system agent rules |
| [.project_development/TOOL_USAGE.md](.project_development/TOOL_USAGE.md) | Tool Usage | Tool selection & usage guidelines |
| [.project_development/CODING_STYLE.md](.project_development/CODING_STYLE.md) | Coding Style | Code conventions & naming |
| [.project_development/TASK_WORKFLOW.md](.project_development/TASK_WORKFLOW.md) | Task Workflow | Step-by-step task process |
| [.project_development/ENVIRONMENT.md](.project_development/ENVIRONMENT.md) | Environment | Runtime & operational notes |
| [.project_development/PROJECT_TESTING_SANDBOX_RULES.md](.project_development/PROJECT_TESTING_SANDBOX_RULES.md) | Testing Rules | TDD strategy and Kent Beck-style rules for AI agents |
| [.project_development/CURRENT_ISSUE.md](.project_development/CURRENT_ISSUE.md) | Meta | Currently tracked issues and their status |
| [.project_development/PROJECT_ROADMAP.md](.project_development/PROJECT_ROADMAP.md) | Roadmap | Planned features and improvements |
| [doc/dependencies.md](doc/dependencies.md) | Configuration | Dependencies table, environment variables, quick start, code style |
| [.project_development/USER_COMMAND_EXTENSION.md](.project_development/USER_COMMAND_EXTENSION.md) | Commands | Simplified, powerful LLM‑agent command reference |


---

## Module Structure

```
agent-x/
├── main.py # Application entry point
├── pyproject.toml # Project configuration, dependencies
├── .project_development/ # Project meta and rules files
│ ├── CORE_DIRECTIVES.md # Non-negotiable system agent rules
│ ├── TOOL_USAGE.md # Tool selection & usage guidelines
│ ├── CODING_STYLE.md # Code conventions & naming
│ ├── TASK_WORKFLOW.md # Step-by-step task process
│ ├── ENVIRONMENT.md # Runtime & operational notes
│ ├── CURRENT_ISSUE.md # Currently tracked issues and fix status
│ ├── PROJECT_DOCUMENTATION.md # This file - documentation map
│ ├── PROJECT_NAVIGATION_ROUTES.md # Navigation routes
│ ├── PROJECT_ROADMAP.md # Planned features and improvements
│ ├── PROJECT_TESTING_SANDBOX_RULES.md # TDD strategy and rules
│ └── USER_COMMAND_EXTENSION.md # Extended user commands
├── src/ # All source code (installed as agent-x package)
│ ├── common/ # Shared utilities and helpers
│ ├── controllers/ # Application controllers (business logic)
│ ├── model/ # Data persistence, SQLite, session management
│ │ ├── db/ # Database layer
│ │ └── session/ # Session lifecycle
│ ├── services/ # Service layer (AI/LLM services)
│ │ └── ai/ # AI service implementations
│ ├── views/ # View layer (user interface)
│ │ ├── chat_view/ # Chat interface
│ │ ├── main_view/ # Main application view
│ │ └── common/ # Shared view utilities
│ └── main.py # Application entry point
├── tests/ # Unit and integration tests (read-only)
├── tests_sandbox/ # Feature and integration testing sandbox
├── _resources/ # Sample data files
└── doc/ # Project documentation
```
agent-x/
├── main.py                          # Application entry point
├── pyproject.toml                   # Project configuration, dependencies
├── .project_development/          # Project meta and rules files
│   ├── CORE_DIRECTIVES.md           # Non-negotiable system agent rules
│   ├── TOOL_USAGE.md                # Tool selection & usage guidelines
│   ├── CODING_STYLE.md              # Code conventions & naming
│   ├── TASK_WORKFLOW.md             # Step-by-step task process
│   ├── ENVIRONMENT.md               # Runtime & operational notes
│   ├── CURRENT_ISSUE.md             # Currently tracked issues and fix status
│   ├── PROJECT_DOCUMENTATION.md     # This file - documentation map
│   ├── PROJECT_NAVIGATION_ROUTES.md # Navigation routes
│   ├── PROJECT_ROADMAP.md           # Planned features and improvements
│   ├── PROJECT_TESTING_SANDBOX_RULES.md # TDD strategy and rules
│   └── USER_COMMAND_EXTENSION.md    # Extended user commands
├── src/                             # All source code (installed as agent-x package)
│   ├── agents/                      # Agent implementations
│   │   ├── chat/                    # SimpleChat, ChatLoop (persistent conversation)
│   │   ├── function_tool_router/    # Query routing with Ollama tool calling
│   │   ├── graph_react_web_search/  # LangGraph-based ReAct web search
│   │   ├── rag_pdf/                 # PDF RAG with FAISS + Ollama embeddings
│   │   └── react_web_search/        # LangChain ReAct web search agent
│   ├── llm_managers/                # Unified AgentFactory + LLM provider strategy
│   │   ├── providers/               # LLM provider implementations (Strategy pattern)
│   │   │   ├── llamacpp_provider.py # Local LLM via llama.cpp
│   │   │   ├── openai_provider.py   # Cloud LLM via OpenAI API
│   │   │   └── openrouter_provider.py # Cloud LLM via OpenRouter
│   │   ├── factory.py               # Unified AgentFactory class
│   │   └── llm_provider.py          # LLMProvider ABC - strategy interface
│   ├── local_mcp/                   # MCP (Model Context Protocol) servers
│   │   ├── mcp_main.py              # MCP server entry point
│   │   └── servers_stdio/           # MCP servers using stdio transport
│   │       └── math_server.py       # Math operations MCP server
│   ├── app/                         # Core application
│   │   ├── common/                  # Shared utilities
│   │   ├── model/                   # Data persistence, sessions, SQLite
│   │   ├── repl/                    # REPL system and commands
│   │   └── security/                # Directory deletion safeguards
│   ├── app_modules/                 # Extended application modules
│   │   ├── data_stores/             # FAISS vector store
│   │   ├── document_loaders/        # PDF loading and chunking
│   │   ├── llm/                     # LangChain and LangGraph integrations
│   │   └── web_ingestion_app/       # Web scraping pipeline
│   ├── llm_models/                  # LLM model providers and vector stores
│   │   ├── cloud/                   # Cloud providers (OpenAI, Google)
│   │   ├── local/                   # Local providers (LlamaCpp, Ollama)
│   │   │   ├── llama_cpp/           # Llama.cpp GGUF models
│   │   │   ├── llama_cpp_factory.py # Pre-configured factory
│   │   │   ├── ollama/              # Ollama chat models
│   │   │   └── ollama_factory.py    # Ollama model manager
│   │   └── vectorstores/            # Vector store integrations
│   │       ├── vectorstore_pinecone.py # Pinecone wrapper
│   │       └── vectorstore_chroma.py   # Chroma wrapper
│   └── main.py                      # Application entry point
├── tests/                           # Unit and integration tests (read-only)
├── tests_sandbox/                   # Feature and integration testing sandbox
├── _resources/                      # Sample data files
└── doc/                             # Project documentation
```

---

## Recent Changes

### Major Architecture Refactor — MVC Pattern (v0.2.0)
- **Date**: April 8, 2026
- **What changed**: Complete architectural reorganization from agent-centric to MVC pattern
- **New structure**:
  - `src/common/` — Shared utilities
  - `src/controllers/` — Business logic and command routing
  - `src/model/` — Data persistence, sessions, SQLite
  - `src/services/` — AI/LLM service layer
  - `src/views/` — User interface layer
- **Removed**: `agents/`, `llm_managers/`, `local_mcp/`, `app/`, `app_modules/`, `llm_models/`
- **Rationale**: Improved maintainability, testability, and adherence to standard application architecture patterns

### Refactored AGENTS.md — Lean Entry Point Pattern
- Extracted rules from monolithic AGENTS.md into focused files: `CORE_DIRECTIVES.md`, `TOOL_USAGE.md`, `CODING_STYLE.md`, `TASK_WORKFLOW.md`, `ENVIRONMENT.md`
- AGENTS.md reduced from 269 lines (9.7KB) to 62 lines (2.5KB) — **77% smaller**
- Added Quick Reference table

### Updated README.md
- Major README rewrite with improved project overview, quick start, and documentation links

### Removed: USER_MANUAL.md
- Deleted outdated user manual (320 lines)

### Reorganized Meta Files into `.project_development/`
- Moved `CURRENT_ISSUE.md`, `PROJECT_DOCUMENTATION.md`, `PROJECT_NAVIGATION_ROUTES.md`, `PROJECT_ROADMAP.md`, `PROJECT_TESTING_SANDBOX_RULES.md`, `USER_COMMAND_EXTENSION.md` to `.project_development/` folder
- Updated all path references in `AGENTS.md` and `tests_sandbox/tests_sandbox.md`
- Cleaner project root directory

### [WIP] RAG Integration to Chat Loop
- `agents/chat/chat_loop.py`: Added RAG support via `retriever` parameter
- `llm_managers/factory.py`: New `create_chat_loop_rag()` factory method - PDF ingestion → FAISS → retriever → ChatLoop
- `llm_managers/providers/__init__.py`: Updated helper functions
- `llm_managers/providers/openrouter_provider.py`: Updated for RAG integration
- `app/repl/commands/llm_chat_commands.py`: Updated to use RAG-enabled ChatLoop
- `tests_sandbox/test_chat_loop.py`: Updated tests for RAG capabilities
- `tests_sandbox/test_llm_providers.py`: Updated provider tests

### Added MCP (Model Context Protocol) Support
- `local_mcp/`: New module for MCP servers
- `local_mcp/mcp_main.py`: MCP server entry point
- `local_mcp/servers_stdio/`: MCP servers using stdio transport
- `local_mcp/servers_stdio/math_server.py`: Math operations MCP server
- Added `mcp` dependency to `pyproject.toml`

### Refactored `llm_managers/` — Unified AgentFactory
- Consolidated 5 factory files into single `AgentFactory` class in `factory.py`
- Removed: `agent_chat_factory.py`, `agent_function_router_factory.py`, `agent_rag_factory.py`, `agent_react_web_search_factory.py`, `graph_react_web_search_factory.py`
- New unified API: `create_chat()`, `create_chat_loop()`, `create_chat_loop_rag()`, `create_function_router()`, `create_rag()`, `create_react_web_search()`, `create_graph_react_web_search()`
- `llm_managers/providers/__init__.py`: Helper functions `local_llm_provider()` and `openrouter_llm_provider()`
- Updated consumers: `llm_chat_commands.py`, `llm_graph_commands.py`
- `tests_sandbox/test_factory_refactor.py`: Tests for new unified API
- Updated `llm_models/local/llama_cpp_factory.py`: Model constants updated (Qwen 3.5)

### Fixed: llama.cpp Provider - Now Uses ChatOpenAI Client
- `llm_models/local/llama_cpp/llamacpp.py`: Refactored to use `ChatOpenAI` with a local OpenAI-compatible client pointing to `http://localhost:8080/v1`
- `llm_managers/providers/llamacpp_provider.py`: Simplified to pass `model_filename` and `context_size` to factory
- `llm_managers/agent_chat_factory.py`: Simplified `create_chat_loop()` - removed redundant code, defaults to `LlamaCppProvider` with Qwen 2.5
- `llm_models/local/llama_cpp_factory.py`: Cleaned up model constants (`LLAMA_CPP_MODEL_QWEN_2_5`, `LLAMA_CPP_MODEL_QWEN_3`)
- Added `openai` dependency to `pyproject.toml`

### Updated: AGENTS.md Rules (Previous Iteration)
- Enhanced system instructions and general rules
- Improved tool usage guidelines
- Updated coding style guidelines

### New: `llm_managers/` Module
- Agent factory files moved from `agents/` to `llm_managers/`
- Centralizes LLM agent creation logic
- Factories: chat, function router, RAG, ReAct web search, graph ReAct web search

### New: Ollama Integration
- `llm_models/local/ollama/ollama.py`: Ollama chat model wrapper with lazy initialization
- `llm_models/local/ollama_factory.py`: `LocalOllamaModelManager` with Qwen 3.5 model
- Provides local think model via `qwen3.5:0.8b`

### New: Chroma Vector Store
- `llm_models/vectorstores/vectorstore_chroma.py`: Chroma wrapper with OpenAI embeddings
- Uses `text-embedding-3-small` model with chunk_size=50
- Alternative to FAISS and Pinecone for vector storage

### Refactored: `app/model/`
- Reorganized into submodules: `db/`, `user_sessions/`
- `SessionDatabase` for per-session SQLite persistence
- `Session` for session lifecycle management
- `Model` facade for command history logging/retrieval

### Updated User Commands
- Updated `USER_COMMMAND_EXTENDED.md` to a lean set of commands focused on refactoring, test generation, auditing, benchmarking and repository synchronization. Removed Git‑related, code‑generation and documentation commands to keep the command suite minimal and secure.

### New: ChatLoop - Persistent Conversational Chat
- `agents/chat/chat_loop.py`: New `ChatLoop` class with persistent message history, single-turn and interactive REPL modes
- `llm_managers/agent_chat_factory.py`: Added `create_chat_loop()` and `create_chat_loop_local()` factory functions
- `app/repl/commands/llm_chat_commands.py`: Updated `AIChat` command to use `ChatLoop` with streaming
- `tests_sandbox/test_chat_loop.py`: 38 TDD tests covering initialization, history, responses, exit conditions, interactive loop, streaming, and factory creation
- `llm_managers/providers/openrouter_provider.py`: Cloud LLM provider with Claude 3.5 Haiku, temperature 0.7, frequency penalty
- Supports both `chat <message>` (single-query) and `chat` (interactive REPL) modes with streaming output
- Streaming uses `llm.stream()` with chunk accumulation and live printing
- Interactive mode prints LLM responses in real-time, exits cleanly on `quit` or `exit`
- Robust error handling with history rollback on LLM invocation failures
- Assistant responses are properly added to history for conversational context

### New: Streaming Enhancements
- `app/common/utils/streaming_metrics.py`: New `StreamingMetrics` class with context manager support, tracks token count, elapsed time, and calculates tokens-per-second
- `app/repl/utils/argument_parser.py`: New `parse_chat_arguments()` function extracts `--model <name>` flag from command arguments
- `agents/chat/chat_loop.py`: Added `run_streaming_with_metrics()` method returning response + metrics tuple; `start_interactive_streaming()` now displays tok/s after each response
- `agents/chat/simple_chat.py`: Added `run_streaming()` method for single-turn streaming via LangChain chain.stream()
- `agents/react_web_search/agent_react_web_search.py`: Added `run_streaming(query)` method for ReAct web search with streaming
- `agents/rag_pdf/agent_rag_pdf.py`: Added `run_streaming(query)` and `rag_pdf_streaming()` methods for RAG pipeline streaming
- `llm_managers/providers/openrouter_provider.py`: Now accepts `model_name` parameter (defaults to `anthropic/claude-3.5-haiku`)
- `llm_managers/agent_chat_factory.py`: Added `create_chat_loop_with_model(model_name)` factory for runtime model selection
- `app/repl/commands/llm_chat_commands.py`: `AIChat` command now supports `--model <model>` flag for runtime model selection, displays streaming metrics (tokens, time, tok/s) after each response
- `tests_sandbox/test_streaming_metrics.py`: 14 tests for StreamingMetrics (initialization, timing, token counting, calculation, context manager)
- `tests_sandbox/test_argument_parser.py`: 14 tests for argument parsing (--model flag at various positions, edge cases)
- `tests_sandbox/test_model_selection.py`: 8 tests for model selection (ChatLoop model override, factory with model name, streaming with metrics, OpenRouterProvider model_name)
- `tests_sandbox/test_chat_command.py`: 6 tests for AIChat command (--model flag, metrics display, interactive mode, error handling)
- `tests_sandbox/test_agent_streaming.py`: 6 tests for agent streaming (SimpleChat, AgentReactWebSearch, AgentRagPdf)
