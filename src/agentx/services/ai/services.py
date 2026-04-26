from agentx.services.ai.providers import OpenRouterProvider, LlamaCppProvider, OpenAIProvider


def openrouter_llm_provider() -> OpenRouterProvider:
    return OpenRouterProvider()

def local_llm_provider(model_filename: str,
        context_size: int) -> LlamaCppProvider:
    return LlamaCppProvider(
        model_filename=model_filename,
        context_size=context_size)


def cloud_llm_provider() -> OpenAIProvider:
    return OpenAIProvider()
