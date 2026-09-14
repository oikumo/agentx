"""UI Interfaces - chat contracts (split from ui/interfaces.py; re-exported for compatibility)."""

from __future__ import annotations

from abc import ABC, abstractmethod

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
    def show_message(self, message: str, role: str = "assistant") -> None:
        """Show message.

        Args:
            message: The message content.
            role: Either "user" or "assistant" (default: "assistant").
        """
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
    def show_message_chat_error(self, message: str | None = None) -> None:
        """Show chat error.

        Args:
            message: Optional actionable error text (e.g. provider name +
                credential hint).  When ``None`` the view uses its own
                generic "chat error" string (backward compatibility).
        """
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
