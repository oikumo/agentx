"""TUI Adapter for the RAG Screen.

Implements :class:`IRagView` by delegating to an existing :class:`RagTUIScreen`.

Refactored (feature_012.tui_framework): inherits :class:`BaseScreenAdapter`, so
the controller storage, ``set_screen``, and the no-op ``show`` come from the
base.  Only the ``IRagView`` delegation methods remain here.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from agentx.ui.interfaces import IRagView
from agentx.ui.tui.framework import BaseScreenAdapter

if TYPE_CHECKING:
    from agentx.ui.interfaces import IRagViewPartner
    from agentx.ui.tui.screens.rag_screen import RagTUIScreen


class TUIRagAdapter(BaseScreenAdapter, IRagView):
    """Adapter that implements :class:`IRagView` by delegating to :class:`RagTUIScreen`.

    This adapter allows the existing :class:`RagController` to work with the
    Textual TUI by connecting to an already-mounted :class:`RagTUIScreen`.
    """

    # __init__, set_screen, and show() are inherited from BaseScreenAdapter.

    def print_message(self, message: str) -> None:
        """Show info message.

        Args:
            message: Message to display
        """
        if self._screen:
            self._screen.notify(message, severity="information", timeout=3)

    def print_message_error(self, message: str) -> None:
        """Show error message.

        Args:
            message: Error message to display
        """
        if self._screen:
            self._screen.notify(message, severity="error", timeout=None)

    def show_repository_state(self, state: object) -> None:
        """Display repository information.

        Args:
            state: Repository state object
        """
        if self._screen:
            self._screen._update_repository_ui(state)

    def show_menu(self) -> None:
        """Display menu options."""
        if self._screen:
            self._screen._show_menu()
