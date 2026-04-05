from abc import ABC, abstractmethod

from langchain_core.language_models import BaseChatModel


class LLMProvider(ABC):
    """Strategy interface for LLM model providers."""

    @abstractmethod
    def create_llm(self) -> BaseChatModel:
        """Create and return a configured LLM instance."""
        ...
