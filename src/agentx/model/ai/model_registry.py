"""Model provider registry — catalog + current selection + persistence.

This module is the single source of truth for *which* AI model provider the
application uses.  It replaces the hardcoded ``AIService().openrouter_llm_provider()``
calls scattered across Chat / RAG / Agent with a user-selectable, persistent
selection (feature_013.ai_model_provider_selector).

Design: ``design_001_model_selector.md``.
Operation spec: ``operation_spec_001_model_selector.md``.

MVC++: pure Model — no ``ui`` import.

Persistence: a single-key JSON file (``{"selected": "<id>"}``).  Selection is
one scalar, not entity CRUD, so a JSON file is the proportionate choice over the
project's sqlite DP pattern (which is for entities like Session/RAG).  All file
I/O is best-effort: a missing/corrupt/unwritable config never crashes the app —
the registry falls back to the default provider (``openrouter``).
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Literal

from langchain_core.language_models import BaseChatModel

from agentx.model.ai.providers import (
    GeminiProvider,
    LlamaCppProvider,
    LLMProvider,
    OpenAIProvider,
    OpenRouterProvider,
    OllamaProvider,
)

_log = logging.getLogger(__name__)

# --- defaults ---------------------------------------------------------------

DEFAULT_CONFIG_PATH = Path.home() / ".agentx" / "model_selection.json"
DEFAULT_PROVIDER_ID = "openrouter"

# Sensible defaults for the local providers' required parameters.
DEFAULT_LLAMACPP_MODEL = "qwen2.5-3b-instruct-q4_k_m.gguf"
DEFAULT_LLAMACPP_CONTEXT = 4096
DEFAULT_OLLAMA_MODEL = "qwen3.5:0.8b"
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash-lite"


@dataclass(frozen=True)
class ProviderInfo:
    """Static metadata + factory for one selectable provider."""

    id: str
    name: str
    kind: Literal["cloud", "local"]
    description: str
    factory: Callable[[], LLMProvider]


def _build_catalog() -> dict[str, ProviderInfo]:
    """Return the static catalog of available providers.

    Order matters: the Models screen renders providers in insertion order, so
    cloud providers are listed first (most likely to work out of the box),
    followed by local providers.
    """
    return {
        "openrouter": ProviderInfo(
            id="openrouter",
            name="OpenRouter",
            kind="cloud",
            description="Auto-routing across models (cloud)",
            factory=lambda: OpenRouterProvider(),
        ),
        "openai": ProviderInfo(
            id="openai",
            name="OpenAI GPT",
            kind="cloud",
            description="gpt-3.5-turbo (cloud)",
            factory=lambda: OpenAIProvider(),
        ),
        "gemini": ProviderInfo(
            id="gemini",
            name="Google Gemini",
            kind="cloud",
            description=f"{DEFAULT_GEMINI_MODEL} (cloud)",
            factory=lambda: GeminiProvider(),
        ),
        "ollama": ProviderInfo(
            id="ollama",
            name="Ollama",
            kind="local",
            description=f"{DEFAULT_OLLAMA_MODEL} via local Ollama server",
            factory=lambda: OllamaProvider(),
        ),
        "llamacpp": ProviderInfo(
            id="llamacpp",
            name="LlamaCpp",
            kind="local",
            description="local GGUF model (cpu)",
            factory=lambda: LlamaCppProvider(
                DEFAULT_LLAMACPP_MODEL, DEFAULT_LLAMACPP_CONTEXT
            ),
        ),
    }


class ModelRegistry:
    """Catalog + current selection + JSON persistence + LLM factory."""

    def __init__(self, config_path: Path | None = None) -> None:
        """Construct the registry.

        Args:
            config_path: Where to read/write the selection JSON.  Defaults to
                ``~/.agentx/model_selection.json``.  Inject a ``tmp_path`` in
                tests for isolation.
        """
        self._config_path: Path = (
            Path(config_path) if config_path is not None else DEFAULT_CONFIG_PATH
        )
        self._providers: dict[str, ProviderInfo] = _build_catalog()
        self._selected_id: str = DEFAULT_PROVIDER_ID
        self._load()

    # ----------------------------------------------------------- catalog API

    def list_providers(self) -> list[ProviderInfo]:
        """Return the catalog in display order (cloud first, then local)."""
        return list(self._providers.values())

    def get_provider(self, provider_id: str) -> ProviderInfo | None:
        """Return a provider by id, or ``None`` if unknown."""
        return self._providers.get(provider_id)

    def get_current(self) -> ProviderInfo:
        """Return the currently selected provider.

        If the stored selection is invalid (e.g. a provider was removed from the
        catalog), silently reset to the default and return it — the app always
        has a working provider.
        """
        info = self._providers.get(self._selected_id)
        if info is None:
            self._selected_id = DEFAULT_PROVIDER_ID
            info = self._providers[DEFAULT_PROVIDER_ID]
        return info

    def get_current_id(self) -> str:
        """Return the id of the currently selected provider."""
        return self.get_current().id

    # ----------------------------------------------------------- selection

    def select(self, provider_id: str) -> bool:
        """Set and persist the current provider.

        Returns ``True`` if ``provider_id`` is valid (selection applied,
        persistence attempted); ``False`` if unknown (selection unchanged).
        """
        if provider_id not in self._providers:
            return False
        self._selected_id = provider_id
        self._save()
        return True

    def create_current_llm(self) -> BaseChatModel:
        """Build a ready-to-use LLM from the current selection.

        Raises:
            Whatever the provider factory/``create_llm`` raises (missing API
            key, model not found, …).  Callers (Chat/RAG/Agent) already handle
            LLM errors.
        """
        info = self.get_current()
        provider = info.factory()
        return provider.create_llm()

    # ----------------------------------------------------------- persistence

    def _load(self) -> None:
        """Best-effort load of the selection from the config file."""
        try:
            if not self._config_path.exists():
                return
            data = json.loads(self._config_path.read_text(encoding="utf-8"))
            sel = data.get("selected")
            if isinstance(sel, str) and sel in self._providers:
                self._selected_id = sel
        except Exception as exc:  # noqa: BLE001 — persistence is best-effort
            _log.warning("model selection load failed (%s): %s", self._config_path, exc)

    def _save(self) -> None:
        """Best-effort persist of the selection to the config file."""
        try:
            self._config_path.parent.mkdir(parents=True, exist_ok=True)
            self._config_path.write_text(
                json.dumps({"selected": self._selected_id}), encoding="utf-8"
            )
        except Exception as exc:  # noqa: BLE001 — persistence is best-effort
            _log.warning("model selection save failed (%s): %s", self._config_path, exc)


# Module-level shared instance.  Reads ``~/.agentx/model_selection.json`` on
# first import (best-effort).  ``AIService`` and ``ModelsController`` default to
# this instance so the whole app shares one selection.
default_registry = ModelRegistry()
