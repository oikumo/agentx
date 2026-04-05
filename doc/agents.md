# Agents Module - Agent-X

**Path**: `src/agents/`

Agent implementations. Each agent represents a different LLM interaction pattern. Factory functions moved to `src/llm_managers/factory.py` (`AgentFactory`).

---

## Module Structure

```
src/agents/
├── chat/
│   ├── simple_chat.py                # SimpleChat class
│   └── chat_loop.py                  # ChatLoop class (persistent conversation with streaming)
├── function_tool_router/
│   ├── function_call.py              # QueryRouter class
│   ├── functions.py                  # Tool functions
│   └── route.py                      # Route class
├── graph_react_web_search/
│   └── graph_react_web_search.py     # GraphReactWebSearch class
├── rag_pdf/
│   └── agent_rag_pdf.py              # AgentRagPdf class
└── react_web_search/
    ├── agent_react_web_search.py     # AgentReactWebSearch class
    ├── prompt.py                     # ReAct prompt template
    ├── schemas.py                    # Pydantic models
    └── search_agent.py               # search_agent() function
```

---

## Simple Chat Agent

### src/agents/chat/simple_chat.py

**Class**: `SimpleChat`

Wraps a `BaseChatModel` with a prompt template chain for simple conversational interaction.

**Methods**:
- `__init__(llm: BaseChatModel)` - stores LLM instance
- `run(query: str, information: str = "")` - creates prompt template chain and invokes LLM
- `run_streaming(query: str, information: str = "")` - streaming variant using `llm.stream()`

### src/agents/chat/chat_loop.py

**Class**: `ChatLoop`

Persistent, conversational chat loop with message history support.

**Methods**:
- `__init__(llm: BaseChatModel, system_prompt: str)` - initializes with LLM and system prompt
- `add_user_message(content: str)` / `add_assistant_message(content: str)` - history management
- `get_response() -> str` - invokes LLM with full history
- `run(user_input: str) -> str | None` - single-turn with error rollback
- `start_interactive()` - interactive REPL loop
- `run_streaming_with_metrics()` - streaming with tok/s tracking via `StreamingMetrics`

---

## ReAct Web Search Agent

### src/agents/react_web_search/search_agent.py

**Function**: `search_agent(llm: BaseLanguageModel)`

Creates a full ReAct agent with Tavily web search and structured output parsing.

**Flow**: `agent_executor | extract_output | parse_output`

### src/agents/react_web_search/agent_react_web_search.py

**Class**: `AgentReactWebSearch` - thin wrapper delegating to `search_agent()`.

**Methods**:
- `__init__(llm: BaseChatModel)` - stores LLM
- `run()` - delegates to `search_agent(llm=self.llm)`
- `run_streaming(query)` - streaming variant

---

## RAG PDF Agent

### src/agents/rag_pdf/agent_rag_pdf.py

**Class**: `AgentRagPdf`

PDF ingestion → FAISS vector store → retrieval QA chain pipeline.

**Methods**:
- `__init__(pdf_path, vectorstore_path, llm, embeddings)` - stores configuration
- `run(query: str)` - full RAG pipeline
- `run_streaming(query)` - streaming variant

**Dependencies**: `app_modules.document_loaders.pdf_loader`, `app_modules.data_stores.vector_store_faiss`

---

## Function Tool Router Agent

### src/agents/function_tool_router/function_call.py

**Class**: `QueryRouter`

Ollama tool calling to dispatch function calls based on user query.

**Tool Functions** (`functions.py`):
- `get_weather(city: str)` - mock weather data
- `get_best_game(year: str)` - mock game data
- `calculate(expression: str)` - evaluates math expression

---

## Graph ReAct Web Search Agent

### src/agents/graph_react_web_search/graph_react_web_search.py

**Class**: `GraphReactWebSearch`

LangGraph state machine with reasoning/act nodes.

**Graph Flow**:
```
ENTRY → agent_reasoning → should_continue?
  ├── Has tool calls → act (ToolNode) → agent_reasoning (loop)
  └── No tool calls → END
```

---

## Factory (in llm_managers/)

All agents are created via `AgentFactory` in `src/llm_managers/factory.py`:

| Method | Returns | Description |
|--------|---------|-------------|
| `create_chat()` | `SimpleChat` | Simple conversational chat |
| `create_chat_loop()` | `ChatLoop` | Persistent chat with history |
| `create_chat_loop_rag()` | `ChatLoop` | RAG-enabled chat with PDF retriever |
| `create_function_router()` | `QueryRouter` | Ollama-based tool calling |
| `create_rag()` | `AgentRagPdf` | PDF RAG pipeline |
| `create_react_web_search()` | `AgentReactWebSearch` | Tavily ReAct agent |
| `create_graph_react_web_search()` | `GraphReactWebSearch` | LangGraph ReAct agent |
