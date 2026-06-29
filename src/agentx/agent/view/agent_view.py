"""Console AgentView — implements :class:`IAgentViewPartner` for terminal output.

A simple, dependency-free view used by tests and non-TUI runs.  The TUI screen
(``view/tui/agent_screen.py``) provides the rich Textual experience.
"""

from __future__ import annotations

from typing import Any

from agentx.agent.interfaces import IAgentViewPartner
from agentx.agent.types import MemoryQuery, PolicyRule, ReflectionEntry


class AgentView(IAgentViewPartner):
    """Console-based agent view."""

    def show_status(self, status: Any) -> None:
        if isinstance(status, dict):
            print(f"  [Agent] {status.get('name', '?')} ({status.get('id', '?')})")
            print(f"    state:    {status.get('state', '?')}")
            print(f"    autonomy: {status.get('autonomy', '?')}")
            print(f"    goals:    {status.get('goals', 0)}")
            print(f"    rules:    {status.get('rules', 0)}")
            print(f"    tools:    {status.get('tools', 0)}")
        else:
            print(f"  [Agent] {status}")

    def show_reflection_log(self, entries: list[ReflectionEntry]) -> None:
        for entry in entries:
            print(f"  [Reflection] {entry.id}")
            print(f"    summary:  {entry.critique.summary}")
            print(f"    confidence: {entry.critique.confidence:.2f}")
            if entry.critique.strengths:
                print(f"    strengths: {entry.critique.strengths}")
            if entry.critique.weaknesses:
                print(f"    weaknesses: {entry.critique.weaknesses}")
            for p in entry.proposals:
                print(f"    proposal: {p.type.value} [{p.status.value}] — {p.rationale}")

    def show_memory_view(self, query: MemoryQuery) -> None:
        print(f"  [Memory] query: text={query.text!r} limit={query.limit}")

    def show_policy_editor(self, rules: list[PolicyRule]) -> None:
        print(f"  [Policy] {len(rules)} rule(s):")
        for rule in rules:
            print(
                f"    {rule.id}  pri={rule.priority}  "
                f"enabled={rule.enabled}  cond={rule.condition_expr!r}"
            )

    def refresh_goal_tree(self) -> None:
        print("  [Goals] tree refreshed")

    def show_message(self, message: str) -> None:
        print(f"  [Agent] {message}")
