#!/usr/bin/env python3
"""
Modification Prompts for KB MCP v4.

Helps agents plan features, trace bugs, and review changes.
"""

PLAN_FEATURE_TEMPLATE = """# Feature Plan: {{ feature_description }}

## Related Components

{{ related_components }}

## Suggested Modification Order

{{ modification_order }}

## Files Likely Affected

{{ affected_files }}

## Tests to Update

{{ related_tests }}

## Impact Analysis

{{ impact_summary }}
"""

TRACE_BUG_TEMPLATE = """# Bug Trace: {{ symptom }}

## Potential Root Cause Paths

{{ trace_paths }}

## Relevant Code Paths

{{ code_paths }}

## Suggested Investigation Order

{{ investigation_order }}

## Related Components

{{ related_components }}
"""

REVIEW_CHANGE_TEMPLATE = """# Change Review

## Planned Changes

{{ planned_changes }}

## Risk Assessment

{{ risk_assessment }}

## Affected Components

{{ affected_components }}

## Recommended Tests

{{ recommended_tests }}

## Potential Issues

{{ potential_issues }}

## Suggested Implementation Order

{{ implementation_order }}
"""

REFACTOR_GUIDE_TEMPLATE = """# Refactoring Guide: {{ target }}

## Goal

{{ goal }}

## Current State

{{ current_state }}

## Target State

{{ target_state }}

## Refactoring Steps

{{ refactoring_steps }}

## Files to Modify

{{ files_to_modify }}

## Tests to Update

{{ tests_to_update }}

## Risks and Mitigations

{{ risks }}
"""


def register_modification_prompts(registry: "PromptRegistry", graph: "KnowledgeGraph" | None = None) -> None:
    """
    Register modification-related prompts.
    
    Args:
        registry: Prompt registry to register with
        graph: Optional knowledge graph for data loading
    """
    from .registry import PromptArgument
    
    # plan-feature prompt
    registry.register(
        name="plan-feature",
        description="I need to add feature X. What do I modify?",
        template=PLAN_FEATURE_TEMPLATE,
        arguments=[
            PromptArgument(
                name="feature_description",
                description="Brief description of the feature",
                required=True,
            ),
        ],
        category="modification",
    )
    
    # trace-bug prompt
    registry.register(
        name="trace-bug",
        description="Bug in Y. Trace the root cause.",
        template=TRACE_BUG_TEMPLATE,
        arguments=[
            PromptArgument(
                name="symptom",
                description="What's the bug symptom?",
                required=True,
            ),
        ],
        category="modification",
    )
    
    # review-change prompt
    registry.register(
        name="review-change",
        description="Review my planned changes for issues.",
        template=REVIEW_CHANGE_TEMPLATE,
        arguments=[
            PromptArgument(
                name="planned_changes",
                description="Description of planned changes",
                required=False,
            ),
        ],
        category="modification",
    )
    
    # refactor-guide prompt
    registry.register(
        name="refactor-guide",
        description="Guide me through refactoring X.",
        template=REFACTOR_GUIDE_TEMPLATE,
        arguments=[
            PromptArgument(
                name="target",
                description="What to refactor",
                required=True,
            ),
            PromptArgument(
                name="goal",
                description="Refactoring goal",
                required=False,
            ),
        ],
        category="modification",
    )


def load_plan_feature_data(feature_description: str, graph: "KnowledgeGraph" | None = None) -> dict[str, str]:
    """
    Load data for the plan-feature prompt.
    
    Args:
        feature_description: Description of the feature to add
        graph: Knowledge graph (optional)
        
    Returns:
        Dictionary of template variables
    """
    if graph is None:
        return {
            "feature_description": feature_description,
            "related_components": "Component analysis not available (graph not connected).",
            "modification_order": "1. Analysis not available\n2. Implementation not available\n3. Testing not available",
            "affected_files": "File analysis not available.",
            "related_tests": "Test analysis not available.",
            "impact_summary": "Impact analysis not available.",
        }
    
    # TODO: Implement feature planning logic using graph
    # For now, return placeholder
    return {
        "feature_description": feature_description,
        "related_components": "Analysis pending implementation.",
        "modification_order": "Implementation pending.",
        "affected_files": "Analysis pending.",
        "related_tests": "Analysis pending.",
        "impact_summary": "Analysis pending.",
    }


def load_trace_bug_data(symptom: str, graph: "KnowledgeGraph" | None = None) -> dict[str, str]:
    """
    Load data for the trace-bug prompt.
    
    Args:
        symptom: Bug symptom description
        graph: Knowledge graph (optional)
        
    Returns:
        Dictionary of template variables
    """
    if graph is None:
        return {
            "symptom": symptom,
            "trace_paths": "Trace analysis not available (graph not connected).",
            "code_paths": "Code path analysis not available.",
            "investigation_order": "1. Analysis not available\n2. Investigation not available",
            "related_components": "Component analysis not available.",
        }
    
    # TODO: Implement bug tracing logic using graph
    return {
        "symptom": symptom,
        "trace_paths": "Analysis pending implementation.",
        "code_paths": "Analysis pending.",
        "investigation_order": "Analysis pending.",
        "related_components": "Analysis pending.",
    }


def load_review_change_data(planned_changes: str = "", graph: "KnowledgeGraph" | None = None) -> dict[str, str]:
    """
    Load data for the review-change prompt.
    
    Args:
        planned_changes: Description of planned changes
        graph: Knowledge graph (optional)
        
    Returns:
        Dictionary of template variables
    """
    if graph is None:
        return {
            "planned_changes": planned_changes or "No changes specified.",
            "risk_assessment": "Risk assessment not available (graph not connected).",
            "affected_components": "Component analysis not available.",
            "recommended_tests": "Test recommendations not available.",
            "potential_issues": "Issue detection not available.",
            "implementation_order": "Implementation order not available.",
        }
    
    # TODO: Implement change review logic
    return {
        "planned_changes": planned_changes or "No changes specified.",
        "risk_assessment": "Analysis pending implementation.",
        "affected_components": "Analysis pending.",
        "recommended_tests": "Analysis pending.",
        "potential_issues": "Analysis pending.",
        "implementation_order": "Analysis pending.",
    }


def load_refactor_guide_data(target: str, goal: str = "", graph: "KnowledgeGraph" | None = None) -> dict[str, str]:
    """
    Load data for the refactor-guide prompt.
    
    Args:
        target: What to refactor
        goal: Refactoring goal
        graph: Knowledge graph (optional)
        
    Returns:
        Dictionary of template variables
    """
    if graph is None:
        return {
            "target": target,
            "goal": goal or "Improve code quality",
            "current_state": "Current state analysis not available (graph not connected).",
            "target_state": "Target state not analyzed.",
            "refactoring_steps": "1. Analysis pending implementation",
            "files_to_modify": "File analysis pending.",
            "tests_to_update": "Test analysis pending.",
            "risks": "Risk analysis pending.",
        }
    
    # TODO: Implement refactoring guide logic
    return {
        "target": target,
        "goal": goal or "Improve code quality",
        "current_state": "Analysis pending implementation.",
        "target_state": "Analysis pending.",
        "refactoring_steps": "Analysis pending.",
        "files_to_modify": "Analysis pending.",
        "tests_to_update": "Analysis pending.",
        "risks": "Analysis pending.",
    }