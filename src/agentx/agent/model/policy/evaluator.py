"""PolicyEngine — rule evaluation, priority resolution, safe add (design §7.3, §11.3).

Implements :class:`IPolicyStorePartner`.  Rules are compiled lazily on first
evaluation and cached.  Priority resolution is deterministic (design §7.3):
priority → source precedence → creation time → lexicographic id.
"""

from __future__ import annotations

import logging
from typing import Any

from agentx.agent.interfaces import IPolicyStorePartner
from agentx.agent.model.policy.conflict_resolver import ConflictResolver
from agentx.agent.model.policy.rule import CompiledCondition, ConditionCompileError
from agentx.agent.persistence.repositories_db import PolicyRepository
from agentx.agent.types import (
    ActionType,
    PolicyAction,
    PolicyContext,
    PolicyDecision,
    PolicyRule,
    RuleSource,
)

_log = logging.getLogger(__name__)

#: RuleSource precedence for tie-breaking (higher index wins).
_SOURCE_PRECEDENCE = {
    RuleSource.DEFAULT: 0,
    RuleSource.LEARNED: 1,
    RuleSource.REFLECTION_PROPOSED: 2,
    RuleSource.USER_DEFINED: 3,
}

def _noop_action() -> PolicyAction:
    """M4 (feature_015): return a fresh PAUSE action each time.

    Previously a module-level ``_NOOP`` singleton was shared across all
    no-op decisions; since ``PolicyAction`` is mutable, any caller that
    mutated ``decision.selected_action.parameters`` corrupted the global
    default.
    """
    return PolicyAction(type=ActionType.PAUSE)


class PolicyEngine(IPolicyStorePartner):
    """Evaluates policy rules against a context and selects the winning action.

    When a :class:`PolicyRepository` is supplied, rules are persisted on add and
    removed on delete (N3 — consistent with :class:`GoalManager`), so policy
    survives a process restart even without an explicit snapshot.
    """

    def __init__(
        self,
        repository: PolicyRepository | None = None,
        agent_id: str = "",
    ) -> None:
        self.rules: dict[str, PolicyRule] = {}
        self._compiled: dict[str, CompiledCondition] = {}
        self._resolver = ConflictResolver()
        self._repository = repository
        self._agent_id = agent_id

    # ----------------------------------------------------------- IPolicyStorePartner

    def add_rule(self, rule: PolicyRule) -> None:
        # fail-fast: compile at load time
        self._compile(rule)
        self.rules[rule.id] = rule
        if self._repository is not None:
            self._repository.save(self._agent_id, rule)

    def remove_rule(self, rule_id: str) -> None:
        self.rules.pop(rule_id, None)
        self._compiled.pop(rule_id, None)
        if self._repository is not None:
            self._repository.delete(rule_id)

    def clear(self) -> None:
        """Drop all rules and compiled conditions (used on session resume, N9)."""
        self.rules.clear()
        self._compiled.clear()

    def load_from_repository(self) -> list[PolicyRule]:
        """Load rules from the repository (N3). Returns the loaded rules.

        Does not re-save (mirrors ``GoalManager.load_from_repository``).
        """
        if self._repository is None:
            return []
        loaded = self._repository.load_by_agent(self._agent_id)
        for rule in loaded:
            self._compile(rule)
            self.rules[rule.id] = rule
        return loaded

    def resolve_conflicts(self) -> dict[str, Any]:
        # L1 (feature_015): previously a stub returning {}.  Now surfaces
        # detected conflicts as {"ruleA:ruleB": score} for the interface.
        conflicts = self._resolver.detect(list(self.rules.values()))
        return {f"{a}:{b}": score for (a, b), score in conflicts.items()}

    # ----------------------------------------------------------- evaluation

    def evaluate(self, context: PolicyContext) -> PolicyDecision:
        """Filter enabled rules whose condition matches; pick winner by priority."""
        candidates = [
            r for r in self.rules.values()
            if r.enabled and self._matches(r, context)
        ]
        if not candidates:
            return PolicyDecision(
                selected_action=_noop_action(),
                confidence=0.0,
                reasoning="no matching rule",
            )
        winner, alternatives = self._select_winner(candidates)
        confidence = self._confidence(winner, candidates)
        return PolicyDecision(
            selected_action=winner.action,
            confidence=confidence,
            reasoning=f"rule {winner.id} (priority {winner.priority})",
            alternatives=[a.action for a in alternatives],
        )

    # ----------------------------------------------------------- safe add (§11.3)

    def add_rule_safely(self, rule: PolicyRule) -> bool:
        """Add a rule via the safe path: compile + conflict check + complexity guard."""
        try:
            self._compile(rule)
        except ConditionCompileError as exc:
            _log.warning("rule %s rejected: %s", rule.id, exc)
            return False
        conflicts = self._resolver.detect(list(self.rules.values()) + [rule])
        for (aid, bid), score in conflicts.items():
            if rule.id in (aid, bid) and score > 0.8:
                _log.warning("rule %s rejected: conflict score %.2f", rule.id, score)
                return False
        if len(rule.action.parameters) > 10:
            _log.warning("rule %s rejected: too complex (>10 params)", rule.id)
            return False
        self.add_rule(rule)
        return True

    def revert_rule(self, rule_id: str, previous: PolicyRule | None = None) -> None:
        """Roll back a reflection-proposed rule (design §7.5).

        M6 (feature_015): if *previous* is provided, restore it instead of
        deleting the rule entirely.  Previously revert always deleted, so
        an UPDATE to an existing rule was lost on revert.
        """
        if previous is not None:
            self.add_rule(previous)
        else:
            self.remove_rule(rule_id)

    # ----------------------------------------------------------- priority resolution

    def _select_winner(
        self, candidates: list[PolicyRule]
    ) -> tuple[PolicyRule, list[PolicyRule]]:
        """Deterministic priority resolution (design §7.3)."""
        sorted_rules = sorted(
            candidates,
            key=lambda r: (
                -r.priority,
                -_SOURCE_PRECEDENCE.get(r.metadata.source, 0),
                r.metadata.created_at,
                r.id,
            ),
        )
        return sorted_rules[0], sorted_rules[1:]

    @staticmethod
    def _confidence(winner: PolicyRule, candidates: list[PolicyRule]) -> float:
        """Confidence = winner priority / 1000, boosted if uncontested."""
        base = winner.priority / 1000.0
        if len(candidates) == 1:
            return min(1.0, base + 0.2)
        # M3 (feature_015): cap contested confidence at 1.0 — a rule with
        # priority > 1000 previously produced confidence > 1.0.
        return min(1.0, base)

    # ----------------------------------------------------------- internals

    def _compile(self, rule: PolicyRule) -> CompiledCondition:
        cc = self._compiled.get(rule.id)
        if cc is None:
            cc = CompiledCondition(expression=rule.condition_expr)
            cc.compile()  # fail-fast
            self._compiled[rule.id] = cc
        return cc

    def _matches(self, rule: PolicyRule, context: PolicyContext) -> bool:
        cc = self._compiled.get(rule.id)
        if cc is None:
            try:
                cc = self._compile(rule)
            except ConditionCompileError:
                return False
        return cc.evaluate(context)
