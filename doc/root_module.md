# Root Module - Agent-X

## main.py

**Path**: `/main.py`

Application entry point. Loads environment variables via `dotenv`, creates `MainController`, registers all commands, and launches `ReplApp`.

```python
def create_controller() -> MainController:
    main_controller = MainController()
    # Register 14 commands...
    return main_controller

if __name__ == "__main__":
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

Project configuration with dependencies managed via `uv`.

- **Name**: agent-x
- **Version**: 0.1.0
- **Python**: >=3.14

---

## README.md

**Path**: `/README.md`

Contains environment variable documentation, package manager instructions (uv/pip), LLM configuration notes (Ollama models, OpenAI), and LangChain tool decorator patterns.
