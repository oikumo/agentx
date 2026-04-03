# Agents - Function Tool Router Submodule

## Overview
Implements a query routing agent that uses Ollama's tool-calling capability to dispatch user queries to specific functions.

## Key Files

| File | Description |
|------|-------------|
| `function_call.py` | `QueryRouter` class - uses Ollama `chat()` with tools to dispatch function calls |
| `functions.py` | Tool functions: `get_weather_info()`, `get_game_recommend()`, `calculate()` |
| `route.py` | `Route` class - maps function name to callable |

## Tool Functions
- `get_weather_info(city, country)` - returns weather info
- `get_game_recommend(genre)` - returns game recommendations
- `calculate(expression)` - evaluates math expressions (uses `eval()`)

## Usage
```python
from agents.function_tool_router.function_call import QueryRouter
router = QueryRouter(llm)
router.run("What's the weather in Santiago?")
```
