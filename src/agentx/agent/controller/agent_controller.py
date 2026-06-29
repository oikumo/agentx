"""AgentController — MVC++ Controller mediating View ↔ Agent (design §3.2, operation_spec §1).

Implements :class:`IAgentModelPartner` operations and delegates display to the
:class:`IAgentViewPartner`.  Small, focused (<300 loc) — no SQL, no direct
Model internals access beyond the :class:`IAgentModelPartner` contract.
"""

from __future__ import annotations

from typing import Any

from agentx.agent.interfaces import IAgentViewPartner
from agentx.agent.model.agent import Agent
from agentx.agent.types import (
    AgentConfig,
    AgentState,
    CycleResult,
    Goal,
    GoalType,
    PolicyRule,
    SuccessCriteria,
)


class AgentController:
    """Mediates View ↔ Agent interactions."""

    def __init__(self, agent: Agent) -> None:
        self._agent = agent
        self._view: IAgentViewPartner | None = None

    def set_view(self, view: IAgentViewPartner) -> None:
        self._view = view

    # ----------------------------------------------------------- session ops

    def start_session(self, config: AgentConfig) -> str:
        """Initialize a new Agent from AgentConfig (operation spec §1.1)."""
        agent_id = self._agent.start_session(config)
        if self._view:
            self._view.show_message(f"Session started: {agent_id}")
            self._view.show_status(self._agent.get_status())
        return agent_id

    def resume_session(self, snapshot_id: str) -> None:
        """Rebuild the Agent from a persisted snapshot (operation spec §1.2)."""
        self._agent.resume_session(snapshot_id)
        if self._view:
            self._view.show_message(f"Session resumed: {snapshot_id}")
            self._view.show_status(self._agent.get_status())

    # ----------------------------------------------------------- goal ops

    def submit_goal(
        self,
        description: str,
        goal_type: GoalType = GoalType.USER_OBJECTIVE,
        priority: int = 50,
        success_criteria: SuccessCriteria | None = None,
    ) -> str:
        """Add a user objective to the GoalTree (operation spec §1.3)."""
        import uuid

        goal = Goal(
            id=str(uuid.uuid4()),
            description=description,
            type=goal_type,
            priority=priority,
            success_criteria=success_criteria or SuccessCriteria(),
        )
        goal_id = self._agent.submit_goal(goal)
        if self._view:
            self._view.refresh_goal_tree()
            self._view.show_message(f"Goal submitted: {goal_id}")
        return goal_id

    # ----------------------------------------------------------- cycle ops

    def run_cycle(self) -> CycleResult:
        """Execute one perceive → decide → act → reflect cycle (operation spec §1.4)."""
        result = self._agent.run_cycle()
        if self._view:
            self._view.show_status(self._agent.get_status())
            if result.reflection:
                self._view.show_reflection_log([result.reflection])
        return result

    def run_cycles(self, n: int) -> list[CycleResult]:
        """Run *n* consecutive cycles."""
        return [self.run_cycle() for _ in range(n)]

    # ----------------------------------------------------------- policy ops

    def update_policy(self, rule: PolicyRule) -> bool:
        """Add or replace a policy rule via the safe path (operation spec §1.5)."""
        ok = self._agent.update_policy(rule)
        if self._view:
            self._view.show_policy_editor(list(self._agent.policy_engine.rules.values()))
            self._view.show_message(
                f"Policy rule {'added' if ok else 'rejected'}: {rule.id}"
            )
        return ok

    # ----------------------------------------------------------- status

    def get_status(self) -> dict[str, Any]:
        status = self._agent.get_status()
        if self._view:
            self._view.show_status(status)
        return status

    def get_agent(self) -> Agent:
        return self._agent
