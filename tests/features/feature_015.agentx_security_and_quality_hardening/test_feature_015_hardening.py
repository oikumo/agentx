"""Regression tests for feature_015 — security & quality hardening.

Covers: C1 (path traversal), C2 (safety deny-list), C3 (DSL subtraction),
H1 (goal priority), H4 (persist failure), M1 (evict OR), M3 (confidence cap),
M4 (_NOOP singleton), M8 (ARCHIVED tier), M9 (dedup), M10 (narrow except),
M11 (unknown identifiers), M13 (reflection log cap), M14 (snapshot retention),
S1 (memory_pressure), and more.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agentx.agent.types import (
    ActionType,
    ActuatorCommand,
    AutonomyLevel,
    EvictionCriteria,
    Goal,
    GoalStatus,
    GoalType,
    MemoryEntry,
    MemoryMetadata,
    MemoryQuery,
    MemorySource,
    MemoryTier,
    PolicyAction,
    PolicyContext,
    PolicyRule,
    Proposal,
    ProposalStatus,
    ProposalType,
    SuccessCriteria,
)
from agentx.agent.model.policy.rule import (
    compile_condition,
    ConditionCompileError,
    CompiledCondition,
)
from agentx.agent.model.reflection.safety_evaluator import DefaultSafetyEvaluator


# ============================================================================
# CRITICAL-1: Path-traversal sandbox bypass
# ============================================================================


class TestPathTraversalFix:
    """C1: str().startswith() replaced with Path.is_relative_to()."""

    def test_sibling_dir_escape_rejected(self, tmp_path):
        """A sibling dir whose name starts with the sandbox name must be rejected."""
        from agentx.agent.model.tools.filesystem_tool import FileSystemTool

        sandbox = tmp_path / "sandbox"
        evil = tmp_path / "sandbox_evil"
        evil.mkdir()
        (evil / "secret.txt").write_text("stolen")

        tool = FileSystemTool(sandbox)
        cmd = ActuatorCommand(
            actuator_id="filesystem",
            action="read",
            parameters={"path": "../sandbox_evil/secret.txt"},
        )
        vr = tool.validate(cmd)
        assert not vr.valid
        assert "escapes sandbox" in vr.errors[0].lower()

    def test_normal_path_accepted(self, tmp_path):
        from agentx.agent.model.tools.filesystem_tool import FileSystemTool

        sandbox = tmp_path / "sandbox"
        tool = FileSystemTool(sandbox)
        cmd = ActuatorCommand(
            actuator_id="filesystem",
            action="read",
            parameters={"path": "target.txt"},
        )
        vr = tool.validate(cmd)
        assert vr.valid

    def test_scenarios_seed_rejects_escape(self, tmp_path):
        """C1 second location: scenarios.py seed_sandbox_files."""
        from agentx.agent.demo.scenarios import seed_sandbox_files, DemoScenario, GoalSpec

        scenario = DemoScenario(
            key="x",
            name="test",
            description="t",
            goal=GoalSpec(description="t"),
            files={"../escape.txt": "evil"},
        )
        with pytest.raises(ValueError, match="escapes sandbox"):
            seed_sandbox_files(scenario, str(tmp_path))


# ============================================================================
# CRITICAL-2: Safety deny-list non-functional
# ============================================================================


class TestSafetyDenyListFix:
    """C2: _infer_op derives op from content shape, not the untrusted op field."""

    def _ctx(self, autonomy=AutonomyLevel.FULLY_AUTONOMOUS):
        return PolicyContext(autonomy_level=autonomy)

    def test_goal_abandon_root_rejected_by_status(self):
        """GOAL_ADJUSTMENT with status=ABANDONED is rejected (content shape)."""
        evaluator = DefaultSafetyEvaluator()
        proposal = Proposal(
            type=ProposalType.GOAL_ADJUSTMENT,
            content={"goal_id": "x", "status": "ABANDONED"},  # no 'op' field
        )
        verdict = evaluator.evaluate(proposal, self._ctx())
        assert verdict.status == ProposalStatus.REJECTED

    def test_memory_delete_all_rejected_by_content(self):
        """MEMORY_UPDATE with delete_all=True is rejected (content shape)."""
        evaluator = DefaultSafetyEvaluator()
        proposal = Proposal(
            type=ProposalType.MEMORY_UPDATE,
            content={"delete_all": True},  # no 'op' field
        )
        verdict = evaluator.evaluate(proposal, self._ctx())
        assert verdict.status == ProposalStatus.REJECTED

    def test_policy_disable_rejected_by_enabled_false(self):
        """POLICY_CHANGE with enabled=False is rejected (content shape)."""
        evaluator = DefaultSafetyEvaluator()
        proposal = Proposal(
            type=ProposalType.POLICY_CHANGE,
            content={"condition": "true", "enabled": False},  # no 'op' field
        )
        verdict = evaluator.evaluate(proposal, self._ctx())
        assert verdict.status == ProposalStatus.REJECTED

    def test_backward_compat_op_field_still_works(self):
        """Explicit op field still works for backward compatibility."""
        evaluator = DefaultSafetyEvaluator()
        proposal = Proposal(
            type=ProposalType.GOAL_ADJUSTMENT,
            content={"op": "delete", "goal_id": "x"},
        )
        verdict = evaluator.evaluate(proposal, self._ctx())
        assert verdict.status == ProposalStatus.REJECTED

    def test_safe_proposal_approved_in_autonomous(self):
        """Non-dangerous proposal is approved in FULLY_AUTONOMOUS."""
        evaluator = DefaultSafetyEvaluator()
        proposal = Proposal(
            type=ProposalType.MEMORY_UPDATE,
            content={"content": "hello"},
        )
        verdict = evaluator.evaluate(proposal, self._ctx())
        assert verdict.status == ProposalStatus.APPROVED


# ============================================================================
# CRITICAL-3: DSL subtraction broken
# ============================================================================


class TestDSLSubtractionFix:
    """C3: subtraction expressions compile and evaluate correctly."""

    def test_subtraction_compiles(self):
        """5-3>1 should compile and evaluate to True."""
        cc = CompiledCondition(expression="5 - 3 > 1")
        assert cc.evaluate(PolicyContext()) is True

    def test_subtraction_evaluates_correctly(self):
        """5-3 should equal 2."""
        ast = compile_condition("5 - 3")
        from agentx.agent.model.policy.rule import ConditionEvaluator

        result = ConditionEvaluator().evaluate(ast, PolicyContext())
        assert result == 2

    def test_unary_minus(self):
        """-5 is a valid negative literal."""
        ast = compile_condition("-5")
        from agentx.agent.model.policy.rule import ConditionEvaluator

        result = ConditionEvaluator().evaluate(ast, PolicyContext())
        assert result == -5

    def test_addition_still_works(self):
        """Addition was already working; ensure no regression."""
        cc = CompiledCondition(expression="2 + 3 == 5")
        assert cc.evaluate(PolicyContext()) is True

    def test_chained_arithmetic(self):
        """10 - 3 + 2 == 9"""
        cc = CompiledCondition(expression="10 - 3 + 2 == 9")
        assert cc.evaluate(PolicyContext()) is True


# ============================================================================
# HIGH-1: Goal promotion ignores priority
# ============================================================================


class TestGoalPriorityPromotion:
    """H1: _promote_next promotes highest-priority pending goal."""

    def test_higher_priority_promoted_first(self):
        from agentx.agent.model.goal.manager import GoalManager

        mgr = GoalManager()
        low = Goal(id="low", description="low", priority=10, status=GoalStatus.PENDING)
        high = Goal(id="high", description="high", priority=90, status=GoalStatus.PENDING)
        mgr.add_goal(low)
        mgr.add_goal(high)

        # Complete the active goal (root is first-added, becomes active)
        root = mgr.active_goal()
        assert root is not None
        mgr.update_status(root.id, GoalStatus.COMPLETED)

        # The high-priority goal should be promoted, not the low one
        active = mgr.active_goal()
        assert active is not None
        assert active.id == "high"


# ============================================================================
# HIGH-4: persist() returns id on failure
# ============================================================================


class TestPersistFailure:
    """H4: persist() returns "" on failure."""

    def test_persist_returns_empty_on_failure(self, tmp_path):
        from agentx.agent.model.agent import Agent
        from agentx.agent.types import AgentConfig

        config = AgentConfig(id="test", sandbox_root=str(tmp_path))
        agent = Agent(config)
        # Mock save_snapshot_with_retry to return False
        agent._db.save_snapshot_with_retry = MagicMock(return_value=False)
        result = agent.persist()
        assert result == ""


# ============================================================================
# M1: evict() elif → if
# ============================================================================


class TestEvictOrSemantics:
    """M1: eviction criteria should be OR, not mutually exclusive."""

    def test_tags_checked_even_when_min_importance_not_met(self):
        from agentx.agent.model.memory.manager import MemoryManager

        mgr = MemoryManager()
        # Entry above min_importance but matching tags — should be evicted by tags
        entry = mgr.create_entry(content={"x": 1}, importance=0.9, tags=["temp"])
        mgr.store(entry, MemoryTier.VOLATILE)

        count = mgr.evict(EvictionCriteria(min_importance=0.5, tags=["temp"]))
        assert count >= 1  # should be evicted by tags even though importance > 0.5


# ============================================================================
# M3: confidence cap + priority bounds
# ============================================================================


class TestConfidenceCapAndPriorityBounds:
    """M3: confidence capped at 1.0; PolicyRule priority 0-1000."""

    def test_contested_confidence_capped(self):
        from agentx.agent.model.policy.evaluator import PolicyEngine

        engine = PolicyEngine()
        # Priority 900 → confidence 0.9 (contested, should be capped at 1.0)
        r1 = PolicyRule(id="r1", condition_expr="true", action=PolicyAction(type=ActionType.PAUSE), priority=900)
        r2 = PolicyRule(id="r2", condition_expr="true", action=PolicyAction(type=ActionType.PAUSE), priority=800)
        engine.add_rule(r1)
        engine.add_rule(r2)
        decision = engine.evaluate(PolicyContext())
        assert decision.confidence <= 1.0

    def test_priority_out_of_bounds_raises(self):
        """PolicyRule with priority > 1000 should raise."""
        with pytest.raises(ValueError, match="priority"):
            PolicyRule(
                id="x",
                condition_expr="true",
                action=PolicyAction(type=ActionType.PAUSE),
                priority=1500,
            )

    def test_priority_zero_allowed(self):
        r = PolicyRule(id="x", condition_expr="true", action=PolicyAction(type=ActionType.PAUSE), priority=0)
        assert r.priority == 0


# ============================================================================
# M4: _NOOP shared mutable singleton
# ============================================================================


class TestNoopNotShared:
    """M4: no-op decisions return fresh PolicyAction, not a shared singleton."""

    def test_noop_action_is_fresh_each_time(self):
        from agentx.agent.model.policy.evaluator import _noop_action

        a1 = _noop_action()
        a2 = _noop_action()
        assert a1 is not a2  # different objects

    def test_noop_mutation_doesnt_corrupt(self):
        from agentx.agent.model.policy.evaluator import PolicyEngine

        engine = PolicyEngine()
        d1 = engine.evaluate(PolicyContext())
        d1.selected_action.parameters["evil"] = True  # mutate
        d2 = engine.evaluate(PolicyContext())
        assert "evil" not in d2.selected_action.parameters  # not corrupted


# ============================================================================
# M8: ARCHIVED tier
# ============================================================================


class TestArchivedTier:
    """M8: ARCHIVED tier entries are stored, not silently dropped."""

    def test_archived_stored_to_repository(self, tmp_path):
        from agentx.agent.model.memory.manager import MemoryManager
        from agentx.agent.persistence.agent_db import SessionDatabase
        from agentx.agent.persistence.repositories_db import MemoryRepository

        db_path = str(tmp_path / "test.db")
        SessionDatabase(db_path)  # ensure schema
        repo = MemoryRepository(db_path)
        mgr = MemoryManager(repository=repo, agent_id="a1")
        entry = mgr.create_entry(content={"x": 1}, importance=0.5)
        mgr.store(entry, MemoryTier.ARCHIVED)
        # Should be loadable from the repository
        loaded = repo.load_by_agent("a1")
        assert any(e.tier == MemoryTier.ARCHIVED for e in loaded)


# ============================================================================
# M9: retrieve() dedup
# ============================================================================


class TestRetrieveDedup:
    """M9: retrieve() deduplicates by entry.id."""

    def test_no_duplicates(self):
        from agentx.agent.model.memory.manager import MemoryManager

        mgr = MemoryManager()
        entry = mgr.create_entry(content={"x": 1})
        mgr.store(entry, MemoryTier.VOLATILE)
        results = mgr.retrieve(MemoryQuery(limit=100))
        ids = [e.id for e in results]
        assert len(ids) == len(set(ids))  # no duplicates


# ============================================================================
# M10 + M11: condition evaluation errors + unknown identifiers
# ============================================================================


class TestConditionErrorHandling:
    """M10: narrow except; M11: unknown identifiers fail-fast."""

    def test_unknown_identifier_returns_false(self):
        """Unknown identifier doesn't crash evaluate — returns False (M10/M11)."""
        cc = CompiledCondition(expression="unknown.thing > 5")
        assert cc.evaluate(PolicyContext()) is False

    def test_unknown_function_returns_false(self):
        cc = CompiledCondition(expression="unknown_func() > 5")
        assert cc.evaluate(PolicyContext()) is False

    def test_known_identifier_compiles(self):
        """Known identifiers compile without error."""
        cc = CompiledCondition(expression="true")
        assert cc.evaluate(PolicyContext()) is True

    def test_compile_raises_for_unknown_identifier(self):
        """compile_condition raises ConditionCompileError for unknown roots (M11)."""
        with pytest.raises(ConditionCompileError, match="unknown identifier"):
            compile_condition("foo.bar > 5")


# ============================================================================
# M13: Reflection log growth
# ============================================================================


class TestReflectionLogCap:
    """M13: reflection log is capped at _MAX_LOG_ENTRIES."""

    def test_log_pruned_when_over_cap(self):
        from agentx.agent.model.reflection.engine import ReflectionEngine, _MAX_LOG_ENTRIES
        from agentx.agent.types import Critique, DecisionTrace, ReflectionEntry

        engine = ReflectionEngine()
        # Add more than _MAX_LOG_ENTRIES entries
        for i in range(_MAX_LOG_ENTRIES + 50):
            entry = ReflectionEntry(
                id=f"entry-{i}",
                trace=DecisionTrace(agent_id="a1"),
                critique=Critique(summary=f"entry {i}", confidence=0.5),
                proposals=[],
            )
            engine._append_entry(entry)

        assert len(engine.get_log()) <= _MAX_LOG_ENTRIES


# ============================================================================
# M14: Snapshot retention
# ============================================================================


class TestSnapshotRetention:
    """M14: old snapshots are deleted beyond retention limit."""

    def test_old_snapshots_deleted(self, tmp_path):
        from agentx.agent.persistence.agent_db import SessionDatabase, _MAX_SNAPSHOTS_PER_AGENT
        from agentx.agent.types import SessionSnapshot

        db = SessionDatabase(str(tmp_path / "test.db"))
        # Save more than the limit
        for i in range(_MAX_SNAPSHOTS_PER_AGENT + 10):
            snap = SessionSnapshot(
                snapshot_id=f"snap-{i}",
                agent_id="agent1",
                config_version=1,
            )
            db.save_snapshot(snap)

        # Count remaining snapshots
        import sqlite3

        with sqlite3.connect(str(tmp_path / "test.db")) as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM session_snapshots WHERE agent_id = ?",
                ("agent1",),
            ).fetchone()[0]
        assert count <= _MAX_SNAPSHOTS_PER_AGENT


# ============================================================================
# S1: memory_pressure heuristic
# ============================================================================


class TestMemoryPressure:
    """S1: memory_pressure is no longer a stub returning 0.0."""

    def test_memory_pressure_nonzero_with_readings(self):
        from agentx.agent.types import EnvironmentModel, SensorReading
        from datetime import datetime, timezone

        env = EnvironmentModel(
            sensor_readings={
                "s1": SensorReading(sensor_id="s1", data={}, timestamp=datetime.now(timezone.utc), confidence=1.0),
                "s2": SensorReading(sensor_id="s2", data={}, timestamp=datetime.now(timezone.utc), confidence=1.0),
            },
        )
        assert env.memory_pressure > 0.0

    def test_memory_pressure_zero_without_readings(self):
        from agentx.agent.types import EnvironmentModel

        env = EnvironmentModel()
        assert env.memory_pressure == 0.0

    def test_memory_pressure_capped_at_1(self):
        from agentx.agent.types import EnvironmentModel, SensorReading
        from datetime import datetime, timezone

        readings = {
            f"s{i}": SensorReading(sensor_id=f"s{i}", data={}, timestamp=datetime.now(timezone.utc), confidence=1.0)
            for i in range(200)
        }
        env = EnvironmentModel(sensor_readings=readings)
        assert env.memory_pressure == 1.0


# ============================================================================
# L6: Registry custom exception
# ============================================================================


class TestRegistryCustomException:
    """L6: get_sensor/get_actuator raise ToolSchemaError, not KeyError."""

    def test_get_sensor_unknown_raises_tool_schema_error(self):
        from agentx.agent.model.tools.registry import ToolRegistry
        from agentx.agent.model.tools.spec import ToolSchemaError

        registry = ToolRegistry()
        with pytest.raises(ToolSchemaError, match="unknown sensor"):
            registry.get_sensor("nonexistent")

    def test_get_actuator_unknown_raises_tool_schema_error(self):
        from agentx.agent.model.tools.registry import ToolRegistry
        from agentx.agent.model.tools.spec import ToolSchemaError

        registry = ToolRegistry()
        with pytest.raises(ToolSchemaError, match="unknown actuator"):
            registry.get_actuator("nonexistent")


# ============================================================================
# L10: CritiqueParser TypeError
# ============================================================================


class TestCritiqueParserTypeError:
    """L10: float(confidence_raw) doesn't crash on non-numeric values."""

    def test_non_numeric_confidence_doesnt_crash(self):
        from agentx.agent.model.reflection.critique_parser import CritiqueParser
        from agentx.agent.types import DecisionTrace

        parser = CritiqueParser()
        # Confidence as a list (non-numeric, non-string)
        raw = json.dumps({"critique": {"confidence": [1, 2, 3]}, "proposals": []})
        entry = parser.parse(raw, DecisionTrace(agent_id="a1"))
        assert entry.critique.confidence == 0.5  # fallback

    def test_none_confidence_doesnt_crash(self):
        from agentx.agent.model.reflection.critique_parser import CritiqueParser
        from agentx.agent.types import DecisionTrace

        parser = CritiqueParser()
        raw = json.dumps({"critique": {"confidence": None}, "proposals": []})
        entry = parser.parse(raw, DecisionTrace(agent_id="a1"))
        assert entry.critique.confidence == 0.5


# ============================================================================
# S7: Expire old proposals
# ============================================================================


class TestExpireOldProposals:
    """S7: old NEEDS_CONFIRMATION proposals are expired."""

    def test_expire_old_proposals(self):
        from agentx.agent.model.reflection.engine import ReflectionEngine
        from agentx.agent.types import Critique, DecisionTrace, ReflectionEntry, Proposal
        from datetime import datetime, timezone, timedelta

        engine = ReflectionEngine()
        old_time = datetime.now(timezone.utc) - timedelta(hours=2)
        entry = ReflectionEntry(
            id="old-entry",
            trace=DecisionTrace(agent_id="a1"),
            critique=Critique(summary="old", confidence=0.5),
            proposals=[
                Proposal(
                    type=ProposalType.MEMORY_UPDATE,
                    content={},
                    rationale="old proposal",
                    status=ProposalStatus.NEEDS_CONFIRMATION,
                ),
            ],
            created_at=old_time,
        )
        engine.restore_log([entry])

        expired = engine.expire_old_proposals(max_age_seconds=3600)
        assert expired == 1
        assert entry.proposals[0].status == ProposalStatus.REJECTED
