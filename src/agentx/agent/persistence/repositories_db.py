"""Repositories — thin DP-layer adapters mapping dataclasses ↔ sqlite rows.

Each repository owns the SQL for its aggregate and returns plain dataclasses /
dicts to the Model layer.  No SQL leaks outside this package (MVC++).
"""

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime, timezone
from typing import Any

from agentx.agent.persistence.schema_db import (
    TableGoals,
    TableMemoryEntries,
    TablePolicyRules,
    TableReflectionEntries,
)
from agentx.agent.types import (
    ActionType,
    Critique,
    DecisionTrace,
    Goal,
    GoalStatus,
    GoalTree,
    GoalType,
    MemoryEntry,
    MemoryMetadata,
    MemorySource,
    MemoryTier,
    PolicyAction,
    PolicyRule,
    Proposal,
    ProposalStatus,
    ProposalType,
    ReflectionEntry,
    RuleMetadata,
    RuleSource,
    SuccessCriteria,
)

_log = logging.getLogger(__name__)


class MemoryRepository:
    """CRUD for :class:`MemoryEntry` rows."""

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    def save(self, agent_id: str, entry: MemoryEntry) -> bool:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                TableMemoryEntries.INSERT,
                (
                    entry.id,
                    agent_id,
                    entry.tier.value,
                    entry.metadata.source.value,
                    json.dumps(entry.content, default=_json_default),
                    json.dumps(entry.metadata.tags),
                    entry.metadata.importance,
                    _to_iso(entry.metadata.created_at),
                    _to_iso(entry.metadata.last_accessed),
                    entry.metadata.access_count,
                ),
            )
            conn.commit()
        return True

    def load_by_agent(self, agent_id: str, tier: MemoryTier | None = None) -> list[MemoryEntry]:
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            if tier is not None:
                rows = conn.execute(
                    TableMemoryEntries.SELECT_BY_AGENT_TIER,
                    (agent_id, tier.value),
                ).fetchall()
            else:
                rows = conn.execute(
                    TableMemoryEntries.SELECT_BY_AGENT, (agent_id,)
                ).fetchall()
        # M12 (feature_015): skip corrupt rows instead of crashing.
        return [e for e in (_row_to_memory_entry(r) for r in rows) if e is not None]

    def delete(self, entry_id: str) -> bool:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(TableMemoryEntries.DELETE_BY_ID, (entry_id,))
            conn.commit()
        return True


class PolicyRepository:
    """CRUD for :class:`PolicyRule` rows."""

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    def save(self, agent_id: str, rule: PolicyRule) -> bool:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                TablePolicyRules.INSERT,
                (
                    rule.id,
                    agent_id,
                    rule.condition_expr,
                    json.dumps(_action_to_dict(rule.action), default=_json_default),
                    rule.priority,
                    int(rule.enabled),
                    rule.metadata.source.value,
                    rule.metadata.created_by,
                    rule.metadata.version,
                    _to_iso(rule.metadata.created_at),
                ),
            )
            conn.commit()
        return True

    def load_by_agent(self, agent_id: str) -> list[PolicyRule]:
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                TablePolicyRules.SELECT_BY_AGENT, (agent_id,)
            ).fetchall()
        # M12: skip corrupt rows.
        return [r for r in (_row_to_policy_rule(row) for row in rows) if r is not None]

    def delete(self, rule_id: str) -> bool:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(TablePolicyRules.DELETE_BY_ID, (rule_id,))
            conn.commit()
        return True


class GoalRepository:
    """CRUD for :class:`Goal` rows."""

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    def save(self, agent_id: str, goal: Goal) -> bool:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                TableGoals.INSERT,
                (
                    goal.id,
                    agent_id,
                    goal.description,
                    goal.type.value,
                    goal.parent,
                    json.dumps(goal.children),
                    goal.status.value,
                    goal.priority,
                    json.dumps(_success_criteria_to_dict(goal.success_criteria)),
                    _to_iso(goal.created_at),
                    _to_iso(goal.updated_at),
                ),
            )
            conn.commit()
        return True

    def load_tree(self, agent_id: str) -> GoalTree:
        tree = GoalTree()
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(TableGoals.SELECT_BY_AGENT, (agent_id,)).fetchall()
        for row in rows:
            # M12: skip corrupt rows instead of crashing load_tree.
            goal = _row_to_goal(row)
            if goal is not None:
                tree.add(goal)
        return tree

    def delete(self, goal_id: str) -> bool:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(TableGoals.DELETE_BY_ID, (goal_id,))
            conn.commit()
        return True


class ReflectionRepository:
    """Append-only log for :class:`ReflectionEntry` rows."""

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    def save(self, agent_id: str, entry_id: str, trace: Any, critique: Any, proposals: list[Proposal]) -> bool:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                TableReflectionEntries.INSERT,
                (
                    entry_id,
                    agent_id,
                    json.dumps(trace, default=_json_default),
                    json.dumps(_critique_to_dict(critique), default=_json_default),
                    json.dumps([_proposal_to_dict(p) for p in proposals], default=_json_default),
                    _now_iso(),
                ),
            )
            conn.commit()
        return True

    def load_recent(self, agent_id: str, limit: int = 20) -> list[dict[str, Any]]:
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                TableReflectionEntries.SELECT_BY_AGENT, (agent_id, limit)
            ).fetchall()
        return [dict(r) for r in rows]

    def load_recent_entries(self, agent_id: str, limit: int = 20) -> list[ReflectionEntry]:
        """Load recent reflection entries as reconstructed :class:`ReflectionEntry`.

        Used on session resume (M2) to repopulate the in-memory reflection log.
        The ``DecisionTrace`` is reconstructed minimally (agent_id + timestamp)
        since the full nested trace is not needed for log display.
        """
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                TableReflectionEntries.SELECT_BY_AGENT, (agent_id, limit)
            ).fetchall()
        # M12: skip corrupt rows.
        return [e for e in (_row_to_reflection_entry(r) for r in rows) if e is not None]


# ---------------------------------------------------------------------------
# Row → dataclass helpers
# ---------------------------------------------------------------------------


def _row_to_memory_entry(row: sqlite3.Row) -> MemoryEntry | None:
    """M12 (feature_015): return None on corrupt rows instead of crashing."""
    try:
        return MemoryEntry(
            id=row["id"],
            content=json.loads(row["content"] or "{}"),
            metadata=MemoryMetadata(
                created_at=_from_iso(row["created_at"]),
                last_accessed=_from_iso(row["last_accessed"]),
                access_count=row["access_count"] or 0,
                importance=row["importance"] or 0.5,
                tags=json.loads(row["tags"] or "[]"),
                source=MemorySource(row["source"]) if row["source"] else MemorySource.PERCEPTION,
            ),
            tier=MemoryTier(row["tier"]) if row["tier"] else MemoryTier.VOLATILE,
        )
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        _log.warning("corrupt memory row: %s", exc)
        return None


def _row_to_policy_rule(row: sqlite3.Row) -> PolicyRule | None:
    """M12 (feature_015): return None on corrupt rows."""
    try:
        action_dict = json.loads(row["action_json"] or "{}")
        return PolicyRule(
            id=row["id"],
            condition_expr=row["condition_expr"] or "true",
            action=_dict_to_action(action_dict),
            priority=row["priority"] or 500,
            enabled=bool(row["enabled"]),
            metadata=RuleMetadata(
                source=RuleSource(row["source"]) if row["source"] else RuleSource.DEFAULT,
                created_by=row["created_by"] or "default",
                version=row["version"] or 1,
                created_at=_from_iso(row["created_at"]),
            ),
        )
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        _log.warning("corrupt policy row: %s", exc)
        return None


def _row_to_goal(row: sqlite3.Row) -> Goal | None:
    """M12 (feature_015): return None on corrupt rows."""
    try:
        return Goal(
            id=row["id"],
            description=row["description"] or "",
            type=GoalType(row["type"]) if row["type"] else GoalType.USER_OBJECTIVE,
            parent=row["parent"],
            children=json.loads(row["children"] or "[]"),
            status=GoalStatus(row["status"]) if row["status"] else GoalStatus.PENDING,
            priority=row["priority"] or 50,
            success_criteria=_dict_to_success_criteria(
                json.loads(row["success_criteria"] or "{}")
            ),
            created_at=_from_iso(row["created_at"]),
            updated_at=_from_iso(row["updated_at"]),
        )
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        _log.warning("corrupt goal row: %s", exc)
        return None


def _row_to_reflection_entry(row: sqlite3.Row) -> ReflectionEntry | None:
    """Reconstruct a :class:`ReflectionEntry` from a persisted row (M2).

    The ``DecisionTrace`` is rebuilt minimally (agent_id + timestamp); the
    critique and proposals are fully restored since those drive log display.

    M12 (feature_015): return None on corrupt rows.
    """
    try:
        critique_data = json.loads(row["critique_json"] or "{}")
        proposals_data = json.loads(row["proposals_json"] or "[]")
        proposals: list[Proposal] = []
        for item in proposals_data:
            if not isinstance(item, dict):
                continue
            try:
                ptype = ProposalType(item.get("type", ""))
            except ValueError:
                continue
            proposals.append(
                Proposal(
                    type=ptype,
                    content=item.get("content", {}),
                    rationale=item.get("rationale", ""),
                    status=ProposalStatus(item.get("status", ProposalStatus.PROPOSED.value)),
                )
            )
        return ReflectionEntry(
            id=row["id"],
            trace=DecisionTrace(agent_id=row["agent_id"], timestamp=_from_iso(row["created_at"])),
            critique=Critique(
                summary=critique_data.get("summary", ""),
                strengths=critique_data.get("strengths", []),
                weaknesses=critique_data.get("weaknesses", []),
                confidence=float(critique_data.get("confidence", 0.0)),
            ),
            proposals=proposals,
            created_at=_from_iso(row["created_at"]),
        )
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        _log.warning("corrupt reflection row: %s", exc)
        return None


# ---------------------------------------------------------------------------
# dataclass ↔ dict serializers
# ---------------------------------------------------------------------------


def _action_to_dict(action: PolicyAction) -> dict[str, Any]:
    return {
        "type": action.type.value,
        "parameters": action.parameters,
        "target_goal": action.target_goal,
    }


def _dict_to_action(data: dict[str, Any]) -> PolicyAction:
    return PolicyAction(
        type=ActionType(data.get("type", ActionType.PAUSE.value)),
        parameters=data.get("parameters", {}),
        target_goal=data.get("target_goal"),
    )


def _success_criteria_to_dict(sc: SuccessCriteria) -> dict[str, Any]:
    return {"kind": sc.kind, "expression": sc.expression, "tool_id": sc.tool_id}


def _dict_to_success_criteria(data: dict[str, Any]) -> SuccessCriteria:
    return SuccessCriteria(
        kind=data.get("kind", "always"),
        expression=data.get("expression"),
        tool_id=data.get("tool_id"),
    )


def _critique_to_dict(critique: Any) -> dict[str, Any]:
    if hasattr(critique, "__dict__"):
        return {
            "summary": critique.summary,
            "strengths": critique.strengths,
            "weaknesses": critique.weaknesses,
            "confidence": critique.confidence,
        }
    return {"summary": str(critique)}


def _proposal_to_dict(proposal: Proposal) -> dict[str, Any]:
    return {
        "type": proposal.type.value,
        "content": proposal.content,
        "rationale": proposal.rationale,
        "status": proposal.status.value,
    }


def _to_iso(dt: datetime) -> str:
    return dt.isoformat()


def _from_iso(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return datetime.now(timezone.utc)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json_default(obj: Any) -> Any:
    if isinstance(obj, datetime):
        return obj.isoformat()
    if hasattr(obj, "value") and hasattr(obj, "name"):
        return obj.value
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    return str(obj)
