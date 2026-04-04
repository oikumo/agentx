# Project Overview - Agent-X

> **Version**: 0.1.0 | **Python**: >=3.14 | **Package Manager**: uv

Agent-X is a Python-based LLM agent framework with a REPL (Read-Eval-Print Loop) interface. It enables users to interact with various language models through command-line commands, supporting multiple interaction patterns:

- **Simple Chat**: Conversational interaction with local/cloud LLMs (single-turn and persistent REPL with streaming)
- **Chat Loop**: Persistent conversation with message history, streaming output, and context preservation
- **Function Calling**: Ollama-based tool calling for function dispatch
- **RAG (Retrieval-Augmented Generation)**: PDF Q&A with FAISS vector store and Ollama embeddings
- **ReAct Web Search**: Web search agents using Tavily with structured output
- **Graph-based Reasoning**: LangGraph workflows for reflection, reflexion, and multi-agent reasoning

---

## Application Flow

```
main.py
  └── create_controller()
        └── MainController (command registry)
              ├── Register 14 commands
              └── ReplApp(controller).run()
                    ├── Model(session_name="test_2") - session + DB
                    ├── Loop:
                    │   ├── input("(agent-x) > ")
                    │   ├── CommandParser.parse() → CommandData(key, arguments)
                    │   ├── MainController.find_command(key)
                    │   ├── Model.log_command(HistoryEntry)
                    │   ├── command.run(arguments) → CommandResult
                    │   ├── result.apply()
                    │   └── Print command history
                    └── Exit on KeyboardInterrupt / EOFError / QuitCommand
```

---

## Command Registry

| Command | Class | Module | Description |
|---------|-------|--------|-------------|
| `sum` | SumCommand | app.repl.commands.math_commands | Add two integers |
| `quit` | QuitCommand | app.repl.commands.cli_commands | Exit the application |
| `clear` | ClearCommand | app.repl.commands.cli_commands | Clear console screen |
| `chat` | AIChat | app.repl.commands.llm_chat_commands | Start AI chat session (single-query or interactive REPL with streaming) |
| `router` | AIRouterAgents | app.repl.commands.llm_chat_commands | Run router agent (CSV + QR) |
| `react` | AIReactTools | app.repl.commands.llm_chat_commands | Run ReAct agent with tools |
| `search` | AISearch | app.repl.commands.llm_chat_commands | ReAct web search agent |
| `read` | ReadFile | app.repl.commands.cli_commands | Read and display a file |
| `function` | AIFunction | app.repl.commands.llm_chat_commands | AI function call demo |
| `rag` | RagPDF | app.repl.commands.llm_chat_commands | Query PDF with RAG |
| `graph` | AIGraphSimple | app.repl.commands.llm_graph_commands | Simple LangGraph workflow |
| `chains` | AIGraphChains | app.repl.commands.llm_graph_commands | LangGraph reflector chains |
| `reflex` | AIGraphReflexion | app.repl.commands.llm_graph_commands | LangGraph reflexion agent |
| `help` | HelpCommand | app.repl.commands.cli_commands | Show available commands |

---

## Design Patterns

- **Factory**: All `agent_*_factory.py` files encapsulate agent creation
- **Command**: `Command` ABC with `run()` method; `CommandResult` ABC with `apply()`
- **Strategy**: Different agents implement different reasoning strategies
- **State Machine**: LangGraph `StateGraph` for graph-based workflows
- **RAG Pipeline**: Standard pipeline: load → embed → store → retrieve → generate
- **Repository**: `SessionDatabase` for per-session SQLite persistence

---

## Key Architectural Decisions

1. **Factory Pattern**: All agents are created via factory functions, decoupling instantiation from usage
2. **Command Pattern**: All REPL commands implement the `Command` ABC, ensuring consistent interface
3. **Session-Based Persistence**: Each REPL session creates a timestamped directory with its own SQLite database
4. **Security-First Deletion**: Directory deletion is restricted to `local_sessions/` within the current working directory
5. **Local-First Default**: All agents default to local LlamaCpp models, with cloud options available via separate factory functions
6. **LangChain Ecosystem**: Heavy reliance on LangChain ecosystem (langchain, langgraph, langchain-community) for LLM abstractions
7. **Vector Store Flexibility**: Supports FAISS (local), Pinecone (cloud), and Chroma (local) for different deployment scenarios
