# Project Roadmap - Agent-X

> **Last Updated**: April 4, 2026

## Planned Features & Improvements

### MVC Architecture Enhancements
- [ ] Complete service layer documentation
- [ ] Add controller test suite
- [ ] Implement view model patterns for better separation

### Testing & Quality
- [ ] Migrate mature `tests_sandbox/` tests to `tests/`
- [ ] Add integration tests with real LLM providers (gated by env var)
- [ ] Add linting and type checking to CI pipeline
- [ ] Increase test coverage to 80%

### Documentation
- [ ] Add API reference documentation for public classes
- [ ] Document controller patterns
- [ ] Add troubleshooting guide

### Future Considerations
- [ ] Evaluate MCP (Model Context Protocol) integration for extended capabilities
- [ ] Consider provider health check / fallback chain
- [ ] Evaluate conversation summarization for context window management

---

## Completed

### Architecture (v0.2.0 - April 2026)
- ✅ MVC architecture migration complete
- ✅ Reorganized into: `common/`, `controllers/`, `model/`, `services/`, `views/`
- ✅ Clean separation of concerns following Python best practices

### Documentation
- ✅ Refactored AGENTS.md — Lean Entry Point Pattern (77% size reduction)
- ✅ Updated README.md with improved project overview
- ✅ Reorganized meta files into `.project_development/` folder
- ✅ Updated PROJECT_NAVIGATION_ROUTES.md and PROJECT_DOCUMENTATION.md

### Core Features
- ✅ ChatLoop with persistent message history and streaming
- ✅ Streaming support with tok/s metrics
- ✅ `--model` flag for runtime model selection
- ✅ OpenRouter provider integration
- ✅ TDD sandbox with Kent Beck methodology
- ✅ LLM provider Strategy pattern
- ✅ CURRENT_ISSUE.md meta tracking file
