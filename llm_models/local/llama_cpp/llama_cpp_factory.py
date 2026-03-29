import os
from dataclasses import dataclass
from typing import Literal

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
import multiprocessing
from pathlib import Path
from langchain_community.chat_models import ChatLlamaCpp
from pydantic import BaseModel

LLAMA_CPP_MODELS_CACHE_PATH = Literal["LLAMA_CPP_MODELS_CACHE_PATH"]

class Config(BaseModel):
    model_filename: str = "",
    temperature: int = 0.7,
    context_size: int = 4096,
    max_tokens: int = 512,
    top_p: int = 0.5


class LlamaCpp:
    def __init__(self):
        self.llama_cpp_cache_dir = os.getenv(str(LLAMA_CPP_MODELS_CACHE_PATH))

    def create_model_instance(self, config: Config) -> BaseChatModel | None:
        base_dir = Path(self.llama_cpp_cache_dir)
        model_path = str((base_dir / config.model_filename).resolve())

        if not Path.exists(Path(model_path)):
            return None

        return ChatLlamaCpp(
            temperature=config.temperature,
            model_path=model_path,
            n_ctx=config.context_size,
            max_tokens=config.max_tokens,
            n_threads=multiprocessing.cpu_count() - 1,
            repeat_penalty=1.5,
            top_p=config.top_p,
            verbose=False)

llama_cpp = LlamaCpp()