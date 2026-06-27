"""TUI Adapter for Chat Screen.

Implements IChatView using Textual widgets.
This adapter bridges the existing ChatController with the new Textual TUI.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from agentx.ui.interfaces import IChatView

if TYPE_CHECKING:
    from agentx.ui.interfaces import IChatViewPartner


class TUIChatAdapter(IChatView):
    """Adapter that implements IChatView using Textual.
    
    This adapter allows the existing ChatController to work with the new Textual TUI
    without any modifications to the controller code.
    """

    def __init__(self, controller: IChatViewPartner) -> None:
        """Initialize TUI adapter for Chat.
        
        Args:
            controller: ChatController instance implementing IChatViewPartner
        """
        self._controller = controller
        self._screen: object | None = None

    def show(self) -> None:
        """Display chat screen using Textual."""
        from textual.app import App
        from agentx.ui.tui.screens.chat_screen import ChatTUIScreen
        
        # Create a simple Textual app that runs the chat screen
        class ChatApp(App):
            def __init__(self, controller: IChatViewPartner):
                super().__init__()
                self._controller = controller
            
            def on_mount(self) -> None:
                self.push_screen(ChatTUIScreen(self._controller))
        
        app = ChatApp(self._controller)
        app.run()

    def show_initial_message(self) -> None:
        """Show welcome message."""
        print("[CHAT] Starting interactive chat session...")

    def show_message(self, message: str) -> None:
        """Show message.
        
        Args:
            message: Message to display
        """
        print(f"[CHAT] {message}")

    def show_partial_message(self, message: str) -> None:
        """Show partial (streaming) message.
        
        Args:
            message: Partial message to display
        """
        print(f"[CHAT STREAM] {message}", end="", flush=True)

    def show_stream_message(self, message: str) -> None:
        """Stream message with typing effect.
        
        Args:
            message: Message chunk to stream
        """
        print(f"[CHAT STREAM] {message}", end="", flush=True)

    def show_message_chat_error(self) -> None:
        """Show chat error."""
        print("[CHAT ERROR] An error occurred during chat")