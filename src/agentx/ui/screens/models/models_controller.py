"""Models screen controller — list/select the current AI model provider.

Implements the :class:`IModelsViewPartner` Abstract Partner (the View's only API
to the controller) and delegates to the :class:`ModelRegistry` (Model layer).

Design: ``design_001_model_selector.md``.
Operation spec: ``operation_spec_001_model_selector.md``.

MVC++: Controller — imports Model (``ModelRegistry``), knows nothing of the
concrete View (the View is duck-typed via the partner interface).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from agentx.model.ai.model_registry import ModelRegistry, default_registry


class IModelsViewPartner(ABC):
    """Abstract Partner for the Models View (implemented by ModelsController).

    The View calls **only** these methods — never the controller's internals or
    the Model layer directly.
    """

    @abstractmethod
    def list_providers(self) -> list:
        """Return the catalog of available providers (ProviderInfo list)."""
        ...

    @abstractmethod
    def get_current_id(self) -> str:
        """Return the id of the currently selected provider."""
        ...

    @abstractmethod
    def select_provider(self, provider_id: str) -> bool:
        """Set + persist the current provider. ``True`` on success."""
        ...

    @abstractmethod
    def get_status_text(self) -> str:
        """Return a one-line human-readable status of the current selection."""
        ...


class ModelsController(IModelsViewPartner):
    """Controller backing the Models screen.

    A thin orchestration layer over :class:`ModelRegistry`: the controller owns
    no state of its own — every call delegates to the registry so the selection
    is shared app-wide (the same registry the ``AIService`` consults).
    """

    def __init__(self, registry: ModelRegistry | None = None) -> None:
        self._registry: ModelRegistry = (
            registry if registry is not None else default_registry
        )

    def list_providers(self) -> list:
        """Return the catalog of available providers in display order."""
        return self._registry.list_providers()

    def get_current_id(self) -> str:
        """Return the id of the currently selected provider."""
        return self._registry.get_current_id()

    def select_provider(self, provider_id: str) -> bool:
        """Set and persist the current provider; ``True`` if applied."""
        return self._registry.select(provider_id)

    def get_status_text(self) -> str:
        """Return e.g. ``'Current: OpenRouter (cloud)'``."""
        info = self._registry.get_current()
        return f"Current: {info.name} ({info.kind})"

    # Convenience for tests / programmatic access.
    @property
    def registry(self) -> ModelRegistry:
        return self._registry
