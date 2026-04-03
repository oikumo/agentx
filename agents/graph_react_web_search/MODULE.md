# Agents - Graph ReAct Web Search Submodule

## Overview
ReAct-pattern web search agent built on LangGraph with a state graph (reasoning → action → loop).

## Key Files

| File | Description |
|------|-------------|
| `graph_react_web_search.py` | `GraphReactWebSearch` class - LangGraph state machine with reasoning/act nodes |

## Features
- LangGraph `StateGraph` with conditional edges (reason ↔ act ↔ end)
- Supports Tavily search + custom tools
- Uses `bind_tools` for tool integration
