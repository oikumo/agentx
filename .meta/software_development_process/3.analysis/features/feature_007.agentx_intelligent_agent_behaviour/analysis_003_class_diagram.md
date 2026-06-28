# Analysis 003: Class Diagram — feature_007.agentx_intelligent_agent_behaviour

> **Phase:** Analysis | **Artifact:** analysis_003_class_diagram.md
> **Feature:** feature_007.agentx_intelligent_agent_behaviour | **Task:** A2

---

## Core Class Diagram — Overview (Mermaid)

High-level view showing the Agent facade and its 7 core subsystems.

```mermaid
classDiagram
    %% Core Agent
    class Agent {
        +id: AgentId
        +config: AgentConfig
        +state: AgentState
        +memory: MemoryManager
        +policyEngine: PolicyEngine
        +goalManager: GoalManager
        +reflectionEngine: ReflectionEngine
        +toolRegistry: ToolRegistry
        +environmentModel: EnvironmentModel
        +perceive() : EnvironmentModel
        +decide() : ActuatorCommand
        +act(command: ActuatorCommand) : ActuatorResult
        +reflect() : ReflectionEntry
        +persist() : SessionSnapshot
        +resume(snapshot: SessionSnapshot) : void
    }

    class AgentConfig {
        +id: AgentId
        +name: string
        +version: int
        +autonomyLevel: AutonomyLevel
    }

    class AgentState {
        <<enumeration>>
        INITIALIZING
        PERCEIVING
        DECIDING
        ACTING
        REFLECTING
        PERSISTING
        PAUSED
        TERMINATED
    }

    class AutonomyLevel {
        <<enumeration>>
        FULLY_AUTONOMOUS
        SUPERVISED
        CONFIRMATION_REQUIRED
        MANUAL_ONLY
    }

    class AgentId { +value: string }

    %% Subsystems (shown as single classes; details in separate diagrams)
    class MemoryManager
    class PolicyEngine
    class GoalManager
    class ReflectionEngine
    class ToolRegistry
    class EnvironmentModel
    class PersistenceManager

    %% Agent orchestrates all subsystems
    Agent *-- AgentConfig
    Agent *-- MemoryManager
    Agent *-- PolicyEngine
    Agent *-- GoalManager
    Agent *-- ReflectionEngine
    Agent *-- ToolRegistry
    Agent *-- EnvironmentModel
    Agent *-- PersistenceManager

    AgentConfig *-- AgentId
```

---

## 1. Configuration & Identity (Mermaid)

```mermaid
classDiagram
    %% Configuration & Identity
    class AgentConfig {
        +id: AgentId
        +name: string
        +version: int
        +sensors: SensorConfig[]
        +actuators: ActuatorConfig[]
        +policyConfig: PolicyConfig
        +memoryConfig: MemoryConfig
        +goalConfig: GoalConfig
        +reflectionConfig: ReflectionConfig
        +autonomyLevel: AutonomyLevel
        +createdAt: DateTime
        +updatedAt: DateTime
    }

    class SensorConfig {
        +id: SensorId
        +type: string
        +enabled: bool
        +parameters: JsonObject
    }

    class ActuatorConfig {
        +id: ActuatorId
        +type: string
        +enabled: bool
        +parameters: JsonObject
    }

    class PolicyConfig {
        +rulesFile: string
        +conflictResolution: ConflictResolutionStrategy
        +defaultAutonomy: AutonomyLevel
    }

    class MemoryConfig {
        +volatileCapacity: int
        +persistentPath: string
        +consolidationInterval: Duration
        +embeddingModel: string
    }

    class GoalConfig {
        +maxActiveGoals: int
        +defaultPriority: int
        +autoDecompose: bool
    }

    class ReflectionConfig {
        +enabled: bool
        +interval: Duration
        +promptTemplate: string
        +aiServiceId: string
    }

    class ConflictResolutionStrategy {
        <<enumeration>>
        PRIORITY_WINS
        MOST_RECENT
        USER_PROMPT
        DENY_ALL
    }

    class AgentId { +value: string }
    class SensorId { +value: string }
    class ActuatorId { +value: string }
    class RuleId { +value: string }
    class GoalId { +value: string }
    class MemoryId { +value: string }
    class ReflectionId { +value: string }

    class AgentState {
        <<enumeration>>
        INITIALIZING
        PERCEIVING
        DECIDING
        ACTING
        REFLECTING
        PERSISTING
        PAUSED
        TERMINATED
    }

    class AutonomyLevel {
        <<enumeration>>
        FULLY_AUTONOMOUS
        SUPERVISED
        CONFIRMATION_REQUIRED
        MANUAL_ONLY
    }

    AgentConfig *-- SensorConfig
    AgentConfig *-- ActuatorConfig
    AgentConfig *-- PolicyConfig
    AgentConfig *-- MemoryConfig
    AgentConfig *-- GoalConfig
    AgentConfig *-- ReflectionConfig
```

---

## 2. Perception & Environment Model (Mermaid)

```mermaid
classDiagram
    %% Perception & Environment Model
    class EnvironmentModel {
        +timestamp: DateTime
        +sensorReadings: Map
        +derivedFacts: Fact[]
        +confidence: float
        +update(reading: SensorReading) : void
        +getFact(key: string) : Fact
    }

    class SensorReading {
        +sensorId: SensorId
        +data: JsonObject
        +timestamp: DateTime
        +confidence: float
    }

    class Fact {
        +key: string
        +value: JsonValue
        +source: SensorId
        +validity: TimeRange
    }

    class TimeRange {
        +start: DateTime
        +end: DateTime
    }

    EnvironmentModel *-- SensorReading
    EnvironmentModel *-- Fact
    Fact *-- TimeRange
```

---

## 3. Tools & Tool Registry (Mermaid)

```mermaid
classDiagram
    %% Tool Registry & Interfaces
    class ToolRegistry {
        +sensors: Map
        +actuators: Map
        +registerSensor(sensor: ISensor) : void
        +registerActuator(actuator: IActuator) : void
        +getSensor(id: SensorId) : ISensor
        +getActuator(id: ActuatorId) : IActuator
        +listSensors() : SensorId[]
        +listActuators() : ActuatorId[]
    }

    class ISensor {
        <<interface>>
        +id: SensorId
        +sense() : SensorReading
        +getSchema() : SensorSchema
    }

    class IActuator {
        <<interface>>
        +id: ActuatorId
        +act(command: ActuatorCommand) : ActuatorResult
        +getSchema() : ActuatorSchema
        +validate(command: ActuatorCommand) : ValidationResult
    }

    ToolRegistry *-- ISensor
    ToolRegistry *-- IActuator

    %% Tool Schemas
    class SensorSchema {
        +sensorId: SensorId
        +description: string
        +outputSchema: JsonSchema
        +samplingRate: Duration
    }

    class ActuatorSchema {
        +actuatorId: ActuatorId
        +description: string
        +inputSchema: JsonSchema
        +outputSchema: JsonSchema
    }

    class ValidationResult {
        +valid: bool
        +errors: string[]
        +warnings: string[]
    }

    class JsonSchema {
        +type: string
        +properties: Map
        +required: string[]
    }

    class ActuatorCommand {
        +actuatorId: ActuatorId
        +action: string
        +parameters: JsonObject
        +expectedOutcome: string
    }

    class ActuatorResult {
        +success: bool
        +output: JsonObject
        +sideEffects: EnvironmentChange[]
        +error: string
    }

    class EnvironmentChange {
        +type: ChangeType
        +target: string
        +newValue: JsonValue
        +timestamp: DateTime
    }

    class ChangeType {
        <<enumeration>>
        CREATE
        UPDATE
        DELETE
        APPEND
    }

    ISensor *-- SensorSchema
    IActuator *-- ActuatorSchema
    IActuator *-- ValidationResult
    ActuatorCommand *-- ActuatorResult
    ActuatorResult *-- EnvironmentChange

    %% Built-in Tools
    class FileSystemTool {
        +id = "filesystem"
        +sense() : SensorReading
        +act(command: ActuatorCommand) : ActuatorResult
    }

    class RagSensorTool {
        +id = "rag_query"
        +sense() : SensorReading
    }

    class SessionTool {
        +id = "session"
        +sense() : SensorReading
        +act(command: ActuatorCommand) : ActuatorResult
    }

    FileSystemTool ..|> ISensor
    FileSystemTool ..|> IActuator
    RagSensorTool ..|> ISensor
    SessionTool ..|> ISensor
    SessionTool ..|> IActuator
```

---

## 4. Memory System (Mermaid)

```mermaid
classDiagram
    %% Memory System
    class MemoryManager {
        +volatile: VolatileMemory
        +persistent: PersistentMemory
        +store(entry: MemoryEntry, tier: MemoryTier) : void
        +retrieve(query: MemoryQuery) : MemoryEntry[]
        +consolidate() : void
        +evict(criteria: EvictionCriteria) : int
    }

    class MemoryQuery {
        +text: string
        +timeRange: TimeRange
        +tags: string[]
        +source: MemorySource
        +minImportance: float
        +limit: int
    }

    class EvictionCriteria {
        +maxAge: Duration
        +minImportance: float
        +maxEntries: int
        +tags: string[]
    }

    class TimeRange {
        +start: DateTime
        +end: DateTime
    }

    class VolatileMemory {
        +workingContext: WorkingContext
        +recentEvents: CircularBuffer
        +sensorCache: Map
        +capacity: int
        +put(key: string, value: JsonValue) : void
        +get(key: string) : JsonValue
    }

    class CircularBuffer {
        +capacity: int
        +size: int
        +push(item) : void
        +pop() : void
        +peek() : void
        +clear() : void
    }

    class Event {
        +id: string
        +type: EventType
        +timestamp: DateTime
        +payload: JsonObject
        +correlationId: string
    }

    class EventType {
        <<enumeration>>
        PERCEPTION
        ACTION
        REFLECTION
        GOAL_CHANGE
        POLICY_CHANGE
        ERROR
    }

    class PersistentMemory {
        +store: MemoryStore
        +semanticIndex: VectorIndex
        +episodicLog: EpisodicLog
        +semanticSearch(query: string, k: int) : MemoryEntry[]
        +episodicQuery(timeRange: TimeRange) : MemoryEntry[]
    }

    class MemoryStore {
        +save(entry: MemoryEntry) : void
        +load(id: MemoryId) : MemoryEntry
        +delete(id: MemoryId) : void
        +find(query: MemoryQuery) : MemoryEntry[]
    }

    class VectorIndex {
        +add(id: MemoryId, embedding: Vector) : void
        +search(vector: Vector, k: int) : MemoryId[]
        +remove(id: MemoryId) : void
    }

    class EpisodicLog {
        +append(entry: MemoryEntry) : void
        +query(timeRange: TimeRange) : MemoryEntry[]
        +getLatest(limit: int) : MemoryEntry[]
    }

    class MemoryEntry {
        +id: MemoryId
        +content: JsonObject
        +metadata: MemoryMetadata
        +embedding: Vector
        +tier: MemoryTier
    }

    class MemoryId { +value: string }
    class ReflectionId { +value: string }

    class Vector {
        +dimensions: float[]
        +dimension: int
    }

    class MemoryMetadata {
        +createdAt: DateTime
        +accessCount: int
        +lastAccessed: DateTime
        +importance: float
        +tags: string[]
        +source: MemorySource
    }

    class WorkingContext {
        +currentGoal: GoalId
        +activeSubGoals: GoalId[]
        +relevantFacts: Fact[]
        +recentDecisions: DecisionTrace[]
        +focusEntities: EntityId[]
    }

    class MemoryTier {
        <<enumeration>>
        VOLATILE
        PERSISTENT
        ARCHIVED
    }

    class MemorySource {
        <<enumeration>>
        PERCEPTION
        ACTION_RESULT
        REFLECTION
        USER_INPUT
        GOAL_PROGRESS
    }

    MemoryManager *-- VolatileMemory
    MemoryManager *-- PersistentMemory
    VolatileMemory *-- WorkingContext
    VolatileMemory *-- CircularBuffer
    CircularBuffer *-- Event
    PersistentMemory *-- MemoryStore
    PersistentMemory *-- VectorIndex
    PersistentMemory *-- EpisodicLog
    MemoryStore *-- MemoryEntry
    VectorIndex *-- MemoryEntry
    EpisodicLog *-- MemoryEntry
    MemoryEntry *-- MemoryMetadata
    MemoryEntry *-- Vector
```

---

## 5. Policy Engine (Mermaid)

```mermaid
classDiagram
    %% Policy Engine
    class PolicyEngine {
        +rules: PolicyRule[]
        +evaluate(context: PolicyContext) : PolicyDecision
        +addRule(rule: PolicyRule) : void
        +removeRule(ruleId: RuleId) : void
        +updateRule(rule: PolicyRule) : void
        +resolveConflicts() : void
    }

    class PolicyRule {
        +id: RuleId
        +condition: ConditionExpr
        +action: PolicyAction
        +priority: int
        +enabled: bool
        +metadata: RuleMetadata
    }

    class ConditionExpr {
        +expression: string
        +evaluate(context: PolicyContext) : bool
    }

    class PolicyAction {
        +type: ActionType
        +parameters: JsonObject
        +targetGoal: GoalId
    }

    class ActionType {
        <<enumeration>>
        EXECUTE_TOOL
        SET_GOAL
        MODIFY_MEMORY
        UPDATE_POLICY
        REQUEST_CONFIRMATION
        PAUSE
    }

    class PolicyContext {
        +environment: EnvironmentModel
        +memory: MemorySnapshot
        +currentGoal: Goal
        +agentState: AgentState
    }

    class PolicyDecision {
        +selectedAction: PolicyAction
        +confidence: float
        +reasoning: string
        +alternatives: PolicyAction[]
    }

    class RuleMetadata {
        +source: RuleSource
        +createdAt: DateTime
        +createdBy: string
        +version: int
    }

    class RuleSource {
        <<enumeration>>
        USER_DEFINED
        REFLECTION_PROPOSED
        DEFAULT
        LEARNED
    }

    class RuleId { +value: string }

    PolicyEngine *-- PolicyRule
    PolicyRule *-- ConditionExpr
    PolicyRule *-- PolicyAction
    PolicyRule *-- RuleMetadata
    PolicyEngine *-- PolicyContext
    PolicyEngine *-- PolicyDecision
```

---

## 6. Goal Management (Mermaid)

```mermaid
classDiagram
    %% Goal Management
    class GoalManager {
        +goalTree: GoalTree
        +activeGoal: Goal
        +selectGoal() : Goal
        +addGoal(goal: Goal) : void
        +decomposeGoal(goal: Goal) : Goal[]
        +updateProgress(goalId: GoalId, progress: float) : void
        +completeGoal(goalId: GoalId, outcome: GoalOutcome) : void
    }

    class Goal {
        +id: GoalId
        +description: string
        +type: GoalType
        +parent: GoalId
        +children: GoalId[]
        +status: GoalStatus
        +priority: int
        +preconditions: Precondition[]
        +successCriteria: SuccessCriteria
        +createdAt: DateTime
        +updatedAt: DateTime
    }

    class GoalTree {
        +root: GoalId
        +nodes: Map
        +getPath(goalId: GoalId) : GoalId[]
        +getDescendants(goalId: GoalId) : GoalId[]
    }

    class GoalType {
        <<enumeration>>
        USER_OBJECTIVE
        AGENT_SUBGOAL
        MAINTENANCE
        EXPLORATION
    }

    class GoalStatus {
        <<enumeration>>
        PENDING
        ACTIVE
        BLOCKED
        COMPLETED
        FAILED
        ABANDONED
    }

    class Precondition {
        +check(context: PolicyContext) : bool
    }

    class SuccessCriteria {
        +evaluate(result: ActuatorResult, context: PolicyContext) : bool
    }

    class GoalOutcome {
        <<enumeration>>
        SUCCESS
        PARTIAL
        FAILED
        SUPERSEDED
    }

    class GoalId { +value: string }

    GoalManager *-- GoalTree
    GoalTree *-- Goal
    Goal *-- Precondition
    Goal *-- SuccessCriteria
    Goal *-- GoalId : parent
    Goal *-- GoalId : children
```

---

## 7. Reflection Engine (Mermaid)

```mermaid
classDiagram
    %% Reflection Engine
    class IAIService {
        <<interface>>
        +complete(prompt: string) : string
        +completeStream(prompt: string) : AsyncIterator<string>
        +getModelInfo() : ModelInfo
    }

    class ModelInfo {
        +name: string
        +version: string
        +maxTokens: int
        +supportsStreaming: bool
    }

    class ReflectionEngine {
        +aiService: IAIService
        +promptTemplate: ReflectionPromptTemplate
        +reflect(trace: DecisionTrace) : ReflectionEntry
        +proposePolicyChanges(entry: ReflectionEntry) : PolicyRule[]
        +proposeMemoryUpdates(entry: ReflectionEntry) : MemoryEntry[]
    }

    class DecisionTrace {
        +agentId: AgentId
        +timestamp: DateTime
        +perception: EnvironmentModel
        +decision: PolicyDecision
        +action: ActuatorCommand
        +result: ActuatorResult
        +goalContext: Goal
    }

    class ReflectionEntry {
        +id: ReflectionId
        +trace: DecisionTrace
        +critique: Critique
        +proposals: Proposal[]
        +createdAt: DateTime
    }

    class Critique {
        +summary: string
        +strengths: string[]
        +weaknesses: string[]
        +confidence: float
    }

    class Proposal {
        +type: ProposalType
        +content: JsonObject
        +rationale: string
    }

    class ProposalType {
        <<enumeration>>
        POLICY_CHANGE
        MEMORY_UPDATE
        GOAL_ADJUSTMENT
        TOOL_CONFIGURATION
    }

    class ReflectionPromptTemplate {
        +template: string
        +render(trace: DecisionTrace) : string
    }

    class ReflectionId { +value: string }

    ReflectionEngine *-- IAIService
    ReflectionEngine *-- ReflectionPromptTemplate
    ReflectionEngine *-- DecisionTrace
    ReflectionEngine *-- ReflectionEntry
    IAIService *-- ModelInfo
    ReflectionEntry *-- Critique
    ReflectionEntry *-- Proposal
```

---

## 8. Persistence (Mermaid)

```mermaid
classDiagram
    %% Persistence
    class SessionSnapshot {
        +agentId: AgentId
        +config: AgentConfig
        +volatileMemory: WorkingContext
        +policyStore: PolicyRule[]
        +goalTree: GoalTree
        +reflectionLogPosition: int
        +timestamp: DateTime
        +version: int
    }

    class PersistenceManager {
        +save(snapshot: SessionSnapshot) : void
        +load(agentId: AgentId) : SessionSnapshot
        +listSessions() : SessionMetadata[]
        +delete(agentId: AgentId) : void
    }

    class SessionMetadata {
        +agentId: AgentId
        +createdAt: DateTime
        +updatedAt: DateTime
        +version: int
    }

    class AgentId { +value: string }
    class AgentConfig { +version: int }
    class WorkingContext
    class PolicyRule
    class GoalTree

    PersistenceManager *-- SessionSnapshot
    SessionSnapshot *-- AgentId
    SessionSnapshot *-- AgentConfig
    SessionSnapshot *-- WorkingContext
    SessionSnapshot *-- PolicyRule
    SessionSnapshot *-- GoalTree
    PersistenceManager *-- SessionMetadata
```

---

## Key Relationships Summary (Mermaid)

Cross-cutting relationships between the 8 subsystems.

```mermaid
classDiagram
    class Agent
    class MemoryManager
    class PolicyEngine
    class GoalManager
    class ReflectionEngine
    class ToolRegistry
    class EnvironmentModel
    class PersistenceManager
    class AgentConfig
    class AgentId
    class AgentState {
        <<enumeration>>
        INITIALIZING
        PERCEIVING
        DECIDING
        ACTING
        REFLECTING
        PERSISTING
        PAUSED
        TERMINATED
    }
    class AutonomyLevel {
        <<enumeration>>
        FULLY_AUTONOMOUS
        SUPERVISED
        CONFIRMATION_REQUIRED
        MANUAL_ONLY
    }

    Agent *-- AgentConfig
    Agent *-- AgentState
    Agent *-- MemoryManager
    Agent *-- PolicyEngine
    Agent *-- GoalManager
    Agent *-- ReflectionEngine
    Agent *-- ToolRegistry
    Agent *-- EnvironmentModel
    Agent *-- PersistenceManager

    AgentConfig *-- AgentId
    AgentConfig *-- AutonomyLevel

    PolicyEngine ..> GoalManager : uses Goal
    PolicyEngine ..> MemoryManager : uses MemorySnapshot
    PolicyEngine ..> EnvironmentModel : uses EnvironmentModel

    GoalManager ..> PolicyEngine : triggers PolicyAction.SET_GOAL
    GoalManager ..> MemoryManager : stores GoalProgress

    ReflectionEngine ..> PolicyEngine : proposes PolicyRule[]
    ReflectionEngine ..> MemoryManager : proposes MemoryEntry[]
    ReflectionEngine ..> GoalManager : proposes GoalAdjustment

    PersistenceManager ..> Agent : saves SessionSnapshot
    PersistenceManager ..> MemoryManager : persists MemoryEntry[]
    PersistenceManager ..> PolicyEngine : persists PolicyRule[]
    PersistenceManager ..> GoalManager : persists GoalTree

    ToolRegistry ..> EnvironmentModel : SensorReading feeds EnvironmentModel
    ToolRegistry ..> PolicyEngine : ActuatorCommand from PolicyAction
```

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Agent as Facade** | Single entry point orchestrating all subsystems; follows MVC++ Controller pattern |
| **Tool Registry with ISensor/IActuator** | Clear separation of perception vs. action; enables tool composition; testable via mocks |
| **Two-tier Memory** | Volatile for low-latency working context; Persistent for long-term knowledge; consolidation bridge |
| **Policy Engine as Rule Evaluator** | Declarative, inspectable, hot-reloadable; supports User-defined + Reflection-proposed rules |
| **Goal Tree with AND/OR Decomposition** | Hierarchical planning; supports User objectives → Agent sub-goals; tracks progress |
| **Reflection Engine using AIService** | Reuses existing AI infrastructure; LLM-based self-critique; produces actionable proposals |
| **Versioned Session Snapshots** | Atomic persistence; migration-friendly; supports resume + audit trail |

---

## Interface Contracts (for MVC++ Compliance)

### Abstract Partners (to be implemented in Design phase)

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
    def update_policy(self, agent_id: AgentId, rule: PolicyRule) -> void: ...
    @abstractmethod
    def set_autonomy(self, agent_id: AgentId, level: AutonomyLevel) -> void: ...
```

---

## Integration Points with Existing Codebase

| Feature | Integration Point | Approach |
|---------|------------------|----------|
| **feature_004 (Modern UI)** | `TUIProvider` → register `AgentAdapter` | New `AgentTUIScreen` implementing `IAgentView` |
| **feature_002 (RAG)** | `Rag` class → wrap as `RagSensorTool` | Implement `ISensor` using `Rag.query()` |
| **feature_001 (Session Objectives)** | `IGoalManager` interface | Stub implementation now; swap when 001 lands |
| **Session Persistence** | Extend `SessionDatabase` | Add Agent tables; reuse SQLite pattern |
| **AI Service** | Reuse `AIService` for Reflection | Existing streaming + provider abstraction |

---

## Traceability to Use Cases (A1)

| Class / Component | Primary Use Case(s) |
|-------------------|---------------------|
| Agent | All (orchestrator) |
| ToolRegistry, ISensor, IActuator | UC1, UC2 |
| EnvironmentModel, SensorReading | UC1 |
| MemoryManager, VolatileMemory, PersistentMemory | UC4 |
| PolicyEngine, PolicyRule | UC3, UC5 |
| GoalManager, Goal, GoalTree | UC5 |
| ReflectionEngine, ReflectionEntry | UC6 |
| PersistenceManager, SessionSnapshot | UC7, UC8 |
| FileSystemTool, RagSensorTool, SessionTool | UC1, UC2 (concrete tools) |

---

## Notes

- All interfaces marked `<<interface>>` follow MVC++ Abstract Partner pattern
- Concrete tools (FileSystemTool, etc.) implement both ISensor and IActuator where applicable
- PolicyEngine is stateless (rules passed in) → highly testable
- ReflectionEngine depends on `IAIService` abstraction (not concrete provider)
- AgentConfig versioning enables migration across schema changes