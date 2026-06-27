"""UI Interfaces - Abstract Base Classes for dependency inversion.

This module defines the abstract interfaces that all UI implementations must follow.
Controllers depend on these abstractions, not concrete implementations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Use TYPE_CHECKING to avoid circular imports
    # RagState is defined in rag_controller.py
    pass


class IMainView(ABC):
    """Abstract interface for Main Screen View."""

    @abstractmethod
    def show(self) -> None:
        """Display main screen."""
        pass

    @abstractmethod
    def print_message(self, message: str) -> None:
        """Show info message."""
        pass

    @abstractmethod
    def print_error_message(self, message: str) -> None:
        """Show error message."""
        pass

    @abstractmethod
    def print_warring_message(self, message: str) -> None:
        """Show warning message."""
        pass

    @abstractmethod
    def print_response(self, message: str) -> None:
        """Show response."""
        pass

    @abstractmethod
    def print_response_error(self, message: str) -> None:
        """Show error response."""
        pass


class IRagView(ABC):
    """Abstract interface for RAG Screen View."""

    @abstractmethod
    def show(self) -> None:
        """Display RAG screen."""
        pass

    @abstractmethod
    def print_message(self, message: str) -> None:
        """Show info message."""
        pass

    @abstractmethod
    def print_message_error(self, message: str) -> None:
        """Show error message."""
        pass

    @abstractmethod
    def show_repository_state(self, state: object) -> None:
        """Display repository information."""
        pass

    @abstractmethod
    def show_menu(self) -> None:
        """Display menu options."""
        pass


class IChatView(ABC):
    """Abstract interface for Chat Screen View."""

    @abstractmethod
    def show(self) -> None:
        """Display chat screen."""
        pass

    @abstractmethod
    def show_initial_message(self) -> None:
        """Show welcome message."""
        pass

    @abstractmethod
    def show_message(self, message: str) -> None:
        """Show message."""
        pass

    @abstractmethod
    def show_partial_message(self, message: str) -> None:
        """Show partial (streaming) message."""
        pass

    @abstractmethod
    def show_stream_message(self, message: str) -> None:
        """Stream message with typing effect."""
        pass

    @abstractmethod
    def show_message_chat_error(self) -> None:
        """Show chat error."""
        pass


class IUIProvider(ABC):
    """Abstract factory for UI components.
    
    This is the main dependency inversion interface.
    Controllers request views through this provider, never creating them directly.
    """

    @abstractmethod
    def create_main_view(self, controller: "IMainViewPartner") -> IMainView:
        """Create main view implementation.
        
        Args:
            controller: The controller that will use this view
            
        Returns:
            IMainView implementation
        """
        pass

    @abstractmethod
    def create_rag_view(self, controller: "IRagViewPartner") -> IRagView:
        """Create RAG view implementation.
        
        Args:
            controller: The controller that will use this view
            
        Returns:
            IRagView implementation
        """
        pass

    @abstractmethod
    def create_chat_view(self, controller: "IChatViewPartner") -> IChatView:
        """Create chat view implementation.
        
        Args:
            controller: The controller that will use this view
            
        Returns:
            IChatView implementation
        """
        pass

    @abstractmethod
    def initialize(self) -> None:
        """Initialize UI framework."""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Cleanup UI resources."""
        pass


# Forward declarations for type hints
# These interfaces are defined in controller files to avoid circular imports
class IMainViewPartner(ABC):
    """Abstract partner for Main View (implemented by MainController)."""

    @abstractmethod
    def run_command(self, user_input: str) -> None:
        """Execute a user command."""
        pass

    @abstractmethod
    def error(self) -> None:
        """Handle error state."""
        pass

    @abstractmethod
    def print(self) -> None:
        """Print output."""
        pass

    @abstractmethod
    def show_chat(self) -> None:
        """Show chat screen."""
        pass

    @abstractmethod
    def show_rag(self) -> None:
        """Show RAG screen."""
        pass


class IRagViewPartner(ABC):
    """Abstract partner for RAG View (implemented by RagController)."""

    @abstractmethod
    def select_repository(self) -> None:
        """Select a repository."""
        pass

    @abstractmethod
    def create_repository(self) -> None:
        """Create a new repository."""
        pass

    @abstractmethod
    def show_chat(self) -> None:
        """Show chat screen."""
        pass

    @abstractmethod
    def show_web_ingestion(self) -> None:
        """Show web ingestion screen."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the view."""
        pass

    @abstractmethod
    def get_rag_state(self) -> object:
        """Get RAG repository state."""
        pass


class IChatViewPartner(ABC):
    """Abstract partner for Chat View (implemented by ChatController)."""

    @abstractmethod
    def process_user_message(self, user_message: str) -> bool:
        """Process a user message."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the view."""
        pass

    @abstractmethod
    def start_interactive_streaming(self, system_prompt: str) -> None:
        """Start interactive streaming with system prompt."""
        pass