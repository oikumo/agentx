from langchain_core.language_models import BaseChatModel
from langchain_openrouter import ChatOpenRouter
from llm_managers.llm_provider import LLMProvider


class OpenRouterProvider(LLMProvider):
    """Cloud LLM provider using OpenRouter with auto-routing."""

    def create_llm(self) -> BaseChatModel:
        return ChatOpenRouter(
            model="anthropic/claude-3.5-haiku",
            temperature=0.7,
            max_tokens=2048,
            max_retries=2,
            frequency_penalty=0.5,
        )
