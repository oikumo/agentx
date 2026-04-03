# App Module

## Overview
Core application module containing the REPL system, data models, database layer, security utilities, and common helpers.

## Structure

```
app/
├── common/
│   ├── files/
│   │   └── file_utils.py              # File saving utilities
│   └── utils/
│       ├── file_utils.py              # Directory creation, safe deletion
│       └── utils.py                   # General utilities (safe_int, clear_console)
├── model/
│   ├── model.py                       # Model class (session + DB facade)
│   ├── model_entities.py              # HistoryEntry dataclass
│   ├── db/
│   │   ├── data_base.py               # SessionDatabase - SQLite wrapper
│   │   └── database_definition.py     # Table schemas (history, users)
│   └── user_sessions/
│       └── session.py                 # Session lifecycle management
├── repl/
│   ├── base.py                        # IMainController interface
│   ├── command.py                     # Command and CommandResult ABCs
│   ├── command_parser.py              # Input tokenization
│   ├── console.py                     # Colored output utilities
│   ├── repl.py                        # ReplApp main loop
│   ├── commands/                      # Command implementations
│   └── controllers/                   # Main controller
└── security/
    ├── security.py                    # Directory deletion safeguards
    └── security_constants.py          # Security constants
```
