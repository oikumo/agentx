from langchain_community.chat_models import ChatLlamaCpp
from langchain_core.language_models import BaseChatModel
import multiprocessing
from pathlib import Path
from llm_models.local.llama_cpp.llamacpp_config import LlamaCppConfig


class LlamaCpp:
    def __init__(self, llama_cpp_cache_dir: str):
        self.llama_cpp_cache_dir = llama_cpp_cache_dir

    def create_model_instance(self, config: LlamaCppConfig) -> BaseChatModel | None:
        base_dir = Path(self.llama_cpp_cache_dir)
        model_filename = config.model_filename
        model_path = str((base_dir / model_filename).resolve())

        if not Path.exists(Path(model_path)):
            raise FileNotFoundError(f"Model file not found: {model_path}")

        return ChatLlamaCpp(
            temperature=config.temperature,
            model_path=model_path,
            n_ctx=config.context_size,
            max_tokens=config.max_tokens,
            n_batch=config.batch_size,
            n_threads=multiprocessing.cpu_count() - 1,
            repeat_penalty=1.5,
            top_p=config.top_p,
            verbose=False)