#!/usr/bin/env python3
"""
Unit tests for Graph Queries.
"""

import pytest

from graph.engine import KnowledgeGraph
from graph.queries import GraphQueries
from graph.models import Entity, EntityKind, Relationship, RelationshipKind


class TestGraphQueries:
    """Tests for high-level graph query operations."""
    
    @pytest.fixture
    def graph_with_data(self):
        """Create a graph with sample data."""
        graph = KnowledgeGraph()
        
        # Create entities
        entities = [
            Entity(
                id="controller.py:10:MainController",
                kind=EntityKind.CLASS,
                name="MainController",
                file_path="/path/to/controller.py",
                line_start=10,
                line_end=50,
                metadata={"layer": "controller"},
            ),
            Entity(
                id="service.py:20:DataService",
                kind=EntityKind.CLASS,
                name="DataService",
                file_path="/path/to/service.py",
                line_start=20,
                line_end=60,
                metadata={"layer": "model"},
            ),
            Entity(
                id="repository.py:30:DataRepository",
                kind=EntityKind.CLASS,
                name="DataRepository",
                file_path="/path/to/repository.py",
                line_start=30,
                line_end=70,
                metadata={"layer": "model"},
            ),
            Entity(
                id="utils.py:40:helper_func",
                kind=EntityKind.FUNCTION,
                name="helper_func",
                file_path="/path/to/utils.py",
                line_start=40,
                line_end=45,
                metadata={"layer": "common"},
            ),
            Entity(
                id="test_controller.py:10:test_main",
                kind=EntityKind.TEST,
                name="test_main",
                file_path="/path/to/test_controller.py",
                line_start=10,
                line_end=25,
            ),
        ]
        
        for entity in entities:
            graph.add_entity(entity)
        
        # Create relationships
        relationships = [
            # Controller calls Service
            Relationship(
                source_id="controller.py:10:MainController",
                target_id="service.py:20:DataService",
                kind=RelationshipKind.CALLS,
            ),
            # Service composes Repository
            Relationship(
                source_id="service.py:20:DataService",
                target_id="repository.py:30:DataRepository",
                kind=RelationshipKind.COMPOSES,
            ),
            # Service calls helper
            Relationship(
                source_id="service.py:20:DataService",
                target_id="utils.py:40:helper_func",
                kind=RelationshipKind.CALLS,
            ),
            # Test tests controller
            Relationship(
                source_id="test_controller.py:10:test_main",
                target_id="controller.py:10:MainController",
                kind=RelationshipKind.TESTS,
            ),
        ]
        
        for rel in relationships:
            graph.add_relationship(rel)
        
        return graph
    
    @pytest.fixture
    def queries(self, graph_with_data):
        """Create GraphQueries instance."""
        return GraphQueries(graph_with_data)
    
    def test_find_callers(self, queries):
        """Test finding entities that call a target."""
        callers = queries.find_callers("service.py:20:DataService", max_depth=1)
        
        assert len(callers) == 1
        assert callers[0].name == "MainController"
    
    def test_find_callees(self, queries):
        """Test finding entities called by a source."""
        # Note: find_callees only looks for 'calls' relationships
        callees = queries.find_callees("service.py:20:DataService", max_depth=1)
        
        # Should find helper_func (via CALLS relationship)
        # DataRepository is via COMPOSES, not CALLS
        assert len(callees) == 1
        assert callees[0].name == "helper_func"
    
    def test_find_dependencies(self, queries):
        """Test finding entities that a target depends on."""
        deps = queries.find_dependencies("service.py:20:DataService", max_depth=1)
        
        # Service depends on Repository (composition)
        assert len(deps) >= 1
        dep_names = [d.name for d in deps]
        assert "DataRepository" in dep_names
    
    def test_find_dependents(self, queries):
        """Test finding entities that depend on a target."""
        dependents = queries.find_dependents("service.py:20:DataService", max_depth=1)
        
        # Controller depends on Service
        assert len(dependents) >= 1
        dependent_names = [d.name for d in dependents]
        assert "MainController" in dependent_names
    
    def test_find_tests_for(self, queries):
        """Test finding tests for an entity."""
        tests = queries.find_tests_for("controller.py:10:MainController")
        
        assert len(tests) == 1
        assert tests[0].name == "test_main"
        assert tests[0].kind == EntityKind.TEST
    
    def test_find_tests_by(self, queries):
        """Test finding what a test tests."""
        tested = queries.find_tests_by("test_controller.py:10:test_main")
        
        assert len(tested) == 1
        assert tested[0].name == "MainController"
    
    def test_find_inheritance_chain(self, graph_with_data):
        """Test finding inheritance chain."""
        graph = graph_with_data
        
        # Add inheritance relationship
        parent = Entity(
            id="base.py:5:BaseClass",
            kind=EntityKind.CLASS,
            name="BaseClass",
            file_path="/path/to/base.py",
            line_start=5,
            line_end=15,
        )
        graph.add_entity(parent)
        
        rel = Relationship(
            source_id="controller.py:10:MainController",
            target_id="base.py:5:BaseClass",
            kind=RelationshipKind.EXTENDS,
        )
        graph.add_relationship(rel)
        
        queries = GraphQueries(graph)
        chain = queries.find_inheritance_chain("controller.py:10:MainController")
        
        assert len(chain) == 1
        assert chain[0].name == "BaseClass"
    
    def test_find_composition_tree(self, queries):
        """Test finding composition tree."""
        tree = queries.find_composition_tree("service.py:20:DataService", max_depth=1)
        
        assert len(tree) == 1
        assert tree[0].name == "DataRepository"
    
    def test_find_path_between(self, queries):
        """Test finding path between two entities."""
        path = queries.find_path_between(
            "controller.py:10:MainController",
            "repository.py:30:DataRepository",
        )
        
        assert path is not None
        assert len(path.entities) == 3  # Controller -> Service -> Repository
    
    def test_find_entry_points(self, graph_with_data):
        """Test finding entry points."""
        graph = graph_with_data
        
        # Add a main function
        main_func = Entity(
            id="main.py:1:main",
            kind=EntityKind.FUNCTION,
            name="main",
            file_path="/path/to/main.py",
            line_start=1,
            line_end=10,
        )
        graph.add_entity(main_func)
        
        queries = GraphQueries(graph)
        entry_points = queries.find_entry_points()
        
        # Should find the main function
        main_funcs = [e for e in entry_points if e.name == "main"]
        assert len(main_funcs) == 1
    
    def test_find_components_by_layer(self, queries):
        """Test finding components by architecture layer."""
        model_components = queries.find_components_by_layer("model")
        
        assert len(model_components) == 2  # DataService and DataRepository
        layer_names = [c.name for c in model_components]
        assert "DataService" in layer_names
        assert "DataRepository" in layer_names
    
    def test_find_patterns(self, graph_with_data):
        """Test finding entities by design pattern."""
        graph = graph_with_data
        
        # Add pattern metadata
        entity = graph.get_entity("controller.py:10:MainController")
        if entity:
            entity.metadata["pattern"] = ["mvc", "singleton"]
        
        queries = GraphQueries(graph)
        mvc_components = queries.find_patterns("mvc")
        
        assert len(mvc_components) == 1
        assert mvc_components[0].name == "MainController"
    
    def test_search_by_name(self, queries):
        """Test searching entities by name."""
        results = queries.search_by_name("Controller")
        
        assert len(results) > 0
        assert results[0].name == "MainController"
    
    def test_search_by_name_case_insensitive(self, queries):
        """Test case-insensitive search."""
        results = queries.search_by_name("controller", case_sensitive=False)
        
        assert len(results) > 0
        assert results[0].name == "MainController"
    
    def test_get_statistics(self, queries):
        """Test getting graph statistics."""
        stats = queries.get_statistics()
        
        assert "total_entities" in stats
        assert "total_relationships" in stats
        assert "by_kind" in stats
        assert "by_layer" in stats
        assert stats["total_entities"] == 5
        assert stats["total_relationships"] == 4
    
    def test_find_high_complexity(self, graph_with_data):
        """Test finding high complexity entities."""
        graph = graph_with_data
        
        # Add complexity metadata
        entity = graph.get_entity("service.py:20:DataService")
        if entity:
            entity.metadata["complexity"] = 0.85
        
        queries = GraphQueries(graph)
        high_complexity = queries.find_high_complexity(threshold=0.7)
        
        assert len(high_complexity) == 1
        assert high_complexity[0].name == "DataService"
    
    def test_find_recently_modified(self, queries):
        """Test finding recently modified entities."""
        recent = queries.find_recently_modified(limit=3)
        
        assert len(recent) <= 3


class TestGraphQueriesEmptyGraph:
    """Tests for queries on empty or minimal graphs."""
    
    @pytest.fixture
    def empty_graph(self):
        """Create an empty graph."""
        return KnowledgeGraph()
    
    @pytest.fixture
    def empty_queries(self, empty_graph):
        """Create GraphQueries for empty graph."""
        return GraphQueries(empty_graph)
    
    def test_find_callers_no_results(self, empty_queries):
        """Test finding callers in empty graph."""
        callers = empty_queries.find_callers("nonexistent")
        assert len(callers) == 0
    
    def test_find_path_nonexistent(self, empty_queries):
        """Test finding path for nonexistent entities."""
        path = empty_queries.find_path_between("a", "b")
        assert path is None
    
    def test_get_statistics_empty(self, empty_queries):
        """Test statistics on empty graph."""
        stats = empty_queries.get_statistics()
        
        assert stats["total_entities"] == 0
        assert stats["total_relationships"] == 0
        assert stats["avg_relationships_per_entity"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])