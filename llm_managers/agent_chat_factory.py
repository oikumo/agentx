from agents.chat.simple_chat import SimpleChat
from agents.chat.chat_loop import ChatLoop
from llm_managers.llm_provider import LLMProvider
from llm_managers.providers.llamacpp_provider import LlamaCppProvider
from llm_managers.providers.openai_provider import OpenAIProvider
from llm_managers.providers.openrouter_provider import OpenRouterProvider
from llm_models.local.llama_cpp_factory import LLAMA_CPP_MODEL_QWEN_3, LLAMA_CPP_MODEL_QWEN_2_5


def create_agent_chat(provider: LLMProvider | None = None) -> SimpleChat:
    if provider is None:
        provider = OpenAIProvider()
    llm = provider.create_llm()
    return SimpleChat(llm=llm)


create_agent_chat_local = create_agent_chat


def create_chat_loop(provider: LLMProvider | None = None) -> ChatLoop:
    if provider is None:
        # provider = OpenAIProvider()
        #provider = OpenRouterProvider()
        provider = LlamaCppProvider(
            model_filename=LLAMA_CPP_MODEL_QWEN_2_5,
            context_size=32768
        )

    llm = provider.create_llm()
    return ChatLoop(llm=llm)


create_chat_loop_local = create_chat_loop


def create_chat_loop_with_model(model_name: str) -> ChatLoop:
    provider = OpenRouterProvider(model_name=model_name)
    llm = provider.create_llm()
    return ChatLoop(llm=llm)
