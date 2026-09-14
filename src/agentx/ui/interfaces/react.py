"""UI Interfaces - react contracts (split from ui/interfaces.py; re-exported for compatibility)."""

from __future__ import annotations

from abc import ABC, abstractmethod

class IReactView(ABC):
    """Abstract interface for ReAct View (console parity)."""

    @abstractmethod
    def show(self) -> None:
        """Display ReAct chat screen."""
        pass

    @abstractmethod
    def show_message(self, message: str, role: str = "assistant") -> None:
        """Show complete message."""
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
    def print_error(self, message: str) -> None:
        """Show error message."""
        pass


class IReactViewPartner(ABC):
    """Abstract partner for ReAct View (implemented by ReactController).

    This is the interface the View calls to interact with the Controller.
    The View receives this via constructor injection and should type-hint it
    as ``Any`` (duck-typed) to avoid a metaclass conflict with UI framework
    Screen.  ``register_partner`` virtually registers the screen as a
    subclass of this ABC.
    """

    @abstractmethod
    def send_message(self, user_message: str) -> bool:
        """Send a user message to the ReAct agent.

        Args:
            user_message: The user's input text.

        Returns:
            True if the message was accepted (agent started), False if the
            agent is already running.
        """
        pass

    @abstractmethod
    def cancel(self) -> None:
        """Cancel an in-progress agent run."""
        pass

    @property
    @abstractmethod
    def is_running(self) -> bool:
        """Whether the agent is currently running."""
        pass

    @abstractmethod
    def get_history(self) -> list:
        """Get the conversation message history."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the controller and cancel any running agent."""
        pass

    @abstractmethod
    def start_new_conversation(self) -> None:
        """Start a new conversation (reset thread)."""
        pass
