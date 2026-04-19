# LLM Models Module

## Overview
LLM model providers and vector store integrations. Supports both cloud-hosted and locally-run models.

## Structure

```
llm_models/
├── cloud/
│   ├── google/
│   │   └── google_gemini.py         # Google Gemini via ChatGoogleGenerativeAI
│   └── open_ai/
│       └── open_ai_gpt.py           # OpenAI GPT via ChatOpenAI
├── local/
│   ├── llama_cpp_factory.py         # LlamaCpp factory singleton
│   ├── llama_cpp/
│   │   ├── llamacpp.py              # LlamaCpp model factory class
│   │   └── llamacpp_config.py       # Pydantic config for LlamaCpp models
│   └── ollama/
│       └── ollama_embeddings.py     # Ollama embeddings (nomic-embed-text)
└── vectorstores/
    └── vectorstore_pinecone.py      # Pinecone vector store with OpenAI embeddings
```

## Model Providers

| Provider | Models | Configuration |
|----------|--------|---------------|
| **OpenAI** | gpt-4-turbo, gpt-3.5-turbo | Hardcoded defaults |
| **Google** | gemini-2.5-flash-lite | Hardcoded defaults |
| **LlamaCpp** | Qwen 2.5, Qwen 3, Qwen 3.5 Opus | `LlamaCppConfig` Pydantic model |
| **Ollama** | nomic-embed-text (embeddings) | Direct instantiation |

## Factory Pattern
- `LlamaCpp` class in `llama_cpp_factory.py` creates local model instances
- Singleton-style module-level instance: `model_factory_llamacpp`
- Returns `None` if GGUF file doesn't exist
- Auto-detects CPU threads (`multiprocessing.cpu_count() - 1`)

## Configuration
- LlamaCpp models use `LlamaCppConfig` (Pydantic BaseModel) with: model_filename, temperature, context_size, max_tokens, top_p, batch_size
- Cache path from env var `LLAMA_CPP_MODELS_CACHE_PATH`
- Pre-defined model constants: `LLAMA_CPP_MODEL_QWEN_2_5`, `LLAMA_CPP_MODEL_QWEN_3`, `LLAMA_CPP_MODEL_QWEN_3_5_OPUS`
