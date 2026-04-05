from langchain_core.language_models import BaseChatModel

from llm_managers.llm_provider import LLMProvider
from llm_models.local.llama_cpp.llamacpp_config import LlamaCppConfig
from llm_models.local.llama_cpp_factory import (
    LLAMA_CPP_MODEL_QWEN_2_5,
    model_factory_llamacpp,
)


class LlamaCppProvider(LLMProvider):
    """Local LLM provider using LlamaCpp with Qwen 2.5."""

    def __init__(
        self,
        model_filename: str,
        context_size: int,
    ) -> None:
        self.model_filename = model_filename
        self.context_size = context_size

    def create_llm(self) -> BaseChatModel:
        config = LlamaCppConfig()
        config.model_filename = self.model_filename
        config.context_size = self.context_size
        return model_factory_llamacpp.create_model_instance(config)
