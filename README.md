# agentx

> **Version**: 0.2.0  
> **Python**: 3.14+  
> **Package Manager**: uv  
> **License**: Apache 2.0 (Educational & Enterprise Use)

---

## What is agentx?

**agentx** is a Python-based LLM agent framework with a modern **Textual TUI** and **console REPL** interface, created strictly for educational purposes. It lets you interact with language models through chat, web search, PDF Q&A, function calling, and graph-based reasoning workflows.

```text
┌─ AgentX TUI ─────────────────────────────────────────────────┐
│  Welcome to AgentX TUI                                       │
│  Press 'c' Chat, 'r' RAG, 'f' Fast Agent, 'a' Advanced Agent │
│  Press 't' ReAct, 'd' Coding, 'm' Models, 'h' Help, 'q' Quit │
│                                                              │
│  [c] Chat  ──→ LLM conversations with streaming responses    │
│  [r] RAG   ──→ PDF Q&A, document ingestion, vector search    │
│  [f] Fast Agent ──→ Modal-dialog-driven agent (simplified)   │
│  [a] Advanced Agent ──→ Full agent workspace (tools, policy) │
│  [t] ReAct  ──→ Reasoning + Acting with visible thinking     │
│  [d] Coding ──→ File system tools (search, read, edit, create)│
│  [m] Models ──→ Select AI model provider                     │
│  [h] Help  ──→ Command reference                             │
│  [q] Quit  ──→ Exit application                              │
└──────────────────────────────────────────────────────────────┘
```


**Key Features:**
- 🎨 **Modern TUI** - Textual-based interface with keyboard navigation
- 💬 **AI Chat** - Multi-provider LLM support (OpenRouter, OpenAI, Google Gemini, NVIDIA NIM, Ollama, LlamaCpp)
- 📚 **RAG** - PDF Q&A, web ingestion, Chroma/FAISS/Pinecone vector stores
- 🤖 **Intelligent Agent** - Autonomous perceive→decide→act→reflect cycle with tool registry, policy DSL engine, and self-improvement loop
- 🧠 **Petri Net Sessions** - Graph-based session/user objective management
- 🔌 **LangChain/LangGraph** - Full integration for agentic workflows
- 🧪 **879+ Tests** - Comprehensive unit + integration + automated TUI tests

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

You'll see the TUI interface. Press `c` for chat, `r` for RAG, `m` for models, `q` to quit.

---

## 🎨 Features

### Modern TUI (Textual Interface)

**Default mode** - A beautiful, keyboard-driven terminal UI:

```text
┌─ AgentX TUI ────────────────────────────────────────────────┐
│  agentx 0.2.0                                               │
│  Session: session_2026-06-27_18-30-00                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Welcome to AgentX!                                         │
│                                                             │
│  Press:                                                     │
│    [c] Chat  ──→ Start AI conversation                      │
│    [r] RAG   ──→ Document Q&A and ingestion                 │
│    [f] Fast Agent ──→ Simple modal agent                    │
│    [a] Advanced Agent ──→ Full agent workspace              │
│    [t] ReAct  ──→ Reasoning + Acting with visible thinking  │
│    [d] Coding ──→ File system tools (search, read, edit)    │
│    [m] Models ──→ Select AI model provider                  │
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
| `f` | Open Fast Agent (modal-dialog-driven) |
| `a` | Open Advanced Agent screen |
| `t` | Open ReAct screen (reasoning + acting) |
| `d` | Open Coding screen (file system tools) |
| `m` | Open Models screen (select AI model provider) |
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
| Google Gemini | Gemini Pro | `GOOGLE_API_KEY` |
| NVIDIA NIM | Nemotron, Llama models | `NVIDIA_API_KEY` |
| Ollama | Local models | `OLLAMA_HOST` |
| LlamaCpp | Local GGUF models | Manual config |

Use the **Models screen** (press `m` from the main TUI) to select the active provider at runtime. The selection is persisted to `~/.agentx/model_selection.json` and used across chat, RAG, and agent features.

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

### 🤖 Intelligent Agent (feature_007)

An autonomous agent subsystem that runs a **perceive → decide → act → reflect → persist** cycle, with a tool registry, a policy DSL engine, and a reflection/self-improvement loop.

**Agent Cycle:**
```text
         ┌──────────┐
         │ perceive │ ← sensors read environment + tool readings
         └────┬─────┘
              ▼
         ┌──────────┐
         │ decide   │ ← policy engine evaluates rules → action
         └────┬─────┘
              ▼
         ┌──────────┐
         │ act      │ ← actuator executes tool command
         └────┬─────┘
              ▼
         ┌──────────┐
         │ reflect  │ ← AI critiques trace → proposals (safety-checked)
         └────┬─────┘
              ▼
         ┌──────────┐
         │ persist  │ ← snapshot to SQLite (memory, goals, policies, reflection log)
         └──────────┘
```

**Core Subsystems:**

| Subsystem | Purpose |
|-----------|---------|
| **Tool Registry** | `ISensor`/`IActuator` interfaces, `ToolSpec` schema, discovery, and built-in tools (FileSystem, RAG query, Session) |
| **Policy Engine** | Condition DSL (tokenizer → AST → visitor), priority resolution, conflict detection, adaptation hooks |
| **Reflection Engine** | Critique parser, safety evaluator (deny-list), proposal router, approval flow |
| **Goal Manager** | Hierarchical goal trees with success criteria and status tracking |
| **Memory Manager** | Volatile + persistent memory with metadata and source tracking |
| **Persistence** | stdlib `sqlite3` (no ORM, no Alembic) — schema, agent DB, and repositories |

**Advanced Agent Screen (TUI):**

Press `a` from the main screen to open the full-featured agent workspace:

| Key / Command | Action |
|---------------|--------|
| `r` / `run` | Run one agent cycle |
| `s` / `save` | Save session snapshot |
| `d` / `demo [a\|b]` | Open the demo screen |
| `goal <desc>` | Submit a new goal |
| `rule <cond> \| <action> <json>` | Add a policy rule |
| `status` / `goals` / `rules` / `memory` | Inspect agent state |
| `proposals` / `approve <id> <idx>` | View and approve reflection proposals |

**Self-Improvement Loop:**

The reflection engine critiques each cycle's trace and may propose changes (new policy rules, goal adjustments, tool enablement). Proposals are safety-evaluated and held as **pending** until approved via the `approve` command — closing the self-improvement loop without uncontrolled autonomy.

---

### ⚡ Fast Agent (feature_011)

A streamlined, modal-dialog-driven agent UX for quick tasks. Press `f` from the main screen:

```text
┌─ Fast Agent ────────────────────────────────────────────────┐
│  ⚡ Goal: What do you want the agent to do?                  │
│  [Advanced ▸] (optional constraints)                        │
│  [ Start ]  [ Cancel ]                                      │
└─────────────────────────────────────────────────────────────┘
      ↓
┌─ Running ───────────────────────────────────────────────────┐
│  Cycle 3 · DECIDING · tool: filesystem · read file.py       │
│  [ Pause] [ Stop]                                           │
└─────────────────────────────────────────────────────────────┘
      ↓ (on self-improvement proposal)
┌─ Reflection ────────────────────────────────────────────────┐
│  ▸ Proposal: Add rule "skip /tmp"                           │
│     because: caught noisy readings                          │
│  [✓ Approve] [✕ Dismiss] [⏹ Stop]                           │
└─────────────────────────────────────────────────────────────┘
      ↓
┌─ Result ────────────────────────────────────────────────────┐
│  ✓ Goal achieved in 4 cycles                                │
│  [💾 Save session]  [⚡ New goal]  [← Back to menu]          │
└─────────────────────────────────────────────────────────────┘
```

**Key Differences from Advanced Agent:**

| Aspect | Fast Agent (`f`) | Advanced Agent (`a`) |
|--------|------------------|---------------------|
| Goal input | Single natural-language prompt | Hierarchical goal tree editor |
| Policy rules | Hidden (auto/off) | Full DSL editor |
| Cycle execution | Auto-run (call_after_refresh) | Manual `r` key / `run` command |
| Proposals | Modal interrupt (Approve/Dismiss/Stop) | `proposals` / `approve` commands |
| Goal completion | Manual (Stop when done) | Auto via SuccessCriteria |
| Best for | Quick one-shot tasks | Complex multi-goal workflows |

The Fast Agent reuses the same `Agent` facade + `AgentController` under the hood — zero Model-layer changes. It's the first use of `textual.screen.ModalScreen` in the codebase.

---

### 🎛️ Models Screen (feature_013)

A runtime AI model provider selector accessible from the main TUI screen (press `m`):

```text
┌─ Models ────────────────────────────────────────────────────┐
│  Select your AI model provider:                             │
│                                                             │
│  ● OpenRouter (cloud)     — 100+ models, auto-routing       │
│    OpenAI (cloud)         — GPT-4, GPT-3.5                  │
│    Google Gemini (cloud)  — Gemini Pro                      │
│    NVIDIA NIM (cloud)     — Nemotron, Llama                 │
│    Ollama (local)         — Local models                    │
│    LlamaCpp (local)       — Local GGUF models               │
│                                                             │
│  [Enter] Select  [Esc/b] Back                               │
└─────────────────────────────────────────────────────────────┘
```

The selected provider is persisted to `~/.agentx/model_selection.json` and used across all features (chat, RAG, agent, ReAct). The registry uses a unified `LLMProvider` ABC with lazy imports — adding a new provider is a single class + one catalog entry.

---

### 🧠 ReAct Screen (feature_018)

A new **Reasoning + Acting** chat screen that uses LangChain's `create_agent` (ReAct pattern) to show the agent's **thinking process**, **tool calls**, and **streaming answers** in real-time.

```text
┌─ ReAct ──────────────────────────────────────────────────────┐
│  Ask me anything — I'll show my reasoning!                   │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  You: What is 15% of 240?                                    │
│                                                              │
│  💭 The user wants 15% of 240. I can calculate this          │
│     with the calculator tool.                                │
│                                                              │
│  🔧 calculator(expression="240*0.15")                        │
│                                                              │
│  📊 36.0                                                     │
│                                                              │
│  💭 The calculator returned 36.0. 15% of 240 is 36.          │
│                                                              │
│  Assistant: 15% of 240 is 36.                                │
│                                                              │
│  > _                                                         │
└──────────────────────────────────────────────────────────────┘
```

**Key Features:**
- 💭 **Thinking** — Visible chain-of-thought reasoning from the agent
- 🔧 **Tool calls** — See which tools the agent uses and with what arguments
- 📊 **Tool results** — Tool outputs displayed inline
- 💬 **Streaming answers** — Final response streams token-by-token
- 🧠 **Context preservation** — Multi-turn conversations via LangGraph checkpointer
- 🛑 **Non-blocking UI** — Agent runs on background thread; `Esc`/`q` always responsive

**Built-in Tools:**
| Tool | Description |
|------|-------------|
| `calculator` | Safe math evaluation (AST-based, no `eval`) |
| `get_current_time` | Returns current ISO 8601 timestamp |

**Architecture:**
- **Model**: `ReactAgentService` wraps `langchain.agents.create_agent` with `InMemorySaver` checkpointer
- **Controller**: `ReactController` implements `IReactViewPartner`; spawns daemon worker thread for agent streaming
- **View**: `ReactTUIScreen` extends `BaseAgentXScreen`; displays thinking/tool/answer blocks with distinct styling
- **Integration**: Added `t` binding + 🧠 ReAct button to Main screen; MenuGrid expanded to 3×3 (7 buttons)

**Key Bindings:**
| Key | Action |
|-----|--------|
| `t` | Open ReAct screen |
| `Ctrl+Enter` | Send message |
| `Esc` / `q` | Return to Main (cancels running agent) |

---
 
### 💻 Coding Agent Screen (feature_019)
 
A new **Coding Agent** chat screen that uses LangChain's `create_agent` with file system tools to search, read, edit, list, and create files in your workspace — with visible thinking, tool calls, and diff highlighting.
 
```text
┌─ Coding ───────────────────────────────────────────────────────┐
│  Ask me to explore, edit, or create files!                     │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  You: Find all Python files in the src/ directory              │
│                                                                │
│  💭 The user wants to find Python files. I'll use file_search. │
│                                                                │
│  🔧 file_search(pattern="src/**/*.py")                         │
│                                                                │
│  📊 Found 3 files: src/main.py, src/utils.py, src/test.py      │
│                                                                │
│  💭 Let me read main.py to understand the structure.           │
│                                                                │
│  🔧 file_read(path="src/main.py")                              │
│                                                                │
│  📊 def main():\n    print('Hello from main')\n                │
│                                                                │
│  💭 Now I'll add a new function to utils.py.                   │
│                                                                │
│  🔧 file_edit(path="src/utils.py", old_str="def helper():",    │
│               new_str="def helper():\n    return 42\n\n\ndef new_func():") │
│                                                                │
│  📊 --- a/src/utils.py\n+++ b/src/utils.py\n@@ -1,2 +1,5 @@\n │
│   def helper():\n+    return 42\n+\n+def new_func():            │
│                                                                │
│  Assistant: Found 3 Python files. Read main.py and added       │
│  new_func() to utils.py.                                       │
│                                                                │
│  > _                                                           │
└────────────────────────────────────────────────────────────────┘
```
 
**Key Features:**
- 💭 **Thinking** — Visible chain-of-thought reasoning from the agent
- 🔧 **Tool calls** — See which file tools the agent uses with arguments
- 📊 **Tool results** — Tool outputs displayed inline with diff highlighting for edits
- 💬 **Streaming answers** — Final response streams token-by-token
- 🧠 **Context preservation** — Multi-turn conversations via LangGraph checkpointer
- 🛑 **Non-blocking UI** — Agent runs on background thread; `Esc`/`q` always responsive
- 🔒 **Sandbox-rooted** — All file operations confined to session working directory
 
**Built-in Tools:**
| Tool | Description |
|------|-------------|
| `file_search` | Glob pattern file search within sandbox |
| `file_read` | Read file with optional line range |
| `file_edit` | Precise edit (old_str must match exactly once) |
| `file_list` | List directory contents (recursive optional) |
| `file_create` | Create new file with content |
 
**Architecture:**
- **Model**: `CodingAgentService` wraps `langchain.agents.create_agent` with 5 file tools + `InMemorySaver` checkpointer
- **Controller**: `CodingController` implements `ICodingViewPartner`; spawns daemon worker thread for agent streaming
- **View**: `CodingTUIScreen` extends `BaseAgentXScreen`; displays thinking/tool/answer blocks with diff highlighting
- **Integration**: Added `d` binding + 💻 Coding button to Main screen; MenuGrid updated to 8 buttons
 
**Key Bindings:**
| Key | Action |
|-----|--------|
| `d` | Open Coding screen |
| `Ctrl+Enter` | Send message |
| `Ctrl+N` | New conversation |
| `Esc` / `q` | Return to Main (cancels running agent) |
 
---
 
### 🎬 Agent Demo (feature_010)

Built-in demo scenarios that seed the agent sandbox with files, goals, and policies — perfect for exploring the agent cycle without configuration.

```text
┌─ Agent Demo ────────────────────────────────────────────────┐
│  [Run]    Run the seeded scenario cycle                     │
│  [Reset]  Clear state and re-seed                           │
│  [Back]   Return to agent screen                            │
└─────────────────────────────────────────────────────────────┘
```

Two scenarios are available (`demo a` / `demo b`), each with pre-configured goals, policy rules, and sandbox files.

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

# For NVIDIA NIM models
NVIDIA_API_KEY=your_key_here

# For Ollama (local models)
OLLAMA_HOST=http://localhost:11434
```

**Get API Keys:**
- OpenRouter: https://openrouter.ai/keys
- Tavily: https://app.tavily.com/
- OpenAI: https://platform.openai.com/api-keys
- Google: https://makersuite.google.com/app/apikey
- NVIDIA: https://build.nvidia.com/

If `OPENROUTER_API_KEY` is not set, the application will prompt for it on startup.

---

## 🎮 Usage

### Starting the Application

```bash
uv run main.py
```

**TUI Mode (default):**
```text
🎨 Starting modern TUI... (press 'q' to quit, 'h' for help)

agentx 0.2.0

┌─ AgentX TUI ────────────────────────────────────────────────┐
│  Welcome to AgentX TUI                                      │
│  Press 'c' Chat, 'r' RAG, 'f' Fast Agent, 'a' Advanced Agent│
│  Press 'm' for Models, 'h' for help, 'q' to quit            │
└─────────────────────────────────────────────────────────────┘
```

**Console Mode (fallback or `--no-tui`):**
```bash
uv run main.py --no-tui
```
```text
💻 Using console mode...

agentx 0.2.0

(agentx) > 
```

### TUI Navigation

| Key | Action |
|-----|--------|
| `c` | Open Chat screen |
| `r` | Open RAG screen |
| `f` | Open Fast Agent (modal-dialog-driven) |
| `a` | Open Advanced Agent screen |
| `m` | Open Models screen (select AI provider) |
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
agentx 0.2.0
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
│  AgentController, SessionController, ToolController         │
│  Implements: IMainViewPartner, IRagViewPartner,             │
│              IAgentViewPartner, IAgentModelPartner, ...     │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Uses (ABC interfaces)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    INTERFACE LAYER                          │
│  IMainView, IRagView, IChatView, IAgentViewPartner          │
│  IUIProvider, IAgentModelPartner, IToolRegistryPartner      │
│  IMemoryStorePartner, IPolicyStorePartner, IGoalManager     │
│  ISafetyEvaluator, IAIServicePartner (ABCs)                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Implemented By
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  VIEW LAYER                                                 │
│  Console: MainView, RagView, ChatView, AgentView            │
│  TUI:     BaseAgentXScreen framework, ModalScreen,          │
│           AgentTUIScreen, AgentDemoScreen, ModelsScreen     │
│           BlockingTaskRunner (non-blocking daemon thread)   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Depends On
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    MODEL LAYER                              │
│  model/ai/       — LLM providers (OpenAI, Ollama, etc.)     │
│  model/rag/      — RAG orchestration, vector stores         │
│  model/session/  — Session management, SQLite persistence   │
│  agent/          — Intelligent agent subsystem              │
│    ├─ model/agent.py     — Agent facade (cycle orchestrator)│
│    ├─ model/tools/       — Tool registry + built-in tools   │
│    ├─ model/policy/      — Policy DSL engine + conflict     │
│    ├─ model/reflection/  — Critique, safety, proposal router│
│    ├─ model/goal/        — Goal tree manager                │
│    ├─ model/memory/      — Volatile + persistent memory     │
│    ├─ persistence/       — stdlib sqlite3 (no ORM)          │
│    └─ demo/              — Seeded demo scenarios            │
└─────────────────────────────────────────────────────────────┘
```

**Key Design Patterns:**
- **Abstract Partner**: View↔Controller communication via ABCs
- **Command Pattern**: Main screen input dispatch
- **Provider Pattern**: Runtime UI selection (TUI vs Console)
- **Facade Pattern**: `Agent` class orchestrates all agent subsystems
- **Data Provider (DP)**: SQL encapsulation in `*_db.py` classes

**Layer Rules:**
- ✅ Model has NO imports from `ui`
- ✅ View has NO business logic
- ✅ Controller has NO rendering code
- ✅ SQL only in `DP_*` / `*_db.py` classes

---

## 🧪 Testing

agentx includes **879+ comprehensive tests** covering all core modules:

```bash
# Run all tests
uv run pytest tests/ -v

# Run model tests
uv run pytest tests/model/ -v

# Run agent subsystem tests
uv run pytest tests/features/feature_007.agentx_intelligent_agent_behaviour/ -v

# Run TUI automated tests
uv run pytest tests/tui/ -v

# Run MVC++ architecture check
uv run scripts/omt/mvc_check.py

# Run TDD enforcement status check
uv run scripts/omt/tdd_check.py status

# Run with coverage (if pytest-cov installed)
uv run pytest tests/ --cov=agentx --cov-report=html
```

**Test Coverage:**
- ✅ Petri nets & session management
- ✅ Commands & controllers
- ✅ Views & adapters (console + TUI)
- ✅ AI services & RAG orchestration
- ✅ Agent tool registry (sensors, actuators, discovery)
- ✅ Policy DSL engine (parsing, evaluation, conflict detection)
- ✅ Reflection engine (critique, safety, proposal routing)
- ✅ Goal manager & memory manager
- ✅ Agent persistence (stdlib sqlite3 repositories)
- ✅ Agent facade cycle (perceive→decide→act→reflect→persist)
- ✅ Demo scenarios & Textual pilot e2e tests
- ✅ TDD enforcement engine (AST analysis, two-hats gate, coverage gap detection)

**Characteristics:**
- **Isolation**: All tests are isolated with mocking (no external dependencies)
- **TUI Tests**: Automated end-to-end tests using Textual Pilot
- **MVC++ Compliant**: 0 errors, 0 warnings on agent module
- **Fast**: Full suite runs in seconds

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
| `omt_complete` | Verify phase artifacts + advance to next phase |
| `omt_testlist` | Record TDD test list (behaviors to implement) |
| `omt_red` | Declare a failing test (TDD Red — test hat) |
| `omt_green` | Declare a passing test (TDD Green — code hat) |
| `omt_refactor` | Declare refactor state (TDD Refactor — code hat) |
| `omt_done` | Declare TDD completion (runs full suite + checklist) |
| `uv run scripts/omt/mvc_check.py` | MVC++ architecture linter (guide §16) |
| `uv run scripts/omt/tdd_check.py` | TDD enforcement engine (9 subcommands) |
| `uv run scripts/omt/new_feature.py "<name>"` | Scaffold a feature's artifacts from `.meta/templates/` |

#### TDD Enforcement (feature_016)

For `major_feature` and `new_screen` tasks, the gate automatically activates **TDD mode** — a Kent Beck-style Red → Green → Refactor cycle enforced mechanically:

```text
  ┌──────────────┐     ┌──────────────┐     ┌─────────────────┐
  │  TESTLIST    │ →   │  RED (test)  │ →   │  GREEN (code)   │
  │  behaviors   │     │  write test  │     │  write code     │
  │  to implement│     │  that FAILS  │     │  to make it PASS│
  └──────────────┘     └──────────────┘     └─────────────────┘
                                                  │
                                                  ▼
                                         ┌──────────────────┐
                                         │  REFACTOR        │
                                         │  improve code    │
                                         │  tests stay GREEN│
                                         └──────────────────┘
                                                  │
                                                  ▼
                                         ┌─────────────────┐
                                         │  DONE           │
                                         │  full suite +   │
                                         │  checklist pass │
                                         └─────────────────┘
```

**Two-Hats Gate:** The enforcer tracks which "hat" you're wearing:
- **RED state** → only `tests/` edits are allowed (you write the failing test)
- **GREEN / REFACTOR state** → only `src/` edits are allowed (you write/refactor the code)
- If you try to edit the wrong layer, the gate blocks you with a message telling you which hat to switch to

**REFACTOR Revert:** If a refactor edit breaks tests, the gate automatically reverts the file to its pre-edit state and blocks the edit — you can't accidentally introduce a regression during refactoring.

**Phase-Exit Validation:** `omt_complete` runs `tdd_check.py validate-exit` which checks for:
- Dangling RED cycles (tests declared RED but never turned GREEN)
- Coverage gaps (public methods with no test coverage)

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
- ✅ **feature_004**: Modern TUI with Textual
- ✅ **feature_005**: File system agentic tools
- ✅ **feature_006**: opencode process enforcement (OMT++ gate, MVC++ linter)
- ✅ **feature_007**: Intelligent agent behaviour (tools, policy DSL, reflection, self-improvement)
- ✅ **feature_010**: Agent demo screen (seeded scenarios A & B)
- ✅ **feature_011**: Fast Agent modal UX (Goal → Running → Reflection → Result)
- ✅ **feature_012**: TUI framework (reusable base-class library for all screens)
- ✅ **feature_013**: AI model provider selector (6 providers: OpenRouter, OpenAI, Gemini, NVIDIA, Ollama, LlamaCpp)
- ✅ **feature_014**: Non-blocking TUI runner (daemon thread + queue poll, no UI freeze)
- ✅ **feature_016**: TDD enforcement (Kent Beck Red→Green→Refactor cycle, two-hats gate, AST analysis)
- ✅ **feature_018**: ReAct chat screen (Reasoning + Acting with visible thinking, tool calls, streaming)
- ✅ **feature_019**: Coding Agent screen (File system tools: search, read, edit, list, create with diff highlighting)

### Pending
- 🔲 **feature_001**: Session/user objectives driven by Petri Nets
- 🔲 **feature_002**: RAG retrieval augmented generation

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
| `.meta/software_development_process/2.requirements/features/feature_007.agentx_intelligent_agent_behaviour/` | Agent feature analysis, design & test artifacts |
| `.meta/software_development_process/2.requirements/features/feature_016.tdd_enforcement/` | TDD enforcement feature artifacts |
| `AGENTS.md` | Enforcement rules for opencode agents |

---

## 🤝 Contributing

agentx is an educational project. Contributions are welcome!

**Development Workflow:**
1. Read `AGENTS.md` for agent behavior rules
2. Read `.meta/software_development_process/omt_agent_guide.md` for OMT++ methodology
3. Declare your phase with `omt_phase` before editing `src/`
4. For major features: follow TDD cycle (`omt_testlist` → `omt_red` → `omt_green` → `omt_refactor` → `omt_done`)
5. Run tests: `uv run pytest tests/ -v`
6. Run MVC++ check: `uv run scripts/omt/mvc_check.py`

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