"""TUI Adapter for RAG Screen.

Implements IRagView using Textual widgets.
This adapter bridges the existing RagController with the new Textual TUI.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from agentx.ui.interfaces import IRagView

if TYPE_CHECKING:
    from agentx.ui.interfaces import IRagViewPartner


class TUIRagAdapter(IRagView):
    """Adapter that implements IRagView using Textual.
    
    This adapter allows the existing RagController to work with the new Textual TUI
    without any modifications to the controller code.
    """

    def __init__(self, controller: IRagViewPartner) -> None:
        """Initialize TUI adapter for RAG.
        
        Args:
            controller: RagController instance implementing IRagViewPartner
        """
        self._controller = controller
        self._screen: object | None = None

    def show(self) -> None:
        """Display RAG screen using Textual."""
        # Run the Textual RAG screen
        from textual.app import App
        from agentx.ui.tui.screens.rag_screen import RagTUIScreen
        
        controller = self._controller
        
        class RagApp(App):
            def on_mount(self) -> None:
                self.push_screen(RagTUIScreen(controller))
        
        app = RagApp()
        app.run()

    def print_message(self, message: str) -> None:
        """Show info message.
        
        Args:
            message: Message to display
        """
        # Use print for now, but could use notifications
        print(f"[RAG INFO] {message}")

    def print_message_error(self, message: str) -> None:
        """Show error message.
        
        Args:
            message: Error message to display
        """
        print(f"[RAG ERROR] {message}")

    def show_repository_state(self, state: object) -> None:
        """Display repository information.
        
        Args:
            state: Repository state object
        """
        print(f"[RAG STATE] {state}")

    def show_menu(self) -> None:
        """Display menu options."""
        print("[RAG MENU]")