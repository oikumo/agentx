"""Unit tests for GoalManager."""

from __future__ import annotations

from agentx.agent.model.goal.manager import GoalManager
from agentx.agent.types import (
    Goal,
    GoalConfig,
    GoalStatus,
    GoalTree,
    GoalType,
    SuccessCriteria,
)


class TestGoalManager:
    def test_add_goal(self):
        mgr = GoalManager(config=GoalConfig())
        goal = mgr.create_goal("test objective")
        gid = mgr.add_goal(goal)
        assert gid == goal.id
        assert mgr.get_goal(gid) is goal

    def test_first_goal_auto_activates(self):
        mgr = GoalManager(config=GoalConfig(max_active_goals=5))
        g = mgr.create_goal("first")
        mgr.add_goal(g)
        assert g.status == GoalStatus.ACTIVE

    def test_update_status_completes_and_promotes(self):
        mgr = GoalManager(config=GoalConfig())
        g1 = mgr.create_goal("first")
        g2 = mgr.create_goal("second")
        mgr.add_goal(g1)
        mgr.add_goal(g2)
        # g1 is active, g2 is pending
        assert g1.status == GoalStatus.ACTIVE
        assert g2.status == GoalStatus.PENDING
        # complete g1 → g2 promoted
        mgr.update_status(g1.id, GoalStatus.COMPLETED)
        assert g2.status == GoalStatus.ACTIVE

    def test_update_status_failed(self):
        mgr = GoalManager()
        g = mgr.create_goal("doomed")
        mgr.add_goal(g)
        mgr.update_status(g.id, GoalStatus.FAILED)
        assert g.status == GoalStatus.FAILED

    def test_active_goal(self):
        mgr = GoalManager()
        g = mgr.create_goal("active one")
        mgr.add_goal(g)
        active = mgr.active_goal()
        assert active is not None
        assert active.id == g.id

    def test_no_active_goal(self):
        mgr = GoalManager()
        assert mgr.active_goal() is None

    def test_get_tree(self):
        mgr = GoalManager()
        g = mgr.create_goal("root")
        mgr.add_goal(g)
        tree = mgr.get_tree()
        assert isinstance(tree, GoalTree)
        assert tree.root == g.id

    def test_apply_and_revert_adjustment(self):
        mgr = GoalManager()
        g = mgr.create_goal("adjust me", priority=50)
        mgr.add_goal(g)
        token = mgr.apply_adjustment({"goal_id": g.id, "priority": 90})
        assert g.priority == 90
        mgr.revert_adjustment(token)
        assert g.priority == 50
