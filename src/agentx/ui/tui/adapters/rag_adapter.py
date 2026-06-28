"""TUI Adapter for RAG Screen.

Implements IRagView by delegating to an existing RagTUIScreen.
This adapter connects the RagController to the already-running TUI screen.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from agentx.ui.interfaces import IRagView

if TYPE_CHECKING:
    from agentx.ui.interfaces import IRagViewPartner
    from agentx.ui.tui.screens.rag_screen import RagTUIScreen


class TUIRagAdapter(IRagView):
    """Adapter that implements IRagView by delegating to RagTUIScreen.
    
    This adapter allows the existing RagController to work with the Textual TUI
    by connecting to an already-mounted RagTUIScreen instance.
    """

    def __init__(self, controller: IRagViewPartner) -> None:
        """Initialize TUI adapter for RAG.
        
        Args:
            controller: RagController instance implementing IRagViewPartner
        """
        self._controller = controller
        self._screen: RagTUIScreen | None = None

    def set_screen(self, screen: RagTUIScreen) -> None:
        """Set the RagTUIScreen instance to delegate to.
        
        Args:
            screen: The mounted RagTUIScreen instance
        """
        self._screen = screen

    def show(self) -> None:
        """Display RAG screen - no-op since screen is already pushed by MainTUIScreen."""
        # The screen is already displayed via app.push_screen() in MainTUIScreen
        pass

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