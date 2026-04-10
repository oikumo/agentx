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
| [Root](#root) | 2 | Entry point and project configuration |
| [_resources/](#_resources) | 2 | Sample data files for demos |
| [src/](#src) | 6 | All source code modules |
| [src/common/](#srccommon) | 2 | Shared utilities and helpers |
| [src/controllers/](#srccontrollers) | 2 | Application controllers (business logic) |
| [src/model/](#srcmodel) | 5 | Data persistence, SQLite, session management |
| [src/services/](#srcservices) | 2 | Service layer (AI/LLM services) |
| [src/views/](#srcviews) | 6 | View layer (user interface) |
| [tests/](#tests) | 7 | Unit and integration tests |
| [tests_sandbox/](#tests_sandbox) | 14 | Feature and integration testing sandbox |
| [Meta](#meta) | 2 | Project meta files (issues, roadmap, rules) |

---

## Root

**Path**: `/`

Entry point for the application.

| File | Description |
|------|-------------|
| `main.py` | Wrapper entry point. Delegates to `src/main.py` |
| `pyproject.toml` | Project configuration, dependencies, metadata |

**Application Flow**:
```
main.py → src/main.py → Application initialization → View/Controller execution
```

**Architecture**: MVC (Model-View-Controller) pattern
- **Models**: Data persistence and session management
- **Views**: User interface and interaction handling
- **Controllers**: Business logic and command routing
- **Services**: AI/LLM service layer
- **Common**: Shared utilities across the application

---

## src/

**Path**: `src/`

All source code modules organized in MVC (Model-View-Controller) architecture. Installed as `agent-x` package in development mode.

### Architecture

```
src/
├── common/         # Shared utilities
├── controllers/    # Business logic & command routing
├── model/          # Data persistence, sessions, SQLite
├── services/       # AI/LLM service layer
└── views/          # User interface layer
```

### Sub-modules

| Sub-module | Description |
|------------|-------------|
| [common/](#srccommon) | Shared utilities and helpers |
| [controllers/](#srccontrollers) | Application controllers (business logic) |
| [model/](#srcmodel) | Data persistence, SQLite, session management |
| [services/](#srcservices) | Service layer (AI/LLM services) |
| [views/](#srcviews) | View layer (user interface) |

---

## src/common/

**Path**: `src/common/`

Shared utilities and helper functions used across the application.

| File | Description |
|------|-------------|
| `__init__.py` | Module initialization |

---

## src/controllers/

**Path**: `src/controllers/`

Application controllers that handle business logic and command routing.

| File | Description |
|------|-------------|
| `__init__.py` | Module initialization |

---

## src/model/

**Path**: `src/model/`

Data persistence layer with SQLite database and session management.

| File | Description |
|------|-------------|
| `db/` | Database layer with SQLite |
| `session/` | Session lifecycle management |

---

## src/services/

**Path**: `src/services/`

Service layer providing AI/LLM services to the application.

### Structure

```
services/
├── ai/               # AI service implementations
│   ├── cloud/        # Cloud providers (OpenAI, Google)
│   └── local/        # Local providers (LlamaCpp, Ollama)
└── __init__.py
```

| Module | Description |
|--------|-------------|
| [ai/](#servicesai) | AI/LLM service implementations |

---

## src/views/

**Path**: `src/views/`

View layer handling user interface and interaction.

| File | Description |
|------|-------------|
| `chat_view/` | Chat interface view |
| `main_view/` | Main application view |
| `common/` | Shared view utilities |

---



### src/app/common/

**Path**: `src/app/common/`  
**Module Doc**: [common.md](app/common/common.md)

| File | Key Functions | Description |
|------|---------------|-------------|
| `utils/utils.py` | `safe_int()`, `clear_console()` | General utilities |
| `utils/file_utils.py` | `create_directory_with_timestamp()`, `dangerous_delete_directory()` | Directory management |
| `utils/streaming_metrics.py` | `StreamingMetrics` | Token-per-second tracking during streaming |
| `files/file_utils.py` | `save_to_output()` | Writes text to `local/output.txt` |

---

### src/app/model/

**Path**: `src/app/model/`  
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

### src/app/repl/

**Path**: `src/app/repl/`  
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
| `utils/argument_parser.py` | `parse_chat_arguments()` | Extracts `--model` flag from command arguments |

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

### src/app/security/

**Path**: `src/app/security/`  
**Module Doc**: [security.md](app/security/security.md)

| File | Key Functions | Description |
|------|---------------|-------------|
| `security.py` | `is_directory_allowed_to_deletion()` | Validates paths are within allowed dirs |
| `security_constants.py` | - | Constants: `SESSION_DEFAULT_NAME`, `DIRECTORIES_DELETION_ALLOWED` |

---

## src/app_modules/

**Path**: `src/app_modules/`  
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

### src/app_modules/data_stores/

**Path**: `src/app_modules/data_stores/`  
**Module Doc**: [data_stores.md](app_modules/data_stores/data_stores.md)

| File | Key Functions | Description |
|------|---------------|-------------|
| `vector_store_faiss.py` | `create_faiss()` | Builds FAISS index from documents, saves to disk, reloads |

---

### src/app_modules/document_loaders/

**Path**: `src/app_modules/document_loaders/`  
**Module Doc**: [document_loaders.md](app_modules/document_loaders/document_loaders.md)

| File | Key Functions | Description |
|------|---------------|-------------|
| `pdf_loader.py` | `pdf_loader()` | Loads PDF via `PyPDFLoader`, splits with `CharacterTextSplitter` |

---

### src/app_modules/llm/langchain/

**Path**: `src/app_modules/llm/langchain/`  
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

### src/app_modules/llm/langgraph/

**Path**: `src/app_modules/llm/langgraph/`  
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

### src/app_modules/web_ingestion_app/

**Path**: `src/app_modules/web_ingestion_app/`  
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

## src/llm_models/

**Path**: `src/llm_models/`  
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
| **LlamaCpp** | Qwen 2.5, Qwen 3 | `LlamaCppConfig` Pydantic model |
| **Ollama** | nomic-embed-text (embeddings) | Direct instantiation |

---

### src/llm_models/cloud/open_ai/

**Path**: `src/llm_models/cloud/open_ai/`  
**Module Doc**: [open_ai.md](llm_models/cloud/open_ai/open_ai.md)

| File | Key Functions | Description |
|------|---------------|-------------|
| `open_ai_gpt.py` | `get_remote_llm_openai_gpt4()`, `get_remote_llm_openai_gpt3_5_turbo()` | OpenAI GPT model wrappers |

---

### src/llm_models/cloud/google/

**Path**: `src/llm_models/cloud/google/`  
**Module Doc**: [google.md](llm_models/cloud/google/google.md)

| File | Key Functions | Description |
|------|---------------|-------------|
| `google_gemini.py` | `get_remote_llm_google_gemini()` | Google Gemini wrapper |

---

### src/llm_models/local/

**Path**: `src/llm_models/local/`

| File | Key Functions | Description |
|------|---------------|-------------|
| `llama_cpp_factory.py` | `model_factory_llamacpp` | Singleton-style factory instance |

### src/llm_models/local/llama_cpp/

**Path**: `src/llm_models/local/llama_cpp/`

| File | Key Classes | Description |
|------|-------------|-------------|
| `llamacpp.py` | `LlamaCpp` | Factory for creating local ChatOpenAI instances via llama.cpp server |
| `llamacpp_config.py` | `LlamaCppConfig` | Pydantic config: model_filename, temperature, context_size, max_tokens, top_p, batch_size |

---

### src/llm_models/local/ollama/

**Path**: `src/llm_models/local/ollama/`

| File | Key Functions | Description |
|------|---------------|-------------|
| `ollama_embeddings.py` | `create_embeddings_model()` | Returns OllamaEmbeddings (nomic-embed-text) |

---

### src/llm_models/vectorstores/

**Path**: `src/llm_models/vectorstores/`

| File | Key Functions | Description |
|------|---------------|-------------|
| `vectorstore_pinecone.py` | `create_vectorstore_pinecone()` | PineconeVectorStore with OpenAI embeddings |

---

## _resources/

**Path**: `_resources/`

Sample data files used for demos and testing.

| File | Description |
|------|-------------|
| `episode_info.csv` | Sample CSV data for testing |
| `react.pdf` | Sample PDF document for RAG testing |

---

## tests/

**Path**: `tests/`

Unit and integration tests (read-only).

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

Feature and integration testing sandbox for experimental development.

### Test Commands
```bash
# Run all sandbox tests
uv run pytest tests_sandbox/ -v

# Run feature tests only
uv run pytest tests_sandbox/features/ -v
```
tests/
├── integration/
│   └── __init__.py
└── unit/
    └── app/
        └── __init__.py
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
├── benchmark_navigation.md            # Benchmark task definitions
├── benchmark_report.md                # Benchmark results report
├── features/                        # Feature-level tests
│   └── test_controller.py           # MainController feature tests
├── test_command_parser.py           # CommandParser unit tests
├── test_commands.py                 # Command implementation tests
├── test_chat_loop.py                # ChatLoop TDD tests (40+ tests)
├── test_streaming_metrics.py        # StreamingMetrics tok/s tracking (14 tests)
├── test_argument_parser.py          # --model flag argument parsing (14 tests)
├── test_model_selection.py          # Model selection + streaming metrics (8 tests)
├── test_chat_command.py             # AIChat command with --model flag (6 tests)
├── test_agent_streaming.py          # Agent streaming methods (6 tests)
├── test_llm_providers.py            # LLM provider tests
├── test_llm_managers.py             # LLM manager tests
├── test_factory_refactor.py         # AgentFactory unified API tests
└── test_benchmark_navigation.py     # AGENTS.md navigation benchmark (12 tests)
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

**Path**: `/.project_development/`

Project meta files for tracking current state and issues.

| File | Description |
|------|-------------|
| `CORE_DIRECTIVES.md` | Non-negotiable system agent rules |
| `TOOL_USAGE.md` | Tool selection & usage guidelines |
| `CODING_STYLE.md` | Code conventions & naming |
| `TASK_WORKFLOW.md` | Step-by-step task process |
| `ENVIRONMENT.md` | Runtime & operational notes |
| `CURRENT_ISSUE.md` | Currently tracked issues, root cause analysis, and fix status |
| `PROJECT_ROADMAP.md` | Planned features, improvements, and completed items |
| `PROJECT_TESTING_SANDBOX_RULES.md` | TDD strategy and rules for AI agents |
| `PROJECT_DOCUMENTATION.md` | Full project documentation map |
| `PROJECT_NAVIGATION_ROUTES.md` | This file - project navigation routes |
| `USER_COMMAND_EXTENSION.md` | Extended user commands documentation |

---

## Architecture

**Current Version**: v0.2.0 - MVC Architecture (April 2026)

Agent-X follows the **MVC (Model-View-Controller)** pattern for clean separation of concerns:

- **Model** (`src/model/`): Data persistence, SQLite database, session management
- **View** (`src/views/`): User interface components (chat view, main view)
- **Controller** (`src/controllers/`): Business logic and command routing
- **Services** (`src/services/`): AI/LLM service layer with cloud and local providers
- **Common** (`src/common/`): Shared utilities across the application

This architecture improves maintainability, testability, and follows standard Python application patterns.

---

## Dependencies

### Core
- **LangChain**: `langchain>=1.2.13`, `langchain-community`, `langchain-experimental`
- **LangGraph**: `langgraph>=1.1.3`
- **LLM Providers**: `langchain-openai`, `langchain-google-genai`, `langchain-ollama`, `langchain-openrouter`
- **Local Models**: `llama-cpp-python>=0.3.19`
- **MCP**: `mcp`

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

# Install in development mode
uv pip install -e .

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
