"""UI Providers - Dependency injection for UI implementations.

This module provides the provider registry and concrete implementations.
Controllers request views through providers, maintaining dependency inversion.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from agentx.ui.interfaces import IMainView, IChatView, IRagView, IUIProvider

if TYPE_CHECKING:
    from agentx.ui.interfaces import IMainViewPartner, IRagViewPartner, IChatViewPartner


class ProviderRegistry:
    """Registry for UI providers.
    
    Allows switching between different UI implementations (TUI, console, etc.)
    without changing controller code.
    """

    _providers: dict[str, IUIProvider] = {}
    _default: str | None = None

    @classmethod
    def register(cls, name: str, provider: IUIProvider, set_default: bool = False) -> None:
        """Register a provider.
        
        Args:
            name: Provider identifier
            provider: Provider instance
            set_default: If True, set as default provider
        """
        cls._providers[name] = provider
        if set_default:
            cls._default = name

    @classmethod
    def get(cls, name: str) -> IUIProvider:
        """Get provider by name.
        
        Args:
            name: Provider identifier
            
        Returns:
            Provider instance
            
        Raises:
            ValueError: If provider not found
        """
        if name not in cls._providers:
            raise ValueError(f"Provider '{name}' not found. Available: {list(cls._providers.keys())}")
        return cls._providers[name]

    @classmethod
    def get_default(cls) -> IUIProvider:
        """Get default provider.
        
        Returns:
            Default provider instance
            
        Raises:
            ValueError: If no default set
        """
        if cls._default is None:
            raise ValueError("No default provider set. Register a provider with set_default=True")
        return cls._providers[cls._default]

    @classmethod
    def list_providers(cls) -> list[str]:
        """List registered provider names.
        
        Returns:
            List of provider names
        """
        return list(cls._providers.keys())


class ConsoleProvider(IUIProvider):
    """Fallback provider using existing console-based views.
    
    This provider maintains backward compatibility by using
    the existing ANSI console views.
    """

    def __init__(self) -> None:
        self._initialized = False

    def create_main_view(self, controller: IMainViewPartner) -> IMainView:
        """Create console-based main view.
        
        Args:
            controller: Controller instance
            
        Returns:
            MainView instance
        """
        from agentx.ui.screens.main.main_view import MainView
        return MainView(controller)  # type: ignore

    def create_rag_view(self, controller: IRagViewPartner) -> IRagView:
        """Create console-based RAG view.
        
        Args:
            controller: Controller instance
            
        Returns:
            RagView instance
        """
        from agentx.ui.screens.rag.rag_view import RagView
        return RagView(controller)  # type: ignore

    def create_chat_view(self, controller: IChatViewPartner) -> IChatView:
        """Create console-based chat view.
        
        Args:
            controller: Controller instance
            
        Returns:
            ChatView instance
        """
        from agentx.ui.screens.chat.chat_view import ChatView
        return ChatView(controller)  # type: ignore

    def initialize(self) -> None:
        """Initialize console UI (no-op)."""
        self._initialized = True

    def shutdown(self) -> None:
        """Shutdown console UI (no-op)."""
        self._initialized = False


# Register console provider as fallback
# Note: TUI provider will be added in ui/tui/provider.py
ProviderRegistry.register("console", ConsoleProvider())

# Import TUI provider to register it (if available)
try:
    from agentx.ui.tui import provider as tui_provider_module
    # TUI provider is registered in its module
except ImportError:
    pass  # TUI not available, use console only