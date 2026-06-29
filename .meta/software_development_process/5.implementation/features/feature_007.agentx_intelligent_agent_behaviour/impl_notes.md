# Implementation Notes — feature_007.agentx_intelligent_agent_behaviour

**Phase:** Programming (I1–I13)  
**Date:** 2026-06-29  
**Design ref:** `4.design/features/feature_007.../design_001_agent_framework.md`

---

## 1. Module Structure (realised)

```
src/agentx/agent/
├── __init__.py
├── types.py                          # All enums + dataclasses (data dictionary A6)
├── interfaces.py                     # Abstract Partners (ABCs)
├── model/
│   ├── agent.py                      # Agent facade (perceive/decide/act/reflect/persist)
│   ├── memory/manager.py             # MemoryManager (IMemoryStorePartner)
│   ├── policy/
│   │   ├── rule.py                   # Condition DSL: tokenizer, parser, AST, evaluator
│   │   ├── evaluator.py              # PolicyEngine (IPolicyStorePartner)
│   │   └── conflict_resolver.py      # ConflictResolver (pairwise detection)
│   ├── tools/
│   │   ├── spec.py                   # ToolSpec, ISensor, IActuator, schemas
│   │   ├── registry.py               # ToolRegistry (IToolRegistryPartner)
│   │   ├── discovery.py              # importlib entry-point scanner
│   │   ├── filesystem_tool.py        # FileSystemTool (HYBRID)
│   │   ├── rag_sensor_tool.py        # RagSensorTool (feature_002 integration)
│   │   └── session_tool.py           # SessionTool (HYBRID)
│   ├── reflection/
│   │   ├── engine.py                 # ReflectionEngine (orchestrator)
│   │   ├── critique_parser.py        # CritiqueParser (resilient JSON parse)
│   │   ├── safety_evaluator.py       # DefaultSafetyEvaluator (ISafetyEvaluator)
│   │   └── proposal_router.py        # ProposalRouter (dispatch + revert)
│   └── goal/manager.py               # GoalManager (IGoalManager)
├── controller/
│   ├── agent_controller.py           # AgentController
│   ├── session_controller.py         # SessionController
│   └── tool_controller.py            # ToolController
├── view/
│   ├── agent_view.py                 # Console AgentView (IAgentViewPartner)
│   └── tui/
│       ├── agent_screen.py           # AgentTUIScreen (Textual)
│       └── agent_adapter.py          # AgentAdapter factory (feature_004 integration)
└── persistence/
    ├── schema_db.py                  # Table* DDL descriptors (sqlite3)
    ├── agent_db.py                   # SessionDatabase (connection + snapshot CRUD)
    └── repositories_db.py            # Memory/Policy/Goal/Reflection repositories
```

## 2. Key Design Decisions

### 2.1 No Pydantic — stdlib dataclasses only
Pydantic is not in the project dependencies. All data models use stdlib
`dataclasses` and `enum`, consistent with the existing `session_db.py` / `rag.py`
convention. This keeps the agent subsystem dependency-free.

### 2.2 Persistence files renamed to `*_db.py`
The MVC++ linter (`mvc_check.py`) requires SQL to live in files ending
`_db.py` (guide §9). The persistence files were renamed:
- `schema.py` → `schema_db.py`
- `database.py` → `agent_db.py`
- `repositories.py` → `repositories_db.py`

This matches the existing `session_db.py` / `rag_db.py` convention and yields
**0 errors, 0 warnings** on `mvc_check.py src/agentx/agent/`.

### 2.3 ISensor/IActuator method naming
The design doc §6.1/§6.2 shows both interfaces with `get_schema()`. For hybrid
tools (e.g. `FileSystemTool`) this creates a return-type conflict. The
interfaces were split into `get_sensor_schema()` (ISensor) and
`get_actuator_schema()` (IActuator) — functionally equivalent, unambiguous.

### 2.4 AgentTUIScreen virtual subclass registration
`AgentTUIScreen` extends Textual's `Screen` (metaclass `_MessagePumpMeta`).
Inheriting from `IAgentViewPartner` (ABCMeta) causes a metaclass conflict.
Instead, `IAgentViewPartner.register(AgentTUIScreen)` is called at module
level to register it as a virtual subclass. `isinstance` checks pass at
runtime; the adapter uses `cast()` for the static checker.

### 2.5 Condition DSL — recursive-descent parser
The policy condition DSL (design §7.2) is implemented as a tokenizer +
recursive-descent parser producing an AST, evaluated by a visitor against
`PolicyContext`. Compilation is cached per rule (`CompiledCondition`).
Unknown identifiers/functions raise `ConditionCompileError` at load time
(fail-fast). Evaluation errors degrade to `False` (non-fatal at `decide()`).

## 3. Integration Points

| Feature | Integration | Status |
|---------|-------------|--------|
| **feature_004** (Modern UI) | `AgentAdapter` factory wires `AgentController` ↔ `AgentTUIScreen` | ✅ Ready |
| **feature_001** (Session Objectives) | `IGoalManager` is the swap point; `GoalManager` is the stub | ✅ Stub ready |
| **feature_002** (RAG) | `RagSensorTool` wraps `Rag.query()`; `Agent.set_rag()` injects the instance | ✅ Ready |
| **AI Service** | `IAIServicePartner` abstracts `AIService`; injected via `Agent.set_ai_service()` | ✅ Ready |

## 4. MVC++ Compliance

```
$ uv run scripts/omt/mvc_check.py src/agentx/agent/ --json
{ "files_scanned": 38, "errors": 0, "warnings": 0, "findings": [] }
```

- **View ↔ Model isolation**: All views depend on `IAgentViewPartner`, never on `Agent`/`MemoryManager`/etc.
- **SQL in DP classes**: All SQL lives in `*_db.py` files under `persistence/`.
- **Partner ABCs**: All Partners inherit `ABC` with `@abstractmethod`.
- **No god controllers**: Controllers are <120 loc each, delegate to the Agent facade.
- **No Controller in model/**: Model-layer classes are named `*Manager`/`*Engine`/`*Registry`.

## 5. Smoke Test

A minimal perceive→decide→act→reflect cycle runs successfully:
```
Agent created: test-agent  state: PERCEIVING
Tools: [filesystem (HYBRID), rag_query (SENSOR), session (HYBRID)]
Cycle result: decision="no matching rule"  action=None
```
(With no policy rules configured, the engine returns a NOOP decision — correct.)

## 6. Deferred to Testing Phase (T1–T6)

- Unit tests for each subsystem (PolicyEngine, MemoryManager, GoalManager, ToolRegistry, ReflectionEngine)
- Integration tests for the full perceive→decide→act→reflect cycle
- Persistence round-trip tests (snapshot save → load → state equality)
- TUI e2e tests with Textual pilot
- Performance tests (policy eval <50ms, persistence <100ms)
