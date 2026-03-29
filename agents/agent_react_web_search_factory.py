from agents.react_web_search.agent_react_web_search import AgentReactWebSearch
from llm_models.local.llama_cpp.llamacpp_config import LlamaCppConfig
from llm_models.local.llama_cpp_factory import LLAMA_CPP_MODEL_QWEN_2_5, model_factory_llamacpp


def create_agent_react_web_search_local() -> AgentReactWebSearch:
    config = LlamaCppConfig()
    config.model_filename = LLAMA_CPP_MODEL_QWEN_2_5
    config.context_size = 32768
    llm = model_factory_llamacpp.create_model_instance(config)

    return AgentReactWebSearch(llm)