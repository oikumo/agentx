from __future__ import annotations

from agentx.model.ai.model_registry import ModelRegistry, ProviderInfo, default_registry
from agentx.model.ai.providers import OpenRouterProvider, LlamaCppProvider, OpenAIProvider


class AIService:
    """Facade over the AI provider stack.

    feature_013: the service now consults a :class:`ModelRegistry` for the
    *current* provider so the user can switch providers at runtime.  The legacy
    ``*_llm_provider`` methods are kept for backward compatibility (nothing that
    still calls them breaks), but new call sites should use
    :meth:`get_current_llm`.
    """

    def __init__(self, registry: ModelRegistry | None = None) -> None:
        self._registry: ModelRegistry = (
            registry if registry is not None else default_registry
        )

    # ----------------------------------------------------------- current selection

    def get_current_llm(self):
        """Build and return the LLM from the user-selected provider."""
        return self._registry.create_current_llm()

    def get_current_provider_info(self) -> ProviderInfo:
        """Return metadata for the currently selected provider."""
        return self._registry.get_current()

    def get_registry(self) -> ModelRegistry:
        """Expose the backing registry (used by the Models screen/controller)."""
        return self._registry

    def get_current_provider_name(self) -> str:
        """Return the name of the currently selected provider."""
        return self._registry.get_current().name

    def get_current_provider_id(self) -> str:
        """Return the id of the currently selected provider."""
        return self._registry.get_current_id()

    # ----------------------------------------------------------- legacy factories

    def openrouter_llm_provider(self) -> OpenRouterProvider:
        return OpenRouterProvider()

    def local_llm_provider(self, model_filename: str,
            context_size: int) -> LlamaCppProvider:
        return LlamaCppProvider(
            model_filename=model_filename,
            context_size=context_size)

    def cloud_llm_provider(self) -> OpenAIProvider:
        return OpenAIProvider()

    def rag_chromadb(self, directory: str):
        # Lazy import keeps AIService import light (saves ~1.1s: Chroma +
        # OllamaEmbeddings pull langchain_chroma/langchain_ollama/ollama/httpcore).
        # Most call sites mock rag_chromadb, so they never pay the heavy cost.
        from agentx.model.ai.vectorstores.vectorstore_chroma import (
            vectorstore_chroma_ollama,
        )

        return vectorstore_chroma_ollama(directory)
