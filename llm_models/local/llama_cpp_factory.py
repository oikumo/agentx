import os
from dotenv import load_dotenv
from llm_models.local.llama_cpp.llamacpp import LlamaCpp

load_dotenv()

LLAMA_CPP_MODEL_QWEN_2_5 = "models--Qwen--Qwen2.5-1.5B-Instruct-GGUF"
LLAMA_CPP_MODEL_QWEN_3 = "unsloth_Qwen3-4B-GGUF_Qwen3-4B-Q2_K_L.gguf"
LLAMA_CPP_MODEL_QWEN_3_5_OPUS = "Jackrong_Qwen3.5-2B-Claude-4.6-Opus-Reasoning-Distilled-GGUF_Qwen3.5-2B.Q4_K_M.gguf"
LLAMA_CPP_MODELS_CACHE_PATH = "LLAMA_CPP_MODELS_CACHE_PATH"

model_factory_llamacpp = LlamaCpp(os.environ[LLAMA_CPP_MODELS_CACHE_PATH])