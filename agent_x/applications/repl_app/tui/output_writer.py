"""TuiOutputWriter — thread-safe bridge between Command output and Textual UI.

Commands call log_info / log_warning / log_error in their run() bodies.
TuiOutputWriter intercepts those calls (via monkey-patching in the Textual
app) and forwards Rich-markup strings to a registered callback, which writes
them into the OutputPane RichLog widget.

The callback is intentionally a plain callable so that tests can inject a
MagicMock without ever spinning up a Textual App.
"""

from __future__ import annotations

from typing import Callable


class TuiOutputWriter:
    """Collect styled output messages and forward them to a Textual pane.

    Usage:
        writer = TuiOutputWriter()
        writer.set_callback(lambda markup: rich_log_widget.write(markup))
        writer.info("App started")
        writer.warning("Low memory")
        writer.error("Connection failed")
    """

    def __init__(self) -> None:
        self._callback: Callable[[str], None] | None = None

    def set_callback(self, callback: Callable[[str], None]) -> None:
        """Register the callable that writes markup into the UI pane."""
        self._callback = callback

    # ── Styled message helpers ────────────────────────────────────────────────

    def info(self, message: str) -> None:
        """Write an informational (blue) message."""
        self._emit(f"[bold cyan]ℹ[/bold cyan]  {message}")

    def warning(self, message: str) -> None:
        """Write a warning (yellow) message."""
        self._emit(f"[bold yellow]⚠[/bold yellow]  {message}")

    def error(self, message: str) -> None:
        """Write an error (red) message."""
        self._emit(f"[bold red]✗[/bold red]  {message}")

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
