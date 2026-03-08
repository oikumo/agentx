"""CommandInput — styled input widget with autocomplete and command history.

Wraps Textual's Input widget and adds:
  - Tab autocomplete from a list of command suggestions.
  - Up/Down arrow command history navigation (bounded deque, max 100 entries).
  - Syntax-highlight-style prefix: the first token is styled differently.
"""

from __future__ import annotations

from collections import deque

from textual.widgets import Input
from textual.widgets.input import Selection
from textual.suggester import SuggestFromList


class CommandInput(Input):
    """Command-line input with autocomplete and bounded history.

    Args:
        suggestions: List of command key strings for autocomplete.
    """

    DEFAULT_CSS = """
    CommandInput {
        border: tall $accent;
        padding: 0 1;
        background: $surface;
    }
    CommandInput:focus {
        border: tall $accent-lighten-1;
    }
    """

    _MAX_HISTORY = 100

    def __init__(self, suggestions: list[str], **kwargs) -> None:
        suggester = SuggestFromList(suggestions, case_sensitive=False)
        kwargs.setdefault(
            "placeholder", "Type a command…  [Tab] autocomplete  [↑↓] history"
        )
        super().__init__(suggester=suggester, **kwargs)
        self.history: deque[str] = deque(maxlen=self._MAX_HISTORY)
        self._history_index: int = -1

    def push_history(self, command: str) -> None:
        """Add a command to history; blank/whitespace entries are ignored."""
        if command.strip():
            self.history.appendleft(command)
            self._history_index = -1

    def on_key(self, event) -> None:
        """Navigate history with Up/Down arrows."""
        if event.key == "up":
            if self.history:
                self._history_index = min(
                    self._history_index + 1, len(self.history) - 1
                )
                self.value = self.history[self._history_index]
                # Move cursor to end
                self.cursor_position = len(self.value)
            event.stop()
        elif event.key == "down":
            if self._history_index > 0:
                self._history_index -= 1
                self.value = self.history[self._history_index]
            elif self._history_index == 0:
                self._history_index = -1
                self.value = ""
            self.cursor_position = len(self.value)
            event.stop()
