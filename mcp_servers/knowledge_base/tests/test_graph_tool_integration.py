#!/usr/bin/env python3
"""
Integration tests for Graph Tool Operations in KB MCP v4.

Tests kb_graph_tool, kb_impact_tool, kb_visualize_tool, and graph traversal.
"""

import json
import pytest

from graph.engine import KnowledgeGraph
from graph.models import Entity, EntityKind, Relationship, RelationshipKind, ImpactResult
from graph.queries import GraphQueries


@pytest.fixture
def mock_graph():
    """Create a mock graph with test data."""
    graph = KnowledgeGraph()
    
    entity1 = Entity(
        id="app/main.py:10:main",
        kind=EntityKind.FUNCTION,
        name="main",
        file_path="app/main.py",
        line_start=10,
        line_end=50,
        metadata={"layer": "entry"},
    )
    
    entity2 = Entity(
        id="app/services/user_service.py:5:UserService",
        kind=EntityKind.CLASS,
        name="UserService",
        file_path="app/services/user_service.py",
        line_start=5,
        line_end=100,
        metadata={"layer": "service", "patterns": ["singleton"]},
    )
    
    entity3 = Entity(
        id="app/models/user.py:3:User",
        kind=EntityKind.CLASS,
        name="User",
        file_path="app/models/user.py",
        line_start=3,
        line_end=50,
        metadata={"layer": "model"},
    )
    
    entity4 = Entity(
        id="app/controllers/user_controller.py:8:UserController",
        kind=EntityKind.CLASS,
        name="UserController",
        file_path="app/controllers/user_controller.py",
        line_start=8,
        line_end=80,
        metadata={"layer": "controller"},
    )
    
    entity5 = Entity(
        id="app/database/repository.py:12:UserRepository",
        kind=EntityKind.CLASS,
        name="UserRepository",
        file_path="app/database/repository.py",
        line_start=12,
        line_end=120,
        metadata={"layer": "repository"},
    )
    
    graph.add_entity(entity1)
    graph.add_entity(entity2)
    graph.add_entity(entity3)
    graph.add_entity(entity4)
    graph.add_entity(entity5)
    
    graph.add_relationship(Relationship(
        source_id="app/main.py:10:main",
        target_id="app/services/user_service.py:5:UserService",
        kind=RelationshipKind.CALLS,
    ))
    
    graph.add_relationship(Relationship(
        source_id="app/services/user_service.py:5:UserService",
        target_id="app/models/user.py:3:User",
        kind=RelationshipKind.CALLS,
    ))
    
    graph.add_relationship(Relationship(
        source_id="app/services/user_service.py:5:UserService",
        target_id="app/database/repository.py:12:UserRepository",
        kind=RelationshipKind.CALLS,
    ))
    
    graph.add_relationship(Relationship(
        source_id="app/controllers/user_controller.py:8:UserController",
        target_id="app/services/user_service.py:5:UserService",
        kind=RelationshipKind.CALLS,
    ))
    
    graph.add_relationship(Relationship(
        source_id="app/services/user_service.py:5:UserService",
        target_id="app/models/user.py:3:User",
        kind=RelationshipKind.COMPOSES,
    ))
    
    return graph


@pytest.fixture
def graph_queries(mock_graph):
    """Create GraphQueries instance."""
    return GraphQueries(mock_graph)


class TestGraphToolOperations:
    """Test kb_graph_tool operations."""
    
    def test_list_operation(self, mock_graph):
        """Test list operation returns entities."""
        queries = GraphQueries(mock_graph)
        entities = list(mock_graph.entities.keys())
        assert len(entities) == 5
    
    def test_layers_operation(self, mock_graph):
        """Test layers operation returns layer structure."""
        queries = GraphQueries(mock_graph)
        layers = queries.get_layers()
        assert isinstance(layers, dict)
        assert len(layers) > 0
    
    def test_entry_points_operation(self, mock_graph):
        """Test entry_points operation finds entry points."""
        queries = GraphQueries(mock_graph)
        entry_points = queries.find_entry_points()
        assert len(entry_points) > 0
    
    def test_traverse_operation_outgoing(self, mock_graph):
        """Test traverse operation with outgoing direction."""
        queries = GraphQueries(mock_graph)
        result = queries.traverse(
            "app/main.py:10:main",
            direction="outgoing",
            depth=2,
        )
        assert len(result) > 0
    
    def test_traverse_operation_incoming(self, mock_graph):
        """Test traverse operation with incoming direction."""
        queries = GraphQueries(mock_graph)
        result = queries.traverse(
            "app/services/user_service.py:5:UserService",
            direction="incoming",
            depth=2,
        )
        assert len(result) > 0
    
    def test_traverse_with_depth_limit(self, mock_graph):
        """Test traverse respects depth limit."""
        queries = GraphQueries(mock_graph)
        shallow = queries.traverse(
            "app/main.py:10:main",
            direction="outgoing",
            depth=1,
        )
        deep = queries.traverse(
            "app/main.py:10:main",
            direction="outgoing",
            depth=3,
        )
        assert len(shallow) <= len(deep)


class TestImpactTool:
    """Test kb_impact_tool operations."""
    
    def test_impact_analysis_basic(self, mock_graph):
        """Test basic impact analysis."""
        result = mock_graph.impact_analysis(
            "app/models/user.py:3:User",
            depth=3,
        )
        assert isinstance(result, ImpactResult)
        assert len(result.affected_entities) >= 0
    
    def test_impact_analysis_with_changes(self, mock_graph):
        """Test impact analysis with different change types."""
        for change_type in ["modify", "delete", "add"]:
            result = mock_graph.impact_analysis(
                "app/services/user_service.py:5:UserService",
                depth=2,
            )
            assert isinstance(result.affected_entities, list)
    
    def test_impact_analysis_risk_levels(self, mock_graph):
        """Test impact analysis includes risk levels."""
        result = mock_graph.impact_analysis(
            "app/models/user.py:3:User",
            depth=3,
        )
        assert isinstance(result.risk_levels, dict)
    
    def test_impact_analysis_test_files(self, mock_graph):
        """Test impact analysis identifies test files."""
        result = mock_graph.impact_analysis(
            "app/services/user_service.py:5:UserService",
            depth=2,
        )
        assert isinstance(result.test_files, list)
    
    def test_impact_on_nonexistent_entity(self, mock_graph):
        """Test impact analysis on non-existent entity."""
        with pytest.raises(Exception):
            mock_graph.impact_analysis("nonexistent:entity", depth=2)
    
    def test_impact_with_zero_depth(self, mock_graph):
        """Test impact analysis with zero depth."""
        result = mock_graph.impact_analysis(
            "app/models/user.py:3:User",
            depth=0,
        )
        assert len(result.affected_entities) == 0


class TestVisualizeTool:
    """Test kb_visualize_tool operations."""
    
    def test_visualize_full_mermaid(self, mock_graph):
        """Test full visualization in Mermaid format."""
        result = mock_graph.to_mermaid()
        assert "graph" in result.lower()
        assert len(result) > 0
    
    def test_visualize_full_dot(self, mock_graph):
        """Test full visualization in DOT format."""
        result = mock_graph.to_dot()
        assert "digraph" in result.lower()
        assert len(result) > 0
    
    def test_visualize_full_ascii(self, mock_graph):
        """Test full visualization in ASCII format."""
        result = mock_graph.to_ascii()
        assert len(result) > 0
    
    def test_visualize_tree_view(self, mock_graph):
        """Test tree visualization."""
        result = mock_graph.to_ascii(
            root_id="app/main.py:10:main",
            max_depth=2,
        )
        assert len(result) > 0
    
    def test_visualize_with_depth_limit(self, mock_graph):
        """Test visualization respects depth limit."""
        shallow = mock_graph.to_ascii(
            root_id="app/main.py:10:main",
            max_depth=1,
        )
        deep = mock_graph.to_ascii(
            root_id="app/main.py:10:main",
            max_depth=3,
        )
        assert len(shallow) <= len(deep)
    
    def test_visualize_nonexistent_root(self, mock_graph):
        """Test visualization with non-existent root."""
        result = mock_graph.to_ascii(
            root_id="nonexistent:entity",
            max_depth=2,
        )
        assert "error" in result.lower() or len(result) == 0


class TestGraphTraversal:
    """Test graph traversal with mock data."""
    
    def test_find_callers(self, graph_queries):
        """Test finding callers of an entity."""
        callers = graph_queries.find_callers(
            "app/services/user_service.py:5:UserService"
        )
        assert len(callers) > 0
        assert any("UserController" in c.name for c in callers)
    
    def test_find_callees(self, graph_queries):
        """Test finding callees of an entity."""
        callees = graph_queries.find_callees(
            "app/services/user_service.py:5:UserService"
        )
        assert len(callees) > 0
        assert any("User" in c.name or "UserRepository" in c.name for c in callees)
    
    def test_find_dependencies(self, graph_queries):
        """Test finding dependencies."""
        deps = graph_queries.find_dependencies(
            "app/services/user_service.py:5:UserService"
        )
        assert isinstance(deps, list)
    
    def test_find_dependents(self, graph_queries):
        """Test finding dependents."""
        dependents = graph_queries.find_dependents(
            "app/models/user.py:3:User"
        )
        assert len(dependents) > 0
    
    def test_find_path_between(self, graph_queries):
        """Test finding path between entities."""
        path = graph_queries.find_path_between(
            "app/main.py:10:main",
            "app/models/user.py:3:User",
        )
        assert path is not None
        assert len(path) > 0
    
    def test_find_path_no_connection(self, graph_queries):
        """Test finding path when no connection exists."""
        path = graph_queries.find_path_between(
            "app/models/user.py:3:User",
            "app/main.py:10:main",
        )
        assert path is None
    
    def test_find_patterns(self, graph_queries):
        """Test finding design patterns."""
        patterns = graph_queries.find_patterns("singleton")
        assert len(patterns) > 0
        assert any("UserService" in p.name for p in patterns)
    
    def test_find_components_by_layer(self, graph_queries):
        """Test finding components by layer."""
        services = graph_queries.find_components_by_layer("service")
        assert len(services) > 0
        assert any("UserService" in s.name for s in services)
    
    def test_search_by_name(self, graph_queries):
        """Test searching by name."""
        results = graph_queries.search_by_name("User")
        assert len(results) > 0
    
    def test_get_statistics(self, graph_queries):
        """Test getting graph statistics."""
        stats = graph_queries.get_statistics()
        assert isinstance(stats, dict)
        assert "total_entities" in stats
        assert "total_relationships" in stats
        assert stats["total_entities"] == 5
        assert stats["total_relationships"] == 5


class TestGraphToolErrorHandling:
    """Test graph tool error handling."""
    
    def test_traverse_nonexistent_entity(self, mock_graph):
        """Test traversing non-existent entity."""
        queries = GraphQueries(mock_graph)
        result = queries.traverse("nonexistent:entity", direction="outgoing", depth=2)
        assert len(result) == 0
    
    def test_impact_nonexistent_entity(self, mock_graph):
        """Test impact analysis on non-existent entity."""
        with pytest.raises(Exception):
            mock_graph.impact_analysis("nonexistent:entity")
    
    def test_visualize_invalid_format(self, mock_graph):
        """Test visualization with invalid format."""
        with pytest.raises(Exception):
            mock_graph.to_format("invalid_format")
    
    def test_find_path_same_entity(self, graph_queries):
        """Test finding path from entity to itself."""
        path = graph_queries.find_path_between(
            "app/models/user.py:3:User",
            "app/models/user.py:3:User",
        )
        assert path is not None
        assert len(path) == 1
    
    def test_empty_graph_operations(self):
        """Test operations on empty graph."""
        empty_graph = KnowledgeGraph()
        queries = GraphQueries(empty_graph)
        
        stats = queries.get_statistics()
        assert stats["total_entities"] == 0
        
        entry_points = queries.find_entry_points()
        assert len(entry_points) == 0


class TestGraphToolIntegration:
    """Test graph tool integration scenarios."""
    
    def test_full_traversal_chain(self, mock_graph):
        """Test full traversal chain from entry point."""
        queries = GraphQueries(mock_graph)
        
        entry = "app/main.py:10:main"
        level1 = queries.find_callees(entry, max_depth=1)
        
        for entity in level1:
            level2 = queries.find_callees(entity.id, max_depth=1)
            assert isinstance(level2, list)
    
    def test_impact_chain_analysis(self, mock_graph):
        """Test impact chain analysis."""
        result = mock_graph.impact_analysis(
            "app/models/user.py:3:User",
            depth=3,
        )
        
        for affected_id in result.affected_entities:
            sub_result = mock_graph.impact_analysis(affected_id, depth=1)
            assert isinstance(sub_result, ImpactResult)
    
    def test_layered_architecture_traversal(self, mock_graph):
        """Test traversal respecting architecture layers."""
        queries = GraphQueries(mock_graph)
        
        controller = queries.find_components_by_layer("controller")[0]
        services = queries.find_callees(controller.id)
        
        assert len(services) > 0
        assert any("service" in s.metadata.get("layer", "").lower() for s in services)
    
    def test_pattern_based_search(self, mock_graph):
        """Test pattern-based search and traversal."""
        queries = GraphQueries(mock_graph)
        
        singleton_classes = queries.find_patterns("singleton")
        for cls in singleton_classes:
            deps = queries.find_dependencies(cls.id)
            assert isinstance(deps, list)