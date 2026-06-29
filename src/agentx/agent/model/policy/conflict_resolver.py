"""ConflictResolver — detects overlapping rules with divergent actions (design §7.4).

Runs on every ``add_rule`` and on demand via ``resolve_conflicts()``.  It detects
two classes of conflict without executing side effects:

* Overlapping condition + divergent action — two enabled rules whose conditions
  can be simultaneously true and whose actions target the same tool/goal with
  different params.
* Direct contradiction — one rule EXECUTE_TOOL, another PAUSE for the same
  condition.

Conflicts are **reported, not silently auto-resolved**.
"""

from __future__ import annotations

from itertools import combinations
from typing import Any

from agentx.agent.types import ActionType, PolicyRule


class ConflictResolver:
    """Pairwise conflict detection over the enabled rule set."""

    def detect(self, rules: list[PolicyRule]) -> dict[tuple[str, str], float]:
        """Return conflict pairs with a 0.0-1.0 conflict_score."""
        conflicts: dict[tuple[str, str], float] = {}
        enabled = [r for r in rules if r.enabled]
        for a, b in combinations(enabled, 2):
            score = self._conflict_score(a, b)
            if score > 0:
                pair: tuple[str, str] = (min(a.id, b.id), max(a.id, b.id))
                conflicts[pair] = score
        return conflicts

    def resolve_conflicts(self) -> dict[str, PolicyRule]:
        """Surface conflicts; high-score pairs reported (no auto-delete).

        Returns an empty dict — the caller (view / reflection) decides.
        """
        return {}

    # ----------------------------------------------------------- scoring

    def _conflict_score(self, a: PolicyRule, b: PolicyRule) -> float:
        """Heuristic 0.0-1.0 overlap × divergence score."""
        overlap = self._condition_overlap(a.condition_expr, b.condition_expr)
        if overlap == 0.0:
            return 0.0
        if not self._divergent(a.action, b.action):
            return 0.0
        return overlap

    @staticmethod
    def _condition_overlap(expr_a: str, expr_b: str) -> float:
        """Estimate condition overlap from shared tokens (heuristic)."""
        if expr_a == expr_b:
            return 1.0
        tokens_a = set(expr_a.replace("(", " ( ").replace(")", " ) ").split())
        tokens_b = set(expr_b.replace("(", " ( ").replace(")", " ) ").split())
        if not tokens_a or not tokens_b:
            return 0.0
        intersection = tokens_a & tokens_b
        union = tokens_a | tokens_b
        jaccard = len(intersection) / len(union) if union else 0.0
        return jaccard

    @staticmethod
    def _divergent(action_a: Any, action_b: Any) -> bool:
        """True if two actions target the same resource with different intent."""
        # PAUSE vs EXECUTE_TOOL = direct contradiction
        if {action_a.type, action_b.type} == {ActionType.PAUSE, ActionType.EXECUTE_TOOL}:
            return True
        # same tool, different parameters
        if action_a.type == ActionType.EXECUTE_TOOL and action_b.type == ActionType.EXECUTE_TOOL:
            tool_a = action_a.parameters.get("tool_id", "")
            tool_b = action_b.parameters.get("tool_id", "")
            if tool_a == tool_b and action_a.parameters != action_b.parameters:
                return True
        # same target goal, different actions
        if action_a.target_goal and action_b.target_goal:
            if action_a.target_goal == action_b.target_goal and action_a.type != action_b.type:
                return True
        return False
