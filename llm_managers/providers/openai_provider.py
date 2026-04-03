from langchain_core.language_models import BaseChatModel

from llm_managers.llm_provider import LLMProvider
from llm_models.cloud.open_ai.open_ai_gpt import get_remote_llm_openai_gpt3_5_turbo


class OpenAIProvider(LLMProvider):
    """Cloud LLM provider using OpenAI GPT-3.5-turbo."""

    def create_llm(self) -> BaseChatModel:
        return get_remote_llm_openai_gpt3_5_turbo()
