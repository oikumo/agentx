from abc import ABC, abstractmethod

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_openrouter import ChatOpenRouter

from agentx.model.ai.local.llama_cpp.llamacpp_config import LlamaCppConfig
from agentx.model.ai.local.llama_cpp_factory import model_factory_llamacpp


class LLMProvider(ABC):
    """Strategy interface for LLM model providers."""

    @abstractmethod
    def create_llm(self) -> BaseChatModel:
        """Create and return a configured LLM instance."""
        ...


class LlamaCppProvider(LLMProvider):
    """Local LLM provider using LlamaCpp with Qwen 2.5."""

    def __init__(
        self,
        model_filename: str,
        context_size: int,
    ) -> None:
        self.model_filename = model_filename
        self.context_size = context_size

    def create_llm(self) -> BaseChatModel:
        config = LlamaCppConfig()
        config.model_filename = self.model_filename
        config.context_size = self.context_size
        return model_factory_llamacpp.create_model_instance(config)


class OpenAIProvider(LLMProvider):
    """Cloud LLM provider using OpenAI GPT-3.5-turbo."""

    def create_llm(self) -> BaseChatModel:
        return ChatOpenAI(model="gpt-3.5-turbo")


class OpenRouterProvider(LLMProvider):
    """Cloud LLM provider using OpenRouter with auto-routing."""

    def __init__(self, model_name: str = "openrouter/auto"):
        self._model_name = model_name

    def create_llm(self) -> BaseChatModel:
        return ChatOpenRouter(
            model=self._model_name,
            temperature=0.7,
            max_tokens=2048,
            max_retries=2,
            frequency_penalty=0.5,
        )


class OllamaProvider(LLMProvider):
    """Local LLM provider using a local Ollama server.

    Wraps the existing :class:`agentx.model.ai.local.ollama.ollama.Ollama`
    adapter so Ollama is reachable through the unified :class:`LLMProvider`
    strategy interface (feature_013).
    """

    def __init__(self, model_name: str = "qwen3.5:0.8b") -> None:
        self._model_name = model_name

    def create_llm(self) -> BaseChatModel:
        # Lazy import keeps provider module load light and survives a missing
        # Ollama server at import time (the error surfaces only on use).
        from agentx.model.ai.local.ollama.ollama import Ollama

        return Ollama(self._model_name).get_model()


class GeminiProvider(LLMProvider):
    """Cloud LLM provider using Google Gemini.

    Wraps the existing ``get_remote_llm_google_gemini`` factory so Gemini is
    reachable through the unified :class:`LLMProvider` strategy interface
    (feature_013).
    """

    def __init__(self, model_name: str = "gemini-2.5-flash-lite") -> None:
        self._model_name = model_name

    def create_llm(self) -> BaseChatModel:
        from agentx.model.ai.cloud.google.google_gemini import (
            get_remote_llm_google_gemini,
        )

        return get_remote_llm_google_gemini()


