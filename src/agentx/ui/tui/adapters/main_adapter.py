"""TUI Adapter for the Main Screen.

Implements :class:`IMainView` using Textual.

Refactored (feature_012.tui_framework): inherits :class:`BaseScreenAdapter` for
the shared controller storage.  Unlike the chat/RAG adapters (which delegate to
a pushed *screen*), the main adapter delegates to the running *app* — its
``show()`` creates and runs the :class:`TUIApplication`, and its ``print_*``
methods call ``app.notify``.  It therefore overrides ``__init__`` (to add the
``_app`` reference) and ``show()``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from agentx.ui.interfaces import IMainView
from agentx.ui.tui.framework import BaseScreenAdapter

if TYPE_CHECKING:
    from agentx.ui.interfaces import IMainViewPartner


class TUIAdapter(BaseScreenAdapter, IMainView):
    """Adapter that implements :class:`IMainView` using Textual.

    This adapter allows the existing :class:`MainController` to work with the
    Textual TUI without any modifications to the controller code.
    """

    def __init__(self, controller: "IMainViewPartner") -> None:
        """Initialize TUI adapter.

        Args:
            controller: MainController instance implementing IMainViewPartner
        """
        super().__init__(controller)
        # The main adapter delegates to the running *app* (not a pushed screen),
        # so it keeps an `_app` reference rather than using the inherited `_screen`.
        self._app: Any = None

    def show(self) -> None:
        """Display main screen by creating and running the TUIApplication."""
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
