"""Integration tests — agent facade cycle, controllers, session persistence (T2)."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentx.agent.controller.agent_controller import AgentController
from agentx.agent.controller.session_controller import SessionController
from agentx.agent.controller.tool_controller import ToolController
from agentx.agent.model.agent import Agent
from agentx.agent.view.agent_view import AgentView
from agentx.agent.types import (
    ActionType,
    AutonomyLevel,
    GoalStatus,
    PolicyAction,
    PolicyRule,
    RuleMetadata,
    RuleSource,
    SuccessCriteria,
)


class TestAgentLifecycle:
    def test_agent_initializes(self, agent_config):
        agent = Agent(agent_config)
        assert agent.id == "test-agent"
        assert agent.state.value == "PERCEIVING"
        assert len(agent.tool_registry.list_specs()) >= 3

    def test_perceive_returns_environment_model(self, agent_config):
        agent = Agent(agent_config)
        env = agent.perceive()
        assert len(env.sensor_readings) >= 1
        assert "filesystem" in env.sensor_readings

    def test_decide_without_rules_returns_noop(self, agent_config):
        agent = Agent(agent_config)
        decision = agent.decide()
        assert decision.confidence == 0.0

    def test_full_cycle_without_rules(self, agent_config):
        agent = Agent(agent_config)
        result = agent.run_cycle()
        assert result.decision is not None
        assert result.action_result is None  # no EXECUTE_TOOL action

    def test_full_cycle_with_rule_and_goal(self, agent_config):
        agent = Agent(agent_config)
        # Create a test file to read
        sandbox = Path(agent_config.sandbox_root)
        (sandbox / "target.txt").write_text("agent data")

        # Submit goal
        goal = agent.goal_manager.create_goal(
            "Read target file",
            success_criteria=SuccessCriteria(kind="tool_success"),
        )
        agent.submit_goal(goal)

        # Add policy rule
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

        # Run cycle
        result = agent.run_cycle()
        assert "r1" in result.decision.reasoning
        assert result.action_result is not None
        assert result.action_result.success is True
        assert result.action_result.output["content"] == "agent data"
        # Goal should be completed (tool_success criteria)
        completed_goal = agent.goal_manager.get_goal(goal.id)
        assert completed_goal is not None
        assert completed_goal.status == GoalStatus.COMPLETED

    def test_persist_and_resume(self, agent_config):
        agent = Agent(agent_config)
        # Add some state
        rule = PolicyRule(
            id="r1", condition_expr="true",
            action=PolicyAction(type=ActionType.PAUSE),
            metadata=RuleMetadata(source=RuleSource.DEFAULT),
        )
        agent.update_policy(rule)
        snapshot_id = agent.persist()
        assert snapshot_id

        # Load the snapshot
        loaded = agent._db.load_snapshot(snapshot_id)  # noqa: SLF001
        assert loaded is not None
        assert loaded.agent_id == "test-agent"
        assert len(loaded.policy_store) >= 1

    def test_get_status(self, agent_config):
        agent = Agent(agent_config)
        status = agent.get_status()
        assert status["id"] == "test-agent"
        assert status["state"] == "PERCEIVING"
        assert status["tools"] >= 3


class TestAgentController:
    def test_controller_with_console_view(self, agent_config):
        agent = Agent(agent_config)
        controller = AgentController(agent)
        view = AgentView()
        controller.set_view(view)

        status = controller.get_status()
        assert status["id"] == "test-agent"

    def test_submit_goal_via_controller(self, agent_config):
        agent = Agent(agent_config)
        controller = AgentController(agent)
        controller.set_view(AgentView())

        gid = controller.submit_goal("test objective")
        assert gid
        assert agent.goal_manager.get_goal(gid) is not None

    def test_run_cycle_via_controller(self, agent_config):
        agent = Agent(agent_config)
        controller = AgentController(agent)
        controller.set_view(AgentView())

        result = controller.run_cycle()
        assert result.decision is not None

    def test_update_policy_via_controller(self, agent_config):
        agent = Agent(agent_config)
        controller = AgentController(agent)
        controller.set_view(AgentView())

        rule = PolicyRule(
            id="r1", condition_expr="true",
            action=PolicyAction(type=ActionType.PAUSE),
            metadata=RuleMetadata(source=RuleSource.USER_DEFINED),
        )
        assert controller.update_policy(rule) is True
        assert "r1" in agent.policy_engine.rules


class TestSessionController:
    def test_save_and_load_snapshot(self, agent_config):
        agent = Agent(agent_config)
        sc = SessionController(agent)
        snapshot_id = sc.save_snapshot()
        assert snapshot_id

        loaded = sc.load_snapshot(snapshot_id)
        assert loaded is not None
        assert loaded.snapshot_id == snapshot_id


class TestToolController:
    def test_list_tools(self, agent_config):
        agent = Agent(agent_config)
        tc = ToolController(agent)
        tools = tc.list_tools()
        assert len(tools) >= 3
        tool_ids = [t.tool_id for t in tools]
        assert "filesystem" in tool_ids
        assert "rag_query" in tool_ids
        assert "session" in tool_ids

    def test_health_check(self, agent_config):
        agent = Agent(agent_config)
        tc = ToolController(agent)
        health = tc.health_check()
        assert all(health.values())

    def test_unregister_tool(self, agent_config):
        agent = Agent(agent_config)
        tc = ToolController(agent)
        assert tc.unregister_tool("rag_query") is True
        assert "rag_query" not in tc.list_tools()


class TestMultiCycleRun:
    def test_run_multiple_cycles(self, agent_config):
        agent = Agent(agent_config)
        controller = AgentController(agent)
        controller.set_view(AgentView())

        results = controller.run_cycles(3)
        assert len(results) == 3
        for r in results:
            assert r.decision is not None

    def test_memory_grows_with_cycles(self, agent_config):
        from agentx.agent.types import MemoryQuery

        agent = Agent(agent_config)
        before = len(agent.memory.retrieve(MemoryQuery(limit=1000)))
        agent.run_cycle()
        agent.run_cycle()
        after = len(agent.memory.retrieve(MemoryQuery(limit=1000)))
        assert after > before
