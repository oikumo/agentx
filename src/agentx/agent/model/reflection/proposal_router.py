"""ProposalRouter — dispatch approved proposals to owning subsystems (design §8.5).

Routing is a dispatch table — each route returns an apply/rollback pair so a
bad proposal can be reverted (feeds §7.5 rollback).
"""

from __future__ import annotations

import logging
from typing import Any, Callable

from agentx.agent.model.memory.manager import MemoryManager
from agentx.agent.model.goal.manager import GoalManager
from agentx.agent.model.policy.evaluator import PolicyEngine
from agentx.agent.model.tools.registry import ToolRegistry
from agentx.agent.types import (
    Proposal,
    ProposalOutcome,
    ProposalStatus,
    ProposalType,
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
            ProposalType.POLICY_CHANGE: self._policy.revert_rule,
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
        from agentx.agent.types import (
            ActionType,
            PolicyAction,
            PolicyRule,
            RuleMetadata,
            RuleSource,
        )
        import uuid

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
        if self._policy.add_rule_safely(rule):
            return rule_id
        raise ValueError("policy rule rejected by safe-add")

    def _apply_memory_update(self, content: dict[str, Any]) -> str:
        return self._memory.apply_update(content)

    def _apply_goal_adjustment(self, content: dict[str, Any]) -> str:
        return self._goals.apply_adjustment(content)

    def _apply_tool_config(self, content: dict[str, Any]) -> str:
        tool_id = content.get("tool_id", "")
        spec = self._tools._specs.get(tool_id)  # noqa: SLF001
        if spec is None:
            raise ValueError(f"unknown tool: {tool_id}")
        if content.get("op") == "enable":
            spec.enabled = True
        elif content.get("op") == "disable":
            spec.enabled = False
        return f"{tool_id}:{content.get('op', 'noop')}"

    def _revert_tool_config(self, token: str) -> None:
        try:
            tool_id, op = token.split(":", 1)
            spec = self._tools._specs.get(tool_id)  # noqa: SLF001
            if spec is not None:
                spec.enabled = op != "disable"
        except (ValueError, KeyError):
            pass
