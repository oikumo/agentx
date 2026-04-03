# Project Documentation - Agent-X

> **Last Updated**: April 3, 2026  
> **Version**: 0.1.0  
> **Python**: >=3.14  
> **Package Manager**: uv

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Root Module](#root-module)
4. [agents/ - Agent Implementations](#agents---agent-implementations)
5. [app/ - Core Application](#app---core-application)
6. [app_modules/ - Extended Modules](#app_modules---extended-modules)
7. [llm_models/ - LLM Providers](#llm_models---llm-providers)
8. [tests/ - Test Suite](#tests---test-suite)
9. [Dependencies](#dependencies)
10. [Environment Variables](#environment-variables)
11. [Quick Start](#quick-start)

---

## Project Overview

Agent-X is a Python-based LLM agent framework with a REPL (Read-Eval-Print Loop) interface. It enables users to interact with various language models through command-line commands, supporting multiple interaction patterns:

- **Simple Chat**: Conversational interaction with local/cloud LLMs
- **Function Calling**: Ollama-based tool calling for function dispatch
- **RAG (Retrieval-Augmented Generation)**: PDF Q&A with FAISS vector store and Ollama embeddings
- **ReAct Web Search**: Web search agents using Tavily with structured output
- **Graph-based Reasoning**: LangGraph workflows for reflection, reflexion, and multi-agent reasoning

---

## Architecture

### Application Flow

```
main.py
  └── create_controller()
        └── MainController (command registry)
              ├── Register 14 commands
              └── ReplApp(controller).run()
                    ├── Model(session_name="test_2") - session + DB
                    ├── Loop:
                    │   ├── input("(agent-x) > ")
                    │   ├── CommandParser.parse() → CommandData(key, arguments)
                    │   ├── MainController.find_command(key)
                    │   ├── Model.log_command(HistoryEntry)
                    │   ├── command.run(arguments) → CommandResult
                    │   ├── result.apply()
                    │   └── Print command history
                    └── Exit on KeyboardInterrupt / EOFError / QuitCommand
```

### Command Registry

| Command | Class | Module | Description |
|---------|-------|--------|-------------|
| `sum` | SumCommand | app.repl.commands.math_commands | Add two integers |
| `quit` | QuitCommand | app.repl.commands.cli_commands | Exit the application |
| `clear` | ClearCommand | app.repl.commands.cli_commands | Clear console screen |
| `chat` | AIChat | app.repl.commands.llm_chat_commands | Start AI chat session |
| `router` | AIRouterAgents | app.repl.commands.llm_chat_commands | Run router agent (CSV + QR) |
| `react` | AIReactTools | app.repl.commands.llm_chat_commands | Run ReAct agent with tools |
| `search` | AISearch | app.repl.commands.llm_chat_commands | ReAct web search agent |
| `read` | ReadFile | app.repl.commands.cli_commands | Read and display a file |
| `function` | AIFunction | app.repl.commands.llm_chat_commands | AI function call demo |
| `rag` | RagPDF | app.repl.commands.llm_chat_commands | Query PDF with RAG |
| `graph` | AIGraphSimple | app.repl.commands.llm_graph_commands | Simple LangGraph workflow |
| `chains` | AIGraphChains | app.repl.commands.llm_graph_commands | LangGraph reflector chains |
| `reflex` | AIGraphReflexion | app.repl.commands.llm_graph_commands | LangGraph reflexion agent |
| `help` | HelpCommand | app.repl.commands.cli_commands | Show available commands |

### Design Patterns

- **Factory**: All `agent_*_factory.py` files encapsulate agent creation
- **Command**: `Command` ABC with `run()` method; `CommandResult` ABC with `apply()`
- **Strategy**: Different agents implement different reasoning strategies
- **State Machine**: LangGraph `StateGraph` for graph-based workflows
- **RAG Pipeline**: Standard pipeline: load → embed → store → retrieve → generate
- **Repository**: `SessionDatabase` for per-session SQLite persistence

---

## Root Module

### main.py

**Path**: `/main.py`

Application entry point. Loads environment variables via `dotenv`, creates `MainController`, registers all commands, and launches `ReplApp`.

```python
def create_controller() -> MainController:
    main_controller = MainController()
    # Register 14 commands...
    return main_controller

if __name__ == "__main__":
    controller = create_controller()
    ReplApp(controller).run()
```

### pyproject.toml

**Path**: `/pyproject.toml`

Project configuration with dependencies managed via `uv`.

- **Name**: agent-x
- **Version**: 0.1.0
- **Python**: >=3.14

### README.md

**Path**: `/README.md`

Contains environment variable documentation, package manager instructions (uv/pip), LLM configuration notes (Ollama models, OpenAI), and LangChain tool decorator patterns.

---

## agents/ - Agent Implementations

**Path**: `/agents/`

Agent implementations and factory functions. Each agent represents a different LLM interaction pattern.

### Module Structure

```
agents/
├── __init__.py
├── agent_chat_factory.py              # Factory for SimpleChat
├── agent_function_router_factory.py   # Factory for QueryRouter
├── agent_rag_factory.py               # Factory for AgentRagPdf
├── agent_react_web_search_factory.py  # Factory for AgentReactWebSearch
├── graph_react_web_search_factory.py  # Factory for GraphReactWebSearch
├── chat/
│   ├── __init__.py
│   └── simple_chat.py                # SimpleChat class
├── function_tool_router/
│   ├── __init__.py
│   ├── function_call.py              # QueryRouter class
│   ├── functions.py                  # Tool functions
│   └── route.py                      # Route class
├── graph_react_web_search/
│   ├── __init__.py
│   └── graph_react_web_search.py     # GraphReactWebSearch class
├── rag_pdf/
│   ├── __init__.py
│   └── agent_rag_pdf.py              # AgentRagPdf class
└── react_web_search/
    ├── __init__.py
    ├── agent_react_web_search.py     # AgentReactWebSearch class
    ├── prompt.py                     # ReAct prompt template
    ├── schemas.py                    # Pydantic models
    └── search_agent.py               # search_agent() function
```

### agents/chat/simple_chat.py

**Class**: `SimpleChat`

Wraps a `BaseChatModel` with a prompt template chain for simple conversational interaction.

**Methods**:
- `__init__(llm: BaseChatModel)` - stores LLM instance
- `run(query: str, information: str = "")` - creates prompt template chain and invokes LLM

**Dependencies**: `langchain_core.language_models.BaseChatModel`, `langchain_core.prompts.PromptTemplate`

### agents/agent_chat_factory.py

**Function**: `create_agent_chat_local() -> SimpleChat`

Factory function that creates a `SimpleChat` with a local LlamaCpp Qwen 2.5 model (context size 32768).

### agents/react_web_search/

#### search_agent.py

**Function**: `search_agent(llm: BaseLanguageModel)`

Creates a full ReAct agent with Tavily web search and structured output parsing via Pydantic.

**Flow**:
1. Creates `TavilySearch` tool
2. Sets up `PydanticOutputParser` with `AgentResponse` schema
3. Creates ReAct prompt with format instructions
4. Builds chain: `agent_executor | extract_output | parse_output`
5. Invokes with sample query about Chile news

**Classes**:
- `Source(BaseModel)` - schema with `url: str`
- `AgentResponse(BaseModel)` - schema with `answer: str` and `sources: List[Source]`

#### agent_react_web_search.py

**Class**: `AgentReactWebSearch`

Thin wrapper delegating to `search_agent()`.

**Methods**:
- `__init__(llm: BaseChatModel)` - stores LLM
- `run()` - delegates to `search_agent(llm=self.llm)`

#### prompt.py

**Constant**: `REACT_PROMPT_WITH_FORMAT_INSTRUCTIONS`

ReAct prompt template with `{tools}`, `{tool_names}`, `{format_instructions}`, `{input}`, and `{agent_scratchpad}` placeholders.

#### schemas.py

Duplicate Pydantic models (`Source`, `AgentResponse`) for structured agent response.

#### agent_react_web_search_factory.py

**Function**: `create_agent_react_web_search_local() -> AgentReactWebSearch`

Factory creating `AgentReactWebSearch` with local LlamaCpp Qwen 2.5 (context size 32768).

### agents/rag_pdf/

#### agent_rag_pdf.py

**Class**: `AgentRagPdf`

PDF ingestion → FAISS vector store → retrieval QA chain pipeline.

**Methods**:
- `__init__(pdf_path: str, vectorstore_path: str, llm: BaseChatModel, embeddings: Embeddings)` - stores configuration
- `run(query: str)` - pulls retrieval QA prompt from LangChain Hub, calls `rag_pdf()`
- `rag_pdf(query, pdf_path, vectorstore_path, retrieval_qa_chat_prompt, llm, embeddings)` - full RAG pipeline:
  1. Load PDF via `pdf_loader()`
  2. Create FAISS vector store via `create_faiss()`
  3. Build stuff documents chain via `create_stuff_documents_chain()`
  4. Build retrieval chain via `create_retrieval_chain()`
  5. Invoke and print answer

**Dependencies**: `langchain_classic.hub`, `langchain_classic.chains.*`, `app_modules.document_loaders.pdf_loader`, `app_modules.data_stores.vector_store_faiss`

#### agent_rag_factory.py

**Function**: `create_agent_rag_local() -> AgentRagPdf`

Factory creating `AgentRagPdf` with:
- Local LlamaCpp Qwen 2.5 (context size 32768)
- Ollama embeddings (`nomic-embed-text`)
- PDF path: `_resources/react.pdf`
- Vector store path: timestamped directory under `local_vector_databases/`

### agents/function_tool_router/

#### function_call.py

**Class**: `QueryRouter`

Ollama tool calling to dispatch function calls based on user query.

**Methods**:
- `__init__(routes: list[Route])` - stores route definitions
- `function_call(model="functiongemma:270m-it-fp16")` - sends prompt to Ollama with tools, matches response to function, executes, and sends result back to LLM for final response

**Flow**:
1. Sends user message to Ollama with tool definitions
2. Parses response to identify tool call
3. Looks up and executes the function
4. Sends tool result back to Ollama
5. Prints final response

**Dependencies**: `rich`, `ollama`, `app.repl.console`

#### functions.py

Tool functions available for the query router:

- `get_weather(city: str) -> str` - returns mock weather data as JSON (22°C, sunny)
- `get_best_game(year: str) -> str` - returns mock game data as JSON (Dark Souls)
- `calculate(expression: str) -> str` - evaluates math expression via `eval()` (with safety warning)

#### route.py

**Class**: `Route`

Maps function name to callable for the router.

**Methods**:
- `__init__(function_name: str, route: Callable)` - stores name and callable
- `run(args)` - executes the callable

#### agent_function_router_factory.py

**Function**: `create_agent_function_router_local() -> QueryRouter`

Factory creating `QueryRouter` with routes for `get_weather`, `get_best_game`, and `calculate`.

### agents/graph_react_web_search/

#### graph_react_web_search.py

**Class**: `GraphReactWebSearch`

LangGraph state machine with reasoning/act nodes for ReAct web search with function calling.

**Methods**:
- `__init__(llm: BaseChatModel, max_search_results: int)` - binds `TavilySearch` and `triple` tool to LLM
- `run()` - builds `StateGraph` with `agent_reasoning` and `act` nodes, compiles and invokes with a query about temperature in Santiago and Tokyo
- `run_agent_reasoning(state: MessagesState) -> MessagesState` - LLM reasoning node
- `should_continue(state: MessagesState) -> str` - checks for tool calls to decide whether to continue to `ACT` node or `END`

**Tool**: `@tool triple(num: float) -> float` - triples a number

**Graph Flow**:
```
ENTRY → agent_reasoning → should_continue?
  ├── Has tool calls → act (ToolNode) → agent_reasoning (loop)
  └── No tool calls → END
```

**Dependencies**: `langchain_tavily.TavilySearch`, `langgraph.graph.*`, `langgraph.prebuilt.ToolNode`

#### graph_react_web_search_factory.py

**Functions**:
- `create_graph_react_web_search_local() -> GraphReactWebSearch` - uses local LlamaCpp Qwen 2.5
- `create_graph_react_web_search_cloud() -> GraphReactWebSearch` - uses OpenAI GPT-3.5-turbo

---

## app/ - Core Application

**Path**: `/app/`

Core application module containing the REPL system, data models, database layer, security utilities, and common helpers.

### Module Structure

```
app/
├── __init__.py
├── common/
│   ├── __init__.py
│   ├── files/
│   │   ├── __init__.py
│   │   └── file_utils.py          # save_to_output()
│   └── utils/
│       ├── __init__.py
│       ├── file_utils.py          # directory management
│       └── utils.py               # safe_int(), clear_console()
├── model/
│   ├── __init__.py
│   ├── model.py                   # Model facade
│   ├── model_entities.py          # HistoryEntry dataclass
│   ├── db/
│   │   ├── __init__.py
│   │   ├── data_base.py           # SessionDatabase
│   │   └── database_definition.py # Table schemas
│   └── user_sessions/
│       ├── __init__.py
│       └── session.py             # Session lifecycle
├── repl/
│   ├── __init__.py
│   ├── base.py                    # IMainController interface
│   ├── command.py                 # Command/CommandResult ABCs
│   ├── command_parser.py          # CommandParser
│   ├── console.py                 # Console, Colors
│   ├── repl.py                    # ReplApp
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── cli_commands.py        # quit, clear, help, read
│   │   ├── llm_chat_commands.py   # chat, search, function, rag, router, react
│   │   ├── llm_graph_commands.py  # graph, chains, reflex
│   │   └── math_commands.py       # sum
│   └── controllers/
│       ├── __init__.py
│       └── main_controller.py     # MainController
└── security/
    ├── __init__.py
    ├── security.py                # is_directory_allowed_to_deletion()
    └── security_constants.py      # deletion constants
```

### app/repl/ - REPL System

#### repl.py

**Class**: `ReplApp`

Main application loop.

**Methods**:
- `__init__(controller: MainController)` - stores controller and creates `CommandParser`
- `run()` - main loop:
  1. Creates `Model(session_name="test_2")`
  2. Reads user input
  3. Parses via `CommandParser`
  4. Finds command via `MainController`
  5. Logs command to Model
  6. Executes command
  7. Applies result if any
  8. Prints command history
  9. Exits on `KeyboardInterrupt`, `EOFError`, or `QuitCommand`

#### command.py

**Classes**:
- `CommandResult(ABC)` - abstract base with `apply()` method
- `Command(ABC)` - abstract base with `key`, `description`, `controller` attributes and abstract `run(arguments) -> CommandResult | None`

#### base.py

**Class**: `IMainController`

Interface for command controllers with `get_commands()` and `close()` methods.

#### command_parser.py

**Classes**:
- `CommandData(dataclass)` - `key: str`, `arguments: list[str]`
- `CommandParser` - tokenizes user input into structured command data
  - `parse(text: str) -> CommandData | None`
  - `add(command: Command)`
  - `_parse_text_command(text_command: str) -> CommandData | None`

#### console.py

**Classes**:
- `Colors` - ANSI color constants (PURPLE, CYAN, DARKCYAN, BLUE, GREEN, YELLOW, RED, BOLD, UNDERLINE, END)
- `Console` - static methods:
  - `log_info(message, color)` - cyan info
  - `log_success(message)` - green success
  - `log_error(message)` - red error
  - `log_warning(message)` - yellow warning
  - `log_header(message)` - purple header with separator

#### controllers/main_controller.py

**Class**: `MainController(IMainController)`

Command registry mapping keys to `Command` instances.

**Methods**:
- `__init__()` - initializes `commands: dict[str, Command]`
- `get_commands() -> list[Command]` - returns all registered commands
- `find_command(key) -> Command | None` - lookup by key
- `add_command(command: Command)` - register command
- `close()` - exits application via `exit(0)`

#### commands/cli_commands.py

**Classes**:
- `QuitCommand(Command)` - calls `controller.close()` to exit
- `ClearCommand(Command)` - clears console screen
- `HelpCommand(Command)` - lists all commands with descriptions, returns `CommandResultLogInfo`
- `ReadFile(Command)` - reads and displays file contents

#### commands/llm_chat_commands.py

**Classes**:
- `AISearch(Command)` - runs ReAct web search agent via `create_agent_react_web_search_local().run()`
- `AIFunction(Command)` - runs function call demo via `create_agent_function_router_local().function_call()`
- `AIChat(Command)` - starts AI chat with query via `create_agent_chat_local().run(query, information)`
- `RagPDF(Command)` - queries PDF with RAG via `create_agent_rag_local().run(query)`
- `AIRouterAgents(Command)` - runs router agent via `router_agent()`
- `AIReactTools(Command)` - runs ReAct agent with tools via `react_tools(llm)`

#### commands/llm_graph_commands.py

**Classes**:
- `AIGraphSimple(Command)` - runs simple LangGraph workflow via `create_graph_react_web_search_cloud().run()`
- `AIGraphChains(Command)` - runs LangGraph reflector chains via `graph_chains()`
- `AIGraphReflexion(Command)` - runs LangGraph reflexion agent via `graph_reflexion_agent()`

#### commands/math_commands.py

**Classes**:
- `SumCommand(Command)` - adds two integers, returns `CommandResultPrint`
- `CommandResultPrint(CommandResult)` - prints a message via `Console.log_info()`
- `CommandResultLogInfo(CommandResult)` - logs multiple info messages

### app/model/ - Data Persistence Layer

#### model.py

**Class**: `Model`

Session + DB facade for logging and retrieving command history.

**Methods**:
- `__init__(session_name: str)` - creates `Session` and `SessionDatabase`, raises `Exception` if session creation fails
- `log_command(entry: HistoryEntry)` - inserts history entry into DB
- `get_command_history() -> list[HistoryEntry]` - retrieves all history entries

#### model_entities.py

**Class**: `HistoryEntry(dataclass)` - `command: str`

#### db/data_base.py

**Class**: `SessionDatabase`

Per-session SQLite database with `history` and `users` tables.

**Methods**:
- `__init__(session: Session)` - creates DB tables
- `_create()` - creates tables via SQLite
- `_get_session_path()` - constructs DB file path from session directory
- `insert_history_entry(info: str) -> bool` - inserts a history row with UTC timestamp
- `select_history_entry() -> list[TableHistory.History] | None` - retrieves all history rows
- `_insert(query, parameters) -> bool` - generic insert (returns False on success, True on error)
- `_select_all(table) -> list[Any] | None` - generic select with table name validation against allowed tables

#### db/database_definition.py

**Classes**:
- `TableHistory` - constants and schema for history table
  - `TABLE_NAME = "history"`
  - `TABLE_HISTORY` - CREATE SQL with `id`, `command`, `created_at`
  - `INSERT_HISTORY` - INSERT SQL
  - `History(dataclass)` - `id: int`, `name: str`, `created_at: str`
- `TableUser` - constants and schema for users table
  - `TABLE_NAME = "users"`
  - `TABLE_USER` - CREATE SQL with `id`, `name`, `age`
  - `INSERT_USER` - INSERT SQL

#### user_sessions/session.py

**Class**: `Session`

Session lifecycle management (create/destroy session directories).

**Methods**:
- `__init__(name: str)` - sanitizes session name (replaces spaces with underscores, lowercases)
- `name` (property) - returns session name
- `directory` (property) - returns session directory path
- `create()` - creates timestamped directory, returns success boolean
- `is_created()` - checks if directory exists
- `destroy() -> bool` - deletes session directory with security validation

### app/security/ - Security Utilities

#### security.py

**Function**: `is_directory_allowed_to_deletion(directory_path: str) -> bool`

Validates that a directory path is:
1. Within the current working directory
2. Within one of the allowed deletion directories (`local_sessions`)

Raises `PermissionError` if validation fails.

#### security_constants.py

**Constants**:
- `SESSION_DEFAULT_NAME = "default"`
- `SESSION_DEFAULT_BASE_DIRECTORY = "local_sessions"`
- `DIRECTORIES_DELETION_ALLOWED = ["local_sessions"]`

### app/common/ - Shared Utilities

#### utils/utils.py

**Functions**:
- `safe_int(value: str) -> int | None` - safe integer conversion, returns None on failure
- `clear_console()` - clears terminal screen (cross-platform: `cls` for Windows, `clear` for others)

#### utils/file_utils.py

**Functions**:
- `create_directory_with_timestamp(name: str, base_directory) -> str | None` - creates a timestamped directory (`{name}_{YYYY-MM-DD-HH-MM-SS}`), returns path or None on error
- `directory_exists(directory: str)` - checks if directory exists
- `dangerous_delete_directory(directory_path: str) -> bool` - deletes directory with security validation and warning

#### files/file_utils.py

**Function**: `save_to_output(text: str)` - writes text to `local/output.txt`

---

## app_modules/ - Extended Modules

**Path**: `/app_modules/`

Extended application modules containing LLM integrations, data stores, document loaders, and web ingestion pipelines.

### Module Structure

```
app_modules/
├── __init__.py
├── data_stores/
│   ├── __init__.py
│   └── vector_store_faiss.py      # FAISS vector store
├── document_loaders/
│   ├── __init__.py
│   └── pdf_loader.py              # PDF loading
├── llm/
│   ├── __init__.py
│   ├── langchain/
│   │   ├── __init__.py
│   │   ├── simple_tool.py         # (unused)
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── simple_tool.py     # multiply tool
│   │   │   └── tavily_web_search/
│   │   │       ├── __init__.py
│   │   │       └── simple_tool_search_tavily.py
│   │   └── react_agents/
│   │       ├── __init__.py
│   │       ├── react_agents_tools/
│   │       │   ├── __init__.py
│   │       │   ├── callbacks.py   # AgentCallbackHandler
│   │       │   └── react_tools.py # manual ReAct loop
│   │       └── router_agents/
│   │           ├── __init__.py
│   │           ├── router_react_agent.py
│   │           └── agent_executors/
│   │               ├── __init__.py
│   │               ├── csv_agent.py
│   │               └── qr_react_agent.py
│   └── langgraph/
│       ├── __init__.py
│       ├── graph_reflector_chain/
│       │   ├── __init__.py
│       │   ├── chains.py          # generate/reflect chains
│       │   └── graph_chains.py    # StateGraph
│       └── graph_reflexion_agent/
│           ├── __init__.py
│           ├── chains.py          # first_responder, revisor
│           ├── graph_reflexion_agent.py
│           ├── schemas.py         # Pydantic models
│           └── tool_executor.py   # TavilySearch execution
└── web_ingestion_app/
    ├── __init__.py
    ├── documents.py               # document processing
    ├── helpers.py                 # JSONL helpers
    ├── tavily.py                  # WebExtract
    ├── web_ingestion.py           # entry point script
    └── web_ingestion_app.py       # WebIngestionApp
```

### app_modules/data_stores/

#### vector_store_faiss.py

**Function**: `create_faiss(vectorstore_path: str, docs: List[Document], embeddings: Embeddings)`

Builds FAISS index from documents, saves to disk, reloads and returns the vector store.

**Flow**:
1. `FAISS.from_documents(docs, embeddings)`
2. `vectorstore.save_local(vectorstore_path)`
3. `FAISS.load_local(vectorstore_path, embeddings, allow_dangerous_deserialization=True)`

### app_modules/document_loaders/

#### pdf_loader.py

**Function**: `pdf_loader(pdf_path: str)`

Loads PDF via `PyPDFLoader`, splits with `CharacterTextSplitter` (chunk_size=1000, chunk_overlap=30, separator="\n").

### app_modules/llm/langchain/

#### tools/simple_tool.py

**Function**: `@tool multiply(x: float, y: float) -> float`

Standalone multiply tool definition.

**Function**: `simple_tool(llm: BaseLanguageModel)` - creates tool-calling agent with multiply tool, invokes with test prompt.

#### tools/tavily_web_search/simple_tool_search_tavily.py

**Function**: `@tool multiply(x: float, y: float) -> float`

**Function**: `simple_tool_search_tavily(llm: BaseLanguageModel)` - creates tool-calling agent with `TavilySearchResults` + `multiply` tools, invokes with weather comparison query.

#### react_agents/react_agents_tools/callbacks.py

**Class**: `AgentCallbackHandler(BaseCallbackHandler)`

Callback handler that prints prompts and LLM responses during agent execution.

**Methods**:
- `on_llm_start(...)` - prints prompts
- `on_llm_end(response: LLMResult, ...)` - prints LLM response text

#### react_agents/react_agents_tools/react_tools.py

**Function**: `@tool get_text_length(text: str) -> int` - returns character count

**Function**: `find_tool_by_name(tools: List[Tool], tool_name: str) -> Tool` - lookup helper

**Function**: `react_tools(llm: BaseLanguageModel)` - manual ReAct loop implementation:
1. Sets up prompt with tool descriptions
2. Configures LLM stop tokens and callbacks
3. Builds agent chain: `{"input", "agent_scratchpad"} | prompt | llm | ReActSingleInputOutputParser`
4. Runs manual loop: invoke agent → if `AgentAction`, execute tool → append to intermediate steps → repeat until `AgentFinish`
5. Prints final return values

#### react_agents/router_agents/router_react_agent.py

**Function**: `router_agent()`

Creates a router agent that dispatches between:
- **Python Agent**: QR code generation via `PythonREPLTool`
- **CSV Agent**: Pandas-based CSV querying of `episode_info.csv`

**Flow**:
1. Creates LlamaCpp Qwen 2.5 LLM
2. Wraps `create_qr_react_agent_executor` and `create_csv_agent_executor` as `Tool` instances
3. Creates ReAct agent with both tools
4. Invokes with two test queries:
   - "which season has the most episodes?"
   - "Create a directory the 'udemy_qr' folder, 15 DIFFERENT qrcodes..."

#### react_agents/router_agents/agent_executors/csv_agent.py

**Function**: `create_csv_agent_executor(llm: BaseLanguageModel, file_path: str) -> AgentExecutor`

Creates CSV agent using `create_csv_agent` from `langchain_experimental`. Uses `allow_dangerous_code=True` for pandas execution.

#### react_agents/router_agents/agent_executors/qr_react_agent.py

**Function**: `create_qr_react_agent_executor(llm: BaseLanguageModel)`

Creates ReAct agent with `PythonREPLTool` for QR code generation. Instructions tell the agent to write and execute Python code, handle errors, and use the `qrcode` package.

### app_modules/llm/langgraph/

#### graph_reflector_chain/chains.py

**Variables**:
- `reflection_prompt` - ChatPromptTemplate for critiquing tweets (viral twitter influencer persona)
- `generation_prompt` - ChatPromptTemplate for generating tweets (twitter techie influencer persona)
- `llm = ChatOpenAI()` - default OpenAI LLM
- `generate_chain = generation_prompt | llm`
- `reflect_chain = reflection_prompt | llm`

#### graph_reflector_chain/graph_chains.py

**Function**: `graph_chains()`

Builds `StateGraph` with generate ↔ reflect loop for tweet improvement.

**Flow**:
1. Defines `MessageGraph` TypedDict with `messages: Annotated[list[BaseMessage], add_messages]`
2. Creates `generation_node` and `reflection_node`
3. Sets up graph: ENTRY → generate → should_continue?
   - If messages > 6 → END
   - Otherwise → reflect → generate (loop)
4. Invokes with a tweet about LangChainAI tool calling
5. Saves output to `local/output.txt`

#### graph_reflexion_agent/schemas.py

**Pydantic Models**:
- `Reflection(BaseModel)` - `missing: str`, `superfluous: str` critique fields
- `AnswerQuestion(BaseModel)` - `answer: str`, `reflection: Reflection`, `search_queries: List[str]`
- `ReviseAnswer(AnswerQuestion)` - extends with `references: List[str]`

#### graph_reflexion_agent/chains.py

**Variables**:
- `llm = ChatOpenAI(model="o4-mini")`
- `first_responder` - prompt + LLM bound to `AnswerQuestion` tool
- `revisor` - prompt + LLM bound to `ReviseAnswer` tool with revision instructions

**Prompts**:
- `actor_prompt_template` - expert researcher persona with time injection
- `first_responder_prompt_template` - "Provide a detailed ~250 word answer"
- `revise_instructions` - instructions for revision with citations and word limits

#### graph_reflexion_agent/tool_executor.py

**Function**: `run_queries(search_queries: list[str], **kwargs)` - batches TavilySearch queries

**Variable**: `execute_tools = ToolNode([...])` - tool node wrapping `run_queries` for `AnswerQuestion` and `ReviseAnswer`

#### graph_reflexion_agent/graph_reflexion_agent.py

**Function**: `graph_reflexion_agent()`

Complete reflexion workflow: draft → execute_tools → revise → loop.

**Flow**:
1. `draft_node` - generates initial response via `first_responder`
2. `execute_tools` - runs TavilySearch via `execute_tools` ToolNode
3. `revise_node` - revises answer via `revisor`
4. `event_loop` - checks iteration count (max 2), decides whether to continue or END
5. Graph: START → draft → execute_tools → revise → event_loop?
   - If iterations <= MAX → execute_tools (loop)
   - Otherwise → END
6. Invokes with query about AI-Powered SOC startups
7. Extracts and prints final answer, saves to `local/output.txt`

### app_modules/web_ingestion_app/

#### tavily.py

**Class**: `WebExtract`

TavilyExtract and TavilyMap wrappers for web content extraction.

**Methods**:
- `__init__(max_depth: int, max_breadth: int, max_pages: int)` - initializes `TavilyExtract` and `TavilyMap`
- `async def extract_batch(urls: List[str], batch_num: int) -> List[Dict[str, Any]]` - async extraction from a batch of URLs
- `async def async_extract(urls_batches: List[List[str]])` - concurrent extraction across all batches, returns list of `Document` objects

#### helpers.py

**Functions**:
- `save_docs(all_docs: list[Any], result_json_file_path: str)` - writes documents to JSONL file via `model_dump_json()`
- `chunk_urls(urls: List[str], chunk_size: int = 3) -> List[List[str]]` - splits URL list into chunks
- `load_docs_from_jsonl(file_path)` - reads documents from JSONL file

#### documents.py

**Functions**:
- `async def index_documents_async(vectorstore, documents: List[Document], batch_size: int = 50)` - async batched document insertion into vector store
- `process_documents(result_json_file_path: str) -> list[Document]` - loads docs from JSONL, splits with `RecursiveCharacterTextSplitter` (chunk_size=4000, chunk_overlap=200)

#### web_ingestion_app.py

**Class**: `WebIngestionApp`

Orchestrates the complete web ingestion pipeline.

**Methods**:
- `__init__(vectorstore: VectorStore, tav: WebExtract, site_url: str, result_json_file_path: str)` - stores configuration
- `configure(site_url: str, result_json_file_path: str) -> WebIngestionApp` - fluent configuration
- `async def run()` - async full pipeline:
  1. Map site URLs via TavilyMap
  2. Extract content in batches
  3. Save docs to JSONL
  4. Process and chunk documents
  5. Index into vector store
- `async def data_ingestion(site_url: str)` - maps site URLs and extracts content

**Pipeline Flow**:
```
TavilyMap → chunk_urls → WebExtract.async_extract → save_docs (JSONL)
    → process_documents → index_documents_async → VectorStore
```

#### web_ingestion.py

Standalone entry point script for web ingestion. Creates session, vector store (Chroma), and runs `WebIngestionApp`.

**Note**: Imports `create_vectorstore_chroma` from `modules.llm_models` which appears to be a missing module in the current codebase.

---

## llm_models/ - LLM Providers

**Path**: `/llm_models/`

LLM model providers and vector store integrations. Supports both cloud-hosted and locally-run models.

### Module Structure

```
llm_models/
├── __init__.py
├── cloud/
│   ├── __init__.py
│   ├── google/
│   │   ├── __init__.py
│   │   └── google_gemini.py     # Gemini wrapper
│   └── open_ai/
│       ├── __init__.py
│       └── open_ai_gpt.py       # GPT wrappers
├── local/
│   ├── __init__.py
│   ├── llama_cpp_factory.py     # Pre-configured factory
│   ├── llama_cpp/
│   │   ├── __init__.py
│   │   ├── llamacpp.py          # LlamaCpp factory class
│   │   └── llamacpp_config.py   # Pydantic config
│   └── ollama/
│       ├── __init__.py
│       └── ollama_embeddings.py # Ollama embeddings
└── vectorstores/
    ├── __init__.py
    └── vectorstore_pinecone.py  # Pinecone wrapper
```

### llm_models/cloud/open_ai/open_ai_gpt.py

**Functions**:
- `get_remote_llm_openai_gpt4() -> ChatOpenAI` - returns GPT-4-turbo (temperature=0)
- `get_remote_llm_openai_gpt3_5_turbo() -> ChatOpenAI` - returns GPT-3.5-turbo

### llm_models/cloud/google/google_gemini.py

**Function**: `get_remote_llm_google_gemini() -> ChatGoogleGenerativeAI`

Returns Gemini 2.5 Flash Lite (temperature=1.0, max_retries=2).

### llm_models/local/llama_cpp/

#### llamacpp_config.py

**Class**: `LlamaCppConfig(BaseModel)`

Pydantic configuration for Llama.cpp parameters:
- `model_filename: str = ""`
- `temperature: int = 0.7`
- `context_size: int = 4096`
- `max_tokens: int = 512`
- `top_p: int = 0.5`
- `batch_size: int = 64`

#### llamacpp.py

**Class**: `LlamaCpp`

Factory for creating local `ChatLlamaCpp` instances from GGUF model files.

**Methods**:
- `__init__(llama_cpp_cache_dir: str)` - stores cache directory
- `create_model_instance(config: LlamaCppConfig) -> BaseChatModel | None` - creates `ChatLlamaCpp` instance, returns None if model file not found

**Configuration**:
- `n_threads = multiprocessing.cpu_count() - 1`
- `repeat_penalty = 1.5`
- `verbose = False`

#### llama_cpp_factory.py

**Constants**:
- `LLAMA_CPP_MODEL_QWEN_2_5 = "Qwen_Qwen2.5-1.5B-Instruct-GGUF_qwen2.5-1.5b-instruct-q4_k_m.gguf"`
- `LLAMA_CPP_MODEL_QWEN_3 = "unsloth_Qwen3-4B-GGUF_Qwen3-4B-Q2_K_L.gguf"`
- `LLAMA_CPP_MODEL_QWEN_3_5_OPUS = "Jackrong_Qwen3.5-2B-Claude-4.6-Opus-Reasoning-Distilled-GGUF_Qwen3.5-2B.Q4_K_M.gguf"`
- `LLAMA_CPP_MODELS_CACHE_PATH = "LLAMA_CPP_MODELS_CACHE_PATH"` (env var name)

**Variable**: `model_factory_llamacpp = LlamaCpp(os.environ[LLAMA_CPP_MODELS_CACHE_PATH])` - pre-configured singleton-style factory instance

### llm_models/local/ollama/

#### ollama_embeddings.py

**Function**: `create_embeddings_model() -> Embeddings`

Returns `OllamaEmbeddings` with `nomic-embed-text` model.

### llm_models/vectorstores/

#### vectorstore_pinecone.py

**Function**: `create_vectorstore_pinecone(index_name: str) -> PineconeVectorStore`

Creates Pinecone vector store with OpenAI `text-embedding-3-small` embeddings (chunk_size=50, retry_min_seconds=10).

---

## tests/ - Test Suite

**Path**: `/tests/`

Unit tests using `unittest` framework.

### Module Structure

```
tests/
├── __init__.py
├── integration/
│   └── __init__.py
└── unit/
    ├── __init__.py
    ├── app/
    │   └── __init__.py
    └── applications/
        ├── __init__.py
        └── repl_app/
            ├── __init__.py
            └── command_line_controller/
                ├── __init__.py
                ├── command_parser_test.py
                └── commands_controller_test.py
```

### tests/unit/applications/repl_app/command_line_controller/command_parser_test.py

**Classes**:
- `CommandDataTest(unittest.TestCase)` - tests for `CommandData` dataclass:
  - `test_creation_stores_key_and_arguments`
  - `test_empty_arguments_list_is_valid`
  - `test_equality_is_value_based`
  - `test_inequality_on_different_key`
- `CommandParserTest(unittest.TestCase)` - tests for `CommandParser`:
  - `test_add_appends_command_to_list`
  - `test_add_multiple_commands`
  - `test_parse_single_word_returns_command_data`
  - `test_parse_command_with_arguments`
  - `test_parse_command_with_single_argument`
  - `test_parse_empty_string_returns_none_and_warns`
  - `test_parse_whitespace_only_returns_none_and_warns`
  - `test_parse_extra_whitespace_between_tokens_is_normalised`

### tests/unit/applications/repl_app/command_line_controller/commands_controller_test.py

**Class**: `CommandsControllerTest(unittest.TestCase)`

Tests for command registration and lookup:
- `test_empty_on_init`
- `test_add_command_makes_it_findable`
- `test_add_multiple_commands`
- `test_find_command_returns_none_for_unknown_key`
- `test_get_commands_returns_all_registered_commands`

**Note**: Tests reference `CommandsController` which maps to `MainController` in the current codebase.

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

## Dependencies

### Core

| Package | Version | Purpose |
|---------|---------|---------|
| langchain | >=1.2.13 | LLM framework |
| langchain-community | >=0.4.1 | Community integrations |
| langchain-ollama | >=1.0.1 | Ollama integration |
| langchain-openai | >=1.1.12 | OpenAI integration |
| langchain-pinecone | >=0.2.12 | Pinecone vector store |
| langchain-tavily | >=0.2.17 | Tavily web search |
| langchainhub | >=0.1.21 | LangChain Hub for prompts |
| langchain-experimental | >=0.4.1 | Experimental features |
| langchain-google-genai | >=4.2.1 | Google Gemini integration |
| langchain-chroma | >=1.1.0 | Chroma vector store |
| langgraph | >=1.1.3 | Graph-based workflows |
| llama-cpp-python | >=0.3.19 | Local LLM inference |

### Tools & Utilities

| Package | Version | Purpose |
|---------|---------|---------|
| chromadb | >=1.5.5 | Vector database |
| faiss-cpu | >=1.13.2 | Local vector store |
| pypdf | >=6.9.2 | PDF parsing |
| python-dotenv | >=1.2.2 | Environment variables |
| pandas | >=3.0.1 | Data manipulation |
| pillow | >=12.1.1 | Image processing |
| qrcode | >=8.2 | QR code generation |
| tabulate | >=0.9.0 | Table formatting |
| grandalf | >=0.8 | Graph visualization |
| qr | >=0.6.0 | QR code utilities |

### Dev

| Package | Version | Purpose |
|---------|---------|---------|
| pytest | >=9.0.2 | Testing framework |

---

## Environment Variables

### Required

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | OpenAI API authentication |
| `TAVILY_API_KEY` | Tavily web search API |
| `LLAMA_CPP_MODELS_CACHE_PATH` | Path to local GGUF model files |

### Optional

| Variable | Purpose |
|----------|---------|
| `LANGSMITH_TRACING` | Enable LangSmith tracing (`true`) |
| `LANGSMITH_ENDPOINT` | LangSmith endpoint URL |
| `LANGSMITH_API_KEY` | LangSmith API key |
| `LANGSMITH_PROJECT` | LangSmith project name |
| `PINECONE_API_KEY` | Pinecone vector store API key |
| `INDEX_NAME` | Pinecone index name |
| `INDEX_NAME_OLLAMA` | Ollama-specific index name |
| `INDEX_NAME_OPENAI` | OpenAI-specific index name |
| `INDEX_NAME_DOCUMENT_HELPER` | Document helper index name |

---

## Quick Start

```bash
# Install dependencies
uv sync

# Run the application
python main.py
```

### Available Commands

Once running, use `help` to see all available commands:

```
(agent-x) > help
```

### LLM Configuration

**Cloud Models**: Set `OPENAI_API_KEY` in `.env` for OpenAI models.

**Local Models**: 
- Set `LLAMA_CPP_MODELS_CACHE_PATH` to directory containing GGUF model files
- Install Ollama and pull `nomic-embed-text` for embeddings
- Install Ollama and pull `functiongemma:270m-it-fp16` for function calling

---

## Code Style

- **Language**: Python >=3.14
- **Line Length**: 88 characters
- **Docstrings**: Google-style for public functions/classes
- **Naming**:
  - Functions/variables: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
  - Private members: `_prefix`
  - Modules/files: `snake_case.py`
- **Type Hints**: Preferred where beneficial
- **Tests**: Mirror source structure; unit tests focus on pure logic

---

## Key Architectural Decisions

1. **Factory Pattern**: All agents are created via factory functions, decoupling instantiation from usage
2. **Command Pattern**: All REPL commands implement the `Command` ABC, ensuring consistent interface
3. **Session-Based Persistence**: Each REPL session creates a timestamped directory with its own SQLite database
4. **Security-First Deletion**: Directory deletion is restricted to `local_sessions/` within the current working directory
5. **Local-First Default**: All agents default to local LlamaCpp models, with cloud options available via separate factory functions
6. **LangChain Ecosystem**: Heavy reliance on LangChain ecosystem (langchain, langgraph, langchain-community) for LLM abstractions
7. **Vector Store Flexibility**: Supports FAISS (local), Pinecone (cloud), and Chroma (local) for different deployment scenarios
