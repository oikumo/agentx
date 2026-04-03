# App - REPL Module

## Overview
Read-Eval-Print Loop system - the core interactive shell of Agent-X. Handles command input, parsing, dispatching, and output.

## Structure

```
repl/
├── base.py                        # IMainController interface
├── command.py                     # Command and CommandResult ABCs
├── command_parser.py              # Input tokenization into key + arguments
├── console.py                     # Colored output utilities (Colors, Console)
├── repl.py                        # ReplApp main loop
├── commands/
│   ├── cli_commands.py            # quit, clear, help, read
│   ├── llm_chat_commands.py       # chat, search, function, rag, router, react
│   ├── llm_graph_commands.py      # graph, chains, reflex
│   └── math_commands.py           # sum
└── controllers/
    └── main_controller.py         # MainController - command registry
```

## Key Classes

| Class | File | Description |
|-------|------|-------------|
| `ReplApp` | `repl.py` | Main application loop |
| `Command` (ABC) | `command.py` | Base for all commands; `run(args) -> CommandResult | None` |
| `CommandResult` (ABC) | `command.py` | Post-execution action via `apply()` |
| `CommandParser` | `command_parser.py` | Tokenizes input into `CommandData(key, arguments)` |
| `IMainController` | `base.py` | Interface for command controllers |
| `MainController` | `controllers/main_controller.py` | Command registry (`dict[str, Command]`) |
| `Console` | `console.py` | Static colored logging methods |

## Execution Flow
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

## Command Registration
Commands are registered via `MainController.add_command(command)`. The controller stores them in a `dict[str, Command]` keyed by `command.key`.
