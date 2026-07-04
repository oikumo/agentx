"""AgentTUIScreen — interactive Textual TUI for the agent subsystem.

Provides a rich terminal UI where the user can:
  - Submit goals            → ``goal <description>``
  - Add policy rules        → ``rule <condition> | <action> <json-params>``
  - Run agent cycles        → ``run`` (or press ``r``)
  - Inspect state           → ``status``, ``goals``, ``rules``, ``memory``
  - Save snapshots          → ``save`` (or press ``s``)
  - Get help                → ``help``

Layout::

    ┌─────────────────────────────────────────────┐
    │  Header                                      │
    ├─────────────────────────────────────────────┤
    │  Status bar (name · state · goals · rules)   │
    ├──────────────────┬──────────────────────────┤
    │  Goal Tree       │  Activity Log             │
    │  (status + prio) │  (cycle results, etc.)    │
    ├──────────────────┴──────────────────────────┤
    │  > command input                             │
    ├─────────────────────────────────────────────┤
    │  Footer (key bindings)                       │
    └─────────────────────────────────────────────┘
"""

from __future__ import annotations

import json
import uuid
from typing import Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Label, RichLog, Static, Tree

from agentx.agent.interfaces import IAgentViewPartner
from agentx.agent.types import (
    ActionType,
    AutonomyLevel,
    MemoryQuery,
    PolicyAction,
    PolicyRule,
    ReflectionEntry,
    RuleMetadata,
    RuleSource,
    SuccessCriteria,
)


class AgentTUIScreen(Screen):
    """Interactive Textual screen for the agent subsystem."""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "run_cycle", "Run Cycle"),
        Binding("s", "save", "Save"),
        Binding("d", "open_demo", "Demo"),
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
        width: 2fr;
    }
    #agent-tree-panel {
        width: 1fr;
        border: solid $primary;
        padding: 0 1;
    }
    #agent-tree {
        height: 1fr;
    }
    #agent-input-panel {
        height: auto;
        padding: 0 1;
        background: $surface;
        border-top: solid $primary;
    }
    #agent-input-panel Label {
        color: $text-muted;
        margin-bottom: 0;
    }
    #agent-input {
        width: 100%;
    }
    """

    def __init__(self, controller: Any | None = None) -> None:
        super().__init__()
        self._controller = controller

    def set_controller(self, controller: Any) -> None:
        self._controller = controller

    # ----------------------------------------------------------- compose

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Agent — idle", id="agent-status")
        with Horizontal(id="agent-body"):
            with Vertical(id="agent-tree-panel"):
                yield Label("🌳 Goals", id="tree-label")
                yield Tree("Goals", id="agent-tree")
            yield RichLog(id="agent-log", highlight=False, markup=True)
        with Vertical(id="agent-input-panel"):
            yield Label("Command (type 'help' for commands):")
            yield Input(
                placeholder="goal <desc> | rule <cond> | <action> <params> | run | status | goals | rules | memory | save | demo [a|b] | proposals | approve <n> | help",
                id="agent-input",
            )
        yield Footer()

    def on_mount(self) -> None:
        self._log("Welcome to the Agent screen.")
        self._log("Type 'help' to see available commands, or press 'r' to run a cycle.")
        if self._controller:
            self._refresh_status()

    # ----------------------------------------------------------- input handling

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Process a user command from the input field."""
        command = event.value.strip()
        if not command:
            return
        event.input.value = ""
        self._log(f"[bold cyan]> {command}[/bold cyan]")
        self._dispatch_command(command)

    def _dispatch_command(self, command: str) -> None:
        """Parse and execute a user command."""
        parts = command.split(None, 1)
        if not parts:
            return
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        if cmd == "help":
            self._cmd_help()
        elif cmd == "goal":
            self._cmd_goal(args)
        elif cmd == "rule":
            self._cmd_rule(args)
        elif cmd in ("run", "cycle"):
            self.action_run_cycle()
        elif cmd == "status":
            self._cmd_status()
        elif cmd == "goals":
            self._cmd_goals()
        elif cmd == "rules":
            self._cmd_rules()
        elif cmd == "memory":
            self._cmd_memory()
        elif cmd == "save":
            self.action_save()
        elif cmd == "demo":  # feature_010: open the demo screen (scenario a|b)
            self._cmd_demo(args)
        elif cmd == "proposals":  # N4: list pending reflection proposals
            self._cmd_proposals()
        elif cmd == "approve":  # N4: approve a pending proposal
            self._cmd_approve(args)
        else:
            self._log(f"[red]Unknown command: {cmd}[/red]. Type 'help' for available commands.")

    # ----------------------------------------------------------- commands

    def _cmd_help(self) -> None:
        self._log("[bold]Available commands:[/bold]")
        self._log("  [cyan]goal <description>[/cyan]      — Submit a new goal")
        self._log("  [cyan]rule <cond> | <act> <json>[/cyan] — Add a policy rule")
        self._log("  [cyan]run[/cyan]                    — Run one agent cycle (also: 'r' key)")
        self._log("  [cyan]status[/cyan]                 — Show agent status")
        self._log("  [cyan]goals[/cyan]                  — List all goals")
        self._log("  [cyan]rules[/cyan]                  — List all policy rules")
        self._log("  [cyan]memory[/cyan]                 — Show recent memory entries")
        self._log("  [cyan]save[/cyan]                   — Save session snapshot (also: 's' key)")
        self._log("  [cyan]demo [a|b][/cyan]             — Open the demo screen (scenario a or b, also: 'd' key)")
        self._log("  [cyan]proposals[/cyan]             — List reflection proposals awaiting approval (N4)")
        self._log("  [cyan]approve <n>[/cyan]           — Approve and apply proposal #<n>")
        self._log("  [cyan]help[/cyan]                   — Show this help")
        self._log("[dim]Key bindings: r=run, s=save, d=demo, q=quit, Esc=back[/dim]")

    def _cmd_goal(self, description: str) -> None:
        if not description:
            self._log("[red]Usage: goal <description>[/red]")
            return
        if not self._controller:
            self._log("[red]No controller connected.[/red]")
            return
        try:
            goal_id = self._controller.submit_goal(
                description,
                success_criteria=SuccessCriteria(kind="tool_success"),
            )
            self._log(f"[green]Goal submitted: {goal_id[:8]}…[/green]")
            self._log(f"  description: {description}")
            self.refresh_goal_tree()
            self._refresh_status()
        except Exception as exc:
            self._log(f"[red]Error submitting goal: {exc}[/red]")

    def _cmd_rule(self, args: str) -> None:
        if not args:
            self._log("[red]Usage: rule <condition> | <action_type> <json-params>[/red]")
            self._log("[dim]Example: rule goal.active | EXECUTE_TOOL {\"tool_id\":\"filesystem\",\"action\":\"read\",\"path\":\"test.txt\"}[/dim]")
            return
        if not self._controller:
            self._log("[red]No controller connected.[/red]")
            return
        # split on '|' — left = condition, right = action_type + params
        if "|" not in args:
            self._log("[red]Missing '|'. Usage: rule <condition> | <action_type> <json-params>[/red]")
            return
        condition_str, action_str = args.split("|", 1)
        condition = condition_str.strip()
        action_parts = action_str.strip().split(None, 1)
        if not action_parts:
            self._log("[red]Missing action type.[/red]")
            return
        action_type_str = action_parts[0].strip().upper()
        params_json = action_parts[1].strip() if len(action_parts) > 1 else "{}"
        try:
            action_type = ActionType(action_type_str)
        except ValueError:
            self._log(f"[red]Unknown action type: {action_type_str}[/red]")
            self._log(f"[dim]Valid types: {', '.join(a.value for a in ActionType)}[/dim]")
            return
        try:
            params = json.loads(params_json) if params_json else {}
        except json.JSONDecodeError as exc:
            self._log(f"[red]Invalid JSON params: {exc}[/red]")
            return
        rule = PolicyRule(
            id=str(uuid.uuid4()),
            condition_expr=condition,
            action=PolicyAction(type=action_type, parameters=params),
            priority=500,
            metadata=RuleMetadata(source=RuleSource.USER_DEFINED, created_by="user"),
        )
        ok = self._controller.update_policy(rule)
        if ok:
            self._log(f"[green]Policy rule added: {rule.id[:8]}…[/green]")
            self._log(f"  condition: {condition}")
            self._log(f"  action: {action_type.value} {params}")
        else:
            self._log("[yellow]Policy rule rejected (conflict or compile error).[/yellow]")
        self._refresh_status()

    def _cmd_status(self) -> None:
        if not self._controller:
            self._log("[red]No controller connected.[/red]")
            return
        status = self._controller.get_status()  # N6: via controller
        self._log(f"[bold]Agent Status[/bold]")
        self._log(f"  id:       {status.get('id', '?')}")
        self._log(f"  name:     {status.get('name', '?')}")
        self._log(f"  state:    {status.get('state', '?')}")
        self._log(f"  autonomy: {status.get('autonomy', '?')}")
        self._log(f"  goals:    {status.get('goals', 0)}")
        self._log(f"  rules:    {status.get('rules', 0)}")
        self._log(f"  tools:    {status.get('tools', 0)}")
        self._log(f"  memory:   {status.get('memory_entries', 0)} entries")

    # ----------------------------------------------------------- demo (feature_010)

    def _cmd_demo(self, args: str) -> None:
        """Open the demo screen with an optional scenario key (``demo [a|b]``)."""
        scenario = args.strip().lower() or "a"
        self._log(f"[bold cyan]Launching demo (scenario {scenario})…[/bold cyan]")
        self.action_open_demo(scenario)

    def action_open_demo(self, scenario_name: str = "a") -> None:
        """Push the :class:`AgentDemoScreen` seeded with *scenario_name*."""
        try:
            from agentx.agent.view.tui.demo_screen import AgentDemoScreen

            if hasattr(self, "app") and self.app is not None:
                self.app.push_screen(
                    AgentDemoScreen(self._controller, scenario_name=scenario_name)
                )
        except Exception as exc:  # noqa: BLE001 — never crash the TUI
            try:
                self.notify(f"Error opening demo: {exc}", severity="error", timeout=None)
            except Exception:
                pass

    # ----------------------------------------------------------- reflection (N4)

    def _cmd_proposals(self) -> None:
        """List reflection proposals awaiting user confirmation."""
        if not self._controller:
            self._log("[red]No controller connected.[/red]")
            return
        pending = self._controller.list_pending_proposals()
        if not pending:
            self._log("[dim]No proposals awaiting approval.[/dim]")
            self._log("[dim]Run cycles (with an AI service wired) to generate proposals.[/dim]")
            return
        self._log(f"[bold]Pending Proposals ({len(pending)}):[/bold]")
        for n, (entry_id, idx, proposal) in enumerate(pending, 1):
            self._log(
                f"  [yellow]#{n}[/yellow] {proposal.type.value} — {proposal.rationale or '(no rationale)'}"
            )
            self._log(f"      [dim]content: {proposal.content}[/dim]")
            self._log(f"      [dim]approve with: approve {n}[/dim]")

    def _cmd_approve(self, args: str) -> None:
        """Approve and apply a pending proposal by its 1-based number."""
        if not self._controller:
            self._log("[red]No controller connected.[/red]")
            return
        if not args.strip().isdigit():
            self._log("[red]Usage: approve <n>  (use 'proposals' to list)[/red]")
            return
        n = int(args.strip())
        pending = self._controller.list_pending_proposals()
        if n < 1 or n > len(pending):
            self._log(f"[red]Invalid number {n}. There are {len(pending)} pending proposal(s).[/red]")
            return
        entry_id, idx, proposal = pending[n - 1]
        ok = self._controller.approve_proposal(entry_id, idx)
        if ok:
            self._log(f"[green]Proposal #{n} ({proposal.type.value}) applied.[/green]")
        else:
            self._log(f"[red]Proposal #{n} could not be applied (check status).[/red]")
        self._refresh_status()

    def _cmd_goals(self) -> None:
        if not self._controller:
            self._log("[red]No controller connected.[/red]")
            return
        tree = self._controller.list_goals()  # N6: via controller, not get_agent()
        if not tree.nodes:
            self._log("[dim]No goals yet. Use 'goal <description>' to add one.[/dim]")
            return
        self._log(f"[bold]Goals ({len(tree.nodes)}):[/bold]")
        for goal in tree.nodes.values():
            status_color = {
                "ACTIVE": "green",
                "PENDING": "yellow",
                "COMPLETED": "cyan",
                "FAILED": "red",
                "BLOCKED": "magenta",
                "ABANDONED": "dim",
            }.get(goal.status.value, "white")
            self._log(
                f"  [{status_color}]{goal.status.value:10s}[/{status_color}] "
                f"pri={goal.priority:3d}  {goal.description}"
            )

    def _cmd_rules(self) -> None:
        if not self._controller:
            self._log("[red]No controller connected.[/red]")
            return
        rules = self._controller.list_rules()  # N6
        if not rules:
            self._log("[dim]No policy rules yet. Use 'rule <condition> | <action> <params>' to add one.[/dim]")
            return
        self._log(f"[bold]Policy Rules ({len(rules)}):[/bold]")
        for rule in rules:
            enabled_str = "[green]ON[/green]" if rule.enabled else "[red]OFF[/red]"
            self._log(
                f"  {rule.id[:8]}…  {enabled_str}  pri={rule.priority:4d}  "
                f"if({rule.condition_expr})  → {rule.action.type.value}"
            )

    def _cmd_memory(self) -> None:
        if not self._controller:
            self._log("[red]No controller connected.[/red]")
            return
        entries = self._controller.query_memory(limit=10)  # N6
        if not entries:
            self._log("[dim]No memory entries yet.[/dim]")
            return
        self._log(f"[bold]Recent Memory ({len(entries)} entries):[/bold]")
        for entry in entries:
            content_str = str(entry.content)
            if len(content_str) > 60:
                content_str = content_str[:57] + "…"
            self._log(
                f"  [{entry.metadata.source.value:14s}] imp={entry.metadata.importance:.2f}  {content_str}"
            )

    # ----------------------------------------------------------- IAgentViewPartner

    def show_status(self, status: Any) -> None:
        try:
            widget = self.query_one("#agent-status", Static)
            if isinstance(status, dict):
                widget.update(
                    f"Agent: {status.get('name', '?')} | "
                    f"state: {status.get('state', '?')} | "
                    f"goals: {status.get('goals', 0)} | "
                    f"rules: {status.get('rules', 0)} | "
                    f"tools: {status.get('tools', 0)}"
                )
        except Exception:
            pass

    def show_reflection_log(self, entries: list[ReflectionEntry]) -> None:
        for entry in entries:
            self._log(f"[bold magenta]Reflection {entry.id[:8]}…[/bold magenta]")
            self._log(f"  summary:    {entry.critique.summary}")
            self._log(f"  confidence: {entry.critique.confidence:.2f}")
            for s in entry.critique.strengths:
                self._log(f"  [green]+ {s}[/green]")
            for w in entry.critique.weaknesses:
                self._log(f"  [red]- {w}[/red]")
            for p in entry.proposals:
                self._log(f"  proposal: {p.type.value} [{p.status.value}] — {p.rationale}")

    def show_memory_view(self, query: MemoryQuery) -> None:
        self._log(f"[Memory] query: text={query.text!r} limit={query.limit}")

    def show_policy_editor(self, rules: list[PolicyRule]) -> None:
        self._log(f"[Policy] {len(rules)} rule(s)")
        for rule in rules:
            self._log(f"  {rule.id[:8]}…  pri={rule.priority}  enabled={rule.enabled}")

    def refresh_goal_tree(self) -> None:
        if self._controller is None:
            return
        try:
            tree = self.query_one("#agent-tree", Tree)
            tree.clear()
            tree.root.expand()
            goal_tree = self._controller.list_goals()  # N6
            if not goal_tree.nodes:
                tree.root.add_leaf("[dim]No goals yet[/dim]")
                return
            if goal_tree.root and goal_tree.root in goal_tree.nodes:
                root_goal = goal_tree.nodes[goal_tree.root]
                label = self._goal_label(root_goal)
                branch = tree.root.add(label, expand=True)
                self._populate_children(branch, goal_tree, root_goal.id)
            else:
                # no root — list all goals flat
                for goal in goal_tree.nodes.values():
                    tree.root.add_leaf(self._goal_label(goal))
        except Exception:
            pass

    def _goal_label(self, goal: Any) -> str:
        """Format a goal for display in the tree."""
        status_icon = {
            "ACTIVE": "🟢",
            "PENDING": "🟡",
            "COMPLETED": "✅",
            "FAILED": "❌",
            "BLOCKED": "🔴",
            "ABANDONED": "⚫",
        }.get(goal.status.value, "⚪")
        return f"{status_icon} {goal.description} [dim](pri={goal.priority})[/dim]"

    def _populate_children(self, branch: Any, goal_tree: Any, parent_id: str) -> None:
        goal = goal_tree.get(parent_id)
        if goal is None:
            return
        for child_id in goal.children:
            child = goal_tree.get(child_id)
            if child:
                sub = branch.add(self._goal_label(child), expand=True)
                self._populate_children(sub, goal_tree, child_id)

    def show_message(self, message: str) -> None:
        self._log(message)

    # ----------------------------------------------------------- actions

    def action_run_cycle(self) -> None:
        if not self._controller:
            return
        self._log("[bold blue]═══ Running cycle ═══[/bold blue]")
        try:
            result = self._controller.run_cycle()
            # Show decision
            self._log(f"  [bold]Decision:[/bold] {result.decision.reasoning} "
                      f"(confidence: {result.decision.confidence:.2f})")
            if result.decision.alternatives:
                self._log(f"  [dim]alternatives: {len(result.decision.alternatives)}[/dim]")
            # Show action result
            if result.action_result:
                ar = result.action_result
                if ar.success:
                    self._log(f"  [green]Action: SUCCESS[/green] ({ar.duration_ms}ms)")
                    if ar.output:
                        output_str = str(ar.output)
                        if len(output_str) > 80:
                            output_str = output_str[:77] + "…"
                        self._log(f"  output: {output_str}")
                else:
                    self._log(f"  [red]Action: FAILED[/red] — {ar.error}")
            else:
                self._log("  [dim]Action: none (no EXECUTE_TOOL)[/dim]")
            # Show reflection
            if result.reflection:
                self._log(f"  [magenta]Reflection:[/magenta] {result.reflection.critique.summary}")
        except Exception as exc:
            self._log(f"[red]Cycle error: {exc}[/red]")
        self._refresh_status()

    def action_save(self) -> None:
        if not self._controller:
            return
        try:
            snapshot_id = self._controller.save_snapshot()  # N6
            self._log(f"[green]Snapshot saved: {snapshot_id[:8]}…[/green]")
        except Exception as exc:
            self._log(f"[red]Save error: {exc}[/red]")

    # ----------------------------------------------------------- helpers

    def _log(self, message: str) -> None:
        """Write a line to the activity log."""
        try:
            log = self.query_one("#agent-log", RichLog)
            log.write(message)
        except Exception:
            pass

    def _refresh_status(self) -> None:
        if self._controller:
            self.show_status(self._controller.get_status())  # N6: via controller
            self.refresh_goal_tree()


# Register as a virtual subclass of IAgentViewPartner (avoids metaclass conflict
# between Textual's _MessagePumpMeta and abc.ABCMeta).
IAgentViewPartner.register(AgentTUIScreen)
