from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_openrouter import ChatOpenRouter

from model.ai.local.llama_cpp.llamacpp_config import LlamaCppConfig
from model.ai.local.llama_cpp_factory import model_factory_llamacpp
from views.main_view import ChatLoop

class LLMProvider(ABC):
    """Strategy interface for LLM model providers."""

    @abstractmethod
    def create_llm(self) -> BaseChatModel:
        """Create and return a configured LLM instance."""
        ...


@dataclass
class RagConfig:
    pdf_path: str = "_resources/react.pdf"
    vectorstore_path: Optional[str] = None
    llm_provider: Optional[LLMProvider] = None
    embeddings: Optional[Embeddings] = None


class AgentFactory:

    @staticmethod
    def create_chat_loop(provider: LLMProvider | None = None) -> ChatLoop:
        if provider is None:
            provider = openrouter_llm_provider()

        llm = provider.create_llm()
        return ChatLoop(llm=llm)



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

    def __init__(self, model_name: str = "qwen/qwen3.6-plus:free"):
        self._model_name = model_name

    def create_llm(self) -> BaseChatModel:
        return ChatOpenRouter(
            model=self._model_name,
            temperature=0.7,
            max_tokens=2048,
            max_retries=2,
            frequency_penalty=0.5,
        )



def openrouter_llm_provider() -> OpenRouterProvider:
    """Return default local LLM provider."""
    return OpenRouterProvider()

def local_llm_provider(model_filename: str,
        context_size: int) -> LlamaCppProvider:
    """Return default local LLM provider."""
    return LlamaCppProvider(
        model_filename=model_filename,
        context_size=context_size)


def cloud_llm_provider() -> OpenAIProvider:
    """Return default cloud LLM provider."""
    return OpenAIProvider()
