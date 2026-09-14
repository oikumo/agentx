"""UI Interfaces - models contracts (split from ui/interfaces.py; re-exported for compatibility)."""

from __future__ import annotations

from abc import ABC, abstractmethod

class IModelsView(ABC):
    """Abstract interface for Models Selector View (console parity)."""

    @abstractmethod
    def show(self) -> None:
        """Display models selector screen."""
        pass

    @abstractmethod
    def show_available_providers(self, providers: list[str]) -> None:
        """Show list of available AI providers."""
        pass

    @abstractmethod
    def show_models_for_provider(self, provider: str, models: list[str]) -> None:
        """Show models available for a specific provider."""
        pass

    @abstractmethod
    def show_message(self, message: str) -> None:
        """Show info message."""
        pass

    @abstractmethod
    def print_error(self, message: str) -> None:
        """Show error message."""
        pass


class IModelsViewPartner(ABC):
    """Abstract partner for Models View (implemented by ModelsController)."""

    @abstractmethod
    def select_model(self, provider: str, model: str) -> None:
        """Select a model from a provider."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the view."""
        pass
