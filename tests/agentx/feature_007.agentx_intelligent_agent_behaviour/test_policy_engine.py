"""Unit tests for PolicyEngine — condition DSL, evaluation, priority, conflicts."""

from __future__ import annotations

import pytest

from agentx.agent.model.policy.conflict_resolver import ConflictResolver
from agentx.agent.model.policy.evaluator import PolicyEngine
from agentx.agent.model.policy.rule import (
    CompiledCondition,
    ConditionCompileError,
    compile_condition,
    ConditionEvaluator,
)
from agentx.agent.types import (
    ActionType,
    AgentState,
    AutonomyLevel,
    EnvironmentModel,
    Goal,
    GoalStatus,
    PolicyAction,
    PolicyContext,
    PolicyDecision,
    PolicyRule,
    RuleMetadata,
    RuleSource,
)


# ---------------------------------------------------------------------------
# Condition DSL tests
# ---------------------------------------------------------------------------


class TestConditionDSL:
    def test_compile_true(self):
        ast = compile_condition("true")
        ctx = PolicyContext()
        assert ConditionEvaluator().evaluate(ast, ctx) is True

    def test_compile_false(self):
        ast = compile_condition("false")
        ctx = PolicyContext()
        assert ConditionEvaluator().evaluate(ast, ctx) is False

    def test_and(self):
        cc = CompiledCondition(expression="true AND false")
        assert cc.evaluate(PolicyContext()) is False

    def test_or(self):
        cc = CompiledCondition(expression="true OR false")
        assert cc.evaluate(PolicyContext()) is True

    def test_not(self):
        cc = CompiledCondition(expression="NOT false")
        assert cc.evaluate(PolicyContext()) is True

    def test_comparison(self):
        cc = CompiledCondition(expression="environment.memory_pressure < 0.8")
        ctx = PolicyContext(environment=EnvironmentModel(confidence=0.5))
        assert cc.evaluate(ctx) is True  # memory_pressure defaults to 0.0

    def test_goal_active(self):
        cc = CompiledCondition(expression="goal.active")
        goal = Goal(id="g1", description="test", status=GoalStatus.ACTIVE)
        ctx = PolicyContext(current_goal=goal)
        assert cc.evaluate(ctx) is True

    def test_goal_active_no_goal(self):
        cc = CompiledCondition(expression="goal.active")
        ctx = PolicyContext(current_goal=None)
        assert cc.evaluate(ctx) is False

    def test_agent_state(self):
        cc = CompiledCondition(expression="agent.state == 'PERCEIVING'")
        ctx = PolicyContext(agent_state=AgentState.PERCEIVING)
        assert cc.evaluate(ctx) is True

    def test_parens_grouping(self):
        cc = CompiledCondition(expression="(true OR false) AND true")
        assert cc.evaluate(PolicyContext()) is True

    def test_compile_error_on_garbage(self):
        with pytest.raises(ConditionCompileError):
            compile_condition("@#$%")

    def test_compiled_condition_evaluate_swallows_errors(self):
        cc = CompiledCondition(expression="unknown.thing.bad")
        # Should return False, not raise
        assert cc.evaluate(PolicyContext()) is False

    def test_has_observation_function(self):
        from agentx.agent.types import MemoryEntry, MemoryMetadata, MemorySource

        cc = CompiledCondition(expression="has_observation('error')")
        ctx = PolicyContext()
        ctx.memory = [
            MemoryEntry(id="m1", content={"msg": "error occurred"}, metadata=MemoryMetadata(source=MemorySource.PERCEPTION)),
        ]
        assert cc.evaluate(ctx) is True

    def test_memory_contains_function(self):
        from agentx.agent.types import MemoryEntry, MemoryMetadata, MemorySource

        cc = CompiledCondition(expression="memory_contains('hello')")
        ctx = PolicyContext()
        ctx.memory = [
            MemoryEntry(id="m1", content={"text": "hello world"}, metadata=MemoryMetadata(source=MemorySource.USER_INPUT)),
        ]
        assert cc.evaluate(ctx) is True


# ---------------------------------------------------------------------------
# PolicyEngine tests
# ---------------------------------------------------------------------------


def _make_rule(rid, condition="true", priority=500, source=RuleSource.DEFAULT, action_type=ActionType.PAUSE):
    return PolicyRule(
        id=rid,
        condition_expr=condition,
        action=PolicyAction(type=action_type),
        priority=priority,
        metadata=RuleMetadata(source=source),
    )


class TestPolicyEngine:
    def test_add_and_evaluate(self):
        engine = PolicyEngine()
        engine.add_rule(_make_rule("r1"))
        decision = engine.evaluate(PolicyContext())
        assert decision.selected_action.type == ActionType.PAUSE
        assert "r1" in decision.reasoning

    def test_no_matching_rule_returns_noop(self):
        engine = PolicyEngine()
        decision = engine.evaluate(PolicyContext())
        assert decision.confidence == 0.0
        assert "no matching rule" in decision.reasoning

    def test_priority_resolution(self):
        engine = PolicyEngine()
        engine.add_rule(_make_rule("low", priority=100))
        engine.add_rule(_make_rule("high", priority=900))
        decision = engine.evaluate(PolicyContext())
        assert "high" in decision.reasoning

    def test_source_precedence_tiebreak(self):
        engine = PolicyEngine()
        engine.add_rule(_make_rule("default", priority=500, source=RuleSource.DEFAULT))
        engine.add_rule(_make_rule("user", priority=500, source=RuleSource.USER_DEFINED))
        decision = engine.evaluate(PolicyContext())
        assert "user" in decision.reasoning

    def test_disabled_rule_skipped(self):
        engine = PolicyEngine()
        rule = _make_rule("r1", priority=900)
        rule.enabled = False
        engine.add_rule(rule)
        engine.add_rule(_make_rule("r2", priority=100))
        decision = engine.evaluate(PolicyContext())
        assert "r2" in decision.reasoning

    def test_remove_rule(self):
        engine = PolicyEngine()
        engine.add_rule(_make_rule("r1"))
        engine.remove_rule("r1")
        assert "r1" not in engine.rules

    def test_add_rule_safely_rejects_compile_error(self):
        engine = PolicyEngine()
        bad = _make_rule("bad", condition="@#$")
        assert engine.add_rule_safely(bad) is False
        assert "bad" not in engine.rules

    def test_add_rule_safely_rejects_too_complex(self):
        engine = PolicyEngine()
        complex_rule = _make_rule("complex")
        complex_rule.action.parameters = {f"k{i}": i for i in range(15)}
        assert engine.add_rule_safely(complex_rule) is False

    def test_add_rule_safely_accepts_valid(self):
        engine = PolicyEngine()
        assert engine.add_rule_safely(_make_rule("ok")) is True

    def test_revert_rule(self):
        engine = PolicyEngine()
        engine.add_rule(_make_rule("r1"))
        engine.revert_rule("r1")
        assert "r1" not in engine.rules


# ---------------------------------------------------------------------------
# ConflictResolver tests
# ---------------------------------------------------------------------------


class TestConflictResolver:
    def test_no_conflicts(self):
        resolver = ConflictResolver()
        rules = [_make_rule("r1"), _make_rule("r2", condition="false")]
        conflicts = resolver.detect(rules)
        assert len(conflicts) == 0

    def test_identical_conditions_detected(self):
        resolver = ConflictResolver()
        r1 = _make_rule("r1", condition="true", action_type=ActionType.EXECUTE_TOOL)
        r1.action.parameters = {"tool_id": "fs", "action": "read"}
        r2 = _make_rule("r2", condition="true", action_type=ActionType.EXECUTE_TOOL)
        r2.action.parameters = {"tool_id": "fs", "action": "delete"}
        conflicts = resolver.detect([r1, r2])
        assert len(conflicts) >= 1

    def test_pause_vs_execute_detected(self):
        resolver = ConflictResolver()
        r1 = _make_rule("r1", condition="true", action_type=ActionType.EXECUTE_TOOL)
        r2 = _make_rule("r2", condition="true", action_type=ActionType.PAUSE)
        conflicts = resolver.detect([r1, r2])
        assert len(conflicts) >= 1

    def test_disabled_rules_ignored(self):
        resolver = ConflictResolver()
        r1 = _make_rule("r1", condition="true", action_type=ActionType.PAUSE)
        r1.enabled = False
        r2 = _make_rule("r2", condition="true", action_type=ActionType.EXECUTE_TOOL)
        conflicts = resolver.detect([r1, r2])
        assert len(conflicts) == 0
