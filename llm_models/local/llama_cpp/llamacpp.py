import openai
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from llm_models.local.llama_cpp.llamacpp_config import LlamaCppConfig


class LlamaCpp:
    def __init__(self, llama_cpp_cache_dir: str):
        self.llama_cpp_cache_dir = llama_cpp_cache_dir

    def create_model_instance(self, config: LlamaCppConfig) -> BaseChatModel | None:
        client = openai.OpenAI(
            base_url="http://localhost:8080/v1",
            api_key="not-needed",
        )

        return ChatOpenAI(
            client=client.chat.completions,
            model=config.model_filename,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            top_p=config.top_p,
            organization=None,
            timeout=10000,
            reasoning_effort="medium",
            verbosity="medium",
        )
