# LLM Models - Agent-X

**Path**: `src/llm_models/`

LLM model providers and vector store integrations. Supports both cloud-hosted and locally-run models.

---

## Module Structure

```
src/llm_models/
├── cloud/
│   ├── google/
│   │   └── google_gemini.py     # Gemini wrapper
│   └── open_ai/
│       └── open_ai_gpt.py       # GPT wrappers
├── local/
│   ├── llama_cpp_factory.py     # Pre-configured factory
│   ├── llama_cpp/
│   │   ├── llamacpp.py          # LlamaCpp factory class
│   │   └── llamacpp_config.py   # Pydantic config
│   └── ollama/
│       └── ollama_embeddings.py # Ollama embeddings
└── vectorstores/
    └── vectorstore_pinecone.py  # Pinecone wrapper
```

---

## Cloud Providers

### cloud/open_ai/open_ai_gpt.py

**Functions**:
- `get_remote_llm_openai_gpt4() -> ChatOpenAI` - returns GPT-4-turbo (temperature=0)
- `get_remote_llm_openai_gpt3_5_turbo() -> ChatOpenAI` - returns GPT-3.5-turbo

### cloud/google/google_gemini.py

**Function**: `get_remote_llm_google_gemini() -> ChatGoogleGenerativeAI`

Returns Gemini 2.5 Flash Lite (temperature=1.0, max_retries=2).

---

## Local Providers

### local/llama_cpp/llamacpp_config.py

**Class**: `LlamaCppConfig(BaseModel)`

Pydantic configuration for Llama.cpp parameters:
- `model_filename: str = ""`
- `temperature: int = 0.7`
- `context_size: int = 4096`
- `max_tokens: int = 512`
- `top_p: int = 0.5`
- `batch_size: int = 64`

### local/llama_cpp/llamacpp.py

**Class**: `LlamaCpp`

Factory for creating local `ChatLlamaCpp` instances from GGUF model files.

**Methods**:
- `__init__(llama_cpp_cache_dir: str)` - stores cache directory
- `create_model_instance(config: LlamaCppConfig) -> BaseChatModel | None` - creates `ChatLlamaCpp` instance, returns None if model file not found

**Configuration**:
- `n_threads = multiprocessing.cpu_count() - 1`
- `repeat_penalty = 1.5`
- `verbose = False`

### local/llama_cpp_factory.py

**Constants**:
- `LLAMA_CPP_MODEL_QWEN_2_5 = "Qwen_Qwen2.5-1.5B-Instruct-GGUF_qwen2.5-1.5b-instruct-q4_k_m.gguf"`
- `LLAMA_CPP_MODEL_QWEN_3 = "unsloth_Qwen3-4B-GGUF_Qwen3-4B-Q2_K_L.gguf"`
- `LLAMA_CPP_MODEL_QWEN_3_5_OPUS = "Jackrong_Qwen3.5-2B-Claude-4.6-Opus-Reasoning-Distilled-GGUF_Qwen3.5-2B.Q4_K_M.gguf"`
- `LLAMA_CPP_MODELS_CACHE_PATH = "LLAMA_CPP_MODELS_CACHE_PATH"` (env var name)

**Variable**: `model_factory_llamacpp = LlamaCpp(os.environ[LLAMA_CPP_MODELS_CACHE_PATH])` - pre-configured singleton-style factory instance

### local/ollama/ollama_embeddings.py

**Function**: `create_embeddings_model() -> Embeddings`

Returns `OllamaEmbeddings` with `nomic-embed-text` model.

---

## Vector Stores

### vectorstores/vectorstore_pinecone.py

**Function**: `create_vectorstore_pinecone(index_name: str) -> PineconeVectorStore`

Creates Pinecone vector store with OpenAI `text-embedding-3-small` embeddings (chunk_size=50, retry_min_seconds=10).
