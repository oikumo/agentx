"""Agent domain types — enums and dataclasses.

Realizes the data dictionary (analysis_006_data_dictionary.md) as stdlib
dataclasses and enums.  No ORM, no Pydantic — plain dataclasses so the agent
subsystem stays dependency-free (stdlib only), matching the existing
``SessionDatabase`` / ``Rag`` convention.

All identifiers are plain ``str`` (UUID v4 by convention) rather than wrapper
NewType aliases, to keep serialization to sqlite3/JSON frictionless.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Enumerations (analysis_006 §"Enumerations Summary")
# ---------------------------------------------------------------------------


class AgentState(str, Enum):
    INITIALIZING = "INITIALIZING"
    PERCEIVING = "PERCEIVING"
    DECIDING = "DECIDING"
    ACTING = "ACTING"
    REFLECTING = "REFLECTING"
    PERSISTING = "PERSISTING"
    PAUSED = "PAUSED"
    TERMINATED = "TERMINATED"


class AutonomyLevel(str, Enum):
    FULLY_AUTONOMOUS = "FULLY_AUTONOMOUS"
    SUPERVISED = "SUPERVISED"
    CONFIRMATION_REQUIRED = "CONFIRMATION_REQUIRED"
    MANUAL_ONLY = "MANUAL_ONLY"


class MemoryTier(str, Enum):
    VOLATILE = "VOLATILE"
    PERSISTENT = "PERSISTENT"
    ARCHIVED = "ARCHIVED"


class MemorySource(str, Enum):
    PERCEPTION = "PERCEPTION"
    ACTION_RESULT = "ACTION_RESULT"
    REFLECTION = "REFLECTION"
    USER_INPUT = "USER_INPUT"
    GOAL_PROGRESS = "GOAL_PROGRESS"


class ConflictResolutionStrategy(str, Enum):
    PRIORITY_WINS = "PRIORITY_WINS"
    MOST_RECENT = "MOST_RECENT"
    USER_PROMPT = "USER_PROMPT"
    DENY_ALL = "DENY_ALL"


class RuleSource(str, Enum):
    USER_DEFINED = "USER_DEFINED"
    REFLECTION_PROPOSED = "REFLECTION_PROPOSED"
    DEFAULT = "DEFAULT"
    LEARNED = "LEARNED"


class ActionType(str, Enum):
    EXECUTE_TOOL = "EXECUTE_TOOL"
    SET_GOAL = "SET_GOAL"
    MODIFY_MEMORY = "MODIFY_MEMORY"
    UPDATE_POLICY = "UPDATE_POLICY"
    REQUEST_CONFIRMATION = "REQUEST_CONFIRMATION"
    PAUSE = "PAUSE"


class GoalType(str, Enum):
    USER_OBJECTIVE = "USER_OBJECTIVE"
    AGENT_SUBGOAL = "AGENT_SUBGOAL"
    MAINTENANCE = "MAINTENANCE"
    EXPLORATION = "EXPLORATION"


class GoalStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ABANDONED = "ABANDONED"


class GoalOutcome(str, Enum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    SUPERSEDED = "SUPERSEDED"


class ProposalType(str, Enum):
    POLICY_CHANGE = "POLICY_CHANGE"
    MEMORY_UPDATE = "MEMORY_UPDATE"
    GOAL_ADJUSTMENT = "GOAL_ADJUSTMENT"
    TOOL_CONFIGURATION = "TOOL_CONFIGURATION"


class ProposalStatus(str, Enum):
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    NEEDS_CONFIRMATION = "NEEDS_CONFIRMATION"
    REJECTED = "REJECTED"
    APPLIED = "APPLIED"
    REVERTED = "REVERTED"


class ChangeType(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    APPEND = "APPEND"


class EventType(str, Enum):
    PERCEPTION = "PERCEPTION"
    ACTION = "ACTION"
    REFLECTION = "REFLECTION"
    GOAL_CHANGE = "GOAL_CHANGE"
    POLICY_CHANGE = "POLICY_CHANGE"
    ERROR = "ERROR"


class ToolKind(str, Enum):
    SENSOR = "sensor"
    ACTUATOR = "actuator"
    HYBRID = "hybrid"


# ---------------------------------------------------------------------------
# Configuration objects
# ---------------------------------------------------------------------------


@dataclass
class SensorConfig:
    id: str
    type: str
    enabled: bool = True
    parameters: dict[str, Any] = field(default_factory=dict)
    sampling_rate: float | None = None  # seconds; None = event-driven


@dataclass
class ActuatorConfig:
    id: str
    type: str
    enabled: bool = True
    parameters: dict[str, Any] = field(default_factory=dict)
    requires_confirmation: bool = False


@dataclass
class PolicyConfig:
    rules_file: str = "policies/rules.json"
    conflict_resolution: ConflictResolutionStrategy = ConflictResolutionStrategy.PRIORITY_WINS
    default_autonomy: AutonomyLevel = AutonomyLevel.SUPERVISED
    max_rules: int = 1000


@dataclass
class MemoryConfig:
    volatile_capacity: int = 10_000
    persistent_path: str = ".agentx/memory"
    consolidation_interval: float = 300.0  # seconds (5 min)
    embedding_model: str = "nomic-embed-text"
    max_persistent_entries: int = 100_000


@dataclass
class GoalConfig:
    max_active_goals: int = 10
    default_priority: int = 50
    auto_decompose: bool = True
    max_depth: int = 5


@dataclass
class ReflectionConfig:
    enabled: bool = True
    interval: float = 600.0  # seconds (10 min)
    prompt_template: str = "built-in"
    ai_service_id: str = "default"
    min_confidence: float = 0.7


@dataclass
class ToolConfig:
    auto_discover: bool = False


@dataclass
class AgentConfig:
    id: str
    name: str = "agentx-agent"
    version: int = 1
    sensors: list[SensorConfig] = field(default_factory=list)
    actuators: list[ActuatorConfig] = field(default_factory=list)
    policy_config: PolicyConfig = field(default_factory=PolicyConfig)
    memory_config: MemoryConfig = field(default_factory=MemoryConfig)
    goal_config: GoalConfig = field(default_factory=GoalConfig)
    reflection_config: ReflectionConfig = field(default_factory=ReflectionConfig)
    tool_config: ToolConfig = field(default_factory=ToolConfig)
    autonomy_level: AutonomyLevel = AutonomyLevel.SUPERVISED
    sandbox_root: str = "."
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# Perception / runtime objects
# ---------------------------------------------------------------------------


@dataclass
class TimeRange:
    start: datetime
    end: datetime | None = None  # None = indefinite


@dataclass
class Fact:
    key: str
    value: Any
    source: str  # SensorId
    validity: TimeRange | None = None


@dataclass
class SensorReading:
    sensor_id: str
    data: dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    confidence: float = 1.0


@dataclass
class EnvironmentChange:
    type: ChangeType
    target: str
    new_value: Any = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class EnvironmentModel:
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    sensor_readings: dict[str, SensorReading] = field(default_factory=dict)
    derived_facts: list[Fact] = field(default_factory=list)
    confidence: float = 1.0

    @property
    def memory_pressure(self) -> float:
        """Heuristic 0.0-1.0 pressure indicator used by policy conditions."""
        return 0.0


@dataclass
class ActuatorCommand:
    actuator_id: str
    action: str
    parameters: dict[str, Any] = field(default_factory=dict)
    expected_outcome: str | None = None
    correlation_id: str = ""


@dataclass
class ActuatorResult:
    success: bool
    output: dict[str, Any] = field(default_factory=dict)
    side_effects: list[EnvironmentChange] = field(default_factory=list)
    error: str | None = None
    duration_ms: int = 0


# ---------------------------------------------------------------------------
# Memory system
# ---------------------------------------------------------------------------


@dataclass
class MemoryMetadata:
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    access_count: int = 0
    last_accessed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    importance: float = 0.5
    tags: list[str] = field(default_factory=list)
    source: MemorySource = MemorySource.PERCEPTION


@dataclass
class MemoryEntry:
    id: str
    content: dict[str, Any]
    metadata: MemoryMetadata = field(default_factory=MemoryMetadata)
    embedding: list[float] | None = None
    tier: MemoryTier = MemoryTier.VOLATILE


@dataclass
class MemoryQuery:
    text: str | None = None
    time_range: TimeRange | None = None
    tags: list[str] | None = None
    source: MemorySource | None = None
    min_importance: float | None = None
    limit: int = 10


@dataclass
class EvictionCriteria:
    max_age: float | None = None  # seconds
    min_importance: float | None = None
    max_entries: int | None = None
    tags: list[str] | None = None


# ---------------------------------------------------------------------------
# Policy engine
# ---------------------------------------------------------------------------


@dataclass
class JsonSchema:
    type: str = "object"
    properties: dict[str, "JsonSchema"] = field(default_factory=dict)
    required: list[str] = field(default_factory=list)


@dataclass
class PolicyAction:
    type: ActionType
    parameters: dict[str, Any] = field(default_factory=dict)
    target_goal: str | None = None


@dataclass
class RuleMetadata:
    source: RuleSource = RuleSource.DEFAULT
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = "default"
    version: int = 1


@dataclass
class PolicyContext:
    environment: EnvironmentModel = field(default_factory=EnvironmentModel)
    memory: list[MemoryEntry] = field(default_factory=list)
    current_goal: "Goal | None" = None
    agent_state: AgentState = AgentState.PERCEIVING
    autonomy_level: AutonomyLevel = AutonomyLevel.SUPERVISED


@dataclass
class PolicyDecision:
    selected_action: PolicyAction
    confidence: float = 0.0
    reasoning: str = ""
    alternatives: list[PolicyAction] = field(default_factory=list)


@dataclass
class PolicyRule:
    id: str
    condition_expr: str  # DSL source text (compiled lazily by PolicyEngine)
    action: PolicyAction
    priority: int = 500  # 0-1000, higher wins
    enabled: bool = True
    metadata: RuleMetadata = field(default_factory=RuleMetadata)


# ---------------------------------------------------------------------------
# Goal management
# ---------------------------------------------------------------------------


@dataclass
class SuccessCriteria:
    """How to know a goal is done — a callable-free serializable form.

    ``kind`` selects the evaluation strategy:

    * ``"always"``  — always satisfied (used for maintenance goals)
    * ``"tool_success"`` — satisfied when the acting tool returns success
    * ``"expression"`` — a policy-DSL expression evaluated against the context
    """

    kind: str = "always"
    expression: str | None = None


@dataclass
class Goal:
    id: str
    description: str
    type: GoalType = GoalType.USER_OBJECTIVE
    parent: str | None = None
    children: list[str] = field(default_factory=list)
    status: GoalStatus = GoalStatus.PENDING
    priority: int = 50  # 0-100
    success_criteria: SuccessCriteria = field(default_factory=SuccessCriteria)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def active(self) -> bool:
        return self.status == GoalStatus.ACTIVE

    @property
    def is_blocked(self) -> bool:
        return self.status == GoalStatus.BLOCKED


@dataclass
class GoalTree:
    root: str | None = None
    nodes: dict[str, Goal] = field(default_factory=dict)

    def add(self, goal: Goal) -> None:
        self.nodes[goal.id] = goal
        if goal.parent and goal.parent in self.nodes:
            if goal.id not in self.nodes[goal.parent].children:
                self.nodes[goal.parent].children.append(goal.id)
        if self.root is None:
            self.root = goal.id

    def get(self, goal_id: str) -> Goal | None:
        return self.nodes.get(goal_id)

    def get_path(self, goal_id: str) -> list[str]:
        path: list[str] = []
        current: str | None = goal_id
        while current and current in self.nodes:
            path.append(current)
            current = self.nodes[current].parent
        return list(reversed(path))

    def get_descendants(self, goal_id: str) -> list[str]:
        result: list[str] = []
        node = self.nodes.get(goal_id)
        if not node:
            return result
        for child_id in node.children:
            result.append(child_id)
            result.extend(self.get_descendants(child_id))
        return result


# ---------------------------------------------------------------------------
# Reflection engine
# ---------------------------------------------------------------------------


@dataclass
class DecisionTrace:
    agent_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    perception: EnvironmentModel = field(default_factory=EnvironmentModel)
    decision: PolicyDecision | None = None
    action: ActuatorCommand | None = None
    result: ActuatorResult | None = None
    goal_context: Goal | None = None


@dataclass
class Critique:
    summary: str = ""
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class Proposal:
    type: ProposalType
    content: dict[str, Any] = field(default_factory=dict)
    rationale: str = ""
    status: ProposalStatus = ProposalStatus.PROPOSED


@dataclass
class ProposalVerdict:
    status: ProposalStatus
    reason: str = ""


@dataclass
class ProposalOutcome:
    status: ProposalStatus
    token: str | None = None  # rollback token
    reason: str | None = None


@dataclass
class ReflectionEntry:
    id: str
    trace: DecisionTrace
    critique: Critique = field(default_factory=Critique)
    proposals: list[Proposal] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# Persistence / session
# ---------------------------------------------------------------------------


@dataclass
class WorkingContext:
    current_goal: str | None = None
    active_sub_goals: list[str] = field(default_factory=list)
    relevant_facts: list[Fact] = field(default_factory=list)
    recent_decisions: list[DecisionTrace] = field(default_factory=list)
    focus_entities: list[str] = field(default_factory=list)


@dataclass
class SessionSnapshot:
    snapshot_id: str
    agent_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    config_version: int = 1
    volatility_data: dict[str, Any] = field(default_factory=dict)
    policy_store: list[dict[str, Any]] = field(default_factory=list)
    goal_tree: dict[str, Any] = field(default_factory=dict)
    reflection_log_position: int = 0


@dataclass
class SessionMetadata:
    agent_id: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = 1


@dataclass
class CycleResult:
    """Outcome of one perceive → decide → act → reflect cycle."""

    perception: EnvironmentModel
    decision: PolicyDecision
    action_result: ActuatorResult | None
    reflection: ReflectionEntry | None = None
