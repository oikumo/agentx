"""Unit tests for MemoryManager."""

from __future__ import annotations

from agentx.agent.model.memory.manager import MemoryManager
from agentx.agent.types import (
    EvictionCriteria,
    MemoryEntry,
    MemoryMetadata,
    MemoryQuery,
    MemorySource,
    MemoryTier,
)


class TestMemoryStoreRetrieve:
    def test_store_volatile(self):
        mgr = MemoryManager(volatile_capacity=100)
        entry = mgr.create_entry({"key": "val"}, source=MemorySource.PERCEPTION)
        mgr.store(entry, MemoryTier.VOLATILE)
        results = mgr.retrieve(MemoryQuery(limit=10))
        assert len(results) == 1
        assert results[0].content == {"key": "val"}

    def test_retrieve_by_source(self):
        mgr = MemoryManager()
        mgr.store(mgr.create_entry({"a": 1}, source=MemorySource.PERCEPTION), MemoryTier.VOLATILE)
        mgr.store(mgr.create_entry({"b": 2}, source=MemorySource.REFLECTION), MemoryTier.VOLATILE)
        results = mgr.retrieve(MemoryQuery(source=MemorySource.REFLECTION, limit=10))
        assert len(results) == 1
        assert results[0].content == {"b": 2}

    def test_retrieve_by_tags(self):
        mgr = MemoryManager()
        mgr.store(mgr.create_entry({"a": 1}, tags=["alpha"]), MemoryTier.VOLATILE)
        mgr.store(mgr.create_entry({"b": 2}, tags=["beta"]), MemoryTier.VOLATILE)
        results = mgr.retrieve(MemoryQuery(tags=["alpha"], limit=10))
        assert len(results) == 1
        assert results[0].content == {"a": 1}

    def test_retrieve_by_min_importance(self):
        mgr = MemoryManager()
        mgr.store(mgr.create_entry({"v": "low"}, importance=0.2), MemoryTier.VOLATILE)
        mgr.store(mgr.create_entry({"v": "high"}, importance=0.9), MemoryTier.VOLATILE)
        results = mgr.retrieve(MemoryQuery(min_importance=0.5, limit=10))
        assert len(results) == 1

    def test_retrieve_limit(self):
        mgr = MemoryManager()
        for i in range(10):
            mgr.store(mgr.create_entry({"i": i}, importance=0.5), MemoryTier.VOLATILE)
        results = mgr.retrieve(MemoryQuery(limit=3))
        assert len(results) == 3


class TestMemoryEviction:
    def test_evict_by_min_importance(self):
        mgr = MemoryManager()
        mgr.store(mgr.create_entry({"v": "low"}, importance=0.1), MemoryTier.VOLATILE)
        mgr.store(mgr.create_entry({"v": "high"}, importance=0.9), MemoryTier.VOLATILE)
        evicted = mgr.evict(EvictionCriteria(min_importance=0.5))
        assert evicted == 1
        results = mgr.retrieve(MemoryQuery(limit=10))
        assert len(results) == 1
        assert results[0].content == {"v": "high"}

    def test_evict_by_max_entries(self):
        mgr = MemoryManager()
        for i in range(10):
            mgr.store(mgr.create_entry({"i": i}, importance=0.5), MemoryTier.VOLATILE)
        evicted = mgr.evict(EvictionCriteria(max_entries=5))
        assert evicted >= 5
        assert len(mgr.retrieve(MemoryQuery(limit=100))) <= 5

    def test_lru_capacity_enforced(self):
        mgr = MemoryManager(volatile_capacity=3)
        for i in range(5):
            mgr.store(mgr.create_entry({"i": i}), MemoryTier.VOLATILE)
        results = mgr.retrieve(MemoryQuery(limit=100))
        assert len(results) == 3  # capacity enforced

    def test_find_least_valuable(self):
        mgr = MemoryManager()
        mgr.store(mgr.create_entry({"v": "a"}, importance=0.9), MemoryTier.VOLATILE)
        mgr.store(mgr.create_entry({"v": "b"}, importance=0.1), MemoryTier.VOLATILE)
        least = mgr.find_least_valuable(1)
        assert len(least) == 1
        assert least[0].content == {"v": "b"}


class TestMemoryApplyRevert:
    def test_apply_update(self):
        mgr = MemoryManager()
        token = mgr.apply_update({"note": "test", "importance": 0.8})
        assert token  # non-empty token
        results = mgr.retrieve(MemoryQuery(limit=10))
        assert len(results) == 1

    def test_revert_update(self):
        mgr = MemoryManager()
        token = mgr.apply_update({"note": "test"})
        mgr.revert_update(token)
        results = mgr.retrieve(MemoryQuery(limit=10))
        assert len(results) == 0
