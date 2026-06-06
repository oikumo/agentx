#!/usr/bin/env python3
"""
Unit tests for Graph Export utilities.
"""

import json
import pytest

from graph.engine import KnowledgeGraph
from graph.export import (
    export_json,
    export_mermaid,
    export_dot,
    export_ascii,
    export_entity_details,
    export_summary,
)
from graph.models import Entity, EntityKind, Relationship, RelationshipKind


class TestExportJson:
    """Tests for JSON export."""
    
    @pytest.fixture
    def sample_graph(self):
        """Create a sample graph."""
        graph = KnowledgeGraph()
        
        entity = Entity(
            id="test.py:10:TestClass",
            kind=EntityKind.CLASS,
            name="TestClass",
            file_path="/path/to/test.py",
            line_start=10,
            line_end=20,
            metadata={"layer": "model"},
        )
        graph.add_entity(entity)
        
        return graph
    
    def test_export_json_basic(self, sample_graph):
        """Test basic JSON export."""
        json_str = export_json(sample_graph)
        
        data = json.loads(json_str)
        assert "entities" in data
        assert "relationships" in data
        assert "metadata" in data
        assert len(data["entities"]) == 1
    
    def test_export_json_pretty(self, sample_graph):
        """Test pretty-printed JSON export."""
        json_str = export_json(sample_graph, pretty=True)
        
        # Pretty print should have newlines and indentation
        assert "\n" in json_str
        assert "  " in json_str
    
    def test_export_json_compact(self, sample_graph):
        """Test compact JSON export."""
        json_str = export_json(sample_graph, pretty=False)
        
        # Compact should be single line
        assert "\n" not in json_str or json_str.count("\n") == 1


class TestExportMermaid:
    """Tests for Mermaid diagram export."""
    
    @pytest.fixture
    def sample_graph(self):
        """Create a sample graph."""
        graph = KnowledgeGraph()
        
        entities = [
            Entity(
                id="a.py:1:ClassA",
                kind=EntityKind.CLASS,
                name="ClassA",
                file_path="/path/to/a.py",
                line_start=1,
                line_end=10,
            ),
            Entity(
                id="b.py:2:ClassB",
                kind=EntityKind.CLASS,
                name="ClassB",
                file_path="/path/to/b.py",
                line_start=2,
                line_end=12,
            ),
        ]
        
        for entity in entities:
            graph.add_entity(entity)
        
        rel = Relationship(
            source_id="a.py:1:ClassA",
            target_id="b.py:2:ClassB",
            kind=RelationshipKind.EXTENDS,
        )
        graph.add_relationship(rel)
        
        return graph
    
    def test_export_mermaid_basic(self, sample_graph):
        """Test basic Mermaid export."""
        mermaid_str = export_mermaid(sample_graph)
        
        assert "graph TD" in mermaid_str
        assert "ClassA" in mermaid_str
        assert "ClassB" in mermaid_str
    
    def test_export_mermaid_with_labels(self, sample_graph):
        """Test Mermaid export with relationship labels."""
        mermaid_str = export_mermaid(sample_graph, show_labels=True)
        
        assert "extends" in mermaid_str
    
    def test_export_mermaid_without_labels(self, sample_graph):
        """Test Mermaid export without relationship labels."""
        mermaid_str = export_mermaid(sample_graph, show_labels=False)
        
        # Should have edge but no label
        assert "-->" in mermaid_str
        assert "|extends|" not in mermaid_str
    
    def test_export_mermaid_with_root(self, sample_graph):
        """Test Mermaid export centered on root entity."""
        mermaid_str = export_mermaid(
            sample_graph,
            root_entity_id="a.py:1:ClassA",
            max_depth=1,
        )
        
        assert "graph TD" in mermaid_str


class TestExportDot:
    """Tests for Graphviz DOT export."""
    
    @pytest.fixture
    def sample_graph(self):
        """Create a sample graph."""
        graph = KnowledgeGraph()
        
        entities = [
            Entity(
                id="a.py:1:ClassA",
                kind=EntityKind.CLASS,
                name="ClassA",
                file_path="/path/to/a.py",
                line_start=1,
                line_end=10,
            ),
            Entity(
                id="b.py:2:func_b",
                kind=EntityKind.FUNCTION,
                name="func_b",
                file_path="/path/to/b.py",
                line_start=2,
                line_end=12,
            ),
        ]
        
        for entity in entities:
            graph.add_entity(entity)
        
        rel = Relationship(
            source_id="a.py:1:ClassA",
            target_id="b.py:2:func_b",
            kind=RelationshipKind.CALLS,
        )
        graph.add_relationship(rel)
        
        return graph
    
    def test_export_dot_basic(self, sample_graph):
        """Test basic DOT export."""
        dot_str = export_dot(sample_graph)
        
        assert "digraph KnowledgeGraph" in dot_str
        assert "layout=dot" in dot_str
    
    def test_export_dot_with_layout(self, sample_graph):
        """Test DOT export with different layout."""
        dot_str = export_dot(sample_graph, layout="neato")
        
        assert "layout=neato" in dot_str
    
    def test_export_dot_node_styling(self, sample_graph):
        """Test that DOT export includes node styling."""
        dot_str = export_dot(sample_graph)
        
        assert "style=filled" in dot_str
        assert "fillcolor" in dot_str


class TestExportAscii:
    """Tests for ASCII tree export."""
    
    @pytest.fixture
    def sample_graph(self):
        """Create a sample graph."""
        graph = KnowledgeGraph()
        
        entities = [
            Entity(
                id="module_a.py:1:ModuleA",
                kind=EntityKind.MODULE,
                name="module_a",
                file_path="/path/to/module_a.py",
                line_start=1,
                line_end=100,
            ),
            Entity(
                id="module_b.py:1:ModuleB",
                kind=EntityKind.MODULE,
                name="module_b",
                file_path="/path/to/module_b.py",
                line_start=1,
                line_end=100,
            ),
        ]
        
        for entity in entities:
            graph.add_entity(entity)
        
        return graph
    
    def test_export_ascii_no_root(self, sample_graph):
        """Test ASCII export without root (shows modules)."""
        ascii_str = export_ascii(sample_graph)
        
        assert "Knowledge Graph" in ascii_str
        assert "module_a" in ascii_str or "ModuleA" in ascii_str
    
    def test_export_ascii_with_root(self, sample_graph):
        """Test ASCII export with root entity."""
        # Add a class entity
        entity = Entity(
            id="test.py:10:TestClass",
            kind=EntityKind.CLASS,
            name="TestClass",
            file_path="/path/to/test.py",
            line_start=10,
            line_end=20,
        )
        sample_graph.add_entity(entity)
        
        rel = Relationship(
            source_id="test.py:10:TestClass",
            target_id="module_a.py:1:ModuleA",
            kind=RelationshipKind.IMPORTS,
        )
        sample_graph.add_relationship(rel)
        
        ascii_str = export_ascii(sample_graph, root_entity_id="test.py:10:TestClass")
        
        assert "TestClass" in ascii_str
        # Check for module_a (could be formatted as module_a or ModuleA depending on display)
        assert "module_a" in ascii_str.lower()
    
    def test_export_ascii_nonexistent_root(self, sample_graph):
        """Test ASCII export with nonexistent root."""
        ascii_str = export_ascii(sample_graph, root_entity_id="nonexistent")
        
        assert "not found" in ascii_str


class TestExportEntityDetails:
    """Tests for entity details export."""
    
    def test_export_entity_details(self):
        """Test exporting entity details."""
        entity = Entity(
            id="test.py:10:TestClass",
            kind=EntityKind.CLASS,
            name="TestClass",
            file_path="/path/to/test.py",
            line_start=10,
            line_end=20,
            metadata={"layer": "model", "pattern": ["factory"]},
        )
        
        relationships = [
            Relationship(
                source_id="other.py:5:OtherClass",
                target_id="test.py:10:TestClass",
                kind=RelationshipKind.EXTENDS,
            ),
        ]
        
        details = export_entity_details(entity, relationships)
        
        assert "TestClass" in details
        assert "class" in details
        assert "test.py" in details
        assert "layer" in details
    
    def test_export_entity_details_with_docstring(self):
        """Test exporting entity with docstring."""
        from graph.models import DocstringInfo
        
        entity = Entity(
            id="test.py:10:TestClass",
            kind=EntityKind.CLASS,
            name="TestClass",
            file_path="/path/to/test.py",
            line_start=10,
            line_end=20,
            docstring=DocstringInfo(summary="A test class"),
        )
        
        details = export_entity_details(entity, [])
        
        assert "A test class" in details


class TestExportSummary:
    """Tests for graph summary export."""
    
    @pytest.fixture
    def sample_graph(self):
        """Create a sample graph."""
        graph = KnowledgeGraph()
        
        entities = [
            Entity(
                id="a.py:1:ClassA",
                kind=EntityKind.CLASS,
                name="ClassA",
                file_path="/path/to/a.py",
                line_start=1,
                line_end=10,
            ),
            Entity(
                id="b.py:2:func_b",
                kind=EntityKind.FUNCTION,
                name="func_b",
                file_path="/path/to/b.py",
                line_start=2,
                line_end=12,
            ),
            Entity(
                id="c.py:3:func_c",
                kind=EntityKind.FUNCTION,
                name="func_c",
                file_path="/path/to/c.py",
                line_start=3,
                line_end=13,
            ),
        ]
        
        for entity in entities:
            graph.add_entity(entity)
        
        rel = Relationship(
            source_id="a.py:1:ClassA",
            target_id="b.py:2:func_b",
            kind=RelationshipKind.CALLS,
        )
        graph.add_relationship(rel)
        
        return graph
    
    def test_export_summary(self, sample_graph):
        """Test exporting graph summary."""
        summary = export_summary(sample_graph)
        
        assert "Knowledge Graph Summary" in summary
        assert "Total Entities: 3" in summary
        assert "Total Relationships: 1" in summary
        assert "class" in summary
        assert "function" in summary
    
    def test_export_summary_with_cycles(self):
        """Test summary with cycle detection."""
        graph = KnowledgeGraph()
        
        entities = [
            Entity(
                id="a.py:1:ClassA",
                kind=EntityKind.CLASS,
                name="ClassA",
                file_path="/path/to/a.py",
                line_start=1,
                line_end=10,
            ),
            Entity(
                id="b.py:2:ClassB",
                kind=EntityKind.CLASS,
                name="ClassB",
                file_path="/path/to/b.py",
                line_start=2,
                line_end=10,
            ),
        ]
        
        for entity in entities:
            graph.add_entity(entity)
        
        # Create cycle
        rel1 = Relationship(
            source_id="a.py:1:ClassA",
            target_id="b.py:2:ClassB",
            kind=RelationshipKind.CALLS,
        )
        rel2 = Relationship(
            source_id="b.py:2:ClassB",
            target_id="a.py:1:ClassA",
            kind=RelationshipKind.CALLS,
        )
        graph.add_relationship(rel1)
        graph.add_relationship(rel2)
        
        summary = export_summary(graph)
        
        assert "Circular Dependencies" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])