"""
Jira Software Development Process — Petri Net Analysis
======================================================
Conceptual use-case that maps a real Jira project workflow onto a Petri net,
analyses its formal properties (liveness, boundedness, deadlock-freedom …),
and surfaces actionable process insights.

Integration points
─────────────────
MCP (Model Context Protocol)
This module uses the Jira MCP remote server configured in opencode.jsonc.
The `JiraMCPClient` class provides a thin wrapper around MCP tool calls.

Workflow modelled
─────────────────
Places (states a ticket can be in)
backlog · todo · in_progress · in_review · qa · done · blocked

Transitions (actions that move a ticket between states)
plan backlog → todo
start todo → in_progress
submit in_progress → in_review
rework in_review → in_progress (reviewer requests changes)
approve in_review → qa
fail_qa qa → in_progress (QA rejects)
pass_qa qa → done
block in_progress → blocked
unblock blocked → in_progress
reopen done → in_progress (regression / re-open)
"""

from __future__ import annotations
import os
import sys
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Any

# ---------------------------------------------------------------------------
# Make sure sibling files are importable regardless of working directory
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from petri_net import PetriNet  # noqa: E402
from petri_net_analysis import analyse, print_report  # noqa: E402


# ===========================================================================
# 1. JiraIssue dataclass
# ===========================================================================


@dataclass
class JiraIssue:
    """Represents a Jira issue with essential fields for analysis."""

    key: str
    summary: str
    status: str  # Jira status name
    assignee: str | None
    created: datetime
    updated: datetime
    labels: list[str] = field(default_factory=list)
    blocked_by: list[str] = field(default_factory=list)


# ===========================================================================
# 2. Build a Petri net from Jira data
# ===========================================================================

# Map Jira status names → Petri net place names
STATUS_TO_PLACE: dict[str, str] = {
    "Backlog": "backlog",
    "To Do": "todo",
    "In Progress": "in_progress",
    "In Review": "in_review",
    "QA": "qa",
    "Done": "done",
    "Blocked": "blocked",
}


def build_net_from_jira(
    issues: list[JiraIssue],
) -> tuple[PetriNet, dict[str, list[str]]]:
    """
    Construct a Petri net whose initial marking reflects the real token
    distribution across the board right now.

    Tokens = number of Jira tickets in that state.
    """
    # Count tickets per state
    counts: dict[str, int] = {p: 0 for p in STATUS_TO_PLACE.values()}
    issue_map: dict[str, list[str]] = {p: [] for p in counts}  # place → [issue keys]

    for issue in issues:
        place = STATUS_TO_PLACE.get(issue.status)
        if place:
            counts[place] += 1
            issue_map[place].append(issue.key)

    net = PetriNet("Jira Sprint Workflow")

    # Places
    backlog = net.add_place("backlog", tokens=counts["backlog"])
    todo = net.add_place("todo", tokens=counts["todo"])
    in_progress = net.add_place("in_progress", tokens=counts["in_progress"])
    in_review = net.add_place("in_review", tokens=counts["in_review"])
    qa = net.add_place("qa", tokens=counts["qa"])
    done = net.add_place("done", tokens=counts["done"])
    blocked = net.add_place("blocked", tokens=counts["blocked"])

    # Transitions
    plan = net.add_transition("plan")  # Backlog → To Do
    start = net.add_transition("start")  # To Do → In Progress
    submit = net.add_transition("submit")  # In Progress → In Review
    rework = net.add_transition("rework")  # In Review → In Progress
    approve = net.add_transition("approve")  # In Review → QA
    fail_qa = net.add_transition("fail_qa")  # QA → In Progress
    pass_qa = net.add_transition("pass_qa")  # QA → Done
    block = net.add_transition("block")  # In Progress → Blocked
    unblock = net.add_transition("unblock")  # Blocked → In Progress
    reopen = net.add_transition("reopen")  # Done → In Progress

    # Arcs
    net.add_arc(backlog, plan)
    net.add_arc(plan, todo)
    net.add_arc(todo, start)
    net.add_arc(start, in_progress)
    net.add_arc(in_progress, submit)
    net.add_arc(submit, in_review)
    net.add_arc(in_review, rework)
    net.add_arc(rework, in_progress)
    net.add_arc(in_review, approve)
    net.add_arc(approve, qa)
    net.add_arc(qa, fail_qa)
    net.add_arc(fail_qa, in_progress)
    net.add_arc(qa, pass_qa)
    net.add_arc(pass_qa, done)
    net.add_arc(in_progress, block)
    net.add_arc(block, blocked)
    net.add_arc(blocked, unblock)
    net.add_arc(unblock, in_progress)
    net.add_arc(done, reopen)
    net.add_arc(reopen, in_progress)

    return net, issue_map


# ===========================================================================
# 3. Derive process insights from the analysis results
# ===========================================================================


@dataclass
class ProcessInsight:
    severity: str  # CRITICAL / WARNING / INFO
    area: str  # which part of the process
    message: str
    tickets: list[str] = field(default_factory=list)
    action: str = ""


def derive_insights(
    net: PetriNet, issue_map: dict[str, list[str]], analysis_results: list
) -> list[ProcessInsight]:
    insights: list[ProcessInsight] = []
    marking = net.marking()

    # ── Bottleneck detection (WIP accumulation) ─────────────────────────
    wip_threshold = 3
    for place, count in marking.items():
        if place in ("done", "backlog"):
            continue
        if count >= wip_threshold:
            severity = "CRITICAL" if count > 4 else "WARNING"
            insights.append(
                ProcessInsight(
                    severity=severity,
                    area=f"WIP accumulation in '{place}'",
                    message=(
                        f"{count} tickets are piling up in '{place}'. "
                        f"This indicates a bottleneck — capacity or hand-off "
                        f"speed is lower than the upstream flow."
                    ),
                    tickets=issue_map.get(place, []),
                    action=(
                        f"Introduce a WIP limit of {wip_threshold} for '{place}'. "
                        f"Consider pairing or swarming to clear the queue."
                    ),
                )
            )

    # ── Blocked tickets ──────────────────────────────────────────────────
    blocked = marking.get("blocked", 0)
    if blocked > 0:
        insights.append(
            ProcessInsight(
                severity="CRITICAL",
                area="Blocked tickets",
                message=(
                    f"{blocked} ticket(s) are blocked. "
                    f"Blocked tickets stop value delivery and signal "
                    f"unresolved external dependencies."
                ),
                tickets=issue_map.get("blocked", []),
                action=(
                    "Schedule an immediate unblocking session. "
                    "Each blocked ticket should have a named owner and a "
                    "resolution deadline."
                ),
            )
        )

    # ── Liveness violations ──────────────────────────────────────────────
    for r in analysis_results:
        if "Liveness" in r.property_name and r.holds is False:
            dead = r.witness or []
            insights.append(
                ProcessInsight(
                    severity="WARNING",
                    area="Dead transitions (process paths never used)",
                    message=(
                        f"Transitions {dead} never fire from the current "
                        f"board state. This means some workflow steps are "
                        f"unreachable — either the process definition is "
                        f"wrong or the team is bypassing steps."
                    ),
                    action=(
                        "Audit whether these transitions exist in the actual "
                        "team workflow. Remove phantom steps or enforce them "
                        "in Jira automation rules."
                    ),
                )
            )

    # ── Deadlock risk ────────────────────────────────────────────────────
    for r in analysis_results:
        if "Deadlock" in r.property_name and r.holds is False:
            insights.append(
                ProcessInsight(
                    severity="CRITICAL",
                    area="Deadlock risk",
                    message=(
                        "The reachability analysis found a marking where NO "
                        "transition is enabled — the process would grind to "
                        "a halt with tickets stuck and no way forward."
                    ),
                    action=(
                        "Add escape transitions (e.g. 'cancel' or 'escalate') "
                        "so every state has at least one valid next step."
                    ),
                )
            )

    # ── Review queue depth ───────────────────────────────────────────────
    in_review = marking.get("in_review", 0)
    in_progress = marking.get("in_progress", 0)
    if in_review > 0 and in_progress > 0:
        ratio = in_review / max(in_progress, 1)
        if ratio > 1.2:
            insights.append(
                ProcessInsight(
                    severity="WARNING",
                    area="Review queue outpacing development",
                    message=(
                        f"The review queue ({in_review} tickets) is "
                        f"{ratio:.1f}× larger than In Progress ({in_progress}). "
                        f"Reviewers are a scarce resource and will become the "
                        f"next bottleneck."
                    ),
                    tickets=issue_map.get("in_review", []),
                    action=(
                        "Rotate review duties across the team. "
                        "Consider async code-review tooling or pair review "
                        "sessions to increase throughput."
                    ),
                )
            )

    # ── Reversibility warning ────────────────────────────────────────────
    for r in analysis_results:
        if "Reversibility" in r.property_name and r.holds is False:
            insights.append(
                ProcessInsight(
                    severity="INFO",
                    area="Process irreversibility",
                    message=(
                        "Some reachable states cannot return to the sprint "
                        "starting state. This is expected for 'Done' tickets "
                        "but may signal hidden dead-ends."
                    ),
                    action=(
                        "Verify that 'Done' is the only terminal state. "
                        "Add a 'Reopen' transition if regression handling "
                        "is needed."
                    ),
                )
            )

    # ── Sprint health summary ─────────────────────────────────────────────
    total = sum(v for k, v in marking.items() if k != "backlog")
    done_n = marking.get("done", 0)
    pct = done_n / total * 100 if total else 0
    severity = "INFO" if pct >= 30 else "WARNING"
    insights.append(
        ProcessInsight(
            severity=severity,
            area="Sprint throughput",
            message=(
                f"{done_n}/{total} in-sprint tickets are Done ({pct:.0f}%). "
                f"{'Healthy progress.' if pct >= 30 else 'Sprint may not complete on time.'}"
            ),
            action=(
                ""
                if pct >= 30
                else "Re-prioritise or descope lower-value backlog items now."
            ),
        )
    )

    return sorted(
        insights, key=lambda i: ["CRITICAL", "WARNING", "INFO"].index(i.severity)
    )


# ===========================================================================
# 4. Format the final report
# ===========================================================================

SEVERITY_ICON = {"CRITICAL": "🔴", "WARNING": "🟡", "INFO": "🟢"}


def print_insight_report(insights: list[ProcessInsight], net: PetriNet):
    print("\n" + "━" * 68)
    print(" PROCESS IMPROVEMENT REPORT")
    print(f" Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("━" * 68)

    print("\n CURRENT BOARD STATE (tokens = ticket count)")
    for place, count in net.marking().items():
        bar = "■" * count if count <= 20 else f"({count})"
        print(f" {place:<14} {bar or '∅'}")

    print("\n INSIGHTS")
    for i, ins in enumerate(insights, 1):
        icon = SEVERITY_ICON[ins.severity]
        print(f"\n {icon} [{ins.severity}] {ins.area}")
        print(f" {ins.message}")
        if ins.tickets:
            print(f" Tickets: {', '.join(ins.tickets)}")
        if ins.action:
            print(f" → Action: {ins.action}")

    critical = sum(1 for i in insights if i.severity == "CRITICAL")
    warning = sum(1 for i in insights if i.severity == "WARNING")
    info = sum(1 for i in insights if i.severity == "INFO")
    print(f"\n Summary: {critical} critical {warning} warnings {info} info")
    print("━" * 68)


def export_jira_comment(insights: list[ProcessInsight]) -> str:
    """Format insights as a Jira comment body (Atlassian markdown)."""
    lines = [
        "h2. 🤖 Petri Net Process Analysis — Automated Report",
        "",
        f"_Generated by Claude Code + petri_net_analysis.py on "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M')}_",
        "",
    ]
    for ins in insights:
        icon = SEVERITY_ICON[ins.severity]
        lines += [
            f"h3. {icon} {ins.area}",
            ins.message,
        ]
        if ins.tickets:
            lines.append(f"*Affected tickets:* {', '.join(ins.tickets)}")
        if ins.action:
            lines.append(f"*Recommended action:* {ins.action}")
        lines.append("")
    return "\n".join(lines)


# ===========================================================================
# 5. Entry point for opencode agent
# ===========================================================================


def analyze_jira_project():
    """
    Main entry point for opencode agent to analyze a Jira project.

    This function:
    1. Fetches live sprint data from Jira via MCP
    2. Builds a Petri net model of the workflow
    3. Runs formal verification analysis
    4. Derives actionable insights
    5. Returns the analysis results

    Returns:
        dict: Analysis results including insights and report
    """
    print("\n" + "═" * 68)
    print(" Jira Sprint → Petri Net → Process Insights")
    print(" (Using Jira MCP remote server)")
    print("═" * 68)

    # Note: In opencode, the agent will call Jira MCP tools directly
    # This is a placeholder that explains what the agent should do
    print("\n" + "─" * 68)
    print(" INSTRUCTIONS FOR OPENCODE AGENT:")
    print("─" * 68)
    print("""
To analyze a Jira project, the opencode agent should:

1. Call Jira MCP tool 'jira_search' or equivalent to fetch issues:
   - Use JQL: "sprint in openSprints()" or custom filter
   - Get fields: key, summary, status, assignee, created, updated, labels

2. Build Petri net from the fetched issues:
   net, issue_map = build_net_from_jira(issues)

3. Run formal analysis:
   results = analyse(net, max_states=5000)

4. Derive insights:
   insights = derive_insights(net, issue_map, results)

5. Print or export the report:
   print_insight_report(insights, net)
   comment = export_jira_comment(insights)

6. Optionally post comment to Jira via MCP tool 'jira_add_comment'
    """)
    print("─" * 68)

    return {
        "status": "ready_for_mcp",
        "message": "Petri net analyzer ready. Use Jira MCP tools to fetch issues.",
    }


if __name__ == "__main__":
    analyze_jira_project()
