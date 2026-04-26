---
name: mcp-issue-tracker-analysis
description: >
  A skill for analyzing MCP-compatible issue tracker workflows using Petri net formal verification.
  This skill analyzes issue tracker workflows via MCP, builds a Petri net model, 
  analyzes behavioral and structural properties (boundedness, liveness, deadlock-freedom, 
  reversibility, etc.), and generates actionable process improvement insights.
version: 0.1.0
author: agentx
dependencies:
  - petri_net_project_analizer/petri_net.py
  - petri_net_project_analizer/petri_net_analysis.py
  - petri_net_project_analizer/mcp_issue_tracker_workflow.py
tools:
  - search_issues (via MCP)
  - get_issue (via MCP)
  - add_comment (via MCP)
entry_point: mcp_issue_tracker_workflow.py
usage:
  description: |
    This skill provides Petri net-based analysis of MCP-compatible issue tracker workflows.
    It works with any issue tracker that provides MCP-compatible endpoints.
   
  example: |
    To use this skill, the opencode agent should:
    
    1. Fetch issues from issue tracker using MCP tool:
       - Call `search_issues` with query like "project:MYPROJ AND status in (To Do, In Progress)"
       - Or use `get_issue` for specific issues
       
    2. Build Petri net from issues:
       from mcp_issue_tracker_workflow import build_net_from_issues, Issue
       issues = [Issue(...)]  # Convert MCP results
       net, issue_map = build_net_from_issues(issues)
       
    3. Run analysis:
       from petri_net_analysis import analyse
       results = analyse(net, max_states=5000)
       
    4. Get insights:
       from issue_tracker_petri_workflow import derive_insights, print_insight_report
       insights = derive_insights(net, issue_map, results)
       print_insight_report(insights, net)
       
    5. Optionally post to issue tracker:
       comment = export_issue_tracker_comment(insights)
       # Call add_comment via MCP

capabilities:
  - Formal verification of issue tracker workflows using Petri nets
  - Detection of bottlenecks and WIP accumulation
  - Identification of blocked tickets and dependencies
  - Analysis of sprint throughput and process irreversibility
  - Generation of actionable process improvement recommendations
  - Integration with any MCP-compatible issue tracker

properties_analyzed:
  - Boundedness: Whether ticket counts stay finite
  - Safeness: Whether any state can have multiple tickets
  - Deadlock-freedom: Whether the process can get stuck
  - Liveness: Whether all workflow transitions can fire
  - Reversibility: Whether the process can return to initial state
  - Siphons & Traps: Structural bottleneck predictors

notes:
  - Works with any MCP-compatible issue tracker (not limited to issue tracker system)
  - No mock data - requires active MCP connection
  - Analysis is exponential in worst case; max_states limits exploration
  - Results ranked by severity: CRITICAL, WARNING, INFO
---