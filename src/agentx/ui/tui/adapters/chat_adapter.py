"""TUI Adapter for the Chat Screen.

Implements :class:`IChatView` by delegating to an existing :class:`ChatTUIScreen`.

Refactored (feature_012.tui_framework): inherits :class:`BaseScreenAdapter`, so
the controller storage, ``set_screen``, and the no-op ``show`` come from the
base.  Only the ``IChatView`` delegation methods remain here.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from agentx.ui.interfaces import IChatView
from agentx.ui.tui.framework import BaseScreenAdapter

if TYPE_CHECKING:
    from agentx.ui.interfaces import IChatViewPartner
    from agentx.ui.tui.screens.chat_screen import ChatTUIScreen


class TUIChatAdapter(BaseScreenAdapter, IChatView):
    """Adapter that implements :class:`IChatView` by delegating to :class:`ChatTUIScreen`.

    This adapter allows the existing :class:`ChatController` to work with the
    Textual TUI by connecting to an already-mounted :class:`ChatTUIScreen`.
    """

    # __init__, set_screen, and show() are inherited from BaseScreenAdapter.

    def show_initial_message(self) -> None:
        """Show welcome message."""
        if self._screen:
            self._screen.show_initial_message()

    def show_message(self, message: str) -> None:
        """Show message.

        Args:
            message: Message to display
        """
        if self._screen:
            self._screen.show_message(message)

    def show_partial_message(self, message: str) -> None:
        """Show partial (streaming) message.

        Args:
            message: Partial message to display
        """
        if self._screen:
            self._screen.show_partial_message(message)

    def show_stream_message(self, message: str) -> None:
        """Stream message with typing effect.

        Args:
            message: Message chunk to stream
        """
        if self._screen:
            self._screen.show_stream_message(message)

    def show_message_chat_error(self) -> None:
        """Show chat error."""
        if self._screen:
            self._screen.show_message_chat_error()
