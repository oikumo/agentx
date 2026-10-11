"""Unit tests for agent domain types (data dictionary realization)."""

from __future__ import annotations

from agentx.agent.types import (
    ActionType,
    AgentState,
    AutonomyLevel,
    Goal,
    GoalStatus,
    GoalTree,
    GoalType,
    MemorySource,
    MemoryTier,
    PolicyAction,
    PolicyRule,
    ProposalType,
    RuleSource,
    SuccessCriteria,
    ToolKind,
)


class TestEnums:
    def test_agent_state_values(self):
        assert AgentState.PERCEIVING.value == "PERCEIVING"
        assert AgentState.TERMINATED.value == "TERMINATED"

    def test_autonomy_levels(self):
        assert AutonomyLevel.FULLY_AUTONOMOUS.value == "FULLY_AUTONOMOUS"
        assert AutonomyLevel.SUPERVISED.value == "SUPERVISED"

    def test_action_types(self):
        assert ActionType.EXECUTE_TOOL.value == "EXECUTE_TOOL"
        assert ActionType.PAUSE.value == "PAUSE"

    def test_memory_tiers(self):
        assert MemoryTier.VOLATILE.value == "VOLATILE"
        assert MemoryTier.PERSISTENT.value == "PERSISTENT"

    def test_proposal_types(self):
        assert ProposalType.POLICY_CHANGE.value == "POLICY_CHANGE"
        assert ProposalType.TOOL_CONFIGURATION.value == "TOOL_CONFIGURATION"

    def test_tool_kinds(self):
        assert ToolKind.SENSOR.value == "sensor"
        assert ToolKind.HYBRID.value == "hybrid"


class TestGoalTree:
    def test_add_root_goal(self):
        tree = GoalTree()
        goal = Goal(id="g1", description="root", type=GoalType.USER_OBJECTIVE)
        tree.add(goal)
        assert tree.root == "g1"
        assert tree.get("g1") is goal

    def test_add_child_goal(self):
        tree = GoalTree()
        root = Goal(id="g1", description="root")
        child = Goal(id="g2", description="child", parent="g1")
        tree.add(root)
        tree.add(child)
        assert "g2" in tree.nodes["g1"].children
        assert tree.get_path("g2") == ["g1", "g2"]

    def test_get_descendants(self):
        tree = GoalTree()
        tree.add(Goal(id="g1", description="root"))
        tree.add(Goal(id="g2", description="c1", parent="g1"))
        tree.add(Goal(id="g3", description="c2", parent="g1"))
        tree.add(Goal(id="g4", description="gc1", parent="g2"))
        assert set(tree.get_descendants("g1")) == {"g2", "g3", "g4"}

    def test_get_missing_goal(self):
        tree = GoalTree()
        assert tree.get("nonexistent") is None


class TestPolicyRule:
    def test_default_values(self):
        rule = PolicyRule(
            id="r1",
            condition_expr="true",
            action=PolicyAction(type=ActionType.PAUSE),
        )
        assert rule.priority == 500
        assert rule.enabled is True
        assert rule.metadata.source == RuleSource.DEFAULT

    def test_goal_active_property(self):
        goal = Goal(id="g1", description="test", status=GoalStatus.ACTIVE)
        assert goal.active is True
        goal.status = GoalStatus.PENDING
        assert goal.active is False

    def test_goal_is_blocked(self):
        goal = Goal(id="g1", description="test", status=GoalStatus.BLOCKED)
        assert goal.is_blocked is True
