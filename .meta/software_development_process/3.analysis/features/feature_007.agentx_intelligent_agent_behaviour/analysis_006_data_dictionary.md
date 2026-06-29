# Analysis 006: Data Dictionary — feature_007.agentx_intelligent_agent_behaviour

> **Phase:** Analysis | **Artifact:** analysis_006_data_dictionary.md
> **Feature:** feature_007.agentx_intelligent_agent_behaviour | **Task:** A6

---

## Core Data Types

### AgentId
| Property | Type | Constraints | Description |
|----------|------|-------------|-------------|
| value | string | UUID v4, required, unique | Globally unique agent identifier |

### SensorId
| Property | Type | Constraints | Description |
|----------|------|-------------|-------------|
| value | string | required, unique per agent | Sensor identifier (e.g., "filesystem", "rag_query") |

### ActuatorId
| Property | Type | Constraints | Description |
|----------|------|-------------|-------------|
| value | string | required, unique per agent | Actuator identifier (e.g., "filesystem", "session") |

### RuleId
| Property | Type | Constraints | Description |
|----------|------|-------------|-------------|
| value | string | UUID v4, required, unique | Policy rule identifier |

### GoalId
| Property | Type | Constraints | Description |
|----------|------|-------------|-------------|
| value | string | UUID v4, required, unique | Goal identifier |

### MemoryId
| Property | Type | Constraints | Description |
|----------|------|-------------|-------------|
| value | string | UUID v4, required, unique | Memory entry identifier |

### ReflectionId
| Property | Type | Constraints | Description |
|----------|------|-------------|-------------|
| value | string | UUID v4, required, unique | Reflection entry identifier |

---

## Configuration Objects

### AgentConfig
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| id | AgentId | Yes | auto-generated | Agent identity |
| name | string | Yes | "agentx-agent" | Human-readable name |
| version | int | Yes | 1 | Config schema version |
| sensors | SensorConfig[] | Yes | [] | Enabled sensor configurations |
| actuators | ActuatorConfig[] | Yes | [] | Enabled actuator configurations |
| policyConfig | PolicyConfig | Yes | default | Policy engine settings |
| memoryConfig | MemoryConfig | Yes | default | Memory system settings |
| goalConfig | GoalConfig | Yes | default | Goal manager settings |
| reflectionConfig | ReflectionConfig | Yes | default | Reflection engine settings |
| autonomyLevel | AutonomyLevel | Yes | SUPERVISED | Default autonomy |
| createdAt | DateTime | Yes | now | Creation timestamp |
| updatedAt | DateTime | Yes | now | Last modification |

### SensorConfig
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | SensorId | Yes | Sensor identifier |
| type | string | Yes | Tool type (e.g., "filesystem", "rag_query") |
| enabled | bool | Yes | Whether sensor is active |
| parameters | JsonObject | No | Tool-specific parameters |
| samplingRate | Duration | No | Polling interval (if applicable) |

### ActuatorConfig
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | ActuatorId | Yes | Actuator identifier |
| type | string | Yes | Tool type (e.g., "filesystem", "session") |
| enabled | bool | Yes | Whether actuator is active |
| parameters | JsonObject | No | Tool-specific parameters |
| requiresConfirmation | bool | No | Override autonomy for this actuator |

### PolicyConfig
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| rulesFile | string | No | "policies/rules.json" | Path to rule definitions |
| conflictResolution | ConflictResolutionStrategy | Yes | PRIORITY_WINS | How to resolve rule conflicts |
| defaultAutonomy | AutonomyLevel | Yes | SUPERVISED | Default for new rules |
| maxRules | int | No | 1000 | Maximum active rules |

### MemoryConfig
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| volatileCapacity | int | Yes | 10000 | Max volatile entries |
| persistentPath | string | Yes | ".agentx/memory" | Persistent storage directory |
| consolidationInterval | Duration | Yes | 5min | Volatile→persistent trigger |
| embeddingModel | string | Yes | "nomic-embed-text" | Embedding model for semantic search |
| maxPersistentEntries | int | No | 100000 | Cap for persistent memory |

### GoalConfig
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| maxActiveGoals | int | Yes | 10 | Concurrent active goals |
| defaultPriority | int | Yes | 50 | Base priority (0-100) |
| autoDecompose | bool | Yes | true | Auto-decompose composite goals |
| maxDepth | int | Yes | 5 | Max decomposition depth |

### ReflectionConfig
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| enabled | bool | Yes | true | Enable reflection engine |
| interval | Duration | Yes | 10min | Periodic reflection interval |
| promptTemplate | string | Yes | built-in | Jinja2 template for prompts |
| aiServiceId | string | Yes | "default" | AIService identifier |
| minConfidence | float | Yes | 0.7 | Threshold for auto-applying proposals |

---

## Core Domain Objects

### SessionConfig
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| agentId | AgentId | Yes | Links to agent |
| sessionId | string | Yes | UUID, session identifier |
| agentConfig | AgentConfig | Yes | Full agent config snapshot |
| workingDirectory | string | Yes | Session working directory |
| createdAt | DateTime | Yes | Session creation time |
| updatedAt | DateTime | Yes | Last activity time |
| version | int | Yes | Schema version for migration |

### AgentConfig (persisted subset)
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | AgentId | Yes | |
| name | string | Yes | |
| version | int | Yes | |
| autonomyLevel | AutonomyLevel | Yes | |
| sensors | SensorConfig[] | Yes | |
| actuators | ActuatorConfig[] | Yes | |
| policyConfig | PolicyConfig | Yes | |
| memoryConfig | MemoryConfig | Yes | |
| goalConfig | GoalConfig | Yes | |
| reflectionConfig | ReflectionConfig | Yes | |

---

## Runtime Objects

### SensorReading
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| sensorId | SensorId | Yes | Source sensor |
| data | JsonObject | Yes | Sensor-specific payload |
| timestamp | DateTime | Yes | When reading was taken |
| confidence | float | Yes | 0.0-1.0 reliability |

### ActuatorCommand
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| actuatorId | ActuatorId | Yes | Target actuator |
| action | string | Yes | Action name (e.g., "write_file", "query_rag") |
| parameters | JsonObject | Yes | Action parameters |
| expectedOutcome | string | No | Human-readable expectation |
| correlationId | string | Yes | Links to decision trace |

### ActuatorResult
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| success | bool | Yes | Whether action succeeded |
| output | JsonObject | No | Actuator-specific output |
| sideEffects | EnvironmentChange[] | Yes | Observed environment changes |
| error | string | No | Error message if failed |
| durationMs | int | Yes | Execution time |

### EnvironmentChange
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| type | ChangeType | Yes | CREATE, UPDATE, DELETE, APPEND |
| target | string | Yes | Resource identifier (path, key, etc.) |
| newValue | JsonValue | No | New state after change |
| timestamp | DateTime | Yes | When change occurred |

### EnvironmentModel
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| timestamp | DateTime | Yes | Model freshness |
| sensorReadings | Map<SensorId, SensorReading> | Yes | Latest readings |
| derivedFacts | Fact[] | Yes | Inferred facts from readings |
| confidence | float | Yes | Overall model confidence |

### Fact
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| key | string | Yes | Fact identifier |
| value | JsonValue | Yes | Fact value |
| source | SensorId | Yes | Origin sensor |
| validity | TimeRange | Yes | Validity window |

### TimeRange
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| start | DateTime | Yes | Inclusive start |
| end | DateTime | Yes | Inclusive end (or null = indefinite) |

---

## Memory System

### MemoryEntry
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | MemoryId | Yes | Unique identifier |
| content | JsonObject | Yes | Stored content |
| metadata | MemoryMetadata | Yes | Provenance & indexing |
| embedding | Vector | No | Semantic embedding (persistent tier) |
| tier | MemoryTier | Yes | VOLATILE, PERSISTENT, ARCHIVED |

### MemoryMetadata
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| createdAt | DateTime | Yes | Entry creation |
| accessCount | int | Yes | Retrieval count |
| lastAccessed | DateTime | Yes | Last retrieval |
| importance | float | Yes | 0.0-1.0 priority |
| tags | string[] | No | User/agent tags |
| source | MemorySource | Yes | PERCEPTION, ACTION_RESULT, REFLECTION, USER_INPUT, GOAL_PROGRESS |

### MemoryTier (enum)
- VOLATILE — Working context, recent events, sensor cache
- PERSISTENT — Consolidated, semantically indexed, survives sessions
- ARCHIVED — Cold storage, compressed, infrequent access

### MemorySource (enum)
- PERCEPTION
- ACTION_RESULT
- REFLECTION
- USER_INPUT
- GOAL_PROGRESS

### MemoryQuery
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| text | string | No | Semantic search query |
| timeRange | TimeRange | No | Temporal filter |
| tags | string[] | No | Tag filter |
| source | MemorySource | No | Source filter |
| minImportance | float | No | Importance threshold |
| limit | int | Yes | Max results (default 10) |

### EvictionCriteria
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| maxAge | Duration | No | Max age for volatile entries |
| minImportance | float | No | Minimum importance to keep |
| maxEntries | int | No | Hard capacity limit |
| tags | string[] | No | Tag-based eviction |

---

## Policy Engine

### PolicyRule
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | RuleId | Yes | Unique rule identifier |
| condition | ConditionExpr | Yes | When rule applies |
| action | PolicyAction | Yes | What to do |
| priority | int | Yes | Higher = wins conflicts (0-1000) |
| enabled | bool | Yes | Can be toggled |
| metadata | RuleMetadata | Yes | Provenance |

### ConditionExpr
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| expression | string | Yes | DSL expression (e.g., "goal.active AND env.has_file('*.py')") |
| evaluate(ctx: PolicyContext) | bool | — | Runtime evaluation |

### PolicyAction
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| type | ActionType | Yes | EXECUTE_TOOL, SET_GOAL, MODIFY_MEMORY, UPDATE_POLICY, REQUEST_CONFIRMATION, PAUSE |
| parameters | JsonObject | Yes | Action-specific parameters |
| targetGoal | GoalId | No | Goal this action serves |

### ActionType (enum)
- EXECUTE_TOOL
- SET_GOAL
- MODIFY_MEMORY
- UPDATE_POLICY
- REQUEST_CONFIRMATION
- PAUSE

### PolicyContext
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| environment | EnvironmentModel | Yes | Current world model |
| memory | MemorySnapshot | Yes | Relevant memory slice |
| currentGoal | Goal | No | Active goal |
| agentState | AgentState | Yes | Current agent state |

### PolicyDecision
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| selectedAction | PolicyAction | Yes | Chosen action |
| confidence | float | Yes | 0.0-1.0 decision confidence |
| reasoning | string | Yes | Human-readable rationale |
| alternatives | PolicyAction[] | No | Other considered actions |

### RuleMetadata
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| source | RuleSource | Yes | USER_DEFINED, REFLECTION_PROPOSED, DEFAULT, LEARNED |
| createdAt | DateTime | Yes | Rule creation time |
| createdBy | string | Yes | "user" or "reflection:<id>" |
| version | int | Yes | Rule version |

### RuleSource (enum)
- USER_DEFINED
- REFLECTION_PROPOSED
- DEFAULT
- LEARNED

---

## Goal Management

### Goal
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | GoalId | Yes | Unique identifier |
| description | string | Yes | Human-readable goal |
| type | GoalType | Yes | USER_OBJECTIVE, AGENT_SUBGOAL, MAINTENANCE, EXPLORATION |
| parent | GoalId | No | Parent goal (for decomposition) |
| children | GoalId[] | No | Sub-goals |
| status | GoalStatus | Yes | Current state |
| priority | int | Yes | 0-100, higher = more important |
| preconditions | Precondition[] | No | Must be true to activate |
| successCriteria | SuccessCriteria | Yes | How to know it's done |
| createdAt | DateTime | Yes | |
| updatedAt | DateTime | Yes | |

### GoalType (enum)
- USER_OBJECTIVE
- AGENT_SUBGOAL
- MAINTENANCE
- EXPLORATION

### GoalStatus (enum)
- PENDING
- ACTIVE
- BLOCKED
- COMPLETED
- FAILED
- ABANDONED

### Precondition
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| check(ctx: PolicyContext) | bool | — | Runtime evaluation |

### SuccessCriteria
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| evaluate(result: ActuatorResult, ctx: PolicyContext) | bool | — | Runtime evaluation |

### GoalOutcome (enum)
- SUCCESS
- PARTIAL
- FAILED
- SUPERSEDED

### GoalTree
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| root | GoalId | Yes | Top-level goal |
| nodes | Map<GoalId, Goal> | Yes | All goals by ID |
| getPath(goalId) | GoalId[] | — | Path from root |
| getDescendants(goalId) | GoalId[] | — | All sub-goals |

---

## Reflection Engine

### DecisionTrace
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| agentId | AgentId | Yes | |
| timestamp | DateTime | Yes | When cycle occurred |
| perception | EnvironmentModel | Yes | What was sensed |
| decision | PolicyDecision | Yes | What was decided |
| action | ActuatorCommand | Yes | What was done |
| result | ActuatorResult | Yes | What happened |
| goalContext | Goal | No | Active goal at time |

### ReflectionEntry
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | ReflectionId | Yes | |
| trace | DecisionTrace | Yes | Full context |
| critique | Critique | Yes | AI-generated analysis |
| proposals | Proposal[] | Yes | Actionable suggestions |
| createdAt | DateTime | Yes | |

### Critique
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| summary | string | Yes | One-paragraph assessment |
| strengths | string[] | Yes | What went well |
| weaknesses | string[] | Yes | What could improve |
| confidence | float | Yes | 0.0-1.0 |

### Proposal
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| type | ProposalType | Yes | POLICY_CHANGE, MEMORY_UPDATE, GOAL_ADJUSTMENT, TOOL_CONFIGURATION |
| content | JsonObject | Yes | Type-specific payload |
| rationale | string | Yes | Why this proposal |

### ProposalType (enum)
- POLICY_CHANGE — New/modified PolicyRule
- MEMORY_UPDATE — New MemoryEntry or importance adjustment
- GOAL_ADJUSTMENT — Goal priority/status change
- TOOL_CONFIGURATION — Sensor/actuator parameter change

### ReflectionPromptTemplate
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| template | string | Yes | Jinja2 template with trace variables |
| render(trace: DecisionTrace) | string | — | Produces prompt for AIService |

---

## Persistence

### SessionSnapshot
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| agentId | AgentId | Yes | |
| config | AgentConfig | Yes | Full config |
| volatileMemory | WorkingContext | Yes | Volatile state |
| policyStore | PolicyRule[] | Yes | All active rules |
| goalTree | GoalTree | Yes | Full goal hierarchy |
| reflectionLogPosition | int | Yes | Offset in reflection log |
| timestamp | DateTime | Yes | Snapshot time |
| version | int | Yes | Schema version |

### WorkingContext
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| currentGoal | GoalId | No | Active goal |
| activeSubGoals | GoalId[] | No | Sub-goals in progress |
| relevantFacts | Fact[] | No | Cached environment facts |
| recentDecisions | DecisionTrace[] | No | Last N decisions |
| focusEntities | EntityId[] | No | Entities in focus |

### SessionMetadata
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| agentId | AgentId | Yes | |
| createdAt | DateTime | Yes | |
| updatedAt | DateTime | Yes | |
| version | int | Yes | Schema version |

---

## Tool Schemas

### SensorSchema
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| sensorId | SensorId | Yes | |
| description | string | Yes | Human-readable purpose |
| outputSchema | JsonSchema | Yes | Expected reading structure |
| samplingRate | Duration | No | Polling interval |

### ActuatorSchema
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| actuatorId | ActuatorId | Yes | |
| description | string | Yes | Human-readable purpose |
| inputSchema | JsonSchema | Yes | Command parameters |
| outputSchema | JsonSchema | Yes | Result structure |

### ValidationResult
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| valid | bool | Yes | |
| errors | string[] | No | Blocking errors |
| warnings | string[] | No | Non-blocking issues |

### JsonSchema
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| type | string | Yes | JSON Schema type |
| properties | Map<string, JsonSchema> | No | Object properties |
| required | string[] | No | Required fields |

---

## Vector / Embedding Types

### Vector
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| dimensions | float[] | Yes | Embedding values |
| dimension | int | Yes | Vector size |

### ModelInfo
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | Model identifier |
| version | string | Yes | Model version |
| maxTokens | int | Yes | Context window |
| supportsStreaming | bool | Yes | Streaming capability |

---

## Events (Volatile Memory Circular Buffer)

### Event
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | Yes | UUID |
| type | EventType | Yes | Event category |
| timestamp | DateTime | Yes | |
| payload | JsonObject | Yes | Event data |
| correlationId | string | Yes | Links related events |

### EventType (enum)
- PERCEPTION
- ACTION
- REFLECTION
- GOAL_CHANGE
- POLICY_CHANGE
- ERROR

---

## Enumerations Summary

| Enum | Values |
|------|--------|
| AgentState | INITIALIZING, PERCEIVING, DECIDING, ACTING, REFLECTING, PERSISTING, PAUSED, TERMINATED |
| AutonomyLevel | FULLY_AUTONOMOUS, SUPERVISED, CONFIRMATION_REQUIRED, MANUAL_ONLY |
| MemoryTier | VOLATILE, PERSISTENT, ARCHIVED |
| MemorySource | PERCEPTION, ACTION_RESULT, REFLECTION, USER_INPUT, GOAL_PROGRESS |
| ConflictResolutionStrategy | PRIORITY_WINS, MOST_RECENT, USER_PROMPT, DENY_ALL |
| RuleSource | USER_DEFINED, REFLECTION_PROPOSED, DEFAULT, LEARNED |
| ActionType | EXECUTE_TOOL, SET_GOAL, MODIFY_MEMORY, UPDATE_POLICY, REQUEST_CONFIRMATION, PAUSE |
| GoalType | USER_OBJECTIVE, AGENT_SUBGOAL, MAINTENANCE, EXPLORATION |
| GoalStatus | PENDING, ACTIVE, BLOCKED, COMPLETED, FAILED, ABANDONED |
| GoalOutcome | SUCCESS, PARTIAL, FAILED, SUPERSEDED |
| ProposalType | POLICY_CHANGE, MEMORY_UPDATE, GOAL_ADJUSTMENT, TOOL_CONFIGURATION |
| ChangeType | CREATE, UPDATE, DELETE, APPEND |
| EventType | PERCEPTION, ACTION, REFLECTION, GOAL_CHANGE, POLICY_CHANGE, ERROR |

---

## Traceability to Class Diagram (A2)

| Data Dictionary Entity | Class Diagram Class |
|------------------------|---------------------|
| AgentConfig | AgentConfig |
| SensorConfig / ActuatorConfig | SensorConfig / ActuatorConfig (Config section) |
| SensorReading | SensorReading (Perception section) |
| ActuatorCommand / ActuatorResult | ActuatorCommand / ActuatorResult (Tools section) |
| EnvironmentModel / Fact | EnvironmentModel / Fact (Perception section) |
| MemoryEntry / MemoryMetadata / MemoryTier | MemoryEntry / MemoryMetadata / MemoryTier (Memory section) |
| PolicyRule / PolicyAction / PolicyDecision | PolicyRule / PolicyAction / PolicyDecision (Policy section) |
| Goal / GoalTree / GoalStatus | Goal / GoalTree / GoalStatus (Goal section) |
| DecisionTrace / ReflectionEntry / Critique / Proposal | DecisionTrace / ReflectionEntry / Critique / Proposal (Reflection section) |
| SessionSnapshot / WorkingContext | SessionSnapshot / WorkingContext (Persistence section) |
| SensorSchema / ActuatorSchema | SensorSchema / ActuatorSchema (Tools section) |
| Vector / ModelInfo | Vector / ModelInfo (Memory/Reflection sections) |
| Event / EventType | Event / EventType (Memory section) |

---

## Notes

- All IDs use UUID v4 for global uniqueness
- JsonObject = arbitrary JSON-serializable dict
- JsonValue = any JSON value (string, number, bool, array, object, null)
- Duration = ISO 8601 duration string (e.g., "PT5M", "PT1H")
- DateTime = ISO 8601 UTC timestamp (e.g., "2026-06-28T15:30:00Z")
- Schema versioning: all persisted objects carry `version` for migration
- Embedding dimension determined by `MemoryConfig.embeddingModel`