# Application Structure Overview

**Feature:** agentx core architecture  
**Date:** 2026-06-27  
**Phase:** Design  
**Status:** Current

---

## 1. Overview

This document describes the overall architecture of the agentx application, following the MVC++ (Model-View-Controller) pattern with dependency inversion through Abstract Partners.

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      ENTRY POINT                                 │
│  main.py — Bootstrap, provider selection, lifecycle              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CONTROLLER LAYER                              │
│  (ui/screens/*/ — Command handling, state management)           │
│                                                                  │
│  MainController ────┬──── RagController ────┬──── ChatController│
│                     │                       │                   │
│  Implements:        │                       │                   │
│  - IMainViewPartner │                       │                   │
│  - IRagViewPartner  │                       │                   │
│  - IChatViewPartner │                       │                   │
└─────────────────────┼───────────────────────┼───────────────────┘
                      │                       │
                      │ Uses                  │ Uses
                      ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                     INTERFACE LAYER                              │
│  (ui/interfaces.py — Abstract Base Classes)                     │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ IMainView    │  │ IRagView     │  │ IChatView    │          │
│  │ (ABC)        │  │ (ABC)        │  │ (ABC)        │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  ┌──────────────────────────────────────────────────┐           │
│  │ IUIProvider (ABC) — Abstract Factory             │           │
│  │  - create_main_view(), create_rag_view(), ...    │           │
│  └──────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ Implemented By
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      VIEW LAYER                                  │
│  (ui/screens/*/, ui/tui/adapters/ — UI rendering)              │
│                                                                  │
│  Console Views:                    TUI Views (Textual):         │
│  - MainView                        - TUIAdapter                 │
│  - RagView                         - TUIRagAdapter              │
│  - ChatView                        - TUIChatAdapter             │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ Depends On
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     MODEL LAYER                                  │
│  (model/ — Business logic, data, external services)            │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ AI Module   │  │ RAG Module  │  │ Session     │             │
│  │ (LLM prov.) │  │ (Vector DB) │  │ (History)   │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Directory Structure (Simplified)

```
agentx/
├── src/agentx/
│   ├── main.py                 # Entry point
│   ├── model/                  # Model layer (business logic)
│   │   ├── ai/                 # LLM providers (OpenAI, Ollama, etc.)
│   │   ├── rag/                # RAG orchestration, vector stores
│   │   └── session/            # Session management, history
│   └── ui/                     # View + Controller layers
│       ├── interfaces.py       # Abstract Base Classes
│       ├── providers.py        # Provider registry
│       ├── common/             # Shared UI components
│       ├── screens/            # Screen MVC triads (main, chat, rag)
│       └── tui/                # Textual TUI implementation
├── tests/                      # Unit tests + automated TUI tests
├── local_sessions/             # Runtime data (gitignored)
├── .meta/                      # OMT++ documentation artifacts
├── scripts/omt/                # OMT++ tooling (linter, scaffolder)
└── .opencode/                  # opencode plugin enforcement
```

---

## 4. Layer Responsibilities

### 4.1 Model Layer (`model/`)

**Responsibility:** Business logic, data persistence, external service integration.

**Key Principles:**
- NO imports from `ui` module (strict layer isolation)
- SQL operations confined to `*_db.py` (Data Provider pattern)
- Entities implement CRUD lifecycle (`create`/`load`/`update`/`delete`)

**Modules:**

| Module | Responsibility |
|--------|----------------|
| `ai/` | LLM provider abstraction and factory (AIService) |
| `rag/` | RAG orchestration, vector store, web ingestion |
| `session/` | Session lifecycle, SQLite history persistence |

### 4.2 View Layer (`ui/screens/`, `ui/tui/`)

**Responsibility:** User interface rendering, input capture.

**Key Principles:**
- NO business logic (delegates to controller)
- NO direct model access
- Implements interfaces from `interfaces.py`

**Implementations:**
- **Console:** Traditional ANSI terminal (`*_view.py`)
- **TUI:** Textual framework adapters (`tui/adapters/`)

### 4.3 Controller Layer (`ui/screens/*/_controller.py`)

**Responsibility:** Command handling, state management, view-model mediation.

**Key Principles:**
- Implements Abstract Partner interfaces
- NO UI rendering code (no `print`, `console`, Textual widgets)
- Main screen uses Command pattern for dispatch

---

## 5. Dependency Injection (Provider Pattern)

UI providers enable runtime selection between Console and TUI implementations:

```
┌──────────────────┐
│  main.py         │
│  (Entry Point)   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ ProviderRegistry │
│  - get("tui")    │
│  - get("console")│
└────────┬─────────┘
         │
         ├─────────────┐
         ▼             ▼
┌────────────────┐ ┌────────────────┐
│  TUIProvider   │ │ ConsoleProvider│
│  (Textual)     │ │ (ANSI console) │
└────────────────┘ └────────────────┘
```

**Usage:**
```python
ui_provider = ProviderRegistry.get_default()
ui_provider.initialize()
main_view = ui_provider.create_main_view(main_controller)
```

---

## 6. Key Design Patterns

### 6.1 Abstract Partner Pattern

All view-controller partnerships use Abstract Base Classes:

| Interface | Implemented By | Partner |
|-----------|----------------|---------|
| `IMainView` | `MainView`, `TUIAdapter` | `MainController` |
| `IRagView` | `RagView`, `TUIRagAdapter` | `RagController` |
| `IChatView` | `ChatView`, `TUIChatAdapter` | `ChatController` |

### 6.2 Command Pattern (Main Screen Only)

Commands encapsulate user actions at the main screen:

```python
class Command(ABC):
    def __init__(self, key: str, controller): ...
    @abstractmethod
    def run(self, arguments: list[str]) -> None: ...
```

**Built-in Commands:** `help`, `quit`, `clear`, `chat`, `rag`, `new`, `history`, `sum`, `version`

### 6.3 Data Provider (DP) Pattern

All SQL operations encapsulated in `DP_*` classes:

| File | Contains |
|------|----------|
| `model/session/session_db.py` | `DP_Session` — session CRUD |
| `model/rag/rag_db.py` | `DP_Rag` — RAG CRUD |

---

## 7. Session & RAG Data Flow

### 7.1 Session Storage

```
local_sessions/
└── <timestamp>_<name>/
    ├── session.db      # SQLite: command_history
    └── rag/
        └── <repo_id>/
            ├── db/     # Chroma vector store
            └── docs/   # Ingested documents
```

### 7.2 RAG Architecture

```
┌─────────────────┐
│ RagController   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ RagRepository   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Rag             │
│  - ingest()     │
│  - query()      │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌──────────┐
│Vector │ │ Web      │
│Store  │ │ Ingestion│
└───────┘ └──────────┘
```

---

## 8. Testing Structure

```
tests/
├── unit/                 # Isolated unit tests (mocked)
│   ├── model/            # AI, RAG, session tests
│   └── ui/               # Controller/view tests
└── automated/
    └── tui/              # Textual Pilot E2E tests
```

**Characteristics:** 205+ tests, all isolated, no external dependencies.

---

## 9. Configuration & Enforcement

| File | Purpose |
|------|---------|
| `opencode.jsonc` | Permission gates (deny git commit, bare python) |
| `.opencode/plugin/omt_enforcer.ts` | OMT++ process gate |
| `AGENTS.md` | Agent instructions |
| `.env` | API keys (gitignored) |

**OMT++ Tools:**
- `omt_phase` — Declare phase before `src/` edits
- `uv run scripts/omt/mvc_check.py` — Architecture linter
- `uv run scripts/omt/new_feature.py` — Feature scaffolder

---

## 10. Related Documents

- **Behavior Overview:** `../behavior/BEHAVIOR.md`
- **OMT++ Methodology:** `../../omt_agent_guide.md`
- **Feature Designs:** `./features/feature_*/design_*.md`