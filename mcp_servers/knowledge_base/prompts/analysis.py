#!/usr/bin/env python3
"""
Analysis Prompts for KB MCP v4.

Helps agents analyze changes and generate tests.
"""

SUMMARIZE_CHANGES_TEMPLATE = """# Code Change Summary

## From {{ from_ref }} to {{ to_ref }}

## Added Entities

{{ added_entities }}

## Removed Entities

{{ removed_entities }}

## Modified Entities

{{ modified_entities }}

## Impact Analysis

{{ impact_analysis }}

## Migration Notes

{{ migration_notes }}
"""

WRITE_TEST_TEMPLATE = """# Test Generation Plan

## Module: {{ module_path }}

## Module Overview

{{ module_overview }}

## Test Strategy

{{ test_strategy }}

## Test Cases to Generate

{{ test_cases }}

## Mock Requirements

{{ mock_requirements }}

## Suggested Test Structure

{{ test_structure }}
"""


def register_analysis_prompts(registry: "PromptRegistry", graph: "KnowledgeGraph" | None = None) -> None:
    """
    Register analysis-related prompts.
    
    Args:
        registry: Prompt registry to register with
        graph: Optional knowledge graph for data loading
    """
    from .registry import PromptArgument
    
    # summarize-changes prompt
    registry.register(
        name="summarize-changes",
        description="Summarize what changed between refs.",
        template=SUMMARIZE_CHANGES_TEMPLATE,
        arguments=[
            PromptArgument(
                name="from_ref",
                description="Starting git reference",
                required=True,
            ),
            PromptArgument(
                name="to_ref",
                description="Ending git reference",
                required=True,
            ),
        ],
        category="analysis",
    )
    
    # write-test prompt
    registry.register(
        name="write-test",
        description="Generate tests for module X.",
        template=WRITE_TEST_TEMPLATE,
        arguments=[
            PromptArgument(
                name="module_path",
                description="Path to module to test",
                required=True,
            ),
        ],
        category="analysis",
    )


def load_summarize_changes_data(from_ref: str, to_ref: str, graph: "KnowledgeGraph" | None = None) -> dict[str, str]:
    """
    Load data for the summarize-changes prompt.
    
    Args:
        from_ref: Starting git reference
        to_ref: Ending git reference
        graph: Knowledge graph (optional)
        
    Returns:
        Dictionary of template variables
    """
    if graph is None:
        return {
            "from_ref": from_ref,
            "to_ref": to_ref,
            "added_entities": "Change analysis not available (graph not connected).",
            "removed_entities": "Change analysis not available.",
            "modified_entities": "Change analysis not available.",
            "impact_analysis": "Impact analysis not available.",
            "migration_notes": "Migration notes not available.",
        }
    
    # TODO: Implement git diff analysis using graph
    return {
        "from_ref": from_ref,
        "to_ref": to_ref,
        "added_entities": "Analysis pending implementation.",
        "removed_entities": "Analysis pending.",
        "modified_entities": "Analysis pending.",
        "impact_analysis": "Analysis pending.",
        "migration_notes": "Analysis pending.",
    }


def load_write_test_data(module_path: str, graph: "KnowledgeGraph" | None = None) -> dict[str, str]:
    """
    Load data for the write-test prompt.
    
    Args:
        module_path: Path to module to test
        graph: Knowledge graph (optional)
        
    Returns:
        Dictionary of template variables
    """
    if graph is None:
        return {
            "module_path": module_path,
            "module_overview": "Module analysis not available (graph not connected).",
            "test_strategy": "Test strategy not available.",
            "test_cases": "Test case generation not available.",
            "mock_requirements": "Mock analysis not available.",
            "test_structure": "Test structure not available.",
        }
    
    # TODO: Implement test generation logic using graph
    return {
        "module_path": module_path,
        "module_overview": "Analysis pending implementation.",
        "test_strategy": "Analysis pending.",
        "test_cases": "Analysis pending.",
        "mock_requirements": "Analysis pending.",
        "test_structure": "Analysis pending.",
    }