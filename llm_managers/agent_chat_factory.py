from agents.chat.simple_chat import SimpleChat
from agents.chat.chat_loop import ChatLoop
from llm_managers.llm_provider import LLMProvider
from llm_managers.providers.llamacpp_provider import LlamaCppProvider
from llm_managers.providers.openai_provider import OpenAIProvider
from llm_managers.providers.openrouter_provider import OpenRouterProvider


def create_agent_chat(provider: LLMProvider | None = None) -> SimpleChat:
    """Create a SimpleChat agent with the specified LLM provider.

    Args:
        provider: LLMProvider strategy implementation. Defaults to OpenAIProvider.

    Returns:
        Configured SimpleChat instance.
    """
    if provider is None:
        provider = OpenAIProvider()
    llm = provider.create_llm()
    return SimpleChat(llm=llm)


create_agent_chat_local = create_agent_chat


def create_chat_loop(provider: LLMProvider | None = None) -> ChatLoop:
    """Create a ChatLoop agent with the specified LLM provider.

    Args:
        provider: LLMProvider strategy implementation. Defaults to OpenAIProvider.

    Returns:
        Configured ChatLoop instance.
    """
    if provider is None:
        # provider = OpenAIProvider()
        provider = OpenRouterProvider()

    llm = provider.create_llm()
    return ChatLoop(llm=llm)


create_chat_loop_local = create_chat_loop


def create_chat_loop_with_model(model_name: str) -> ChatLoop:
    """Create a ChatLoop agent with a specific model name.

    Args:
        model_name: The model identifier to use (e.g., "gpt-4", "claude-3").

    Returns:
        Configured ChatLoop instance with the specified model.
    """
    provider = OpenRouterProvider(model_name=model_name)
    llm = provider.create_llm()
    return ChatLoop(llm=llm)
