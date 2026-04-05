# Current Issue - Agent-X

> **Last Updated**: April 4, 2026

## No Active Issues

**Status**: EMPTY

---

## Recently Completed

### Moved Source Code to `src/` Folder ✅

**Status**: COMPLETED

**What was done**:
- Moved all source code modules (`agents/`, `app/`, `app_modules/`, `llm_managers/`, `llm_models/`, `local_mcp/`, `main.py`) into `src/` folder
- Installed package in development mode (`uv pip install -e .`) so imports resolve correctly
- Updated `pyproject.toml` with `[tool.setuptools.packages.find]` where = ["src"]
- Created wrapper `main.py` at root that delegates to `src/main.py`
- Updated all documentation files to reflect new paths
- All 12 benchmark tests pass ✅

### Refactored AGENTS.md — Lean Entry Point Pattern ✅

**Status**: COMPLETED

**What was done**:
- Extracted rules from monolithic AGENTS.md into focused files: `CORE_DIRECTIVES.md`, `TOOL_USAGE.md`, `CODING_STYLE.md`, `TASK_WORKFLOW.md`, `ENVIRONMENT.md`
- AGENTS.md reduced from 269 lines (9.7KB) to 62 lines (2.5KB) — 77% smaller
- Added Quick Reference table linking to all rule files
- Removed XML-style tags in favor of Markdown (research-backed for better LLM comprehension)
- Added benchmark suite for navigation accuracy verification
- All 12 benchmark tests pass ✅

### Updated README.md ✅

**Status**: COMPLETED

**What was done**:
- Major README rewrite with improved project overview, quick start, and documentation links

### Removed: USER_MANUAL.md ✅

**Status**: COMPLETED

**What was done**:
- Deleted outdated user manual (320 lines)

### Refactor `llm_managers/` — Simplify Module ✅

**Status**: COMPLETED

**What was done**:
- Consolidated 5 separate factory files into single `AgentFactory` class in `factory.py`
- Created unified API with static methods: `create_chat`, `create_chat_loop`, `create_chat_loop_rag`, `create_function_router`, `create_rag`, `create_react_web_search`, `create_graph_react_web_search`
- Centralized defaults in `providers/__init__.py` with helper functions `local_llm_provider()` and `openrouter_llm_provider()`
- Updated consumers (`llm_chat_commands.py`, `llm_graph_commands.py`)
- Removed old factory files (`agent_chat_factory.py`, `agent_function_router_factory.py`, `agent_rag_factory.py`, `agent_react_web_search_factory.py`, `graph_react_web_search_factory.py`)
- Added `test_factory_refactor.py` for new unified API

### [WIP] RAG Integration to Chat Loop

**Status**: IN PROGRESS

**What's being worked on**:
- `ChatLoop` now supports RAG capabilities via `create_chat_loop_rag()` factory method
- PDF ingestion → FAISS vector store → retriever integration with ChatLoop
- Streaming metrics support for RAG-enhanced conversations
- Updated tests in `test_chat_loop.py` and `test_llm_providers.py`
