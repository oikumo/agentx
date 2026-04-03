# Project Documentation - Agent-X

> **Last Updated**: April 3, 2026  
> **Version**: 0.1.0  
> **Python**: >=3.14  
> **Package Manager**: uv

Agent-X is a Python‑based LLM agent framework with a REPL interface. This file serves as a **navigation map** to the detailed documentation stored in the `doc/` folder, and to auxiliary reference files such as command guides and testing rules.

---

## Documentation Index

_This section lists the primary documentation files. Click a link to open the detailed markdown for that area._

| File | Domain | Description |
|------|--------|-------------|
| [doc/overview.md](doc/overview.md) | Project | Overview, architecture, application flow, command registry, design patterns, key decisions |
| [doc/root_module.md](doc/root_module.md) | Root | `main.py`, `pyproject.toml`, `README.md` |
| [doc/agents.md](doc/agents.md) | Agents | All agent implementations: chat, RAG, function router, ReAct search, graph search |
| [doc/app_repl.md](doc/app_repl.md) | App/REPL | REPL system, command pattern, controllers, all command classes |
| [doc/app_model.md](doc/app_model.md) | App/Model | Data persistence, sessions, SQLite database, command history |
| [doc/app_security.md](doc/app_security.md) | App/Security | Directory deletion safeguards, allowed paths |
| [doc/app_common.md](doc/app_common.md) | App/Common | Shared utilities: file ops, console helpers |
| [doc/app_modules_langchain.md](doc/app_modules_langchain.md) | App Modules/LangChain | ReAct agents, router agents, tools, callbacks |
| [doc/app_modules_langgraph.md](doc/app_modules_langgraph.md) | App Modules/LangGraph | Reflection chains, reflexion agent workflows |
| [doc/app_modules_data_stores.md](doc/app_modules_data_stores.md) | App Modules/Data Stores | FAISS vector store creation and persistence |
| [doc/app_modules_document_loaders.md](doc/app_modules_document_loaders.md) | App Modules/Loaders | PDF loading and text chunking |
| [doc/app_modules_web_ingestion.md](doc/app_modules_web_ingestion.md) | App Modules/Web Ingestion | Tavily extraction, document processing, vector store indexing pipeline |
| [doc/llm_models.md](doc/llm_models.md) | LLM Models | Cloud providers (OpenAI, Google), local providers (LlamaCpp, Ollama), vector stores (Pinecone, Chroma) |
| [doc/tests.md](doc/tests.md) | Tests | Unit test suite, test commands |
| [tests_sandbox/tests_sandbox.md](tests_sandbox/tests_sandbox.md) | Tests Sandbox | Feature and integration testing sandbox documentation |
| [PROJECT_TESTING_SANDBOX_RULES.md](PROJECT_TESTING_SANDBOX_RULES.md) | Testing Rules | TDD strategy and Kent Beck-style rules for AI agents |
| [doc/dependencies.md](doc/dependencies.md) | Configuration | Dependencies table, environment variables, quick start, code style |
| [USER_COMMMAND_EXTENDED.md](USER_COMMAND_EXTENSION.md) | Commands | Simplified, powerful LLM‑agent command reference |


---

## Module Structure

```
agent-x/
├── main.py                          # Application entry point
├── pyproject.toml                   # Project configuration, dependencies
├── agents/                          # Agent implementations
│   ├── chat/                        # Simple conversational agent
│   ├── function_tool_router/        # Query routing with Ollama tool calling
│   ├── graph_react_web_search/      # LangGraph-based ReAct web search
│   ├── rag_pdf/                     # PDF RAG with FAISS + Ollama embeddings
│   └── react_web_search/            # LangChain ReAct web search agent
├── llm_managers/                    # Agent factory functions (moved from agents/)
│   ├── agent_chat_factory.py        # Factory for SimpleChat
│   ├── agent_function_router_factory.py  # Factory for QueryRouter
│   ├── agent_rag_factory.py         # Factory for AgentRagPdf
│   ├── agent_react_web_search_factory.py # Factory for AgentReactWebSearch
│   └── graph_react_web_search_factory.py # Factory for GraphReactWebSearch
├── app/                             # Core application
│   ├── common/                      # Shared utilities
│   ├── model/                       # Data persistence, sessions, SQLite
│   ├── repl/                        # REPL system and commands
│   └── security/                    # Directory deletion safeguards
├── app_modules/                     # Extended application modules
│   ├── data_stores/                 # FAISS vector store
│   ├── document_loaders/            # PDF loading and chunking
│   ├── llm/                         # LangChain and LangGraph integrations
│   └── web_ingestion_app/           # Web scraping pipeline
├── llm_models/                      # LLM model providers and vector stores
│   ├── cloud/                       # Cloud providers (OpenAI, Google)
│   ├── local/                       # Local providers (LlamaCpp, Ollama)
│   │   ├── llama_cpp/               # Llama.cpp GGUF models
│   │   ├── llama_cpp_factory.py     # Pre-configured factory
│   │   ├── ollama/                  # Ollama chat models
│   │   └── ollama_factory.py        # Ollama model manager
│   └── vectorstores/                # Vector store integrations
│       ├── vectorstore_pinecone.py  # Pinecone wrapper
│       └── vectorstore_chroma.py    # Chroma wrapper
├── tests/                           # Unit and integration tests (read-only)
├── tests_sandbox/                   # Feature and integration testing sandbox
│   ├── tests_sandbox.md             # Sandbox documentation
│   ├── features/                    # Feature-level tests (controllers, workflows)
│   ├── test_command_parser.py       # Command parser unit tests
│   └── test_commands.py             # Command implementation tests
├── PROJECT_TESTING_SANDBOX_RULES.md # TDD strategy and rules for AI agents
├── _resources/                      # Sample data files
└── doc/                             # Project documentation
```

---

## Recent Changes

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
