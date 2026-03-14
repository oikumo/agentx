"""TextualReplApp — full-screen Textual TUI for Agent-X.

Layout (top → bottom):
  ┌─────────────────────────────────────┐
  │  Header: "Agent-X"                  │  ← Textual Header (docked top)
  ├─────────────────────────────────────┤
  │                                     │
  │  OutputPane (RichLog, scrollable)   │  ← takes all remaining height
  │                                     │
  ├─────────────────────────────────────┤
  │  (agent-x) > CommandInput           │  ← Input row (3 lines high)
  ├─────────────────────────────────────┤
  │  StatusBar                          │  ← docked bottom (1 line)
  └─────────────────────────────────────┘

Command execution runs in a Textual worker (thread pool) so the UI never
freezes while an LLM command is running.  The logger integration writes
markup directly to the OutputPane from any thread.
"""

from __future__ import annotations

from pathlib import Path
from collections import deque

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Static, RichLog

from agent_x.applications.repl_app.command_line_controller.command_parser import (
    CommandParser,
)
from agent_x.applications.repl_app.command_line_controller.commands_controller import (
    CommandsController,
)
from agent_x.applications.repl_app.tui.widgets.command_input import CommandInput


class TextualReplApp(App):
    """Full-screen Textual TUI that wraps the Agent-X command system.

    Args:
        controller: A CommandsController (typically MainController) that
                    holds the registered command dispatch table.
    """

    TITLE = "Agent-X"
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=True, priority=True),
        Binding("ctrl+l", "clear_output", "Clear", show=True),
    ]

    # Inline CSS - eliminates external stylesheet
    CSS = """
    Screen {
        layout: vertical;
    }
    RichLog {
        border: solid $primary-darken-2;
        padding: 0 1;
        scrollbar-gutter: stable;
    }
    CommandInput {
        border: tall $accent;
        padding: 0 1;
        background: $surface;
    }
    CommandInput:focus {
        border: tall $accent-lighten-1;
    }
    Static#status-bar {
        background: $primary-darken-2;
        color: $text;
        height: 1;
        padding: 0 1;
        dock: bottom;
    }
    Static#prompt-label {
        color: cyan;
        text-style: bold;
    }
    """

    def __init__(self, controller: CommandsController, **kwargs) -> None:
        super().__init__(**kwargs)
        self._controller = controller
        self._parser = CommandParser()
        self._command_history: deque[str] = deque(maxlen=100)
        self._history_index: int = -1

    # ── Compose ───────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        suggestions = [cmd.key for cmd in self._controller.get_commands()]

        yield Header(show_clock=True)
        yield RichLog(id="output-pane", markup=True, highlight=True, wrap=True)
        with Static(id="input-row"):
            yield Static("[bold cyan](agent-x) >[/bold cyan] ", id="prompt-label")
            yield CommandInput(suggestions=suggestions, id="command-input")
        yield Static(id="status-bar")

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def on_mount(self) -> None:
        """Wire logger → OutputPane and focus the input."""
        output = self.query_one("#output-pane", RichLog)

        # Import and setup logger handler: delegate all log output to the RichLog
        import agent_x.common.logger as logger_module

        self._orig_handler = logger_module.get_handler()
        logger_module.set_handler(lambda msg: output.write(msg))

        # Set initial status to ready
        self.query_one("#status-bar", Static).update(
            "[bold]Ready[/bold]  │  [dim]ctrl+c quit  │  Tab autocomplete  │  ↑↓ history[/dim]"
        )

        self._show_welcome()
        self.query_one("#command-input").focus()

    def on_unmount(self) -> None:
        """Restore the original logger handler when the app exits."""
        import agent_x.common.logger as logger_module

        if hasattr(self, "_orig_handler"):
            logger_module.set_handler(self._orig_handler)

    # ── Input submission ──────────────────────────────────────────────────────

    def on_input_submitted(self, event) -> None:
        """Handle Enter on the CommandInput — parse and dispatch the command."""
        raw = event.value.strip()
        if not raw:
            return

        inp = self.query_one("#command-input", CommandInput)
        # History management (delegated to the widget)
        inp.push_history(raw)
        inp.clear()

        # Echo the command into the output pane
        output = self.query_one("#output-pane", RichLog)
        output.write(f"[bold cyan]>[/bold cyan] {raw}")

        command_data = self._parser.parse(raw)
        if not command_data:
            return

        command = self._controller.find_command(command_data.key)
        if not command:
            self.notify(f"Unknown command: {command_data.key}", severity="error")
            self.query_one("#status-bar", Static).update(
                f"[bold]Unknown command: {command_data.key}[/bold]  │  "
                "[dim]ctrl+c quit  │  Tab autocomplete  │  ↑↓ history[/dim]"
            )
            return

        # Run the command in a worker thread so the UI stays responsive
        self.query_one("#status-bar", Static).update(
            f"[bold]Running: {command_data.key}…[/bold]  │  "
            "[dim]ctrl+c quit  │  Tab autocomplete  │  ↑↓ history[/dim]"
        )
        self.run_worker(
            lambda: self._run_command(command, command_data.arguments),
            thread=True,
            name=f"cmd-{command_data.key}",
        )

    def _run_command(self, command, arguments: list[str]) -> None:
        """Execute command.run() inside a worker thread."""
        try:
            command.run(arguments)
        except Exception as exc:
            self.call_from_thread(self.notify, f"Error: {exc}", severity="error")
        finally:
            self.call_from_thread(
                self.query_one("#status-bar", Static).update,
                "[bold]Ready[/bold]  │  [dim]ctrl+c quit  │  Tab autocomplete  │  ↑↓ history[/dim]",
            )

    # ── Actions ───────────────────────────────────────────────────────────────

    def action_clear_output(self) -> None:
        """ctrl+l — clear the OutputPane."""
        self.query_one("#output-pane", RichLog).clear()
        self.query_one("#status-bar", Static).update(
            "[bold]Ready[/bold]  │  [dim]ctrl+c quit  │  Tab autocomplete  │  ↑↓ history[/dim]"
        )

    # ── Welcome banner ────────────────────────────────────────────────────────

    def _show_welcome(self) -> None:
        output = self.query_one("#output-pane", RichLog)
        commands = self._controller.get_commands()
        output.write("[bold cyan]╔══════════════════════════════════════╗[/bold cyan]")
        output.write(
            "[bold cyan]║[/bold cyan]  [bold white]Agent-X[/bold white]"
            "  —  [dim]AI-powered terminal[/dim]"
            "  [bold cyan]║[/bold cyan]"
        )
        output.write("[bold cyan]╚══════════════════════════════════════╝[/bold cyan]")
        output.write("")
        output.write(
            f"[dim]{len(commands)} commands available."
            "  Type [bold]help[/bold] to list them."
            "  [bold]Tab[/bold] autocompletes.  [bold]↑↓[/bold] recalls history.[/dim]"
        )
        output.write("")
