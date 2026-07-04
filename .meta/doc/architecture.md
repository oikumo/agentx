# Architecture

> **Scope:** MVC++ layering, dependency rules, the provider/adapter pattern,
> core design patterns, tech stack, and configuration/enforcement.
> **See also:** [subsystems.md](subsystems.md) for per-subsystem internals.

---

## 1. MVC++ — the core architecture

Every feature is split into exactly three layers. No mixing.

```
┌──────────────────────────────────────────────────────┐
│                    CONTROLLER                         │
│  Application logic, orchestration, command dispatch   │
│  Knows: View + Model        Seen by: View (Partner)   │
├──────────────────────────────────────────────────────┤
│                       VIEW                            │
│  UI rendering, input capture                          │
│  Knows: Controller (via Abstract Partner only)        │
├──────────────────────────────────────────────────────┤
│                      MODEL                            │
│  Domain logic, business rules, data persistence       │
│  Knows: nothing about UI layers                       │
└──────────────────────────────────────────────────────┘
```

### Layer dependency rules (absolute)

| What | Controller | View | Model |
|------|-----------|------|-------|
| Imports Model? | ✅ Yes | ❌ Never | N/A |
| Imports View? | ✅ Yes | N/A | ❌ Never |
| Imports Controller? | N/A | ❌ Only via Abstract Partner | ❌ Never |
| Contains UI code? | ❌ Never | ✅ Yes | ❌ Never |
| Contains business logic? | ✅ Orchestration only | ❌ Never | ✅ Core logic |
| Contains SQL? | ❌ Never | ❌ Never | ✅ In `DP_*` classes only |

> Enforced by `uv run scripts/omt/mvc_check.py` (0 errors is the baseline).

### File naming

```
<layer>/<screen>/<screen>_<layer>.py
ui/screens/main/main_controller.py
ui/screens/main/main_view.py
model/session/session.py            # model files omit the suffix
```

---

## 2. Abstract Partner pattern

The **only** way a View talks to its Controller. A View never constructs or
imports a concrete controller — it receives an `ABC` partner in its constructor.

```
View ──calls──▶ I*ViewPartner (ABC) ◀──implements── Controller
Controller ──calls──▶ I*View (ABC) ◀──implements── View
```

**Rules:**
1. Always `ABC` with `@abstractmethod` (never a plain class).
2. Name starts with `I`: `IMainViewPartner`, `IChatViewPartner`, `IRagViewPartner`.
3. The View interface (`I*View`) and the partner interface (`I*ViewPartner`)
   are both defined in `src/agentx/ui/interfaces.py`.
4. Controller implements `I*ViewPartner`; View implements `I*View`.

**Screen partner interfaces** (`src/agentx/ui/interfaces.py`):

| Interface | Implemented by (Controller) | View interface |
|-----------|------------------------------|----------------|
| `IMainViewPartner` | `MainController` | `IMainView` |
| `IChatViewPartner` | `ChatController` | `IChatView` |
| `IRagViewPartner` | `RagController` | `IRagView` |

**Agent subsystem partners** (`src/agentx/agent/interfaces.py`):
`IAgentViewPartner`, `IAgentModelPartner`, `IAIServicePartner`,
`IMemoryStorePartner`, `IPolicyStorePartner`, `IToolRegistryPartner`,
`IGoalManager`, `IPersistencePartner`, `ISafetyEvaluator`.

> The agent's Textual screens (`AgentTUIScreen`, `AgentDemoScreen`) are
> registered as **virtual subclasses** of `IAgentViewPartner` (avoids the
> Textual/abc metaclass conflict) — see `agent_screen.py` / `demo_screen.py`
> footers.

---

## 3. Provider / Adapter pattern (Console ⇄ TUI)

A **Strategy + Abstract Factory** lets the app switch between a Console UI and a
rich Textual TUI at boot. Controllers depend only on `IUIProvider` / `I*View`;
the concrete backend is chosen at startup.

```
main.py → ProviderRegistry.get_default()
              │
      ┌───────┴───────┐
      ▼               ▼
 TUIProvider     ConsoleProvider      (both implement IUIProvider)
      │               │
      ▼               ▼
 TUIAdapter      MainView             (both implement IMainView)
 TUIChatAdapter  ChatView             (both implement IChatView)
 TUIRagAdapter   RagView              (both implement IRagView)
```

- `ProviderRegistry` (`src/agentx/ui/providers.py`) holds named providers; the
  `tui` provider self-registers as default on import (if Textual is available).
- `TUIProvider` (`src/agentx/ui/tui/provider.py`) creates adapters that wrap
  Textual screens.
- Adapters are thin delegates: `TUIChatAdapter` / `TUIRagAdapter` hold a
  `_screen` connected later via `set_screen()` (the Textual screen is pushed by
  `MainTUIScreen.action_open_*()` and the adapter is wired afterwards).
- **Fallback:** if the TUI raises at runtime, `main.py` falls back to the
  console provider.

---

## 4. Command pattern (main screen dispatch)

Used **only** at the main screen to route typed input.

```
ui/screens/main/commands/
├── commands_base.py     # Command(ABC): __init__(key, controller); run(args)
├── commands_parser.py   # CommandParser → CommandData(key, arguments)
└── commands.py          # concrete commands
```

Flow: `User input → CommandParser.parse() → MainController.run_command() →
commands[key].run(args)`. Commands are registered in
`MainController.load_commands()`. See [extending.md](extending.md) §"Add a
command".

> The agent screens have their **own** internal command dispatch (in
> `AgentTUIScreen._dispatch_command`), separate from this main-screen system.

---

## 5. Database Partner (DP) pattern

**All** SQL lives in `DP_*` / `*Database` classes. No SQL in controllers or
views.

| DP class | File | DB |
|----------|------|----|
| `SessionDatabase` (`DP_Session`) | `model/session/session_db.py` | `session.db` |
| `RagDatabase` (`DP_Rag`) | `model/rag/rag_db.py` | `rag.db` |
| `SessionDatabase` + repositories | `agent/persistence/` | `agent_session.db` |

All use **stdlib `sqlite3`** with idempotent `CREATE TABLE IF NOT EXISTS` DDL —
**no ORM, no Alembic**. See [persistence.md](persistence.md).

---

## 6. Tech stack

| Concern | Technology |
|---------|-----------|
| Language | Python (run via `uv` — bare `python`/`pytest` are denied) |
| TUI framework | [Textual](https://textual.textualize.io/) (`Screen`, widgets, pilot tests) |
| LLM orchestration | LangChain (`BaseChatModel`, retrieval chains, stuff-documents) |
| LLM providers | OpenRouter (default), OpenAI, Google Gemini, Ollama, llama.cpp |
| Vector store | Chroma (local), Pinecone (cloud) |
| Web ingestion | Tavily (`TavilyMap`, `TavilyExtract`) |
| Persistence | stdlib `sqlite3` (no ORM) |
| Process enforcement | opencode + `.opencode/plugin/omt_enforcer.ts` |

### Environment configuration

- `.env` (gitignored) — API keys. `OPENROUTER_API_KEY` is prompted at boot if
  unset (see `main.py`).
- `LLAMA_CPP_MODELS_CACHE_PATH` — for local llama.cpp models.
- `--no-tui` flag or no TTY → console mode.

---

## 7. Configuration & enforcement

| File | Purpose |
|------|---------|
| `opencode.jsonc` | Permission gates: deny `git commit`/`git push`, bare `python`/`pip`/`pytest`; `.env` deny; `bash` default `ask` |
| `.opencode/plugin/omt_enforcer.ts` | OMT++ process gate — blocks `src/` edits without `omt_phase`; blocks `tests/` without approval; runs `mvc_check.py` on edits |
| `AGENTS.md` | Agent behaviour rules (mandatory read) |
| `scripts/omt/mvc_check.py` | MVC++ architecture linter (View↔Model leaks, non-ABC partners, SQL outside DP, god controllers) |
| `scripts/omt/new_feature.py` | Feature scaffolder (creates `requirements/features/feature_NNN.<slug>/`) |

**OMT++ process in one line:** declare `omt_phase` before editing `src/`;
`new_screen`/`major_feature` require a design doc; produce phase artifacts;
advance phases with `omt_complete`. See `omt_agent_guide.md`.

---

## 8. Key design decisions (recorded)

- **No ORM, no Alembic** — stdlib `sqlite3` with explicit DDL, matching the
  existing `SessionDatabase`/`RagDatabase` convention (decided during
  feature_007 design; recorded in `WORK.md`).
- **Agent persistence is snapshot-based** — a `SessionSnapshot` captures
  config, volatile memory, policy store, goal tree root, and reflection log
  position; `resume_session()` rebuilds in-memory state from it.
- **Single-active goal model** — `GoalManager` activates one goal at a time;
  completing a goal promotes the next pending one.
- **Reflection is AI-optional** — skipped entirely when no AI service is wired
  (N11), so cycles run cleanly offline.
