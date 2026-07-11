"""GoalManager — goal tree management (design §4, data dictionary §Goal Management).

Implements :class:`IGoalManager`.  This is the stub that feature_001 (Session
Objectives driven by Petri Net) will swap in at runtime — the agent facade
depends on the :class:`IGoalManager` abstraction, not this concrete class.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from agentx.agent.interfaces import IGoalManager
from agentx.agent.persistence.repositories_db import GoalRepository
from agentx.agent.types import (
    Goal,
    GoalConfig,
    GoalStatus,
    GoalTree,
    GoalType,
    SuccessCriteria,
)

_log = logging.getLogger(__name__)


class GoalManager(IGoalManager):
    """AND/OR goal-tree manager with priority-based activation."""

    def __init__(
        self,
        config: GoalConfig | None = None,
        repository: GoalRepository | None = None,
        agent_id: str = "",
    ) -> None:
        self._config = config or GoalConfig()
        self._tree = GoalTree()
        self._repository = repository
        self._agent_id = agent_id

    # ----------------------------------------------------------- IGoalManager

    def add_goal(self, goal: Goal) -> str:
        self._tree.add(goal)
        # Single-active model: activate only when no goal is currently active.
        # (m4: the previous ``len(active) < max_active_goals`` clause was dead
        # — ``active`` is empty here, so the bound was always satisfied.)
        active = [g for g in self._tree.nodes.values() if g.status == GoalStatus.ACTIVE]
        if not active:
            goal.status = GoalStatus.ACTIVE
        if self._repository is not None:
            self._repository.save(self._agent_id, goal)
        return goal.id

    def get_goal(self, goal_id: str) -> Goal | None:
        return self._tree.get(goal_id)

    def get_tree(self) -> GoalTree:
        return self._tree

    def clear(self) -> None:
        """Reset the goal tree to empty (feature_010: demo re-seed support).

        Only in-memory state is cleared; persisted goal rows in the repository
        are not deleted, so a saved snapshot is unaffected.
        """
        self._tree = GoalTree()

    def update_status(self, goal_id: str, status: Any) -> None:
        goal = self._tree.get(goal_id)
        if goal is None:
            return
        if isinstance(status, str):
            try:
                status = GoalStatus(status)
            except ValueError:
                # L9 (feature_015): catch invalid status strings instead of
                # crashing the entire goal manager.
                _log.warning("invalid goal status: %s", status)
                return
        goal.status = status
        goal.updated_at = datetime.now(timezone.utc)
        if self._repository is not None:
            self._repository.save(self._agent_id, goal)
        # promote next pending goal if this one completed/failed/abandoned
        if status in {GoalStatus.COMPLETED, GoalStatus.FAILED, GoalStatus.ABANDONED}:
            self._promote_next(goal_id)

    # ----------------------------------------------------------- helpers

    def _promote_next(self, completed_id: str) -> None:
        # H1 (feature_015): promote the highest-priority pending goal, not
        # the first-inserted one.  The class docstring promises "priority-
        # based activation" — dict iteration order was being used instead.
        pending = [g for g in self._tree.nodes.values() if g.status == GoalStatus.PENDING]
        if not pending:
            return
        goal = max(pending, key=lambda g: g.priority)
        goal.status = GoalStatus.ACTIVE
        goal.updated_at = datetime.now(timezone.utc)
        if self._repository is not None:
            self._repository.save(self._agent_id, goal)

    def create_goal(
        self,
        description: str,
        goal_type: GoalType = GoalType.USER_OBJECTIVE,
        parent: str | None = None,
        priority: int | None = None,
        success_criteria: SuccessCriteria | None = None,
    ) -> Goal:
        return Goal(
            id=str(uuid.uuid4()),
            description=description,
            type=goal_type,
            parent=parent,
            priority=priority if priority is not None else self._config.default_priority,
            success_criteria=success_criteria or SuccessCriteria(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    def active_goal(self) -> Goal | None:
        for goal in self._tree.nodes.values():
            if goal.status == GoalStatus.ACTIVE:
                return goal
        return None

    def apply_adjustment(self, content: dict[str, Any]) -> str:
        """Apply a reflection GOAL_ADJUSTMENT proposal; returns rollback token."""
        goal_id = content.get("goal_id", "")
        goal = self._tree.get(goal_id)
        if goal is None:
            return ""
        old_priority = goal.priority
        old_status = goal.status
        # M5 (feature_015): track if update_status promotes another goal so
        # revert_adjustment can undo the side-effect.
        promoted_id = ""
        if "priority" in content:
            goal.priority = int(content["priority"])
        if "status" in content:
            old_active = self.active_goal()
            self.update_status(goal_id, content["status"])
            new_active = self.active_goal()
            if (
                new_active is not None
                and new_active.id != goal_id
                and (old_active is None or old_active.id != new_active.id)
            ):
                promoted_id = new_active.id
        return f"{goal_id}:{old_priority}:{old_status.value}:{promoted_id}"

    def revert_adjustment(self, token: str) -> None:
        """Roll back a previously applied goal adjustment.

        M5 (feature_015): also demotes a goal that was promoted as a side-
        effect of the original adjustment.
        """
        try:
            parts = token.split(":")
            goal_id, old_prio, old_status = parts[0], parts[1], parts[2]
            promoted_id = parts[3] if len(parts) > 3 else ""
            goal = self._tree.get(goal_id)
            if goal is not None:
                goal.priority = int(old_prio)
                goal.status = GoalStatus(old_status)
            # M5: demote the side-effected promotion back to PENDING.
            if promoted_id:
                promoted = self._tree.get(promoted_id)
                if promoted is not None and promoted.status == GoalStatus.ACTIVE:
                    promoted.status = GoalStatus.PENDING
                    promoted.updated_at = datetime.now(timezone.utc)
        except (ValueError, KeyError):
            pass

    def load_from_repository(self, root_id: str | None = None) -> None:
        if self._repository is None:
            return
        self._tree = self._repository.load_tree(self._agent_id)
        # honour the persisted root if provided and valid (N8: otherwise the
        # root drifts to whichever row SQLite returns first, since load_tree
        # sets root to the first-inserted goal).
        if root_id and root_id in self._tree.nodes:
            self._tree.root = root_id
