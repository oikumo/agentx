# Project Documentation - Agent-X

> **Last Updated**: April 3, 2026  
> **Version**: 0.1.0  
> **Python**: >=3.14  
> **Package Manager**: uv

Agent-X is a Python-based LLM agent framework with a REPL interface. This file is a **map** to domain-specific documentation in the `doc/` folder.

---

## Documentation Index

| File | Domain | Description |
|------|--------|-------------|
| [doc/overview.md](doc/overview.md) | Project | Overview, architecture, application flow, command registry, design patterns, key decisions |
| [doc/root_module.md](doc/root_module.md) | Root | `main.py`, `pyproject.toml`, `README.md` |
| [doc/agents.md](doc/agents.md) | Agents | All agent implementations: chat, RAG, function router, ReAct search, graph search |
| [doc/app_repl.md](doc/app_repl.md) | App/REPL | REPL system, command pattern, controllers, all command classes |
| [doc/app_model.md](doc/app_model.md) | App/Model | Data persistence, sessions, SQLite database, command history |
| [doc/app_security.md](doc/app_security.md) | App/Security | Directory deletion safeguards, allowed paths |
| [doc/app_common.md](doc/app_common.md) | App/Common | Shared utilities: file ops, console helpers |
| [doc/app_modules_langchain.md](doc/app_modules_langchain.md) | App Modules/LangChain | ReAct agents, router agents, tools, callbacks |
| [doc/app_modules_langgraph.md](doc/app_modules_langgraph.md) | App Modules/LangGraph | Reflection chains, reflexion agent workflows |
| [doc/app_modules_data_stores.md](doc/app_modules_data_stores.md) | App Modules/Data Stores | FAISS vector store creation and persistence |
| [doc/app_modules_document_loaders.md](doc/app_modules_document_loaders.md) | App Modules/Loaders | PDF loading and text chunking |
| [doc/app_modules_web_ingestion.md](doc/app_modules_web_ingestion.md) | App Modules/Web Ingestion | Tavily extraction, document processing, vector store indexing pipeline |
| [doc/llm_models.md](doc/llm_models.md) | LLM Models | Cloud providers (OpenAI, Google), local providers (LlamaCpp, Ollama), Pinecone vector store |
| [doc/tests.md](doc/tests.md) | Tests | Unit test suite, test commands |
| [doc/dependencies.md](doc/dependencies.md) | Configuration | Dependencies table, environment variables, quick start, code style |
