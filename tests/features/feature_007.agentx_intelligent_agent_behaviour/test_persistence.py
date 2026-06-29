"""Unit tests for persistence layer — schema, database, repositories."""

from __future__ import annotations

import json
from pathlib import Path

from agentx.agent.persistence.agent_db import SessionDatabase
from agentx.agent.persistence.repositories_db import (
    GoalRepository,
    MemoryRepository,
    PolicyRepository,
    ReflectionRepository,
)
from agentx.agent.persistence.schema_db import (
    ALL_TABLES,
    TableAgents,
    TableGoals,
    TableMemoryEntries,
    TablePolicyRules,
    TableReflectionEntries,
    TableSessionSnapshots,
)
from agentx.agent.types import (
    Goal,
    GoalStatus,
    GoalType,
    MemoryEntry,
    MemoryMetadata,
    MemorySource,
    MemoryTier,
    PolicyAction,
    PolicyRule,
    RuleMetadata,
    RuleSource,
    ActionType,
    SessionSnapshot,
    SuccessCriteria,
)


class TestSchemaDescriptors:
    def test_all_tables_have_query(self):
        for table in ALL_TABLES:
            assert hasattr(table, "TABLE_QUERY")
            assert "CREATE TABLE IF NOT EXISTS" in table.TABLE_QUERY

    def test_table_names_unique(self):
        names = [t.TABLE_NAME for t in ALL_TABLES]
        assert len(names) == len(set(names))

    def test_snapshot_table_columns(self):
        assert "snapshot_id" in TableSessionSnapshots.TABLE_QUERY
        assert "agent_id" in TableSessionSnapshots.TABLE_QUERY
        assert "volatility_data" in TableSessionSnapshots.TABLE_QUERY


class TestSessionDatabase:
    def test_creates_schema(self, tmp_agent_dir):
        db_path = str(Path(tmp_agent_dir) / "test_agent.db")
        db = SessionDatabase(db_path)
        assert Path(db_path).exists()

    def test_upsert_agent(self, tmp_agent_dir):
        db_path = str(Path(tmp_agent_dir) / "test_agent.db")
        db = SessionDatabase(db_path)
        assert db.upsert_agent("a1", "Test", 1, "SUPERVISED", "{}") is True

    def test_save_and_load_snapshot(self, tmp_agent_dir):
        db_path = str(Path(tmp_agent_dir) / "test_agent.db")
        db = SessionDatabase(db_path)
        snapshot = SessionSnapshot(
            snapshot_id="snap1",
            agent_id="a1",
            config_version=1,
            volatility_data={"state": "PERCEIVING"},
            policy_store=[{"id": "r1"}],
            goal_tree={"root": "g1"},
            reflection_log_position=0,
        )
        assert db.save_snapshot(snapshot) is True
        loaded = db.load_snapshot("snap1")
        assert loaded is not None
        assert loaded.agent_id == "a1"
        assert loaded.volatility_data == {"state": "PERCEIVING"}

    def test_load_latest_snapshot(self, tmp_agent_dir):
        db_path = str(Path(tmp_agent_dir) / "test_agent.db")
        db = SessionDatabase(db_path)
        for i in range(3):
            db.save_snapshot(SessionSnapshot(
                snapshot_id=f"snap{i}", agent_id="a1", config_version=1,
            ))
        latest = db.load_latest_snapshot("a1")
        assert latest is not None
        assert latest.snapshot_id == "snap2"

    def test_load_missing_snapshot(self, tmp_agent_dir):
        db_path = str(Path(tmp_agent_dir) / "test_agent.db")
        db = SessionDatabase(db_path)
        assert db.load_snapshot("nonexistent") is None

    def test_save_with_retry(self, tmp_agent_dir):
        db_path = str(Path(tmp_agent_dir) / "test_agent.db")
        db = SessionDatabase(db_path)
        snapshot = SessionSnapshot(snapshot_id="s1", agent_id="a1")
        assert db.save_snapshot_with_retry(snapshot) is True


class TestMemoryRepository:
    def test_save_and_load(self, tmp_agent_dir):
        db_path = str(Path(tmp_agent_dir) / "test_agent.db")
        SessionDatabase(db_path)
        repo = MemoryRepository(db_path)
        entry = MemoryEntry(
            id="m1",
            content={"note": "test"},
            metadata=MemoryMetadata(source=MemorySource.PERCEPTION, importance=0.8),
            tier=MemoryTier.VOLATILE,
        )
        assert repo.save("a1", entry) is True
        loaded = repo.load_by_agent("a1")
        assert len(loaded) == 1
        assert loaded[0].content == {"note": "test"}
        assert loaded[0].metadata.importance == 0.8

    def test_load_by_tier(self, tmp_agent_dir):
        db_path = str(Path(tmp_agent_dir) / "test_agent.db")
        SessionDatabase(db_path)
        repo = MemoryRepository(db_path)
        repo.save("a1", MemoryEntry(
            id="m1", content={"a": 1},
            metadata=MemoryMetadata(source=MemorySource.PERCEPTION),
            tier=MemoryTier.VOLATILE,
        ))
        repo.save("a1", MemoryEntry(
            id="m2", content={"b": 2},
            metadata=MemoryMetadata(source=MemorySource.REFLECTION),
            tier=MemoryTier.PERSISTENT,
        ))
        volatile = repo.load_by_agent("a1", MemoryTier.VOLATILE)
        assert len(volatile) == 1
        assert volatile[0].id == "m1"


class TestPolicyRepository:
    def test_save_and_load(self, tmp_agent_dir):
        db_path = str(Path(tmp_agent_dir) / "test_agent.db")
        SessionDatabase(db_path)
        repo = PolicyRepository(db_path)
        rule = PolicyRule(
            id="r1",
            condition_expr="goal.active",
            action=PolicyAction(type=ActionType.EXECUTE_TOOL, parameters={"tool_id": "fs"}),
            priority=700,
            metadata=RuleMetadata(source=RuleSource.USER_DEFINED, created_by="user"),
        )
        assert repo.save("a1", rule) is True
        loaded = repo.load_by_agent("a1")
        assert len(loaded) == 1
        assert loaded[0].condition_expr == "goal.active"
        assert loaded[0].priority == 700
        assert loaded[0].metadata.source == RuleSource.USER_DEFINED


class TestGoalRepository:
    def test_save_and_load_tree(self, tmp_agent_dir):
        db_path = str(Path(tmp_agent_dir) / "test_agent.db")
        SessionDatabase(db_path)
        repo = GoalRepository(db_path)
        goal = Goal(
            id="g1", description="root", type=GoalType.USER_OBJECTIVE,
            status=GoalStatus.ACTIVE, priority=80,
            success_criteria=SuccessCriteria(kind="always"),
        )
        assert repo.save("a1", goal) is True
        tree = repo.load_tree("a1")
        goal = tree.get("g1")
        assert goal is not None
        assert goal.description == "root"


class TestReflectionRepository:
    def test_save_and_load(self, tmp_agent_dir):
        db_path = str(Path(tmp_agent_dir) / "test_agent.db")
        SessionDatabase(db_path)
        repo = ReflectionRepository(db_path)
        repo.save("a1", "ref1", {"perception": "ok"}, Critique_stub(), [])
        loaded = repo.load_recent("a1", limit=10)
        assert len(loaded) == 1
        assert loaded[0]["id"] == "ref1"


def Critique_stub():
    """Minimal stub matching the _critique_to_dict serializer."""
    class _C:
        summary = "ok"
        strengths = []
        weaknesses = []
        confidence = 0.8
    return _C()
