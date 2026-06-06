#!/usr/bin/env python3
"""
Graph builder for KB MCP v4.

Builds knowledge graph from analyzer output.
"""

from pathlib import Path
from typing import Any

from .engine import KnowledgeGraph
from .models import Entity, EntityKind, Relationship, RelationshipKind
from .store import GraphStore


class GraphBuilder:
    """
    Builds KnowledgeGraph from analyzer output.
    
    This class takes entities and relationships extracted by language
    analyzers and constructs a coherent knowledge graph.
    """
    
    def __init__(self, graph: KnowledgeGraph | None = None):
        """
        Initialize graph builder.
        
        Args:
            graph: Optional existing graph to build upon
        """
        self.graph = graph or KnowledgeGraph()
    
    def add_entities(self, entities: list[Entity]) -> None:
        """
        Add multiple entities to the graph.
        
        Args:
            entities: List of entities to add
        """
        for entity in entities:
            self.graph.add_entity(entity)
    
    def add_relationships(self, relationships: list[Relationship]) -> None:
        """
        Add multiple relationships to the graph.
        
        Args:
            relationships: List of relationships to add
        """
        for rel in relationships:
            try:
                self.graph.add_relationship(rel)
            except ValueError as e:
                # Skip relationships with missing entities
                # (will be resolved in later passes)
                pass
    
    def build_from_analysis(
        self,
        entities: list[Entity],
        relationships: list[Relationship],
    ) -> KnowledgeGraph:
        """
        Build graph from complete analysis results.
        
        Args:
            entities: All entities from analyzer
            relationships: All relationships from analyzer
            
        Returns:
            The constructed KnowledgeGraph
        """
        self.add_entities(entities)
        self.add_relationships(relationships)
        return self.graph
    
    def save(self, db_path: Path | str) -> None:
        """
        Save graph to SQLite database.
        
        Args:
            db_path: Path to database file
        """
        store = GraphStore(db_path)
        store.save(self.graph)
    
    @classmethod
    def load(cls, db_path: Path | str) -> "GraphBuilder":
        """
        Load graph from SQLite database.
        
        Args:
            db_path: Path to database file
            
        Returns:
            GraphBuilder with loaded graph
        """
        store = GraphStore(db_path)
        graph = store.load()
        
        if graph is None:
            graph = KnowledgeGraph()
        
        return cls(graph)
    
    def update_metadata(self, **kwargs: Any) -> None:
        """
        Update graph metadata.
        
        Args:
            **kwargs: Metadata key-value pairs
        """
        for key, value in kwargs.items():
            if hasattr(self.graph.metadata, key):
                setattr(self.graph.metadata, key, value)
            else:
                self.graph.metadata.languages.append(key)
    
    def get_or_create_entity(self, entity_id: str) -> Entity | None:
        """
        Get existing entity or create placeholder.
        
        Args:
            entity_id: The entity ID
            
        Returns:
            Existing entity or None if creation failed
        """
        existing = self.graph.get_entity(entity_id)
        if existing:
            return existing
        
        # Parse entity ID to create placeholder
        # Format: {file_path}:{line_start}:{name}
        parts = entity_id.rsplit(":", 2)
        if len(parts) != 3:
            return None
        
        file_path, line_str, name = parts
        try:
            line = int(line_str)
        except ValueError:
            return None
        
        placeholder = Entity(
            id=entity_id,
            kind=EntityKind.FUNCTION,  # Default kind
            name=name,
            file_path=file_path,
            line_start=line,
            line_end=line,
            metadata={"placeholder": True},
        )
        
        self.graph.add_entity(placeholder)
        return placeholder