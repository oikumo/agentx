# Operation Spec: Agent Controller Operations

**Feature:** feature_007.agentx_intelligent_agent_behaviour
**Phase:** Design
**Date:** 2026-06-29
**Reference:** `design_001_agent_framework.md` §3.2, §5, §6, §7, §8, §11; `analysis_002_use_cases.md` (UC1–UC6); `analysis_004_sequence_diagrams.md` (SD1–SD8)

> Per `omt_agent_guide.md §10`, every public Controller operation that handles a user/agent
> operation carries an operation specification (Preconditions / Exceptions / Postconditions).
> These specifications are the contract the Implementation phase (I4) realizes as docstrings
> and the Testing phase (T1–T2) verifies. Operations are grouped by controller. Persistence
> uses stdlib `sqlite3` only (no ORM, no Alembic) per the design persistence strategy.

---

## 1. AgentController

### 1.1 start_session
```python
def start_session(self, config: AgentConfig) -> AgentId:
    """
    Operation: Initialize a new Agent from AgentConfig and enter the PERCEIVING state.

    Preconditions:
      - config.id is unique among live agents (not already active).
      - config.sensors / config.actuators reference tools available to the ToolRegistry.
      - config.memory_config.persistent_path is writable.

    Exceptions:
      - AgentConfigError: invalid config -> session not created, state stays CREATED.
      - ToolSchemaError: a referenced tool fails schema validation -> fail-fast, no agent.
      - sqlite3.OperationalError: persistence path unusable -> rolled back, no agent.

    Postconditions:
      - A new Agent exists in state INITIALIZING -> PERCEIVING.
      - Built-in tools registered (design §6.6) unless disabled in config.
      - SessionMetadata row written via SessionDatabase.
      - AgentId returned to caller.
    """
```

### 1.2 resume_session
```python
def resume_session(self, snapshot_id: str) -> Agent:
    """
    Operation: Rebuild an Agent from a persisted SessionSnapshot.

    Preconditions:
      - snapshot_id exists in TableSessionSnapshots.
      - Stored config_version is compatible with the running code.

    Exceptions:
      - SnapshotNotFoundError: snapshot_id absent -> no agent created.
      - SnapshotCorruptError: JSON payload unparseable -> no agent created.
      - IncompatibleVersionError: config_version mismatch -> agent not resumed.

    Postconditions:
      - Agent state restored to the snapshot's PERCEIVING/DECIDING state.
      - Volatile memory, policy store, goal tree, reflection log position restored.
      - Tools re-registered from config (SD: session resume).
    """
```

### 1.3 submit_goal
```python
def submit_goal(self, goal: Goal) -> GoalId:
    """
    Operation: Add a user objective to the GoalTree and notify the view.

    Preconditions:
      - Agent state is PERCEIVING, DECIDING, or ACTING (not TERMINATED).
      - goal.successCriteria is defined.

    Exceptions:
      - InvalidGoalError: missing required fields -> goal rejected, GoalId not issued.
      - AgentTerminatedError: agent state is TERMINATED -> goal rejected.

    Postconditions:
      - Goal inserted into GoalTree with status PENDING (or ACTIVE if no active goal).
      - IAgentViewPartner.refresh_goal_tree() invoked.
      - GoalId returned.
    """
```

### 1.4 run_cycle
```python
def run_cycle(self) -> CycleResult:
    """
    Operation: Execute one perceive -> decide -> act -> reflect cycle (UC1, UC2, UC6).

    Preconditions:
      - Agent state is PERCEIVING.
      - At least one PolicyRule is enabled, or NOOP is acceptable.

    Exceptions:
      - ToolExecutionError: an actuator raised -> ActuatorResult.success=False recorded,
        cycle continues (non-fatal; design §11.1).
      - ReflectionParseError: AI returned non-JSON -> low-confidence Critique with no
        proposals, cycle continues (non-fatal; design §8.3).

    Postconditions:
      - EnvironmentModel updated from sensors.
      - One PolicyDecision selected (priority resolution, design §7.3) and acted on.
      - DecisionTrace persisted; ReflectionEntry written if reflection ran.
      - Agent state returns to PERCEIVING (or PAUSED/TERMINATED on policy action).
    """
```

### 1.5 update_policy
```python
def update_policy(self, rule: PolicyRule) -> bool:
    """
    Operation: Add or replace a PolicyRule via the safe path (design §7.4, §11.3).

    Preconditions:
      - rule.condition compiles (no unknown identifiers/functions).
      - rule.priority in [0, 1000].

    Exceptions:
      - ConditionCompileError: rule.condition invalid -> rule rejected at load time.
      - (swallowed) conflict_score > 0.8 -> returns False, warning logged.

    Postconditions:
      - On True: rule stored, versioned in TablePolicyRules; conflicts re-evaluated.
      - On False: rule not stored; conflict/complexity reason logged.
      - Existing enabled ruleset otherwise unchanged.
    """
```

---

## 2. SessionController

### 2.1 save_snapshot
```python
def save_snapshot(self) -> str:
    """
    Operation: Persist the current Agent state as a SessionSnapshot.

    Preconditions:
      - Agent is initialized (has a valid AgentId).
      - SessionDatabase is reachable (sqlite3 connection OK).

    Exceptions:
      - sqlite3.Error (after retries, design §11.2): returns failure; last good snapshot
        retained.

    Postconditions:
      - A new row in TableSessionSnapshots with monotonically increasing timestamp.
      - Volatile memory, policy store, goal tree, reflection log position serialized.
      - Snapshot id returned.
    """
```

### 2.2 load_snapshot
```python
def load_snapshot(self, snapshot_id: str) -> SessionSnapshot:
    """
    Operation: Read a SessionSnapshot by id.

    Preconditions:
      - snapshot_id exists.

    Exceptions:
      - SnapshotNotFoundError: id absent -> raised.

    Postconditions:
      - Returns a SessionSnapshot dataclass; no agent state mutated.
    """
```

---

## 3. ToolController

### 3.1 register_tool
```python
def register_tool(self, tool: ISensor | IActuator) -> ToolSpec:
    """
    Operation: Register a sensor/actuator with the ToolRegistry (UC tool setup, SD8).

    Preconditions:
      - tool.id is non-empty and not already registered.
      - tool.get_schema() returns a structurally valid schema.

    Exceptions:
      - ToolSchemaError: schema invalid -> tool not registered (fail-fast, design §6.4).
      - DuplicateToolError: tool.id already registered -> rejected.

    Postconditions:
      - ToolSpec built and stored; tool discoverable via list_sensors/list_actuators.
      - get_spec(tool.id) returns the new spec.
    """
```

### 3.2 execute_action
```python
def execute_action(self, command: ActuatorCommand) -> ActuatorResult:
    """
    Operation: Validate and run an actuator command via the registry (UC2, SD2).

    Preconditions:
      - command.actuatorId is registered.
      - command.correlationId links to a DecisionTrace.

    Exceptions:
      - ToolExecutionError: actuator raised -> ActuatorResult(success=False, error=...).
      - (validation) ValidationResult.valid == False -> failure result, no side effects.

    Postconditions:
      - On success: ActuatorResult.sideEffects applied to EnvironmentModel.
      - Result recorded in DecisionTrace; durationMs measured.
    """
```

---

## 4. Traceability

| Operation | Use Case (analysis_002) | Sequence (analysis_004) | Design § |
|-----------|-------------------------|--------------------------|----------|
| start_session | init | SD8 (tool registration) | §3.2 |
| resume_session | session resume | session resume | §3.2, §5.2 |
| submit_goal | UC5 Pursue Goal | SD4 | §3.2 |
| run_cycle | UC1, UC2, UC6 | SD1, SD2 | §3.1, §7, §8 |
| update_policy | UC3 Update Policy | SD3 | §7, §11.3 |
| save_snapshot | UC4 Manage Memory | persistence | §5, §11.2 |
| register_tool | UC1, UC2 setup | SD8 | §6.4 |
| execute_action | UC2 Execute Action | SD2 | §6, §11.1 |
