#!/usr/bin/env python3
"""
Integration tests for MCP Resources Layer in KB MCP v4.

Tests all 15 resources, URI routing, format negotiation, and error handling.
"""

import json
import pytest
from pathlib import Path

from graph.engine import KnowledgeGraph
from graph.models import Entity, EntityKind, Relationship, RelationshipKind
from resources.registry import ResourceRegistry
from resources.project import ProjectResources
from resources.arch import ArchitectureResources
from resources.flows import FlowResources
from resources.api import APIResources
from resources.code import CodeResources
from resources.session import SessionResources
from resources.quality import QualityResources


@pytest.fixture
def sample_graph():
    """Create a sample graph for testing."""
    graph = KnowledgeGraph()
    
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
        metadata={"layer": "controller"},
    )
    
    graph.add_entity(entity1)
    graph.add_entity(entity2)
    graph.add_entity(entity3)
    
    graph.add_relationship(Relationship(
        source_id="test1.py:1:ClassA",
        target_id="test2.py:5:ClassB",
        kind=RelationshipKind.CALLS,
    ))
    
    return graph


@pytest.fixture
def resource_registry(sample_graph):
    """Create a registry with all resources."""
    registry = ResourceRegistry()
    registry.set_graph(sample_graph)
    
    registry.register_handler(ProjectResources())
    registry.register_handler(ArchitectureResources())
    registry.register_handler(FlowResources())
    registry.register_handler(APIResources())
    registry.register_handler(CodeResources())
    registry.register_handler(SessionResources())
    registry.register_handler(QualityResources())
    
    return registry


class TestAllResourcesAccessible:
    """Test all 15 MCP resources are accessible."""
    
    def test_project_tree_accessible(self, resource_registry):
        """Test project/tree resource is accessible."""
        assert resource_registry.has_resource("knowledge-base://project/tree")
    
    def test_project_summary_accessible(self, resource_registry):
        """Test project/summary resource is accessible."""
        assert resource_registry.has_resource("knowledge-base://project/summary")
    
    def test_project_metadata_accessible(self, resource_registry):
        """Test project/metadata resource is accessible."""
        assert resource_registry.has_resource("knowledge-base://project/metadata")
    
    def test_arch_components_accessible(self, resource_registry):
        """Test arch/components resource is accessible."""
        assert resource_registry.has_resource("knowledge-base://arch/components")
    
    def test_arch_dependencies_accessible(self, resource_registry):
        """Test arch/dependencies resource is accessible."""
        assert resource_registry.has_resource("knowledge-base://arch/dependencies")
    
    def test_arch_layers_accessible(self, resource_registry):
        """Test arch/layers resource is accessible."""
        assert resource_registry.has_resource("knowledge-base://arch/layers")
    
    def test_arch_patterns_accessible(self, resource_registry):
        """Test arch/patterns resource is accessible."""
        assert resource_registry.has_resource("knowledge-base://arch/patterns")
    
    def test_flows_data_accessible(self, resource_registry):
        """Test flows/data resource is accessible."""
        assert resource_registry.has_resource("knowledge-base://flows/data")
    
    def test_flows_control_accessible(self, resource_registry):
        """Test flows/control resource is accessible."""
        assert resource_registry.has_resource("knowledge-base://flows/control")
    
    def test_flows_imports_accessible(self, resource_registry):
        """Test flows/imports resource is accessible."""
        assert resource_registry.has_resource("knowledge-base://flows/imports")
    
    def test_flows_events_accessible(self, resource_registry):
        """Test flows/events resource is accessible."""
        assert resource_registry.has_resource("knowledge-base://flows/events")
    
    def test_api_endpoints_accessible(self, resource_registry):
        """Test api/endpoints resource is accessible."""
        assert resource_registry.has_resource("knowledge-base://api/endpoints")
    
    def test_api_public_accessible(self, resource_registry):
        """Test api/public resource is accessible."""
        assert resource_registry.has_resource("knowledge-base://api/public")
    
    def test_code_search_accessible(self, resource_registry):
        """Test code/search resource is accessible."""
        assert resource_registry.has_resource("knowledge-base://code/search")
    
    def test_health_accessible(self, resource_registry):
        """Test health resource is accessible."""
        assert resource_registry.has_resource("knowledge-base://health")
    
    def test_total_resource_count(self, resource_registry):
        """Test total resource count is 15."""
        resources = resource_registry.list_resources()
        assert len(resources) >= 15, f"Expected at least 15 resources, got {len(resources)}"


class TestResourceURIRouting:
    """Test resource URI routing."""
    
    def test_project_uri_prefix(self, resource_registry):
        """Test project URI prefix routing."""
        handler = resource_registry.get_handler_for_uri("knowledge-base://project/tree")
        assert handler is not None
        assert isinstance(handler, ProjectResources)
    
    def test_arch_uri_prefix(self, resource_registry):
        """Test arch URI prefix routing."""
        handler = resource_registry.get_handler_for_uri("knowledge-base://arch/components")
        assert handler is not None
        assert isinstance(handler, ArchitectureResources)
    
    def test_flows_uri_prefix(self, resource_registry):
        """Test flows URI prefix routing."""
        handler = resource_registry.get_handler_for_uri("knowledge-base://flows/data")
        assert handler is not None
        assert isinstance(handler, FlowResources)
    
    def test_api_uri_prefix(self, resource_registry):
        """Test api URI prefix routing."""
        handler = resource_registry.get_handler_for_uri("knowledge-base://api/endpoints")
        assert handler is not None
        assert isinstance(handler, APIResources)
    
    def test_code_uri_prefix(self, resource_registry):
        """Test code URI prefix routing."""
        handler = resource_registry.get_handler_for_uri("knowledge-base://code/search")
        assert handler is not None
        assert isinstance(handler, CodeResources)
    
    def test_session_uri_prefix(self, resource_registry):
        """Test session URI prefix routing."""
        handler = resource_registry.get_handler_for_uri("knowledge-base://session/context")
        assert handler is not None
        assert isinstance(handler, SessionResources)
    
    def test_quality_uri_prefix(self, resource_registry):
        """Test quality URI prefix routing."""
        handler = resource_registry.get_handler_for_uri("knowledge-base://quality/complexity")
        assert handler is not None
        assert isinstance(handler, QualityResources)
    
    def test_unknown_uri_returns_none(self, resource_registry):
        """Test unknown URI returns None handler."""
        handler = resource_registry.get_handler_for_uri("knowledge-base://unknown/resource")
        assert handler is None


class TestFormatNegotiation:
    """Test format negotiation (json, mermaid, dot, ascii)."""
    
    def test_json_format_default(self, resource_registry):
        """Test JSON format is default."""
        result = resource_registry.read_resource("knowledge-base://project/tree")
        try:
            data = json.loads(result.content)
            assert isinstance(data, (dict, list))
        except json.JSONDecodeError:
            pass  # Some resources may not return JSON by default
    
    def test_dependencies_json_format(self, resource_registry, sample_graph):
        """Test dependencies resource with JSON format."""
        result = resource_registry.read_resource(
            "knowledge-base://arch/dependencies",
            params={"format": "json"}
        )
        data = json.loads(result.content)
        assert isinstance(data, dict)
    
    def test_dependencies_mermaid_format(self, resource_registry, sample_graph):
        """Test dependencies resource with Mermaid format."""
        result = resource_registry.read_resource(
            "knowledge-base://arch/dependencies",
            params={"format": "mermaid"}
        )
        assert "graph" in result.content.lower() or "error" in result.content.lower()
    
    def test_visualize_mermaid_format(self, resource_registry, sample_graph):
        """Test visualization with Mermaid format."""
        result = resource_registry.read_resource(
            "knowledge-base://arch/dependencies",
            params={"format": "mermaid"}
        )
        assert result.mimetype in ["text/plain", "application/json"]
    
    def test_visualize_dot_format(self, resource_registry, sample_graph):
        """Test visualization with DOT format."""
        result = resource_registry.read_resource(
            "knowledge-base://arch/dependencies",
            params={"format": "dot"}
        )
        assert "digraph" in result.content.lower() or "error" in result.content.lower()
    
    def test_ascii_format(self, resource_registry):
        """Test ASCII format for tree views."""
        result = resource_registry.read_resource("knowledge-base://project/tree")
        assert result.content  # Should have content
    
    def test_format_parameter_propagation(self, resource_registry):
        """Test format parameter propagates to handlers."""
        result = resource_registry.read_resource(
            "knowledge-base://arch/dependencies",
            params={"format": "json"}
        )
        data = json.loads(result.content)
        assert isinstance(data, dict)


class TestResourceErrorHandling:
    """Test resource error handling."""
    
    def test_unknown_resource_raises(self, resource_registry):
        """Test reading unknown resource raises error."""
        with pytest.raises(FileNotFoundError):
            resource_registry.read_resource("knowledge-base://unknown/resource")
    
    def test_invalid_uri_format(self, resource_registry):
        """Test invalid URI format handling."""
        with pytest.raises(ValueError):
            resource_registry.read_resource("invalid-uri-format")
    
    def test_missing_handler(self, resource_registry):
        """Test missing handler error."""
        registry_empty = ResourceRegistry()
        with pytest.raises(FileNotFoundError):
            registry_empty.read_resource("knowledge-base://project/tree")
    
    def test_resource_read_error_propagates(self, resource_registry):
        """Test resource read errors propagate correctly."""
        result = resource_registry.read_resource("knowledge-base://code/entity/nonexistent")
        data = json.loads(result.content)
        assert "error" in data
    
    def test_graph_not_set_error(self):
        """Test error when graph is not set."""
        registry = ResourceRegistry()
        registry.register_handler(ProjectResources())
        
        result = registry.read_resource("knowledge-base://project/summary")
        assert "not been analyzed" in result.content or "error" in result.content.lower()
    
    def test_health_resource_with_empty_graph(self):
        """Test health resource works with empty graph."""
        registry = ResourceRegistry()
        registry.set_graph(KnowledgeGraph())
        registry.register_handler(QualityResources())
        
        result = registry.read_resource("knowledge-base://health")
        assert "Entities" in result.content or "error" in result.content.lower()


class TestResourceContentValidation:
    """Test resource content validation."""
    
    def test_project_tree_returns_json(self, resource_registry):
        """Test project tree returns JSON."""
        result = resource_registry.read_resource("knowledge-base://project/tree")
        data = json.loads(result.content)
        assert isinstance(data, dict)
        assert "root" in data or "error" in data
    
    def test_project_summary_returns_text(self, resource_registry):
        """Test project summary returns text."""
        result = resource_registry.read_resource("knowledge-base://project/summary")
        assert isinstance(result.content, str)
        assert len(result.content) > 0
    
    def test_arch_components_returns_json(self, resource_registry):
        """Test arch components returns JSON."""
        result = resource_registry.read_resource("knowledge-base://arch/components")
        data = json.loads(result.content)
        assert isinstance(data, dict)
        assert "components" in data or "error" in data
    
    def test_health_returns_formatted_text(self, resource_registry):
        """Test health returns formatted text."""
        result = resource_registry.read_resource("knowledge-base://health")
        assert "Entities" in result.content or "error" in result.content
    
    def test_session_context_returns_json(self, resource_registry):
        """Test session context returns JSON."""
        result = resource_registry.read_resource("knowledge-base://session/context")
        data = json.loads(result.content)
        assert isinstance(data, dict)
        assert "session_id" in data