#!/usr/bin/env python3
"""
Petri Net Analysis for Agent-X Sprint 2 (SCRUM Project)

This script demonstrates the power of Petri Net formal verification
applied to a real Jira sprint with 57 tickets across multiple epics.

Author: Agent-X System
Date: April 11, 2026
"""

import sys
from pathlib import Path

SKILL_PATH = (
    Path(__file__).parent.parent
    / ".opencode"
    / "skills"
    / "jira_project_management"
    / "petri_net_project_analizer"
)
sys.path.insert(0, str(SKILL_PATH))

from petri_net import PetriNet
from petri_net_analysis import (
    check_boundedness,
    check_safeness,
    check_liveness,
    check_deadlock_freedom,
    check_reversibility,
)
from jira_petri_workflow import (
    build_net_from_jira,
    derive_insights,
    print_insight_report,
    JiraIssue,
)

JIRA_DATA_RAW = {
    "SCRUM-1": {
        "summary": "Agent-x release 1.0.0",
        "status": "En curso",
        "type": "Tarea",
    },
    "SCRUM-2": {
        "summary": "Agent-x release 1.1.0",
        "status": "En curso",
        "type": "Tarea",
    },
    "SCRUM-3": {
        "summary": "Petri Net module",
        "status": "Tareas por hacer",
        "type": "Epic",
    },
    "SCRUM-4": {
        "summary": "Implement MCP local module for Jira",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-5": {
        "summary": "Implement LLM factory pattern",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-6": {
        "summary": "Add OpenAI GPT-4o provider",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-7": {
        "summary": "Add Anthropic Claude provider",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-8": {
        "summary": "Add Ollama local LLM provider",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-9": {
        "summary": "Implement rate limiting",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-10": {
        "summary": "Add retry logic",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-11": {
        "summary": "Token usage tracking",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-12": {
        "summary": "LLM response caching",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-13": {
        "summary": "Base agent class",
        "status": "Tareas por hacer",
        "type": "Historia",
    },
    "SCRUM-14": {
        "summary": "Chat agent with tools",
        "status": "Tareas por hacer",
        "type": "Historia",
    },
    "SCRUM-15": {
        "summary": "ReAct agent",
        "status": "Tareas por hacer",
        "type": "Historia",
    },
    "SCRUM-16": {
        "summary": "Graph-based agent",
        "status": "Tareas por hacer",
        "type": "Historia",
    },
    "SCRUM-17": {
        "summary": "Conversation persistence",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-18": {
        "summary": "Agent state management",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-19": {
        "summary": "Agent configuration",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-20": {"summary": "RAG module", "status": "Tareas por hacer", "type": "Epic"},
    "SCRUM-21": {
        "summary": "PDF loader",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-22": {
        "summary": "Markdown loader",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-23": {
        "summary": "Text chunking",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-24": {
        "summary": "ChromaDB integration",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-25": {
        "summary": "FAISS integration",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-26": {
        "summary": "OpenAI embeddings",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-27": {
        "summary": "Local embeddings",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-28": {
        "summary": "Semantic search",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-29": {
        "summary": "RAG pipeline",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-30": {
        "summary": "MCP servers",
        "status": "Tareas por hacer",
        "type": "Epic",
    },
    "SCRUM-31": {
        "summary": "MCP Jira server",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-32": {
        "summary": "MCP Confluence server",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-33": {
        "summary": "MCP filesystem server",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-34": {
        "summary": "MCP GitHub server",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-35": {
        "summary": "MCP tool discovery",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-36": {
        "summary": "MCP resource management",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-37": {
        "summary": "Pytest framework",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-38": {
        "summary": "LLM unit tests",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-39": {
        "summary": "RAG integration tests",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-40": {
        "summary": "Code coverage",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-41": {
        "summary": "Pre-commit hooks",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-42": {
        "summary": "API documentation",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-43": {
        "summary": "Getting started guide",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-44": {
        "summary": "Architecture docs",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-45": {
        "summary": "Docker image",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-46": {
        "summary": "CI/CD pipeline",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-47": {
        "summary": "Structured logging",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-48": {
        "summary": "Configuration management",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-49": {
        "summary": "Interactive CLI",
        "status": "Tareas por hacer",
        "type": "Historia",
    },
    "SCRUM-50": {
        "summary": "REPL syntax highlighting",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-51": {
        "summary": "Command history",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-52": {
        "summary": "Async LLM calls",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-53": {
        "summary": "Connection pooling",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-54": {
        "summary": "Performance profiling",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-55": {
        "summary": "API key encryption",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-56": {
        "summary": "Secrets management",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
    "SCRUM-57": {
        "summary": "Input validation",
        "status": "Tareas por hacer",
        "type": "Tarea",
    },
}


def main():
    print("=" * 80)
    print("PETRI NET FORMAL VERIFICATION - AGENT-X SPRINT 2 ANALYSIS")
    print("=" * 80)
    print()

    print(f"📊 SPRINT STATISTICS")
    print(f"   Total Issues: {len(JIRA_DATA_RAW)}")
    status_counts = {}
    for issue in JIRA_DATA_RAW.values():
        status = issue["status"]
        status_counts[status] = status_counts.get(status, 0) + 1
    for status, count in sorted(status_counts.items()):
        print(f"   - {status}: {count}")
    print()

    print("🔧 BUILDING PETRI NET MODEL FROM JIRA DATA...")
    jira_issues = [
        JiraIssue(
            key=key, summary=data["summary"], status=data["status"], type=data["type"]
        )
        for key, data in JIRA_DATA_RAW.items()
    ]

    net, issue_map = build_net_from_jira(jira_issues)

    print(f"   Places: {len(net.places)}")
    print(f"   Transitions: {len(net.transitions)}")
    print()

    print("🔍 FORMAL VERIFICATION RESULTS")
    print("-" * 80)

    bounded_result = check_boundedness(net)
    print(f"   Boundedness: {bounded_result.is_passed}")

    safe_result = check_safeness(net)
    print(f"   Safeness: {safe_result.is_passed}")

    live_result = check_liveness(net)
    print(f"   Liveness: {live_result.is_passed}")

    deadlock_result = check_deadlock_freedom(net)
    print(f"   Deadlock-Free: {deadlock_result.is_passed}")

    reversible_result = check_reversibility(net)
    print(f"   Reversibility: {reversible_result.is_passed}")
    print()

    print("📈 PROCESS INSIGHTS")
    print("-" * 80)
    insights = derive_insights(jira_issues, net)

    for insight in insights:
        print(f"   • [{insight.severity.upper()}] {insight.description}")
        print(f"     Recommendation: {insight.action}")
    print()

    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
