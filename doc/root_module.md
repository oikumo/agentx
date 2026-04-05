# Root Module - Agent-X

## main.py (wrapper)

**Path**: `/main.py`

Thin wrapper that delegates to `src/main.py`.

```python
from src.main import main

if __name__ == "__main__":
    main()
```

## src/main.py (entry point)

**Path**: `src/main.py`

Application entry point. Loads environment variables via `dotenv`, creates `MainController`, registers all commands, and launches `ReplApp`.

```python
def main():
    controller = create_controller()
    ReplApp(controller).run()
```

**Registered Commands**:
- **CLI**: `quit`, `clear`, `help`, `read`
- **Math**: `sum`
- **LLM Chat**: `chat`, `router`, `react`, `search`, `function`, `rag`
- **LLM Graph**: `graph`, `chains`, `reflex`

---

## pyproject.toml

**Path**: `/pyproject.toml`

Project configuration with dependencies managed via `uv`. Source code discovered via `[tool.setuptools.packages.find]` where = ["src"].

- **Name**: agent-x
- **Version**: 0.1.0
- **Python**: >=3.14
- **Install**: `uv pip install -e .` (development mode)

---

## README.md

**Path**: `/README.md`

Contains environment variable documentation, package manager instructions (uv/pip), LLM configuration notes (Ollama models, OpenAI), and LangChain tool decorator patterns.
