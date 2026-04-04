# Dependencies & Configuration - Agent-X

---

## Dependencies

### Core

| Package | Version | Purpose |
|---------|---------|---------|
| langchain | >=1.2.13 | LLM framework |
| langchain-community | >=0.4.1 | Community integrations |
| langchain-ollama | >=1.0.1 | Ollama integration |
| langchain-openai | >=1.1.12 | OpenAI integration |
| langchain-pinecone | >=0.2.12 | Pinecone vector store |
| langchain-tavily | >=0.2.17 | Tavily web search |
| langchainhub | >=0.1.21 | LangChain Hub for prompts |
| langchain-experimental | >=0.4.1 | Experimental features |
| langchain-google-genai | >=4.2.1 | Google Gemini integration |
| langchain-openrouter | - | OpenRouter API integration (auto-routing) |
| langchain-chroma | >=1.1.0 | Chroma vector store |
| langgraph | >=1.1.3 | Graph-based workflows |
| llama-cpp-python | >=0.3.19 | Local LLM inference |

### Tools & Utilities

| Package | Version | Purpose |
|---------|---------|---------|
| chromadb | >=1.5.5 | Vector database |
| faiss-cpu | >=1.13.2 | Local vector store |
| pypdf | >=6.9.2 | PDF parsing |
| python-dotenv | >=1.2.2 | Environment variables |
| pandas | >=3.0.1 | Data manipulation |
| pillow | >=12.1.1 | Image processing |
| qrcode | >=8.2 | QR code generation |
| tabulate | >=0.9.0 | Table formatting |
| grandalf | >=0.8 | Graph visualization |
| qr | >=0.6.0 | QR code utilities |

### Dev

| Package | Version | Purpose |
|---------|---------|---------|
| pytest | >=9.0.2 | Testing framework |

---

## Environment Variables

### Required

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | OpenAI API authentication |
| `TAVILY_API_KEY` | Tavily web search API |
| `LLAMA_CPP_MODELS_CACHE_PATH` | Path to local GGUF model files |

### Optional

| Variable | Purpose |
|----------|---------|
| `LANGSMITH_TRACING` | Enable LangSmith tracing (`true`) |
| `LANGSMITH_ENDPOINT` | LangSmith endpoint URL |
| `LANGSMITH_API_KEY` | LangSmith API key |
| `LANGSMITH_PROJECT` | LangSmith project name |
| `PINECONE_API_KEY` | Pinecone vector store API key |
| `INDEX_NAME` | Pinecone index name |
| `INDEX_NAME_OLLAMA` | Ollama-specific index name |
| `INDEX_NAME_OPENAI` | OpenAI-specific index name |
| `INDEX_NAME_DOCUMENT_HELPER` | Document helper index name |

---

## Quick Start

```bash
# Install dependencies
uv sync

# Run the application
python main.py
```

### Available Commands

Once running, use `help` to see all available commands:

```
(agent-x) > help
```

### LLM Configuration

**Cloud Models**: Set `OPENAI_API_KEY` in `.env` for OpenAI models.

**Local Models**:
- Set `LLAMA_CPP_MODELS_CACHE_PATH` to directory containing GGUF model files
- Install Ollama and pull `nomic-embed-text` for embeddings
- Install Ollama and pull `functiongemma:270m-it-fp16` for function calling

---

## Code Style

- **Language**: Python >=3.14
- **Line Length**: 88 characters
- **Docstrings**: Google-style for public functions/classes
- **Naming**:
  - Functions/variables: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
  - Private members: `_prefix`
  - Modules/files: `snake_case.py`
- **Type Hints**: Preferred where beneficial
- **Tests**: Mirror source structure; unit tests focus on pure logic
