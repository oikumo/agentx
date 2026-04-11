#!/usr/bin/env python3
"""
Test script for Jira Project Management Petri Net Analysis.
This script simulates the Jira MCP data fetch and runs the Petri net analysis.
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add the petri_net_analyzer to path
skill_path = (
    Path(__file__).parent
    / ".opencode"
    / "skills"
    / "jira_project_management"
    / "petri_net_project_analizer"
)
sys.path.insert(0, str(skill_path))

from jira_petri_workflow import (
    JiraIssue,
    build_net_from_jira,
    derive_insights,
    print_insight_report,
    export_jira_comment,
)
from petri_net_analysis import analyse, print_report


def create_test_jira_issues():
    """Create sample Jira issues mimicking Sprint 2 data."""
    now = datetime.now()

    issues = [
        # In Progress issues (2)
        JiraIssue(
            key="SCRUM-1",
            summary="Agent-x release 1.0.0",
            status="In Progress",
            assignee=None,
            created=now - timedelta(days=5),
            updated=now,
            labels=["release"],
        ),
        JiraIssue(
            key="SCRUM-2",
            summary="Agent-x release 1.1.0",
            status="In Progress",
            assignee="pedro.veas.basso@gmail.com",
            created=now - timedelta(days=4),
            updated=now,
            labels=["release"],
        ),
        # To Do issues (2)
        JiraIssue(
            key="SCRUM-3",
            summary="Petri Net module",
            status="To Do",
            assignee="pedro.veas.basso@gmail.com",
            created=now - timedelta(days=3),
            updated=now - timedelta(days=1),
            labels=["epic", "analysis"],
        ),
        JiraIssue(
            key="SCRUM-4",
            summary="Implement MCP local module for Jira",
            status="To Do",
            assignee=None,
            created=now - timedelta(days=2),
            updated=now - timedelta(hours=12),
            labels=["mcp", "integration"],
        ),
        # In Review (1)
        JiraIssue(
            key="SCRUM-5",
            summary="Add RAG agent functionality",
            status="In Review",
            assignee="developer@example.com",
            created=now - timedelta(days=6),
            updated=now - timedelta(hours=6),
            labels=["rag", "agent"],
        ),
        # QA (1)
        JiraIssue(
            key="SCRUM-6",
            summary="Fix authentication bug",
            status="QA",
            assignee="qa@example.com",
            created=now - timedelta(days=7),
            updated=now - timedelta(hours=2),
            labels=["bug", "security"],
        ),
        # Done (1)
        JiraIssue(
            key="SCRUM-7",
            summary="Setup project structure",
            status="Done",
            assignee="developer@example.com",
            created=now - timedelta(days=10),
            updated=now - timedelta(days=2),
            labels=["setup"],
        ),
        # Blocked (1)
        JiraIssue(
            key="SCRUM-8",
            summary="Wait for API credentials",
            status="Blocked",
            assignee="developer@example.com",
            created=now - timedelta(days=3),
            updated=now - timedelta(hours=1),
            labels=["blocked", "external"],
        ),
    ]

    return issues


def main():
    """Run the Petri net analysis test."""
    print("\n" + "=" * 68)
    print(" JIRA PROJECT MANAGEMENT SKILL - PETRI NET ANALYSIS TEST")
    print(" Sprint 2 Simulation")
    print("=" * 68)

    # Create test issues
    print("\n[1/4] Creating sample Jira issues from Sprint 2...")
    issues = create_test_jira_issues()
    print(f"      Created {len(issues)} issues")

    # Build Petri net
    print("\n[2/4] Building Petri net from Jira workflow...")
    net, issue_map = build_net_from_jira(issues)
    print(f"      Places: {len(net.places)}")
    print(f"      Transitions: {len(net.transitions)}")
    print(
        f"      Total tokens (issues): {sum(net.places[p].tokens for p in net.places)}"
    )

    # Run analysis
    print("\n[3/4] Running formal verification analysis...")
    results = analyse(net, max_states=5000)

    print("\n" + "=" * 68)
    print(" PETRI NET ANALYSIS RESULTS")
    print("=" * 68)
    print_report(net, results)

    # Derive insights
    print("\n[4/4] Deriving process insights...")
    insights = derive_insights(net, issue_map, results)

    # Print insight report
    print_insight_report(insights, net)

    # Export Jira comment
    print("\n" + "=" * 68)
    print(" JIRA COMMENT (for posting to Sprint board)")
    print("=" * 68)
    comment = export_jira_comment(insights)
    print(comment)

    print("\n" + "=" * 68)
    print(" TEST COMPLETED SUCCESSFULLY")
    print("=" * 68)

    return {
        "status": "success",
        "issues_count": len(issues),
        "places_count": len(net.places),
        "transitions_count": len(net.transitions),
        "insights_count": len(insights),
        "critical_issues": sum(1 for i in insights if i.severity == "CRITICAL"),
        "warnings": sum(1 for i in insights if i.severity == "WARNING"),
    }


if __name__ == "__main__":
    result = main()
    print("\nFinal Result:", result)
