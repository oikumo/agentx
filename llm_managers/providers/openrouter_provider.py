from langchain_core.language_models import BaseChatModel
from langchain_openrouter import ChatOpenRouter
from llm_managers.llm_provider import LLMProvider


class OpenRouterProvider(LLMProvider):
    """Local LLM provider using LlamaCpp with Qwen 2.5."""

    def create_llm(self) -> BaseChatModel:
        return ChatOpenRouter(
            model="openrouter/auto",
            temperature=0,
            max_tokens=1024,
            max_retries=2,
            # other params...
        )

