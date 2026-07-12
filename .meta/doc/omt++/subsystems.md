# subsystems.md — Subsystem Internals (compressed)

**SCOPE:** How each subsystem works internally. Layering: architecture.md; Flows: data_flow.md.

---

## 1. Intelligent Agent (`src/agentx/agent/`)

Self-contained MVC++ triad: goal-driven, policy-based agent with perceive → decide → act → reflect cycle. Largest subsystem.

### 1.1 Layer Map
| Layer | Files | Responsibility |
|-------|-------|----------------|
| Model | `model/agent.py` (`Agent` facade), `model/goal/`, `model/policy/`, `model/memory/`, `model/reflection/`, `model/tools/`, `persistence/`, `types.py` | Domain logic + persistence |
| Controller | `controller/agent_controller.py`, `session_controller.py`, `tool_controller.py` | View ↔ Agent mediation |
| View | `view/agent_view.py` (console), `view/tui/{agent_screen,demo_screen,fast_agent_screen,fast_agent_modals,fast_agent_view}.py` | UI |
| Wiring | `adapter.py` (`AgentAdapter`) | Factory: builds Agent + Controller (+ screen) |
| Contracts | `interfaces.py` | 8 Abstract Partners |

### 1.2 `Agent` Facade (`model/agent.py`)
Single Model entry point. Constructor builds subsystems + registers built-in tools → `PERCEIVING`.

| API | Description |
|-----|-------------|
| `run_cycle()` | perceive → decide → act → (reflect if AI) → `CycleResult` |
| `run_cycles(n)` | Run N cycles |
| `submit_goal(goal)` | `GoalManager.add_goal` (single-active model) |
| `update_policy(rule)` | `PolicyEngine.add_rule_safely` |
| `clear_state()` | Clear goals/rules/volatile memory (feature_010) |
| `persist()` | `SessionSnapshot` → DB |
| `resume_session(id)` | Rebuild state from snapshot (N1/N7/N8/N9 fixes) |
| `load_latest_snapshot()` | Load most recent |
| `register_tool` / `unregister_tool` / `list_tools` | ToolRegistry ops |
| `execute_tool_action` / `tool_health_check` | Execute / health |
| `list_pending_proposals()` / `approve_proposal(id, idx)` | Reflection approval |
| `list_rules()` / `list_goals()` / `query_memory()` / `get_status()` | Query (N6) |

### 1.3 GoalManager (`model/goal/manager.py` → `IGoalManager`)
AND/OR goal tree, priority-based activation.
- Single-active: new goal auto-activates only if none ACTIVE
- `update_status()` completes/abandons goal → promotes next PENDING
- `apply_adjustment` / `revert_adjustment` — reflection-driven changes with rollback tokens
- `load_from_repository(root_id)` — restores tree, honours persisted root (N8: prevents root drift)
- `clear()` (feature_010) — empties tree

### 1.4 PolicyEngine (`model/policy/`)
Evaluates rules against `PolicyContext` → `PolicyDecision`.
- **Condition DSL** (`rule.py`): tokenizer + AST + visitor compiles `condition_expr` strings. Supports identifiers (`goal.active`, `agent.state`, `environment.confidence`, `memory`, …), functions (`has_observation(tag)`, `goal_is_blocked()`, `memory_contains(query)`), operators (`AND OR NOT == != < <= > >= + -`), `true`/`false` literals.
- `evaluate(context)` → `PolicyDecision(action, confidence, reasoning, alternatives)`
- `add_rule_safely(rule)` — compiles, checks conflicts (reject if overlap score > 0.8), checks complexity (≤10 params), persists
- `ConflictResolver` (`conflict_resolver.py`) — priority-based resolution, detects overlap by `tool_id` + action
- Rules persist via `PolicyRepository` (N3: repo = source of truth)

### 1.5 MemoryManager (`model/memory/manager.py`)
Volatile (OrderedDict, capacity-bounded LRU) + persistent (repo-backed) tiers.
- `store(entry, tier)`, `retrieve(query)`, `consolidate()`, `evict(criteria)`
- `export_volatile()` / `import_volatile(entries)` — snapshot serialisation
- `apply_update` / `revert_update` — reflection-driven memory changes
- `clear_volatile()` (feature_010)
- `context_memory_limit` config bounds memory fed to policy context (m2)

### 1.6 Reflection (`model/reflection/`)
`ReflectionEngine` → `ReflectionEntry` (critique + proposals) from `DecisionTrace`.
- `critique_parser.py` — parses AI critique into strengths/weaknesses
- `safety_evaluator.py` (`DefaultSafetyEvaluator`) — deny-list gate (expanded, M7)
- `proposal_router.py` — routes proposals (GOAL_ADJUSTMENT, MEMORY_UPDATE, TOOL_CONFIGURATION, POLICY_UPDATE) with rollback tokens
- **Approval flow (N4):** proposals PENDING until `approve_proposal(entry_id, idx)` applies; `pending_proposals()` lists them; TUI `proposals` / `approve <n>` commands close loop
- **AI-optional (N11):** `reflect()` skipped entirely when no AI service wired

### 1.7 Tools (`model/tools/`)
`ToolRegistry` registers sensors (`ISensor`), actuators (`IActuator`), or hybrid (both).

| Tool | id | Kind | Notes |
|------|----|------|-------|
| `FileSystemTool` | `filesystem` | hybrid | sandboxed CRUD + listing; `MAX_FILES=2000` (m10); path-escape guard |
| `RagSensorTool` | `rag_query` | hybrid | senses RAG availability; `act(query)` queries KB (N12); RAG injected via `set_rag` |
| `SessionTool` | `session` | hybrid | `persist` / `restore` snapshots (M8: calls `resume_session`) |

- `discovery.py` — optional entry-point-based tool discovery
- **Action dispatch:** `_decision_to_command` extracts `tool_id` + `action` from `PolicyAction.parameters` into `ActuatorCommand(actuator_id, action, parameters)`. Tools read canonical `command.action` (feature_010 bug fix — was reading `command.parameters`, breaking non-read actions at runtime)
- Tool enable/disable enforced in perceive + execute (N5); `set_tool_enabled` / `is_enabled` public (M6)

### 1.8 Persistence (`persistence/`)
`SessionDatabase` (stdlib sqlite3) + 4 repositories (Goal/Memory/Policy/Reflection). Schema in `schema_db.py` (idempotent DDL). Snapshot-based: `SessionSnapshot` captures config, volatile memory, policy store, goal-tree root, reflection-log position. See persistence.md §3.

### 1.9 Controllers & Views
- `AgentController` (`controller/agent_controller.py`) — small (<200 loc), mediates View ↔ Agent: submit_goal, run_cycle, update_policy, save_snapshot, list_*, approve_proposal, reset_state, load_demo_scenario_by_name, get_demo_scenario_info, **get_cycle_summary**
- `SessionController`, `ToolController` — thin specialists
- `AgentView` (console) — `IAgentViewPartner`
- `AgentTUIScreen` (Textual) — own command dispatch (`goal`, `rule`, `run`, `status`, `goals`, `rules`, `memory`, `save`, `demo`, `proposals`, `approve`); bindings `q`/`r`/`s`/`d`/`escape`
- `AgentDemoScreen` (feature_010) — demo with Run/Reset/Back buttons
- `FastAgentTUIScreen` (feature_011) — modal stack (Goal → Running → Reflection → Result); pushes `ModalScreen` dialogs; `escape` pops host
- `FastAgentTUIView` (feature_011) — no-op `IAgentViewPartner` virtual subclass (swallows controller UI callbacks during `run_cycle()`)
- `AgentAdapter` (`adapter.py`) — factory owning AI-service wiring (I4) + snapshot resume (C5/I1); **create_fast()** builds Fast Agent triad with `FastAgentTUIView`

### 1.10 Types (`types.py`)
38 enums + dataclasses: `AgentState`, `AutonomyLevel`, `GoalType`, `GoalStatus`, `ActionType`, `RuleSource`, `MemoryTier/Source`, `AgentConfig`, `MemoryConfig`, `Goal`, `GoalTree`, `PolicyRule`, `PolicyAction`, `PolicyDecision`, `SuccessCriteria`, `ActuatorCommand/Result`, `SensorReading`, `ReflectionEntry`, `Proposal`, `SessionSnapshot`, etc. Plain dataclasses (no Pydantic) — agent stays dependency-free.

---

## 2. RAG Subsystem (`src/agentx/model/rag/`)

Retrieval-augmented generation: ingest docs into vector store, answer questions with retrieval-augmented LLM responses.

| File | Role |
|------|------|
| `rag.py` | `Rag` orchestrator — `query()`, `web_ingestion()`, `is_data()`, `get_ingested_url()` |
| `rag_db.py` | `RagDatabase` (DP_Rag) — `ingestion` table; `insert/select_ingestion_entry` |
| `rag_provider.py` | `RagProvider` — lists `rag_*` dirs containing `rag.db` |
| `rag_repository.py` | `RagRepository` dataclass |
| `query/rag_query.py` | `RagQuery` + `RagChatHistory` — LangChain retrieval chain (history-aware retriever + stuff-documents + retrieval chain) |
| `query/rag_prompts.py` | `ChatPromptTemplate`s (system + `MessagesPlaceholder("chat_history")`) |
| `web_ingestion/` | `WebIngestionApp`, `WebExtract` (Tavily Map+Extract), chunking/indexing |

**Ingestion:** `Rag.web_ingestion(extract_level)` → TavilyMap crawls site → `RecursiveCharacterTextSplitter(4000, 200)` → concurrent `aadd_documents` into Chroma. Extract levels (Low/Mid/High) control `max_depth`/`max_breadth`/`max_pages` (`ui/screens/rag/constants.py`).

**Query:** `RagQuery.ask(prompt, history)` builds LangChain `create_retrieval_chain` over `create_history_aware_retriever` + `create_stuff_documents_chain`; appends sources string.

**Vectorstores:** Chroma (OpenAI/Ollama embeddings) or Pinecone (`model/ai/vectorstores/`).

---

## 3. Session Subsystem (`src/agentx/model/session/`)

Manages per-session working dirs + command history.

| File | Role |
|------|------|
| `session.py` | `Session` entity — `create()` builds dir under `local_sessions/`, owns `SessionDatabase`; `create_new_session()`, `backup_current_session()`, history insert/select |
| `session_manager.py` | `SessionManager` facade — `get_current_session()`, `get_directory_rag()`, history, session name |
| `session_db.py` | `SessionDatabase` (DP_Session) — `history` + `users` tables; `insert/select_history_entry`; allowlist-guarded `_select_all` |

- "Current" session (`SESSION_CURRENT_NAME = "current"`) = active working dir; `new [name]` backs it up and creates timestamped one.
- Command history recorded by `MainController.run_command()` → stored in `session.db`.

---

## 4. AI Subsystem (`src/agentx/model/ai/`)

LLM provider abstraction + vectorstores.

| File | Role |
|------|------|
| `service.py` | `AIService` factory facade — `openrouter_llm_provider()`, `local_llm_provider(...)`, `cloud_llm_provider()`, `rag_chromadb(...)` |
| `providers.py` | `LLMProvider(ABC)` + `LlamaCppProvider`, `OpenAIProvider`, `OpenRouterProvider` |
| `cloud/google/`, `cloud/open_ai/` | Google Gemini, OpenAI GPT helpers |
| `local/llama_cpp/` | `LlamaCpp` + `LlamaCppConfig` (Pydantic) + factory singleton |
| `local/ollama/` | `Ollama` + `LocalOllamaModelManager` |
| `vectorstores/` | Chroma (OpenAI/Ollama embeddings) + Pinecone factories |

- **Default:** OpenRouter (`openrouter/auto`), key via `OPENROUTER_API_KEY` (prompted at boot)
- **Agent integration:** `agent/model/ai_adapter.py` (`AIServiceAdapter`) implements `IAIServicePartner` so agent's `ReflectionEngine` calls LLM without importing LangChain directly

---

## 5. UI / Command Subsystem (`src/agentx/ui/`)

### 5.1 Screens (MVC Triads)
| Screen | Controller | View (console) | View (TUI) | Partner |
|--------|-----------|----------------|------------|---------|
| Main | `MainController` | `MainView` | `TUIAdapter`→`MainTUIScreen` | `IMainViewPartner` / `IMainView` |
| Chat | `ChatController` | `ChatView` | `TUIChatAdapter`→`ChatTUIScreen` | `IChatViewPartner` / `IChatView` |
| RAG | `RagController` (+4 sub) | `RagView` | `TUIRagAdapter`→`RagTUIScreen` | `IRagViewPartner` / `IRagView` |

RAG sub-triads (`ui/screens/rag/`): repository selection, create repository, RAG chat, web ingestion — each own controller+view.

### 5.2 Main Screen (Textual)
`MainTUIScreen` (`ui/tui/screens/main_screen.py`) — real main screen.
Widgets: `SessionStatusBar`, `WelcomePanel`, `MenuGrid` (Chat/RAG/Agent/Help buttons), `CommandInput`.
Bindings: `q`/`c`/`r`/`a`/`h`/`ctrl+l`.
`action_open_*()` calls `controller.show_*()` (wiring) then `app.push_screen()` (navigation) and connects adapter via `set_screen()`.

### 5.3 Commands (`ui/screens/main/commands/`)
10 built-in commands in `MainController.load_commands()`: `sum`, `quit`, `clear`, `help`, `history`, `chat`, `new`, `ls`, `rag`, `version`. See architecture.md §4 for dispatch flow.

### 5.4 Common Components (`ui/common/`)
- `ui_console.py` — `UIConsole` (ANSI helper), `UIMessage`/`UIMessageType`, `UIPrompt`, `UIConsoleColors`
- `input/` — 4 reusable input mini-triads: `options` (numbered menu), `text_list`, `create_folder`, `url_entry` (pre-date interface layer; wire controller↔view directly)

### 5.5 Known Inconsistencies
- `ChatView` defines local `ChatViewPartner` ABC instead of importing `IChatViewPartner` from `interfaces.py`
- `UIConsole.waning` typo (missing "r") propagated across views
- `MainController.show_react()` references non-existent `react/` screen (dangling import)
- `app.py` contains stub `MainTUIScreen` (dead code; real one imported from `screens/main_screen.py`)

---

## 6. Agent Demo (`src/agentx/agent/demo/`)
Feature_010's seeded scenarios, launched from `AgentTUIScreen` via `d` / `demo [a|b]`.
- `scenarios.py` — `DemoScenario` dataclass + `SCENARIO_A` (File Reader) + `SCENARIO_B` (Knowledge Assistant) + `get_scenario(name)` + `seed_sandbox_files(scenario, root)`. Pure data; controller translates specs into real `Goal`/`PolicyRule`.
- See data_flow.md §"Demo flow" for runtime sequence.

---

## 7. Utils (`src/agentx/utils/`)
| File | Role |
|------|------|
| `constants.py` | `SESSION_DEFAULT_BASE_DIRECTORY`, `APP_VERSION`, deletion allowlist |
| `utils.py` | `safe_int`, `clear_console`, directory creation (with/without timestamp), `get_directories_start_with`, safe deletion |
| `utils_directories.py` | pathlib toolkit: checks, creation, text/binary/JSON I/O, copy/move/delete, listing, sizing |
| `utils_input.py` | `is_valid_url` |