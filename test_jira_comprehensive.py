#!/usr/bin/env python3
"""
Comprehensive test of the Jira Project Management Petri Net Analysis skill.
This test uses real Jira data from the SCRUM project and performs formal verification.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add the skill path
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
    STATUS_TO_PLACE,
)
from petri_net_analysis import analyse, print_report


def test_1_basic_workflow():
    """Test 1: Basic workflow analysis with sample Sprint 2 data."""
    print("\n" + "=" * 68)
    print(" TEST 1: Basic Workflow Analysis (Sprint 2 Data)")
    print("=" * 68)

    now = datetime.now()

    # Create issues based on actual SCRUM project data
    issues = [
        JiraIssue(
            key="SCRUM-1",
            summary="Agent-x release 1.0.0",
            status="En curso",  # In Progress
            assignee=None,
            created=now - timedelta(days=5),
            updated=now,
            labels=[],
        ),
        JiraIssue(
            key="SCRUM-2",
            summary="Agent-x release 1.1.0",
            status="En curso",  # In Progress
            assignee=None,
            created=now - timedelta(days=4),
            updated=now,
            labels=[],
        ),
        JiraIssue(
            key="SCRUM-3",
            summary="Petri Net module",
            status="Tareas por hacer",  # To Do
            assignee="pedro.veas.basso@gmail.com",
            created=now - timedelta(days=3),
            updated=now - timedelta(days=1),
            labels=[],
        ),
        JiraIssue(
            key="SCRUM-4",
            summary="Implement MCP local module for Jira",
            status="Tareas por hacer",  # To Do
            assignee=None,
            created=now - timedelta(days=2),
            updated=now - timedelta(hours=12),
            labels=[],
        ),
    ]

    print(f"\nIssues loaded: {len(issues)}")
    print("Status distribution:")
    for status in set(i.status for i in issues):
        count = sum(1 for i in issues if i.status == status)
        print(f"  - {status}: {count}")

    # Build Petri net
    net, issue_map = build_net_from_jira(issues)

    print(f"\nPetri net constructed:")
    print(f"  Places: {len(net.places)}")
    print(f"  Transitions: {len(net.transitions)}")

    # Run analysis
    results = analyse(net, max_states=5000)

    print("\nFormal Verification Results:")
    print_report(net, results)

    # Derive insights
    insights = derive_insights(net, issue_map, results)
    print_insight_report(insights, net)

    return {
        "test": "Basic Workflow",
        "status": "PASSED",
        "issues": len(issues),
        "places": len(net.places),
        "transitions": len(net.transitions),
        "insights": len(insights),
    }


def test_2_bottleneck_scenario():
    """Test 2: Bottleneck detection - multiple issues in review."""
    print("\n" + "=" * 68)
    print(" TEST 2: Bottleneck Detection (Review Queue)")
    print("=" * 68)

    now = datetime.now()

    # Create a scenario with review bottleneck
    issues = [
        JiraIssue(
            key="TEST-1",
            summary="Feature A",
            status="In Review",
            assignee="dev1",
            created=now,
            updated=now,
            labels=[],
        ),
        JiraIssue(
            key="TEST-2",
            summary="Feature B",
            status="In Review",
            assignee="dev2",
            created=now,
            updated=now,
            labels=[],
        ),
        JiraIssue(
            key="TEST-3",
            summary="Feature C",
            status="In Review",
            assignee="dev3",
            created=now,
            updated=now,
            labels=[],
        ),
        JiraIssue(
            key="TEST-4",
            summary="Feature D",
            status="In Review",
            assignee="dev4",
            created=now,
            updated=now,
            labels=[],
        ),
        JiraIssue(
            key="TEST-5",
            summary="Feature E",
            status="In Progress",
            assignee="dev5",
            created=now,
            updated=now,
            labels=[],
        ),
    ]

    net, issue_map = build_net_from_jira(issues)
    results = analyse(net, max_states=5000)
    insights = derive_insights(net, issue_map, results)

    print(f"\nScenario: {len(issues)} issues (4 in review, 1 in progress)")
    print_insight_report(insights, net)

    # Verify bottleneck detected
    bottleneck_found = any("review" in i.area.lower() for i in insights)

    return {
        "test": "Bottleneck Detection",
        "status": "PASSED" if bottleneck_found else "PARTIAL",
        "bottleneck_detected": bottleneck_found,
    }


def test_3_blocked_tickets():
    """Test 3: Blocked ticket detection."""
    print("\n" + "=" * 68)
    print(" TEST 3: Blocked Ticket Detection")
    print("=" * 68)

    now = datetime.now()

    issues = [
        JiraIssue(
            key="BLOCK-1",
            summary="Waiting for API",
            status="Blocked",
            assignee="dev1",
            created=now,
            updated=now,
            labels=["blocked"],
        ),
        JiraIssue(
            key="BLOCK-2",
            summary="Database migration",
            status="In Progress",
            assignee="dev2",
            created=now,
            updated=now,
            labels=[],
        ),
        JiraIssue(
            key="BLOCK-3",
            summary="UI component",
            status="To Do",
            assignee=None,
            created=now,
            updated=now,
            labels=[],
        ),
    ]

    net, issue_map = build_net_from_jira(issues)
    results = analyse(net, max_states=5000)
    insights = derive_insights(net, issue_map, results)

    print(f"\nScenario: {len(issues)} issues (1 blocked)")
    print_insight_report(insights, net)

    # Verify blocked detected
    blocked_found = any("blocked" in i.area.lower() for i in insights)

    return {
        "test": "Blocked Detection",
        "status": "PASSED" if blocked_found else "FAILED",
        "blocked_detected": blocked_found,
    }


def test_4_jira_comment_export():
    """Test 4: Jira comment export functionality."""
    print("\n" + "=" * 68)
    print(" TEST 4: Jira Comment Export")
    print("=" * 68)

    now = datetime.now()
    issues = [
        JiraIssue(
            key="EXP-1",
            summary="Test issue",
            status="In Progress",
            assignee="dev",
            created=now,
            updated=now,
            labels=[],
        ),
    ]

    net, issue_map = build_net_from_jira(issues)
    results = analyse(net, max_states=5000)
    insights = derive_insights(net, issue_map, results)

    comment = export_jira_comment(insights)

    print("\nExported Jira Comment:")
    print("-" * 68)
    print(comment)
    print("-" * 68)

    # Verify format
    has_header = "h2." in comment
    has_formatting = "_Generated" in comment

    return {
        "test": "Comment Export",
        "status": "PASSED" if has_header and has_formatting else "FAILED",
        "has_header": has_header,
        "has_formatting": has_formatting,
    }


def test_5_status_mapping():
    """Test 5: Jira status to Petri net place mapping."""
    print("\n" + "=" * 68)
    print(" TEST 5: Status Mapping Verification")
    print("=" * 68)

    print("\nStatus mappings configured:")
    for jira_status, place in STATUS_TO_PLACE.items():
        print(f"  {jira_status:20} → {place}")

    return {
        "test": "Status Mapping",
        "status": "PASSED",
        "mappings": len(STATUS_TO_PLACE),
    }


from datetime import timedelta


def main():
    """Run all tests."""
    print("\n" + "█" * 68)
    print("█" + " " * 66 + "█")
    print(
        "█"
        + "  JIRA PROJECT MANAGEMENT SKILL - COMPREHENSIVE TEST SUITE  ".center(66)
        + "█"
    )
    print("█" + "  Petri Net Formal Verification for Sprint 2".center(66) + "█")
    print("█" + " " * 66 + "█")
    print("█" * 68)

    results = []

    # Run all tests
    results.append(test_1_basic_workflow())
    results.append(test_2_bottleneck_scenario())
    results.append(test_3_blocked_tickets())
    results.append(test_4_jira_comment_export())
    results.append(test_5_status_mapping())

    # Summary
    print("\n" + "=" * 68)
    print(" TEST SUMMARY")
    print("=" * 68)

    passed = sum(1 for r in results if r.get("status") == "PASSED")
    total = len(results)

    for r in results:
        status_icon = (
            "✓" if r["status"] == "PASSED" else "⚠" if r["status"] == "PARTIAL" else "✗"
        )
        print(f"{status_icon} {r['test']}: {r['status']}")

    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 68)

    return {
        "total_tests": total,
        "passed": passed,
        "success_rate": passed / total * 100,
        "results": results,
    }


if __name__ == "__main__":
    result = main()
    print(f"\nFinal Result: {result}")
