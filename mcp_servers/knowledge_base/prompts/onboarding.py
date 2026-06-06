#!/usr/bin/env python3
"""
Onboarding Prompts for KB MCP v4.

Helps agents get oriented with a new project.
"""

from graph.queries import GraphQueries
from prompts.registry import PromptRegistry

ONBOARD_AGENT_TEMPLATE = """# Project Overview

{{ project_summary }}

## Architecture

{{ arch_layers }}

## Key Components

{{ key_components }}

## Entry Points

{{ entry_points }}

## How to Navigate

The KB exposes these resources to help you:
- `knowledge-base://arch/components` — all components
- `knowledge-base://flows/data` — data flow
- `knowledge-base://api/endpoints` — API surface

Suggested first steps:
1. Read `knowledge-base://project/tree`
2. Read `knowledge-base://arch/dependencies`
3. Ask a specific question via `kb_query_tool`
"""

FIND_ENTRY_POINT_TEMPLATE = """# Entry Points

{{ entry_points_detailed }}

## Main Flow

{% if main_flow_diagram %}
```mermaid
{{ main_flow_diagram }}
```
{% endif %}

## Startup Sequence

{{ startup_sequence }}
"""


def register_onboarding_prompts(registry: "PromptRegistry", graph: "KnowledgeGraph" | None = None) -> None:
    """
    Register onboarding-related prompts.
    
    Args:
        registry: Prompt registry to register with
        graph: Optional knowledge graph for data loading
    """
    from .registry import PromptArgument
    
    # onboard-agent prompt
    registry.register(
        name="onboard-agent",
        description="I'm new to this project. Explain it to me.",
        template=ONBOARD_AGENT_TEMPLATE,
        arguments=[],
        category="onboarding",
    )
    
    # find-entry-point prompt
    registry.register(
        name="find-entry-point",
        description="Where does this application start?",
        template=FIND_ENTRY_POINT_TEMPLATE,
        arguments=[],
        category="onboarding",
    )


def load_onboard_agent_data(graph: "KnowledgeGraph" | None = None) -> dict[str, str]:
    """
    Load data for the onboard-agent prompt.
    
    Args:
        graph: Knowledge graph (optional, will use stubs if None)
        
    Returns:
        Dictionary of template variables
    """
    if graph is None:
        return {
            "project_summary": "Project summary not available (graph not connected).",
            "arch_layers": "Architecture layers not available.",
            "key_components": "Key components not available.",
            "entry_points": "Entry points not available.",
        }
    
    queries = GraphQueries(graph)
    
    # Get project summary
    summary = queries.get_project_summary()
    
    # Get architecture layers
    layers = queries.get_arch_layers()
    arch_text = "\n".join([f"- {layer}" for layer in layers]) if layers else "No layers detected"
    
    # Get key components
    components = queries.get_key_components(limit=10)
    comp_text = "\n".join([f"- {c.name} ({c.kind})" for c in components]) if components else "No components detected"
    
    # Get entry points
    entry_points = queries.get_entry_points()
    ep_text = "\n".join([f"- {ep.name} in {ep.file_path}" for ep in entry_points]) if entry_points else "No entry points detected"
    
    return {
        "project_summary": summary,
        "arch_layers": arch_text,
        "key_components": comp_text,
        "entry_points": ep_text,
    }


def load_entry_point_data(graph: "KnowledgeGraph" | None = None) -> dict[str, str]:
    """
    Load data for the find-entry-point prompt.
    
    Args:
        graph: Knowledge graph (optional)
        
    Returns:
        Dictionary of template variables
    """
    if graph is None:
        return {
            "entry_points_detailed": "Entry points not available (graph not connected).",
            "main_flow_diagram": "",
            "startup_sequence": "Startup sequence not available.",
        }
    
    queries = GraphQueries(graph)
    entry_points = queries.get_entry_points()
    
    # Format detailed entry points
    detailed = []
    for ep in entry_points:
        detailed.append(f"## {ep.name}\n- File: {ep.file_path}\n- Kind: {ep.kind}")
        if ep.doc:
            detailed.append(f"- Description: {ep.doc[:200]}...")
    
    # Try to get main flow diagram
    try:
        from graph.export import GraphExporter
        exporter = GraphExporter(graph)
        main_flow = exporter.to_mermaid(depth=2)
    except Exception:
        main_flow = ""
    
    return {
        "entry_points_detailed": "\n\n".join(detailed) if detailed else "No entry points found",
        "main_flow_diagram": main_flow,
        "startup_sequence": "Analyze entry points above for startup sequence.",
    }