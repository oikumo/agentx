#!/usr/bin/env python3
"""
Prompt Engine for KB MCP v4.

Renders prompt templates with live KB data using Jinja2.
"""

from typing import Any

from jinja2 import Template

from graph.engine import KnowledgeGraph
from prompts.registry import PromptRegistry


class PromptEngine:
    """
    Engine for rendering prompt templates with live KB data.
    
    Integrates with PromptRegistry and KnowledgeGraph to provide
    context-aware prompt rendering.
    
    Example:
        engine = PromptEngine(registry, graph)
        rendered = engine.render_prompt(
            "onboard-agent",
            context={}
        )
    """
    
    def __init__(self, registry: PromptRegistry, graph: KnowledgeGraph | None = None):
        """
        Initialize the prompt engine.
        
        Args:
            registry: Prompt registry with templates
            graph: Optional knowledge graph for data loading
        """
        self._registry = registry
        self._graph = graph
    
    @property
    def registry(self) -> PromptRegistry:
        """Get the prompt registry."""
        return self._registry
    
    @property
    def graph(self) -> KnowledgeGraph | None:
        """Get the knowledge graph."""
        return self._graph
    
    def render_prompt(
        self,
        prompt_name: str,
        args: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
    ) -> str:
        """
        Render a prompt template with live data.
        
        Args:
            prompt_name: Name of the prompt to render
            args: User-provided arguments for the template
            context: Additional context variables
            
        Returns:
            Rendered prompt string
            
        Raises:
            ValueError: If prompt not found or missing required args
        """
        prompt = self._registry.get(prompt_name)
        if not prompt:
            raise ValueError(f"Prompt '{prompt_name}' not found")
        
        # Validate required arguments
        template_args = args or {}
        for arg in prompt["arguments"]:
            if arg.required and arg.name not in template_args:
                raise ValueError(f"Missing required argument: {arg.name}")
        
        # Load prompt-specific data
        data = self._load_prompt_data(prompt_name, template_args)
        
        # Merge with user args and context
        data.update(template_args)
        if context:
            data.update(context)
        
        # Render template
        template = Template(prompt["template"])
        return template.render(**data)
    
    def _load_prompt_data(self, prompt_name: str, args: dict[str, Any]) -> dict[str, Any]:
        """
        Load live KB data for a specific prompt.
        
        Args:
            prompt_name: Name of the prompt
            args: User-provided arguments
            
        Returns:
            Dictionary of template variables
        """
        # Import data loaders lazily to avoid circular imports
        if prompt_name == "onboard-agent":
            from .onboarding import load_onboard_agent_data
            return load_onboard_agent_data(self._graph)
        
        elif prompt_name == "find-entry-point":
            from .onboarding import load_entry_point_data
            return load_entry_point_data(self._graph)
        
        elif prompt_name == "plan-feature":
            from .modification import load_plan_feature_data
            feature_desc = args.get("feature_description", "")
            return load_plan_feature_data(feature_desc, self._graph)
        
        elif prompt_name == "trace-bug":
            from .modification import load_trace_bug_data
            symptom = args.get("symptom", "")
            return load_trace_bug_data(symptom, self._graph)
        
        elif prompt_name == "review-change":
            from .modification import load_review_change_data
            changes = args.get("planned_changes", "")
            return load_review_change_data(changes, self._graph)
        
        elif prompt_name == "refactor-guide":
            from .modification import load_refactor_guide_data
            target = args.get("target", "")
            goal = args.get("goal", "")
            return load_refactor_guide_data(target, goal, self._graph)
        
        elif prompt_name == "understand-flow":
            from .navigation import load_understand_flow_data
            source = args.get("source", "")
            target = args.get("target", "")
            return load_understand_flow_data(source, target, self._graph)
        
        elif prompt_name == "find-similar":
            from .navigation import load_find_similar_data
            pattern = args.get("code_pattern", "")
            return load_find_similar_data(pattern, self._graph)
        
        elif prompt_name == "summarize-changes":
            from .analysis import load_summarize_changes_data
            from_ref = args.get("from_ref", "")
            to_ref = args.get("to_ref", "")
            return load_summarize_changes_data(from_ref, to_ref, self._graph)
        
        elif prompt_name == "write-test":
            from .analysis import load_write_test_data
            module_path = args.get("module_path", "")
            return load_write_test_data(module_path, self._graph)
        
        else:
            return {}
    
    def list_prompts(self, category: str | None = None) -> str:
        """
        List available prompts.
        
        Args:
            category: Optional category filter
            
        Returns:
            Formatted list of prompts
        """
        prompts = self._registry.list_prompts(category)
        
        if not prompts:
            return "No prompts found."
        
        lines = ["## Available Prompts\n"]
        for prompt in prompts:
            args_str = ""
            if prompt.arguments:
                arg_names = [arg.name for arg in prompt.arguments]
                args_str = f" (args: {', '.join(arg_names)})"
            lines.append(f"- **{prompt.name}**{args_str}: {prompt.description}")
        
        return "\n".join(lines)
    
    def get_prompt_info(self, prompt_name: str) -> str:
        """
        Get detailed information about a prompt.
        
        Args:
            prompt_name: Name of the prompt
            
        Returns:
            Formatted prompt information
        """
        prompt = self._registry.get(prompt_name)
        if not prompt:
            return f"Prompt '{prompt_name}' not found."
        
        lines = [
            f"## {prompt_name}",
            f"\n**Description**: {prompt['description']}",
            f"**Category**: {prompt['category']}",
        ]
        
        if prompt["arguments"]:
            lines.append("\n**Arguments**:")
            for arg in prompt["arguments"]:
                req = "required" if arg.required else "optional"
                lines.append(f"- `{arg.name}` ({req}): {arg.description}")
        
        return "\n".join(lines)


def register_all_prompts(registry: PromptRegistry, graph: KnowledgeGraph | None = None) -> None:
    """
    Register all prompt templates.
    
    Args:
        registry: Prompt registry to register with
        graph: Optional knowledge graph for data loading
    """
    from .onboarding import register_onboarding_prompts
    from .modification import register_modification_prompts
    from .navigation import register_navigation_prompts
    from .analysis import register_analysis_prompts
    
    register_onboarding_prompts(registry, graph)
    register_modification_prompts(registry, graph)
    register_navigation_prompts(registry, graph)
    register_analysis_prompts(registry, graph)