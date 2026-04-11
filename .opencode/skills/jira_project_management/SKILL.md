---
name: jira-project-management
description: >
  A skill for analyzing Jira project workflows using Petri net formal verification.
  This skill connects to Jira via the remote MCP server (https://mcp.atlassian.com/v1/mcp),
  builds a Petri net model of the workflow, analyzes behavioral and structural properties
  (boundedness, liveness, deadlock-freedom, reversibility, etc.), and generates actionable
  process improvement insights.
version: 0.1.0
author: Agent-X
dependencies:
  - petri_net_project_analizer/petri_net.py
  - petri_net_project_analizer/petri_net_analysis.py
  - petri_net_project_analizer/jira_petri_workflow.py
mcp_servers:
  - jira (remote: https://mcp.atlassian.com/v1/mcp)
tools:
  - jira_search (via MCP)
  - jira_get_issue (via MCP)
  - jira_add_comment (via MCP)
entry_point: jira_petri_workflow.py
usage:
  description: |
    This skill provides Petri net-based analysis of Jira project workflows.
    It uses the Jira MCP remote server configured in opencode.jsonc.
  
  example: |
    To use this skill, the opencode agent should:
    
    1. Fetch issues from Jira using MCP tool:
       - Call `jira_search` with JQL query like "sprint in openSprints()"
       - Or use `jira_get_issue` for specific issues
    
    2. Build Petri net from issues:
       from jira_petri_workflow import build_net_from_jira, JiraIssue
       issues = [JiraIssue(...)]  # Convert MCP results
       net, issue_map = build_net_from_jira(issues)
    
    3. Run analysis:
       from petri_net_analysis import analyse
       results = analyse(net, max_states=5000)
    
    4. Get insights:
       from jira_petri_workflow import derive_insights, print_insight_report
       insights = derive_insights(net, issue_map, results)
       print_insight_report(insights, net)
    
    5. Optionally post to Jira:
       comment = export_jira_comment(insights)
       # Call jira_add_comment via MCP

capabilities:
  - Formal verification of Jira workflows using Petri nets
  - Detection of bottlenecks and WIP accumulation
  - Identification of blocked tickets and dependencies
  - Analysis of sprint throughput and process irreversibility
  - Generation of actionable process improvement recommendations
  - Integration with Jira via MCP remote server

properties_analyzed:
  - Boundedness: Whether ticket counts stay finite
  - Safeness: Whether any state can have multiple tickets
  - Deadlock-freedom: Whether the process can get stuck
  - Liveness: Whether all workflow transitions can fire
  - Reversibility: Whether the process can return to initial state
  - Siphons & Traps: Structural bottleneck predictors

notes:
  - Uses remote Jira MCP server at https://mcp.atlassian.com/v1/mcp
  - No mock data - requires active Jira MCP connection
  - Analysis is exponential in worst case; max_states limits exploration
  - Results ranked by severity: CRITICAL, WARNING, INFO
---
