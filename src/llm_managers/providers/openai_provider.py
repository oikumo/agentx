from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

from llm_managers.llm_provider import LLMProvider

class OpenAIProvider(LLMProvider):
    """Cloud LLM provider using OpenAI GPT-3.5-turbo."""

    def create_llm(self) -> BaseChatModel:
        return ChatOpenAI(model="gpt-3.5-turbo")

