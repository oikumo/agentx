"""AXR-10 durable regression: single-active-goal invariant (agentx_1_0_0 package 6).

Acceptance (round_007, from round_001 §AXR-10 Regression check):
completing/failing/abandoning a PENDING goal leaves the active goal as the
only active one; completing the active goal promotes exactly one
highest-priority pending goal (two candidates inserted opposite to priority
order); repeating a terminal update promotes nothing; insertion of an
already-ACTIVE goal, explicit activation, rollback, and repository
restoration all preserve the single-active invariant.

Replaces sandbox/consistency_enforcement/round_001_review_probes.py::
test_axr10_pending_terminal_update_promotes_second_active (observation probe
retired per D4 — never gated in CI).
"""

from __future__ import annotations

import sqlite3

from agentx.agent.model.goal.manager import GoalManager
from agentx.agent.types import (
    Goal,
    GoalStatus,
    GoalType,
    SuccessCriteria,
)


def _actives(manager):
    return [
        g.description
        for g in manager.get_tree().nodes.values()
        if g.status == GoalStatus.ACTIVE
    ]


class TestAxr10SingleActiveInvariant:
    def test_pending_terminal_update_leaves_sole_active(self):
        for status in (GoalStatus.COMPLETED, GoalStatus.FAILED, GoalStatus.ABANDONED):
            manager = GoalManager()
            goals = [manager.create_goal(n) for n in ("A", "B", "C")]
            for goal in goals:
                manager.add_goal(goal)
            manager.update_status(goals[1].id, status)  # terminate PENDING B
            assert _actives(manager) == ["A"], status

    def test_repeated_terminal_updates_are_idempotent(self):
        manager = GoalManager()
        goals = [manager.create_goal(n) for n in ("A", "B", "C", "D")]
        for goal in goals:
            manager.add_goal(goal)
        manager.update_status(goals[1].id, GoalStatus.ABANDONED)
        manager.update_status(goals[1].id, GoalStatus.ABANDONED)  # repeat
        manager.update_status(goals[1].id, GoalStatus.COMPLETED)  # another terminal
        assert _actives(manager) == ["A"]

    def test_active_completion_promotes_exactly_one_highest_priority(self):
        manager = GoalManager()
        a = manager.create_goal("A", priority=1)
        manager.add_goal(a)  # A active
        low = manager.create_goal("low", priority=10)
        high = manager.create_goal("high", priority=90)
        manager.add_goal(low)  # inserted opposite to priority order
        manager.add_goal(high)
        manager.update_status(a.id, GoalStatus.COMPLETED)
        assert _actives(manager) == ["high"]  # exactly one, priority-ordered

    def test_already_active_insertion_is_demoted(self):
        manager = GoalManager()
        a = manager.create_goal("A")
        manager.add_goal(a)
        raw = Goal(
            id="raw-active",
            description="raw",
            type=GoalType.USER_OBJECTIVE,
            priority=1,
            status=GoalStatus.ACTIVE,
            success_criteria=SuccessCriteria(),
        )
        manager.add_goal(raw)
        assert raw.status == GoalStatus.PENDING  # insertion lands as PENDING
        assert _actives(manager) == ["A"]

    def test_explicit_activation_is_a_focus_switch(self):
        manager = GoalManager()
        a = manager.create_goal("A")
        b = manager.create_goal("B")
        manager.add_goal(a)
        manager.add_goal(b)
        manager.update_status(b.id, GoalStatus.ACTIVE)
        assert _actives(manager) == ["B"]  # requested goal wins
        assert manager.get_goal(a.id).status == GoalStatus.PENDING  # not lost

    def test_revert_restores_single_active(self):
        manager = GoalManager()
        a = manager.create_goal("A")
        b = manager.create_goal("B")
        c = manager.create_goal("C")
        for g in (a, b, c):
            manager.add_goal(g)
        token = manager.apply_adjustment({"goal_id": a.id, "status": "COMPLETED"})
        assert _actives(manager) == ["B"]  # A completed → B promoted
        manager.update_status(c.id, GoalStatus.ACTIVE)  # interim focus switch
        assert _actives(manager) == ["C"]
        manager.revert_adjustment(token)
        assert _actives(manager) == ["A"]  # restored goal preferred, single active

    def test_repository_load_heals_double_active_rows(self, tmp_path):
        from agentx.agent.persistence.repositories_db import GoalRepository
        from agentx.agent.persistence.schema_db import TableGoals

        db = str(tmp_path / "agent_session.db")
        with sqlite3.connect(db) as conn:
            conn.execute(TableGoals.TABLE_QUERY)
            conn.commit()
        repo = GoalRepository(db)

        # simulate pre-fix corruption: two ACTIVE rows persisted
        manager = GoalManager(repository=repo, agent_id="heal")
        one = manager.create_goal("one")
        one.status = GoalStatus.ACTIVE
        repo.save("heal", one)
        two = manager.create_goal("two")
        two.status = GoalStatus.ACTIVE
        repo.save("heal", two)

        manager.load_from_repository()
        assert _actives(manager) == ["one"]  # first active kept, surplus demoted

        # healing persisted: a fresh manager loading the same rows converges
        second = GoalManager(repository=repo, agent_id="heal")
        second.load_from_repository()
        assert _actives(second) == ["one"]
