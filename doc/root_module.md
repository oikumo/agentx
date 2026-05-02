# Root Module - Agent-X

> **Last Updated**: April 2026

---

## main.py

Application entry point located at project root.

**Purpose**: Bootstraps the application and initiates the REPL loop.

**Key Functions**:
- Imports main controller from `src/main.py`
- Initializes the REPL application
- Handles application lifecycle

---

## pyproject.toml

Project configuration and dependency management.

### Project Metadata
- **Name**: agent-x
- **Version**: 0.1.0
- **Python**: >=3.14
- **Package Manager**: uv

### Dependencies
Core dependencies include:
- **LLM Providers**: langchain-openai, langchain-google-genai, langchain-ollama
- **Vector Stores**: chromadb, langchain-pinecone, faiss-cpu
- **LangChain**: langchain, langchain-community, langgraph
- **Local LLM**: llama-cpp-python
- **Utilities**: python-dotenv, pypdf

### Configuration
```toml
[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests", "tests_sandbox"]
pythonpath = ["src"]
```

---

## README.md

Project readme with:
- Project overview
- Installation instructions
- Quick start guide
- Feature list
- Architecture summary

---

## Related Files

| File | Description |
|------|-------------|
| `AGENTS.md` | System agent rules and commands |
| `.env` | Environment variables (not committed) |
| `uv.lock` | Dependency lock file |
