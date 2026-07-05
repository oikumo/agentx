"""AgentDemoScreen — dedicated Textual screen demonstrating feature_007 (feature_010).

Launched from the :class:`AgentTUIScreen` via the ``demo`` command (or ``d``
key).  On open it loads a seeded scenario (A or B): clears prior state, writes a
sandbox file, submits a goal, and installs policy rules — then auto-runs one
perceive → decide → act → reflect cycle so the user immediately sees behaviour.

Buttons / keys:
  * **Run Cycle** (``r``)  — step one agent cycle; narrate the result.
  * **Reset** (``x``)      — clear + re-seed the current scenario (idempotent).
  * **Back** (``Escape``)  — pop back to the :class:`AgentTUIScreen` (agent main screen).

The screen is a pure View: it talks to the existing :class:`AgentController`
only (no Model imports).  It reads display data from controller query methods
(``get_status``, ``list_goals``, ``list_rules``) and the ``run_cycle()`` return
value, so it never reaches into agent internals.
"""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Label, RichLog, Static

from agentx.agent.interfaces import IAgentViewPartner
from agentx.ui.tui.framework import BaseAgentXScreen, register_partner


class AgentDemoScreen(BaseAgentXScreen):
    """Demonstrates the intelligent-agent cycle with a seeded scenario."""

    BINDINGS = [
        Binding("r", "run_cycle", "Run Cycle", show=True),
        Binding("x", "reset", "Reset", show=True),
        Binding("escape", "back", "Back", show=True),
    ]

    DEFAULT_CSS = """
    AgentDemoScreen {
        layout: vertical;
    }
    #demo-status {
        height: 3;
        background: $boost;
        padding: 0 1;
    }
    #demo-body {
        height: 1fr;
    }
    #demo-summary-panel {
        width: 1fr;
        border: solid $accent;
        padding: 0 1;
    }
    #demo-log {
        border: solid $primary;
        width: 2fr;
    }
    #demo-buttons {
        height: auto;
        padding: 0 1;
        background: $surface;
        border-top: solid $primary;
    }
    #demo-buttons Button {
        margin-right: 1;
    }
    #demo-scenario {
        color: $text;
        text-style: bold;
    }
    """

    def __init__(self, controller: Any | None = None, scenario_name: str = "a") -> None:
        super().__init__(controller)
        self._scenario_name = scenario_name.strip().lower() or "a"

    # ----------------------------------------------------------- compose

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Agent Demo — loading…", id="demo-status")
        with Horizontal(id="demo-body"):
            with Vertical(id="demo-summary-panel"):
                yield Label("🎯 Scenario", id="demo-scenario")
                yield Static("", id="demo-summary")
            yield RichLog(id="demo-log", highlight=False, markup=True)
        with Horizontal(id="demo-buttons"):
            yield Button("▶ Run Cycle", id="btn-run")
            yield Button("↻ Reset", id="btn-reset")
            yield Button("← Back to Agent", id="btn-back")
        yield Footer()

    def on_mount(self) -> None:
        self._log("[bold cyan]═══ Agent Demo ═══[/bold cyan]")
        loaded = self._load_scenario()
        if loaded:
            self._log("[dim]Auto-running one cycle…[/dim]")
            self.action_run_cycle()
        self._refresh_status()

    # ----------------------------------------------------------- buttons

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "btn-run":
            self.action_run_cycle()
        elif bid == "btn-reset":
            self.action_reset()
        elif bid == "btn-back":
            self.action_back()

    # ----------------------------------------------------------- actions

    def action_run_cycle(self) -> None:
        """Run one demo cycle on a worker thread (feature_014 freeze fix).

        ``run_cycle()`` makes a blocking ``llm.invoke()`` HTTP call.  Running
        it on the UI thread froze the entire TUI.  Now it runs via
        :meth:`run_blocking` on a daemon worker thread; the result is rendered
        in :meth:`_on_cycle_result` on the UI thread.
        """
        if not self._controller:
            self._log("[red]No controller connected.[/red]")
            return
        self._log("[bold blue]─── Running cycle ───[/bold blue]")
        self.run_blocking(
            self._controller.run_cycle,
            on_result=self._on_cycle_result,
            on_error=self._on_cycle_error,
        )

    def _on_cycle_result(self, result: Any) -> None:
        """Render the cycle result on the UI thread (called by run_blocking)."""
        try:
            self._render_cycle_result(result)
        except Exception as exc:  # noqa: BLE001 — never crash the TUI
            self._log(f"[red]Render error: {exc}[/red]")
        self._refresh_status()

    def _on_cycle_error(self, exc: Exception) -> None:
        """Handle a cycle error on the UI thread (called by run_blocking)."""
        self._log(f"[red]Cycle error: {exc}[/red]")
        self._refresh_status()

    def action_reset(self) -> None:
        self._log("[bold yellow]↻ Reset — re-seeding scenario…[/bold yellow]")
        self._load_scenario()
        self._refresh_status()

    # action_back is inherited from BaseAgentXScreen (try app.pop_screen()).

    # ----------------------------------------------------------- scenario loading

    def _load_scenario(self) -> bool:
        """Clear + seed the current scenario via the controller. Returns success."""
        if not self._controller:
            self._log("[red]No controller connected.[/red]")
            return False
        ok = self._controller.load_demo_scenario_by_name(self._scenario_name)
        if ok:
            info = self._controller.get_demo_scenario_info(self._scenario_name)
            if info:
                self._log(f"[green]Scenario loaded: {info['name']}[/green]")
        else:
            self._log(f"[red]Could not load scenario '{self._scenario_name}'.[/red]")
        return ok

    # ----------------------------------------------------------- rendering

    def _render_cycle_result(self, result: Any) -> None:
        # Decision
        decision = getattr(result, "decision", None)
        if decision is not None:
            self._log(
                f"  [bold]Decide:[/bold] {decision.reasoning} "
                f"(confidence: {decision.confidence:.2f})"
            )
            if getattr(decision, "alternatives", None):
                self._log(f"  [dim]alternatives: {len(decision.alternatives)}[/dim]")
        # Action
        ar = getattr(result, "action_result", None)
        if ar is not None:
            if ar.success:
                self._log(f"  [green]Act: SUCCESS[/green] ({ar.duration_ms}ms)")
                if ar.output:
                    out = str(ar.output)
                    if len(out) > 90:
                        out = out[:87] + "…"
                    self._log(f"  [dim]output: {out}[/dim]")
            else:
                self._log(f"  [red]Act: FAILED[/red] — {ar.error}")
        else:
            self._log("  [dim]Act: none (no EXECUTE_TOOL fired)[/dim]")
        # Reflection
        refl = getattr(result, "reflection", None)
        if refl is not None:
            self._log(f"  [magenta]Reflect:[/magenta] {refl.critique.summary}")
        else:
            self._log("  [dim]Reflect: skipped (no AI service)[/dim]")

    def _refresh_status(self) -> None:
        if not self._controller:
            return
        # status bar
        try:
            status = self._controller.get_status()
            self.query_one("#demo-status", Static).update(
                f"Demo | scenario: {self._scenario_name} | "
                f"state: {status.get('state', '?')} | "
                f"goals: {status.get('goals', 0)} | "
                f"rules: {status.get('rules', 0)} | "
                f"memory: {status.get('memory_entries', 0)}"
            )
        except Exception:
            pass
        # scenario summary panel
        try:
            info = self._controller.get_demo_scenario_info(self._scenario_name)
            goals = self._controller.list_goals()
            rules = self._controller.list_rules()
            lines: list[str] = []
            if info:
                lines.append(f"[bold]{info['name']}[/bold]  [dim](key: {info['key']})[/dim]")
                lines.append(info["description"])
                lines.append(f"[dim]seed files: {', '.join(info['files']) or 'none'}[/dim]")
            lines.append("")
            lines.append(f"[bold]Goals ({len(goals.nodes)}):[/bold]")
            if goals.nodes:
                for g in goals.nodes.values():
                    lines.append(f"  • {g.status.value}  {g.description}")
            else:
                lines.append("  [dim]none[/dim]")
            lines.append("")
            lines.append(f"[bold]Rules ({len(rules)}):[/bold]")
            if rules:
                for r in rules:
                    lines.append(f"  • pri={r.priority}  if({r.condition_expr}) → {r.action.type.value}")
            else:
                lines.append("  [dim]none[/dim]")
            self.query_one("#demo-summary", Static).update("\n".join(lines))
        except Exception:
            pass

    # ----------------------------------------------------------- helpers

    def _log(self, message: str) -> None:
        """Append a line to the demo log (delegates to BaseAgentXScreen.safe_log)."""
        self.safe_log("demo-log", message)


# Register as a virtual subclass of IAgentViewPartner via the framework helper
# (matches AgentTUIScreen's pattern; avoids the Textual/abc metaclass conflict).
register_partner(IAgentViewPartner, AgentDemoScreen)
