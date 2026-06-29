"""AgentTUIScreen — Textual TUI implementing :class:`IAgentViewPartner` (design §10, feature_004 integration).

Provides a rich terminal UI for the agent subsystem: status panel, goal tree,
policy editor, reflection log, and memory viewer.  Registers with the existing
``IUIProvider`` infrastructure so the main screen can navigate to it.
"""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Footer, Header, RichLog, Static, Tree

from agentx.agent.interfaces import IAgentViewPartner
from agentx.agent.types import MemoryQuery, PolicyRule, ReflectionEntry


class AgentTUIScreen(Screen):
    """Textual screen for the agent subsystem."""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "run_cycle", "Run Cycle"),
        Binding("s", "save", "Save"),
        Binding("escape", "app.pop_screen", "Back"),
    ]

    DEFAULT_CSS = """
    AgentTUIScreen {
        layout: vertical;
    }
    #agent-status {
        height: 3;
        background: $boost;
        padding: 0 1;
    }
    #agent-body {
        height: 1fr;
    }
    #agent-log {
        border: solid $primary;
        height: 1fr;
    }
    #agent-tree {
        width: 1fr;
        border: solid $primary;
        padding: 0 1;
    }
    """

    def __init__(self, controller: Any | None = None) -> None:
        super().__init__()
        self._controller = controller

    def set_controller(self, controller: Any) -> None:
        self._controller = controller

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Agent — idle", id="agent-status")
        with Horizontal(id="agent-body"):
            yield Tree("Goals", id="agent-tree")
            yield RichLog(id="agent-log", highlight=False, markup=True)
        yield Footer()

    def on_mount(self) -> None:
        if self._controller:
            self._refresh_status()

    # ----------------------------------------------------------- IAgentViewPartner

    def show_status(self, status: Any) -> None:
        try:
            widget = self.query_one("#agent-status", Static)
            if isinstance(status, dict):
                widget.update(
                    f"Agent: {status.get('name', '?')} | "
                    f"state: {status.get('state', '?')} | "
                    f"goals: {status.get('goals', 0)} | "
                    f"rules: {status.get('rules', 0)}"
                )
        except Exception:
            pass

    def show_reflection_log(self, entries: list[ReflectionEntry]) -> None:
        try:
            log = self.query_one("#agent-log", RichLog)
            for entry in entries:
                log.write(f"[bold]Reflection {entry.id}[/bold]")
                log.write(f"  summary: {entry.critique.summary}")
                log.write(f"  confidence: {entry.critique.confidence:.2f}")
                for p in entry.proposals:
                    log.write(f"  proposal: {p.type.value} [{p.status.value}]")
        except Exception:
            pass

    def show_memory_view(self, query: MemoryQuery) -> None:
        try:
            log = self.query_one("#agent-log", RichLog)
            log.write(f"[Memory] query: text={query.text!r} limit={query.limit}")
        except Exception:
            pass

    def show_policy_editor(self, rules: list[PolicyRule]) -> None:
        try:
            log = self.query_one("#agent-log", RichLog)
            log.write(f"[Policy] {len(rules)} rule(s)")
            for rule in rules:
                log.write(f"  {rule.id}  pri={rule.priority}  enabled={rule.enabled}")
        except Exception:
            pass

    def refresh_goal_tree(self) -> None:
        if self._controller is None:
            return
        try:
            tree = self.query_one("#agent-tree", Tree)
            tree.clear()
            agent = self._controller.get_agent()
            goal_tree = agent.goal_manager.get_tree()
            if goal_tree.root and goal_tree.root in goal_tree.nodes:
                root_goal = goal_tree.nodes[goal_tree.root]
                branch = tree.root.add(root_goal.description, expand=True)
                self._populate_children(branch, goal_tree, root_goal.id)
        except Exception:
            pass

    def _populate_children(self, branch: Any, goal_tree: Any, parent_id: str) -> None:
        goal = goal_tree.get(parent_id)
        if goal is None:
            return
        for child_id in goal.children:
            child = goal_tree.get(child_id)
            if child:
                sub = branch.add(child.description, expand=True)
                self._populate_children(sub, goal_tree, child_id)

    def show_message(self, message: str) -> None:
        try:
            log = self.query_one("#agent-log", RichLog)
            log.write(message)
        except Exception:
            pass

    # ----------------------------------------------------------- actions

    def action_run_cycle(self) -> None:
        if self._controller:
            self._controller.run_cycle()

    def action_save(self) -> None:
        if self._controller:
            snapshot_id = self._controller.get_agent().persist()
            self.show_message(f"Snapshot saved: {snapshot_id}")

    def _refresh_status(self) -> None:
        if self._controller:
            self.show_status(self._controller.get_agent().get_status())
            self.refresh_goal_tree()


# Register as a virtual subclass of IAgentViewPartner (avoids metaclass conflict
# between Textual's _MessagePumpMeta and abc.ABCMeta).
IAgentViewPartner.register(AgentTUIScreen)
