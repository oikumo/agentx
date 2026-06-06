#!/usr/bin/env python3
"""
Unit tests for Knowledge Graph Engine.
"""

import pytest
import tempfile
from pathlib import Path

from graph.engine import KnowledgeGraph
from graph.store import GraphStore
from graph.models import (
    Entity,
    EntityKind,
    Relationship,
    RelationshipKind,
)


class TestKnowledgeGraph:
    """Tests for KnowledgeGraph class."""
    
    @pytest.fixture
    def graph(self):
        """Create an empty graph for testing."""
        return KnowledgeGraph()
    
    @pytest.fixture
    def sample_entities(self):
        """Create sample entities for testing."""
        return [
            Entity(
                id="module_a.py:10:ClassA",
                kind=EntityKind.CLASS,
                name="ClassA",
                file_path="/path/to/module_a.py",
                line_start=10,
                line_end=20,
                metadata={"layer": "model"},
            ),
            Entity(
                id="module_b.py:30:ClassB",
                kind=EntityKind.CLASS,
                name="ClassB",
                file_path="/path/to/module_b.py",
                line_start=30,
                line_end=40,
                metadata={"layer": "model"},
            ),
            Entity(
                id="module_c.py:50:func_c",
                kind=EntityKind.FUNCTION,
                name="func_c",
                file_path="/path/to/module_c.py",
                line_start=50,
                line_end=60,
                metadata={"layer": "controller"},
            ),
        ]
    
    def test_add_entity(self, graph, sample_entities):
        """Test adding entities to graph."""
        entity = sample_entities[0]
        graph.add_entity(entity)
        
        assert graph.num_entities == 1
        assert graph.get_entity(entity.id) == entity
    
    def test_add_multiple_entities(self, graph, sample_entities):
        """Test adding multiple entities."""
        for entity in sample_entities:
            graph.add_entity(entity)
        
        assert graph.num_entities == 3
        assert graph.get_entity("module_a.py:10:ClassA") is not None
        assert graph.get_entity("module_b.py:30:ClassB") is not None
        assert graph.get_entity("module_c.py:50:func_c") is not None
    
    def test_get_nonexistent_entity(self, graph):
        """Test getting entity that doesn't exist."""
        assert graph.get_entity("nonexistent") is None
    
    def test_remove_entity(self, graph, sample_entities):
        """Test removing an entity."""
        entity = sample_entities[0]
        graph.add_entity(entity)
        
        assert graph.num_entities == 1
        graph.remove_entity(entity.id)
        assert graph.num_entities == 0
        assert graph.get_entity(entity.id) is None
    
    def test_add_relationship(self, graph, sample_entities):
        """Test adding relationship between entities."""
        for entity in sample_entities:
            graph.add_entity(entity)
        
        rel = Relationship(
            source_id="module_a.py:10:ClassA",
            target_id="module_b.py:30:ClassB",
            kind=RelationshipKind.EXTENDS,
        )
        graph.add_relationship(rel)
        
        assert graph.num_relationships == 1
        rels = graph.get_relationships("module_a.py:10:ClassA")
        assert len(rels) == 1
        assert rels[0].kind == RelationshipKind.EXTENDS
    
    def test_add_relationship_missing_entity_fails(self, graph):
        """Test that adding relationship with missing entity fails."""
        rel = Relationship(
            source_id="nonexistent1",
            target_id="nonexistent2",
            kind=RelationshipKind.CALLS,
        )
        
        with pytest.raises(ValueError):
            graph.add_relationship(rel)
    
    def test_get_relationships_incoming(self, graph, sample_entities):
        """Test getting incoming relationships."""
        for entity in sample_entities:
            graph.add_entity(entity)
        
        rel = Relationship(
            source_id="module_a.py:10:ClassA",
            target_id="module_b.py:30:ClassB",
            kind=RelationshipKind.EXTENDS,
        )
        graph.add_relationship(rel)
        
        rels = graph.get_relationships("module_b.py:30:ClassB", direction="incoming")
        assert len(rels) == 1
        assert rels[0].source_id == "module_a.py:10:ClassA"
    
    def test_get_relationships_outgoing(self, graph, sample_entities):
        """Test getting outgoing relationships."""
        for entity in sample_entities:
            graph.add_entity(entity)
        
        rel = Relationship(
            source_id="module_a.py:10:ClassA",
            target_id="module_b.py:30:ClassB",
            kind=RelationshipKind.CALLS,
        )
        graph.add_relationship(rel)
        
        rels = graph.get_relationships("module_a.py:10:ClassA", direction="outgoing")
        assert len(rels) == 1
        assert rels[0].target_id == "module_b.py:30:ClassB"
    
    def test_traverse_outgoing(self, graph, sample_entities):
        """Test traversing graph in outgoing direction."""
        for entity in sample_entities:
            graph.add_entity(entity)
        
        rel1 = Relationship(
            source_id="module_a.py:10:ClassA",
            target_id="module_b.py:30:ClassB",
            kind=RelationshipKind.CALLS,
        )
        rel2 = Relationship(
            source_id="module_b.py:30:ClassB",
            target_id="module_c.py:50:func_c",
            kind=RelationshipKind.CALLS,
        )
        graph.add_relationship(rel1)
        graph.add_relationship(rel2)
        
        # Traverse from A with depth=2
        results = graph.traverse("module_a.py:10:ClassA", direction="outgoing", depth=2)
        assert len(results) == 2
        assert results[0].id == "module_b.py:30:ClassB"
        assert results[1].id == "module_c.py:50:func_c"
    
    def test_traverse_with_depth_limit(self, graph, sample_entities):
        """Test traversal respects depth limit."""
        for entity in sample_entities:
            graph.add_entity(entity)
        
        rel1 = Relationship(
            source_id="module_a.py:10:ClassA",
            target_id="module_b.py:30:ClassB",
            kind=RelationshipKind.CALLS,
        )
        rel2 = Relationship(
            source_id="module_b.py:30:ClassB",
            target_id="module_c.py:50:func_c",
            kind=RelationshipKind.CALLS,
        )
        graph.add_relationship(rel1)
        graph.add_relationship(rel2)
        
        # Traverse from A with depth=1
        results = graph.traverse("module_a.py:10:ClassA", direction="outgoing", depth=1)
        assert len(results) == 1
        assert results[0].id == "module_b.py:30:ClassB"
    
    def test_traverse_with_relationship_filter(self, graph, sample_entities):
        """Test traversal with relationship kind filter."""
        for entity in sample_entities:
            graph.add_entity(entity)
        
        rel1 = Relationship(
            source_id="module_a.py:10:ClassA",
            target_id="module_b.py:30:ClassB",
            kind=RelationshipKind.CALLS,
        )
        rel2 = Relationship(
            source_id="module_a.py:10:ClassA",
            target_id="module_c.py:50:func_c",
            kind=RelationshipKind.COMPOSES,
        )
        graph.add_relationship(rel1)
        graph.add_relationship(rel2)
        
        # Filter by CALLS only
        results = graph.traverse(
            "module_a.py:10:ClassA",
            direction="outgoing",
            relationship_kind="calls",
            depth=1,
        )
        assert len(results) == 1
        assert results[0].id == "module_b.py:30:ClassB"
    
    def test_find_path(self, graph, sample_entities):
        """Test finding shortest path between entities."""
        for entity in sample_entities:
            graph.add_entity(entity)
        
        rel1 = Relationship(
            source_id="module_a.py:10:ClassA",
            target_id="module_b.py:30:ClassB",
            kind=RelationshipKind.CALLS,
        )
        rel2 = Relationship(
            source_id="module_b.py:30:ClassB",
            target_id="module_c.py:50:func_c",
            kind=RelationshipKind.CALLS,
        )
        graph.add_relationship(rel1)
        graph.add_relationship(rel2)
        
        path = graph.find_path("module_a.py:10:ClassA", "module_c.py:50:func_c")
        
        assert path is not None
        assert len(path.entities) == 3
        assert path.entities[0] == "module_a.py:10:ClassA"
        assert path.entities[-1] == "module_c.py:50:func_c"
    
    def test_find_path_no_path(self, graph, sample_entities):
        """Test finding path when none exists."""
        for entity in sample_entities:
            graph.add_entity(entity)
        
        path = graph.find_path("module_a.py:10:ClassA", "module_c.py:50:func_c")
        
        assert path is None
    
    def test_impact_analysis(self, graph, sample_entities):
        """Test impact analysis for entity modification."""
        for entity in sample_entities:
            graph.add_entity(entity)
        
        rel = Relationship(
            source_id="module_b.py:30:ClassB",
            target_id="module_a.py:10:ClassA",
            kind=RelationshipKind.CALLS,
        )
        graph.add_relationship(rel)
        
        result = graph.impact_analysis("module_a.py:10:ClassA", change_type="modify", depth=1)
        
        assert result.entity_id == "module_a.py:10:ClassA"
        assert result.change_type == "modify"
        assert "module_b.py:30:ClassB" in result.affected_entities
        assert result.risk_levels["module_b.py:30:ClassB"] == "high"
    
    def test_find_cycles(self, graph, sample_entities):
        """Test cycle detection."""
        for entity in sample_entities:
            graph.add_entity(entity)
        
        # Create a cycle: A -> B -> C -> A
        rel1 = Relationship(
            source_id="module_a.py:10:ClassA",
            target_id="module_b.py:30:ClassB",
            kind=RelationshipKind.CALLS,
        )
        rel2 = Relationship(
            source_id="module_b.py:30:ClassB",
            target_id="module_c.py:50:func_c",
            kind=RelationshipKind.CALLS,
        )
        rel3 = Relationship(
            source_id="module_c.py:50:func_c",
            target_id="module_a.py:10:ClassA",
            kind=RelationshipKind.CALLS,
        )
        graph.add_relationship(rel1)
        graph.add_relationship(rel2)
        graph.add_relationship(rel3)
        
        cycles = graph.find_cycles()
        assert len(cycles) > 0
    
    def test_clear_graph(self, graph, sample_entities):
        """Test clearing all graph data."""
        for entity in sample_entities:
            graph.add_entity(entity)
        
        rel = Relationship(
            source_id="module_a.py:10:ClassA",
            target_id="module_b.py:30:ClassB",
            kind=RelationshipKind.CALLS,
        )
        graph.add_relationship(rel)
        
        assert graph.num_entities == 3
        assert graph.num_relationships == 1
        
        graph.clear()
        
        assert graph.num_entities == 0
        assert graph.num_relationships == 0
    
    def test_to_dict(self, graph, sample_entities):
        """Test graph serialization to dict."""
        for entity in sample_entities:
            graph.add_entity(entity)
        
        data = graph.to_dict()
        
        assert "entities" in data
        assert "relationships" in data
        assert "metadata" in data
        assert len(data["entities"]) == 3
    
    def test_from_dict(self, sample_entities):
        """Test graph deserialization from dict."""
        original = KnowledgeGraph()
        for entity in sample_entities:
            original.add_entity(entity)
        
        data = original.to_dict()
        restored = KnowledgeGraph.from_dict(data)
        
        assert restored.num_entities == original.num_entities
        assert restored.get_entity("module_a.py:10:ClassA") is not None


class TestGraphStore:
    """Tests for GraphStore persistence."""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database file."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = Path(f.name)
        yield db_path
        db_path.unlink(missing_ok=True)
    
    @pytest.fixture
    def sample_graph(self):
        """Create a graph with sample data."""
        graph = KnowledgeGraph()
        
        entities = [
            Entity(
                id="test.py:10:ClassA",
                kind=EntityKind.CLASS,
                name="ClassA",
                file_path="/path/to/test.py",
                line_start=10,
                line_end=20,
                metadata={"layer": "model"},
            ),
            Entity(
                id="test.py:30:func_b",
                kind=EntityKind.FUNCTION,
                name="func_b",
                file_path="/path/to/test.py",
                line_start=30,
                line_end=40,
            ),
        ]
        
        for entity in entities:
            graph.add_entity(entity)
        
        rel = Relationship(
            source_id="test.py:30:func_b",
            target_id="test.py:10:ClassA",
            kind=RelationshipKind.CALLS,
        )
        graph.add_relationship(rel)
        
        return graph
    
    def test_save_and_load(self, temp_db, sample_graph):
        """Test saving and loading graph."""
        store = GraphStore(temp_db)
        store.save(sample_graph)
        
        # Load the graph back
        loaded = store.load()
        
        assert loaded is not None
        assert loaded.num_entities == sample_graph.num_entities
        assert loaded.num_relationships == sample_graph.num_relationships
        assert loaded.get_entity("test.py:10:ClassA") is not None
    
    def test_load_nonexistent_db(self, temp_db):
        """Test loading from nonexistent database."""
        temp_db.unlink()
        store = GraphStore(temp_db)
        
        loaded = store.load()
        assert loaded is None
    
    def test_save_entity_incremental(self, temp_db):
        """Test incrementally saving single entity."""
        store = GraphStore(temp_db)
        
        entity = Entity(
            id="test.py:10:ClassA",
            kind=EntityKind.CLASS,
            name="ClassA",
            file_path="/path/to/test.py",
            line_start=10,
            line_end=20,
        )
        
        store.save_entity(entity)
        assert store.get_entity_count() == 1
    
    def test_save_relationship_incremental(self, temp_db):
        """Test incrementally saving single relationship."""
        store = GraphStore(temp_db)
        
        entity1 = Entity(
            id="test.py:10:ClassA",
            kind=EntityKind.CLASS,
            name="ClassA",
            file_path="/path/to/test.py",
            line_start=10,
            line_end=20,
        )
        entity2 = Entity(
            id="test.py:30:func_b",
            kind=EntityKind.FUNCTION,
            name="func_b",
            file_path="/path/to/test.py",
            line_start=30,
            line_end=40,
        )
        
        store.save_entity(entity1)
        store.save_entity(entity2)
        
        rel = Relationship(
            source_id="test.py:30:func_b",
            target_id="test.py:10:ClassA",
            kind=RelationshipKind.CALLS,
        )
        store.save_relationship(rel)
        
        assert store.get_relationship_count() == 1
    
    def test_remove_entity(self, temp_db):
        """Test removing entity from database."""
        store = GraphStore(temp_db)
        
        entity = Entity(
            id="test.py:10:ClassA",
            kind=EntityKind.CLASS,
            name="ClassA",
            file_path="/path/to/test.py",
            line_start=10,
            line_end=20,
        )
        store.save_entity(entity)
        
        assert store.get_entity_count() == 1
        store.remove_entity("test.py:10:ClassA")
        assert store.get_entity_count() == 0
    
    def test_exists(self, temp_db):
        """Test database existence check."""
        store = GraphStore(temp_db)
        
        # Empty database
        assert not store.exists()
        
        # Add entity
        entity = Entity(
            id="test.py:10:ClassA",
            kind=EntityKind.CLASS,
            name="ClassA",
            file_path="/path/to/test.py",
            line_start=10,
            line_end=20,
        )
        store.save_entity(entity)
        
        assert store.exists()
    
    def test_backup(self, temp_db, tmp_path):
        """Test database backup."""
        store = GraphStore(temp_db)
        
        entity = Entity(
            id="test.py:10:ClassA",
            kind=EntityKind.CLASS,
            name="ClassA",
            file_path="/path/to/test.py",
            line_start=10,
            line_end=20,
        )
        store.save_entity(entity)
        
        backup_path = tmp_path / "backup.db"
        store.backup(backup_path)
        
        assert backup_path.exists()
        assert backup_path.stat().st_size > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])