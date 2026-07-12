# architecture.md — MVC++ Architecture (compressed)

**SCOPE:** Layering, dependency rules, patterns, stack, enforcement.

---

## 1. MVC++ — Layer Rules (Hard)

```
CONTROLLER: App logic, orchestration, dispatch | knows: View+Model | seen by: View(Partner)
VIEW:       UI render, input capture           | knows: Controller(Partner only)
MODEL:      Domain logic, biz rules, data      | knows: nothing about UI
```

| What | Controller | View | Model |
|------|-----------|------|-------|
| Imports Model | ✅ | ❌ | N/A |
| Imports View | ✅ | N/A | ❌ |
| Imports Controller | N/A | ❌ (Partner only) | ❌ |
| Contains UI code | ❌ | ✅ | ❌ |
| Contains biz logic | Orchestration | ❌ | ✅ Core |
| Contains SQL | ❌ | ❌ | ✅ DP only |

> Enforced: `uv run scripts/omt/mvc_check.py` (0 errors baseline)

---

## 2. Abstract Partner Pattern

```
View ──calls──▶ I*ViewPartner(ABC) ◀──implements── Controller
Controller ──calls──▶ I*View(ABC) ◀──implements── View
```

**Rules:** ABC + @abstractmethod only | Name: `I*ViewPartner` | Defined in `ui/interfaces.py` / `agent/interfaces.py`

| Interface | Controller | View |
|-----------|------------|------|
| `IMainViewPartner` | `MainController` | `IMainView` |
| `IChatViewPartner` | `ChatController` | `IChatView` |
| `IRagViewPartner` | `RagController` | `IRagView` |
| `IAgentViewPartner` | `AgentController` | `IAgentView` |
| ... | 7 more in `agent/interfaces.py` |

> Textual screens: register as virtual subclass: `IAgentViewPartner.register(MyScreen)`

---

## 2.5. Fast Agent (feature_011) — Modal UX

| Aspect | Detail |
|--------|--------|
| Entry | `f` key / `⚡ Fast Agent` button |
| Flow | GoalModal → RunningModal → ReflectionModal → ResultModal (ModalScreen stack) |
| Engine | Reuses feature_007 `Agent` + `AgentController` |
| Auto-run | `call_after_refresh` chain; pauses only on reflection proposals |
| Goal completion | Manual (`SuccessCriteria(kind="manual")`) |
| No-op partner | `FastAgentTUIView` swallows UI callbacks during `run_cycle()` |
| Existing Agent | Relabeled `⚙️ Advanced Agent` |

---

## 3. Provider / Adapter Pattern (Console ⇄ TUI)

```
main.py → ProviderRegistry.get_default()
  ├─ TUIProvider → TUIAdapter → MainTUIScreen (IMainView)
  └─ ConsoleProvider → MainView (IMainView)
```
- `ProviderRegistry` (`ui/providers.py`) holds providers; `tui` auto-registers default
- Adapters: thin delegates; `TUIChatAdapter`/`TUIRagAdapter` wired via `set_screen()`
- Fallback: TUI exception → ConsoleProvider

---

## 4. Command Pattern (Main Screen Only)

```
ui/screens/main/commands/
  commands_base.py   # Command(ABC): __init__(key, controller); run(args)
  commands_parser.py # CommandParser → CommandData(key, args)
  commands.py        # 10 concrete commands
```
Flow: `Input → Parser → MainController.run_command() → commands[key].run(args)`

---

## 5. Database Partner (DP) Pattern

**All SQL in `DP_*` classes only** (enforced by `mvc_check.py:SQL_OUTSIDE_DP`)

| DP Class | File | DB |
|----------|------|-----|
| `SessionDatabase` (`DP_Session`) | `model/session/session_db.py` | `session.db` |
| `RagDatabase` (`DP_Rag`) | `model/rag/rag_db.py` | `rag.db` |
| `SessionDatabase` (agent) | `agent/persistence/agent_db.py` | `agent_session.db` |

All: stdlib `sqlite3`, idempotent `CREATE TABLE IF NOT EXISTS`, no ORM/Alembic.

---

## 6. Tech Stack

| Concern | Tech |
|---------|------|
| Language | Python via `uv` (bare python/pip/pytest denied) |
| TUI | Textual (Screen, widgets, pilot tests) |
| LLM | LangChain (BaseChatModel, retrieval chains) |
| Providers | OpenRouter (default), OpenAI, Gemini, Ollama, llama.cpp |
| Vector | Chroma (local), Pinecone (cloud) |
| Web | Tavily (Map + Extract) |
| Persistence | stdlib sqlite3 |
| Enforcement | opencode + `.opencode/plugin/omt_enforcer.ts` |

**Env:** `.env` (gitignored) — `OPENROUTER_API_KEY` prompted at boot | `--no-tui` or no TTY → console

---

## 7. Config & Enforcement

| File | Purpose |
|------|---------|
| `opencode.jsonc` | Deny: git commit/push, bare python/pip/pytest, .env; bash default ask |
| `.opencode/plugin/omt_enforcer.ts` | OMT++ gate: blocks src/ w/o `omt_phase`; blocks tests/ w/o approval; runs mvc_check |
| `AGENTS.md` | Agent rules |
| `scripts/omt/mvc_check.py` | MVC++ linter (View↔Model leaks, non-ABC partners, SQL outside DP, god controllers) |
| `scripts/omt/new_feature.py` | Feature scaffolder |

**Process:** `omt_phase` before `src/` edits → design doc for new_screen/major_feature → artifacts per phase → `omt_complete` to advance.

---

## 8. Key Design Decisions

- **No ORM/Alembic** — stdlib sqlite3 + explicit DDL
- **Agent persistence = snapshot** — `SessionSnapshot` captures config, volatile memory, policy, goal tree root, reflection log position
- **Single-active goal** — `GoalManager` activates one goal; completion promotes next
- **Reflection AI-optional** — skipped when no AI service wired (N11)