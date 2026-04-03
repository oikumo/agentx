# App REPL Module - Agent-X

**Path**: `/app/repl/`

The core interactive shell of Agent-X.

---

## Module Structure

```
app/repl/
├── base.py                    # IMainController interface
├── command.py                 # Command/CommandResult ABCs
├── command_parser.py          # CommandParser
├── console.py                 # Console, Colors
├── repl.py                    # ReplApp
├── commands/
│   ├── cli_commands.py        # quit, clear, help, read
│   ├── llm_chat_commands.py   # chat, search, function, rag, router, react
│   ├── llm_graph_commands.py  # graph, chains, reflex
│   └── math_commands.py       # sum
└── controllers/
    └── main_controller.py     # MainController
```

---

## Core Classes

### repl.py - ReplApp

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

### command.py - Abstract Base Classes

**Classes**:
- `CommandResult(ABC)` - abstract base with `apply()` method
- `Command(ABC)` - abstract base with `key`, `description`, `controller` attributes and abstract `run(arguments) -> CommandResult | None`

### base.py - Interface

**Class**: `IMainController`

Interface for command controllers with `get_commands()` and `close()` methods.

### command_parser.py - Input Parsing

**Classes**:
- `CommandData(dataclass)` - `key: str`, `arguments: list[str]`
- `CommandParser` - tokenizes user input into structured command data
  - `parse(text: str) -> CommandData | None`
  - `add(command: Command)`
  - `_parse_text_command(text_command: str) -> CommandData | None`

### console.py - Terminal Output

**Classes**:
- `Colors` - ANSI color constants (PURPLE, CYAN, DARKCYAN, BLUE, GREEN, YELLOW, RED, BOLD, UNDERLINE, END)
- `Console` - static methods:
  - `log_info(message, color)` - cyan info
  - `log_success(message)` - green success
  - `log_error(message)` - red error
  - `log_warning(message)` - yellow warning
  - `log_header(message)` - purple header with separator

---

## Controllers

### controllers/main_controller.py

**Class**: `MainController(IMainController)`

Command registry mapping keys to `Command` instances.

**Methods**:
- `__init__()` - initializes `commands: dict[str, Command]`
- `get_commands() -> list[Command]` - returns all registered commands
- `find_command(key) -> Command | None` - lookup by key
- `add_command(command: Command)` - register command
- `close()` - exits application via `exit(0)`

---

## Commands

### commands/cli_commands.py

**Classes**:
- `QuitCommand(Command)` - calls `controller.close()` to exit
- `ClearCommand(Command)` - clears console screen
- `HelpCommand(Command)` - lists all commands with descriptions, returns `CommandResultLogInfo`
- `ReadFile(Command)` - reads and displays file contents

### commands/llm_chat_commands.py

**Classes**:
- `AISearch(Command)` - runs ReAct web search agent via `create_agent_react_web_search_local().run()`
- `AIFunction(Command)` - runs function call demo via `create_agent_function_router_local().function_call()`
- `AIChat(Command)` - starts AI chat with query using `ChatLoop`. Supports two modes:
  - Interactive REPL: `chat` (no args) - enters persistent conversation loop with `ChatLoop.start_interactive()`, prints LLM responses to stdout, exits on `quit` or `exit`
  - Single-query: `chat <query>` - uses `ChatLoop.run(query)` for one-turn conversation
  - Delegates to `create_chat_loop_local()` for local LLM instance
- `RagPDF(Command)` - queries PDF with RAG via `create_agent_rag_local().run(query)`
- `AIRouterAgents(Command)` - runs router agent via `router_agent()`
- `AIReactTools(Command)` - runs ReAct agent with tools via `react_tools(llm)`

### commands/llm_graph_commands.py

**Classes**:
- `AIGraphSimple(Command)` - runs simple LangGraph workflow via `create_graph_react_web_search_cloud().run()`
- `AIGraphChains(Command)` - runs LangGraph reflector chains via `graph_chains()`
- `AIGraphReflexion(Command)` - runs LangGraph reflexion agent via `graph_reflexion_agent()`

### commands/math_commands.py

**Classes**:
- `SumCommand(Command)` - adds two integers, returns `CommandResultPrint`
- `CommandResultPrint(CommandResult)` - prints a message via `Console.log_info()`
- `CommandResultLogInfo(CommandResult)` - logs multiple info messages
