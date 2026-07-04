"""MemoryManager — tiered memory subsystem (design §4.1, §12).

Implements :class:`IMemoryStorePartner`.  Uses an LRU-style volatile cache and
an optional persistent sqlite backing store.  No external vector library at
runtime — embeddings are optional and degrade gracefully.
"""

from __future__ import annotations

import heapq
import uuid
from collections import OrderedDict
from datetime import datetime, timezone
from typing import Any

from agentx.agent.interfaces import IMemoryStorePartner
from agentx.agent.persistence.repositories_db import MemoryRepository
from agentx.agent.types import (
    EvictionCriteria,
    MemoryEntry,
    MemoryMetadata,
    MemoryQuery,
    MemorySource,
    MemoryTier,
)


class MemoryManager(IMemoryStorePartner):
    """Volatile (LRU) + persistent (sqlite) memory with consolidation."""

    def __init__(
        self,
        volatile_capacity: int = 10_000,
        repository: MemoryRepository | None = None,
        agent_id: str = "",
    ) -> None:
        self._volatile: OrderedDict[str, MemoryEntry] = OrderedDict()
        self._volatile_capacity = volatile_capacity
        self._repository = repository
        self._agent_id = agent_id

    # ----------------------------------------------------------- IMemoryStorePartner

    def store(self, entry: MemoryEntry, tier: MemoryTier = MemoryTier.VOLATILE) -> None:
        entry.tier = tier
        if tier == MemoryTier.VOLATILE:
            self._volatile[entry.id] = entry
            self._volatile.move_to_end(entry.id)
            self._enforce_capacity()
        elif tier == MemoryTier.PERSISTENT and self._repository is not None:
            self._repository.save(self._agent_id, entry)

    def retrieve(self, query: MemoryQuery) -> list[MemoryEntry]:
        results = list(self._volatile.values())
        if self._repository is not None:
            results.extend(self._repository.load_by_agent(self._agent_id))
        # filter by source
        if query.source is not None:
            results = [e for e in results if e.metadata.source == query.source]
        # filter by tags
        if query.tags:
            results = [
                e for e in results
                if any(t in e.metadata.tags for t in query.tags)
            ]
        # filter by min importance
        if query.min_importance is not None:
            results = [e for e in results if e.metadata.importance >= query.min_importance]
        # filter by time range
        if query.time_range is not None:
            results = [
                e for e in results
                if query.time_range.start <= e.metadata.created_at
                and (query.time_range.end is None or e.metadata.created_at <= query.time_range.end)
            ]
        # sort by importance desc, then recency
        results.sort(key=lambda e: (e.metadata.importance, e.metadata.created_at), reverse=True)
        return results[: query.limit]

    def consolidate(self) -> int:
        """Move high-importance volatile entries to persistent tier. Returns count moved."""
        if self._repository is None:
            return 0
        moved = 0
        for entry in list(self._volatile.values()):
            if entry.metadata.importance >= 0.7:
                entry.tier = MemoryTier.PERSISTENT
                self._repository.save(self._agent_id, entry)
                del self._volatile[entry.id]
                moved += 1
        return moved

    def evict(self, criteria: EvictionCriteria) -> int:
        """Evict low-importance volatile entries. Returns count evicted."""
        to_evict: list[str] = []
        now = datetime.now(timezone.utc)
        for eid, entry in self._volatile.items():
            if criteria.min_importance is not None and entry.metadata.importance < criteria.min_importance:
                to_evict.append(eid)
            elif criteria.max_age is not None:
                age = (now - entry.metadata.created_at).total_seconds()
                if age > criteria.max_age:
                    to_evict.append(eid)
            elif criteria.tags and any(t in entry.metadata.tags for t in criteria.tags):
                to_evict.append(eid)
        # hard capacity limit
        if criteria.max_entries is not None and len(self._volatile) > criteria.max_entries:
            excess = len(self._volatile) - criteria.max_entries
            least_valuable = heapq.nsmallest(
                excess,
                self._volatile.items(),
                key=lambda item: item[1].metadata.importance,
            )
            to_evict.extend([eid for eid, _ in least_valuable])
        for eid in set(to_evict):
            self._volatile.pop(eid, None)
        return len(set(to_evict))

    # ----------------------------------------------------------- helpers

    def find_least_valuable(self, k: int) -> list[MemoryEntry]:
        """Efficient eviction candidate selection (design §12)."""
        return heapq.nsmallest(
            k, self._volatile.values(), key=lambda e: e.metadata.importance
        )

    # ----------------------------------------------------------- snapshot helpers

    def export_volatile(self) -> list[MemoryEntry]:
        """Return a shallow copy of the volatile cache (for snapshot serialisation)."""
        return list(self._volatile.values())

    def import_volatile(self, entries: list[MemoryEntry]) -> None:
        """Replace the volatile cache with *entries* (used on session resume)."""
        self._volatile = OrderedDict()
        for entry in entries:
            entry.tier = MemoryTier.VOLATILE
            self._volatile[entry.id] = entry
        self._enforce_capacity()

    def count_volatile(self) -> int:
        """Public accessor for the volatile entry count (replaces private reach-through)."""
        return len(self._volatile)

    def create_entry(
        self,
        content: dict[str, Any],
        source: MemorySource = MemorySource.PERCEPTION,
        importance: float = 0.5,
        tags: list[str] | None = None,
    ) -> MemoryEntry:
        return MemoryEntry(
            id=str(uuid.uuid4()),
            content=content,
            metadata=MemoryMetadata(
                source=source,
                importance=importance,
                tags=tags or [],
            ),
        )

    def apply_update(self, content: dict[str, Any]) -> str:
        """Apply a reflection MEMORY_UPDATE proposal; returns rollback token."""
        entry = self.create_entry(
            content=content,
            source=MemorySource.REFLECTION,
            importance=content.get("importance", 0.6),
        )
        self.store(entry, MemoryTier.VOLATILE)
        return entry.id

    def revert_update(self, token: str) -> None:
        """Roll back a previously applied memory update."""
        self._volatile.pop(token, None)

    def _enforce_capacity(self) -> None:
        while len(self._volatile) > self._volatile_capacity:
            self._volatile.popitem(last=False)
