# Agents Module - Agent-X

**Path**: `/agents/`

Agent implementations and factory functions. Each agent represents a different LLM interaction pattern.

---

## Module Structure

```
agents/
├── agent_chat_factory.py              # Factory for SimpleChat
├── agent_function_router_factory.py   # Factory for QueryRouter
├── agent_rag_factory.py               # Factory for AgentRagPdf
├── agent_react_web_search_factory.py  # Factory for AgentReactWebSearch
├── graph_react_web_search_factory.py  # Factory for GraphReactWebSearch
├── chat/
│   └── simple_chat.py                # SimpleChat class
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

### agents/chat/simple_chat.py

**Class**: `SimpleChat`

Wraps a `BaseChatModel` with a prompt template chain for simple conversational interaction.

**Methods**:
- `__init__(llm: BaseChatModel)` - stores LLM instance
- `run(query: str, information: str = "")` - creates prompt template chain and invokes LLM

**Dependencies**: `langchain_core.language_models.BaseChatModel`, `langchain_core.prompts.PromptTemplate`

### agents/agent_chat_factory.py

**Function**: `create_agent_chat_local() -> SimpleChat`

Factory function that creates a `SimpleChat` with a local LlamaCpp Qwen 2.5 model (context size 32768).

---

## ReAct Web Search Agent

### agents/react_web_search/search_agent.py

**Function**: `search_agent(llm: BaseLanguageModel)`

Creates a full ReAct agent with Tavily web search and structured output parsing via Pydantic.

**Flow**:
1. Creates `TavilySearch` tool
2. Sets up `PydanticOutputParser` with `AgentResponse` schema
3. Creates ReAct prompt with format instructions
4. Builds chain: `agent_executor | extract_output | parse_output`
5. Invokes with sample query about Chile news

**Classes**:
- `Source(BaseModel)` - schema with `url: str`
- `AgentResponse(BaseModel)` - schema with `answer: str` and `sources: List[Source]`

### agents/react_web_search/agent_react_web_search.py

**Class**: `AgentReactWebSearch`

Thin wrapper delegating to `search_agent()`.

**Methods**:
- `__init__(llm: BaseChatModel)` - stores LLM
- `run()` - delegates to `search_agent(llm=self.llm)`

### agents/react_web_search/prompt.py

**Constant**: `REACT_PROMPT_WITH_FORMAT_INSTRUCTIONS`

ReAct prompt template with `{tools}`, `{tool_names}`, `{format_instructions}`, `{input}`, and `{agent_scratchpad}` placeholders.

### agents/react_web_search/schemas.py

Duplicate Pydantic models (`Source`, `AgentResponse`) for structured agent response.

### agents/agent_react_web_search_factory.py

**Function**: `create_agent_react_web_search_local() -> AgentReactWebSearch`

Factory creating `AgentReactWebSearch` with local LlamaCpp Qwen 2.5 (context size 32768).

---

## RAG PDF Agent

### agents/rag_pdf/agent_rag_pdf.py

**Class**: `AgentRagPdf`

PDF ingestion → FAISS vector store → retrieval QA chain pipeline.

**Methods**:
- `__init__(pdf_path: str, vectorstore_path: str, llm: BaseChatModel, embeddings: Embeddings)` - stores configuration
- `run(query: str)` - pulls retrieval QA prompt from LangChain Hub, calls `rag_pdf()`
- `rag_pdf(query, pdf_path, vectorstore_path, retrieval_qa_chat_prompt, llm, embeddings)` - full RAG pipeline:
  1. Load PDF via `pdf_loader()`
  2. Create FAISS vector store via `create_faiss()`
  3. Build stuff documents chain via `create_stuff_documents_chain()`
  4. Build retrieval chain via `create_retrieval_chain()`
  5. Invoke and print answer

**Dependencies**: `langchain_classic.hub`, `langchain_classic.chains.*`, `app_modules.document_loaders.pdf_loader`, `app_modules.data_stores.vector_store_faiss`

### agents/agent_rag_factory.py

**Function**: `create_agent_rag_local() -> AgentRagPdf`

Factory creating `AgentRagPdf` with:
- Local LlamaCpp Qwen 2.5 (context size 32768)
- Ollama embeddings (`nomic-embed-text`)
- PDF path: `_resources/react.pdf`
- Vector store path: timestamped directory under `local_vector_databases/`

---

## Function Tool Router Agent

### agents/function_tool_router/function_call.py

**Class**: `QueryRouter`

Ollama tool calling to dispatch function calls based on user query.

**Methods**:
- `__init__(routes: list[Route])` - stores route definitions
- `function_call(model="functiongemma:270m-it-fp16")` - sends prompt to Ollama with tools, matches response to function, executes, and sends result back to LLM for final response

**Flow**:
1. Sends user message to Ollama with tool definitions
2. Parses response to identify tool call
3. Looks up and executes the function
4. Sends tool result back to Ollama
5. Prints final response

**Dependencies**: `rich`, `ollama`, `app.repl.console`

### agents/function_tool_router/functions.py

Tool functions available for the query router:

- `get_weather(city: str) -> str` - returns mock weather data as JSON (22°C, sunny)
- `get_best_game(year: str) -> str` - returns mock game data as JSON (Dark Souls)
- `calculate(expression: str) -> str` - evaluates math expression via `eval()` (with safety warning)

### agents/function_tool_router/route.py

**Class**: `Route`

Maps function name to callable for the router.

**Methods**:
- `__init__(function_name: str, route: Callable)` - stores name and callable
- `run(args)` - executes the callable

### agents/agent_function_router_factory.py

**Function**: `create_agent_function_router_local() -> QueryRouter`

Factory creating `QueryRouter` with routes for `get_weather`, `get_best_game`, and `calculate`.

---

## Graph ReAct Web Search Agent

### agents/graph_react_web_search/graph_react_web_search.py

**Class**: `GraphReactWebSearch`

LangGraph state machine with reasoning/act nodes for ReAct web search with function calling.

**Methods**:
- `__init__(llm: BaseChatModel, max_search_results: int)` - binds `TavilySearch` and `triple` tool to LLM
- `run()` - builds `StateGraph` with `agent_reasoning` and `act` nodes, compiles and invokes with a query about temperature in Santiago and Tokyo
- `run_agent_reasoning(state: MessagesState) -> MessagesState` - LLM reasoning node
- `should_continue(state: MessagesState) -> str` - checks for tool calls to decide whether to continue to `ACT` node or `END`

**Tool**: `@tool triple(num: float) -> float` - triples a number

**Graph Flow**:
```
ENTRY → agent_reasoning → should_continue?
  ├── Has tool calls → act (ToolNode) → agent_reasoning (loop)
  └── No tool calls → END
```

**Dependencies**: `langchain_tavily.TavilySearch`, `langgraph.graph.*`, `langgraph.prebuilt.ToolNode`

### agents/graph_react_web_search_factory.py

**Functions**:
- `create_graph_react_web_search_local() -> GraphReactWebSearch` - uses local LlamaCpp Qwen 2.5
- `create_graph_react_web_search_cloud() -> GraphReactWebSearch` - uses OpenAI GPT-3.5-turbo
