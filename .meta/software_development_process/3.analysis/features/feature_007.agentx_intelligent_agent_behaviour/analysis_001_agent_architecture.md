# Analysis 001: Agent Architecture Summary — feature_007.agentx_intelligent_agent_behaviour

> **Phase:** Analysis | **Artifact:** analysis_001_agent_architecture.md
> **Feature:** feature_007.agentx_intelligent_agent_behaviour | **Task:** A8

---

## Executive Summary

This document summarizes the complete Analysis phase for **feature_007: Agentx Intelligent Agent Behaviour**. The agent architecture transforms agentx from a reactive command-line tool into an **autonomous intelligent agent** that perceives its environment, pursues goals through policy-driven decisions, maintains persistent memory across sessions, and continuously improves through AI-powered reflection.

---

## Problem Statement

**Current State (feature_004 complete):** agentx provides a modern TUI with Chat, RAG, and Repository management screens. The application is **reactive** — it waits for user commands and executes them.

**Desired State:** An **intelligent agent** that:
- Lives in an environment (filesystem, repos, session state)
- Perceives changes via sensors (filesystem watch, RAG queries, session events)
- Makes decisions via configurable policies (rules with priorities, conflict resolution)
- Acts via actuators (file ops, session management, RAG ingestion)
- Remembers via two-tier memory (volatile working context + persistent semantic/episodic)
- Pursues goals hierarchically (user objectives → agent sub-goals)
- Reflects on its behavior via AI self-critique (proposing policy/memory/goal improvements)
- Persists its entire identity (config + state + memory + policies + goals + reflections) across sessions

---

## Architecture Overview

### Core Agent Loop (Sensor → Decide → Act → Reflect)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        AGENT MAIN LOOP                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐         │
│   │  PERCEIVE    │───▶│   DECIDE     │───▶│     ACT      │         │
│   │  (Sensors)   │    │ (PolicyEngine)│    │ (Actuators)  │         │
│   └──────────────┘    └──────────────┘    └──────────────┘         │
│        │                     │                     │                │
│        ▼                     ▼                     ▼                │
│   EnvironmentModel      PolicyDecision      ActuatorResult         │
│   SensorReadings        GoalSelection       EnvChanges             │
│   VolatileMemory        ActionPlan          MemoryUpdate           │
│                                                                      │
│        ▲                     │                     │                │
│        │                     ▼                     │                │
│        │              ┌──────────────┐             │                │
│        └──────────────│  REFLECT     │◀────────────┘                │
│                       │ (ReflectionEngine)                         │
│                       └──────────────┘                              │
│                              │                                      │
│                              ▼                                      │
│                       ReflectionEntry                               │
│                       (Critique + Proposals)                        │
│                              │                                      │
│                    ┌─────────┴─────────┐                            │
│                    ▼                   ▼                            │
│             PolicyEngine           MemoryManager                   │
│             (new rules)            (new entries)                   │
│                              │                   │                  │
│                              └─────────┬─────────┘                  │
│                                        ▼                            │
│                              ┌──────────────────┐                   │
│                              │   PERSIST        │                   │
│                              │ (SessionSnapshot)│                   │
│                              └──────────────────┘                   │
└─────────────────────────────────────────────────────────────────────┘
```

### Seven Subsystems (from Class Diagram A2)

| # | Subsystem | Purpose | Key Classes |
|---|-----------|---------|-------------|
| 1 | **Configuration & Identity** | Agent config, versioning, autonomy levels | AgentConfig, SensorConfig, ActuatorConfig, AutonomyLevel |
| 2 | **Perception & Environment** | Sensors → EnvironmentModel → Facts | EnvironmentModel, SensorReading, Fact, ToolRegistry, ISensor |
| 3 | **Tools & Tool Registry** | Sensors/actuators as pluggable tools | ToolRegistry, ISensor, IActuator, SensorSchema, ActuatorSchema |
| 4 | **Memory System** | Two-tier: volatile (working) + persistent (semantic/episodic) | MemoryManager, VolatileMemory, PersistentMemory, VectorIndex, EpisodicLog |
| 5 | **Policy Engine** | Declarative rules: condition → action, priority, conflict resolution | PolicyEngine, PolicyRule, ConditionExpr, PolicyAction, PolicyDecision |
| 6 | **Goal Management** | Hierarchical goals with AND/OR decomposition | GoalManager, Goal, GoalTree, Precondition, SuccessCriteria |
| 7 | **Reflection Engine** | AI-powered self-critique → actionable proposals | ReflectionEngine, IAIService, DecisionTrace, ReflectionEntry, Critique, Proposal |
| 8 | **Persistence** | Atomic session snapshots, versioned schema | PersistenceManager, SessionSnapshot, WorkingContext |

---

## Key Design Decisions (from A2 §8)

| Decision | Rationale |
|----------|-----------|
| **Agent as Facade** | Single entry point orchestrating all subsystems; follows MVC++ Controller pattern |
| **Tool Registry with ISensor/IActuator** | Clear perception vs. action separation; enables tool composition; testable via mocks |
| **Two-tier Memory** | Volatile for low-latency working context; Persistent for long-term knowledge; consolidation bridge |
| **Policy Engine as Rule Evaluator** | Declarative, inspectable, hot-reloadable; supports User-defined + Reflection-proposed rules |
| **Goal Tree with AND/OR Decomposition** | Hierarchical planning; supports User objectives → Agent sub-goals; tracks progress |
| **Reflection Engine using AIService** | Reuses existing AI infrastructure; LLM-based self-critique; produces actionable proposals |
| **Versioned Session Snapshots** | Atomic persistence; migration-friendly; supports resume + audit trail |

---

## MVC++ Compliance (from A2 §9)

### Abstract Partners (to be implemented in Design)

| Partner | Purpose | Implemented By |
|---------|---------|----------------|
| `IAgentViewPartner` | View → Agent: user input, display requests | TUI/Console adapters |
| `IAgentModelPartner` | Model → Agent: persistence events, config changes | SessionDatabase, ConfigStore |
| `IToolRegistryPartner` | Agent → Tools: discovery, health checks | ToolRegistry |
| `IMemoryStorePartner` | Agent → Memory: CRUD, indexing | SQLiteVectorStore, JSONStore |
| `IPolicyStorePartner` | Agent → Policy: CRUD, versioning | PolicyDatabase |

### Agent as Abstract Partner (to Controllers/Views)

```python
class IAgentPartner(ABC):
    @abstractmethod
    def start_session(self, config: AgentConfig) -> AgentId: ...
    @abstractmethod
    def resume_session(self, agent_id: AgentId) -> AgentId: ...
    @abstractmethod
    def submit_goal(self, agent_id: AgentId, goal: Goal) -> GoalId: ...
    @abstractmethod
    def get_status(self, agent_id: AgentId) -> AgentStatus: ...
    @abstractmethod
    def get_reflection_log(self, agent_id: AgentId, limit: int) -> list[ReflectionEntry]: ...
    @abstractmethod
    def update_policy(self, agent_id: AgentId, rule: PolicyRule) -> None: ...
    @abstractmethod
    def set_autonomy(self, agent_id: AgentId, level: AutonomyLevel) -> None: ...
```

### MVC++ Layer Separation

| Layer | Components | Rules |
|-------|------------|-------|
| **Model** | Agent, MemoryManager, PolicyEngine, GoalManager, ReflectionEngine, PersistenceManager, ToolRegistry | No UI imports; pure domain logic |
| **View** | AgentTUIScreen, AgentView, ReflectionView, PolicyView, MemoryView (Textual widgets) | No Model imports; only calls Abstract Partner |
| **Controller** | AgentController, SessionController, ToolController | Orchestrates View ↔ Model via Abstract Partners |

---

## Integration Points (from A2 §10)

| Feature | Integration Point | Approach |
|---------|------------------|----------|
| **feature_004 (Modern UI)** | `TUIProvider` → register `AgentAdapter` | New `AgentTUIScreen` implementing `IAgentView` |
| **feature_002 (RAG)** | `Rag` class → wrap as `RagSensorTool` | Implement `ISensor` using `Rag.query()` |
| **feature_001 (Session Objectives)** | `IGoalManager` interface | Stub implementation now; swap when 001 lands |
| **Session Persistence** | Extend `SessionDatabase` | Add Agent tables; reuse SQLite pattern |
| **AI Service** | Reuse `AIService` for Reflection | Existing streaming + provider abstraction |

---

## Data Flow Summary

### Perception Cycle (SD1)
```
Agent.perceive()
  → ToolRegistry.listSensors()
  → for each sensor: sensor.sense() → SensorReading
  → EnvironmentModel.update(reading)
  → VolatileMemory.put(sensorCache, reading)
  → PolicyEngine.notifyEnvironmentChanged()
  → (optional) reactive PolicyDecision → decide()/act()
```

### Action Execution (SD2)
```
Agent.act(command)
  → PolicyEngine.evaluate(context) → PolicyDecision
  → (if low confidence + autonomy requires) User confirmation
  → ToolRegistry.getActuator()
  → Actuator.validate(command)
  → Actuator.act(command) → ActuatorResult
  → VolatileMemory.store(result)
  → EnvironmentModel.applySideEffects()
  → GoalManager.updateProgress()
  → ReflectionEngine.reflect(trace) → ReflectionEntry
  → (if proposals pass safety) apply to PolicyEngine/MemoryManager/GoalManager
```

### Goal Pursuit (SD4)
```
User.submitGoal(USER_OBJECTIVE)
  → GoalManager.addGoal()
  → loop: GoalManager.selectGoal() → active Goal
    → if atomic: PolicyEngine.evaluateForGoal() → ActuatorCommand → act()
    → if composite: GoalManager.decomposeGoal() → sub-goals → recurse
    → on completion: GoalManager.completeGoal() → trigger Reflection
```

### Memory Consolidation (SD5)
```
Timer/Significance trigger
  → VolatileMemory.getCandidates(criteria)
  → for each: PersistentMemory.prepareForPersistence()
    → VectorIndex.generateEmbedding()
    → EpisodicLog.append()
  → VolatileMemory.evict() (optional)
  → PersistentMemory.commit()
```

### Reflection Cycle (SD6)
```
Trigger (periodic/post-goal/post-failure/user)
  → ReflectionEngine.reflect(trace)
  → buildPrompt(trace) using Jinja2 template
  → AIService.complete(prompt) → response
  → parseResponse() → Critique + Proposals
  → ReflectionLog.append(entry)
  → for each proposal: route to PolicyEngine/MemoryManager/GoalManager (safety-checked)
```

### Session Persistence (SD7)
```
Save: collectState() → PersistenceManager.save() → SQLite transaction (all tables)
Load: PersistenceManager.load() → SessionSnapshot → Agent.restoreState() → reinitializeTools() → startPerceptionCycle()
```

---

## Non-Functional Highlights (from A7)

| Category | Key Targets |
|----------|-------------|
| **Performance** | Perception <200ms, Decision <50ms, Actuation <100ms (FS), Reflection <30s (AI) |
| **Scalability** | 10k volatile, 100k persistent entries, 1k policies, 10 active goals |
| **Reliability** | Atomic persistence, sensor/actuator fault isolation, AI degradation graceful |
| **Security** | Filesystem sandbox, policy safety evaluation, data sanitization for AI |
| **Usability** | Pause <100ms, autonomy change immediate, observable reasoning |

---

## Analysis Artifacts Produced

| Artifact | Path | Purpose |
|----------|------|---------|
| **FEATURE.md** | `2.requirements/.../FEATURE.md` | Requirements, scope, success criteria |
| **PLAN.md** | `2.requirements/.../plan/PLAN.md` | Phase tasks, feasibility, risk register |
| **FEASIBILITY.md** | `2.requirements/.../plan/FEASIBILITY.md` | Technical validation, go/no-go |
| **A1: Use Cases** | `3.analysis/.../analysis_002_use_cases.md` | 8 use cases with specs, traceability |
| **A2: Class Diagrams** | `3.analysis/.../analysis_003_class_diagram.md` | 8 subsystem diagrams + relationships |
| **A3: Sequence Diagrams** | `3.analysis/.../analysis_004_sequence_diagrams.md` | 8 key flows (SD1-SD8) |
| **A5: State Diagrams** | `3.analysis/.../analysis_005_state_diagram.md` | 8 state machines (agent, session, goal, policy, memory, reflection, tool, composite) |
| **A6: Data Dictionary** | `3.analysis/.../analysis_006_data_dictionary.md` | 50+ entities with fields, types, constraints |
| **A7: NFRs** | `3.analysis/.../analysis_007_nfrs.md` | Perf, scale, reliability, security, usability |
| **A8: Traceability** | `3.analysis/.../analysis_008_traceability.md` | Full vertical + horizontal traceability matrix |

---

## Readiness for Design Phase

### ✅ Analysis Complete — All Required Artifacts Present
- [x] Use cases (A1) — 8 UCs covering all success criteria
- [x] Class diagrams (A2) — 7 subsystems + integration view
- [x] Sequence diagrams (A3) — 8 key flows
- [x] State diagrams (A5) — 8 state machines
- [x] Data dictionary (A6) — Complete entity definitions
- [x] NFRs (A7) — Quantified targets + acceptance tests
- [x] Traceability matrix (A8) — FEATURE.md → Design inputs mapped

### 🔄 Design Phase Inputs Ready
1. **MVC++ Architecture** defined with Abstract Partners
2. **Interfaces** specified: ISensor, IActuator, IAIService, IAgentPartner, 5 Model Partners
3. **Data models** fully defined in Data Dictionary (A6)
4. **Persistence schema** implied by SessionSnapshot + MemoryEntry + PolicyRule + Goal + ReflectionEntry
5. **Integration contracts** with features 001, 002, 004 documented
6. **NFR targets** to drive performance testing

### 📋 Next Steps (Design Phase)
1. **Scaffold design doc** via `new_feature.py` → `design_001_agent_framework.md`
2. **Declare `omt_phase Design`** with design doc path
3. **Design tasks (D1-D10)** per PLAN.md:
   - D1: Scaffold design doc
   - D2: MVC++ component diagram
   - D3: Interface definitions (Abstract Partners)
   - D4: Data models (Pydantic/dataclasses)
   - D5: Persistence schema (stdlib `sqlite3` DDL, no ORM, no migrations)
   - D6: Tool registry protocol
   - D7: Policy engine DSL
   - D8: Reflection engine prompt engineering
   - D9: MVC++ compliance checklist
   - D10: Design summary

---

## Risk Summary (from FEASIBILITY.md)

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Tool Registry complexity | Medium | High | Start with 3 built-in tools; extend incrementally |
| Policy Engine performance | Low | Medium | Cache rule evaluation; lazy compilation; profile early |
| Reflection Engine LLM costs | Medium | Low | Configurable frequency; local models via Ollama/LlamaCPP |
| Memory bloat | Medium | Medium | TTL policies, compaction, size limits |
| MVC++ violations in new code | Low | High | Run `mvc_check.py` after each component; TDD |
| Session/agent config migration | Low | Medium | Versioned schema from day 1; migration scripts |
| Feature_001 dependency (GoalManager) | High | Medium | Design `IGoalManager` interface now; stub impl; swap later |

---

## Conclusion

The Analysis phase establishes a **complete, traceable, and feasible** architecture for an intelligent agent framework. All seven subsystems are designed with clear interfaces, MVC++ compliance, and integration paths to existing features. The design phase can proceed immediately with scaffolded artifacts and well-defined interfaces.

**Recommendation:** Proceed to Design phase. Scaffold `design_001_agent_framework.md` via `new_feature.py`, declare `omt_phase Design`, and begin with MVC++ component diagram and Abstract Partner interfaces.