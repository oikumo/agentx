"""AXR-03 policy acceptance regressions — durable proof of package 03.

Acceptance source: ``sandbox/consistency_enforcement/round_004_package_03_policy_acceptance.md``
§Result (user picked A — one success/failure contract): fresh-compile into a
throwaway (never touches the live cache) → complexity guard → conflict check vs
the FINAL set (same-ID old excluded) → repository save → publish rule+compiled
together. Any failure (compile, guard, conflict, save) leaves live rules, the
compiled cache, and persisted state untouched.

Probe-retired note (D4): this module retires the four observation probes in
``sandbox/consistency_enforcement/round_001_review_probes.py``
(``test_axr03_stale_and_invalid_replacements``,
``test_axr03_rejected_first_insertion_seeds_cache``,
``test_axr03_replacement_conflicts_with_itself``,
``test_axr03_failed_persistence_publishes_live_rule``). Those probes asserted
the faulty behavior and must now FAIL; the six tests below pin the fixed
contract instead.

No network: pure in-memory ``PolicyEngine`` plus an in-memory repository
double; no DB files are created.
"""

from __future__ import annotations

import pytest

from agentx.agent.model.policy.evaluator import PolicyEngine
from agentx.agent.types import (
    ActionType,
    PolicyAction,
    PolicyContext,
    PolicyRule,
)

_RULE_ID = "axr03-rule"


def _make_rule(
    rule_id: str = _RULE_ID,
    condition: str = "true",
    action_type: ActionType = ActionType.EXECUTE_TOOL,
    parameters: dict | None = None,
    priority: int = 500,
) -> PolicyRule:
    """Mirror the probe ``rule()`` helper (EXECUTE_TOOL default)."""
    return PolicyRule(
        id=rule_id,
        condition_expr=condition,
        action=PolicyAction(action_type, dict(parameters or {})),
        priority=priority,
    )


class _FailingPolicyRepository:
    """In-memory PolicyRepository double with a toggleable failing save.

    Records every ``save`` attempt; when ``fail_save`` is set, ``save`` raises
    ``OSError`` (probe pattern) without touching ``stored``.
    """

    def __init__(self, *, fail_save: bool = True) -> None:
        self.fail_save = fail_save
        self.stored: dict[str, PolicyRule] = {}
        self.save_attempts: list[str] = []

    def save(self, agent_id: str, rule: PolicyRule) -> bool:
        self.save_attempts.append(rule.id)
        if self.fail_save:
            raise OSError("synthetic save failure")
        self.stored[rule.id] = rule
        return True

    def load_by_agent(self, agent_id: str) -> list[PolicyRule]:
        return list(self.stored.values())

    def delete(self, rule_id: str) -> bool:
        self.stored.pop(rule_id, None)
        return True


def test_axr03_replacement_applies_immediately():
    """Replacing a ``true`` rule with ``false`` (same ID) stops matching NOW."""
    engine = PolicyEngine()
    assert engine.add_rule_safely(_make_rule(condition="true")) is True
    before = engine.evaluate(PolicyContext())
    assert before.selected_action.type == ActionType.EXECUTE_TOOL
    assert _RULE_ID in before.reasoning

    assert engine.add_rule_safely(_make_rule(condition="false")) is True
    assert engine.rules[_RULE_ID].condition_expr == "false"
    assert engine._compiled[_RULE_ID].expression == "false"

    after = engine.evaluate(PolicyContext())
    assert after.reasoning == "no matching rule"
    assert _RULE_ID not in after.reasoning


def test_axr03_invalid_replacement_rejected_previous_intact():
    """An invalid replacement FAILS; the previous rule stays intact/matching."""
    engine = PolicyEngine()
    assert engine.add_rule_safely(_make_rule(condition="true")) is True

    assert engine.add_rule_safely(_make_rule(condition="@@invalid@@")) is False

    assert engine.rules[_RULE_ID].condition_expr == "true"
    assert engine._compiled[_RULE_ID].expression == "true"
    decision = engine.evaluate(PolicyContext())
    assert decision.selected_action.type == ActionType.EXECUTE_TOOL
    assert _RULE_ID in decision.reasoning


def test_axr03_rejected_first_insert_inert():
    """A complexity-guard-rejected first insert seeds nothing; same-ID retry works."""
    engine = PolicyEngine()
    too_complex = _make_rule(condition="true")
    too_complex.action.parameters = {f"p{i}": i for i in range(11)}
    assert engine.add_rule_safely(too_complex) is False
    assert _RULE_ID not in engine.rules
    assert _RULE_ID not in engine._compiled

    assert engine.add_rule_safely(_make_rule(condition="false")) is True
    assert engine._compiled[_RULE_ID].expression == "false"
    decision = engine.evaluate(PolicyContext())
    # Not the stale EXECUTE_TOOL the faulty cache produced.
    assert decision.reasoning == "no matching rule"


def test_axr03_no_self_conflict_but_real_conflict_rejected():
    """Legit same-ID action swap is ACCEPTED; genuine PAUSE-vs-EXECUTE is REJECTED."""
    engine = PolicyEngine()
    assert engine.add_rule_safely(_make_rule(condition="true")) is True
    # Action-only replacement of the same ID must NOT self-conflict.
    assert (
        engine.add_rule_safely(
            _make_rule(condition="true", action_type=ActionType.PAUSE)
        )
        is True
    )
    decision = engine.evaluate(PolicyContext())
    assert decision.selected_action.type == ActionType.PAUSE
    assert _RULE_ID in decision.reasoning

    # Genuine cross-rule conflict (different IDs) is still rejected ...
    rival = PolicyEngine()
    assert (
        rival.add_rule_safely(
            _make_rule("axr03-a", condition="true", action_type=ActionType.EXECUTE_TOOL)
        )
        is True
    )
    assert (
        rival.add_rule_safely(
            _make_rule("axr03-b", condition="true", action_type=ActionType.PAUSE)
        )
        is False
    )
    assert "axr03-b" not in rival.rules
    assert "axr03-b" not in rival._compiled

    # ... and the same pair genuinely scores 1.00 on the trusted path.
    witness = PolicyEngine()
    witness.add_rule(
        _make_rule("axr03-a", condition="true", action_type=ActionType.EXECUTE_TOOL)
    )
    witness.add_rule(
        _make_rule("axr03-b", condition="true", action_type=ActionType.PAUSE)
    )
    assert witness.resolve_conflicts() == {"axr03-a:axr03-b": 1.0}


def test_axr03_save_failure_publishes_nothing():
    """Failing save raises and publishes NOTHING: live, compiled, stored intact."""
    repository = _FailingPolicyRepository(fail_save=False)
    engine = PolicyEngine(repository=repository, agent_id="axr03-agent")
    assert engine.add_rule_safely(_make_rule(condition="true")) is True
    assert set(repository.stored) == {_RULE_ID}

    repository.fail_save = True
    with pytest.raises(OSError, match="synthetic save failure"):
        engine.add_rule_safely(_make_rule(condition="false"))

    # The double recorded the attempt but persisted state is untouched.
    assert repository.save_attempts == [_RULE_ID, _RULE_ID]
    assert set(repository.stored) == {_RULE_ID}
    assert repository.stored[_RULE_ID].condition_expr == "true"
    # Live rules and compiled cache are untouched.
    assert engine.rules[_RULE_ID].condition_expr == "true"
    assert engine._compiled[_RULE_ID].expression == "true"
    decision = engine.evaluate(PolicyContext())
    assert decision.selected_action.type == ActionType.EXECUTE_TOOL
    assert _RULE_ID in decision.reasoning


def test_axr03_rollback_restores_rule_and_compiled():
    """``revert_rule`` restores BOTH the rule and its compiled expression."""
    engine = PolicyEngine()
    v1 = _make_rule(condition="true", action_type=ActionType.EXECUTE_TOOL)
    assert engine.add_rule_safely(v1) is True
    assert (
        engine.add_rule_safely(
            _make_rule(condition="false", action_type=ActionType.PAUSE)
        )
        is True
    )
    assert engine.evaluate(PolicyContext()).reasoning == "no matching rule"

    engine.revert_rule(_RULE_ID, previous=v1)

    assert engine.rules[_RULE_ID].condition_expr == "true"
    assert engine._compiled[_RULE_ID].expression == "true"
    restored = engine.evaluate(PolicyContext())
    assert restored.selected_action.type == ActionType.EXECUTE_TOOL
    assert _RULE_ID in restored.reasoning
