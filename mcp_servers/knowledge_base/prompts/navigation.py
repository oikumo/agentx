#!/usr/bin/env python3
"""
Navigation Prompts for KB MCP v4.

Helps agents navigate and understand code flows.
"""

UNDERSTAND_FLOW_TEMPLATE = """# Data Flow: {{ source }} → {{ target }}

## Flow Path

{{ flow_path }}

## Key Functions

{{ key_functions }}

## Diagram

{% if flow_diagram %}
```mermaid
{{ flow_diagram }}
```
{% endif %}

## Description

{{ flow_description }}
"""

FIND_SIMILAR_TEMPLATE = """# Similar Code Search

## Search Pattern

{{ code_pattern }}

## Matches Found

{{ matches }}

## Similarity Scores

{{ similarity_scores }}

## Recommendations

{{ recommendations }}
"""


def register_navigation_prompts(registry: "PromptRegistry", graph: "KnowledgeGraph" | None = None) -> None:
    """
    Register navigation-related prompts.
    
    Args:
        registry: Prompt registry to register with
        graph: Optional knowledge graph for data loading
    """
    from .registry import PromptArgument
    
    # understand-flow prompt
    registry.register(
        name="understand-flow",
        description="Explain how data flows from A to B.",
        template=UNDERSTAND_FLOW_TEMPLATE,
        arguments=[
            PromptArgument(
                name="source",
                description="Starting point",
                required=True,
            ),
            PromptArgument(
                name="target",
                description="End point",
                required=True,
            ),
        ],
        category="navigation",
    )
    
    # find-similar prompt
    registry.register(
        name="find-similar",
        description="Find code similar to this pattern.",
        template=FIND_SIMILAR_TEMPLATE,
        arguments=[
            PromptArgument(
                name="code_pattern",
                description="Code pattern to search for",
                required=True,
            ),
        ],
        category="navigation",
    )


def load_understand_flow_data(source: str, target: str, graph: "KnowledgeGraph" | None = None) -> dict[str, str]:
    """
    Load data for the understand-flow prompt.
    
    Args:
        source: Starting point
        target: End point
        graph: Knowledge graph (optional)
        
    Returns:
        Dictionary of template variables
    """
    if graph is None:
        return {
            "source": source,
            "target": target,
            "flow_path": "Flow path not available (graph not connected).",
            "key_functions": "Key functions not available.",
            "flow_diagram": "",
            "flow_description": "Flow analysis not available.",
        }
    
    # TODO: Implement flow tracing using graph
    return {
        "source": source,
        "target": target,
        "flow_path": "Analysis pending implementation.",
        "key_functions": "Analysis pending.",
        "flow_diagram": "",
        "flow_description": "Analysis pending.",
    }


def load_find_similar_data(code_pattern: str, graph: "KnowledgeGraph" | None = None) -> dict[str, str]:
    """
    Load data for the find-similar prompt.
    
    Args:
        code_pattern: Code pattern to search for
        graph: Knowledge graph (optional)
        
    Returns:
        Dictionary of template variables
    """
    if graph is None:
        return {
            "code_pattern": code_pattern,
            "matches": "Search not available (graph not connected).",
            "similarity_scores": "Scoring not available.",
            "recommendations": "Recommendations not available.",
        }
    
    # TODO: Implement pattern matching using graph
    return {
        "code_pattern": code_pattern,
        "matches": "Search pending implementation.",
        "similarity_scores": "Scoring pending.",
        "recommendations": "Analysis pending.",
    }