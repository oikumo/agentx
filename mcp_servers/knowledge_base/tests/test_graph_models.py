#!/usr/bin/env python3
"""
Unit tests for Knowledge Graph models.
"""

import pytest
from datetime import datetime

from graph.models import (
    DocstringInfo,
    Entity,
    EntityKind,
    GraphMetadata,
    GraphPath,
    ImpactResult,
    Relationship,
    RelationshipKind,
)


class TestEntity:
    """Tests for Entity model."""
    
    def test_create_entity(self):
        """Test creating a basic entity."""
        entity = Entity(
            id="test.py:10:TestClass",
            kind=EntityKind.CLASS,
            name="TestClass",
            file_path="/path/to/test.py",
            line_start=10,
            line_end=20,
        )
        
        assert entity.id == "test.py:10:TestClass"
        assert entity.kind == EntityKind.CLASS
        assert entity.name == "TestClass"
        assert entity.line_start == 10
        assert entity.line_end == 20
    
    def test_entity_with_docstring(self):
        """Test entity with docstring info."""
        docstring = DocstringInfo(
            summary="A test class",
            description="This is a longer description",
            args={"arg1": "First argument"},
            returns="A value",
        )
        
        entity = Entity(
            id="test.py:10:test_func",
            kind=EntityKind.FUNCTION,
            name="test_func",
            file_path="/path/to/test.py",
            line_start=10,
            line_end=15,
            docstring=docstring,
        )
        
        assert entity.docstring.summary == "A test class"
        assert entity.docstring.args["arg1"] == "First argument"
        assert entity.docstring.returns == "A value"
    
    def test_entity_to_dict(self):
        """Test entity serialization to dict."""
        entity = Entity(
            id="test.py:10:MyClass",
            kind=EntityKind.CLASS,
            name="MyClass",
            file_path="/path/to/test.py",
            line_start=10,
            line_end=20,
            metadata={"layer": "model"},
        )
        
        data = entity.to_dict()
        
        assert data["id"] == "test.py:10:MyClass"
        assert data["kind"] == "class"
        assert data["name"] == "MyClass"
        assert data["metadata"]["layer"] == "model"
    
    def test_entity_from_dict(self):
        """Test entity deserialization from dict."""
        data = {
            "id": "test.py:10:MyClass",
            "kind": "class",
            "name": "MyClass",
            "file_path": "/path/to/test.py",
            "line_start": 10,
            "line_end": 20,
            "docstring": None,
            "metadata": {"layer": "model"},
            "created_at": datetime.now().isoformat(),
        }
        
        entity = Entity.from_dict(data)
        
        assert entity.id == "test.py:10:MyClass"
        assert entity.kind == EntityKind.CLASS
        assert entity.metadata["layer"] == "model"
    
    def test_entity_roundtrip(self):
        """Test entity serialize/deserialize roundtrip."""
        original = Entity(
            id="test.py:10:MyClass",
            kind=EntityKind.CLASS,
            name="MyClass",
            file_path="/path/to/test.py",
            line_start=10,
            line_end=20,
            metadata={"layer": "model", "pattern": ["factory"]},
        )
        
        data = original.to_dict()
        restored = Entity.from_dict(data)
        
        assert restored.id == original.id
        assert restored.kind == original.kind
        assert restored.name == original.name
        assert restored.metadata == original.metadata


class TestRelationship:
    """Tests for Relationship model."""
    
    def test_create_relationship(self):
        """Test creating a basic relationship."""
        rel = Relationship(
            source_id="module_a.py:10:ClassA",
            target_id="module_b.py:20:ClassB",
            kind=RelationshipKind.EXTENDS,
        )
        
        assert rel.source_id == "module_a.py:10:ClassA"
        assert rel.target_id == "module_b.py:20:ClassB"
        assert rel.kind == RelationshipKind.EXTENDS
    
    def test_relationship_self_reference_fails(self):
        """Test that self-referencing relationships fail."""
        with pytest.raises(ValueError, match="same source and target"):
            Relationship(
                source_id="test.py:10:Class",
                target_id="test.py:10:Class",
                kind=RelationshipKind.CALLS,
            )
    
    def test_relationship_to_dict(self):
        """Test relationship serialization."""
        rel = Relationship(
            source_id="a.py:1:func_a",
            target_id="b.py:2:func_b",
            kind=RelationshipKind.CALLS,
            metadata={"confidence": 0.95},
        )
        
        data = rel.to_dict()
        
        assert data["source_id"] == "a.py:1:func_a"
        assert data["target_id"] == "b.py:2:func_b"
        assert data["kind"] == "calls"
        assert data["metadata"]["confidence"] == 0.95
    
    def test_relationship_from_dict(self):
        """Test relationship deserialization."""
        data = {
            "id": 1,
            "source_id": "a.py:1:func_a",
            "target_id": "b.py:2:func_b",
            "kind": "calls",
            "metadata": {"confidence": 0.95},
        }
        
        rel = Relationship.from_dict(data)
        
        assert rel.id == 1
        assert rel.kind == RelationshipKind.CALLS
        assert rel.metadata["confidence"] == 0.95


class TestRelationshipKind:
    """Tests for RelationshipKind enum."""
    
    def test_all_relationship_kinds(self):
        """Test all relationship kinds are defined."""
        kinds = [
            "imports", "extends", "implements", "composes",
            "calls", "creates", "passes_to", "defines",
            "tests", "configures", "routes", "emits_event",
            "listens_event", "decorates", "instantiated_by", "called_by",
        ]
        
        for kind in kinds:
            assert RelationshipKind(kind) is not None


class TestEntityKind:
    """Tests for EntityKind enum."""
    
    def test_all_entity_kinds(self):
        """Test all entity kinds are defined."""
        kinds = [
            "class", "function", "method", "module",
            "interface", "config", "test", "package",
        ]
        
        for kind in kinds:
            assert EntityKind(kind) is not None


class TestDocstringInfo:
    """Tests for DocstringInfo model."""
    
    def test_create_docstring(self):
        """Test creating docstring info."""
        doc = DocstringInfo(
            summary="Brief summary",
            description="Longer description",
            args={"x": "First param", "y": "Second param"},
            returns="Result value",
            raises=["ValueError", "TypeError"],
            examples=["Example 1"],
        )
        
        assert doc.summary == "Brief summary"
        assert len(doc.args) == 2
        assert len(doc.raises) == 2
        assert len(doc.examples) == 1
    
    def test_empty_docstring(self):
        """Test empty docstring defaults."""
        doc = DocstringInfo()
        
        assert doc.summary == ""
        assert doc.args == {}
        assert doc.returns is None
        assert doc.raises == []
        assert doc.examples == []


class TestGraphMetadata:
    """Tests for GraphMetadata model."""
    
    def test_create_metadata(self):
        """Test creating graph metadata."""
        meta = GraphMetadata(
            total_entities=100,
            total_relationships=250,
            version="4.0.0",
            project_root="/path/to/project",
            languages=["python", "javascript"],
        )
        
        assert meta.total_entities == 100
        assert meta.total_relationships == 250
        assert meta.version == "4.0.0"
        assert len(meta.languages) == 2
    
    def test_metadata_to_dict(self):
        """Test metadata serialization."""
        meta = GraphMetadata(
            total_entities=50,
            total_relationships=120,
        )
        
        data = meta.to_dict()
        
        assert data["total_entities"] == 50
        assert data["total_relationships"] == 120
        assert data["version"] == "4.0.0"


class TestImpactResult:
    """Tests for ImpactResult model."""
    
    def test_create_impact_result(self):
        """Test creating impact analysis result."""
        result = ImpactResult(
            entity_id="test.py:10:MyClass",
            change_type="modify",
            affected_entities=["a.py:1:FuncA", "b.py:2:FuncB"],
            risk_levels={"a.py:1:FuncA": "high", "b.py:2:FuncB": "medium"},
            test_files=["test_module.py"],
            depth=3,
            warnings=["Circular dependency detected"],
        )
        
        assert result.entity_id == "test.py:10:MyClass"
        assert result.change_type == "modify"
        assert len(result.affected_entities) == 2
        assert result.risk_levels["a.py:1:FuncA"] == "high"
        assert len(result.warnings) == 1
    
    def test_impact_result_to_dict(self):
        """Test impact result serialization."""
        result = ImpactResult(
            entity_id="test.py:10:MyClass",
            change_type="delete",
            affected_entities=[],
            risk_levels={},
            test_files=[],
            depth=2,
        )
        
        data = result.to_dict()
        
        assert data["entity_id"] == "test.py:10:MyClass"
        assert data["change_type"] == "delete"
        assert data["depth"] == 2


class TestGraphPath:
    """Tests for GraphPath model."""
    
    def test_create_graph_path(self):
        """Test creating a graph path."""
        rel = Relationship(
            source_id="a.py:1:func_a",
            target_id="b.py:2:func_b",
            kind=RelationshipKind.CALLS,
        )
        
        path = GraphPath(
            entities=["a.py:1:func_a", "b.py:2:func_b"],
            relationships=[rel],
            total_weight=1.0,
        )
        
        assert len(path.entities) == 2
        assert len(path.relationships) == 1
        assert path.total_weight == 1.0
    
    def test_graph_path_to_dict(self):
        """Test path serialization."""
        rel = Relationship(
            source_id="a.py:1:func_a",
            target_id="b.py:2:func_b",
            kind=RelationshipKind.CALLS,
        )
        
        path = GraphPath(
            entities=["a.py:1:func_a", "b.py:2:func_b"],
            relationships=[rel],
        )
        
        data = path.to_dict()
        
        assert len(data["entities"]) == 2
        assert len(data["relationships"]) == 1
        assert data["relationships"][0]["kind"] == "calls"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])