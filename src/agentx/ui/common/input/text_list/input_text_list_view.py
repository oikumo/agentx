from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentx.ui.common.input.text_list.input_text_list_controller import InputTextListController
from agentx.ui.common.ui_console import UIConsole


class InputTextView:
    """View for the comma-separated text-list input component."""

    def __init__(self, controller: InputTextListController):
        self.controller = controller
        self.console = UIConsole("(list)")

    def capture_input(self) -> str | None:
        """Prompt for a comma-separated list of items.

        Returns the raw input string, or None if cancelled.
        """
        return self.console.capture_input()

    def show_done(self, items: list[str]) -> None:
        """Display the list of collected items."""
        items_str = ", ".join(items)
        self.console.info(f"Items: [{items_str}]")

    def show_cancelled(self) -> None:
        """Tell the user no items were entered."""
        self.console.waning("No items entered.")
