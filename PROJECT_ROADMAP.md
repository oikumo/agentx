# Project Roadmap - Agent-X

> **Last Updated**: April 3, 2026

## Planned Features & Improvements

### Streaming Enhancements
- [ ] Add streaming support to all REPL commands (not just `chat`)
- [ ] Implement token-per-second display during streaming
- [ ] Add `--model` flag to `chat` command for runtime model selection

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
- ✅ ChatLoop with persistent message history and streaming
- ✅ OpenRouter provider integration
- ✅ TDD sandbox with Kent Beck methodology
- ✅ LLM provider Strategy pattern with 3 implementations
- ✅ CURRENT_ISSUE.md meta tracking file
