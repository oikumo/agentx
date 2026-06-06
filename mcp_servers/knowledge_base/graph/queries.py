#!/usr/bin/env python3
"""
High-level graph query operations for KB MCP v4.

Provides convenient query methods for common graph navigation patterns.
"""

from typing import Any, Optional

from .engine import KnowledgeGraph
from .models import Entity, EntityKind, GraphPath, Relationship, RelationshipKind


class GraphQueries:
    """
    High-level query operations for KnowledgeGraph.
    
    These methods provide convenient access to common graph navigation
    patterns used by agents.
    """
    
    def __init__(self, graph: KnowledgeGraph):
        """
        Initialize query operations.
        
        Args:
            graph: The KnowledgeGraph to query
        """
        self.graph = graph
    
    def find_callers(self, entity_id: str, max_depth: int = 3) -> list[Entity]:
        """
        Find all entities that call this entity.
        
        Args:
            entity_id: The entity to find callers for
            max_depth: Maximum depth to traverse
            
        Returns:
            List of caller entities
        """
        return self.graph.traverse(
            target_id=entity_id,
            direction="incoming",
            relationship_kind="calls",
            depth=max_depth,
        )
    
    def find_callees(self, entity_id: str, max_depth: int = 3) -> list[Entity]:
        """
        Find all entities called by this entity.
        
        Args:
            entity_id: The entity to find callees for
            max_depth: Maximum depth to traverse
            
        Returns:
            List of callee entities
        """
        return self.graph.traverse(
            target_id=entity_id,
            direction="outgoing",
            relationship_kind="calls",
            depth=max_depth,
        )
    
    def find_dependencies(self, entity_id: str, max_depth: int = 3) -> list[Entity]:
        """
        Find all entities this entity depends on (imports, extends, composes).
        
        Args:
            entity_id: The entity to find dependencies for
            max_depth: Maximum depth to traverse
            
        Returns:
            List of dependency entities
        """
        # Get all incoming relationships (things this entity depends on)
        all_deps = []
        for rel_kind in ["imports", "extends", "composes", "implements"]:
            deps = self.graph.traverse(
                target_id=entity_id,
                direction="outgoing",
                relationship_kind=rel_kind,
                depth=max_depth,
            )
            all_deps.extend(deps)
        
        # Remove duplicates
        seen = set()
        unique_deps = []
        for dep in all_deps:
            if dep.id not in seen:
                seen.add(dep.id)
                unique_deps.append(dep)
        
        return unique_deps
    
    def find_dependents(self, entity_id: str, max_depth: int = 3) -> list[Entity]:
        """
        Find all entities that depend on this entity.
        
        Args:
            entity_id: The entity to find dependents for
            max_depth: Maximum depth to traverse
            
        Returns:
            List of dependent entities
        """
        # Get all incoming relationships
        all_dependents = []
        for rel_kind in ["imports", "extends", "composes", "implements", "calls"]:
            dependents = self.graph.traverse(
                target_id=entity_id,
                direction="incoming",
                relationship_kind=rel_kind,
                depth=max_depth,
            )
            all_dependents.extend(dependents)
        
        # Remove duplicates
        seen = set()
        unique_dependents = []
        for dep in all_dependents:
            if dep.id not in seen:
                seen.add(dep.id)
                unique_dependents.append(dep)
        
        return unique_dependents
    
    def find_tests_for(self, entity_id: str) -> list[Entity]:
        """
        Find all test entities that test this entity.
        
        Args:
            entity_id: The entity to find tests for
            
        Returns:
            List of test entities
        """
        return self.graph.traverse(
            target_id=entity_id,
            direction="incoming",
            relationship_kind="tests",
            depth=1,
        )
    
    def find_tests_by(self, test_entity_id: str) -> list[Entity]:
        """
        Find all entities tested by this test.
        
        Args:
            test_entity_id: The test entity
            
        Returns:
            List of tested entities
        """
        return self.graph.traverse(
            target_id=test_entity_id,
            direction="outgoing",
            relationship_kind="tests",
            depth=1,
        )
    
    def find_inheritance_chain(self, entity_id: str) -> list[Entity]:
        """
        Find the full inheritance chain for a class.
        
        Args:
            entity_id: The class entity
            
        Returns:
            List of parent classes in inheritance order
        """
        return self.graph.traverse(
            target_id=entity_id,
            direction="outgoing",
            relationship_kind="extends",
            depth=10,
        )
    
    def find_composition_tree(self, entity_id: str, max_depth: int = 3) -> list[Entity]:
        """
        Find all components composed by this entity.
        
        Args:
            entity_id: The entity to find composition tree for
            max_depth: Maximum depth to traverse
            
        Returns:
            List of composed entities
        """
        return self.graph.traverse(
            target_id=entity_id,
            direction="outgoing",
            relationship_kind="composes",
            depth=max_depth,
        )
    
    def find_path_between(
        self,
        source_id: str,
        target_id: str,
        max_depth: int = 10,
    ) -> Optional[GraphPath]:
        """
        Find the shortest path between two entities.
        
        Args:
            source_id: Starting entity
            target_id: Target entity
            max_depth: Maximum path length
            
        Returns:
            GraphPath or None if no path exists
        """
        return self.graph.find_path(source_id, target_id, max_depth)
    
    def find_entry_points(self) -> list[Entity]:
        """
        Find likely entry points in the codebase.
        
        Entry points are:
        - Functions named "main"
        - Functions with @app.route or similar decorators
        - Module-level functions with no callers
        
        Returns:
            List of entry point entities
        """
        entry_points = []
        
        for entity in self.graph.get_all_entities():
            # Look for main functions
            if entity.kind == EntityKind.FUNCTION and entity.name == "main":
                entry_points.append(entity)
                continue
            
            # Look for functions with no callers (likely entry points)
            if entity.kind in (EntityKind.FUNCTION, EntityKind.METHOD):
                callers = self.find_callers(entity.id, max_depth=1)
                if not callers:
                    # Check if it's in a controller or similar
                    if "controller" in entity.file_path.lower():
                        entry_points.append(entity)
        
        return entry_points
    
    def find_components_by_layer(self, layer: str) -> list[Entity]:
        """
        Find all entities in a specific architecture layer.
        
        Args:
            layer: Layer name (e.g., "model", "view", "controller")
            
        Returns:
            List of entities in that layer
        """
        return [
            entity for entity in self.graph.get_all_entities()
            if entity.metadata.get("layer") == layer
        ]
    
    def find_patterns(self, pattern_name: str) -> list[Entity]:
        """
        Find all entities using a specific design pattern.
        
        Args:
            pattern_name: Pattern name (e.g., "factory", "singleton", "observer")
            
        Returns:
            List of entities using this pattern
        """
        return [
            entity for entity in self.graph.get_all_entities()
            if pattern_name.lower() in [p.lower() for p in entity.metadata.get("pattern", [])]
        ]
    
    def find_high_complexity(self, threshold: float = 0.7) -> list[Entity]:
        """
        Find entities marked as high complexity.
        
        Args:
            threshold: Minimum complexity score
            
        Returns:
            List of high-complexity entities
        """
        return [
            entity for entity in self.graph.get_all_entities()
            if entity.metadata.get("complexity", 0) >= threshold
        ]
    
    def find_recently_modified(self, limit: int = 10) -> list[Entity]:
        """
        Find most recently modified entities.
        
        Args:
            limit: Maximum number of entities to return
            
        Returns:
            List of recently modified entities
        """
        entities = self.graph.get_all_entities()
        # Sort by created_at (which reflects when added to KB)
        entities.sort(key=lambda e: e.created_at, reverse=True)
        return entities[:limit]
    
    def search_by_name(self, query: str, case_sensitive: bool = False) -> list[Entity]:
        """
        Search for entities by name.
        
        Args:
            query: Search query (supports substring matching)
            case_sensitive: Whether search is case-sensitive
            
        Returns:
            List of matching entities
        """
        results = []
        
        for entity in self.graph.get_all_entities():
            name = entity.name if case_sensitive else entity.name.lower()
            search_query = query if case_sensitive else query.lower()
            
            if search_query in name:
                results.append(entity)
        
        # Sort by relevance (exact match first, then by name length)
        results.sort(key=lambda e: (
            e.name.lower() != query.lower(),  # Exact matches first
            len(e.name),  # Shorter names first
        ))
        
        return results
    
    def get_statistics(self) -> dict[str, Any]:
        """
        Get graph statistics.
        
        Returns:
            Dictionary with graph statistics
        """
        entities = self.graph.get_all_entities()
        relationships = self.graph.get_all_relationships()
        
        # Count by kind
        by_kind = {}
        for entity in entities:
            kind = entity.kind.value if isinstance(entity.kind, EntityKind) else entity.kind
            by_kind[kind] = by_kind.get(kind, 0) + 1
        
        # Count by relationship kind
        by_rel_kind = {}
        for rel in relationships:
            kind = rel.kind.value if isinstance(rel.kind, RelationshipKind) else rel.kind
            by_rel_kind[kind] = by_rel_kind.get(kind, 0) + 1
        
        # Count by layer
        by_layer = {}
        for entity in entities:
            layer = entity.metadata.get("layer", "unknown")
            by_layer[layer] = by_layer.get(layer, 0) + 1
        
        return {
            "total_entities": len(entities),
            "total_relationships": len(relationships),
            "by_kind": by_kind,
            "by_relationship_kind": by_rel_kind,
            "by_layer": by_layer,
            "avg_relationships_per_entity": len(relationships) / len(entities) if entities else 0,
            "has_cycles": len(self.graph.find_cycles()) > 0,
        }