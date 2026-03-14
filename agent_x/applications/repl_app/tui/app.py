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
freezes while an LLM command is running.  The TuiOutputWriter callback uses
call_from_thread() to safely post markup back to the OutputPane from the
worker thread.
"""

from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Static
from textual.worker import Worker, get_current_worker

from agent_x.applications.repl_app.command_line_controller.command_parser import \
    CommandParser
from agent_x.applications.repl_app.command_line_controller.commands_controller import \
    CommandsController
from agent_x.applications.repl_app.tui.output_writer import TuiOutputWriter
from agent_x.applications.repl_app.tui.widgets.command_input import \
    CommandInput
from agent_x.applications.repl_app.tui.widgets.output_pane import OutputPane
from agent_x.applications.repl_app.tui.widgets.status_bar import StatusBar

# Path to the companion CSS file
_CSS_PATH = Path(__file__).parent / "styles" / "app.tcss"


class TextualReplApp(App):
    """Full-screen Textual TUI that wraps the Agent-X command system.

    Args:
        controller: A CommandsController (typically MainController) that
                    holds the registered command dispatch table.
    """

    TITLE = "Agent-X"
    CSS_PATH = _CSS_PATH

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=True, priority=True),
        Binding("ctrl+l", "clear_output", "Clear", show=True),
    ]

    def __init__(self, controller: CommandsController, **kwargs) -> None:
        super().__init__(**kwargs)
        self._controller = controller
        self._parser = CommandParser()
        self._writer = TuiOutputWriter()

    # ── Compose ───────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        suggestions = [cmd.key for cmd in self._controller.get_commands()]

        yield Header(show_clock=True)
        yield OutputPane(id="output-pane")
        with Static(id="input-row"):
            yield Static("[bold cyan](agent-x) >[/bold cyan] ", id="prompt-label")
            yield CommandInput(suggestions=suggestions, id="command-input")
        yield StatusBar(id="status-bar")

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def on_mount(self) -> None:
        """Wire TuiOutputWriter → OutputPane and focus the input."""
        import threading

        import agent_x.common.logger as logger_module

        output = self.query_one(OutputPane)

        def _write_markup(markup: str) -> None:
            """Write markup safely from any thread."""
            try:
                # call_from_thread works when called from a worker thread.
                # When called from the main app thread (e.g. during tests via
                # the async Pilot), use output.write() directly.
                if threading.current_thread() is threading.main_thread():
                    output.write(markup)
                else:
                    self.call_from_thread(output.write, markup)
            except Exception:
                # Last resort: direct write (always safe on main thread)
                output.write(markup)

        self._writer.set_callback(_write_markup)

        # Store the default handler so we can restore it on shutdown.
        self._orig_handler = logger_module.get_handler()

        # Replace the logger handler with our TuiOutputWriter.  Every caller
        # that imported log_info / log_warning / log_error holds a reference
        # to those *functions*, which now delegate through _handler — so they
        # all transparently route output to the OutputPane.
        logger_module.set_handler(self._writer)

        self._show_welcome()
        self.query_one(CommandInput).focus()

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

        inp = self.query_one(CommandInput)
        inp.push_history(raw)
        inp.clear()

        # Echo the command into the output pane
        output = self.query_one(OutputPane)
        output.write(f"[bold cyan]>[/bold cyan] {raw}")

        command_data = self._parser.parse(raw)
        if not command_data:
            return

        command = self._controller.find_command(command_data.key)
        if not command:
            self._writer.unknown_command(command_data.key)
            self.query_one(StatusBar).set_status(f"Unknown command: {command_data.key}")
            return

        # Run the command in a worker thread so the UI stays responsive
        self.query_one(StatusBar).set_status(f"Running: {command_data.key}…")
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
            self.call_from_thread(self._writer.error, str(exc))
        finally:
            self.call_from_thread(self.query_one(StatusBar).set_status, "Ready")

    # ── Actions ───────────────────────────────────────────────────────────────

    def action_clear_output(self) -> None:
        """ctrl+l — clear the OutputPane."""
        self.query_one(OutputPane).clear()
        self.query_one(StatusBar).set_status("Ready")

    # ── Welcome banner ────────────────────────────────────────────────────────

    def _show_welcome(self) -> None:
        output = self.query_one(OutputPane)
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
