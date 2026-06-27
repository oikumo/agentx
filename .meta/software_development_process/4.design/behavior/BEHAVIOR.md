# Application Behavior Overview

**Feature:** agentx core behavior  
**Date:** 2026-06-27  
**Phase:** Design  
**Status:** Current

---

## 1. Overview

This document describes the runtime behavior of the agentx application, organized by user-facing features and component interactions following OMT++ behavioral modeling principles.

---

## 2. Application Lifecycle

### 2.1 Startup Sequence

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Initialize                                               │
│    - Load .env configuration                                │
│    - Prompt for OPENROUTER_API_KEY if missing               │
│    - Detect TTY capability                                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Select UI Provider                                       │
│    - TUI if TTY detected and --no-tui not passed            │
│    - Console otherwise (fallback)                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Create Controller + View                                 │
│    - MainController instantiated                            │
│    - View created via Provider (dependency injection)       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Start Main Loop                                          │
│    - TUI: Textual event-driven loop                         │
│    - Console: Blocking input loop                           │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Shutdown

- **Normal:** User types `quit` or presses `q` (TUI)
- **Interrupt:** Ctrl+C → graceful cleanup, provider shutdown
- **Error:** TUI exception → fallback to console mode

---

## 3. Main Screen Behavior

### 3.1 State Machine

```
┌──────────────┐
│   STARTED    │
│ (show banner)│
└──────┬───────┘
       │
       ▼
┌──────────────┐     ┌──────────────┐
│  WAITING     │────▶│  PARSING     │
│ (prompt)     │     │ (command)    │
└──────┬───────┘     └──────┬───────┘
       │                    │
       │                    ▼
       │             ┌──────────────┐
       │             │  EXECUTING   │
       │             │ (command.run)│
       │             └──────┬───────┘
       │                    │
       ▼                    ▼
┌──────────────┐     ┌──────────────┐
│   QUIT       │◀────│  COMPLETED   │
│ (exit loop)  │     │ (show result)│
└──────────────┘     └──────────────┘
```

### 3.2 Command Processing Flow

```
User Input → CommandParser.parse() → CommandData(key, args)
    │
    ▼
MainController.run_command()
    │
    ├─ Lookup: commands[key]
    │   ├─ Found → command.run(arguments)
    │   └─ Not Found → "Unknown command: {key}"
    │
    ▼
Record in session history (SQLite)
```

### 3.3 Command Behaviors

| Command | Behavior |
|---------|----------|
| `help` | List all commands with descriptions |
| `quit` | Exit application |
| `clear` | Clear terminal screen |
| `history` | Show command history from session |
| `sum <a> <b>` | Add two integers |
| `chat` | Launch chat screen |
| `rag` | Launch RAG screen |
| `new [name]` | Create new session |
| `ls` | List RAG repositories |
| `version` | Show application version |

---

## 4. Chat Screen Behavior

### 4.1 State Machine

```
┌──────────────┐
│   STARTED    │
│ (welcome msg)│
└──────┬───────┘
       │
       ▼
┌──────────────┐     ┌──────────────┐
│  WAITING     │────▶│  PROCESSING  │
│ (user input) │     │ (LLM call)   │
└──────┬───────┘     └──────┬───────┘
       │                    │
       │                    ▼
       │             ┌──────────────┐
       │             │  STREAMING   │
       │             │ (chunks)     │
       │             └──────┬───────┘
       │                    │
       ▼                    ▼
┌──────────────┐     ┌──────────────┐
│   QUIT       │◀────│  COMPLETED   │
│ (exit/quit)  │     │ (append to   │
└──────────────┘     │  history)    │
                     └──────────────┘
```

### 4.2 Message Processing

1. User types message
2. Append `HumanMessage` to history
3. Call LLM with full history (streaming)
4. Display chunks as they arrive
5. Append `AIMessage` to history
6. Repeat until user types `quit` or `exit`

---

## 5. RAG Screen Behavior

### 5.1 State Machine

```
┌──────────────┐
│   STARTED    │
│ (show menu)  │
└──────┬───────┘
       │
       ├─────────────────┬─────────────────┐
       ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  SELECT_REPO │  │ CREATE_REPO  │  │   QUIT       │
│ (browse)     │  │ (new repo)   │  │ (back)       │
└──────┬───────┘  └──────┬───────┘  └──────────────┘
       │                 │
       ▼                 ▼
┌──────────────┐  ┌──────────────┐
│  REPO_READY  │  │  REPO_CREATED│
└──────┬───────┘  └──────┬───────┘
       │                 │
       └────────┬────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│           SUB-MENU (repo selected)       │
│  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │ CHAT     │  │ INGEST   │  │ BACK   │ │
│  └──────────┘  └──────────┘  └────────┘ │
└─────────────────────────────────────────┘
```

### 5.2 Repository Operations

| Operation | Behavior |
|-----------|----------|
| **Select** | Browse existing repositories, load selected |
| **Create** | Wizard: name → location → initialize |
| **Chat** | RAG-enabled chat with selected repository |
| **Ingest** | Fetch URL → parse → chunk → store in vector DB |

---

## 6. Session Management

### 6.1 Session Lifecycle

```
┌──────────────┐
│  NO SESSION  │
│ (default)    │
└──────┬───────┘
       │ new [name]
       ▼
┌──────────────┐
│  CREATING    │
│ (mkdir, init)│
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   ACTIVE     │◀──────┐
│ (run cmds)   │       │
└──────┬───────┘       │
       │               │
       │ new [name]    │
       └───────────────┘
```

### 6.2 Persistence

| Data | Storage | Lifetime |
|------|---------|----------|
| Command history | SQLite (session.db) | Per session |
| RAG repositories | File system (rag/) | Permanent |
| Vector embeddings | Chroma DB | Permanent |
| Ingested documents | File system | Permanent |

---

## 7. Provider Selection

### 7.1 Runtime Decision

```
if --no-tui not passed AND TTY detected:
    → TUIProvider (Textual)
else:
    → ConsoleProvider (fallback)
```

### 7.2 Error Fallback

```
try:
    main_view.show()  # TUI
except Exception:
    print("Falling back to console mode...")
    console_view = ConsoleProvider.create_main_view()
    console_view.show()
```

---

## 8. Component Collaborations

### 8.1 Chat Sequence

```
User → ChatView → ChatController → AIService → LLM API
  │                                        │
  │                                        ▼
  │                                   (stream chunks)
  │                                        │
  ▼                                        ▼
ChatView ← ChatController ← AIService ← Response
(display)
```

### 8.2 RAG Repository Selection

```
User → RagView → RagController → RepositorySelection
                                         │
                                         ▼
                                   List repositories
                                         │
                                         ▼
                                   User selects
                                         │
                                         ▼
RagView ← RagController ← Repository set
(display confirmation)
```

---

## 9. Error Handling

| Error Type | Handling |
|------------|----------|
| `KeyboardInterrupt` | Graceful shutdown |
| `ValueError` (invalid input) | Error message, retry |
| `ConnectionError` (LLM API) | Error message, retry option |
| `FileNotFoundError` | Error message |
| TUI exception | Fallback to console mode |

---

## 10. User Interaction Patterns

### 10.1 Console Mode

```
(agentx) Agent-X
         Type 'help' for commands, Ctrl+C to exit

(agentx) > chat
Welcome to Chat! Type your message or 'quit' to exit.

You: Hello!
Assistant: Hello! How can I help you today?

You: quit
(agentx) > 
```

### 10.2 TUI Mode

```
┌─ AgentX TUI ──────────────────────────────────┐
│  Welcome to AgentX TUI                         │
│  Press 'c' for Chat, 'r' for RAG, 'q' to quit  │
│                                                │
│  [c] Chat  [r] RAG  [h] Help  [q] Quit        │
└────────────────────────────────────────────────┘
```

**Key Bindings:** `q` (Quit), `c` (Chat), `r` (RAG), `h` (Help)

---

## 11. Related Documents

- **Structure Overview:** `../structure/STRUCTURE.md`
- **Feature Designs:** `./features/feature_*/design_*.md`
- **OMT++ Behavioral Modeling:** `../../omt_agent_guide.md §3, §7-9`