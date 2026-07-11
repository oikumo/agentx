"""ProposalRouter — dispatch approved proposals to owning subsystems (design §8.5).

Routing is a dispatch table — each route returns an apply/rollback pair so a
bad proposal can be reverted (feeds §7.5 rollback).
"""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any, Callable

from agentx.agent.model.memory.manager import MemoryManager
from agentx.agent.model.goal.manager import GoalManager
from agentx.agent.model.policy.evaluator import PolicyEngine
from agentx.agent.model.tools.registry import ToolRegistry
from agentx.agent.types import (
    ActionType,
    PolicyAction,
    PolicyRule,
    Proposal,
    ProposalOutcome,
    ProposalStatus,
    ProposalType,
    RuleMetadata,
    RuleSource,
)

_log = logging.getLogger(__name__)


class ProposalRouter:
    """Routes proposals by type to the owning subsystem."""

    def __init__(
        self,
        policy: PolicyEngine,
        memory: MemoryManager,
        goals: GoalManager,
        tools: ToolRegistry,
    ) -> None:
        self._policy = policy
        self._memory = memory
        self._goals = goals
        self._tools = tools
        self._routes: dict[ProposalType, Callable[[dict[str, Any]], str]] = {
            ProposalType.POLICY_CHANGE: self._apply_policy_change,
            ProposalType.MEMORY_UPDATE: self._apply_memory_update,
            ProposalType.GOAL_ADJUSTMENT: self._apply_goal_adjustment,
            ProposalType.TOOL_CONFIGURATION: self._apply_tool_config,
        }
        self._reverters: dict[ProposalType, Callable[[str], None]] = {
            ProposalType.POLICY_CHANGE: self._revert_policy_change,
            ProposalType.MEMORY_UPDATE: self._memory.revert_update,
            ProposalType.GOAL_ADJUSTMENT: self._goals.revert_adjustment,
            ProposalType.TOOL_CONFIGURATION: self._revert_tool_config,
        }

    def route(self, proposal: Proposal) -> ProposalOutcome:
        """Apply an approved proposal; return outcome with rollback token."""
        apply_fn = self._routes.get(proposal.type)
        if apply_fn is None:
            return ProposalOutcome(status=ProposalStatus.REJECTED, reason="no route")
        try:
            token = apply_fn(proposal.content)
            proposal.status = ProposalStatus.APPLIED
            return ProposalOutcome(status=ProposalStatus.APPLIED, token=token)
        except Exception as exc:  # noqa: BLE001 — non-fatal
            _log.warning("proposal routing failed: %s", exc)
            proposal.status = ProposalStatus.REJECTED
            return ProposalOutcome(status=ProposalStatus.REJECTED, reason=str(exc))

    def revert(self, proposal_type: ProposalType, token: str) -> None:
        """Roll back a previously applied proposal."""
        reverter = self._reverters.get(proposal_type)
        if reverter and token:
            try:
                reverter(token)
            except Exception as exc:  # noqa: BLE001
                _log.warning("proposal revert failed: %s", exc)

    # ----------------------------------------------------------- route impls

    def _apply_policy_change(self, content: dict[str, Any]) -> str:
        rule_id = content.get("id", str(uuid.uuid4()))
        action_type = ActionType(content.get("action_type", ActionType.PAUSE.value))
        rule = PolicyRule(
            id=rule_id,
            condition_expr=content.get("condition", "true"),
            action=PolicyAction(
                type=action_type,
                parameters=content.get("parameters", {}),
                target_goal=content.get("target_goal"),
            ),
            priority=int(content.get("priority", 500)),
            enabled=bool(content.get("enabled", True)),
            metadata=RuleMetadata(
                source=RuleSource.REFLECTION_PROPOSED,
                created_by=f"reflection:{rule_id}",
            ),
        )
        # M6 (feature_015): capture the previous rule so revert can restore
        # it instead of deleting.  The token is "rule_id:{json of previous}".
        existing = self._policy.rules.get(rule_id)
        if self._policy.add_rule_safely(rule):
            prev_json = json.dumps(_rule_to_dict(existing)) if existing else ""
            return f"{rule_id}:{prev_json}"
        raise ValueError("policy rule rejected by safe-add")

    def _revert_policy_change(self, token: str) -> None:
        """M6 (feature_015): restore the previous rule (or delete if none)."""
        try:
            sep = token.index(":")
            rule_id = token[:sep]
            prev_json = token[sep + 1:]
        except ValueError:
            rule_id = token
            prev_json = ""
        if prev_json:
            try:
                prev_data = json.loads(prev_json)
                previous = _dict_to_rule(prev_data)
                self._policy.revert_rule(rule_id, previous=previous)
                return
            except (json.JSONDecodeError, KeyError, ValueError, TypeError):
                _log.warning("policy revert: failed to decode previous rule from token")
        self._policy.revert_rule(rule_id)

    def _apply_memory_update(self, content: dict[str, Any]) -> str:
        return self._memory.apply_update(content)

    def _apply_goal_adjustment(self, content: dict[str, Any]) -> str:
        return self._goals.apply_adjustment(content)

    def _apply_tool_config(self, content: dict[str, Any]) -> str:
        tool_id = content.get("tool_id", "")
        op = content.get("op", "noop")
        # M6: use the public registry API instead of reaching into _specs.
        if op == "enable":
            if not self._tools.set_tool_enabled(tool_id, True):
                raise ValueError(f"unknown tool: {tool_id}")
        elif op == "disable":
            if not self._tools.set_tool_enabled(tool_id, False):
                raise ValueError(f"unknown tool: {tool_id}")
        return f"{tool_id}:{op}"

    def _revert_tool_config(self, token: str) -> None:
        try:
            tool_id, op = token.split(":", 1)
            # revert: undo the applied enable/disable
            self._tools.set_tool_enabled(tool_id, op == "disable")
        except (ValueError, KeyError):
            pass


# ---------------------------------------------------------------------------
# M6 (feature_015): rule serialisation helpers for policy revert.
# ---------------------------------------------------------------------------


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
