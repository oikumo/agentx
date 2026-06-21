# agentx

> **Version**: 0.1.1
> **Python**: 3.14+
> **Package Manager**: uv

---

## What is agentx?

agentx is a Python-based LLM agent framework with a REPL (Read-Eval-Print Loop) interface, created strictly for educational purposes. This project is free to use for everyone, including enterprise users, under the Apache 2.0 License.

It lets you interact with language models through a command-line shell, supporting chat, web search, PDF Q&A, function calling, and graph-based reasoning workflows. 

The development of this project is assisted by opencode coding agent (https://opencode.ai/).

---

## ⚠️ Important Legal Notice

**THIS IS AN EDUCATIONAL PROJECT ONLY**

agentx is created solely for educational and experimental purposes. It is not affiliated with, endorsed by, or sponsored by any of the companies or projects mentioned herein.

All product names, logos, brands, trademarks, and registered trademarks mentioned in this documentation or code are the property of their respective owners. Use of these names, logos, brands, and trademarks does not imply endorsement.

Specifically, but not limited to:
- OpenAI, OpenRouter, Ollama, LlamaCpp, Qwen are trademarks of their respective owners
- LangChain, LangGraph, FAISS, Pinecone, Chroma, Tavily are trademarks of their respective owners
- Any other third-party products or services mentioned are trademarks of their respective owners

This project may reference these trademarks solely for the purpose of describing compatibility or educational examples, which is permissible under nominative fair use. No association with or endorsement by these trademark owners is implied or intended.

Users are solely responsible for ensuring their use of any third-party services (such as OpenAI API, etc.) complies with those services' terms of service and applicable laws.

---

## Getting Started

### Prerequisites

- Python 3.14 or later
- `uv` package manager

### Installation

#### Direct Usage Globally


##### Install
```bash
# Clone the repository
git clone <repository-url>
uv tool install --editable agentx
```

##### Uninstall
```bash
uv tool uninstall agentx
```

#### Development

```bash
# Clone the repository
git clone <repository-url>
cd agentx
uv sync
```

### Testing

agentx includes comprehensive unit tests (205+ tests) covering all core modules:

```bash
# Run all unit tests
uv run pytest tests/unit/ -v

# Run specific module
uv run pytest tests/unit/model/session/ -v

# Run with coverage (if pytest-cov installed)
uv run pytest tests/unit/ --cov=agentx --cov-report=html
```

**Test Coverage**: Petri nets, session management, commands, views, utilities  
**Isolation**: All tests are isolated with mocking (no external dependencies)  
**Documentation**: See `tests/unit/README.md` for complete test documentation

### API Keys

agentx requires at least an **OpenRouter API key** to run the default chat agent. Other features may need additional keys. Set them in a `.env` file:

```env
# Required for default chat
OPENROUTER_API_KEY=your_key_here

# For web search agents
TAVILY_API_KEY=your_key_here

# For OpenAI models
OPENAI_API_KEY=your_key_here
```

If `OPENROUTER_API_KEY` is not set, the application will prompt for it on startup.

### Starting the Application

```bash
uv run main.py
```

You will see the agentx banner and the prompt:

```
(agentx)
```

Type `help` to see all available commands, or `quit` to exit.

---

## The REPL Interface

agentx uses an interactive command loop. Each line you enter is parsed as a command with optional arguments:

```
(agentx) command arg1 arg2
```

After each command, agentx prints the command history for the current session.

### Exiting

- Type `quit`
- Press `Ctrl+C`
- Press `Ctrl+D` (EOF)

---

## Commands Reference

### Utility Commands

| Command | Usage | Description |
|---------|-------|-------------|
| `help` | `help` | Lists all available commands with descriptions |
| `quit` | `quit` | Exits the application |
| `clear` | `clear` | Clears the terminal screen |
| `history` | `history` | Shows command history for current session |
| `sum` | `sum <a> <b>` | Adds two integers together |
| `new` | `new [name]` | Creates a new session |

**Examples:**

```
(agent-x) > help
(agent-x) > sum 42 58
100
(agent-x) > history
(agent-x) > new my-session
(agent-x) > clear
(agent-x) > quit
```

---

### AI Chat

The `chat` command is the primary way to interact with LLMs. It supports model selection and interactive conversations.

---

## Session Management

Each agentx session creates:
- A timestamped directory under `local_sessions/`
- A SQLite database for command history

Sessions are isolated and command history is persisted per session.

### Creating New Sessions

```
(agent-x) > new [session_name]
```

If no name is provided, a default session name will be used.


## Troubleshooting

### "Unknown command" error
Check your spelling with `help`. Commands are case-sensitive.

### API key prompt on startup
Set `OPENROUTER_API_KEY` in your `.env` file to avoid the interactive prompt.

### LLM connection errors
- Verify your API key is valid
- Check your internet connection
- For local models, ensure Ollama or LlamaCpp is properly configured

---

## License

Apache 2.0 - Educational and experimental purposes.
