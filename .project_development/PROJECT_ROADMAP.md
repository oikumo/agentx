# Project Roadmap - Agent-X

> **Last Updated**: April 4, 2026

## Planned Features & Improvements

### RAG Enhancements
- [ ] Complete RAG integration to ChatLoop (currently WIP)
- [ ] Add support for multiple document types (not just PDF)
- [ ] Implement incremental vector store updates
- [ ] Add RAG source citation in responses

### MCP Integration
- [ ] Add more MCP servers (weather, games, file system)
- [ ] Implement MCP client in ChatLoop for tool discovery
- [ ] Add MCP server configuration via CLI flags

### Agent Improvements
- [ ] Add tool calling support to `ChatLoop` (function dispatch within conversation)
- [ ] Implement conversation summarization to prevent context window overflow
- [ ] Add configurable system prompts per session

### Provider Expansion
- [ ] Add `OllamaProvider` to `llm_managers/providers/` for local Ollama chat
- [ ] Add `GeminiProvider` to `llm_managers/providers/` for Google models
- [ ] Implement provider health check / fallback chain

### Testing & Quality
- [ ] Migrate mature `tests_sandbox/` tests to `tests/`
- [ ] Add integration tests with real LLM providers (gated by env var)
- [ ] Add linting and type checking to CI pipeline

### Documentation
- [ ] Add API reference documentation for public classes
- [ ] Document agent configuration patterns
- [ ] Add troubleshooting guide for common LLM provider issues

---

## Completed
- ✅ Refactored AGENTS.md — Lean Entry Point Pattern (77% size reduction)
- ✅ Updated README.md with improved project overview
- ✅ Reorganized meta files into `.project_development/` folder
- ✅ Unified AgentFactory in llm_managers/ (replaced 5 factory files)
- ✅ MCP (Model Context Protocol) server support
- ✅ RAG integration to ChatLoop (WIP → complete)
- ✅ ChatLoop with persistent message history and streaming
- ✅ OpenRouter provider integration
- ✅ TDD sandbox with Kent Beck methodology
- ✅ LLM provider Strategy pattern with 3 implementations
- ✅ CURRENT_ISSUE.md meta tracking file
- ✅ Streaming support with tok/s metrics
- ✅ `--model` flag for runtime model selection
- ✅ llama.cpp provider using ChatOpenAI client
