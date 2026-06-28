"""TUI Adapter for Chat Screen.

Implements IChatView by delegating to an existing ChatTUIScreen.
This adapter connects the ChatController to the already-running TUI screen.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from agentx.ui.interfaces import IChatView

if TYPE_CHECKING:
    from agentx.ui.interfaces import IChatViewPartner
    from agentx.ui.tui.screens.chat_screen import ChatTUIScreen


class TUIChatAdapter(IChatView):
    """Adapter that implements IChatView by delegating to ChatTUIScreen.
    
    This adapter allows the existing ChatController to work with the Textual TUI
    by connecting to an already-mounted ChatTUIScreen instance.
    """

    def __init__(self, controller: IChatViewPartner) -> None:
        """Initialize TUI adapter for Chat.
        
        Args:
            controller: ChatController instance implementing IChatViewPartner
        """
        self._controller = controller
        self._screen: ChatTUIScreen | None = None

    def set_screen(self, screen: ChatTUIScreen) -> None:
        """Set the ChatTUIScreen instance to delegate to.
        
        Args:
            screen: The mounted ChatTUIScreen instance
        """
        self._screen = screen

    def show(self) -> None:
        """Display chat screen - no-op since screen is already pushed by MainTUIScreen."""
        # The screen is already displayed via app.push_screen() in MainTUIScreen
        pass

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