# Project Documentation - Agent-X

> **Last Updated**: April 4, 2026  
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
| [CURRENT_ISSUE.md](CURRENT_ISSUE.md) | Meta | Currently tracked issues and their status |
| [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md) | Roadmap | Planned features and improvements |
| [doc/dependencies.md](doc/dependencies.md) | Configuration | Dependencies table, environment variables, quick start, code style |
| [USER_COMMMAND_EXTENDED.md](USER_COMMAND_EXTENSION.md) | Commands | Simplified, powerful LLM‑agent command reference |


---

## Module Structure

```
agent-x/
├── main.py                          # Application entry point
├── pyproject.toml                   # Project configuration, dependencies
├── CURRENT_ISSUE.md                 # Currently tracked issues and fix status
├── agents/                          # Agent implementations
│   ├── chat/                        # SimpleChat, ChatLoop (persistent conversation)
│   ├── function_tool_router/        # Query routing with Ollama tool calling
│   ├── graph_react_web_search/      # LangGraph-based ReAct web search
│   ├── rag_pdf/                     # PDF RAG with FAISS + Ollama embeddings
│   └── react_web_search/            # LangChain ReAct web search agent
├── llm_managers/                    # Agent factory functions + LLM provider strategy
│   ├── providers/                   # LLM provider implementations (Strategy pattern)
│   │   ├── llamacpp_provider.py     # Local LLM via llama.cpp
│   │   ├── openai_provider.py       # Cloud LLM via OpenAI API
│   │   └── openrouter_provider.py   # Cloud LLM via OpenRouter (Claude 3.5 Haiku)
│   ├── llm_provider.py              # LLMProvider ABC - strategy interface
│   ├── agent_chat_factory.py        # Factories for SimpleChat and ChatLoop
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
│   ├── test_commands.py             # Command implementation tests
│   ├── test_chat_loop.py            # ChatLoop TDD tests (38 tests)
│   ├── test_streaming_metrics.py    # StreamingMetrics tok/s tracking (14 tests)
│   ├── test_argument_parser.py      # --model flag argument parsing (14 tests)
│   ├── test_model_selection.py      # Model selection + streaming metrics (8 tests)
│   ├── test_chat_command.py         # AIChat command with --model flag (6 tests)
│   ├── test_agent_streaming.py      # Agent streaming methods (6 tests)
│   ├── test_llm_providers.py        # LLM provider tests
│   └── test_llm_managers.py         # LLM manager tests
├── PROJECT_TESTING_SANDBOX_RULES.md # TDD strategy and rules for AI agents
├── _resources/                      # Sample data files
└── doc/                             # Project documentation
```

---

## Recent Changes

### Fixed: llama.cpp Provider - Now Uses ChatOpenAI Client
- `llm_models/local/llama_cpp/llamacpp.py`: Refactored to use `ChatOpenAI` with a local OpenAI-compatible client pointing to `http://localhost:8080/v1`
- `llm_managers/providers/llamacpp_provider.py`: Simplified to pass `model_filename` and `context_size` to factory
- `llm_managers/agent_chat_factory.py`: Simplified `create_chat_loop()` - removed redundant code, defaults to `LlamaCppProvider` with Qwen 2.5
- `llm_models/local/llama_cpp_factory.py`: Cleaned up model constants (`LLAMA_CPP_MODEL_QWEN_2_5`, `LLAMA_CPP_MODEL_QWEN_3`)
- Added `openai` dependency to `pyproject.toml`

### New: USER_MANUAL.md
- Comprehensive user manual added (320 lines)

### Updated: AGENTS.md Rules
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
