#!/usr/bin/env python3
"""
Tests for MCP Prompts Layer.
"""

import pytest

from prompts.engine import PromptEngine, register_all_prompts
from prompts.registry import PromptArgument, PromptInfo, PromptRegistry


class TestPromptRegistry:
    """Test PromptRegistry functionality."""
    
    def test_create_registry(self):
        """Test registry initialization."""
        registry = PromptRegistry()
        assert registry is not None
        assert registry.list_prompts() == []
    
    def test_register_prompt(self):
        """Test prompt registration."""
        registry = PromptRegistry()
        registry.register(
            name="test-prompt",
            description="Test description",
            template="Hello {{ name }}!",
            arguments=[],
            category="test",
        )
        
        assert registry.has_prompt("test-prompt")
        assert registry.get("test-prompt") is not None
    
    def test_register_prompt_with_args(self):
        """Test prompt registration with arguments."""
        registry = PromptRegistry()
        registry.register(
            name="test-prompt",
            description="Test with args",
            template="Hello!",
            arguments=[
                PromptArgument(name="arg1", description="First arg", required=True),
                PromptArgument(name="arg2", description="Second arg", required=False, default="default"),
            ],
            category="test",
        )
        
        prompt = registry.get("test-prompt")
        assert prompt is not None
        assert len(prompt["arguments"]) == 2
        assert prompt["arguments"][0].required is True
        assert prompt["arguments"][1].required is False
    
    def test_register_duplicate_fails(self):
        """Test that duplicate registration fails."""
        registry = PromptRegistry()
        registry.register(
            name="test-prompt",
            description="Test",
            template="Hello!",
        )
        
        with pytest.raises(ValueError, match="already registered"):
            registry.register(
                name="test-prompt",
                description="Duplicate",
                template="World!",
            )
    
    def test_list_prompts(self):
        """Test listing prompts."""
        registry = PromptRegistry()
        registry.register("prompt1", "Desc 1", "Template 1", category="cat1")
        registry.register("prompt2", "Desc 2", "Template 2", category="cat1")
        registry.register("prompt3", "Desc 3", "Template 3", category="cat2")
        
        all_prompts = registry.list_prompts()
        assert len(all_prompts) == 3
        
        cat1_prompts = registry.list_prompts(category="cat1")
        assert len(cat1_prompts) == 2
        
        cat2_prompts = registry.list_prompts(category="cat2")
        assert len(cat2_prompts) == 1
    
    def test_list_categories(self):
        """Test listing categories."""
        registry = PromptRegistry()
        registry.register("p1", "Desc", "Template", category="alpha")
        registry.register("p2", "Desc", "Template", category="beta")
        registry.register("p3", "Desc", "Template", category="alpha")
        
        categories = registry.list_categories()
        assert categories == ["alpha", "beta"]
    
    def test_get_template(self):
        """Test getting raw template."""
        registry = PromptRegistry()
        registry.register(
            name="test",
            description="Test",
            template="Hello {{ name }}!",
        )
        
        template = registry.get_template("test")
        assert template == "Hello {{ name }}!"
    
    def test_get_unknown_prompt(self):
        """Test getting unknown prompt returns None."""
        registry = PromptRegistry()
        assert registry.get("unknown") is None
    
    def test_get_unknown_template(self):
        """Test getting unknown template returns None."""
        registry = PromptRegistry()
        assert registry.get_template("unknown") is None


class TestPromptEngine:
    """Test PromptEngine functionality."""
    
    @pytest.fixture
    def registry_with_prompts(self) -> PromptRegistry:
        """Create a registry with test prompts."""
        registry = PromptRegistry()
        register_all_prompts(registry, graph=None)
        return registry
    
    @pytest.fixture
    def engine(self, registry_with_prompts: PromptRegistry) -> PromptEngine:
        """Create a prompt engine."""
        return PromptEngine(registry_with_prompts, graph=None)
    
    def test_create_engine(self, registry_with_prompts: PromptRegistry):
        """Test engine initialization."""
        engine = PromptEngine(registry_with_prompts)
        assert engine is not None
        assert engine.registry is registry_with_prompts
        assert engine.graph is None
    
    def test_render_simple_prompt(self, engine: PromptEngine):
        """Test rendering a prompt without arguments."""
        # Create a simple test prompt
        engine.registry.register(
            name="simple",
            description="Simple test",
            template="Hello World!",
            arguments=[],
        )
        
        result = engine.render_prompt("simple")
        assert result == "Hello World!"
    
    def test_render_prompt_with_args(self, engine: PromptEngine):
        """Test rendering a prompt with arguments."""
        engine.registry.register(
            name="greeting",
            description="Greeting test",
            template="Hello {{ name }}!",
            arguments=[
                PromptArgument(name="name", description="Name", required=True),
            ],
        )
        
        result = engine.render_prompt("greeting", args={"name": "Alice"})
        assert result == "Hello Alice!"
    
    def test_render_prompt_missing_required_arg(self, engine: PromptEngine):
        """Test that missing required argument raises error."""
        engine.registry.register(
            name="greeting",
            description="Greeting test",
            template="Hello {{ name }}!",
            arguments=[
                PromptArgument(name="name", description="Name", required=True),
            ],
        )
        
        with pytest.raises(ValueError, match="Missing required argument"):
            engine.render_prompt("greeting", args={})
    
    def test_render_prompt_not_found(self, engine: PromptEngine):
        """Test rendering unknown prompt raises error."""
        with pytest.raises(ValueError, match="not found"):
            engine.render_prompt("unknown-prompt")
    
    def test_render_with_context(self, engine: PromptEngine):
        """Test rendering with additional context."""
        engine.registry.register(
            name="context-test",
            description="Context test",
            template="{{ greeting }}, {{ name }}!",
            arguments=[
                PromptArgument(name="name", description="Name", required=True),
            ],
        )
        
        result = engine.render_prompt(
            "context-test",
            args={"name": "Bob"},
            context={"greeting": "Hi"},
        )
        assert result == "Hi, Bob!"
    
    def test_list_prompts(self, engine: PromptEngine):
        """Test listing prompts."""
        result = engine.list_prompts()
        assert "Available Prompts" in result
        assert len(result) > 0
    
    def test_list_prompts_by_category(self, engine: PromptEngine):
        """Test listing prompts by category."""
        result = engine.list_prompts(category="onboarding")
        assert "Available Prompts" in result
    
    def test_get_prompt_info(self, engine: PromptEngine):
        """Test getting prompt info."""
        result = engine.get_prompt_info("onboard-agent")
        assert "onboard-agent" in result
        assert "Description" in result
    
    def test_get_unknown_prompt_info(self, engine: PromptEngine):
        """Test getting info for unknown prompt."""
        result = engine.get_prompt_info("unknown")
        assert "not found" in result


class TestOnboardingPrompts:
    """Test onboarding prompt templates."""
    
    @pytest.fixture
    def engine(self) -> PromptEngine:
        """Create engine with onboarding prompts."""
        registry = PromptRegistry()
        register_all_prompts(registry, graph=None)
        return PromptEngine(registry, graph=None)
    
    def test_onboard_agent_exists(self, engine: PromptEngine):
        """Test onboard-agent prompt exists."""
        assert engine.registry.has_prompt("onboard-agent")
    
    def test_onboard_agent_renders(self, engine: PromptEngine):
        """Test onboard-agent renders without error."""
        result = engine.render_prompt("onboard-agent")
        assert "Project Overview" in result
        assert "Architecture" in result
    
    def test_find_entry_point_exists(self, engine: PromptEngine):
        """Test find-entry-point prompt exists."""
        assert engine.registry.has_prompt("find-entry-point")
    
    def test_find_entry_point_renders(self, engine: PromptEngine):
        """Test find-entry-point renders without error."""
        result = engine.render_prompt("find-entry-point")
        assert "Entry Points" in result


class TestModificationPrompts:
    """Test modification prompt templates."""
    
    @pytest.fixture
    def engine(self) -> PromptEngine:
        """Create engine with modification prompts."""
        registry = PromptRegistry()
        register_all_prompts(registry, graph=None)
        return PromptEngine(registry, graph=None)
    
    def test_plan_feature_exists(self, engine: PromptEngine):
        """Test plan-feature prompt exists."""
        assert engine.registry.has_prompt("plan-feature")
    
    def test_plan_feature_requires_arg(self, engine: PromptEngine):
        """Test plan-feature requires feature_description arg."""
        with pytest.raises(ValueError, match="Missing required argument"):
            engine.render_prompt("plan-feature", args={})
    
    def test_plan_feature_renders(self, engine: PromptEngine):
        """Test plan-feature renders with arg."""
        result = engine.render_prompt(
            "plan-feature",
            args={"feature_description": "Add caching"}
        )
        assert "Feature Plan:" in result
        assert "Add caching" in result
    
    def test_trace_bug_exists(self, engine: PromptEngine):
        """Test trace-bug prompt exists."""
        assert engine.registry.has_prompt("trace-bug")
    
    def test_trace_bug_renders(self, engine: PromptEngine):
        """Test trace-bug renders with arg."""
        result = engine.render_prompt(
            "trace-bug",
            args={"symptom": "Connection timeout"}
        )
        assert "Bug Trace:" in result
    
    def test_review_change_exists(self, engine: PromptEngine):
        """Test review-change prompt exists."""
        assert engine.registry.has_prompt("review-change")
    
    def test_review_change_renders(self, engine: PromptEngine):
        """Test review-change renders."""
        result = engine.render_prompt("review-change", args={})
        assert "Change Review" in result
    
    def test_refactor_guide_exists(self, engine: PromptEngine):
        """Test refactor-guide prompt exists."""
        assert engine.registry.has_prompt("refactor-guide")
    
    def test_refactor_guide_renders(self, engine: PromptEngine):
        """Test refactor-guide renders with args."""
        result = engine.render_prompt(
            "refactor-guide",
            args={"target": "database module", "goal": "Improve performance"}
        )
        assert "Refactoring Guide:" in result


class TestNavigationPrompts:
    """Test navigation prompt templates."""
    
    @pytest.fixture
    def engine(self) -> PromptEngine:
        """Create engine with navigation prompts."""
        registry = PromptRegistry()
        register_all_prompts(registry, graph=None)
        return PromptEngine(registry, graph=None)
    
    def test_understand_flow_exists(self, engine: PromptEngine):
        """Test understand-flow prompt exists."""
        assert engine.registry.has_prompt("understand-flow")
    
    def test_understand_flow_requires_args(self, engine: PromptEngine):
        """Test understand-flow requires source and target."""
        with pytest.raises(ValueError, match="Missing required argument"):
            engine.render_prompt("understand-flow", args={})
    
    def test_understand_flow_renders(self, engine: PromptEngine):
        """Test understand-flow renders with args."""
        result = engine.render_prompt(
            "understand-flow",
            args={"source": "API", "target": "Database"}
        )
        assert "Data Flow:" in result
        assert "API" in result
        assert "Database" in result
    
    def test_find_similar_exists(self, engine: PromptEngine):
        """Test find-similar prompt exists."""
        assert engine.registry.has_prompt("find-similar")
    
    def test_find_similar_renders(self, engine: PromptEngine):
        """Test find-similar renders with arg."""
        result = engine.render_prompt(
            "find-similar",
            args={"code_pattern": "def login"}
        )
        assert "Similar Code Search" in result


class TestAnalysisPrompts:
    """Test analysis prompt templates."""
    
    @pytest.fixture
    def engine(self) -> PromptEngine:
        """Create engine with analysis prompts."""
        registry = PromptRegistry()
        register_all_prompts(registry, graph=None)
        return PromptEngine(registry, graph=None)
    
    def test_summarize_changes_exists(self, engine: PromptEngine):
        """Test summarize-changes prompt exists."""
        assert engine.registry.has_prompt("summarize-changes")
    
    def test_summarize_changes_requires_args(self, engine: PromptEngine):
        """Test summarize-changes requires refs."""
        with pytest.raises(ValueError, match="Missing required argument"):
            engine.render_prompt("summarize-changes", args={})
    
    def test_summarize_changes_renders(self, engine: PromptEngine):
        """Test summarize-changes renders with args."""
        result = engine.render_prompt(
            "summarize-changes",
            args={"from_ref": "v1.0", "to_ref": "v1.1"}
        )
        assert "Code Change Summary" in result
        assert "v1.0" in result
        assert "v1.1" in result
    
    def test_write_test_exists(self, engine: PromptEngine):
        """Test write-test prompt exists."""
        assert engine.registry.has_prompt("write-test")
    
    def test_write_test_renders(self, engine: PromptEngine):
        """Test write-test renders with arg."""
        result = engine.render_prompt(
            "write-test",
            args={"module_path": "src/auth.py"}
        )
        assert "Test Generation Plan" in result
        assert "src/auth.py" in result


class TestPromptCategories:
    """Test prompt categorization."""
    
    def test_all_categories_registered(self):
        """Test all expected categories exist."""
        registry = PromptRegistry()
        register_all_prompts(registry, graph=None)
        
        categories = registry.list_categories()
        assert "onboarding" in categories
        assert "modification" in categories
        assert "navigation" in categories
        assert "analysis" in categories
    
    def test_prompts_per_category(self):
        """Test correct number of prompts per category."""
        registry = PromptRegistry()
        register_all_prompts(registry, graph=None)
        
        onboarding = registry.list_prompts(category="onboarding")
        assert len(onboarding) == 2  # onboard-agent, find-entry-point
        
        modification = registry.list_prompts(category="modification")
        assert len(modification) == 4  # plan-feature, trace-bug, review-change, refactor-guide
        
        navigation = registry.list_prompts(category="navigation")
        assert len(navigation) == 2  # understand-flow, find-similar
        
        analysis = registry.list_prompts(category="analysis")
        assert len(analysis) == 2  # summarize-changes, write-test