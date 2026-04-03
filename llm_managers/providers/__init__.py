from llm_managers.providers.llamacpp_provider import LlamaCppProvider
from llm_managers.providers.openai_provider import OpenAIProvider


def local_llm_provider() -> LlamaCppProvider:
    """Return default local LLM provider."""
    return LlamaCppProvider()


def cloud_llm_provider() -> OpenAIProvider:
    """Return default cloud LLM provider."""
    return OpenAIProvider()
