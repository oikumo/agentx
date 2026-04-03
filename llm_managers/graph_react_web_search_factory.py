from agents.graph_react_web_search.graph_react_web_search import GraphReactWebSearch
from llm_managers.llm_provider import LLMProvider
from llm_managers.providers.llamacpp_provider import LlamaCppProvider
from llm_managers.providers.openai_provider import OpenAIProvider


def create_graph_react_web_search(
    provider: LLMProvider | None = None,
    max_search_results: int = 1,
) -> GraphReactWebSearch:
    """Create a GraphReactWebSearch instance with the specified LLM provider.

    Args:
        provider: LLMProvider strategy implementation. Defaults to LlamaCppProvider.
        max_search_results: Maximum number of search results to process.

    Returns:
        Configured GraphReactWebSearch instance.
    """
    if provider is None:
        provider = LlamaCppProvider()
    llm = provider.create_llm()
    return GraphReactWebSearch(llm=llm, max_search_results=max_search_results)


def create_graph_react_web_search_local(
    max_search_results: int = 1,
) -> GraphReactWebSearch:
    """Create GraphReactWebSearch with local LLM provider.

    Args:
        max_search_results: Maximum number of search results to process.

    Returns:
        Configured GraphReactWebSearch instance.
    """
    return create_graph_react_web_search(LlamaCppProvider(), max_search_results)


def create_graph_react_web_search_cloud(
    max_search_results: int = 1,
) -> GraphReactWebSearch:
    """Create GraphReactWebSearch with cloud LLM provider.

    Args:
        max_search_results: Maximum number of search results to process.

    Returns:
        Configured GraphReactWebSearch instance.
    """
    return create_graph_react_web_search(OpenAIProvider(), max_search_results)
