# agentx

> **Version**: 0.2.0  
> **Python**: 3.14+  
> **Package Manager**: uv  
> **License**: Apache 2.0 (Educational & Enterprise Use)

---

## What is agentx?

**agentx** is a Python-based LLM agent framework with a **console REPL** interface, created strictly for educational purposes. It lets you interact with language models through chat, web search, PDF Q&A, function calling, and graph-based reasoning workflows.

```text
┌─ AgentX Console ──────────────────────────────────────────────┐
│  Welcome to AgentX                                            │
│  Press 'c' Chat, 'r' RAG, 'f' Fast Agent, 'a' Advanced Agent  │
│  Press 't' ReAct, 'd' Coding, 'm' Models, 'h' Help, 'q' Quit  │
│                                                               │
│  [c] Chat  ──→ LLM conversations with streaming responses     │
│  [r] RAG   ──→ PDF Q&A, document ingestion, vector search     │
│  [f] Fast Agent ──→ Modal-dialog-driven agent (simplified)    │
│  [a] Advanced Agent ──→ Full agent workspace (tools, policy)  │
│  [t] ReAct  ──→ Reasoning + Acting with visible thinking      │
│  [d] Coding ──→ File system tools (search, read, edit, create)│
│  [m] Models ──→ Select AI model provider                      │
│  [h] Help  ──→ Command reference                              │
│  [q] Quit  ──→ Exit application                               │
└───────────────────────────────────────────────────────────────┘
```


**Key Features:**
- 🖥️ **Console REPL** - Keyboard-driven terminal interface
- 💬 **AI Chat** - Multi-provider LLM support (OpenRouter, OpenAI, Google Gemini, NVIDIA NIM, Ollama, LlamaCpp)
- 📚 **RAG** - PDF Q&A, web ingestion, Chroma/FAISS/Pinecone vector stores
- 🤖 **Intelligent Agent** - Autonomous perceive→decide→act→reflect cycle with tool registry, policy DSL engine, and self-improvement loop
- 🧠 **Petri Net Sessions** - Graph-based session/user objective management
- 🖥️ **Petri Net Studio** - A standalone browser-based Petri net workbench (`tools/petri-net-studio/`) with exact engine parity to the Python model, structural analysis (reachability/deadlocks/bounds/liveness), a reachability-graph explorer, and a full React Flow editor/simulator
- 🔌 **LangChain/LangGraph** - Full integration for agentic workflows
- 🧪 **2,300+ Tests** - Comprehensive unit + integration + automated tests (2085 pytest + 283 Vitest)

Developed with **opencode**.

---

## ⚡ Quick Start

### Prerequisites

- Python 3.14 or later
- `uv` package manager — install with `curl -LsSf https://astral.sh/uv/install.sh | sh`
- At least one API key (OpenRouter recommended — see Configuration below)

### Option 1: Development Mode (recommended)

```bash
git clone https://github.com/oikumo/agentx.git
cd agentx
uv sync
uv run agentx
```

### Option 2: Global Install (run from anywhere)

```bash
git clone https://github.com/oikumo/agentx.git
uv tool install --editable agentx
agentx        # run from anywhere
```

Uninstall with `uv tool uninstall agentx`.

You'll see the console interface. Commands: `c` for chat, `r` for RAG, `m` for models, `q` to quit. Legacy `--tui`/`--no-tui` flags are accepted as no-ops for backwards compatibility.

---

## 🎨 Features

### Console REPL

**Only mode** - A keyboard-driven console REPL:

```text
┌─ AgentX Console ────────────────────────────────────────────┐
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

Use the **Models screen** (press `m` from the main menu) to select the active provider at runtime. The selection is persisted to `~/.agentx/model_selection.json` and used across chat, RAG, and agent features.

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

**Advanced Agent Screen:**

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

The Fast Agent reuses the same `Agent` facade + `AgentController` under the hood — zero Model-layer changes. It uses a console modal-dialog flow (Goal → Running → Reflection → Result).

---

### 🎛️ Models Screen (feature_013)

A runtime AI model provider selector accessible from the main menu (press `m`):

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
- **View**: `ConsoleReactView` is the console view; displays thinking/tool/answer blocks with distinct styling
- **Integration**: Added `t` binding + 🧠 ReAct entry to the main menu

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
┌─ Coding ──────────────────────────────────────────────────────────┐
│  Ask me to explore, edit, or create files!                        │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  You: Find all Python files in the src/ directory                 │
│                                                                   │
│  💭 The user wants to find Python files. I'll use file_search.    │
│                                                                   │
│  🔧 file_search(pattern="src/**/*.py")                            │
│                                                                   │
│  📊 Found 3 files: src/main.py, src/utils.py, src/test.py         │
│                                                                   │
│  💭 Let me read main.py to understand the structure.              │
│                                                                   │
│  🔧 file_read(path="src/main.py")                                 │
│                                                                   │
│  📊 def main():\n    print('Hello from main')\n                   │
│                                                                   │
│  💭 Now I'll add a new function to utils.py.                      │
│                                                                   │
│  🔧 file_edit(path="src/utils.py", old_str="def helper():",       │
│      new_str="def helper():\n    return 42\n\n\ndef new_func():") │
│                                                                   │
│  📊 --- a/src/utils.py\n+++ b/src/utils.py\n@@ -1,2 +1,5 @@\n     │
│   def helper():\n+    return 42\n+\n+def new_func():              │
│                                                                   │
│  Assistant: Found 3 Python files. Read main.py and added          │
│  new_func() to utils.py.                                          │
│                                                                   │
│  > _                                                              │
└───────────────────────────────────────────────────────────────────┘
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
- **View**: `ConsoleCodingView` is the console view; displays thinking/tool/answer blocks with diff highlighting
- **Integration**: Added `d` binding + 💻 Coding entry to the main menu
 
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

**feature_001**: The session lifecycle (create → active → switch) is implemented with SQLite persistence. Petri-net-driven **user objective** management is in progress — the `GoalManager` is currently a stub awaiting full integration.

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

### 🖥️ Petri Net Studio (feature_034/035/036)

A **standalone browser-based Petri net workbench** at [`tools/petri-net-studio/`](tools/petri-net-studio/) — a Vite + React + TypeScript app that is **independent of agentx at runtime** (zero agentx/harness imports; `shared/petri-net/` is the only coupling). Its TypeScript engine is an exact behavioral port of the Python model (`src/agentx/model/petri_net/`), with golden byte-parity on the canonical JSON format.

Shipped in three stages:

| Stage | Feature | What shipped |
|-------|---------|--------------|
| **v1 — Editor** | feature_034 | TS engine port (`model`/`io`/`errors`, golden byte-parity), zustand store, React Flow **edit/simulate** UI (draw → set tokens/weights → click-to-fire with enabled highlighting → export/re-import identical canonical JSON), strict-JSON parser |
| **v2 — Analysis** | feature_035 | Exact-parity **analysis engine** (`fraction.ts` exact rationals + `analysis.ts`: reachability, deadlock, bounds, liveness, SCC, P/T-invariants) + a no-overclaim `AnalysisPanel` with `maxStates` dial + a canonical **conformance-vector generator** (9 vectors @ `shared/petri-net/conformance/analysis-v1/`) |
| **v3 — Graph** | feature_036 | **Reachability-graph explorer** (`GraphExplorer`) with elkjs auto-layout, SCC coloring, deadlock highlight, truncation banner; **firing-sequence animation** (Play/Step/Reset); liveness/SCC views; example **Gallery**; `npm run conformance` formalization |

**Engine parity guarantees:** deterministic code-point ordering everywhere, hand-rolled `fraction.ts` (no floats in the algebra path), line-for-line port of the Python `_explore` reachability loop, and conformance vectors that are byte-identical across re-runs (pinned by `npm run conformance`).

```bash
cd tools/petri-net-studio
npm install
npm run dev       # launch the studio in the browser
npm run test      # Vitest suite (283 tests across 14 files: model/io/analysis/projection/store/dashboard/conformance)
npm run build     # typecheck (tsc) + static dist/ build
npm run conformance  # regenerate conformance vectors + assert byte-identical + run suite
npm run check-independence  # assert no cross-boundary src/ imports
```

---

### 🔌 LangChain & LangGraph Integration

Full integration with the LangChain ecosystem:

- **LangChain** (1.3.14): Chains, prompts, output parsers
- **LangGraph** (1.2.10): Graph-based agentic workflows
- **LangChain Experimental** (0.4.2): Advanced features
- **Integrations**: Community (0.4.2), OpenAI, OpenRouter, Google-GenAI, NVIDIA, Tavily, Pinecone, Chroma, Ollama + `deepagents` (0.7.5)

**Already in use:** The ReAct (`t`) and Coding (`d`) screens run on LangChain's `create_agent` with a LangGraph `InMemorySaver` checkpointer for multi-turn context. The agent subsystem (`a`) wraps its own perceive→decide→act→reflect cycle. Custom user-defined LangGraph state machines are a future roadmap item.

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

Run `uv run agentx` (or `agentx` if globally installed) — see Quick Start above. The app starts in **console mode**. Legacy `--tui`/`--no-tui` flags are accepted as no-ops for backwards compatibility.

### Console Navigation

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
│  agentx/main.py — Bootstrap, provider selection, lifecycle  │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                   UI LAYER (ui/)                            │
│  Controllers + Views are co-located per feature screen      │
│  (NOT a separate controller layer):                         │
│  ui/screens/{main,chat,rag,react,models}/ — controllers     │
│      + console views (MainController, ChatController, ...)  │
│  ui/screens/ — Console views per feature screen              │
│  agent/controller/ — AgentController, SessionController,    │
│      ToolController                                         │
│  agent/view/       — Console agent view                      │
└─────────────────────────────────────────────────────────────┘
                             │
                             │ Talks through (ABC interfaces)
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                INTERFACE LAYER (ABCs)                       │
│  IMainView, IChatView, IRagView, IAgentViewPartner          │
│  IUIProvider, IAgentModelPartner, IToolRegistryPartner      │
│  IMemoryStorePartner, IPolicyStorePartner, IGoalManager     │
│  ISafetyEvaluator, IAIServicePartner                        │
└─────────────────────────────────────────────────────────────┘
                             │
                             │ Implemented By (Model)
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    MODEL LAYER                              │
│  model/ai/       — LLM providers (OpenRouter, OpenAI,       │
│                    Gemini, NVIDIA, Ollama, LlamaCpp) +      │
│                    model_registry (runtime selection)       │
│  model/chat/     — Chat service                             │
│  model/rag/      — RAG orchestration, vector stores         │
│  model/rag_v2/   — RAG v2 (feature_027, slash commands 029) │
│  model/petri_net/— Canonical Petri net model (format+io)    │
│  model/session/  — Session management, SQLite persistence   │
│  model/react/    — ReAct agent service (LangChain)          │
│  model/coding/   — Coding agent service + file tools        │
│  model/program/  — Console REPL / program logic             │
│  agent/          — Intelligent agent subsystem (nested MVC) │
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
- **Provider Pattern**: Console UI via provider (`ConsoleProvider`)
- **Facade Pattern**: `Agent` class orchestrates all agent subsystems
- **Data Provider (DP)**: SQL encapsulation in `*_db.py` classes

**Layer Rules:**
- ✅ Model has NO imports from `ui`
- ✅ View has NO business logic
- ✅ Controller has NO rendering code
- ✅ SQL only in `DP_*` / `*_db.py` classes

---

## 🧪 Testing

agentx includes automated tests covering all core modules — pytest (agentx) plus Vitest (Petri Net Studio TS engine/suite):

```bash
# Run all tests
uv run pytest tests/ -v

# Run model tests
uv run pytest tests/model/ -v

# Run agent subsystem tests
uv run pytest tests/features/feature_007.agentx_intelligent_agent_behaviour/ -v

# Petri Net Studio (TS) suite
(cd tools/petri-net-studio && npm run test)

# Run with coverage (if pytest-cov installed)
uv run pytest tests/ --cov=agentx --cov-report=html
```

**Test Coverage:**
- ✅ Petri nets & session management
- ✅ Commands & controllers
- ✅ Views (console)
- ✅ AI services & RAG orchestration
- ✅ Agent tool registry (sensors, actuators, discovery)
- ✅ Policy DSL engine (parsing, evaluation, conflict detection)
- ✅ Reflection engine (critique, safety, proposal routing)
- ✅ Goal manager & memory manager
- ✅ Agent persistence (stdlib sqlite3 repositories)
- ✅ Agent facade cycle (perceive→decide→act→reflect→persist)
- ✅ Demo scenarios & automated e2e tests
- ✅ Petri Net Studio engine (Vitest 283: model/io exact parity, fraction rationals, analysis 38-behavior port, graph projection, store, dashboard, conformance vectors — byte-identical re-runs)
- ✅ RAG v2 + slash commands

**Characteristics:**
- **Isolation**: All tests are isolated with mocking (no external dependencies)
- **Automated Tests**: End-to-end console tests
- **MVC++ Compliant**: 0 errors, 0 warnings on agent module
- **Fast**: Full suite runs in seconds

---

## 🛠️ Troubleshooting

### "Unknown command" error
Check your spelling with `help`. Commands are case-sensitive.

### API key prompt on startup
Set `OPENROUTER_API_KEY` in your `.env` file to avoid the interactive prompt.

### Console input not working
- Ensure you're running in a proper terminal (not piped input)
- Check TTY capability: `sys.stdin.isatty() and sys.stdout.isatty()`

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
- ✅ **feature_002**: RAG (retrieval augmented generation — Chroma/FAISS/Pinecone, PDF/web ingestion, vector search)
- ✅ **feature_004**: Modern TUI with Textual (removed — console-only now)
- ✅ **feature_005**: File system agentic tools
- ✅ **feature_007**: Intelligent agent behaviour (tools, policy DSL, reflection, self-improvement)
- ✅ **feature_010**: Agent demo screen (seeded scenarios A & B)
- ✅ **feature_011**: Fast Agent modal UX (Goal → Running → Reflection → Result)
- ✅ **feature_012**: TUI framework (removed — console-only now)
- ✅ **feature_013**: AI model provider selector (6 providers: OpenRouter, OpenAI, Gemini, NVIDIA, Ollama, LlamaCpp)
- ✅ **feature_014**: Non-blocking runner (daemon thread + queue poll, no UI freeze; TUI removed — console-only now)
- ✅ **feature_018**: ReAct chat screen (Reasoning + Acting with visible thinking, tool calls, streaming)
- ✅ **feature_019**: Coding Agent screen (File system tools: search, read, edit, list, create with diff highlighting)
- ✅ **feature_024**: Console parity — all features (react/coding/models/agent/fast-agent) available in the console REPL via `IUIProvider` + streaming (now the only UI)
- ✅ **feature_031**: Petri Net library project — shared cross-language Petri net contract (`shared/petri-net/` FORMAT + examples)
- ✅ **feature_032/033**: Petri net format + I/O (canonical JSON format, strict parser)
- ✅ **feature_034**: Petri Net Studio v1 — standalone browser workbench (`tools/petri-net-studio/`): exact TS engine port, React Flow edit/simulate editor, import/export (golden byte-parity)
- ✅ **feature_035**: Petri Net Studio v2 — exact-parity analysis engine (fraction.ts + analysis.ts) + no-overclaim AnalysisPanel + conformance-vector generator (9 vectors)
- ✅ **feature_036**: Petri Net Studio v3 — reachability-graph explorer (elkjs layout, SCC/deadlock views), firing-sequence animation, example gallery, `npm run conformance` (283 Vitest live)
- ✅ **feature_tui_dark_mode**: Default dark theme (removed with the TUI — console-only now)

### In Progress
- 🔄 **feature_001**: Petri-net-driven user objectives — session lifecycle (create → active → switch, SQLite-backed) is implemented; the Petri-net objective engine is stubbed (`GoalManager`) pending full integration
- 🔄 **rag_v2**: RAG v2 + slash commands — active (`src/agentx/model/rag_v2/`, `ui/screens/rag_v2/`)

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
| `shared/petri-net/FORMAT.md` | Canonical cross-language Petri net JSON format (LOCKED v1) + example corpus |
| `tools/petri-net-studio/` | Standalone TS Petri net workbench (engine port, analysis, graph explorer) |

---

## 🤝 Contributing

agentx is an educational project. Contributions are welcome!

**Development Workflow:**
1. Run tests: `uv run pytest tests/ -v`
2. Keep `src/agentx/` imports free of dev-tooling (`scripts/`, `toolbox/` were removed on the `meta_harness_removal` branch).

**Note**: This project uses opencode for development.

---

## 📄 License

Apache 2.0 - Educational and experimental purposes.

**Free for everyone**, including enterprise users.

---

## 🙏 Acknowledgments

- Developed with assistance from [opencode](https://opencode.ai) coding agent
- Built on [LangChain](https://python.langchain.com/) ecosystem

---

**Made for learning, experimentation, and exploration of LLM agent architectures.** 🚀