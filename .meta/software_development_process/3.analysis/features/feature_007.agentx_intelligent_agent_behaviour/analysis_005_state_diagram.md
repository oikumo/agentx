# Analysis 005: State Diagrams — feature_007.agentx_intelligent_agent_behaviour

> **Phase:** Analysis | **Artifact:** analysis_005_state_diagram.md
> **Feature:** feature_007.agentx_intelligent_agent_behaviour | **Task:** A5

---

## 1. Agent Lifecycle State Machine

```mermaid
stateDiagram-v2
    [*] --> INITIALIZING : start_session() / resume_session()
    INITIALIZING --> PERCEIVING : tools registered, config loaded
    INITIALIZING --> PAUSED : user request / error
    INITIALIZING --> TERMINATED : fatal error
    
    PERCEIVING --> DECIDING : environment model updated
    PERCEIVING --> PAUSED : user pause request
    PERCEIVING --> PERSISTING : periodic / goal complete / shutdown
    PERCEIVING --> TERMINATED : fatal error
    
    DECIDING --> ACTING : policy decision made
    DECIDING --> REFLECTING : reflection triggered
    DECIDING --> PAUSED : user pause / confirmation needed
    DECIDING --> PERCEIVING : no action needed (idle)
    DECIDING --> PERSISTING : checkpoint
    
    ACTING --> PERCEIVING : action complete, result stored
    ACTING --> REFLECTING : post-action reflection trigger
    ACTING --> PAUSED : user interrupt
    ACTING --> DECIDING : re-plan needed (failure)
    ACTING --> PERSISTING : goal complete
    
    REFLECTING --> DECIDING : proposals evaluated
    REFLECTING --> PERCEIVING : reflection complete
    REFLECTING --> PAUSED : user review of proposals
    REFLECTING --> PERSISTING : reflection logged
    
    PERSISTING --> PERCEIVING : state saved
    PERSISTING --> PAUSED : user request during save
    PERSISTING --> TERMINATED : shutdown complete
    
    PAUSED --> PERCEIVING : user resume
    PAUSED --> DECIDING : user provides decision
    PAUSED --> INITIALIZING : config change requires reload
    PAUSED --> TERMINATED : user quit
    
    TERMINATED --> [*]
```

### State Descriptions

| State | Description | Entry Actions | Exit Actions |
|-------|-------------|---------------|--------------|
| **INITIALIZING** | Loading config, restoring state, registering tools | Load AgentConfig, restore PersistentMemory, PolicyStore, GoalTree; register sensors/actuators | Start perception timer |
| **PERCEIVING** | Active sensor cycle, building EnvironmentModel | Trigger perception cycle (SD1); update EnvironmentModel; notify PolicyEngine | Cancel perception timer |
| **DECIDING** | Policy evaluation, goal selection, action planning | Evaluate PolicyEngine; select goal; produce PolicyDecision | Clear decision cache |
| **ACTING** | Executing actuator command via ToolRegistry | Validate command; invoke actuator; store result; update EnvModel | Trigger reflection if needed |
| **REFLECTING** | AI-powered self-critique of recent trace | Build prompt; call AIService; parse proposals; safety check | Log ReflectionEntry |
| **PERSISTING** | Atomic session snapshot to storage | Collect all state; serialize; transactional write | Release persistence lock |
| **PAUSED** | User intervention, waiting for input | Stop all cycles; preserve volatile state | Resume from interruption point |
| **TERMINATED** | Clean shutdown | Final persist; cleanup resources; close connections | — |

---

## 2. Session Lifecycle

```mermaid
stateDiagram-v2
    [*] --> CREATED : new session
    CREATED --> ACTIVE : start_session()
    ACTIVE --> PAUSED : user pause / agent pause
    PAUSED --> ACTIVE : user resume
    ACTIVE --> PERSISTING : checkpoint / goal complete
    PERSISTING --> ACTIVE : save complete
    ACTIVE --> COMPLETED : user marks done
    ACTIVE --> ARCHIVED : user archives
    PAUSED --> ARCHIVED : user archives
    COMPLETED --> ARCHIVED : auto-archive after TTL
    ARCHIVED --> ACTIVE : user resumes (restore)
    ARCHIVED --> DELETED : user deletes
    DELETED --> [*]
```

---

## 3. Goal State Machine

```mermaid
stateDiagram-v2
    [*] --> PENDING : added to GoalTree
    PENDING --> ACTIVE : selected by GoalManager
    ACTIVE --> BLOCKED : precondition failed / resource unavailable
    BLOCKED --> ACTIVE : unblocked (sub-goal complete)
    ACTIVE --> COMPLETED : success criteria met
    ACTIVE --> FAILED : actuator failure / criteria impossible
    ACTIVE --> ABANDONED : user cancel / obsolete
    FAILED --> PENDING : retry (if policy allows)
    COMPLETED --> [*]
    FAILED --> [*]
    ABANDONED --> [*]
```

---

## 4. Policy Rule Lifecycle

```mermaid
stateDiagram-v2
    [*] --> PROPOSED : user defines / reflection proposes
    PROPOSED --> VALIDATING : syntax/semantic check
    VALIDATING --> CONFLICT_CHECK : valid
    VALIDATING --> REJECTED : invalid
    CONFLICT_CHECK --> ACTIVE : no conflicts / resolved
    CONFLICT_CHECK --> CONFLICT : conflicts exist
    CONFLICT --> ACTIVE : user/resolver resolves
    ACTIVE --> DISABLED : user disables / superseded
    DISABLED --> ACTIVE : user re-enables
    ACTIVE --> ARCHIVED : version upgrade / migration
    ARCHIVED --> [*]
    REJECTED --> [*]
```

---

## 5. Memory Entry Lifecycle (Volatile → Persistent)

```mermaid
stateDiagram-v2
    [*] --> VOLATILE : created (perception/action/reflection)
    VOLATILE --> CONSOLIDATING : meets criteria (importance/age/frequency)
    VOLATILE --> EVICTED : capacity full, low priority
    CONSOLIDATING --> PERSISTENT : embedding generated, indexed
    CONSOLIDATING --> VOLATILE : consolidation failed
    PERSISTENT --> ARCHIVED : age > TTL, low access
    ARCHIVED --> PERSISTENT : accessed (cache promotion)
    PERSISTENT --> DELETED : user purge / corruption
    ARCHIVED --> DELETED : user purge
    EVICTED --> [*]
    DELETED --> [*]
```

---

## 6. Reflection Trigger States

```mermaid
stateDiagram-v2
    [*] --> IDLE
    IDLE --> PERIODIC : timer elapsed
    IDLE --> POST_GOAL : goal completed/failed
    IDLE --> POST_FAILURE : action failed
    IDLE --> USER_REQUESTED : user triggers reflection
    PERIODIC --> REFLECTING : collect trace
    POST_GOAL --> REFLECTING : collect trace
    POST_FAILURE --> REFLECTING : collect trace
    USER_REQUESTED --> REFLECTING : collect trace
    REFLECTING --> IDLE : complete
    REFLECTING --> DEFERRED : AI unavailable
    DEFERRED --> REFLECTING : AI available
```

---

## 7. Tool Registration States

```mermaid
stateDiagram-v2
    [*] --> UNREGISTERED
    UNREGISTERED --> REGISTERING : registerSensor/Actuator()
    REGISTERING --> VALIDATING : schema received
    VALIDATING --> ACTIVE : schema valid
    VALIDATING --> FAILED : schema invalid
    ACTIVE --> UNREGISTERED : unregister() / shutdown
    FAILED --> UNREGISTERED : fix & retry
```

---

## 8. Composite: Agent Main Loop (Perception-Decision-Action-Reflection)

```mermaid
stateDiagram-v2
    [*] --> INITIALIZING
    INITIALIZING --> MAIN_LOOP : ready
    
    state MAIN_LOOP {
        [*] --> PERCEIVING
        PERCEIVING --> DECIDING : env changed / goal active
        DECIDING --> ACTING : decision made
        ACTING --> REFLECTING : trigger condition met
        REFLECTING --> PERCEIVING : loop
        DECIDING --> PERCEIVING : no action (idle)
        ACTING --> DECIDING : re-plan
    }
    
    MAIN_LOOP --> PERSISTING : checkpoint trigger
    PERSISTING --> MAIN_LOOP : saved
    MAIN_LOOP --> PAUSED : user interrupt
    PAUSED --> MAIN_LOOP : resume
    MAIN_LOOP --> TERMINATED : shutdown
    TERMINATED --> [*]
```

---

## Traceability to Use Cases (A1) & Class Diagram (A2)

| State Machine | Use Case | Key Classes |
|---------------|----------|-------------|
| Agent Lifecycle | All UC | Agent, AgentState enum |
| Session Lifecycle | UC7, UC8 | SessionSnapshot, PersistenceManager |
| Goal State | UC5 | Goal, GoalStatus, GoalManager |
| Policy Rule Lifecycle | UC3 | PolicyRule, RuleSource, PolicyEngine |
| Memory Entry Lifecycle | UC4 | MemoryEntry, MemoryTier, MemoryManager |
| Reflection Triggers | UC6 | ReflectionEngine, DecisionTrace |
| Tool Registration | UC1, UC2 | ToolRegistry, ISensor, IActuator |
| Composite Main Loop | All UC | Agent (orchestrator) |

---

## Notes

- All state machines use **hierarchical states** where applicable (MAIN_LOOP composite)
- Transitions are **event-driven** (not polling) — events from Tools, User, Timers, PolicyEngine
- **PAUSED** state is the primary user-intervention point across all machines
- **TERMINATED/DELETED** are final states — no transitions out
- State persistence (PERSISTING) captures full composite state for resume fidelity