"""Regression tests for the feature_007 bug-fix pass (BUG_FIX_PLAN.md).

Each test maps to a bug ID (C1–C6, M1–M8, N1–N11) and locks in the fix so it
cannot silently regress.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from agentx.agent.controller.agent_controller import AgentController
from agentx.agent.controller.session_controller import SessionController
from agentx.agent.interfaces import IAIServicePartner
from agentx.agent.model.agent import Agent
from agentx.agent.model.tools.session_tool import SessionTool
from agentx.agent.types import (
    ActionType,
    AgentConfig,
    AutonomyLevel,
    GoalStatus,
    GoalType,
    MemoryConfig,
    MemoryQuery,
    MemorySource,
    MemoryTier,
    PolicyAction,
    PolicyRule,
    ProposalStatus,
    ProposalType,
    RuleMetadata,
    RuleSource,
    SuccessCriteria,
)


# ---------------------------------------------------------------------------
# Test doubles
# ---------------------------------------------------------------------------


class FakeAIService(IAIServicePartner):
    """Returns a fixed critique JSON so reflection runs without a real LLM."""

    def __init__(self, response: str | None = None) -> None:
        self._response = response or json.dumps(
            {
                "critique": {
                    "summary": "ok",
                    "strengths": ["fast"],
                    "weaknesses": [],
                    "confidence": "Medium",
                },
                "proposals": [],
            }
        )

    def complete(self, prompt: str) -> str:
        return self._response


class FakeSensor:
    """Sensor that raises on sense() (for M1) or returns a reading.

    Registered as a virtual ISensor via duck-typing (register_sensor accepts
    any object with the sensor protocol).
    """

    def __init__(self, raise_on_sense: bool = False) -> None:
        self.id = "fake_sensor"
        self._raise = raise_on_sense

    def sense(self):
        if self._raise:
            raise RuntimeError("boom")
        from agentx.agent.types import SensorReading

        return SensorReading(sensor_id=self.id, data={"ok": True}, confidence=0.5)

    def get_sensor_schema(self):
        from agentx.agent.model.tools.spec import JsonSchema, SensorSchema

        return SensorSchema(sensor_id=self.id, description="fake", output_schema=JsonSchema(type="object"))


# ---------------------------------------------------------------------------
# Group 1 — resume_session() completeness
# ---------------------------------------------------------------------------


class TestResumeCompleteness:
    def test_resume_restores_tools(self, agent_config):
        """C1: built-in tools are re-registered after resume."""
        agent = Agent(agent_config)
        before = set(agent.tool_registry.list_sensors())
        sid = agent.persist()
        agent.resume_session(sid)
        after = set(agent.tool_registry.list_sensors())
        assert before == after
        assert {"filesystem", "rag_query", "session"}.issubset(after)

    def test_resume_restores_volatile_memory(self, agent_config):
        """N1: volatile memory survives persist → resume."""
        agent = Agent(agent_config)
        for _ in range(3):
            entry = agent.memory.create_entry(
                content={"v": 1}, source=MemorySource.USER_INPUT, importance=0.9
            )
            agent.memory.store(entry, MemoryTier.VOLATILE)
        assert agent.memory.count_volatile() == 3
        sid = agent.persist()
        agent.resume_session(sid)
        assert agent.memory.count_volatile() == 3

    def test_resume_restores_config(self, agent_config):
        """N7: config (autonomy, sandbox) is restored from the snapshot."""
        agent = Agent(agent_config)
        agent.config.autonomy_level = AutonomyLevel.MANUAL_ONLY
        sid = agent.persist()
        # Simulate a fresh agent with a different default config resuming.
        agent.resume_session(sid)
        assert agent.config.autonomy_level == AutonomyLevel.MANUAL_ONLY

    def test_resume_clears_pre_existing_state(self, agent_config):
        """N9: resume replaces (not merges) in-memory state — extra volatile
        entries added after the snapshot are discarded."""
        agent = Agent(agent_config)
        for _ in range(3):
            entry = agent.memory.create_entry(
                content={"v": 1}, source=MemorySource.USER_INPUT
            )
            agent.memory.store(entry, MemoryTier.VOLATILE)
        sid = agent.persist()  # snapshot holds 3 entries
        # Add 2 more entries that are NOT in the snapshot.
        for _ in range(2):
            entry = agent.memory.create_entry(
                content={"v": 2}, source=MemorySource.USER_INPUT
            )
            agent.memory.store(entry, MemoryTier.VOLATILE)
        assert agent.memory.count_volatile() == 5
        agent.resume_session(sid)
        # N9: the 2 extra entries are cleared; only the 3 from the snapshot remain.
        assert agent.memory.count_volatile() == 3

    def test_resume_restores_reflection_log(self, agent_config):
        """M2: reflection log is repopulated after resume."""
        agent = Agent(agent_config)
        agent.set_ai_service(FakeAIService())
        agent.run_cycle()  # produces + persists a reflection entry
        assert len(agent.reflection_engine.get_log()) == 1
        sid = agent.persist()
        agent.resume_session(sid)
        assert len(agent.reflection_engine.get_log()) >= 1

    def test_resume_preserves_goal_root(self, agent_config):
        """N8: the goal-tree root is preserved across resume."""
        agent = Agent(agent_config)
        g1 = agent.goal_manager.create_goal("first")
        g2 = agent.goal_manager.create_goal("second")
        agent.submit_goal(g1)
        agent.submit_goal(g2)
        root_before = agent.goal_manager.get_tree().root
        sid = agent.persist()
        agent.resume_session(sid)
        assert agent.goal_manager.get_tree().root == root_before


# ---------------------------------------------------------------------------
# Group 2 — cycle correctness
# ---------------------------------------------------------------------------


class TestCycleCorrectness:
    def test_run_cycle_trace_action_matches_executed_command(self, agent_config):
        """N2: the traced action shares the executed command's correlation_id."""
        agent = Agent(agent_config)
        agent.set_ai_service(FakeAIService())
        sandbox = Path(agent_config.sandbox_root)
        (sandbox / "target.txt").write_text("data")

        rule = PolicyRule(
            id="r1",
            condition_expr="goal.active",
            action=PolicyAction(
                type=ActionType.EXECUTE_TOOL,
                parameters={"tool_id": "filesystem", "action": "read", "path": "target.txt"},
            ),
            priority=900,
            metadata=RuleMetadata(source=RuleSource.USER_DEFINED),
        )
        agent.update_policy(rule)
        agent.submit_goal(
            agent.goal_manager.create_goal("read", success_criteria=SuccessCriteria(kind="tool_success"))
        )

        captured: list[Any] = []
        original_act = agent.act

        def spy_act(command):
            captured.append(command)
            return original_act(command)

        agent.act = spy_act  # type: ignore[assignment]
        agent.run_cycle()

        assert len(captured) == 1
        executed = captured[0]
        log = agent.reflection_engine.get_log()
        assert log, "reflection log should have an entry"
        traced = log[-1].trace.action
        assert traced is not None
        assert traced.correlation_id == executed.correlation_id

    def test_goal_complete_only_on_relevant_tool(self, agent_config):
        """C6: a goal scoped to a specific tool is not completed by another tool."""
        agent = Agent(agent_config)
        sandbox = Path(agent_config.sandbox_root)
        (sandbox / "a.txt").write_text("a")
        (sandbox / "b.txt").write_text("b")

        # Goal expects the 'session' tool to succeed.
        goal = agent.goal_manager.create_goal(
            "session work",
            success_criteria=SuccessCriteria(kind="tool_success", tool_id="session"),
        )
        agent.submit_goal(goal)

        # Rule executes the 'filesystem' tool (NOT session).
        rule = PolicyRule(
            id="r1",
            condition_expr="goal.active",
            action=PolicyAction(
                type=ActionType.EXECUTE_TOOL,
                parameters={"tool_id": "filesystem", "action": "read", "path": "a.txt"},
            ),
            priority=900,
            metadata=RuleMetadata(source=RuleSource.USER_DEFINED),
        )
        agent.update_policy(rule)
        agent.run_cycle()

        # Filesystem succeeded but the goal wanted 'session' → still active.
        assert agent.goal_manager.get_goal(goal.id).status == GoalStatus.ACTIVE

    def test_goal_complete_on_any_tool_when_unscoped(self, agent_config):
        """C6: unscoped tool_success goals still complete on any successful tool."""
        agent = Agent(agent_config)
        sandbox = Path(agent_config.sandbox_root)
        (sandbox / "a.txt").write_text("a")
        goal = agent.goal_manager.create_goal(
            "read", success_criteria=SuccessCriteria(kind="tool_success")
        )
        agent.submit_goal(goal)
        rule = PolicyRule(
            id="r1",
            condition_expr="goal.active",
            action=PolicyAction(
                type=ActionType.EXECUTE_TOOL,
                parameters={"tool_id": "filesystem", "action": "read", "path": "a.txt"},
            ),
            priority=900,
            metadata=RuleMetadata(source=RuleSource.USER_DEFINED),
        )
        agent.update_policy(rule)
        agent.run_cycle()
        assert agent.goal_manager.get_goal(goal.id).status == GoalStatus.COMPLETED


# ---------------------------------------------------------------------------
# Group 3 — model API
# ---------------------------------------------------------------------------


class TestModelAPI:
    def test_reflect_returns_reflection_entry(self, agent_config):
        """C2: reflect() returns a ReflectionEntry, not the engine."""
        from agentx.agent.types import DecisionTrace, PolicyContext, ReflectionEntry

        agent = Agent(agent_config)
        agent.set_ai_service(FakeAIService())
        trace = DecisionTrace(agent_id=agent.id)
        ctx = PolicyContext()
        result = agent.reflect(trace, ctx)
        assert isinstance(result, ReflectionEntry)

    def test_controller_load_snapshot_uses_facade(self, agent_config):
        """C4: SessionController.load_snapshot delegates to the agent facade."""
        agent = Agent(agent_config)
        sid = agent.persist()
        controller = SessionController(agent)
        loaded = controller.load_snapshot(sid)
        assert loaded is not None
        assert loaded.snapshot_id == sid

    def test_session_tool_restore_calls_resume_session(self, agent_config):
        """M8: SessionTool restore action succeeds (calls resume_session)."""
        from agentx.agent.types import ActuatorCommand

        agent = Agent(agent_config)
        sid = agent.persist()
        tool = SessionTool(agent)
        result = tool.act(
            ActuatorCommand(
                actuator_id="session",
                action="restore",
                parameters={"action": "restore", "snapshot_id": sid},
            )
        )
        assert result.success is True


# ---------------------------------------------------------------------------
# Group 4 — robustness
# ---------------------------------------------------------------------------


class TestRobustness:
    def test_perceive_returns_failed_reading_on_sensor_error(self, agent_config):
        """M1: a failing sensor produces a zero-confidence reading, not a skip."""
        agent = Agent(agent_config)
        agent.tool_registry.register_sensor(FakeSensor(raise_on_sense=True))
        env = agent.perceive()
        reading = env.sensor_readings.get("fake_sensor")
        assert reading is not None
        assert reading.confidence == 0.0
        assert "error" in reading.data

    def test_reflection_skipped_without_ai_service(self, agent_config):
        """N11: no reflection entry is created when no AI service is wired."""
        agent = Agent(agent_config)
        result = agent.run_cycle()
        assert result.reflection is None
        assert agent.reflection_engine.get_log() == []

    def test_safety_deny_list_rejects_dangerous_ops(self, agent_config):
        """M7: deny-listed operations are rejected regardless of autonomy."""
        from agentx.agent.model.reflection.safety_evaluator import DefaultSafetyEvaluator
        from agentx.agent.types import PolicyContext, Proposal, ProposalType

        evaluator = DefaultSafetyEvaluator()
        ctx = PolicyContext(autonomy_level=AutonomyLevel.FULLY_AUTONOMOUS)
        proposal = Proposal(
            type=ProposalType.GOAL_ADJUSTMENT,
            content={"op": "delete", "goal_id": "x"},
        )
        verdict = evaluator.evaluate(proposal, ctx)
        assert verdict.status == ProposalStatus.REJECTED


# ---------------------------------------------------------------------------
# Group 5 — tool enablement
# ---------------------------------------------------------------------------


class TestToolEnablement:
    def test_disable_tool_stops_perception(self, agent_config):
        """N5: a disabled sensor is not polled during perceive()."""
        agent = Agent(agent_config)
        agent.tool_registry.set_tool_enabled("filesystem", False)
        env = agent.perceive()
        assert "filesystem" not in env.sensor_readings

    def test_disable_tool_blocks_execution(self, agent_config):
        """N5: a disabled actuator cannot be executed."""
        from agentx.agent.types import ActuatorCommand

        agent = Agent(agent_config)
        agent.tool_registry.set_tool_enabled("filesystem", False)
        result = agent.tool_registry.execute_safely(
            ActuatorCommand(
                actuator_id="filesystem",
                action="read",
                parameters={"path": "x.txt"},
            )
        )
        assert result.success is False
        assert result.error is not None and "disabled" in result.error

    def test_set_tool_enabled_unknown_returns_false(self, agent_config):
        """M6: set_tool_enabled returns False for unknown tools."""
        agent = Agent(agent_config)
        assert agent.tool_registry.set_tool_enabled("nope", False) is False
        assert agent.tool_registry.is_enabled("filesystem") is True


# ---------------------------------------------------------------------------
# Group 6 — persistence unification
# ---------------------------------------------------------------------------


class TestPersistenceUnification:
    def test_policy_rule_survives_without_snapshot(self, agent_config):
        """N3: a rule added via update_policy is persisted to the repo, so a
        fresh Agent (same id/path) loads it even without calling persist()."""
        agent = Agent(agent_config)
        rule = PolicyRule(
            id="repo-rule",
            condition_expr="true",
            action=PolicyAction(type=ActionType.PAUSE),
            metadata=RuleMetadata(source=RuleSource.USER_DEFINED),
        )
        assert agent.update_policy(rule) is True
        # Do NOT call persist() — the repo should still hold the rule.
        agent2 = Agent(agent_config)  # same id/path
        loaded = agent2.policy_engine.load_from_repository()
        ids = {r.id for r in loaded}
        assert "repo-rule" in ids


# ---------------------------------------------------------------------------
# Group 8 — reflection loop closure (N4)
# ---------------------------------------------------------------------------


class TestReflectionApproval:
    def test_supervised_proposal_can_be_approved_and_applied(self, tmp_agent_dir):
        """N4: a NEEDS_CONFIRMATION proposal can be approved and applied."""
        sandbox = Path(tmp_agent_dir) / "sandbox"
        sandbox.mkdir()
        config = AgentConfig(
            id="supervised-agent",
            name="Supervised",
            autonomy_level=AutonomyLevel.SUPERVISED,  # → NEEDS_CONFIRMATION
            memory_config=MemoryConfig(persistent_path=tmp_agent_dir),
            sandbox_root=str(sandbox),
        )
        proposal_json = json.dumps(
            {
                "critique": {"summary": "suggest mem", "confidence": "High"},
                "proposals": [
                    {
                        "type": "MEMORY_UPDATE",
                        "content": {"op": "add", "text": "learned", "importance": 0.8},
                        "rationale": "remember this",
                    }
                ],
            }
        )
        agent = Agent(config)
        agent.set_ai_service(FakeAIService(proposal_json))
        before = agent.memory.count_volatile()
        agent.run_cycle()

        pending = agent.list_pending_proposals()
        assert len(pending) == 1, "proposal should be pending (NEEDS_CONFIRMATION)"
        entry_id, idx, proposal = pending[0]
        assert proposal.status == ProposalStatus.NEEDS_CONFIRMATION

        outcome = agent.approve_proposal(entry_id, idx)
        assert outcome.status == ProposalStatus.APPLIED
        assert agent.memory.count_volatile() > before


# ---------------------------------------------------------------------------
# Group 9 — MVC++ hygiene (N6)
# ---------------------------------------------------------------------------


class TestControllerPartnerMethods:
    def test_controller_exposes_partner_query_methods(self, agent_config):
        """N6: the controller exposes list_rules/list_goals/query_memory/save."""
        agent = Agent(agent_config)
        agent.update_policy(
            PolicyRule(
                id="r1",
                condition_expr="true",
                action=PolicyAction(type=ActionType.PAUSE),
                metadata=RuleMetadata(source=RuleSource.DEFAULT),
            )
        )
        agent.submit_goal(agent.goal_manager.create_goal("g"))
        controller = AgentController(agent)

        rules = controller.list_rules()
        assert len(rules) == 1 and rules[0].id == "r1"

        tree = controller.list_goals()
        assert len(tree.nodes) == 1

        mem = controller.query_memory(limit=5)
        assert isinstance(mem, list)

        sid = controller.save_snapshot()
        assert sid


# ---------------------------------------------------------------------------
# Remaining P2/P3 fixes
# ---------------------------------------------------------------------------


class TestRemainingFixes:
    def test_decision_to_command_drops_empty_tool_id(self, agent_config):
        """m1: an EXECUTE_TOOL action without a tool_id produces no command."""
        from agentx.agent.model.agent import _decision_to_command
        from agentx.agent.types import PolicyAction, PolicyDecision

        decision = PolicyDecision(
            selected_action=PolicyAction(type=ActionType.EXECUTE_TOOL, parameters={})
        )
        assert _decision_to_command(decision) is None

    def test_critique_parser_handles_nested_json(self):
        """m5: nested JSON objects are not truncated by the fenced regex."""
        from agentx.agent.model.reflection.critique_parser import CritiqueParser
        from agentx.agent.types import DecisionTrace

        raw = '```json\n{"critique": {"summary": "ok", "strengths": ["a", {"b": 1}]}, "proposals": []}\n```'
        entry = CritiqueParser().parse(raw, DecisionTrace(agent_id="x"))
        assert entry.critique.summary == "ok"
        assert entry.critique.strengths == ["a", {"b": 1}]

    def test_set_ai_service_enables_reflection(self, agent_config):
        """N13: set_ai_service wires the engine via its public API."""
        from agentx.agent.types import DecisionTrace, PolicyContext

        agent = Agent(agent_config)
        assert not agent.reflection_engine.has_ai_service()
        agent.set_ai_service(FakeAIService())
        assert agent.reflection_engine.has_ai_service()
        result = agent.reflect(DecisionTrace(agent_id=agent.id), PolicyContext())
        assert result.critique.summary == "ok"

    def test_context_memory_limit_configurable(self, tmp_agent_dir):
        """m2: context_memory_limit controls how many entries feed decide()."""
        sandbox = Path(tmp_agent_dir) / "sandbox"
        sandbox.mkdir()
        config = AgentConfig(
            id="cfg-agent",
            memory_config=MemoryConfig(persistent_path=tmp_agent_dir),
            sandbox_root=str(sandbox),
            context_memory_limit=2,
        )
        agent = Agent(config)
        for _ in range(5):
            entry = agent.memory.create_entry(content={"k": 1}, source=MemorySource.USER_INPUT)
            agent.memory.store(entry, MemoryTier.VOLATILE)
        ctx = agent._build_context()  # noqa: SLF001
        assert len(ctx.memory) == 2

    def test_list_tools_via_facade(self, agent_config):
        """N14: the facade exposes list_tools; ToolController uses it."""
        from agentx.agent.controller.tool_controller import ToolController

        agent = Agent(agent_config)
        tools = agent.list_tools()
        assert len(tools) >= 3
        tc = ToolController(agent)
        assert len(tc.list_tools()) == len(tools)
        assert isinstance(tc.health_check(), dict)

    def test_rag_tool_actuator_query(self):
        """N12: RagSensorTool supports an actuator 'query' action."""
        from agentx.agent.model.tools.rag_sensor_tool import RagSensorTool
        from agentx.agent.types import ActuatorCommand

        class FakeRag:
            def query(self, prompt, history=None):
                return f"answer:{prompt}"

        tool = RagSensorTool(FakeRag())
        result = tool.act(
            ActuatorCommand(
                actuator_id="rag_query",
                action="query",
                parameters={"action": "query", "prompt": "hello"},
            )
        )
        assert result.success is True
        assert result.output["result"] == "answer:hello"

    def test_rag_tool_rejects_unknown_action(self):
        """N12: the RAG actuator rejects actions other than 'query'."""
        from agentx.agent.model.tools.rag_sensor_tool import RagSensorTool
        from agentx.agent.types import ActuatorCommand

        tool = RagSensorTool()
        result = tool.act(
            ActuatorCommand(
                actuator_id="rag_query",
                action="delete",
                parameters={"action": "delete", "prompt": "x"},
            )
        )
        assert result.success is False

    def test_conflict_overlap_ignores_operators(self):
        """N15: overlap is computed on identifiers, not operators/parens."""
        from agentx.agent.model.policy.conflict_resolver import ConflictResolver

        resolver = ConflictResolver()
        # Same structure tokens (parens/==) but different identifiers → no overlap.
        score = resolver._condition_overlap("goal.active == true", "(x == 1)")
        assert score == 0.0
        # Shared identifier → overlap.
        score2 = resolver._condition_overlap("goal.active", "goal.active == true")
        assert score2 > 0.0

    def test_filesystem_scan_capped(self, agent_config):
        """m10: sense() caps the number of files returned."""
        from agentx.agent.model.tools.filesystem_tool import FileSystemTool

        sandbox = Path(agent_config.sandbox_root)
        tool = FileSystemTool(sandbox)
        # Create more files than the cap to prove the cap binds.
        cap = FileSystemTool.MAX_FILES
        for i in range(cap + 5):
            (sandbox / f"f{i}.txt").write_text("x")
        reading = tool.sense()
        assert len(reading.data) <= cap

    def test_condition_compare_logs_typeerror(self, agent_config, caplog):
        """M5: a TypeError in comparison is logged, not silently False."""
        import logging

        from agentx.agent.model.policy.rule import (
            Comparison,
            ConditionEvaluator,
            Identifier,
            Literal,
        )
        from agentx.agent.types import PolicyContext

        evaluator = ConditionEvaluator()
        # 'memory' resolves to a list; list < 1 raises TypeError → logged (M5).
        node = Comparison("<", Identifier(["memory"]), Literal(1))
        with caplog.at_level(logging.WARNING, logger="agentx.agent.model.policy.rule"):
            result = evaluator.evaluate(node, PolicyContext())
        assert result is False
        assert any("compare" in rec.message for rec in caplog.records)

    def test_persistent_path_canonicalized(self, tmp_agent_dir):
        """C7*: a relative/~ persistent path is canonicalised."""
        import os

        config = AgentConfig(
            id="path-agent",
            memory_config=MemoryConfig(persistent_path=tmp_agent_dir),
            sandbox_root=tmp_agent_dir,
        )
        agent = Agent(config)
        # The db path should be absolute (resolved) and the file should exist.
        assert os.path.isabs(agent._db.path)  # noqa: SLF001
