"""TuiOutputWriter — thread-safe bridge between Command output and Textual UI.

Commands call log_info / log_warning / log_error in their run() bodies.
The logger module delegates through a swappable handler; on TUI startup the
handler is replaced with a TuiOutputWriter instance so all command output is
captured and forwarded to the OutputPane RichLog widget.

The callback is intentionally a plain callable so that tests can inject a
MagicMock without ever spinning up a Textual App.
"""

from __future__ import annotations

from typing import Callable


class TuiOutputWriter:
    """Collect styled output messages and forward them to a Textual pane.

    Implements the same interface as ``agent_x.common.logger._DefaultHandler``
    so it can be passed directly to ``logger.set_handler()``.

    Usage:
        writer = TuiOutputWriter()
        writer.set_callback(lambda markup: rich_log_widget.write(markup))
        # Register as the active log handler so all log_* calls go here:
        import agent_x.common.logger as logger_module
        logger_module.set_handler(writer)
    """

    def __init__(self) -> None:
        self._callback: Callable[[str], None] | None = None

    def set_callback(self, callback: Callable[[str], None]) -> None:
        """Register the callable that writes markup into the UI pane."""
        self._callback = callback

    # ── Handler interface (mirrors logger._DefaultHandler) ────────────────────

    def info(self, message: str, color: str = "") -> None:
        """Write an informational (cyan) message."""
        self._emit(f"[bold cyan]ℹ[/bold cyan]  {message}")

    def success(self, message: str) -> None:
        """Write a success (green) message."""
        self._emit(f"[bold green]✔[/bold green]  {message}")

    def warning(self, message: str) -> None:
        """Write a warning (yellow) message."""
        self._emit(f"[bold yellow]⚠[/bold yellow]  {message}")

    def error(self, message: str) -> None:
        """Write an error (red) message."""
        self._emit(f"[bold red]✗[/bold red]  {message}")

    def header(self, message: str) -> None:
        """Write a header/section separator."""
        self._emit(f"[bold magenta]{'=' * 40}[/bold magenta]")
        self._emit(f"[bold magenta]  {message}[/bold magenta]")
        self._emit(f"[bold magenta]{'=' * 40}[/bold magenta]")

    def unknown_command(self, key: str) -> None:
        """Write a styled 'unknown command' error for the given key."""
        self._emit(
            f"[bold red]✗[/bold red]  Unknown command: [bold]{key}[/bold]"
            "  — type [bold]help[/bold] to see available commands"
        )

    def stream_token(self, token: str) -> None:
        """Forward a raw LLM token string to the output pane (no extra markup)."""
        self._emit(token)

    # ── Internal ──────────────────────────────────────────────────────────────

    def _emit(self, markup: str) -> None:
        """Send markup to the registered callback; silently no-op if absent."""
        if self._callback is not None:
            self._callback(markup)
