#!/usr/bin/env python3
"""
Integration tests for MCP Prompts Layer in KB MCP v4.

Tests all 10 prompts, rendering with arguments, templates, and error handling.
"""

import pytest

from prompts.engine import PromptEngine, register_all_prompts
from prompts.registry import PromptArgument, PromptRegistry


@pytest.fixture
def registry_with_prompts():
    """Create a registry with all prompts registered."""
    registry = PromptRegistry()
    register_all_prompts(registry, graph=None)
    return registry


@pytest.fixture
def prompt_engine(registry_with_prompts):
    """Create a prompt engine with all prompts."""
    return PromptEngine(registry_with_prompts, graph=None)


class TestAllPromptsRegistered:
    """Test all 10 MCP prompts are registered."""
    
    def test_onboard_agent_registered(self, registry_with_prompts):
        """Test onboard-agent prompt is registered."""
        assert registry_with_prompts.has_prompt("onboard-agent")
    
    def test_find_entry_point_registered(self, registry_with_prompts):
        """Test find-entry-point prompt is registered."""
        assert registry_with_prompts.has_prompt("find-entry-point")
    
    def test_plan_feature_registered(self, registry_with_prompts):
        """Test plan-feature prompt is registered."""
        assert registry_with_prompts.has_prompt("plan-feature")
    
    def test_trace_bug_registered(self, registry_with_prompts):
        """Test trace-bug prompt is registered."""
        assert registry_with_prompts.has_prompt("trace-bug")
    
    def test_understand_flow_registered(self, registry_with_prompts):
        """Test understand-flow prompt is registered."""
        assert registry_with_prompts.has_prompt("understand-flow")
    
    def test_review_change_registered(self, registry_with_prompts):
        """Test review-change prompt is registered."""
        assert registry_with_prompts.has_prompt("review-change")
    
    def test_find_similar_registered(self, registry_with_prompts):
        """Test find-similar prompt is registered."""
        assert registry_with_prompts.has_prompt("find-similar")
    
    def test_write_test_registered(self, registry_with_prompts):
        """Test write-test prompt is registered."""
        assert registry_with_prompts.has_prompt("write-test")
    
    def test_refactor_guide_registered(self, registry_with_prompts):
        """Test refactor-guide prompt is registered."""
        assert registry_with_prompts.has_prompt("refactor-guide")
    
    def test_summarize_changes_registered(self, registry_with_prompts):
        """Test summarize-changes prompt is registered."""
        assert registry_with_prompts.has_prompt("summarize-changes")
    
    def test_total_prompt_count(self, registry_with_prompts):
        """Test total prompt count is 10."""
        prompts = registry_with_prompts.list_prompts()
        assert len(prompts) == 10, f"Expected 10 prompts, got {len(prompts)}"
    
    def test_all_prompts_have_descriptions(self, registry_with_prompts):
        """Test all prompts have descriptions."""
        prompts = registry_with_prompts.list_prompts()
        for prompt_info in prompts:
            assert "description" in prompt_info
            assert len(prompt_info["description"]) > 0
    
    def test_all_prompts_have_templates(self, registry_with_prompts):
        """Test all prompts have templates."""
        for prompt_name in [p["name"] for p in registry_with_prompts.list_prompts()]:
            template = registry_with_prompts.get_template(prompt_name)
            assert template is not None
            assert len(template) > 0


class TestPromptCategories:
    """Test prompt categorization."""
    
    def test_onboarding_category_exists(self, registry_with_prompts):
        """Test onboarding category exists."""
        categories = registry_with_prompts.list_categories()
        assert "onboarding" in categories
    
    def test_modification_category_exists(self, registry_with_prompts):
        """Test modification category exists."""
        categories = registry_with_prompts.list_categories()
        assert "modification" in categories
    
    def test_navigation_category_exists(self, registry_with_prompts):
        """Test navigation category exists."""
        categories = registry_with_prompts.list_categories()
        assert "navigation" in categories
    
    def test_analysis_category_exists(self, registry_with_prompts):
        """Test analysis category exists."""
        categories = registry_with_prompts.list_categories()
        assert "analysis" in categories
    
    def test_onboarding_prompts_count(self, registry_with_prompts):
        """Test correct number of onboarding prompts."""
        prompts = registry_with_prompts.list_prompts(category="onboarding")
        assert len(prompts) == 2  # onboard-agent, find-entry-point
    
    def test_modification_prompts_count(self, registry_with_prompts):
        """Test correct number of modification prompts."""
        prompts = registry_with_prompts.list_prompts(category="modification")
        assert len(prompts) == 4  # plan-feature, trace-bug, review-change, refactor-guide
    
    def test_navigation_prompts_count(self, registry_with_prompts):
        """Test correct number of navigation prompts."""
        prompts = registry_with_prompts.list_prompts(category="navigation")
        assert len(prompts) == 2  # understand-flow, find-similar
    
    def test_analysis_prompts_count(self, registry_with_prompts):
        """Test correct number of analysis prompts."""
        prompts = registry_with_prompts.list_prompts(category="analysis")
        assert len(prompts) == 2  # summarize-changes, write-test


class TestPromptRendering:
    """Test prompt rendering with arguments."""
    
    def test_render_onboard_agent_no_args(self, prompt_engine):
        """Test onboard-agent renders without arguments."""
        result = prompt_engine.render_prompt("onboard-agent")
        assert "Project Overview" in result
        assert len(result) > 0
    
    def test_render_find_entry_point_no_args(self, prompt_engine):
        """Test find-entry-point renders without arguments."""
        result = prompt_engine.render_prompt("find-entry-point")
        assert "Entry Points" in result
    
    def test_render_plan_feature_with_arg(self, prompt_engine):
        """Test plan-feature renders with feature_description."""
        result = prompt_engine.render_prompt(
            "plan-feature",
            args={"feature_description": "Add user authentication"}
        )
        assert "Add user authentication" in result
        assert "Feature Plan" in result
    
    def test_render_plan_feature_missing_arg(self, prompt_engine):
        """Test plan-feature fails without required arg."""
        with pytest.raises(ValueError, match="Missing required argument"):
            prompt_engine.render_prompt("plan-feature", args={})
    
    def test_render_trace_bug_with_arg(self, prompt_engine):
        """Test trace-bug renders with symptom."""
        result = prompt_engine.render_prompt(
            "trace-bug",
            args={"symptom": "Connection timeout error"}
        )
        assert "Bug Trace" in result
    
    def test_render_understand_flow_with_args(self, prompt_engine):
        """Test understand-flow renders with source and target."""
        result = prompt_engine.render_prompt(
            "understand-flow",
            args={"source": "API", "target": "Database"}
        )
        assert "Data Flow" in result
        assert "API" in result
        assert "Database" in result
    
    def test_render_understand_flow_missing_args(self, prompt_engine):
        """Test understand-flow fails without required args."""
        with pytest.raises(ValueError, match="Missing required argument"):
            prompt_engine.render_prompt("understand-flow", args={})
    
    def test_render_review_change_optional_args(self, prompt_engine):
        """Test review-change renders with optional args."""
        result = prompt_engine.render_prompt(
            "review-change",
            args={"planned_changes": "Refactor database module"}
        )
        assert "Change Review" in result
    
    def test_render_find_similar_with_arg(self, prompt_engine):
        """Test find-similar renders with code_pattern."""
        result = prompt_engine.render_prompt(
            "find-similar",
            args={"code_pattern": "def login(username, password)"}
        )
        assert "Similar Code" in result
    
    def test_render_write_test_with_arg(self, prompt_engine):
        """Test write-test renders with module_path."""
        result = prompt_engine.render_prompt(
            "write-test",
            args={"module_path": "src/auth.py"}
        )
        assert "Test Generation" in result
        assert "src/auth.py" in result
    
    def test_render_refactor_guide_with_args(self, prompt_engine):
        """Test refactor-guide renders with target and goal."""
        result = prompt_engine.render_prompt(
            "refactor-guide",
            args={"target": "database module", "goal": "Improve performance"}
        )
        assert "Refactoring Guide" in result
    
    def test_render_summarize_changes_with_args(self, prompt_engine):
        """Test summarize-changes renders with refs."""
        result = prompt_engine.render_prompt(
            "summarize-changes",
            args={"from_ref": "v1.0", "to_ref": "v1.1"}
        )
        assert "Code Change Summary" in result
        assert "v1.0" in result
        assert "v1.1" in result


class TestPromptTemplates:
    """Test prompt templates load correctly."""
    
    def test_onboard_agent_template_not_empty(self, registry_with_prompts):
        """Test onboard-agent template is not empty."""
        template = registry_with_prompts.get_template("onboard-agent")
        assert len(template) > 50
    
    def test_plan_feature_template_has_placeholder(self, registry_with_prompts):
        """Test plan-feature template has feature_description placeholder."""
        template = registry_with_prompts.get_template("plan-feature")
        assert "{{" in template and "}}" in template
    
    def test_understand_flow_template_has_placeholders(self, registry_with_prompts):
        """Test understand-flow template has source and target placeholders."""
        template = registry_with_prompts.get_template("understand-flow")
        assert "source" in template.lower()
        assert "target" in template.lower()
    
    def test_refactor_guide_template_structure(self, registry_with_prompts):
        """Test refactor-guide template has proper structure."""
        template = registry_with_prompts.get_template("refactor-guide")
        assert "target" in template.lower()
        assert "goal" in template.lower()
    
    def test_summarize_changes_template_has_refs(self, registry_with_prompts):
        """Test summarize-changes template has ref placeholders."""
        template = registry_with_prompts.get_template("summarize-changes")
        assert "from_ref" in template.lower() or "from" in template.lower()
        assert "to_ref" in template.lower() or "to" in template.lower()
    
    def test_all_templates_are_strings(self, registry_with_prompts):
        """Test all templates are strings."""
        for prompt_info in registry_with_prompts.list_prompts():
            template = registry_with_prompts.get_template(prompt_info["name"])
            assert isinstance(template, str)
    
    def test_templates_contain_jinja_syntax(self, registry_with_prompts):
        """Test templates use Jinja2 syntax."""
        templates_with_syntax = 0
        for prompt_info in registry_with_prompts.list_prompts():
            template = registry_with_prompts.get_template(prompt_info["name"])
            if "{{" in template or "{%" in template:
                templates_with_syntax += 1
        
        assert templates_with_syntax > 0, "No templates use Jinja2 syntax"


class TestPromptErrorHandling:
    """Test prompt error handling."""
    
    def test_render_unknown_prompt_raises_error(self, prompt_engine):
        """Test rendering unknown prompt raises error."""
        with pytest.raises(ValueError, match="not found"):
            prompt_engine.render_prompt("nonexistent-prompt")
    
    def test_render_missing_required_arg_raises_error(self, prompt_engine):
        """Test missing required argument raises error."""
        with pytest.raises(ValueError, match="Missing required argument"):
            prompt_engine.render_prompt("plan-feature", args={})
    
    def test_render_with_extra_args_succeeds(self, prompt_engine):
        """Test rendering with extra arguments succeeds."""
        result = prompt_engine.render_prompt(
            "plan-feature",
            args={
                "feature_description": "Add caching",
                "extra_arg": "ignored",
            }
        )
        assert "Add caching" in result
    
    def test_get_unknown_prompt_info(self, prompt_engine):
        """Test getting info for unknown prompt."""
        result = prompt_engine.get_prompt_info("unknown")
        assert "not found" in result
    
    def test_list_prompts_by_unknown_category(self, prompt_engine):
        """Test listing prompts by unknown category."""
        result = prompt_engine.list_prompts(category="nonexistent")
        assert "Available Prompts" in result
    
    def test_render_with_none_args(self, prompt_engine):
        """Test rendering with None args."""
        result = prompt_engine.render_prompt("onboard-agent", args=None)
        assert len(result) > 0
    
    def test_render_with_empty_args_dict(self, prompt_engine):
        """Test rendering with empty args dict."""
        result = prompt_engine.render_prompt("onboard-agent", args={})
        assert len(result) > 0


class TestPromptEngineInterface:
    """Test prompt engine interface."""
    
    def test_list_prompts_returns_formatted_text(self, prompt_engine):
        """Test list_prompts returns formatted text."""
        result = prompt_engine.list_prompts()
        assert "Available Prompts" in result
        assert len(result) > 0
    
    def test_list_prompts_by_category(self, prompt_engine):
        """Test list_prompts filters by category."""
        result = prompt_engine.list_prompts(category="onboarding")
        assert "Available Prompts" in result
        assert "onboard-agent" in result or "find-entry-point" in result
    
    def test_get_prompt_info_returns_details(self, prompt_engine):
        """Test get_prompt_info returns details."""
        result = prompt_engine.get_prompt_info("plan-feature")
        assert "plan-feature" in result
        assert "Description" in result
        assert "Arguments" in result
    
    def test_render_prompt_with_context(self, prompt_engine):
        """Test rendering prompt with additional context."""
        registry = prompt_engine.registry
        registry.register(
            name="test-context",
            description="Test",
            template="{{ greeting }}, {{ name }}!",
            arguments=[
                PromptArgument(name="name", description="Name", required=True),
            ],
        )
        
        result = prompt_engine.render_prompt(
            "test-context",
            args={"name": "Alice"},
            context={"greeting": "Hello"},
        )
        assert "Hello, Alice!" in result