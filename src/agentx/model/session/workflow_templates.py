"""
Workflow Templates for AgentX Session State Management.

This module provides pre-defined Petri Net workflow templates for common task types:
- Debug workflows
- Analysis workflows
- Implementation workflows
- Documentation workflows

Each template defines a Petri Net structure using the format:
- Nodes: List of states (places)
- Transitions: List of actions that change state
- Edges: State -> [Transition] -> Next State
"""

from typing import Dict, List, Tuple

# Type aliases
WorkflowTemplate = Dict[str, any]
TransitionDef = Tuple[str, List[str], List[str]]  # (name, inputs, outputs)


class WorkflowTemplates:
    """
    Library of workflow templates for different task types.
    
    Each template defines:
    - name: Human-readable name
    - description: What this workflow is for
    - places: List of state names (places in Petri Net)
    - transitions: List of transition definitions
    - initial_place: Where the token starts
    - final_places: Completion states
    """
    
    # ========================================================================
    # DEBUG WORKFLOW
    # ========================================================================
    DEBUG = {
        "name": "Debug Workflow",
        "description": "Systematic debugging process from issue reproduction to fix",
        "places": [
            "issue_pending",
            "issue_reproduced",
            "cause_diagnosed",
            "fix_implemented",
            "fix_verified",
            "issue_resolved"
        ],
        "transitions": [
            ("reproduce", ["issue_pending"], ["issue_reproduced"]),
            ("diagnose", ["issue_reproduced"], ["cause_diagnosed"]),
            ("implement_fix", ["cause_diagnosed"], ["fix_implemented"]),
            ("verify", ["fix_implemented"], ["fix_verified"]),
            ("close", ["fix_verified"], ["issue_resolved"])
        ],
        "initial_place": "issue_pending",
        "final_places": ["issue_resolved"]
    }
    
    # Enhanced debug workflow with retry loop
    DEBUG_WITH_RETRY = {
        "name": "Debug Workflow with Retry",
        "description": "Debugging with ability to retry fix if verification fails",
        "places": [
            "issue_pending",
            "issue_reproduced",
            "cause_diagnosed",
            "fix_implemented",
            "fix_verified",
            "fix_failed",
            "issue_resolved"
        ],
        "transitions": [
            ("reproduce", ["issue_pending"], ["issue_reproduced"]),
            ("diagnose", ["issue_reproduced"], ["cause_diagnosed"]),
            ("implement_fix", ["cause_diagnosed"], ["fix_implemented"]),
            ("verify", ["fix_implemented"], ["fix_verified"]),
            ("fix_accepted", ["fix_verified"], ["issue_resolved"]),
            ("fix_rejected", ["fix_verified"], ["fix_failed"]),
            ("reanalyze", ["fix_failed"], ["cause_diagnosed"])
        ],
        "initial_place": "issue_pending",
        "final_places": ["issue_resolved"]
    }
    
    # ========================================================================
    # ANALYSIS WORKFLOW
    # ========================================================================
    ANALYSIS = {
        "name": "Analysis Workflow",
        "description": "Systematic analysis from context gathering to documentation",
        "places": [
            "analysis_pending",
            "context_gathered",
            "structure_analyzed",
            "findings_documented",
            "analysis_completed"
        ],
        "transitions": [
            ("gather_context", ["analysis_pending"], ["context_gathered"]),
            ("analyze_structure", ["context_gathered"], ["structure_analyzed"]),
            ("document_findings", ["structure_analyzed"], ["findings_documented"]),
            ("complete", ["findings_documented"], ["analysis_completed"])
        ],
        "initial_place": "analysis_pending",
        "final_places": ["analysis_completed"]
    }
    
    # Deep analysis with multiple passes
    ANALYSIS_DEEP = {
        "name": "Deep Analysis Workflow",
        "description": "Comprehensive analysis with multiple review cycles",
        "places": [
            "analysis_pending",
            "context_gathered",
            "initial_analysis_done",
            "reviewed",
            "gaps_identified",
            "deep_analysis_done",
            "findings_documented",
            "analysis_completed"
        ],
        "transitions": [
            ("gather_context", ["analysis_pending"], ["context_gathered"]),
            ("initial_analysis", ["context_gathered"], ["initial_analysis_done"]),
            ("review", ["initial_analysis_done"], ["reviewed"]),
            ("identify_gaps", ["reviewed"], ["gaps_identified"]),
            ("deep_dive", ["gaps_identified"], ["deep_analysis_done"]),
            ("document_findings", ["deep_analysis_done"], ["findings_documented"]),
            ("complete", ["findings_documented"], ["analysis_completed"])
        ],
        "initial_place": "analysis_pending",
        "final_places": ["analysis_completed"]
    }
    
    # ========================================================================
    # IMPLEMENTATION WORKFLOW
    # ========================================================================
    IMPLEMENTATION = {
        "name": "Implementation Workflow",
        "description": "Feature implementation from planning to completion",
        "places": [
            "feature_pending",
            "approach_planned",
            "feature_implemented",
            "feature_tested",
            "feature_completed"
        ],
        "transitions": [
            ("plan", ["feature_pending"], ["approach_planned"]),
            ("implement", ["approach_planned"], ["feature_implemented"]),
            ("test", ["feature_implemented"], ["feature_tested"]),
            ("finalize", ["feature_tested"], ["feature_completed"])
        ],
        "initial_place": "feature_pending",
        "final_places": ["feature_completed"]
    }
    
    # Implementation with refinement loop
    IMPLEMENTATION_WITH_REFACTOR = {
        "name": "Implementation with Refinement",
        "description": "Implementation with code review and refactoring cycle",
        "places": [
            "feature_pending",
            "approach_planned",
            "feature_implemented",
            "feature_tested",
            "feature_reviewed",
            "needs_refinement",
            "feature_refined",
            "feature_completed"
        ],
        "transitions": [
            ("plan", ["feature_pending"], ["approach_planned"]),
            ("implement", ["approach_planned"], ["feature_implemented"]),
            ("test", ["feature_implemented"], ["feature_tested"]),
            ("review", ["feature_tested"], ["feature_reviewed"]),
            ("accept", ["feature_reviewed"], ["feature_completed"]),
            ("request_changes", ["feature_reviewed"], ["needs_refinement"]),
            ("refine", ["needs_refinement"], ["feature_implemented"])
        ],
        "initial_place": "feature_pending",
        "final_places": ["feature_completed"]
    }
    
    # ========================================================================
    # DOCUMENTATION WORKFLOW
    # ========================================================================
    DOCUMENTATION = {
        "name": "Documentation Workflow",
        "description": "Documentation creation from outline to publication",
        "places": [
            "doc_pending",
            "outline_created",
            "draft_written",
            "draft_reviewed",
            "doc_published"
        ],
        "transitions": [
            ("create_outline", ["doc_pending"], ["outline_created"]),
            ("write_draft", ["outline_created"], ["draft_written"]),
            ("review_draft", ["draft_written"], ["draft_reviewed"]),
            ("publish", ["draft_reviewed"], ["doc_published"])
        ],
        "initial_place": "doc_pending",
        "final_places": ["doc_published"]
    }
    
    # ========================================================================
    # REFACTORING WORKFLOW
    # ========================================================================
    REFACTORING = {
        "name": "Refactoring Workflow",
        "description": "Code refactoring from analysis to deployment",
        "places": [
            "refactor_pending",
            "code_analyzed",
            "refactor_plan_ready",
            "tests_ready",
            "refactoring_done",
            "tests_passing",
            "refactor_completed"
        ],
        "transitions": [
            ("analyze_code", ["refactor_pending"], ["code_analyzed"]),
            ("plan_refactor", ["code_analyzed"], ["refactor_plan_ready"]),
            ("prepare_tests", ["refactor_plan_ready"], ["tests_ready"]),
            ("execute_refactor", ["tests_ready"], ["refactoring_done"]),
            ("verify_tests", ["refactoring_done"], ["tests_passing"]),
            ("complete", ["tests_passing"], ["refactor_completed"])
        ],
        "initial_place": "refactor_pending",
        "final_places": ["refactor_completed"]
    }
    
    # ========================================================================
    # RESEARCH WORKFLOW
    # ========================================================================
    RESEARCH = {
        "name": "Research Workflow",
        "description": "Research task from question to conclusion",
        "places": [
            "research_pending",
            "question_defined",
            "sources_gathered",
            "information_analyzed",
            "conclusions_drawn",
            "research_completed"
        ],
        "transitions": [
            ("define_question", ["research_pending"], ["question_defined"]),
            ("gather_sources", ["question_defined"], ["sources_gathered"]),
            ("analyze_info", ["sources_gathered"], ["information_analyzed"]),
            ("draw_conclusions", ["information_analyzed"], ["conclusions_drawn"]),
            ("complete", ["conclusions_drawn"], ["research_completed"])
        ],
        "initial_place": "research_pending",
        "final_places": ["research_completed"]
    }
    
    # ========================================================================
    # PARALLEL WORKFLOW (Multi-Agent)
    # ========================================================================
    PARALLEL_ANALYSIS = {
        "name": "Parallel Analysis Workflow",
        "description": "Parallel analysis branches that merge at completion",
        "places": [
            "task_pending",
            "security_analyzed",
            "performance_analyzed",
            "security_report_ready",
            "performance_report_ready",
            "reports_merged",
            "task_completed"
        ],
        "transitions": [
            ("analyze_security", ["task_pending"], ["security_analyzed"]),
            ("analyze_performance", ["task_pending"], ["performance_analyzed"]),
            ("complete_security", ["security_analyzed"], ["security_report_ready"]),
            ("complete_performance", ["performance_analyzed"], ["performance_report_ready"]),
            ("merge_reports", ["security_report_ready", "performance_report_ready"], ["reports_merged"]),
            ("finalize", ["reports_merged"], ["task_completed"])
        ],
        "initial_place": "task_pending",
        "final_places": ["task_completed"]
    }
    
    # Simple query workflow
    SIMPLE_QUERY = {
        "name": "Simple Query Workflow",
        "description": "Simple single-step query processing",
        "places": [
            "query_pending",
            "query_processing",
            "query_completed"
        ],
        "transitions": [
            ("start", ["query_pending"], ["query_processing"]),
            ("finish", ["query_processing"], ["query_completed"])
        ],
        "initial_place": "query_pending",
        "final_places": ["query_completed"]
    }


# ============================================================================
# Template Selection Logic
# ============================================================================

def get_workflow_for_task(task_type: str) -> WorkflowTemplate:
    """
    Get the appropriate workflow template for a given task type.
    
    Args:
        task_type: Type of task (debug, analysis, implementation, etc.)
        
    Returns:
        WorkflowTemplate dictionary
    """
    task_type_lower = task_type.lower().strip()
    
    # Direct matches
    template_map = {
        "debug": WorkflowTemplates.DEBUG,
        "debugging": WorkflowTemplates.DEBUG,
        "bugfix": WorkflowTemplates.DEBUG,
        "bug": WorkflowTemplates.DEBUG,
        "fix": WorkflowTemplates.DEBUG,
        
        "debug_retry": WorkflowTemplates.DEBUG_WITH_RETRY,
        "debug_with_retry": WorkflowTemplates.DEBUG_WITH_RETRY,
        
        "analysis": WorkflowTemplates.ANALYSIS,
        "analyze": WorkflowTemplates.ANALYSIS,
        "review": WorkflowTemplates.ANALYSIS,
        "examine": WorkflowTemplates.ANALYSIS,
        "investigate": WorkflowTemplates.ANALYSIS,
        
        "deep_analysis": WorkflowTemplates.ANALYSIS_DEEP,
        "deep_analyze": WorkflowTemplates.ANALYSIS_DEEP,
        "comprehensive_analysis": WorkflowTemplates.ANALYSIS_DEEP,
        
        "implementation": WorkflowTemplates.IMPLEMENTATION,
        "implement": WorkflowTemplates.IMPLEMENTATION,
        "feature": WorkflowTemplates.IMPLEMENTATION,
        "develop": WorkflowTemplates.IMPLEMENTATION,
        "build": WorkflowTemplates.IMPLEMENTATION,
        "create": WorkflowTemplates.IMPLEMENTATION,
        
        "implementation_refine": WorkflowTemplates.IMPLEMENTATION_WITH_REFACTOR,
        "implement_with_review": WorkflowTemplates.IMPLEMENTATION_WITH_REFACTOR,
        
        "documentation": WorkflowTemplates.DOCUMENTATION,
        "document": WorkflowTemplates.DOCUMENTATION,
        "doc": WorkflowTemplates.DOCUMENTATION,
        "write_docs": WorkflowTemplates.DOCUMENTATION,
        
        "refactoring": WorkflowTemplates.REFACTORING,
        "refactor": WorkflowTemplates.REFACTORING,
        "optimize": WorkflowTemplates.REFACTORING,
        "restructure": WorkflowTemplates.REFACTORING,
        
        "research": WorkflowTemplates.RESEARCH,
        "study": WorkflowTemplates.RESEARCH,
        "investigate_topic": WorkflowTemplates.RESEARCH,
        
        "parallel": WorkflowTemplates.PARALLEL_ANALYSIS,
        "multi_agent": WorkflowTemplates.PARALLEL_ANALYSIS,
        
        "simple": WorkflowTemplates.SIMPLE_QUERY,
        "query": WorkflowTemplates.SIMPLE_QUERY,
        "question": WorkflowTemplates.SIMPLE_QUERY,
    }
    
    return template_map.get(task_type_lower, WorkflowTemplates.SIMPLE_QUERY)


def get_all_templates() -> Dict[str, WorkflowTemplate]:
    """Get all available workflow templates."""
    return {
        "debug": WorkflowTemplates.DEBUG,
        "debug_with_retry": WorkflowTemplates.DEBUG_WITH_RETRY,
        "analysis": WorkflowTemplates.ANALYSIS,
        "deep_analysis": WorkflowTemplates.ANALYSIS_DEEP,
        "implementation": WorkflowTemplates.IMPLEMENTATION,
        "implementation_with_refinement": WorkflowTemplates.IMPLEMENTATION_WITH_REFACTOR,
        "documentation": WorkflowTemplates.DOCUMENTATION,
        "refactoring": WorkflowTemplates.REFACTORING,
        "research": WorkflowTemplates.RESEARCH,
        "parallel_analysis": WorkflowTemplates.PARALLEL_ANALYSIS,
        "simple_query": WorkflowTemplates.SIMPLE_QUERY
    }


def get_template_names() -> List[str]:
    """Get list of all template names."""
    return list(get_all_templates().keys())
