"""Agent — MVC++ Model facade orchestrating all agent subsystems (design §3.1).

The Agent is the single Model-layer entry point.  It wires together the tool
registry, memory, policy engine, goal manager, and reflection engine, and
exposes the perceive → decide → act → reflect → persist cycle.

Controllers depend on :class:`IAgentModelPartner`, not this concrete class.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from agentx.agent.interfaces import (
    IAIServicePartner,
    IAgentModelPartner,
    IPersistencePartner,
)
from agentx.agent.model.goal.manager import GoalManager
from agentx.agent.model.memory.manager import MemoryManager
from agentx.agent.model.policy.evaluator import PolicyEngine
from agentx.agent.model.reflection.engine import ReflectionEngine
from agentx.agent.model.reflection.proposal_router import ProposalRouter
from agentx.agent.model.reflection.safety_evaluator import DefaultSafetyEvaluator
from agentx.agent.model.tools.discovery import discover_tools
from agentx.agent.model.tools.filesystem_tool import FileSystemTool
from agentx.agent.model.tools.registry import ToolRegistry
from agentx.agent.model.tools.rag_sensor_tool import RagSensorTool
from agentx.agent.model.tools.session_tool import SessionTool
from agentx.agent.persistence.agent_db import SessionDatabase
from agentx.agent.persistence.repositories_db import (
    GoalRepository,
    MemoryRepository,
    PolicyRepository,
    ReflectionRepository,
)
from agentx.agent.types import (
    ActuatorCommand,
    ActuatorResult,
    AgentConfig,
    AgentState,
    AutonomyLevel,
    CycleResult,
    DecisionTrace,
    EnvironmentModel,
    Goal,
    GoalStatus,
    MemorySource,
    MemoryTier,
    PolicyAction,
    PolicyContext,
    PolicyDecision,
    PolicyRule,
    RuleMetadata,
    RuleSource,
    SensorReading,
    SessionSnapshot,
)

_log = logging.getLogger(__name__)


class Agent(IAgentModelPartner):
    """Facade orchestrating all agent subsystems."""

    def __init__(self, config: AgentConfig) -> None:
        self.id = config.id
        self.config = config
        self.state = AgentState.INITIALIZING

        # --- persistence (stdlib sqlite3) ---
        db_path = f"{config.memory_config.persistent_path}/agent_session.db"
        self._db = SessionDatabase(db_path)
        self._mem_repo = MemoryRepository(db_path)
        self._pol_repo = PolicyRepository(db_path)
        self._goal_repo = GoalRepository(db_path)
        self._refl_repo = ReflectionRepository(db_path)

        # --- subsystems ---
        self.tool_registry = ToolRegistry()
        self.memory = MemoryManager(
            volatile_capacity=config.memory_config.volatile_capacity,
            repository=self._mem_repo,
            agent_id=self.id,
        )
        self.policy_engine = PolicyEngine()
        self.goal_manager = GoalManager(
            config=config.goal_config,
            repository=self._goal_repo,
            agent_id=self.id,
        )

        # reflection wiring (AI service injected later)
        self._ai_service: IAIServicePartner | None = None
        self._safety = DefaultSafetyEvaluator()
        self._router = ProposalRouter(
            policy=self.policy_engine,
            memory=self.memory,
            goals=self.goal_manager,
            tools=self.tool_registry,
        )
        self.reflection_engine = ReflectionEngine(
            safety_evaluator=self._safety,
            router=self._router,
        )

        # --- environment model ---
        self.environment_model = EnvironmentModel()

        # --- register built-in tools ---
        self._register_builtin_tools(config)

        # --- transition to PERCEIVING ---
        self.state = AgentState.PERCEIVING

    # ============================================================ IAgentModelPartner

    def start_session(self, config: AgentConfig) -> str:
        """Initialize a new Agent from AgentConfig (operation spec §1.1)."""
        self.id = config.id
        self.config = config
        self.state = AgentState.PERCEIVING
        self._register_builtin_tools(config)
        self._persist_agent_row()
        return self.id

    def resume_session(self, snapshot_id: str) -> None:
        """Rebuild the Agent from a persisted snapshot (operation spec §1.2)."""
        snapshot = self._db.load_snapshot(snapshot_id)
        if snapshot is None:
            raise FileNotFoundError(f"snapshot not found: {snapshot_id}")
        # restore policy store
        for rule_data in snapshot.policy_store:
            rule = _dict_to_rule(rule_data)
            self.policy_engine.add_rule(rule)
        # restore goal tree
        self.goal_manager.load_from_repository()
        # restore volatile memory
        for entry in self._mem_repo.load_by_agent(self.id, MemoryTier.VOLATILE):
            self.memory.store(entry, MemoryTier.VOLATILE)
        self.state = AgentState.PERCEIVING

    def submit_goal(self, goal: Goal) -> str:
        """Add a user objective to the GoalTree (operation spec §1.3)."""
        if self.state == AgentState.TERMINATED:
            raise RuntimeError("agent is terminated")
        return self.goal_manager.add_goal(goal)

    def run_cycle(self) -> CycleResult:
        """Execute one perceive → decide → act → reflect cycle (operation spec §1.4)."""
        perception = self.perceive()
        decision = self.decide()
        action_result = self.act(_decision_to_command(decision)) if decision.selected_action else None
        reflection = None
        if self.config.reflection_config.enabled:
            self.state = AgentState.REFLECTING
            ctx = self._build_context()
            trace = DecisionTrace(
                agent_id=self.id,
                perception=perception,
                decision=decision,
                action=_decision_to_command(decision) if decision.selected_action else None,
                result=action_result,
                goal_context=self.goal_manager.active_goal(),
            )
            reflection = self.reflection_engine.reflect(trace, ctx)
            self._refl_repo.save(
                self.id, reflection.id, trace, reflection.critique, reflection.proposals
            )
        self.state = AgentState.PERCEIVING
        return CycleResult(
            perception=perception,
            decision=decision,
            action_result=action_result,
            reflection=reflection,
        )

    def update_policy(self, rule: PolicyRule) -> bool:
        """Add or replace a policy rule via the safe path (operation spec §1.5)."""
        return self.policy_engine.add_rule_safely(rule)

    def get_status(self) -> dict[str, Any]:
        """Return a serializable status snapshot."""
        return {
            "id": self.id,
            "name": self.config.name,
            "state": self.state.value,
            "autonomy": self.config.autonomy_level.value,
            "goals": len(self.goal_manager.get_tree().nodes),
            "rules": len(self.policy_engine.rules),
            "tools": len(self.tool_registry.list_specs()),
            "memory_entries": len(self.memory._volatile),  # noqa: SLF001
        }

    def persist(self) -> str:
        """Persist the current state as a SessionSnapshot."""
        self.state = AgentState.PERSISTING
        snapshot = SessionSnapshot(
            snapshot_id=str(uuid.uuid4()),
            agent_id=self.id,
            config_version=self.config.version,
            volatility_data={"state": self.state.value},
            policy_store=[_rule_to_dict(r) for r in self.policy_engine.rules.values()],
            goal_tree={"root": self.goal_manager.get_tree().root},
            reflection_log_position=len(self.reflection_engine.get_log()),
        )
        ok = self._db.save_snapshot_with_retry(snapshot)
        self.state = AgentState.PERCEIVING
        if not ok:
            _log.error("persistence failed for agent %s", self.id)
        return snapshot.snapshot_id

    # ============================================================ cycle steps

    def perceive(self) -> EnvironmentModel:
        """Sensor → EnvironmentModel → VolatileMemory."""
        self.state = AgentState.PERCEIVING
        readings: dict[str, SensorReading] = {}
        for sid in self.tool_registry.list_sensors():
            sensor = self.tool_registry.get_sensor(sid)
            try:
                reading = sensor.sense()
                readings[sid] = reading
                # store perception in volatile memory
                entry = self.memory.create_entry(
                    content={"sensor": sid, "data": reading.data},
                    source=MemorySource.PERCEPTION,
                    importance=0.4,
                )
                self.memory.store(entry, MemoryTier.VOLATILE)
            except Exception as exc:  # noqa: BLE001 — sensors must not crash the cycle
                _log.warning("sensor %s failed: %s", sid, exc)
        self.environment_model = EnvironmentModel(
            sensor_readings=readings,
            confidence=sum(r.confidence for r in readings.values()) / max(len(readings), 1),
        )
        return self.environment_model

    def decide(self) -> PolicyDecision:
        """PolicyEngine.evaluate() → PolicyDecision."""
        self.state = AgentState.DECIDING
        ctx = self._build_context()
        return self.policy_engine.evaluate(ctx)

    def act(self, command: ActuatorCommand | None) -> ActuatorResult | None:
        """PolicyDecision → Actuator.act() → update Memory/Environment/Goals."""
        if command is None:
            return None
        self.state = AgentState.ACTING
        result = self.tool_registry.execute_safely(command)
        # store action result in memory
        entry = self.memory.create_entry(
            content={
                "actuator": command.actuator_id,
                "action": command.action,
                "success": result.success,
                "error": result.error,
            },
            source=MemorySource.ACTION_RESULT,
            importance=0.6 if result.success else 0.8,
        )
        self.memory.store(entry, MemoryTier.VOLATILE)
        # update goals based on success
        if result.success:
            active = self.goal_manager.active_goal()
            if active and active.success_criteria.kind == "tool_success":
                self.goal_manager.update_status(active.id, GoalStatus.COMPLETED)
        return result

    def reflect(self) -> Any:
        """ReflectionEngine.reflect() → actionable proposals."""
        return self.reflection_engine

    # ============================================================ wiring

    def set_ai_service(self, ai: IAIServicePartner) -> None:
        """Inject the AI service for reflection (deferred wiring)."""
        self._ai_service = ai
        self.reflection_engine._ai = ai  # noqa: SLF001

    def set_rag(self, rag: Any) -> None:
        """Inject a RAG instance into the RagSensorTool (feature_002 integration)."""
        for sid in self.tool_registry.list_sensors():
            if sid == "rag_query":
                sensor: Any = self.tool_registry.get_sensor(sid)
                if hasattr(sensor, "set_rag"):
                    sensor.set_rag(rag)

    # ============================================================ internals

    def _register_builtin_tools(self, config: AgentConfig) -> None:
        """Register built-in tools from config (design §6.6)."""
        fs = FileSystemTool(config.sandbox_root)
        self._safe_register_sensor(fs)
        self._safe_register_actuator(fs)

        rag_tool = RagSensorTool()
        self._safe_register_sensor(rag_tool)

        session_tool = SessionTool(self)
        self._safe_register_sensor(session_tool)
        self._safe_register_actuator(session_tool)

        # optional entry-point discovery
        if config.tool_config.auto_discover:
            for tool in discover_tools():
                if hasattr(tool, "sense"):
                    self._safe_register_sensor(tool)
                if hasattr(tool, "act"):
                    self._safe_register_actuator(tool)

    def _safe_register_sensor(self, sensor: Any) -> None:
        try:
            self.tool_registry.register_sensor(sensor)
        except Exception as exc:  # noqa: BLE001
            _log.debug("sensor registration skipped: %s", exc)

    def _safe_register_actuator(self, actuator: Any) -> None:
        try:
            self.tool_registry.register_actuator(actuator)
        except Exception as exc:  # noqa: BLE001
            _log.debug("actuator registration skipped: %s", exc)

    def _build_context(self) -> PolicyContext:
        from agentx.agent.types import MemoryQuery

        return PolicyContext(
            environment=self.environment_model,
            memory=self.memory.retrieve(MemoryQuery(limit=5)),
            current_goal=self.goal_manager.active_goal(),
            agent_state=self.state,
            autonomy_level=self.config.autonomy_level,
        )

    def _persist_agent_row(self) -> None:
        self._db.upsert_agent(
            agent_id=self.id,
            name=self.config.name,
            version=self.config.version,
            autonomy_level=self.config.autonomy_level.value,
            config_json=json.dumps(
                {"name": self.config.name, "version": self.config.version},
                default=str,
            ),
        )


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _decision_to_command(decision: PolicyDecision) -> ActuatorCommand | None:
    """Convert a PolicyDecision's EXECUTE_TOOL action into an ActuatorCommand."""
    from agentx.agent.types import ActionType

    if decision.selected_action.type != ActionType.EXECUTE_TOOL:
        return None
    params = decision.selected_action.parameters
    tool_id = params.get("tool_id", "")
    return ActuatorCommand(
        actuator_id=tool_id,
        action=params.get("action", "default"),
        parameters={k: v for k, v in params.items() if k not in {"tool_id", "action"}},
        correlation_id=str(uuid.uuid4()),
    )


def _rule_to_dict(rule: PolicyRule) -> dict[str, Any]:
    return {
        "id": rule.id,
        "condition_expr": rule.condition_expr,
        "action": {
            "type": rule.action.type.value,
            "parameters": rule.action.parameters,
            "target_goal": rule.action.target_goal,
        },
        "priority": rule.priority,
        "enabled": rule.enabled,
        "metadata": {
            "source": rule.metadata.source.value,
            "created_by": rule.metadata.created_by,
            "version": rule.metadata.version,
        },
    }


def _dict_to_rule(data: dict[str, Any]) -> PolicyRule:
    from agentx.agent.types import ActionType

    action_data = data.get("action", {})
    meta_data = data.get("metadata", {})
    return PolicyRule(
        id=data.get("id", str(uuid.uuid4())),
        condition_expr=data.get("condition_expr", "true"),
        action=PolicyAction(
            type=ActionType(action_data.get("type", ActionType.PAUSE.value)),
            parameters=action_data.get("parameters", {}),
            target_goal=action_data.get("target_goal"),
        ),
        priority=int(data.get("priority", 500)),
        enabled=bool(data.get("enabled", True)),
        metadata=RuleMetadata(
            source=RuleSource(meta_data.get("source", RuleSource.DEFAULT.value)),
            created_by=meta_data.get("created_by", "default"),
            version=int(meta_data.get("version", 1)),
        ),
    )
