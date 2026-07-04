"""Unit tests for Fast Agent components (feature_011).

Tests:
  - AgentController.get_cycle_summary() — before/after a cycle
  - FastAgentTUIView — virtual subclass + no-op methods
  - AgentAdapter.create_fast() — returns the right triad
"""

from __future__ import annotations

from agentx.agent.controller.agent_controller import AgentController
from agentx.agent.interfaces import IAgentViewPartner
from agentx.agent.model.agent import Agent
from agentx.agent.types import GoalType, Goal, SuccessCriteria
from agentx.agent.view.tui.fast_agent_view import FastAgentTUIView


# ============================================================================
# FastAgentTUIView
# ============================================================================


class TestFastAgentTUIView:
    def test_is_view_partner(self):
        """FastAgentTUIView must be registered as IAgentViewPartner virtual subclass."""
        view = FastAgentTUIView()
        assert isinstance(view, IAgentViewPartner)

    def test_is_subclass(self):
        assert issubclass(FastAgentTUIView, IAgentViewPartner)

    def test_all_methods_are_noops(self):
        """All IAgentViewPartner methods should be callable no-ops (return None)."""
        view = FastAgentTUIView()
        assert view.show_status({"state": "PERCEIVING"}) is None
        assert view.show_reflection_log([]) is None
        assert view.show_memory_view(None) is None
        assert view.show_policy_editor([]) is None
        assert view.refresh_goal_tree() is None
        assert view.show_message("hello") is None


# ============================================================================
# AgentController.get_cycle_summary()
# ============================================================================


class TestGetCycleSummary:
    def test_summary_before_any_cycle(self, wired_controller):
        """get_cycle_summary() returns sensible defaults before any cycle."""
        agent, controller = wired_controller
        summary = controller.get_cycle_summary()
        assert summary["cycle"] == 0
        assert summary["phase"] in {"INITIALIZING", "PERCEIVING", "IDLE"}
        assert summary["last_tool"] is None
        assert summary["last_action"] == "(none)"
        assert summary["goal_status"] == "NONE"
        assert summary["pending_proposals"] == 0

    def test_summary_after_one_cycle(self, wired_controller):
        """get_cycle_summary() reflects state after one cycle."""
        import uuid

        agent, controller = wired_controller

        # Submit a goal so the summary has a goal_status.
        goal = Goal(
            id=str(uuid.uuid4()),
            description="test goal",
            type=GoalType.USER_OBJECTIVE,
            success_criteria=SuccessCriteria(kind="manual"),
        )
        agent.submit_goal(goal)

        controller.run_cycle()

        summary = controller.get_cycle_summary()
        assert summary["cycle"] == 1
        # Phase should be one of the agent states.
        assert "phase" in summary
        assert isinstance(summary["phase"], str)
        # Goal should now be ACTIVE (submitted but not completed).
        assert summary["goal_status"] in {"ACTIVE", "PENDING"}
        assert summary["pending_proposals"] == 0

    def test_summary_cycle_count_increments(self, wired_controller):
        """Each run_cycle() increments the cycle counter."""
        agent, controller = wired_controller
        assert controller.get_cycle_summary()["cycle"] == 0
        controller.run_cycle()
        assert controller.get_cycle_summary()["cycle"] == 1
        controller.run_cycle()
        assert controller.get_cycle_summary()["cycle"] == 2
        controller.run_cycle()
        assert controller.get_cycle_summary()["cycle"] == 3


# ============================================================================
# AgentAdapter.create_fast()
# ============================================================================


class TestCreateFast:
    def test_create_fast_returns_triad(self, agent_config):
        """create_fast() returns (Agent, AgentController, FastAgentTUIScreen)."""
        from agentx.agent.adapter import AgentAdapter
        from agentx.agent.view.tui.fast_agent_screen import FastAgentTUIScreen

        agent, controller, screen = AgentAdapter.create_fast(
            agent_config, resume=False
        )
        assert isinstance(agent, Agent)
        assert isinstance(controller, AgentController)
        assert isinstance(screen, FastAgentTUIScreen)
        # The controller should have a view wired (FastAgentTUIView).
        assert controller._view is not None
        assert isinstance(controller._view, IAgentViewPartner)

    def test_create_fast_wires_noop_view(self, agent_config):
        """create_fast() wires FastAgentTUIView as the controller's partner."""
        from agentx.agent.adapter import AgentAdapter

        _agent, controller, _screen = AgentAdapter.create_fast(
            agent_config, resume=False
        )
        # The view should be a FastAgentTUIView (no-op partner).
        assert isinstance(controller._view, FastAgentTUIView)

    def test_create_fast_screen_has_controller(self, agent_config):
        """The screen created by create_fast() holds the controller."""
        from agentx.agent.adapter import AgentAdapter

        _agent, controller, screen = AgentAdapter.create_fast(
            agent_config, resume=False
        )
        assert screen._controller is controller
