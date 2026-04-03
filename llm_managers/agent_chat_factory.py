from agents.chat.simple_chat import SimpleChat
from llm_models.cloud.open_ai.open_ai_gpt import get_remote_llm_openai_gpt3_5_turbo
from llm_models.local.llama_cpp.llamacpp_config import LlamaCppConfig
from llm_models.local.llama_cpp_factory import model_factory_llamacpp, LLAMA_CPP_MODEL_QWEN_2_5
from llm_models.local.ollama_factory import local_ollama_models


def create_agent_chat_local():
    """
    config = LlamaCppConfig()
    config.model_filename = LLAMA_CPP_MODEL_QWEN_2_5
    config.context_size = 32768
    llm = model_factory_llamacpp.create_model_instance(config)
    """
    #llm = local_ollama_models.get_think_model()

    llm = get_remote_llm_openai_gpt3_5_turbo()

    return SimpleChat(llm=llm)
