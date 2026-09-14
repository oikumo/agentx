"""UI Interfaces - main contracts (split from ui/interfaces.py; re-exported for compatibility)."""

from __future__ import annotations

from abc import ABC, abstractmethod

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
