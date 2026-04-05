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
main.py → src/main.py
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
| `sum` | SumCommand | src.app.repl.commands.math_commands | Add two integers |
| `quit` | QuitCommand | src.app.repl.commands.cli_commands | Exit the application |
| `clear` | ClearCommand | src.app.repl.commands.cli_commands | Clear console screen |
| `chat` | AIChat | src.app.repl.commands.llm_chat_commands | Start AI chat session (single-query or interactive REPL with streaming) |
| `router` | AIRouterAgents | src.app.repl.commands.llm_chat_commands | Run router agent (CSV + QR) |
| `react` | AIReactTools | src.app.repl.commands.llm_chat_commands | Run ReAct agent with tools |
| `search` | AISearch | src.app.repl.commands.llm_chat_commands | ReAct web search agent |
| `read` | ReadFile | src.app.repl.commands.cli_commands | Read and display a file |
| `function` | AIFunction | src.app.repl.commands.llm_chat_commands | AI function call demo |
| `rag` | RagPDF | src.app.repl.commands.llm_chat_commands | Query PDF with RAG |
| `graph` | AIGraphSimple | src.app.repl.commands.llm_graph_commands | Simple LangGraph workflow |
| `chains` | AIGraphChains | src.app.repl.commands.llm_graph_commands | LangGraph reflector chains |
| `reflex` | AIGraphReflexion | src.app.repl.commands.llm_graph_commands | LangGraph reflexion agent |
| `help` | HelpCommand | src.app.repl.commands.cli_commands | Show available commands |

---

## Design Patterns

- **Factory**: `AgentFactory` class in `src/llm_managers/factory.py` encapsulates all agent creation
- **Command**: `Command` ABC with `run()` method; `CommandResult` ABC with `apply()`
- **Strategy**: LLM providers implement `LLMProvider` ABC; different agents implement different reasoning strategies
- **State Machine**: LangGraph `StateGraph` for graph-based workflows
- **RAG Pipeline**: Standard pipeline: load → embed → store → retrieve → generate
- **Repository**: `SessionDatabase` for per-session SQLite persistence

---

## Key Architectural Decisions

1. **Factory Pattern**: All agents are created via `AgentFactory` static methods, decoupling instantiation from usage
2. **Command Pattern**: All REPL commands implement the `Command` ABC, ensuring consistent interface
3. **Session-Based Persistence**: Each REPL session creates a timestamped directory with its own SQLite database
4. **Security-First Deletion**: Directory deletion is restricted to `local_sessions/` within the current working directory
5. **Local-First Default**: All agents default to local LlamaCpp models, with cloud options available via separate factory functions
6. **LangChain Ecosystem**: Heavy reliance on LangChain ecosystem (langchain, langgraph, langchain-community) for LLM abstractions
7. **Vector Store Flexibility**: Supports FAISS (local), Pinecone (cloud), and Chroma (local) for different deployment scenarios
8. **src/ Layout**: All source code lives in `src/` and is installed as the `agent-x` package in development mode
9. **MCP Support**: Model Context Protocol servers extend agent capabilities via stdio transport
