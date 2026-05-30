from __future__ import annotations

from agentx.ui.common.input.text_list.input_text_list_view import InputTextView


class InputTextListController:
    """Controller for collecting a comma-separated list of text items."""

    items: list[str]

    def __init__(self):
        self.view = InputTextView(self)
        self.items = []

    def show(self) -> None:
        """Prompt the user for a comma-separated list and parse the result."""
        self.items = []

        raw = self.view.capture_input()
        if not raw:
            self.view.show_cancelled()
            return

        self.items = [
            part.strip()
            for part in raw.split(",")
            if part.strip()
        ]

        if self.items:
            self.view.show_done(self.items)
        else:
            self.view.show_cancelled()
