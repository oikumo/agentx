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
    ActionType,
    AgentConfig,
    AgentState,
    CycleResult,
    Goal,
    GoalType,
    MemoryQuery,
    PolicyAction,
    PolicyRule,
    RuleMetadata,
    RuleSource,
    SuccessCriteria,
)


class AgentController:
    """Mediates View ↔ Agent interactions."""

    def __init__(self, agent: Agent) -> None:
        self._agent = agent
        self._view: IAgentViewPartner | None = None
        # feature_011: display counter for Fast Agent's RunningModal. Not
        # persisted — resets when the controller is reconstructed. Acceptable
        # for "current run" display only.
        self._cycle_count: int = 0
        self._last_result: CycleResult | None = None

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
        # feature_011: track for get_cycle_summary() (Fast Agent display).
        self._cycle_count += 1
        self._last_result = result
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
            self._view.show_policy_editor(self._agent.list_rules())  # N14: via facade
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

    # ----------------------------------------------------------- fast agent (feature_011)

    def get_cycle_summary(self) -> dict[str, Any]:
        """Return a read-only dict bundling display data for Fast Agent's RunningModal.

        Keeps the View free of Model-type imports (``CycleResult``,
        ``PolicyDecision``, ``ActuatorResult``, ``Proposal``).  See
        ``operation_spec_001_fast_agent.md``.

        Keys: ``cycle`` (int), ``phase`` (str), ``last_tool`` (str|None),
        ``last_action`` (str), ``goal_status`` (str), ``pending_proposals`` (int).
        """
        status = self._agent.get_status()
        phase = status.get("state", "IDLE")

        last_tool: str | None = None
        last_action = "(none)"
        result = self._last_result
        if result is not None and result.decision is not None:
            action = result.decision.selected_action
            params = dict(action.parameters)
            # EXECUTE_TOOL actions carry a tool_id in their parameters.
            if action.type == ActionType.EXECUTE_TOOL:
                last_tool = params.get("tool_id")
            # Human-readable, truncated to 80 chars for the status line.
            param_str = ", ".join(f"{k}={v!r}" for k, v in params.items())
            last_action = f"{action.type.value}({param_str})"[:80]

        # Root goal status — the Fast Agent runs a single root goal.
        goal_status = "NONE"
        tree = self._agent.list_goals()
        if tree is not None and tree.root is not None:
            root_goal = tree.nodes.get(tree.root)
            if root_goal is not None:
                goal_status = root_goal.status.value

        pending = self._agent.list_pending_proposals()

        return {
            "cycle": self._cycle_count,
            "phase": phase,
            "last_tool": last_tool,
            "last_action": last_action,
            "goal_status": goal_status,
            "pending_proposals": len(pending),
        }

    # ----------------------------------------------------------- query ops (N6)
    #  The view calls these instead of reaching into the Agent's model
    #  internals (goal_manager, policy_engine, memory) directly.

    def list_rules(self) -> list[PolicyRule]:
        return self._agent.list_rules()

    def list_goals(self):
        return self._agent.list_goals()

    def query_memory(self, limit: int = 10):
        return self._agent.query_memory(MemoryQuery(limit=limit))

    def save_snapshot(self) -> str:
        return self._agent.persist()

    # ----------------------------------------------------------- reflection (N4)

    def list_pending_proposals(self):
        return self._agent.list_pending_proposals()

    def approve_proposal(self, entry_id: str, proposal_idx: int) -> bool:
        outcome = self._agent.approve_proposal(entry_id, proposal_idx)
        if self._view:
            self._view.show_message(
                f"Proposal {'applied' if outcome.status.value == 'APPLIED' else outcome.status.value}"
            )
        return outcome.status.value == "APPLIED"

    # ----------------------------------------------------------- demo (feature_010)

    def reset_state(self) -> None:
        """Clear agent state so a demo scenario can be re-seeded (operation_spec §reset_state)."""
        self._agent.clear_state()
        if self._view:
            self._view.show_status(self._agent.get_status())
            self._view.refresh_goal_tree()

    def load_demo_scenario_by_name(self, name: str) -> bool:
        """Load + apply a named demo scenario (operation_spec §load_demo_scenario_by_name).

        Clears state, seeds sandbox files, submits the scenario goal, and installs
        the scenario policy rules.  Returns ``True`` when the goal was installed.
        """
        import uuid

        from agentx.agent.demo.scenarios import get_scenario, seed_sandbox_files

        scenario = get_scenario(name)
        if scenario is None:
            if self._view:
                self._view.show_message(
                    f"Unknown demo scenario: {name!r} (use 'a' or 'b')"
                )
            return False
        try:
            self._agent.clear_state()
            seed_sandbox_files(scenario, self._agent.config.sandbox_root)
        except Exception as exc:  # noqa: BLE001 — surface to the view, do not crash
            if self._view:
                self._view.show_message(f"Demo seed failed: {exc}")
            return False

        # --- scenario goal ---
        goal_spec = scenario.goal
        goal = Goal(
            id=str(uuid.uuid4()),
            description=goal_spec.description,
            type=GoalType.USER_OBJECTIVE,
            priority=goal_spec.priority,
            success_criteria=SuccessCriteria(
                kind=goal_spec.success_kind,
                expression=goal_spec.success_expression,
                tool_id=goal_spec.success_tool_id,
            ),
        )
        self._agent.submit_goal(goal)

        # --- scenario rules (skip any that fail to compile/conflict) ---
        for rule_spec in scenario.rules:
            try:
                action_type = ActionType(rule_spec.action_type)
            except ValueError:
                continue
            rule = PolicyRule(
                id=str(uuid.uuid4()),
                condition_expr=rule_spec.condition_expr,
                action=PolicyAction(type=action_type, parameters=dict(rule_spec.parameters)),
                priority=rule_spec.priority,
                metadata=RuleMetadata(source=RuleSource.USER_DEFINED, created_by="demo"),
            )
            self._agent.update_policy(rule)

        if self._view:
            self._view.show_message(f"Demo scenario loaded: {scenario.name}")
            self._view.show_status(self._agent.get_status())
            self._view.refresh_goal_tree()
        return True

    def get_demo_scenario_info(self, name: str) -> dict[str, Any] | None:
        """Return display info for a scenario as a plain dict (View must not import Model).

        Returns ``None`` for an unknown key.  Keys: ``key``, ``name``,
        ``description``, ``files``.
        """
        from agentx.agent.demo.scenarios import get_scenario

        scenario = get_scenario(name)
        if scenario is None:
            return None
        return {
            "key": scenario.key,
            "name": scenario.name,
            "description": scenario.description,
            "files": list(scenario.files),
        }
