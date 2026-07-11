"""Agent — MVC++ Model facade orchestrating all agent subsystems (design §3.1).

The Agent is the single Model-layer entry point.  It wires together the tool
registry, memory, policy engine, goal manager, and reflection engine, and
exposes the perceive → decide → act → reflect → persist cycle.

Controllers depend on :class:`IAgentModelPartner`, not this concrete class.
"""

from __future__ import annotations

import dataclasses
import json
import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
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
    ActuatorConfig,
    ActuatorResult,
    AgentConfig,
    AgentState,
    AutonomyLevel,
    CycleResult,
    DecisionTrace,
    EnvironmentModel,
    Goal,
    GoalConfig,
    GoalStatus,
    GoalTree,
    MemoryEntry,
    MemoryMetadata,
    MemoryQuery,
    MemorySource,
    MemoryTier,
    MemoryConfig,
    PolicyAction,
    PolicyConfig,
    PolicyContext,
    PolicyDecision,
    PolicyRule,
    Proposal,
    ProposalOutcome,
    ReflectionConfig,
    ReflectionEntry,
    RuleMetadata,
    RuleSource,
    SensorConfig,
    SensorReading,
    SessionSnapshot,
    ToolConfig,
)

_log = logging.getLogger(__name__)


class Agent(IAgentModelPartner):
    """Facade orchestrating all agent subsystems."""

    def __init__(self, config: AgentConfig) -> None:
        self.id = config.id
        self.config = config
        self.state = AgentState.INITIALIZING

        # --- persistence (stdlib sqlite3) ---
        # C7*: canonicalise the persistent path (expand ~, resolve relative).
        from pathlib import Path as _Path

        persistent_path = str(_Path(config.memory_config.persistent_path).expanduser())
        db_path = f"{persistent_path}/agent_session.db"
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
        self.policy_engine = PolicyEngine(repository=self._pol_repo, agent_id=self.id)
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

    @property
    def sandbox_root(self) -> str:
        """L16 (feature_015): expose sandbox_root via the interface."""
        return self.config.sandbox_root

    def start_session(self, config: AgentConfig) -> str:
        """Initialize a new Agent from AgentConfig (operation spec §1.1)."""
        self.id = config.id
        self.config = config
        self.state = AgentState.PERCEIVING
        # H2 (feature_015): propagate the new id to all subsystems so
        # repository saves use the correct agent_id.  Previously the
        # subsystems retained the original __init__ id, splitting data
        # across two agent identities.
        self.policy_engine._agent_id = config.id
        self.memory._agent_id = config.id
        self.goal_manager._agent_id = config.id
        self._register_builtin_tools(config)
        self._persist_agent_row()
        return self.id

    def resume_session(self, snapshot_id: str) -> None:
        """Rebuild the Agent from a persisted snapshot (operation spec §1.2).

        Restores: config (N7), policy rules, goal tree with persisted root
        (N8), volatile memory (N1), reflection log (M2), and built-in tools
        (C1). Pre-existing in-memory state is cleared first (N9).

        The AI service is a non-serialisable runtime object: it is preserved
        on this instance if already set, but callers resuming a *fresh* Agent
        must re-inject it via :meth:`set_ai_service` (C3).

        H7 (feature_015): if the restore fails (corrupted snapshot,
        deserialisation error), the pre-clear in-memory state is restored so
        the agent is not left empty.
        """
        snapshot = self._db.load_snapshot(snapshot_id)
        if snapshot is None:
            raise FileNotFoundError(f"snapshot not found: {snapshot_id}")

        # H7: snapshot pre-clear state so we can roll back on failure.
        saved_rules = dict(self.policy_engine.rules)
        saved_volatile = self.memory.export_volatile()
        saved_reflection = self.reflection_engine.get_log()

        try:
            self._do_restore(snapshot)
        except Exception:
            # Restore the pre-clear state.
            self.policy_engine.clear()
            for rule in saved_rules.values():
                self.policy_engine.add_rule(rule)
            self.memory.import_volatile(saved_volatile)
            self.reflection_engine.restore_log(saved_reflection)
            self.state = AgentState.PERCEIVING
            raise

    def _do_restore(self, snapshot: SessionSnapshot) -> None:
        """The actual restore logic (extracted from resume_session for H7)."""
        # --- N9: clear pre-existing in-memory state before restoring ---
        self.policy_engine.clear()
        self.memory.import_volatile([])
        self.reflection_engine.restore_log([])

        # --- N7: restore config from the snapshot ---
        vol = snapshot.volatility_data or {}
        config_data = vol.get("config")
        if config_data:
            restored = _dict_to_config(config_data)
            if restored is not None:
                restored.id = self.id  # keep the live agent id
                self.config = restored

        # --- restore policy store (N3: repo is source of truth; snapshot is
        # a fallback for data created before the repo-based fix) ---
        loaded_rules = self.policy_engine.load_from_repository()
        if not loaded_rules:
            for rule_data in snapshot.policy_store:
                rule = _dict_to_rule(rule_data)
                # H3 (feature_015): use add_rule_safely so legacy snapshot
                # rules are conflict-checked (previously bypassed via add_rule).
                if not self.policy_engine.add_rule_safely(rule):
                    _log.warning("legacy snapshot rule %s skipped (conflict)", rule.id)

        # --- restore goal tree (N8: honour the persisted root) ---
        root_id = snapshot.goal_tree.get("root") if snapshot.goal_tree else None
        self.goal_manager.load_from_repository(root_id)

        # --- N1: restore volatile memory from the snapshot ---
        volatile_data = vol.get("volatile_memory")
        if volatile_data:
            entries = [_dict_to_memory_entry(d) for d in volatile_data]
            self.memory.import_volatile(entries)

        # --- M2: restore reflection log ---
        if snapshot.reflection_log_position:
            entries = self._refl_repo.load_recent_entries(
                self.id, limit=snapshot.reflection_log_position
            )
            self.reflection_engine.restore_log(entries)

        # --- C1: re-register built-in tools ---
        self._register_builtin_tools(self.config)

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
        # N2: build the command ONCE so the executed action and the traced
        # action share the same correlation_id.
        command = _decision_to_command(decision)
        action_result = self.act(command) if command is not None else None
        reflection = None
        # N11: skip reflection entirely when no AI service is wired, so the
        # reflection log is not polluted with "(reflection disabled)" entries
        # every cycle. The engine still degrades gracefully if the AI call
        # itself fails at runtime.
        if self.config.reflection_config.enabled and self.reflection_engine.has_ai_service():
            self.state = AgentState.REFLECTING
            ctx = self._build_context()
            trace = DecisionTrace(
                agent_id=self.id,
                perception=perception,
                decision=decision,
                action=command,
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

    def clear_state(self) -> None:
        """Clear all volatile agent state (feature_010: demo re-seed support).

        Clears the goal tree, policy rules, and volatile memory, then returns
        the agent to the ``PERCEIVING`` state so a demo scenario can be loaded
        cleanly.  Only in-memory state is cleared; persisted snapshots and
        repository rows are not modified (operation_spec_001_agent_demo.md).
        """
        self.goal_manager.clear()
        self.policy_engine.clear()
        self.memory.clear_volatile()
        self.state = AgentState.PERCEIVING

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
            "memory_entries": self.memory.count_volatile(),
        }

    def persist(self) -> str:
        """Persist the current state as a SessionSnapshot."""
        self.state = AgentState.PERSISTING
        snapshot = SessionSnapshot(
            snapshot_id=str(uuid.uuid4()),
            agent_id=self.id,
            config_version=self.config.version,
            volatility_data={
                "state": self.state.value,
                "config": _config_to_dict(self.config),  # N7
                "volatile_memory": [  # N1
                    _memory_entry_to_dict(e) for e in self.memory.export_volatile()
                ],
            },
            policy_store=[_rule_to_dict(r) for r in self.policy_engine.rules.values()],
            goal_tree={"root": self.goal_manager.get_tree().root},
            reflection_log_position=len(self.reflection_engine.get_log()),
        )
        ok = self._db.save_snapshot_with_retry(snapshot)
        self.state = AgentState.PERCEIVING
        if not ok:
            _log.error("persistence failed for agent %s", self.id)
            # H4 (feature_015): return "" so callers can detect failure.
            return ""
        return snapshot.snapshot_id

    def load_snapshot(self, snapshot_id: str) -> SessionSnapshot | None:
        """Read a persisted SessionSnapshot by id (C4: facade owns persistence)."""
        return self._db.load_snapshot(snapshot_id)

    def load_latest_snapshot(self) -> SessionSnapshot | None:
        """Read the most recent snapshot for this agent (C5/I1: resume on open)."""
        return self._db.load_latest_snapshot(self.id)

    # ----------------------------------------------------------- query helpers (N6)

    def list_rules(self) -> list[PolicyRule]:
        """Return the current policy rules."""
        return list(self.policy_engine.rules.values())

    def list_goals(self) -> GoalTree:
        """Return the current goal tree."""
        return self.goal_manager.get_tree()

    def query_memory(self, query: "MemoryQuery") -> list[MemoryEntry]:
        """Retrieve memory entries matching *query*."""
        return self.memory.retrieve(query)

    # ----------------------------------------------------------- tool ops (N14)

    def list_tools(self) -> list[Any]:
        """Return the registered tool specs (N14: via facade, not tool_registry)."""
        return self.tool_registry.list_specs()

    def register_tool(self, tool: Any) -> Any:
        """Register a sensor/actuator with the tool registry (N14)."""
        if hasattr(tool, "sense"):
            return self.tool_registry.register_sensor(tool)
        return self.tool_registry.register_actuator(tool)

    def unregister_tool(self, tool_id: str) -> bool:
        """Unregister a tool by id (N14)."""
        return self.tool_registry.unregister(tool_id)

    def execute_tool_action(self, command: ActuatorCommand) -> ActuatorResult:
        """Validate and run an actuator command (N14)."""
        return self.tool_registry.execute_safely(command)

    def tool_health_check(self) -> dict[str, bool]:
        """Return {tool_id: alive} for all tools (N14)."""
        return self.tool_registry.health_check()

    # ----------------------------------------------------------- reflection (N4)

    def list_pending_proposals(self) -> list[tuple[str, int, "Proposal"]]:
        """Return ``(entry_id, proposal_index, proposal)`` for proposals
        awaiting user confirmation (N4: closes the self-improvement loop)."""
        return self.reflection_engine.pending_proposals()

    def approve_proposal(self, entry_id: str, proposal_idx: int) -> "ProposalOutcome":
        """Apply a pending reflection proposal via its router (N4)."""
        return self.reflection_engine.approve_proposal(entry_id, proposal_idx)

    # ============================================================ cycle steps

    def perceive(self) -> EnvironmentModel:
        """Sensor → EnvironmentModel → VolatileMemory."""
        self.state = AgentState.PERCEIVING
        readings: dict[str, SensorReading] = {}
        for sid in self.tool_registry.list_sensors():
            # N5: skip disabled sensors (set via reflection/TOOL_CONFIGURATION).
            if not self.tool_registry.is_enabled(sid):
                continue
            sensor = self.tool_registry.get_sensor(sid)
            try:
                reading = sensor.sense()
            except Exception as exc:  # noqa: BLE001 — sensors must not crash the cycle
                # M1: surface the failure as a zero-confidence reading so the
                # policy layer can react (e.g. `environment.confidence < 0.5`).
                _log.warning("sensor %s failed: %s", sid, exc)
                reading = SensorReading(
                    sensor_id=sid,
                    data={"error": str(exc)},
                    confidence=0.0,
                )
            readings[sid] = reading
            # store perception in volatile memory
            entry = self.memory.create_entry(
                content={"sensor": sid, "data": reading.data},
                source=MemorySource.PERCEPTION,
                importance=0.4,
            )
            self.memory.store(entry, MemoryTier.VOLATILE)
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
        # C6: only complete the active goal when the acting tool matches the
        # goal's expected tool (or the goal accepts any successful tool).
        # L7 (feature_015): removed dead `and command is not None` check —
        # command is always non-None here (None is returned at line 408).
        # S8 (feature_015): "manual" kind never auto-completes.
        if result.success:
            active = self.goal_manager.active_goal()
            if active and active.success_criteria.kind == "tool_success":
                expected_tool = active.success_criteria.tool_id
                if expected_tool is None or expected_tool == command.actuator_id:
                    self.goal_manager.update_status(active.id, GoalStatus.COMPLETED)
        return result

    def reflect(self, trace: DecisionTrace, ctx: PolicyContext) -> ReflectionEntry:
        """ReflectionEngine.reflect() → actionable proposals (operation spec §1.6).

        C2: previously returned the engine itself. ``run_cycle`` calls the
        engine directly; this method exposes reflection for external callers.
        """
        return self.reflection_engine.reflect(trace, ctx)

    # ============================================================ wiring

    def set_ai_service(self, ai: IAIServicePartner) -> None:
        """Inject the AI service for reflection (deferred wiring)."""
        self._ai_service = ai
        self.reflection_engine.set_ai_service(ai)  # N13: public API, not _ai reach

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
        # L8 (feature_015): unregister stale tools first so config changes
        # (e.g. sandbox_root) take effect.  Previously DuplicateToolError was
        # silently swallowed, so the old tool with the old sandbox was kept.
        self.tool_registry.unregister("filesystem")
        self.tool_registry.unregister("rag_query")
        self.tool_registry.unregister("session")

        fs = FileSystemTool(config.sandbox_root)
        self._safe_register_sensor(fs)
        self._safe_register_actuator(fs)

        rag_tool = RagSensorTool()
        self._safe_register_sensor(rag_tool)
        self._safe_register_actuator(rag_tool)  # N12: query action for EXECUTE_TOOL

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
            memory=self.memory.retrieve(MemoryQuery(limit=self.config.context_memory_limit)),  # m2
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
    # m1: an EXECUTE_TOOL action without a valid tool_id cannot be dispatched.
    if not tool_id:
        _log.warning("EXECUTE_TOOL action has no tool_id — dropping command")
        return None
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


# ---------------------------------------------------------------------------
# config serialisation (N7)
# ---------------------------------------------------------------------------


def _config_to_dict(config: AgentConfig) -> dict[str, Any]:
    """Recursively serialise an :class:`AgentConfig` (enums→value, datetimes→iso)."""

    def _normalize(obj: Any) -> Any:
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, datetime):
            return obj.isoformat()
        if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
            return {f.name: _normalize(getattr(obj, f.name)) for f in dataclasses.fields(obj)}
        if isinstance(obj, list):
            return [_normalize(x) for x in obj]
        if isinstance(obj, dict):
            return {k: _normalize(v) for k, v in obj.items()}
        return obj

    return _normalize(config)


def _dict_to_config(data: dict[str, Any]) -> AgentConfig | None:
    """Reconstruct an :class:`AgentConfig` from a serialised dict (N7).

    Returns ``None`` on malformed input so resume degrades gracefully rather
    than crashing.
    """
    if not data:
        return None
    try:
        return AgentConfig(
            id=data.get("id", ""),
            name=data.get("name", "agentx-agent"),
            version=int(data.get("version", 1)),
            sensors=[_dict_to_sensor_config(s) for s in data.get("sensors", [])],
            actuators=[_dict_to_actuator_config(a) for a in data.get("actuators", [])],
            policy_config=_dict_to_policy_config(data.get("policy_config", {})),
            memory_config=_dict_to_memory_config(data.get("memory_config", {})),
            goal_config=_dict_to_goal_config(data.get("goal_config", {})),
            reflection_config=_dict_to_reflection_config(data.get("reflection_config", {})),
            tool_config=_dict_to_tool_config(data.get("tool_config", {})),
            autonomy_level=AutonomyLevel(
                data.get("autonomy_level", AutonomyLevel.SUPERVISED.value)
            ),
            sandbox_root=data.get("sandbox_root", "."),
            context_memory_limit=int(data.get("context_memory_limit", 5)),  # m2
            created_at=_from_iso_str(data.get("created_at")),
            updated_at=_from_iso_str(data.get("updated_at")),
        )
    except (KeyError, ValueError, TypeError):
        return None


def _dict_to_sensor_config(data: dict[str, Any]) -> SensorConfig:
    return SensorConfig(
        id=data.get("id", ""),
        type=data.get("type", ""),
        enabled=bool(data.get("enabled", True)),
        parameters=data.get("parameters", {}),
        sampling_rate=data.get("sampling_rate"),
    )


def _dict_to_actuator_config(data: dict[str, Any]) -> ActuatorConfig:
    return ActuatorConfig(
        id=data.get("id", ""),
        type=data.get("type", ""),
        enabled=bool(data.get("enabled", True)),
        parameters=data.get("parameters", {}),
        requires_confirmation=bool(data.get("requires_confirmation", False)),
    )


def _dict_to_policy_config(data: dict[str, Any]) -> PolicyConfig:
    from agentx.agent.types import ConflictResolutionStrategy

    return PolicyConfig(
        rules_file=data.get("rules_file", "policies/rules.json"),
        conflict_resolution=ConflictResolutionStrategy(
            data.get("conflict_resolution", ConflictResolutionStrategy.PRIORITY_WINS.value)
        ),
        default_autonomy=AutonomyLevel(
            data.get("default_autonomy", AutonomyLevel.SUPERVISED.value)
        ),
        max_rules=int(data.get("max_rules", 1000)),
    )


def _dict_to_memory_config(data: dict[str, Any]) -> MemoryConfig:
    return MemoryConfig(
        volatile_capacity=int(data.get("volatile_capacity", 10_000)),
        persistent_path=data.get("persistent_path", "local_sessions/current"),
        consolidation_interval=float(data.get("consolidation_interval", 300.0)),
        embedding_model=data.get("embedding_model", "nomic-embed-text"),
        max_persistent_entries=int(data.get("max_persistent_entries", 100_000)),
    )


def _dict_to_goal_config(data: dict[str, Any]) -> GoalConfig:
    return GoalConfig(
        max_active_goals=int(data.get("max_active_goals", 10)),
        default_priority=int(data.get("default_priority", 50)),
        auto_decompose=bool(data.get("auto_decompose", True)),
        max_depth=int(data.get("max_depth", 5)),
    )


def _dict_to_reflection_config(data: dict[str, Any]) -> ReflectionConfig:
    return ReflectionConfig(
        enabled=bool(data.get("enabled", True)),
        interval=float(data.get("interval", 600.0)),
        prompt_template=data.get("prompt_template", "built-in"),
        ai_service_id=data.get("ai_service_id", "default"),
        min_confidence=float(data.get("min_confidence", 0.7)),
    )


def _dict_to_tool_config(data: dict[str, Any]) -> ToolConfig:
    return ToolConfig(auto_discover=bool(data.get("auto_discover", False)))


# ---------------------------------------------------------------------------
# memory-entry serialisation (N1)
# ---------------------------------------------------------------------------


def _memory_entry_to_dict(entry: MemoryEntry) -> dict[str, Any]:
    return {
        "id": entry.id,
        "content": entry.content,
        "metadata": {
            "created_at": entry.metadata.created_at.isoformat(),
            "access_count": entry.metadata.access_count,
            "last_accessed": entry.metadata.last_accessed.isoformat(),
            "importance": entry.metadata.importance,
            "tags": entry.metadata.tags,
            "source": entry.metadata.source.value,
        },
        "embedding": entry.embedding,
        "tier": entry.tier.value,
    }


def _dict_to_memory_entry(data: dict[str, Any]) -> MemoryEntry:
    meta = data.get("metadata", {})
    return MemoryEntry(
        id=data.get("id", str(uuid.uuid4())),
        content=data.get("content", {}),
        metadata=MemoryMetadata(
            created_at=_from_iso_str(meta.get("created_at")),
            access_count=int(meta.get("access_count", 0)),
            last_accessed=_from_iso_str(meta.get("last_accessed")),
            importance=float(meta.get("importance", 0.5)),
            tags=meta.get("tags", []),
            source=MemorySource(meta.get("source", MemorySource.PERCEPTION.value)),
        ),
        embedding=data.get("embedding"),
        tier=MemoryTier(data.get("tier", MemoryTier.VOLATILE.value)),
    )


def _from_iso_str(value: Any) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromisoformat(str(value))
    except (ValueError, TypeError):
        return datetime.now(timezone.utc)
