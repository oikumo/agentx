"""UI Interfaces - agent contracts (split from ui/interfaces.py; re-exported for compatibility)."""

from __future__ import annotations

from abc import ABC, abstractmethod

class IAgentView(ABC):
    """Abstract interface for Advanced Agent View (console parity)."""

    @abstractmethod
    def show(self) -> None:
        """Display Advanced Agent screen."""
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


class IConsoleAgentViewPartner(ABC):
    """Abstract partner for Advanced Agent View (implemented by AgentController) — console mode."""

    @abstractmethod
    def send_message(self, user_message: str) -> bool:
        """Send a user message to the Agent."""
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


class IFastAgentView(ABC):
    """Abstract interface for Fast Agent View (console parity)."""

    @abstractmethod
    def show(self) -> None:
        """Display Fast Agent modal screen."""
        pass

    @abstractmethod
    def show_cycle_summary(self, summary: dict) -> None:
        """Show cycle summary result."""
        pass

    @abstractmethod
    def print_error(self, message: str) -> None:
        """Show error message."""
        pass


class IConsoleFastAgentViewPartner(ABC):
    """Abstract partner for Fast Agent View (implemented by FastAgentController) — console mode."""

    @abstractmethod
    def send_message(self, user_message: str) -> bool:
        """Send a user message to the Fast Agent."""
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
    def get_cycle_summary(self) -> dict:
        """Get the last cycle summary."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the controller and cancel any running agent."""
        pass

    @abstractmethod
    def start_new_conversation(self) -> None:
        """Start a new conversation (reset thread)."""
        pass
