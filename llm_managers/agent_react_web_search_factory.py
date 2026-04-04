from agents.react_web_search.agent_react_web_search import AgentReactWebSearch
from llm_managers.llm_provider import LLMProvider
from llm_managers.providers.llamacpp_provider import LlamaCppProvider
from llm_models.local.llama_cpp_factory import LLAMA_CPP_MODEL_QWEN_2_5


def create_agent_react_web_search(
    provider: LLMProvider | None = None,
) -> AgentReactWebSearch:
    """Create an AgentReactWebSearch instance with the specified LLM provider.

    Args:
        provider: LLMProvider strategy implementation. Defaults to LlamaCppProvider.

    Returns:
        Configured AgentReactWebSearch instance.
    """
    if provider is None:
        provider = LlamaCppProvider(
            model_filename=LLAMA_CPP_MODEL_QWEN_2_5,
            context_size=32768,
        )
    llm = provider.create_llm()
    return AgentReactWebSearch(llm)


create_agent_react_web_search_local = create_agent_react_web_search
