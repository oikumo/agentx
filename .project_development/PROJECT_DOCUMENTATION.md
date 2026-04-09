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
├── main.py                     # Application entry point
├── pyproject.toml              # Project configuration, dependencies
├── .project_development/       # Project meta and rules files
│   ├── CORE_DIRECTIVES.md
│   ├── TOOL_USAGE.md
│   ├── CODING_STYLE.md
│   ├── TASK_WORKFLOW.md
│   ├── ENVIRONMENT.md
│   ├── CURRENT_ISSUE.md
│   ├── PROJECT_DOCUMENTATION.md
│   ├── PROJECT_NAVIGATION_ROUTES.md
│   ├── PROJECT_ROADMAP.md
│   ├── PROJECT_TESTING_SANDBOX_RULES.md
│   └── USER_COMMAND_EXTENSION.md
├── src/                        # All source code (MVC architecture)
│   ├── common/                 # Shared utilities
│   ├── controllers/            # Business logic & command routing
│   ├── model/                  # Data persistence, SQLite, sessions
│   │   ├── db/                 # Database layer
│   │   └── session/            # Session lifecycle
│   ├── services/               # AI/LLM service layer
│   │   └── ai/                 # AI service implementations
│   ├── views/                  # User interface layer
│   │   ├── chat_view/          # Chat interface
│   │   ├── main_view/          # Main application view
│   │   └── common/             # Shared view utilities
│   └── main.py                 # Module entry point
├── tests/                      # Unit and integration tests (read-only)
├── tests_sandbox/              # Feature and integration testing sandbox
├── _resources/                 # Sample data files
└── doc/                        # Project documentation
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

### MVC Architecture Migration (v0.2.0) - April 2026
- **Complete architectural reorganization** from agent-centric to MVC pattern
- **New structure**:
  - `src/common/` — Shared utilities
  - `src/controllers/` — Business logic and command routing  
  - `src/model/` — Data persistence, sessions, SQLite
  - `src/services/` — AI/LLM service layer
  - `src/views/` — User interface layer
- **Rationale**: Improved maintainability, testability, and standard Python application patterns

### Documentation Improvements
- Refactored AGENTS.md into focused files: `CORE_DIRECTIVES.md`, `TOOL_USAGE.md`, `CODING_STYLE.md`, `TASK_WORKFLOW.md`, `ENVIRONMENT.md`
- Reorganized meta files into `.project_development/` folder
- Updated PROJECT_NAVIGATION_ROUTES.md and PROJECT_DOCUMENTATION.md
