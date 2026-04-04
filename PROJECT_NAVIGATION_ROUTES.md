# Project Navigation Routes - Agent-X

> **Last Updated**: April 3, 2026  
> **Version**: 0.1.0  
> **Python**: 3.14+  
> **Package Manager**: uv

---

## Project Overview

Agent-X is a Python-based LLM agent framework with a REPL (Read-Eval-Print Loop) interface. It enables users to interact with various language models through command-line commands, supporting multiple interaction patterns: simple chat, function calling, RAG with PDFs, ReAct web search, and graph-based reasoning workflows.

---

## Module Index

| Module | Files | Description |
|--------|-------|-------------|
| [Root](#root) | 2 | Entry point and project configuration |
| [_resources/](#_resources) | 2 | Sample data files for demos |
| [agents/](#agents) | 16 | Agent implementations (SimpleChat, ChatLoop, RAG, ReAct, Graph) |
| [llm_managers/](#llm_managers) | 9 | Agent factory functions + LLM provider strategy pattern |
| [app/](#app) | 20 | Core application: REPL, models, DB, security |
| [app_modules/](#app_modules) | 20 | LLM integrations, data stores, web ingestion |
| [llm_models/](#llm_models) | 7 | LLM model providers (cloud + local) |
| [tests/](#tests) | 7 | Unit and integration tests |
| [tests_sandbox/](#tests_sandbox) | 6 | Feature and integration testing sandbox |
| [Meta](#meta) | 1 | Project meta files (issues, rules) |

---

## Root

**Path**: `/`

Entry point for the application.

| File | Description |
|------|-------------|
| `main.py` | Application entry point. Creates `MainController`, registers all commands, launches `ReplApp` |
| `pyproject.toml` | Project configuration, dependencies, metadata |

**Application Flow**:
```
main.py → create_controller() → register commands → ReplApp(controller).run()
```

**Registered Commands**:
- **CLI**: `quit`, `clear`, `help`, `read`
- **Math**: `sum`
- **LLM Chat**: `chat`, `router`, `react`, `search`, `function`, `rag`
- **LLM Graph**: `graph`, `chains`, `reflex`

---

## llm_managers/

**Path**: `llm_managers/`

Factory functions and LLM provider strategy pattern. Centralizes agent creation logic and model provider abstraction.

### Sub-modules

| Sub-module | Description |
|------------|-------------|
| [providers/](#llm_managersproviders) | LLM provider implementations (Strategy pattern) |

### Factory Files

| File | Description |
|------|-------------|
| `llm_provider.py` | `LLMProvider` ABC - strategy interface for LLM providers |
| `agent_chat_factory.py` | Factories for SimpleChat and ChatLoop (`create_chat_loop`, `create_chat_loop_local`) |
| `agent_function_router_factory.py` | Factory for QueryRouter |
| `agent_rag_factory.py` | Factory for AgentRagPdf |
| `agent_react_web_search_factory.py` | Factory for AgentReactWebSearch |
| `graph_react_web_search_factory.py` | Factory for GraphReactWebSearch (local + cloud) |

### llm_managers/providers/

**Path**: `llm_managers/providers/`

LLM provider implementations following the Strategy pattern.

| File | Key Functions | Description |
|------|---------------|-------------|
| `llamacpp_provider.py` | `LlamaCppProvider` - local LLM via llama.cpp with Qwen 2.5 |
| `openai_provider.py` | `OpenAIProvider` - cloud LLM via OpenAI API |
| `openrouter_provider.py` | `OpenRouterProvider` - cloud LLM via OpenRouter (Claude 3.5 Haiku, streaming-enabled) |

---

## agents/

**Path**: `agents/`  
**Module Doc**: [agents.md](agents/agents.md)

Agent implementations and factory functions. Each agent represents a different LLM interaction pattern.

### Sub-modules

| Sub-module | Description |
|------------|-------------|
| [chat/](#agentschat) | Simple conversational agent |
| [function_tool_router/](#agentsfunction_tool_router) | Query routing with Ollama tool calling |
| [graph_react_web_search/](#agentsgraph_react_web_search) | LangGraph-based ReAct web search |
| [rag_pdf/](#agentsrag_pdf) | PDF RAG with FAISS + Ollama embeddings |
| [react_web_search/](#agentsreact_web_search) | LangChain ReAct web search agent |

### Factory Files

| File | Description |
|------|-------------|
| `agent_chat_factory.py` | Factory for SimpleChat, ChatLoop (`create_chat_loop`, `create_chat_loop_local`) |
| `agent_function_router_factory.py` | Factory for QueryRouter |
| `agent_rag_factory.py` | Factory for AgentRagPdf |
| `agent_react_web_search_factory.py` | Factory for AgentReactWebSearch |
| `graph_react_web_search_factory.py` | Factory for GraphReactWebSearch (local + cloud) |

### Design Patterns
- **Factory**: All `agent_*_factory.py` files encapsulate agent creation
- **Strategy**: Different agents implement different reasoning strategies
- **State Machine**: `GraphReactWebSearch` uses LangGraph `StateGraph`
- **RAG**: Standard pipeline: load → embed → store → retrieve → generate

---

### agents/chat/

**Path**: `agents/chat/`  
**Module Doc**: [chat.md](agents/chat/chat.md)

| File | Description |
|------|-------------|
| `simple_chat.py` | `SimpleChat` class - wraps `BaseChatModel` with a prompt template chain |
| `chat_loop.py` | `ChatLoop` class - persistent conversational chat with message history, single-turn and interactive REPL modes |

---

### agents/function_tool_router/

**Path**: `agents/function_tool_router/`  
**Module Doc**: [function_tool_router.md](agents/function_tool_router/function_tool_router.md)

| File | Description |
|------|-------------|
| `function_call.py` | `QueryRouter` class - Ollama tool calling to dispatch function calls |
| `functions.py` | Tool functions: `get_weather_info()`, `get_game_recommend()`, `calculate()` |
| `route.py` | `Route` class - maps function name to callable |

---

### agents/graph_react_web_search/

**Path**: `agents/graph_react_web_search/`  
**Module Doc**: [graph_react_web_search.md](agents/graph_react_web_search/graph_react_web_search.md)

| File | Description |
|------|-------------|
| `graph_react_web_search.py` | `GraphReactWebSearch` - LangGraph state machine with reasoning/act nodes |

---

### agents/rag_pdf/

**Path**: `agents/rag_pdf/`  
**Module Doc**: [rag_pdf.md](agents/rag_pdf/rag_pdf.md)

| File | Description |
|------|-------------|
| `agent_rag_pdf.py` | `AgentRagPdf` - PDF ingestion → FAISS vector store → retrieval QA chain |

---

### agents/react_web_search/

**Path**: `agents/react_web_search/`  
**Module Doc**: [react_web_search.md](agents/react_web_search/react_web_search.md)

| File | Description |
|------|-------------|
| `agent_react_web_search.py` | `AgentReactWebSearch` - thin wrapper delegating to `search_agent()` |
| `prompt.py` | ReAct prompt template |
| `schemas.py` | Pydantic models: `Source`, `AgentResponse` |
| `search_agent.py` | `search_agent()` function - creates ReAct agent with Tavily |

---

## app/

**Path**: `app/`  
**Module Doc**: [app.md](app/app.md)

Core application module containing the REPL system, data models, database layer, security utilities, and common helpers.

### Sub-modules

| Sub-module | Files | Description |
|------------|-------|-------------|
| [common/](#appcommon) | 3 | Shared utilities (file ops, console helpers) |
| [model/](#appmodel) | 5 | Data persistence, SQLite, session management |
| [repl/](#apprepl) | 10 | REPL system (core interactive shell) |
| [security/](#appsecurity) | 2 | Directory deletion safeguards |

---

### app/common/

**Path**: `app/common/`  
**Module Doc**: [common.md](app/common/common.md)

| File | Key Functions | Description |
|------|---------------|-------------|
| `utils/utils.py` | `safe_int()`, `clear_console()` | General utilities |
| `utils/file_utils.py` | `create_directory_with_timestamp()`, `dangerous_delete_directory()` | Directory management |
| `files/file_utils.py` | `save_to_output()` | Writes text to `local/output.txt` |

---

### app/model/

**Path**: `app/model/`  
**Module Doc**: [model.md](app/model/model.md)

| File | Key Classes | Description |
|------|-------------|-------------|
| `model.py` | `Model` | Session + DB facade; logs/retrieves command history |
| `model_entities.py` | `HistoryEntry` | Dataclass for command history entries |
| `db/data_base.py` | `SessionDatabase` | Per-session SQLite DB with `history` and `users` tables |
| `db/database_definition.py` | - | Table schemas (history, users) |
| `user_sessions/session.py` | `Session` | Session lifecycle (create/destroy) |

**Database Schema**:
```sql
CREATE TABLE IF NOT EXISTS history (id, command, created_at);
CREATE TABLE IF NOT EXISTS users (id, name, age);
```

---

### app/repl/

**Path**: `app/repl/`  
**Module Doc**: [repl.md](app/repl/repl.md)

The core interactive shell of Agent-X.

#### Core Files

| File | Key Classes | Description |
|------|-------------|-------------|
| `repl.py` | `ReplApp` | Main application loop |
| `command.py` | `Command` (ABC), `CommandResult` (ABC) | Base classes for commands |
| `command_parser.py` | `CommandParser` | Tokenizes input into `CommandData(key, arguments)` |
| `console.py` | `Console`, `Colors` | Colored output utilities |
| `base.py` | `IMainController` | Interface for command controllers |
| `controllers/main_controller.py` | `MainController` | Command registry (`dict[str, Command]`) |

#### Commands

| File | Commands | Description |
|------|----------|-------------|
| `commands/cli_commands.py` | `quit`, `clear`, `help`, `read` | CLI utilities |
| `commands/llm_chat_commands.py` | `chat`, `search`, `function`, `rag`, `router`, `react` | LLM chat interactions |
| `commands/llm_graph_commands.py` | `graph`, `chains`, `reflex` | LLM graph workflows |
| `commands/math_commands.py` | `sum` | Math operations |

#### Execution Flow
```
ReplApp.run()
  ├── Creates Model(session_name="test_2")
  ├── Loop:
  │   ├── input("(agent-x) > ")
  │   ├── CommandParser.parse() → CommandData(key, arguments)
  │   ├── MainController.find_command(key)
  │   ├── Model.log_command(HistoryEntry(key))
  │   ├── command.run(arguments) → CommandResult
  │   ├── result.apply()
  │   └── Print command history
  └── Exit on KeyboardInterrupt / EOFError / QuitCommand
```

---

### app/security/

**Path**: `app/security/`  
**Module Doc**: [security.md](app/security/security.md)

| File | Key Functions | Description |
|------|---------------|-------------|
| `security.py` | `is_directory_allowed_to_deletion()` | Validates paths are within allowed dirs |
| `security_constants.py` | - | Constants: `SESSION_DEFAULT_NAME`, `DIRECTORIES_DELETION_ALLOWED` |

---

## app_modules/

**Path**: `app_modules/`  
**Module Doc**: [app_modules.md](app_modules/app_modules.md)

Extended application modules containing LLM integrations, data stores, document loaders, and web ingestion pipelines.

### Sub-modules

| Sub-module | Files | Description |
|------------|-------|-------------|
| [data_stores/](#app_modulesdata_stores) | 1 | FAISS vector store creation and persistence |
| [document_loaders/](#app_modulesdocument_loaders) | 1 | PDF loading and text chunking |
| [llm/langchain/](#app_modulesllmlangchain) | 7 | LangChain ReAct agents, router agents, tools |
| [llm/langgraph/](#app_modulesllmlanggraph) | 6 | LangGraph reflection and reflexion workflows |
| [web_ingestion_app/](#app_modulesweb_ingestion_app) | 5 | Web scraping pipeline (Tavily → chunk → index) |

---

### app_modules/data_stores/

**Path**: `app_modules/data_stores/`  
**Module Doc**: [data_stores.md](app_modules/data_stores/data_stores.md)

| File | Key Functions | Description |
|------|---------------|-------------|
| `vector_store_faiss.py` | `create_faiss()` | Builds FAISS index from documents, saves to disk, reloads |

---

### app_modules/document_loaders/

**Path**: `app_modules/document_loaders/`  
**Module Doc**: [document_loaders.md](app_modules/document_loaders/document_loaders.md)

| File | Key Functions | Description |
|------|---------------|-------------|
| `pdf_loader.py` | `pdf_loader()` | Loads PDF via `PyPDFLoader`, splits with `CharacterTextSplitter` |

---

### app_modules/llm/langchain/

**Path**: `app_modules/llm/langchain/`  
**Module Doc**: [langchain.md](app_modules/llm/langchain/langchain.md)

#### React Agents

| File | Key Functions | Description |
|------|---------------|-------------|
| `react_agents/react_agents_tools/react_tools.py` | `react_tools()` | Manual ReAct loop with tools (get_text_length) |
| `react_agents/react_agents_tools/callbacks.py` | `AgentCallbackHandler` | Prints prompts and LLM responses |
| `react_agents/router_agents/router_react_agent.py` | `router_agent()` | Routes between Python Agent + CSV Agent |
| `react_agents/router_agents/agent_executors/csv_agent.py` | `create_csv_agent_executor()` | Pandas-based CSV querying |
| `react_agents/router_agents/agent_executors/qr_react_agent.py` | `create_qr_react_agent_executor()` | QR code generation via PythonREPLTool |

#### Tools

| File | Key Functions | Description |
|------|---------------|-------------|
| `simple_tool.py` | `simple_tool()` | Basic `multiply` tool with tool-calling agent |
| `tools/tavily_web_search/simple_tool_search_tavily.py` | `simple_tool_search_tavily()` | Tavily search + multiply tool agent |

---

### app_modules/llm/langgraph/

**Path**: `app_modules/llm/langgraph/`  
**Module Doc**: [langgraph.md](app_modules/llm/langgraph/langgraph.md)

#### Graph Reflector Chain

| File | Key Functions | Description |
|------|---------------|-------------|
| `graph_reflector_chain/chains.py` | `generate_chain`, `reflect_chain` | Tweet generation and reflection prompts |
| `graph_reflector_chain/graph_chains.py` | `graph_chains()` | StateGraph with generate ↔ reflect loop (6 messages) |

#### Graph Reflexion Agent

| File | Key Functions | Description |
|------|---------------|-------------|
| `graph_reflexion_agent/chains.py` | `first_responder`, `revisor` | Initial answer + self-reflection + revision |
| `graph_reflexion_agent/graph_reflexion_agent.py` | `graph_reflexion_agent()` | Workflow: draft → execute_tools → revise → loop |
| `graph_reflexion_agent/schemas.py` | `Reflection`, `AnswerQuestion`, `ReviseAnswer` | Pydantic models for structured output |
| `graph_reflexion_agent/tool_executor.py` | `run_queries()`, `execute_tools` | TavilySearch tool execution |

---

### app_modules/web_ingestion_app/

**Path**: `app_modules/web_ingestion_app/`  
**Module Doc**: [web_ingestion_app.md](app_modules/web_ingestion_app/web_ingestion_app.md)

| File | Key Classes/Functions | Description |
|------|-----------------------|-------------|
| `web_ingestion_app.py` | `WebIngestionApp` | Orchestrates full pipeline |
| `web_ingestion.py` | - | Entry point script |
| `tavily.py` | `WebExtract` | TavilyExtract and TavilyMap wrappers |
| `documents.py` | `process_documents()`, `index_documents_async()` | Document processing and async indexing |
| `helpers.py` | `save_docs()`, `chunk_urls()`, `load_docs_from_jsonl()` | JSONL serialization, URL chunking |

**Pipeline Flow**:
```
TavilyMap → chunk_urls → WebExtract.async_extract → save_docs (JSONL)
    → process_documents → index_documents_async → VectorStore
```

---

## llm_models/

**Path**: `llm_models/`  
**Module Doc**: [llm_models.md](llm_models/llm_models.md)

LLM model providers and vector store integrations. Supports both cloud-hosted and locally-run models.

### Sub-modules

| Sub-module | Files | Description |
|------------|-------|-------------|
| [cloud/open_ai/](#llm_modelscloudopen_ai) | 1 | OpenAI GPT models |
| [cloud/google/](#llm_modelsgoogle) | 1 | Google Gemini models |
| [local/](#llm_modelslocal) | 1 | Local model factory |
| [local/llama_cpp/](#llm_modelslocalllama_cpp) | 2 | Local Llama.cpp GGUF models |
| [local/ollama/](#llm_modelslocalollama) | 1 | Ollama embeddings |
| [vectorstores/](#llm_modelsvectorstores) | 1 | Pinecone vector store |

### Model Providers

| Provider | Models | Configuration |
|----------|--------|---------------|
| **OpenAI** | gpt-4-turbo, gpt-3.5-turbo | Hardcoded defaults |
| **Google** | gemini-2.5-flash-lite | Hardcoded defaults |
| **LlamaCpp** | Qwen 2.5, Qwen 3, Qwen 3.5 Opus | `LlamaCppConfig` Pydantic model |
| **Ollama** | nomic-embed-text (embeddings) | Direct instantiation |

---

### llm_models/cloud/open_ai/

**Path**: `llm_models/cloud/open_ai/`  
**Module Doc**: [open_ai.md](llm_models/cloud/open_ai/open_ai.md)

| File | Key Functions | Description |
|------|---------------|-------------|
| `open_ai_gpt.py` | `get_remote_llm_openai_gpt4()`, `get_remote_llm_openai_gpt3_5_turbo()` | OpenAI GPT model wrappers |

---

### llm_models/cloud/google/

**Path**: `llm_models/cloud/google/`  
**Module Doc**: [google.md](llm_models/cloud/google/google.md)

| File | Key Functions | Description |
|------|---------------|-------------|
| `google_gemini.py` | `get_remote_llm_google_gemini()` | Google Gemini wrapper |

---

### llm_models/local/

**Path**: `llm_models/local/`

| File | Key Functions | Description |
|------|---------------|-------------|
| `llama_cpp_factory.py` | `model_factory_llamacpp` | Singleton-style factory instance |

### llm_models/local/llama_cpp/

**Path**: `llm_models/local/llama_cpp/`

| File | Key Classes | Description |
|------|-------------|-------------|
| `llamacpp.py` | `LlamaCpp` | Factory for creating local ChatLlamaCpp instances |
| `llamacpp_config.py` | `LlamaCppConfig` | Pydantic config: model_filename, temperature, context_size, max_tokens, top_p, batch_size |

---

### llm_models/local/ollama/

**Path**: `llm_models/local/ollama/`

| File | Key Functions | Description |
|------|---------------|-------------|
| `ollama_embeddings.py` | `create_embeddings_model()` | Returns OllamaEmbeddings (nomic-embed-text) |

---

### llm_models/vectorstores/

**Path**: `llm_models/vectorstores/`

| File | Key Functions | Description |
|------|---------------|-------------|
| `vectorstore_pinecone.py` | `create_vectorstore_pinecone()` | PineconeVectorStore with OpenAI embeddings |

---

## _resources/

**Path**: `_resources/`

Sample data files used by agents and demos.

| File | Description |
|------|-------------|
| `episode_info.csv` | CSV data for CSV agent demos |
| `react.pdf` | PDF document for RAG agent demos |

---

## tests/

**Path**: `tests/`

Unit and integration tests.

### Structure

```
tests/
├── integration/
│   └── __init__.py
└── unit/
    ├── app/
    │   └── __init__.py
    └── applications/
        └── repl_app/
            └── command_line_controller/
                ├── command_parser_test.py
                └── commands_controller_test.py
```

### Test Commands
```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit -q

# Run integration tests only
pytest tests/integration -q

# Run specific test
pytest tests/path/to/test_file.py::TestClass::test_function_name -q

# Run tests matching pattern
pytest tests/path/to/test_file.py -k "pattern" -q
```

---

## tests_sandbox/

**Path**: `tests_sandbox/`

Feature and integration testing sandbox. Used for experimental tests during development.

### Structure

```
tests_sandbox/
├── tests_sandbox.md                   # Sandbox documentation
├── features/                        # Feature-level tests
│   └── test_controller.py           # MainController feature tests
├── test_command_parser.py           # CommandParser unit tests
├── test_commands.py                 # Command implementation tests
└── test_chat_loop.py                # ChatLoop TDD tests (38 tests)
```

### Test Commands
```bash
# Run all sandbox tests
uv run pytest tests_sandbox/ -v

# Run feature tests only
uv run pytest tests_sandbox/features/ -v
```

---

## Meta

**Path**: `/`

Project meta files for tracking current state and issues.

| File | Description |
|------|-------------|
| `CURRENT_ISSUE.md` | Currently tracked issues, root cause analysis, and fix status |
| `PROJECT_TESTING_SANDBOX_RULES.md` | TDD strategy and rules for AI agents |

---

## Dependencies

### Core
- **LangChain**: `langchain>=1.2.13`, `langchain-community`, `langchain-experimental`
- **LangGraph**: `langgraph>=1.1.3`
- **LLM Providers**: `langchain-openai`, `langchain-google-genai`, `langchain-ollama`, `langchain-openrouter`
- **Local Models**: `llama-cpp-python>=0.3.19`

### Vector Stores
- **Chroma**: `chromadb`, `langchain-chroma`
- **FAISS**: `faiss-cpu`
- **Pinecone**: `langchain-pinecone`

### Tools & Utilities
- **Web Search**: `langchain-tavily`
- **PDF**: `pypdf`
- **Data**: `pandas`, `tabulate`
- **Images**: `pillow`, `qrcode`
- **Graph Viz**: `grandalf`
- **Env**: `python-dotenv`

### Dev
- **Testing**: `pytest>=9.0.2`

---

## Quick Start

```bash
# Install dependencies
uv sync

# Run the application
python main.py
```

---

## Code Style

- **Language**: Python 3.14+
- **Line Length**: 88 characters
- **Docstrings**: Google-style for public functions/classes
- **Naming**:
  - Functions/variables: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
  - Private members: `_prefix`
  - Modules/files: `snake_case.py`
