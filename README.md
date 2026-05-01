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
cd agentx
uv tool install --editable .
```

##### Uninstall
```bash
uv tool uninstall agent-x
```

#### Development

```bash
# Clone the repository
git clone <repository-url>
cd agentx
uv sync
```

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
python main.py
```

You will see the agentx banner and the prompt:

```
(agent-x) >
```

Type `help` to see all available commands, or `quit` to exit.

---

## The REPL Interface

agentx uses an interactive command loop. Each line you enter is parsed as a command with optional arguments:

```
(agent-x) > command arg1 arg2
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

The `chat` command is the primary way to interact with LLMs. It supports model selection and interactive conversations:

```
(agent-x) > chat [query]
(agent-x) > chat --model <model_name> [query]
```

**Features:**
- Single-query chat: `chat What is Python?`
- Model selection: `chat --model gpt-4 Explain quantum computing`
- Interactive mode: `chat` (then conversation loop)
- The `--model` flag can appear anywhere in the command
- When multiple `--model` flags are given, the last one wins

**Streaming Metrics:** After each response, agentx displays performance metrics:

```
150 tokens in 3.2s (46.9 tok/s)
```

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

### Session State with Petri Nets

agentx uses **Petri Nets** to formally model and track the semantic state of user queries throughout a session. This provides:

- **Formal State Tracking**: Mathematically rigorous session progression
- **Semantic Representation**: User intent captured as network structure
- **Verifiable Properties**: Provable boundedness, liveness, and deadlock-freedom
- **Progress Visualization**: Clear view of workflow completion status

**Example**: A query like *"I want to analyze the project structure"* creates a Petri Net where tokens flow through semantic states:

```
[analysis_pending] → [understanding_layout] → [identifying_components] → [analysis_completed]
```

The system automatically:
1. Extracts the objective from your query
2. Classifies the task type (analysis, debug, implementation, etc.)
3. Generates an appropriate workflow template
4. Tracks progress through token movement

This enables the agent to maintain context, show progress, and resume sessions from saved states. For detailed technical documentation, see `.meta/doc/petri-nets-for-session-state.md`.

---

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

## Architecture Overview

```
main.py
└── create_controller()
    └── MainController
        └── ReplApp(controller).run()
            ├── Session management
            ├── Command parsing & execution
            └── Exit on quit / Ctrl+C / Ctrl+D
```

### Design Patterns

- **Command Pattern**: Every REPL command implements a consistent `run()` interface
- **Strategy Pattern**: LLM providers (OpenRouter, OpenAI, Google Gemini, Ollama) are interchangeable
- **Session Pattern**: Isolated command history per session with SQLite persistence
- **Petri Net Pattern**: Formal semantic state tracking for user query workflows

---

## Development with Meta Harness

agentx uses the **Meta Harness** - a structured development system optimized for AI-assisted development.

### Key Directories

| Directory | Purpose |
|-----------|---------|
| `.meta/project_development/` | Rules, standards, workflows |
| `.meta/sandbox/` | Safe workspace for code modifications |
| `.meta/tests_sandbox/` | TDD workspace |
| `.meta/experiments/` | Experimental features |
| `.meta/development_tools/` | Development utilities |
| `.meta/knowledge_base/` | Knowledge storage |

### For AI Agents

1. Read `AGENTS.md` first - it contains mandatory rules
2. Review `META_HARNESS.md` for complete documentation
3. Always work in safe spaces (`.meta/sandbox/`, `.meta/experiments/`)
4. Follow TDD in `.meta/tests_sandbox/`
5. Never modify production code directly

### For Human Developers

- **Getting Started**: See `META_HARNESS.md`
- **Quick Reference**: `.meta/project_development/QUICK_REFERENCE.md`
- **Standards**: `.meta/project_development/` directory

---

## License

Apache 2.0 - Educational and experimental purposes.
