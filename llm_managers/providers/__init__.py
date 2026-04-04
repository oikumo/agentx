from llm_managers.providers.llamacpp_provider import LlamaCppProvider
from llm_managers.providers.openai_provider import OpenAIProvider
from llm_models.local.llama_cpp_factory import LLAMA_CPP_MODEL_QWEN_2_5


def local_llm_provider() -> LlamaCppProvider:
    """Return default local LLM provider."""
    return LlamaCppProvider(
        model_filename=LLAMA_CPP_MODEL_QWEN_2_5,
        context_size=32768,
    )


def cloud_llm_provider() -> OpenAIProvider:
    """Return default cloud LLM provider."""
    return OpenAIProvider()
