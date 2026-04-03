# Agents - ReAct Web Search Submodule

## Overview
ReAct-pattern web search agent using Tavily search tool and LangChain's ReAct agent executor with structured Pydantic output.

## Key Files

| File | Description |
|------|-------------|
| `agent_react_web_search.py` | `AgentReactWebSearch` class - thin wrapper delegating to `search_agent()` |
| `prompt.py` | ReAct prompt template |
| `schemas.py` | Pydantic models: `Source`, `AgentResponse` |
| `search_agent.py` | `search_agent()` function - creates ReAct agent with Tavily, Pydantic output parser |

## Pattern
Thought → Action → Observation loop via LangChain's `create_react_agent`
