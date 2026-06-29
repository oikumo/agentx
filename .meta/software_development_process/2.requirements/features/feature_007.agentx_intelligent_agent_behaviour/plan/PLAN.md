# PLAN — feature_007: Agentx_Intelligent_Agent_Behaviour

> Task type: **major_feature** · See `omt_agent_guide.md §12` for the required artifacts.

## Objective

Implement an intelligent agent framework where agents have persistent session state, sensor/actuator tools, policy-driven behavior, and internal memory/reasoning capabilities that evolve during execution.

## Steps

### Analysis Phase
- [ ] **A1** Create use case diagram with actors (User, Agent, Environment, Tool Registry) and use cases (Perceive Environment, Execute Action, Update Policy, Manage Memory, Pursue Goal, Reflect)
- [ ] **A2** Create class diagram: Agent, Environment, Sensor, Actuator, Tool, Memory (Volatile/Persistent), Policy, Goal, Session, ToolRegistry
- [ ] **A3** Create sequence diagrams for key flows: Agent Perception Cycle, Action Execution, Policy Evaluation, Goal Decomposition, Memory Consolidation, Reflection Cycle
- [ ] **A4** Create state diagram: Agent Lifecycle (Created → Initialized → Perceiving → Deciding → Acting → Reflecting → Persisting → Terminated), Session Lifecycle
- [ ] **A5** Create data dictionary: SessionConfig, AgentConfig, MemoryEntry, PolicyRule, Goal, SubGoal, ToolSpec, SensorReading, ActuatorCommand, ReflectionEntry
- [ ] **A6** Document non-functional requirements: persistence latency <100ms, memory growth <10MB/session, policy eval <50ms, tool registry extensibility
- [ ] **A7** Create traceability matrix: FEATURE.md requirements → Analysis artifacts → Design artifacts
- [ ] **A8** Write Analysis summary document: `analysis_001_agent_architecture.md`

### Design Phase
- [ ] **D1** Scaffold design doc via `new_feature.py` → `design_001_agent_framework.md`
- [ ] **D2** Define MVC++ architecture: Model (Agent, Session, Memory, Policy, Goal), View (AgentView, MemoryView, PolicyView), Controller (AgentController, SessionController, ToolController), Abstract Partners (IEnvironment, IToolRegistry, IPersistence)
- [ ] **D3** Define interfaces: ISensor, IActuator, ITool, IMemoryStore, IPolicyEngine, IGoalManager, IReflectionEngine
- [ ] **D4** Define data models: SessionConfig (JSON/YAML), MemoryEntry (volatile/persistent), PolicyRule (condition→action), GoalTree, ReflectionLog
- [ ] **D5** Define persistence schema: stdlib `sqlite3` DDL (`Table*` descriptor classes with idempotent `CREATE TABLE IF NOT EXISTS`) for Session, Memory, Policy, Goals, Reflections — **no ORM, no Alembic** (matches existing `SessionDatabase`/`RagDatabase` convention)
- [ ] **D6** Define tool registry protocol: ToolSpec (name, description, schema, side_effects), registration, discovery, composition
- [ ] **D7** Define policy engine: rule evaluation, priority, conflict resolution, learning/adaptation hooks
- [ ] **D8** Define reflection engine: reasoning trace, decision log, self-critique, improvement proposals
- [ ] **D9** Define MVC++ compliance checklist (no View↔Model, ABC partners, no SQL in controllers, no god controllers)
- [ ] **D10** Write Design summary document: `design_001_agent_framework.md`

### Implementation Phase
- [ ] **I1** Scaffold feature directory: `5.implementation/features/feature_007.agentx_intelligent_agent_behaviour/`
- [ ] **I2** Implement Model layer: `src/agentx/agent/model/` — Agent, Session, MemoryStore, PolicyEngine, GoalManager, ReflectionEngine
- [ ] **I3** Implement Abstract Partners: `src/agentx/agent/partners/` — IEnvironment, IToolRegistry, IPersistence (ABCs)
- [ ] **I4** Implement Controller layer: `src/agentx/agent/controller/` — AgentController, SessionController, ToolController
- [ ] **I5** Implement View layer: `src/agentx/agent/view/` — AgentView, MemoryView, PolicyView, ReflectionView (Textual widgets)
- [ ] **I6** Implement Tool Registry: `src/agentx/agent/tools/` — ToolRegistry, BaseTool, SensorMixin, ActuatorMixin, built-in tools (FS, Session, RAG, UI)
- [ ] **I7** Implement Persistence: `src/agentx/agent/persistence/` — stdlib `sqlite3` backend (`schema.py` DDL + `database.py` connection/CRUD + repositories), SessionRepository, MemoryRepository, PolicyRepository — **no ORM, no Alembic**
- [ ] **I8** Implement Policy Engine: rule DSL, evaluation loop, priority resolution, adaptation hooks
- [ ] **I9** Implement Reflection Engine: reasoning trace capture, self-critique prompts, improvement proposal generation
- [ ] **I10** Integrate with feature_004 (Modern UI): AgentView widget, session dashboard, reflection log viewer
- [ ] **I11** Integrate with feature_001 (Session Objectives): GoalManager consumes user objectives
- [ ] **I12** Integrate with feature_002 (RAG): RAG as Sensor tool for knowledge retrieval
- [ ] **I13** Write implementation notes: `5.implementation/features/feature_007.../impl_notes.md`

### Testing Phase
- [ ] **T1** Unit tests: Model classes, PolicyEngine, GoalManager, ReflectionEngine, MemoryStore, ToolRegistry
- [ ] **T2** Integration tests: Agent perception→decision→action cycle, Session persistence/load, Tool registration/discovery
- [ ] **T3** MVC++ compliance tests: `uv run scripts/omt/mvc_check.py src/agentx/agent/`
- [ ] **T4** E2E tests (Textual): Agent session lifecycle, goal pursuit, reflection capture, session resume
- [ ] **T5** Performance tests: Policy eval latency, memory growth, persistence latency
- [ ] **T6** Write test report: `6.testing/features/feature_007.agentx_intelligent_agent_behaviour/test_report.md`

## Artifacts produced

- Requirements: `feature_007.agentx_intelligent_agent_behaviour/FEATURE.md`
- Analysis: `3.analysis/features/feature_007.agentx_intelligent_agent_behaviour/analysis_001_agent_architecture.md`
- Analysis: `3.analysis/features/feature_007.agentx_intelligent_agent_behaviour/analysis_002_use_cases.md`
- Analysis: `3.analysis/features/feature_007.agentx_intelligent_agent_behaviour/analysis_003_class_diagram.md`
- Analysis: `3.analysis/features/feature_007.agentx_intelligent_agent_behaviour/analysis_004_sequence_diagrams.md`
- Analysis: `3.analysis/features/feature_007.agentx_intelligent_agent_behaviour/analysis_005_state_diagram.md`
- Analysis: `3.analysis/features/feature_007.agentx_intelligent_agent_behaviour/analysis_006_data_dictionary.md`
- Analysis: `3.analysis/features/feature_007.agentx_intelligent_agent_behaviour/analysis_007_nfrs.md`
- Analysis: `3.analysis/features/feature_007.agentx_intelligent_agent_behaviour/analysis_008_traceability.md`
- Design: `4.design/features/feature_007.agentx_intelligent_agent_behaviour/design_001_agent_framework.md`
- Implementation: `5.implementation/features/feature_007.agentx_intelligent_agent_behaviour/impl_notes.md`
- Testing: `6.testing/features/feature_007.agentx_intelligent_agent_behaviour/test_report.md`
