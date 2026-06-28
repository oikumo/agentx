# Analysis 004: Sequence Diagrams — feature_007.agentx_intelligent_agent_behaviour

> **Phase:** Analysis | **Artifact:** analysis_004_sequence_diagrams.md
> **Feature:** feature_007.agentx_intelligent_agent_behaviour | **Task:** A3

---

## Sequence Diagram Overview

Key flows showing the **Sensor → Decide → Act → Reflect** cycle and session management.

---

## SD1: Agent Perception Cycle

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Agent
    participant ToolRegistry
    participant Sensor as ISensor
    participant EnvModel as EnvironmentModel
    participant VolatileMem as VolatileMemory
    participant PolicyEngine

    Note over Agent: Perception Cycle Triggered (periodic/event)
    Agent->>ToolRegistry: listSensors()
    ToolRegistry-->>Agent: [SensorId...]
    
    loop For each Sensor
        Agent->>Sensor: sense()
        Sensor-->>Agent: SensorReading
        Agent->>EnvModel: update(reading)
        Agent->>VolatileMem: put(sensorCache, reading)
    end
    
    Agent->>VolatileMem: put(workingContext.environment, EnvModel)
    Agent->>PolicyEngine: notifyEnvironmentChanged(EnvModel)
    PolicyEngine-->>Agent: PolicyDecision? (if reactive rules match)
    
    opt Reactive Rule Fired
        Agent->>Agent: decide() → act()
    end
```

---

## SD2: Action Execution Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Agent
    participant PolicyEngine
    participant ToolRegistry
    participant Actuator as IActuator
    participant VolatileMem as VolatileMemory
    participant ReflectionEngine
    participant EnvModel as EnvironmentModel

    Note over Agent: Decision Made (from SD1 or Goal Pursuit)
    Agent->>PolicyEngine: evaluate(context)
    PolicyEngine-->>Agent: PolicyDecision {action, confidence}
    
    alt Confidence < Threshold AND AutonomyLevel requires confirmation
        Agent->>User: requestConfirmation(action)
        User-->>Agent: confirmed / rejected
        alt Rejected
            Agent->>PolicyEngine: requestAlternative()
            Note right of Agent: Loop back to evaluate
        end
    end
    
    Agent->>ToolRegistry: getActuator(action.actuatorId)
    ToolRegistry-->>Agent: Actuator
    
    Agent->>Actuator: validate(command)
    Actuator-->>Agent: ValidationResult
    
    alt Invalid
        Agent->>PolicyEngine: requestAlternative()
    else Valid
        Agent->>Actuator: act(command)
        Actuator-->>Agent: ActuatorResult {success, output, sideEffects}
        
        Agent->>VolatileMem: store(actionResult)
        Agent->>EnvModel: applySideEffects(sideEffects)
        
        opt Success + Goal Active
            Agent->>Agent: updateGoalProgress(result)
        end
        
        Agent->>ReflectionEngine: reflect(trace)
        ReflectionEngine-->>Agent: ReflectionEntry {critique, proposals}
        
        opt Proposals Pass Safety Check
            Agent->>Agent: applyProposals(proposals)
        end
    end
```

---

## SD3: Policy Evaluation & Update

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Agent
    participant PolicyEngine
    participant PolicyStore
    participant ReflectionEngine

    Note over User,Agent: User-Driven Policy Update
    User->>Agent: updatePolicy(rule)
    Agent->>PolicyEngine: validateRule(rule)
    PolicyEngine-->>Agent: ValidationResult
    
    alt Valid
        Agent->>PolicyEngine: checkConflicts(rule)
        PolicyEngine-->>Agent: ConflictSet
        
        opt Conflicts Exist
            Agent->>User: resolveConflicts(conflicts)
            User-->>Agent: resolvedRule
        end
        
        Agent->>PolicyStore: persist(rule)
        Agent->>PolicyEngine: addRule(rule)
        Agent->>Agent: notifyPolicyChanged()
    else Invalid
        Agent->>User: rejectWithReason(reason)
    end

    Note over Agent,ReflectionEngine: Agent-Driven (Reflection) Policy Update
    ReflectionEngine->>Agent: proposePolicyChanges(entry)
    Agent->>Agent: evaluateProposals(proposals)
    
    loop For each approved proposal
        Agent->>PolicyStore: persist(proposal.rule)
        Agent->>PolicyEngine: addRule(proposal.rule)
    end
    
    Agent->>Agent: notifyPolicyChanged()
```

---

## SD4: Goal Decomposition & Pursuit

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Agent
    participant GoalManager
    participant PolicyEngine
    participant ToolRegistry
    participant Actuator as IActuator

    User->>Agent: submitGoal(Goal{type=USER_OBJECTIVE})
    Agent->>GoalManager: addGoal(goal)
    GoalManager-->>Agent: GoalId
    
    loop Goal Pursuit Cycle
        Agent->>GoalManager: selectGoal()
        GoalManager-->>Agent: Goal (or null)
        
        alt Goal is Atomic
            Agent->>PolicyEngine: evaluateForGoal(goal, context)
            PolicyEngine-->>Agent: PolicyDecision{action}
            
            Agent->>ToolRegistry: getActuator(action.actuatorId)
            ToolRegistry-->>Agent: Actuator
            Agent->>Actuator: act(command)
            Actuator-->>Agent: ActuatorResult
            
            Agent->>GoalManager: updateProgress(goalId, result)
            
            alt SuccessCriteria Met
                Agent->>GoalManager: completeGoal(goalId, SUCCESS)
            else Failed
                Agent->>GoalManager: completeGoal(goalId, FAILED)
            end
            
        else Goal is Composite
            Agent->>GoalManager: decomposeGoal(goal)
            GoalManager-->>Agent: [SubGoal...]
            
            loop For each SubGoal
                Agent->>GoalManager: addGoal(subGoal)
            end
        end
    end
    
    opt Goal Completed
        Agent->>Agent: triggerReflection(goalTrace)
    end
```

---

## SD5: Memory Consolidation (Volatile → Persistent)

```mermaid
sequenceDiagram
    autonumber
    participant Agent
    participant VolatileMem as VolatileMemory
    participant PersistentMem as PersistentMemory
    participant VectorIndex
    participant EpisodicLog

    Note over Agent: Consolidation Trigger (timer/significance)
    Agent->>VolatileMem: getCandidates(criteria)
    VolatileMem-->>Agent: [MemoryEntry...]
    
    loop For each candidate
        Agent->>PersistentMem: prepareForPersistence(entry)
        PersistentMem->>VectorIndex: generateEmbedding(entry.content)
        VectorIndex-->>PersistentMem: embedding
        PersistentMem->>EpisodicLog: append(entry)
        PersistentMem-->>Agent: persistedEntry
        
        Note right of Agent: optional eviction
        Agent->>VolatileMem: evict(entry.id)
    end
    
    Agent->>VolatileMem: updateIndices()
    Agent->>PersistentMem: commit()
```

---

## SD6: Reflection Cycle

```mermaid
sequenceDiagram
    autonumber
    participant Agent
    participant ReflectionEngine
    participant AIService as IAIService
    participant PolicyEngine
    participant MemoryManager
    participant ReflectionLog

    Note over Agent: Reflection Triggered (periodic/post-goal/post-failure/user)
    Agent->>ReflectionEngine: reflect(trace)
    
    ReflectionEngine->>ReflectionEngine: buildPrompt(trace)
    ReflectionEngine->>AIService: complete(prompt)
    AIService-->>ReflectionEngine: Response (streaming or batch)
    
    ReflectionEngine->>ReflectionEngine: parseResponse(response)
    ReflectionEngine-->>Agent: ReflectionEntry {critique, proposals}
    
    Agent->>ReflectionLog: append(entry)
    
    loop For each proposal
        alt ProposalType.POLICY_CHANGE
            Agent->>PolicyEngine: evaluateProposal(proposal)
            opt Approved
                Agent->>PolicyEngine: addRule(proposal.rule)
        else ProposalType.MEMORY_UPDATE
            Agent->>MemoryManager: store(proposal.entry, PERSISTENT)
        else ProposalType.GOAL_ADJUSTMENT
            Agent->>GoalManager: adjustGoal(proposal.goalId, proposal.changes)
        end
    end
```

---

## SD7: Session Persistence

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant Agent
    participant PersistenceManager
    participant SessionDB as SQLite/JSON

    Note over User,Agent: Save Session
    User->>Agent: persistSession()
    Agent->>Agent: collectState()
    Agent->>PersistenceManager: save(snapshot)
    PersistenceManager->>SessionDB: BEGIN TRANSACTION
    PersistenceManager->>SessionDB: INSERT/UPDATE agent_state
    PersistenceManager->>SessionDB: INSERT/UPDATE memory_entries
    PersistenceManager->>SessionDB: INSERT/UPDATE policy_rules
    PersistenceManager->>SessionDB: INSERT/UPDATE goals
    PersistenceManager->>SessionDB: INSERT/UPDATE reflections
    PersistenceManager->>SessionDB: COMMIT
    PersistenceManager-->>Agent: saved
    Agent-->>User: session persisted

    Note over User,Agent: Resume Session
    User->>Agent: resumeSession(agentId)
    Agent->>PersistenceManager: load(agentId)
    PersistenceManager->>SessionDB: SELECT * FROM agent_state WHERE id=?
    PersistenceManager->>SessionDB: SELECT * FROM memory WHERE agent_id=?
    PersistenceManager->>SessionDB: SELECT * FROM policies WHERE agent_id=?
    PersistenceManager->>SessionDB: SELECT * FROM goals WHERE agent_id=?
    PersistenceManager->>SessionDB: SELECT * FROM reflections WHERE agent_id=?
    PersistenceManager-->>Agent: SessionSnapshot
    Agent->>Agent: restoreState(snapshot)
    Agent->>Agent: reinitializeTools()
    Agent->>Agent: startPerceptionCycle()
    Agent-->>User: session resumed
```

---

## SD8: Tool Registration & Discovery

```mermaid
sequenceDiagram
    autonumber
    participant Agent
    participant ToolRegistry
    participant Sensor as ISensor
    participant Actuator as IActuator

    Note over Agent: Startup / Dynamic Tool Loading
    Agent->>ToolRegistry: registerSensor(sensor)
    ToolRegistry->>Sensor: getSchema()
    Sensor-->>ToolRegistry: SensorSchema
    ToolRegistry->>ToolRegistry: validateSchema(schema)
    ToolRegistry-->>Agent: registered
    
    Agent->>ToolRegistry: registerActuator(actuator)
    ToolRegistry->>Actuator: getSchema()
    Actuator-->>ToolRegistry: ActuatorSchema
    ToolRegistry->>ToolRegistry: validateSchema(schema)
    ToolRegistry-->>Agent: registered
    
    Note over Agent: Runtime Discovery
    Agent->>ToolRegistry: listSensors()
    ToolRegistry-->>Agent: [SensorId, Schema...]
    Agent->>ToolRegistry: listActuators()
    ToolRegistry-->>Agent: [ActuatorId, Schema...]
    
    Agent->>ToolRegistry: getSensor("filesystem")
    ToolRegistry-->>Agent: FileSystemTool
    Agent->>ToolRegistry: getActuator("filesystem")
    ToolRegistry-->>Agent: FileSystemTool
```

---

## Summary of Participants per Flow

| Sequence | Primary Participants |
|----------|---------------------|
| SD1: Perception | Agent, ToolRegistry, ISensor, EnvironmentModel, VolatileMemory, PolicyEngine |
| SD2: Action | Agent, PolicyEngine, ToolRegistry, IActuator, VolatileMemory, ReflectionEngine |
| SD3: Policy Update | User, Agent, PolicyEngine, PolicyStore, ReflectionEngine |
| SD4: Goal Pursuit | User, Agent, GoalManager, PolicyEngine, ToolRegistry, IActuator |
| SD5: Memory Consolidation | Agent, VolatileMemory, PersistentMemory, VectorIndex, EpisodicLog |
| SD6: Reflection | Agent, ReflectionEngine, IAIService, PolicyEngine, MemoryManager, ReflectionLog |
| SD7: Session Persistence | User, Agent, PersistenceManager, SQLite/JSON |
| SD8: Tool Registration | Agent, ToolRegistry, ISensor, IActuator |

---

## Traceability to Use Cases (A1) & Class Diagram (A2)

| Sequence | Use Case | Key Classes |
|----------|----------|-------------|
| SD1 | UC1: Perceive Environment | Agent, ToolRegistry, ISensor, EnvironmentModel |
| SD2 | UC2: Execute Action | Agent, PolicyEngine, IActuator, ReflectionEngine |
| SD3 | UC3: Update Policy | Agent, PolicyEngine, PolicyStore, ReflectionEngine |
| SD4 | UC5: Pursue Goal | Agent, GoalManager, PolicyEngine, ToolRegistry |
| SD5 | UC4: Manage Memory (consolidate) | VolatileMemory, PersistentMemory, VectorIndex |
| SD6 | UC6: Reflect on Behavior | ReflectionEngine, IAIService, PolicyEngine |
| SD7 | UC7: Persist Session, UC8: Resume Session | Agent, PersistenceManager, SessionSnapshot |
| SD8 | UC1, UC2 (tool setup) | ToolRegistry, ISensor, IActuator |

---

## Notes

- All sequences follow MVC++: Agent acts as Controller; Tools/Models as Model; Views not shown (separate)
- ReflectionEngine uses `IAIService` abstraction → testable with mock
- PolicyEngine is stateless → pure function `evaluate(context)` → Decision
- Session persistence is atomic (transaction) → crash-safe
- ToolRegistry validates schemas at registration → fail-fast