"""StatusBar — bottom status bar showing current app state and keybindings."""

from __future__ import annotations

from textual.widgets import Static
from textual.reactive import reactive


class StatusBar(Static):
    """Persistent bottom bar that displays the current status message.

    The Textual App calls set_status() after each command to update
    the bar with context like "Ready", "Running: chat…", or error info.
    """

    DEFAULT_CSS = """
    StatusBar {
        background: $primary-darken-2;
        color: $text;
        height: 1;
        padding: 0 1;
        dock: bottom;
    }
    """

    current_status: str = "Ready"

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.current_status = "Ready"

    def set_status(self, message: str) -> None:
        """Update the displayed status message."""
        self.current_status = message
        self.update(self._render_status())

    def _render_status(self) -> str:
        return (
            f"[bold]{self.current_status}[/bold]"
            "  │  [dim]ctrl+c quit  │  Tab autocomplete  │  ↑↓ history[/dim]"
        )

    def on_mount(self) -> None:
        self.update(self._render_status())
