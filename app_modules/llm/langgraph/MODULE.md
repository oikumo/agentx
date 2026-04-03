# App Modules - LLM / LangGraph

## Overview
LangGraph-based workflow implementations for reflection and reflexion patterns.

## Structure

```
llm/langgraph/
├── graph_reflector_chain/
│   ├── chains.py                  # reflection_prompt, generation_prompt, generate_chain, reflect_chain
│   └── graph_chains.py            # StateGraph with generate ↔ reflect loop (6 messages)
└── graph_reflexion_agent/
    ├── chains.py                  # first_responder, revisor with structured output
    ├── graph_reflexion_agent.py   # Workflow: draft → execute_tools → revise → loop (2 iterations)
    ├── schemas.py                 # Pydantic: Reflection, AnswerQuestion, ReviseAnswer
    └── tool_executor.py           # run_queries() + ToolNode for TavilySearch
```

## Graph Patterns

### Reflector Chain
- **generate** node: creates content (e.g., tweets)
- **reflect** node: critiques and improves
- **Termination**: After 6 messages

### Reflexion Agent
- **draft** node: initial answer + self-reflection + search queries
- **execute_tools** node: runs search queries via TavilySearch
- **revise** node: revises answer with citations
- **Termination**: After MAX_ITERATIONS=2

## LangGraph Features
- `StateGraph` with `MessagesState` and custom `TypedDict` schemas
- Nodes: `add_node`, edges: `add_edge`, conditional: `add_conditional_edges`
- `ToolNode` (prebuilt) for tool execution
- Graph visualization via `draw_mermaid()` / `print_ascii()`
