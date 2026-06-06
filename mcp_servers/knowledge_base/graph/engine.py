#!/usr/bin/env python3
"""
Knowledge Graph Engine for KB MCP v4.

Provides graph operations using NetworkX with SQLite persistence.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import networkx as nx

from .models import (
    Entity,
    EntityKind,
    GraphMetadata,
    GraphPath,
    ImpactResult,
    Relationship,
    RelationshipKind,
)


class KnowledgeGraph:
    """
    In-memory knowledge graph using NetworkX.
    
    This class provides graph operations for navigating code entities
    and their relationships. Data is persisted to SQLite for durability.
    """
    
    def __init__(self):
        """Initialize an empty knowledge graph."""
        self._graph = nx.DiGraph()
        self._metadata = GraphMetadata()
        self._entity_index: dict[str, Entity] = {}
        self._relationship_index: dict[tuple[str, str, str], Relationship] = {}
    
    @property
    def metadata(self) -> GraphMetadata:
        """Get graph metadata."""
        return self._metadata
    
    @property
    def num_entities(self) -> int:
        """Get number of entities in graph."""
        return len(self._entity_index)
    
    @property
    def num_relationships(self) -> int:
        """Get number of relationships in graph."""
        return len(self._relationship_index)
    
    def add_entity(self, entity: Entity) -> None:
        """
        Add an entity to the graph.
        
        Args:
            entity: The entity to add
            
        Note:
            If entity already exists, it will be updated.
        """
        self._graph.add_node(entity.id, **entity.to_dict())
        self._entity_index[entity.id] = entity
        self._metadata.total_entities = len(self._entity_index)
        self._metadata.updated_at = datetime.now()
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """
        Get an entity by ID.
        
        Args:
            entity_id: The entity ID
            
        Returns:
            The entity or None if not found
        """
        return self._entity_index.get(entity_id)
    
    def remove_entity(self, entity_id: str) -> bool:
        """
        Remove an entity and all its relationships.
        
        Args:
            entity_id: The entity ID to remove
            
        Returns:
            True if entity was removed, False if not found
        """
        if entity_id not in self._entity_index:
            return False
        
        # Remove all relationships involving this entity
        for rel_key in list(self._relationship_index.keys()):
            source_id, target_id, _ = rel_key
            if source_id == entity_id or target_id == entity_id:
                del self._relationship_index[rel_key]
        
        self._graph.remove_node(entity_id)
        del self._entity_index[entity_id]
        self._metadata.total_entities = len(self._entity_index)
        self._metadata.updated_at = datetime.now()
        return True
    
    def add_relationship(self, relationship: Relationship) -> None:
        """
        Add a relationship between two entities.
        
        Args:
            relationship: The relationship to add
            
        Raises:
            ValueError: If source or target entity doesn't exist
        """
        if relationship.source_id not in self._entity_index:
            raise ValueError(f"Source entity {relationship.source_id} not found")
        if relationship.target_id not in self._entity_index:
            raise ValueError(f"Target entity {relationship.target_id} not found")
        
        # Add edge to NetworkX graph
        self._graph.add_edge(
            relationship.source_id,
            relationship.target_id,
            kind=relationship.kind.value,
            **relationship.metadata,
        )
        
        # Index the relationship
        rel_key = (relationship.source_id, relationship.target_id, relationship.kind.value)
        self._relationship_index[rel_key] = relationship
        self._metadata.total_relationships = len(self._relationship_index)
        self._metadata.updated_at = datetime.now()
    
    def get_relationships(
        self,
        entity_id: str,
        direction: str = "both",
        relationship_kind: Optional[str] = None,
    ) -> list[Relationship]:
        """
        Get relationships for an entity.
        
        Args:
            entity_id: The entity ID
            direction: "incoming", "outgoing", or "both"
            relationship_kind: Optional filter by relationship type
            
        Returns:
            List of matching relationships
        """
        results = []
        
        for (source_id, target_id, kind), rel in self._relationship_index.items():
            if relationship_kind and kind != relationship_kind:
                continue
            
            if direction == "outgoing" and source_id == entity_id:
                results.append(rel)
            elif direction == "incoming" and target_id == entity_id:
                results.append(rel)
            elif direction == "both" and (source_id == entity_id or target_id == entity_id):
                results.append(rel)
        
        return results
    
    def traverse(
        self,
        target_id: str,
        direction: str = "both",
        relationship_kind: Optional[str] = None,
        depth: int = 1,
    ) -> list[Entity]:
        """
        Traverse the graph from a target entity.
        
        Args:
            target_id: Starting entity ID
            direction: "incoming", "outgoing", or "both"
            relationship_kind: Optional filter by relationship type
            depth: Maximum depth of traversal
            
        Returns:
            List of entities found within depth
        """
        if target_id not in self._entity_index:
            return []
        
        visited = {target_id}
        to_visit = [(target_id, 0)]
        results = []
        
        while to_visit:
            current_id, current_depth = to_visit.pop(0)
            
            if current_depth > 0:  # Don't include start node in results
                if current_id in self._entity_index:
                    results.append(self._entity_index[current_id])
            
            if current_depth >= depth:
                continue
            
            # Get neighbors based on direction
            if direction in ("outgoing", "both"):
                neighbors = self._graph.successors(current_id)
            else:
                neighbors = list(self._graph.predecessors(current_id))
                if direction == "both":
                    neighbors = list(neighbors) + list(self._graph.successors(current_id))
            
            for neighbor_id in neighbors:
                # Check relationship kind filter
                if relationship_kind:
                    edge_data = self._graph.get_edge_data(current_id, neighbor_id)
                    if edge_data and edge_data.get("kind") != relationship_kind:
                        continue
                
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    to_visit.append((neighbor_id, current_depth + 1))
        
        return results
    
    def find_path(self, source_id: str, target_id: str, max_depth: int = 10) -> Optional[GraphPath]:
        """
        Find shortest path between two entities.
        
        Args:
            source_id: Starting entity ID
            target_id: Target entity ID
            max_depth: Maximum path length to search
            
        Returns:
            GraphPath or None if no path exists
        """
        if source_id not in self._entity_index or target_id not in self._entity_index:
            return None
        
        try:
            # Use weight parameter instead of cutoff for NetworkX 3.x compatibility
            path_ids = nx.shortest_path(self._graph, source_id, target_id)
            # Check if path exceeds max_depth
            if len(path_ids) > max_depth + 1:
                return None
        except nx.NetworkXNoPath:
            return None
        
        if len(path_ids) < 2:
            return None
        
        # Build relationships list
        relationships = []
        for i in range(len(path_ids) - 1):
            edge_data = self._graph.get_edge_data(path_ids[i], path_ids[i + 1])
            if edge_data:
                kind = edge_data.get("kind", "unknown")
                rel = Relationship(
                    source_id=path_ids[i],
                    target_id=path_ids[i + 1],
                    kind=RelationshipKind(kind) if kind in [k.value for k in RelationshipKind] else RelationshipKind.CALLS,
                    metadata=edge_data,
                )
                relationships.append(rel)
        
        return GraphPath(entities=path_ids, relationships=relationships)
    
    def impact_analysis(self, entity_id: str, change_type: str = "modify", depth: int = 3) -> ImpactResult:
        """
        Analyze the impact of changing an entity.
        
        Args:
            entity_id: The entity being changed
            change_type: Type of change ("modify", "delete", "add")
            depth: Depth of impact analysis
            
        Returns:
            ImpactResult with affected entities and risk levels
        """
        if entity_id not in self._entity_index:
            return ImpactResult(
                entity_id=entity_id,
                change_type=change_type,
                affected_entities=[],
                risk_levels={},
                test_files=[],
                depth=depth,
                warnings=[f"Entity {entity_id} not found"],
            )
        
        # Find all entities that depend on this one (incoming relationships)
        affected = self.traverse(entity_id, direction="incoming", depth=depth)
        affected_ids = [e.id for e in affected]
        
        # Calculate risk levels
        risk_levels = {}
        for entity in affected:
            # Direct dependencies are high risk
            if self._graph.has_edge(entity.id, entity_id):
                risk_levels[entity.id] = "high"
            # Test files are medium risk
            elif entity.kind == EntityKind.TEST:
                risk_levels[entity.id] = "low"
            else:
                risk_levels[entity.id] = "medium"
        
        # Find test files
        test_files = []
        for entity in affected:
            if entity.kind == EntityKind.TEST:
                test_files.append(entity.file_path)
        
        # Check for circular dependencies
        warnings = []
        if self._has_cycle_involving(entity_id):
            warnings.append(f"Circular dependency detected involving {entity_id}")
        
        return ImpactResult(
            entity_id=entity_id,
            change_type=change_type,
            affected_entities=affected_ids,
            risk_levels=risk_levels,
            test_files=test_files,
            depth=depth,
            warnings=warnings,
        )
    
    def _has_cycle_involving(self, entity_id: str) -> bool:
        """Check if there's a cycle involving the given entity."""
        if entity_id not in self._entity_index:
            return False
        
        try:
            cycles = list(nx.simple_cycles(self._graph))
            for cycle in cycles:
                if entity_id in cycle:
                    return True
        except nx.NetworkXNoCycle:
            return False
        
        return False
    
    def find_cycles(self) -> list[list[str]]:
        """
        Find all cycles in the graph.
        
        Returns:
            List of cycles (each cycle is a list of entity IDs)
        """
        try:
            return list(nx.simple_cycles(self._graph))
        except nx.NetworkXNoCycle:
            return []
    
    def get_all_entities(self) -> list[Entity]:
        """Get all entities in the graph."""
        return list(self._entity_index.values())
    
    def get_all_relationships(self) -> list[Relationship]:
        """Get all relationships in the graph."""
        return list(self._relationship_index.values())
    
    def clear(self) -> None:
        """Clear all entities and relationships."""
        self._graph.clear()
        self._entity_index.clear()
        self._relationship_index.clear()
        self._metadata = GraphMetadata()
    
    def to_dict(self) -> dict[str, Any]:
        """Convert graph to dictionary for serialization."""
        return {
            "entities": [e.to_dict() for e in self.get_all_entities()],
            "relationships": [r.to_dict() for r in self.get_all_relationships()],
            "metadata": self._metadata.to_dict(),
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "KnowledgeGraph":
        """Create graph from dictionary."""
        graph = cls()
        
        for entity_data in data.get("entities", []):
            entity = Entity.from_dict(entity_data)
            graph.add_entity(entity)
        
        for rel_data in data.get("relationships", []):
            rel = Relationship.from_dict(rel_data)
            graph.add_relationship(rel)
        
        if "metadata" in data:
            meta = data["metadata"]
            graph._metadata = GraphMetadata(
                total_entities=meta.get("total_entities", 0),
                total_relationships=meta.get("total_relationships", 0),
                version=meta.get("version", "4.0.0"),
            )
        
        return graph