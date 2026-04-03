from agents.chat.simple_chat import SimpleChat
from llm_managers.llm_provider import LLMProvider
from llm_managers.providers.openai_provider import OpenAIProvider


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
