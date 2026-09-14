"""UI Interfaces - rag contracts (split from ui/interfaces.py; re-exported for compatibility)."""

from __future__ import annotations

from abc import ABC, abstractmethod

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
