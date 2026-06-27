"""TUI Provider - Textual-based UI implementation.

This module provides the Textual TUI implementation of the UI provider interface.
It is completely isolated from the existing UI module.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from agentx.ui.interfaces import IUIProvider, IMainView, IRagView, IChatView
from agentx.ui.providers import ProviderRegistry

if TYPE_CHECKING:
    from agentx.ui.interfaces import IMainViewPartner, IRagViewPartner, IChatViewPartner


class TUIProvider(IUIProvider):
    """Textual TUI provider.
    
    Creates TUI adapters for all screens using the Textual framework.
    This is a completely isolated implementation that doesn't modify existing UI code.
    """

    def __init__(self) -> None:
        self._app: object | None = None
        self._initialized = False

    def create_main_view(self, controller: IMainViewPartner) -> IMainView:
        """Create TUI adapter for main screen.
        
        Args:
            controller: Controller instance
            
        Returns:
            TUIAdapter instance
        """
        from agentx.ui.tui.adapters.main_adapter import TUIAdapter
        return TUIAdapter(controller)

    def create_rag_view(self, controller: IRagViewPartner) -> IRagView:
        """Create TUI adapter for RAG screen.
        
        Args:
            controller: Controller instance
            
        Returns:
            TUIRagAdapter instance
        """
        from agentx.ui.tui.adapters.rag_adapter import TUIRagAdapter
        return TUIRagAdapter(controller)

    def create_chat_view(self, controller: IChatViewPartner) -> IChatView:
        """Create TUI adapter for chat screen.
        
        Args:
            controller: Controller instance
            
        Returns:
            TUIChatAdapter instance
        """
        from agentx.ui.tui.adapters.chat_adapter import TUIChatAdapter
        return TUIChatAdapter(controller)

    def initialize(self) -> None:
        """Initialize Textual framework."""
        self._initialized = True

    def shutdown(self) -> None:
        """Shutdown Textual framework."""
        self._initialized = False


# Register TUI provider
ProviderRegistry.register("tui", TUIProvider(), set_default=True)