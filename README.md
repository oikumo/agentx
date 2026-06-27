# agentx

> **Version**: 0.1.1  
> **Python**: 3.14+  
> **Package Manager**: uv  
> **License**: Apache 2.0 (Educational & Enterprise Use)

---

## What is agentx?

**agentx** is a Python-based LLM agent framework with a modern **Textual TUI** and **console REPL** interface, created strictly for educational purposes. It lets you interact with language models through chat, web search, PDF Q&A, function calling, and graph-based reasoning workflows.

```text
┌─ AgentX TUI ────────────────────────────────────────────────┐
│  Welcome to AgentX TUI                                      │
│  Press 'c' for Chat, 'r' for RAG, 'q' to quit               │
│                                                             │
│  [c] Chat  ──→ LLM conversations with streaming responses   │
│  [r] RAG   ──→ PDF Q&A, document ingestion, vector search   │
│  [h] Help  ──→ Command reference                            │
│  [q] Quit  ──→ Exit application                             │
└─────────────────────────────────────────────────────────────┘
```

```
**Key Features:**
- 🎨 **Modern TUI** - Textual-based interface with keyboard navigation
- 💬 **AI Chat** - Multi-provider LLM support (OpenRouter, OpenAI, Ollama, Google GenAI)
- 📚 **RAG** - PDF Q&A, web ingestion, Chroma/FAISS/Pinecone vector stores
- 🧠 **Petri Net Sessions** - Graph-based session/user objective management
- 🔌 **LangChain/LangGraph** - Full integration for agentic workflows
- 🧪 **205+ Tests** - Comprehensive unit + automated TUI tests

Developed with **opencode** using **OMT++ methodology** (Analysis → Design → Programming → Testing with visible artifacts).

---

## ⚡ Quick Start

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and run
git clone <repository-url>
cd agentx
uv sync
uv run main.py
```

You'll see the TUI interface. Press `c` for chat, `r` for RAG, `q` to quit.

---

## 🎨 Features

### Modern TUI (Textual Interface)

**Default mode** - A beautiful, keyboard-driven terminal UI:

```text
┌─ AgentX TUI ────────────────────────────────────────────────┐
│  agentx 0.1.1                                               │
│  Session: session_2026-06-27_18-30-00                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Welcome to AgentX!                                         │
│                                                             │
│  Press:                                                     │
│    [c] Chat  ──→ Start AI conversation                      │
│    [r] RAG   ──→ Document Q&A and ingestion                 │
│    [h] Help  ──→ View all commands                          │
│    [q] Quit  ──→ Exit application                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Key Bindings:**
| Key | Action |
|-----|--------|
| `c` | Open Chat screen |
| `r` | Open RAG screen |
| `h` | Show help |
| `q` | Quit application |
| `Esc` | Go back / Close screen |

**Chat Screen:**
```text
┌─ Chat ──────────────────────────────────────────────────────┐
│  Type your message (streaming responses enabled)            │
├─────────────────────────────────────────────────────────────┤
│  You: What is a Petri net?                                  │
│                                                             │
│  Assistant: A Petri net is a mathematical modeling...       │
│             (streaming in real-time)                        │
│                                                             │
│  > _                                                        │
└─────────────────────────────────────────────────────────────┘
```

**RAG Screen:**
```text
┌─ RAG (Retrieval Augmented Generation) ──────────────────────┐
│  Repositories:                                              │
│    > my-pdf-docs/                                           │
│      langchain-docs/                                        │
├─────────────────────────────────────────────────────────────┤
│  [n] New repo  [s] Select  [i] Ingest URL  [q] Back         │
└─────────────────────────────────────────────────────────────┘
```

---

### 💬 AI Chat

Multi-provider LLM support with streaming responses:

**Supported Providers:**
| Provider | Models | Config |
|----------|--------|--------|
| OpenRouter | 100+ models (auto-routing) | `OPENROUTER_API_KEY` |
| OpenAI | GPT-4, GPT-3.5 | `OPENAI_API_KEY` |
| Google GenAI | Gemini Pro | `GOOGLE_API_KEY` |
| Ollama | Local models | `OLLAMA_HOST` |
| LlamaCpp | Local GGUF models | Manual config |

**Example Conversation:**
```text
(agentx) > chat

Welcome to Chat! Type your message or 'quit' to exit.

You: Explain dependency injection in Python

Assistant: Dependency Injection (DI) is a design pattern where...
           [streaming response continues]

You: Can you show an example?

Assistant: Sure! Here's a simple example using constructor injection:

           class Database:
               def query(self): ...
           
           class UserService:
               def __init__(self, db: Database):
                   self.db = db  # ← injected dependency

You: quit
(agentx) > 
```

---

### 📚 RAG (Retrieval Augmented Generation)

Ask questions about your documents, PDFs, and web pages using vector search.

**RAG Workflow:**
```text
1. Create Repository
   └─→ (agentx) > rag
       └─→ [n] New repository: "my-docs"

2. Ingest Documents
   └─→ [i] Ingest URL: https://example.com/guide.pdf
       └─→ Fetch → Parse (PyPDF) → Chunk → Embed → Store (Chroma)

3. Chat with Repository
   └─→ [c] Chat: "What does the guide say about authentication?"
       └─→ Query vector DB → Inject context → LLM response
```

**Supported Vector Stores:**
- Chroma (default)
- FAISS (CPU)
- Pinecone (cloud)

**Ingestion Sources:**
- PDF files (PyPDF)
- Web URLs (Tavily search)
- Local documents

---

### 🧠 Session Management (Petri Net Driven)

**feature_001**: Session and user objectives are modeled using **Petri nets** for graph-based state management.

**Session Lifecycle:**
```text
┌──────────────┐
│  NO SESSION  │
└──────┬───────┘
       │ new [name]
       ▼
┌──────────────┐
│  CREATING    │ → Creates timestamped directory
│              │ → Initializes SQLite database
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   ACTIVE     │ → Commands recorded to session.db
│              │ → RAG repos stored in rag/
└──────┬───────┘
       │
       └─→ new [name] → Switch to new session
```

**Persistence:**
```text
local_sessions/
└── 2026-06-27_18-30-00_my-session/
    ├── session.db          # SQLite: command history
    └── rag/
        └── my-pdf-docs/
            ├── db/         # Chroma vector store
            └── docs/       # Ingested PDFs
```

---

### 🔌 LangChain & LangGraph Integration

Full integration with the LangChain ecosystem:

- **LangChain** (1.3.10): Chains, prompts, output parsers
- **LangGraph** (1.2.6): Graph-based agentic workflows
- **LangChain Experimental**: Advanced features
- **Integrations**: Community, OpenAI, Tavily, Pinecone, Chroma

**Example Agentic Workflow:**
```python
# Future feature: Custom agent graphs
from langgraph.graph import StateGraph

# Define your agent's state machine
# Coming in future releases
```

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

## 🚀 Getting Started

### Prerequisites

- Python 3.14 or later
- `uv` package manager
- At least one API key (OpenRouter recommended for beginners)

### Installation

#### Option 1: Direct Usage (Global Install)

```bash
# Clone the repository
git clone <repository-url>

# Install globally with uv
uv tool install --editable agentx

# Run from anywhere
agentx
```

**Uninstall:**
```bash
uv tool uninstall agentx
```

#### Option 2: Development Mode

```bash
# Clone the repository
git clone <repository-url>
cd agentx

# Install with development dependencies
uv sync

# Run with uv
uv run main.py
```

---

## ⚙️ Configuration

### API Keys

agentx requires at least an **OpenRouter API key** to run the default chat agent. Other features may need additional keys.

Create a `.env` file in the project root:

```env
# Required for default chat
OPENROUTER_API_KEY=your_key_here

# For web search agents
TAVILY_API_KEY=your_key_here

# For OpenAI models
OPENAI_API_KEY=your_key_here

# For Google Gemini
GOOGLE_API_KEY=your_key_here

# For Ollama (local models)
OLLAMA_HOST=http://localhost:11434
```

**Get API Keys:**
- OpenRouter: https://openrouter.ai/keys
- Tavily: https://app.tavily.com/
- OpenAI: https://platform.openai.com/api-keys
- Google: https://makersuite.google.com/app/apikey

If `OPENROUTER_API_KEY` is not set, the application will prompt for it on startup.

---

## 🎮 Usage

### Starting the Application

```bash
uv run main.py
```

**TUI Mode (default):**
```text
🎨 Starting modern TUI... (press \'q\' to quit, \'h\' for help)

agentx 0.1.1

┌─ AgentX TUI ────────────────────────────────────────────────┐
│  Welcome to AgentX TUI                                      │
│  Press 'c' for Chat, 'r' for RAG, 'q' to quit               │
└─────────────────────────────────────────────────────────────┘
```

**Console Mode (fallback or `--no-tui`):**
```bash
uv run main.py --no-tui
```
```text
💻 Using console mode...

agentx 0.1.1

(agentx) > 
```

### TUI Navigation

| Key | Action |
|-----|--------|
| `c` | Open Chat screen |
| `r` | Open RAG screen |
| `h` | Show help/commands |
| `q` | Quit application |
| `Esc` | Go back to previous screen |
| `Tab` | Switch focus (where applicable) |
| `Enter` | Activate selected button |

### Console Commands Reference

#### Utility Commands

| Command | Usage | Description |
|---------|-------|-------------|
| `help` | `help` | Lists all available commands |
| `quit` | `quit` | Exits the application |
| `clear` | `clear` | Clears the terminal screen |
| `history` | `history` | Shows command history for current session |
| `sum` | `sum <a> <b>` | Adds two integers (demo command) |
| `new` | `new [name]` | Creates a new session |
| `version` | `version` | Shows application version |

**Examples:**
```text
(agentx) > help
(agentx) > sum 42 58
100
(agentx) > new my-session
(agentx) > history
(agentx) > version
agentx 0.1.1
(agentx) > quit
```

#### AI Chat Command

```text
(agentx) > chat
Welcome to Chat! Type your message or 'quit' to exit.

You: Hello, can you help me with Python?
Assistant: Of course! I'd be happy to help you with Python...

You: quit
(agentx) > 
```

#### RAG Command

```text
(agentx) > rag

RAG Menu:
  [n] Create new repository
  [s] Select existing repository
  [q] Back to main menu

> n
Enter repository name: my-docs
Repository 'my-docs' created!

RAG Repository 'my-docs':
  [i] Ingest URL
  [c] Chat with repository
  [l] List documents
  [q] Back

> i
Enter URL to ingest: https://example.com/guide.pdf
Ingesting... Done! 15 pages, 42 chunks created.

> c
Ask your question: What does the guide say about authentication?
Based on the ingested documents, authentication is described as...
```

---

## 🏗️ Architecture

### MVC++ Pattern with Abstract Partners

agentx follows a strict **MVC++** (Model-View-Controller) architecture with dependency inversion through **Abstract Partner** interfaces:

```text
┌─────────────────────────────────────────────────────────────┐
│                      ENTRY POINT                            │
│  main.py — Bootstrap, provider selection, lifecycle         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   CONTROLLER LAYER                          │
│  MainController, RagController, ChatController              │
│  Implements: IMainViewPartner, IRagViewPartner, ...         │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Uses (ABC interfaces)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    INTERFACE LAYER                          │
│  IMainView, IRagView, IChatView, IUIProvider (ABCs)         │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Implemented By
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     VIEW LAYER                              │
│  Console: MainView, RagView, ChatView                       │
│  TUI:     TUIAdapter, TUIRagAdapter, TUIChatAdapter         │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Depends On
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    MODEL LAYER                              │
│  model/ai/     — LLM providers (OpenAI, Ollama, etc.)       │
│  model/rag/    — RAG orchestration, vector stores           │
│  model/session/ — Session management, SQLite persistence    │
└─────────────────────────────────────────────────────────────┘
```

**Key Design Patterns:**
- **Abstract Partner**: View↔Controller communication via ABCs
- **Command Pattern**: Main screen input dispatch
- **Provider Pattern**: Runtime UI selection (TUI vs Console)
- **Data Provider (DP)**: SQL encapsulation in `*_db.py` classes

**Layer Rules:**
- ✅ Model has NO imports from `ui`
- ✅ View has NO business logic
- ✅ Controller has NO rendering code
- ✅ SQL only in `DP_*` classes

---

## 🧪 Testing

agentx includes **205+ comprehensive unit tests** covering all core modules:

```bash
# Run all unit tests
uv run pytest tests/unit/ -v

# Run specific module
uv run pytest tests/unit/model/session/ -v

# Run TUI automated tests
uv run pytest tests_automated/tui/ -v

# Run with coverage (if pytest-cov installed)
uv run pytest tests/ --cov=agentx --cov-report=html
```

**Test Coverage:**
- ✅ Petri nets
- ✅ Session management
- ✅ Commands & controllers
- ✅ Views & adapters
- ✅ AI services
- ✅ RAG orchestration
- ✅ Utilities

**Characteristics:**
- **Isolation**: All tests are isolated with mocking (no external dependencies)
- **TUI Tests**: Automated end-to-end tests using Textual Pilot
- **Fast**: Full suite runs in seconds

**Documentation:** See `tests/unit/README.md` and `tests_automated/tui/README.md` for complete test documentation.

---

## 📖 opencode Process Enforcement

agentx development is driven by **opencode only** with a mechanically enforced **OMT++** (Object Modeling Technique++) process harness. This ensures every code change follows a structured Analysis → Design → Programming → Testing workflow with visible artifacts.

### How Enforcement Works

The enforcement lives in two layers:

| Layer | File | Purpose |
|-------|------|---------|
| **Coarse permissions** | `opencode.jsonc` | Declarative deny/allow rules (git commit, bare python, .env edits, etc.) |
| **Fine process gate** | `.opencode/plugin/omt_enforcer.ts` | Programmatic phase checking, MVC++ linting, artifact scaffolding |

#### The OMT++ Gate

Before editing any file under `src/`, you **must** declare your OMT++ phase using the `omt_phase` tool:

```text
omt_phase{ task_type: "bug_fix|minor_feature|major_feature|new_screen|refactor|test|docs", 
           phase: "Analysis|Design|Programming|Testing",
           scope: "one sentence: what 'done' looks like" }
```

This creates a ledger entry in `.meta/.omt/ledger.jsonl` and unlocks `src/` edits for the session.

#### Rigor Scales to Task Size

| task_type | Required Artifacts |
|-----------|-------------------|
| `bug_fix` / `minor_feature` / `refactor` | Phase declaration only |
| `major_feature` / `new_screen` | Phase declaration **+** design doc on disk (scaffold with `uv run scripts/omt/new_feature.py "<name>" --type major_feature`) |

#### Automatic Architecture Checks

After every `src/` edit and on session idle, the gate runs the MVC++ linter (`uv run scripts/omt/mvc_check.py`) which checks for:
- View ↔ Model layer leaks
- Non-ABC Abstract Partners
- SQL outside Data Provider classes
- God controllers (>300 lines)
- Controllers in `model/` directory

Violations surface as non-blocking toasts (guiding, not punishing).

#### Escape Hatch (Logged)

For genuine emergencies: `omt_skip{ reason: "...", scope: "src|tests|all" }`. Every skip is recorded in the ledger for audit.

#### Tooling

| Tool | Purpose |
|------|---------|
| `omt_phase` | Declare OMT++ phase; unlocks `src/` edits |
| `omt_skip` | Logged process-override escape hatch |
| `uv run scripts/omt/mvc_check.py` | MVC++ architecture linter (guide §16) |
| `uv run scripts/omt/new_feature.py "<name>"` | Scaffold feature artifacts from `.meta/templates/` |

#### References

- **OMT++ methodology**: `.meta/software_development_process/omt_agent_guide.md` (source of truth)
- **Process enforcement plan**: `.meta/software_development_process/2.requirements/features/feature_006.opencode_process_enforcement/plan/PLAN.md`
- **AGENTS.md**: Complete enforcement rules for opencode agents

---

## 🛠️ Troubleshooting

### "Unknown command" error
Check your spelling with `help`. Commands are case-sensitive.

### API key prompt on startup
Set `OPENROUTER_API_KEY` in your `.env` file to avoid the interactive prompt.

### TUI not showing / keyboard input not working
- Ensure you're running in a proper terminal (not piped input)
- Check TTY capability: `sys.stdin.isatty() and sys.stdout.isatty()`
- Use `--no-tui` flag to force console mode

### LLM connection errors
- Verify your API key is valid
- Check your internet connection
- For local models, ensure Ollama or LlamaCpp is properly configured

### RAG ingestion fails
- Check if URL is accessible
- Verify PDF is not password-protected
- Ensure vector store directory has write permissions

---

## 🗺️ Roadmap

### Completed Features
- ✅ **feature_003**: agentx process (OMT++ methodology)
- ✅ **feature_004**: Modern TUI with Textual
- ✅ **feature_005**: File system agentic tools
- ✅ **feature_006**: opencode process enforcement

### In Progress
- 🔄 **feature_001**: Session/user objectives driven by Petri Nets
- 🔄 **feature_002**: RAG retrieval augmented generation

### Future Features
- 🔮 Custom agent graphs with LangGraph
- 🔮 Multi-agent collaboration
- 🔮 Voice input/output
- 🔮 Web UI adapter
- 🔮 Plugin system for custom commands

---

## 📚 Documentation

For deep dives into architecture, design decisions, and development methodology:

| Document | Description |
|----------|-------------|
| `.meta/META.md` | Overview of all development artifacts |
| `.meta/software_development_process/omt_agent_guide.md` | Complete OMT++ methodology guide |
| `.meta/software_development_process/4.design/structure/STRUCTURE.md` | Architecture deep dive |
| `.meta/software_development_process/4.design/behavior/BEHAVIOR.md` | Runtime behavior specifications |
| `tests/unit/README.md` | Unit testing documentation |
| `tests_automated/tui/README.md` | TUI automated testing guide |

---

## 🤝 Contributing

agentx is an educational project. Contributions are welcome!

**Development Workflow:**
1. Read `AGENTS.md` for agent behavior rules
2. Read `.meta/software_development_process/omt_agent_guide.md` for OMT++ methodology
3. Declare your phase with `omt_phase` before editing `src/`
4. Run tests: `uv run pytest tests/ -v`
5. Run MVC++ check: `uv run scripts/omt/mvc_check.py`

**Note**: This project uses opencode for development. All code changes must follow the OMT++ process with visible artifacts.

---

## 📄 License

Apache 2.0 - Educational and experimental purposes.

**Free for everyone**, including enterprise users.

---

## 🙏 Acknowledgments

- Developed with assistance from [opencode](https://opencode.ai) coding agent
- Built on [LangChain](https://python.langchain.com/) ecosystem
- TUI powered by [Textual](https://textual.textualize.io/)
- Following [OMT++](https://example.com/omt) methodology

---

**Made for learning, experimentation, and exploration of LLM agent architectures.** 🚀