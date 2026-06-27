"""TUI Adapter for Main Screen.

Implements IMainView using Textual widgets.
This adapter bridges the existing MainController with the new Textual TUI.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import App

from agentx.ui.interfaces import IMainView

if TYPE_CHECKING:
    from agentx.ui.interfaces import IMainViewPartner


class TUIAdapter(IMainView):
    """Adapter that implements IMainView using Textual.
    
    This adapter allows the existing MainController to work with the new Textual TUI
    without any modifications to the controller code.
    """

    def __init__(self, controller: IMainViewPartner) -> None:
        """Initialize TUI adapter.
        
        Args:
            controller: MainController instance implementing IMainViewPartner
        """
        self._controller = controller
        self._app: "App[object] | None" = None

    def show(self) -> None:
        """Display main screen using Textual."""
        from textual.app import App
        from agentx.ui.tui.app import TUIApplication
        
        # Create and run the Textual application
        app = TUIApplication(self._controller)
        self._app = app
        app.run()

    def print_message(self, message: str) -> None:
        """Show info message via notification.
        
        Args:
            message: Message to display
        """
        if self._app and hasattr(self._app, 'notify'):
            self._app.notify(message, severity="information", timeout=3)

    def print_error_message(self, message: str) -> None:
        """Show error message via notification.
        
        Args:
            message: Error message to display
        """
        if self._app and hasattr(self._app, 'notify'):
            self._app.notify(message, severity="error", timeout=None)

    def print_warring_message(self, message: str) -> None:
        """Show warning message via notification.
        
        Args:
            message: Warning message to display
        """
        if self._app and hasattr(self._app, 'notify'):
            self._app.notify(message, severity="warning", timeout=5)

    def print_response(self, message: str) -> None:
        """Show response via notification.
        
        Args:
            message: Response message to display
        """
        self.print_message(message)

    def print_response_error(self, message: str) -> None:
        """Show error response via notification.
        
        Args:
            message: Error response to display
        """
        self.print_error_message(message)