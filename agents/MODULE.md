# Agents Module

## Overview
Contains all agent implementations and their factory functions. Each agent represents a different LLM interaction pattern: simple chat, function routing, RAG, ReAct web search, and graph-based agents.

## Structure

```
agents/
├── agent_chat_factory.py              # Factory for SimpleChat
├── agent_function_router_factory.py   # Factory for QueryRouter
├── agent_rag_factory.py               # Factory for AgentRagPdf
├── agent_react_web_search_factory.py  # Factory for AgentReactWebSearch
├── graph_react_web_search_factory.py  # Factory for GraphReactWebSearch
├── chat/
│   └── simple_chat.py                 # Basic conversational agent
├── function_tool_router/
│   ├── function_call.py               # QueryRouter with Ollama tool calling
│   ├── functions.py                   # Tool functions (weather, game, calculate)
│   └── route.py                       # Route class (name + callable mapping)
├── graph_react_web_search/
│   └── graph_react_web_search.py      # LangGraph-based ReAct web search
├── rag_pdf/
│   └── agent_rag_pdf.py               # PDF RAG with FAISS + Ollama embeddings
└── react_web_search/
    ├── agent_react_web_search.py      # ReAct web search agent
    ├── prompt.py                      # ReAct prompt template
    ├── schemas.py                     # Pydantic models (Source, AgentResponse)
    └── search_agent.py                # search_agent() function
```

## Design Patterns
- **Factory**: All `agent_*_factory.py` files encapsulate agent creation
- **Strategy**: Different agents implement different reasoning strategies
- **Chain of Responsibility**: LangChain chains compose processing steps
- **State Machine**: `GraphReactWebSearch` uses LangGraph `StateGraph`
- **Tool Calling**: Ollama native tool-calling and LangChain `bind_tools`
- **RAG**: Standard RAG pipeline: load → embed → store → retrieve → generate

## Dependencies
- All factories depend on `llm_models/` for model instantiation
- Agents are standalone with no inter-agent dependencies
- Default to local LlamaCpp (Qwen 2.5); some support cloud OpenAI
