# Current Issue - Agent-X

> **Last Updated**: April 4, 2026

## Refactor `llm_managers/` — Simplify Module

**Status**: IN PROGRESS

**Problem**:
- 5 separate factory files with redundant patterns
- `_local` aliases duplicated across files
- Hardcoded LlamaCppProvider defaults scattered everywhere
- Empty `__init__.py` — no public API surface
- Inconsistent patterns (RagConfig dataclass vs simple params)

**Plan**:
1. Write TDD tests for new unified `AgentFactory` API
2. Create single `factory.py` with `AgentFactory` class (static methods)
3. Centralize defaults in `providers/__init__.py`
4. Update consumers (`llm_chat_commands.py`, `llm_graph_commands.py`)
5. Remove old factory files
6. Expose public API in `__init__.py`
7. Run all tests and verify

**Target API**:
```python
from llm_managers.factory import AgentFactory

AgentFactory.create_chat(provider=None)
AgentFactory.create_chat_loop(provider=None)
AgentFactory.create_function_router(routes=None)
AgentFactory.create_rag(config=None)
AgentFactory.create_react_web_search(provider=None)
AgentFactory.create_graph_react_web_search(provider=None, max_search_results=1)
```
