#!/usr/bin/env python3
"""
Tests for MCP Resources Layer in KB MCP v4.
"""

import json
import pytest
from pathlib import Path

from graph.engine import KnowledgeGraph
from graph.models import Entity, EntityKind, Relationship, RelationshipKind, DocstringInfo
from resources.registry import ResourceRegistry, ResourceHandler, ResourceResult
from resources.project import ProjectResources
from resources.arch import ArchitectureResources
from resources.flows import FlowResources
from resources.api import APIResources
from resources.code import CodeResources
from resources.session import SessionResources
from resources.quality import QualityResources


class TestResourceRegistry:
    """Test ResourceRegistry functionality."""
    
    def test_create_registry(self):
        """Test registry creation."""
        registry = ResourceRegistry()
        assert registry is not None
        assert len(registry.list_resources()) == 0
    
    def test_register_handler(self):
        """Test handler registration."""
        registry = ResourceRegistry()
        handler = ProjectResources()
        registry.register_handler(handler)
        
        assert "project" in registry._handlers
        assert len(registry.list_resources()) == 3  # tree, summary, metadata
    
    def test_register_multiple_handlers(self):
        """Test registering multiple handlers."""
        registry = ResourceRegistry()
        registry.register_handler(ProjectResources())
        registry.register_handler(ArchitectureResources())
        registry.register_handler(FlowResources())
        
        assert len(registry._handlers) == 3
        assert len(registry.list_resources()) > 0
    
    def test_register_duplicate_handler_fails(self):
        """Test that duplicate handler registration fails."""
        registry = ResourceRegistry()
        registry.register_handler(ProjectResources())
        
        with pytest.raises(ValueError, match="already registered"):
            registry.register_handler(ProjectResources())
    
    def test_set_graph_propagates(self):
        """Test that setting graph propagates to handlers."""
        registry = ResourceRegistry()
        graph = KnowledgeGraph()
        
        registry.register_handler(ProjectResources())
        registry.set_graph(graph)
        
        handler = registry.get_handler("project")
        assert handler.get_graph() is graph
    
    def test_get_statistics(self):
        """Test registry statistics."""
        registry = ResourceRegistry()
        registry.register_handler(ProjectResources())
        registry.register_handler(ArchitectureResources())
        
        stats = registry.get_statistics()
        
        assert stats["total_handlers"] == 2
        assert stats["total_resources"] > 0
        assert "project" in stats["categories"]
        assert "arch" in stats["categories"]


class TestProjectResources:
    """Test ProjectResources handler."""
    
    def test_category_prefix(self):
        """Test category prefix."""
        handler = ProjectResources()
        assert handler.category_prefix == "project"
    
    def test_register_resources(self):
        """Test resource registration."""
        handler = ProjectResources()
        registry = ResourceRegistry()
        handler.register_resources(registry)
        
        assert registry.has_resource("knowledge-base://project/tree")
        assert registry.has_resource("knowledge-base://project/summary")
        assert registry.has_resource("knowledge-base://project/metadata")
    
    def test_read_tree_no_graph(self):
        """Test reading tree without graph."""
        handler = ProjectResources()
        result = handler.read_resource("tree")
        
        data = json.loads(result.content)
        assert "error" in data or "tree" in data
    
    def test_read_tree_with_graph(self, sample_graph):
        """Test reading tree with graph."""
        handler = ProjectResources()
        handler.set_graph(sample_graph)
        
        result = handler.read_resource("tree")
        data = json.loads(result.content)
        
        assert "root" in data
        assert "children" in data
    
    def test_read_summary_no_graph(self):
        """Test reading summary without graph."""
        handler = ProjectResources()
        result = handler.read_resource("summary")
        
        assert "not been analyzed" in result.content
    
    def test_read_summary_with_graph(self, sample_graph):
        """Test reading summary with graph."""
        handler = ProjectResources()
        handler.set_graph(sample_graph)
        
        result = handler.read_resource("summary")
        
        assert "entities" in result.content
        assert "relationships" in result.content
    
    def test_read_metadata(self):
        """Test reading metadata."""
        handler = ProjectResources()
        result = handler.read_resource("metadata")
        
        data = json.loads(result.content)
        assert "languages" in data
        assert "analysis_info" in data
    
    def test_read_unknown_resource(self):
        """Test reading unknown resource."""
        handler = ProjectResources()
        
        with pytest.raises(FileNotFoundError):
            handler.read_resource("unknown")


class TestArchitectureResources:
    """Test ArchitectureResources handler."""
    
    def test_category_prefix(self):
        """Test category prefix."""
        handler = ArchitectureResources()
        assert handler.category_prefix == "arch"
    
    def test_register_resources(self):
        """Test resource registration."""
        handler = ArchitectureResources()
        registry = ResourceRegistry()
        handler.register_resources(registry)
        
        assert registry.has_resource("knowledge-base://arch/components")
        assert registry.has_resource("knowledge-base://arch/dependencies")
        assert registry.has_resource("knowledge-base://arch/layers")
        assert registry.has_resource("knowledge-base://arch/patterns")
    
    def test_read_components_with_graph(self, sample_graph):
        """Test reading components."""
        handler = ArchitectureResources()
        handler.set_graph(sample_graph)
        
        result = handler.read_resource("components")
        data = json.loads(result.content)
        
        assert "components" in data
    
    def test_read_dependencies_json(self, sample_graph):
        """Test reading dependencies in JSON format."""
        handler = ArchitectureResources()
        handler.set_graph(sample_graph)
        
        result = handler.read_resource("dependencies", {"format": "json"})
        data = json.loads(result.content)
        
        assert "entities" in data or "error" in data
    
    def test_read_dependencies_mermaid(self, sample_graph):
        """Test reading dependencies in Mermaid format."""
        handler = ArchitectureResources()
        handler.set_graph(sample_graph)
        
        result = handler.read_resource("dependencies", {"format": "mermaid"})
        
        assert result.mimetype == "text/plain"
        # Mermaid diagrams start with "graph" directive
        assert result.content.strip().startswith("graph") or "error" in result.content.lower()
    
    def test_read_layers(self, sample_graph):
        """Test reading layers."""
        handler = ArchitectureResources()
        handler.set_graph(sample_graph)
        
        result = handler.read_resource("layers")
        data = json.loads(result.content)
        
        assert "layers" in data
    
    def test_read_patterns(self, sample_graph):
        """Test reading patterns."""
        handler = ArchitectureResources()
        handler.set_graph(sample_graph)
        
        result = handler.read_resource("patterns")
        data = json.loads(result.content)
        
        assert "patterns" in data


class TestFlowResources:
    """Test FlowResources handler."""
    
    def test_category_prefix(self):
        """Test category prefix."""
        handler = FlowResources()
        assert handler.category_prefix == "flows"
    
    def test_register_resources(self):
        """Test resource registration."""
        handler = FlowResources()
        registry = ResourceRegistry()
        handler.register_resources(registry)
        
        assert registry.has_resource("knowledge-base://flows/data")
        assert registry.has_resource("knowledge-base://flows/control")
        assert registry.has_resource("knowledge-base://flows/imports")
        assert registry.has_resource("knowledge-base://flows/events")
    
    def test_read_data_flow(self, sample_graph):
        """Test reading data flow."""
        handler = FlowResources()
        handler.set_graph(sample_graph)
        
        result = handler.read_resource("data")
        data = json.loads(result.content)
        
        assert "data_flows" in data
        assert "flow_chains" in data
    
    def test_read_control_flow(self, sample_graph):
        """Test reading control flow."""
        handler = FlowResources()
        handler.set_graph(sample_graph)
        
        result = handler.read_resource("control")
        data = json.loads(result.content)
        
        assert "call_graph" in data
    
    def test_read_imports(self, sample_graph):
        """Test reading imports."""
        handler = FlowResources()
        handler.set_graph(sample_graph)
        
        result = handler.read_resource("imports")
        data = json.loads(result.content)
        
        assert "imports_by_file" in data


class TestAPIResources:
    """Test APIResources handler."""
    
    def test_category_prefix(self):
        """Test category prefix."""
        handler = APIResources()
        assert handler.category_prefix == "api"
    
    def test_register_resources(self):
        """Test resource registration."""
        handler = APIResources()
        registry = ResourceRegistry()
        handler.register_resources(registry)
        
        assert registry.has_resource("knowledge-base://api/endpoints")
        assert registry.has_resource("knowledge-base://api/public")
        assert registry.has_resource("knowledge-base://api/config")
    
    def test_read_endpoints(self, sample_graph):
        """Test reading endpoints."""
        handler = APIResources()
        handler.set_graph(sample_graph)
        
        result = handler.read_resource("endpoints")
        data = json.loads(result.content)
        
        assert "endpoints" in data
    
    def test_read_public_api(self, sample_graph):
        """Test reading public API."""
        handler = APIResources()
        handler.set_graph(sample_graph)
        
        result = handler.read_resource("public")
        data = json.loads(result.content)
        
        assert "public_api" in data
    
    def test_read_config(self):
        """Test reading config."""
        handler = APIResources()
        result = handler.read_resource("config")
        
        data = json.loads(result.content)
        assert "config_files" in data
        assert "env_vars" in data


class TestCodeResources:
    """Test CodeResources handler."""
    
    def test_category_prefix(self):
        """Test category prefix."""
        handler = CodeResources()
        assert handler.category_prefix == "code"
    
    def test_read_entity_not_found(self, sample_graph):
        """Test reading non-existent entity."""
        handler = CodeResources()
        handler.set_graph(sample_graph)
        
        result = handler.read_resource("entity/nonexistent")
        data = json.loads(result.content)
        
        assert "error" in data
    
    def test_read_entity_found(self, sample_graph):
        """Test reading existing entity."""
        handler = CodeResources()
        handler.set_graph(sample_graph)
        
        # Add an entity first
        entity = Entity(
            id="test.py:1:TestClass",
            kind=EntityKind.CLASS,
            name="TestClass",
            file_path="test.py",
            line_start=1,
            line_end=10,
        )
        sample_graph.add_entity(entity)
        
        result = handler.read_resource("entity/test.py:1:TestClass")
        data = json.loads(result.content)
        
        assert "entity" in data
        assert data["entity"]["name"] == "TestClass"
    
    def test_read_search(self, sample_graph):
        """Test code search."""
        handler = CodeResources()
        handler.set_graph(sample_graph)
        
        result = handler.read_resource("search/TestClass")
        data = json.loads(result.content)
        
        assert "query" in data
        assert "results" in data
    
    def test_read_file_not_found(self, sample_graph):
        """Test reading non-existent file."""
        handler = CodeResources()
        handler.set_graph(sample_graph)
        
        result = handler.read_resource("file/nonexistent.py")
        data = json.loads(result.content)
        
        assert "error" in data or "entities" in data


class TestSessionResources:
    """Test SessionResources handler."""
    
    def test_category_prefix(self):
        """Test category prefix."""
        handler = SessionResources()
        assert handler.category_prefix == "session"
    
    def test_register_resources(self):
        """Test resource registration."""
        handler = SessionResources()
        registry = ResourceRegistry()
        handler.register_resources(registry)
        
        assert registry.has_resource("knowledge-base://session/context")
    
    def test_read_context_empty(self):
        """Test reading empty context."""
        handler = SessionResources()
        result = handler.read_resource("context")
        
        data = json.loads(result.content)
        assert "session_id" in data
        assert data["queries"] == []
    
    def test_update_context(self):
        """Test updating context."""
        handler = SessionResources()
        handler.update_context(
            session_id="test-session",
            query="What is RAG?",
            entity_id="test.py:1:TestClass",
        )
        
        result = handler.read_resource("context", {"session_id": "test-session"})
        data = json.loads(result.content)
        
        assert len(data["queries"]) == 1
        assert len(data["learned_entities"]) == 1
    
    def test_clear_session(self):
        """Test clearing session."""
        handler = SessionResources()
        handler.update_context(session_id="test-session", query="test")
        
        assert handler.clear_session("test-session") is True
        assert handler.clear_session("nonexistent") is False


class TestQualityResources:
    """Test QualityResources handler (v4.1 stubs)."""
    
    def test_category_prefix(self):
        """Test category prefix."""
        handler = QualityResources()
        assert handler.category_prefix == "quality"
    
    def test_read_complexity_stub(self):
        """Test complexity stub."""
        handler = QualityResources()
        result = handler.read_resource("complexity")
        
        data = json.loads(result.content)
        assert "status" in data
        assert data["status"] == "stub"
    
    def test_read_coverage_stub(self):
        """Test coverage stub."""
        handler = QualityResources()
        result = handler.read_resource("coverage")
        
        data = json.loads(result.content)
        assert data["status"] == "stub"
    
    def test_read_smells_stub(self):
        """Test smells stub."""
        handler = QualityResources()
        result = handler.read_resource("smells")
        
        data = json.loads(result.content)
        assert data["status"] == "stub"


# Fixtures

@pytest.fixture
def sample_graph():
    """Create a sample graph for testing."""
    graph = KnowledgeGraph()
    
    # Add some entities
    entity1 = Entity(
        id="test1.py:1:ClassA",
        kind=EntityKind.CLASS,
        name="ClassA",
        file_path="test1.py",
        line_start=1,
        line_end=10,
        metadata={"layer": "model", "patterns": ["factory"]},
    )
    
    entity2 = Entity(
        id="test2.py:5:ClassB",
        kind=EntityKind.CLASS,
        name="ClassB",
        file_path="test2.py",
        line_start=5,
        line_end=20,
        metadata={"layer": "view"},
    )
    
    entity3 = Entity(
        id="test3.py:10:function_c",
        kind=EntityKind.FUNCTION,
        name="function_c",
        file_path="test3.py",
        line_start=10,
        line_end=30,
        docstring=DocstringInfo(summary="A test function"),
        metadata={"layer": "controller"},
    )
    
    graph.add_entity(entity1)
    graph.add_entity(entity2)
    graph.add_entity(entity3)
    
    # Add relationships
    graph.add_relationship(Relationship(
        source_id="test1.py:1:ClassA",
        target_id="test2.py:5:ClassB",
        kind=RelationshipKind.CALLS,
    ))
    
    graph.add_relationship(Relationship(
        source_id="test2.py:5:ClassB",
        target_id="test3.py:10:function_c",
        kind=RelationshipKind.CALLS,
    ))
    
    return graph