from llm_managers.providers.openrouter_provider import OpenRouterProvider
from llm_managers.providers.llamacpp_provider import LlamaCppProvider
from llm_managers.providers.openai_provider import OpenAIProvider
from llm_models.local.llama_cpp_factory import LLAMA_CPP_MODEL_QWEN_2_5

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
