import os
from dotenv import load_dotenv
from llm_models.local.llama_cpp.llamacpp import LlamaCpp

load_dotenv()

LLAMA_CPP_MODEL_QWEN_2_5 = "Qwen2.5-1.5B-Instruct-GGUF"
LLAMA_CPP_MODEL_QWEN_3 = "Qwen3-4B-GGUF"
LLAMA_CPP_MODELS_CACHE_PATH = "LLAMA_CPP_MODELS_CACHE_PATH"

model_factory_llamacpp = LlamaCpp(os.environ[LLAMA_CPP_MODELS_CACHE_PATH])