# AGENTS.md - Agent-X System Agent Rules

> **Purpose**: Primary entry point for the system agent. Defines rules, commands, and navigation paths.
> **Last Updated**: April 4, 2026

---

## 📋 Quick Reference

| Category | File | Description |
|----------|------|-------------|
| **Core Directives** | `.project_development/CORE_DIRECTIVES.md` | Non-negotiable rules |
| **Tool Usage** | `.project_development/TOOL_USAGE.md` | How to interact with codebase |
| **Coding Style** | `.project_development/CODING_STYLE.md` | Conventions & naming |
| **Task Workflow** | `.project_development/TASK_WORKFLOW.md` | Step-by-step process |
| **Environment** | `.project_development/ENVIRONMENT.md` | Runtime & operational notes |
| **Navigation** | `.project_development/PROJECT_NAVIGATION_ROUTES.md` | Project structure map |
| **Documentation** | `.project_development/PROJECT_DOCUMENTATION.md` | Detailed module docs |
| **Current Issue** | `.project_development/CURRENT_ISSUE.md` | Active bugs & tasks |
| **Roadmap** | `.project_development/PROJECT_ROADMAP.md` | Planned features |
| **Testing Rules** | `.project_development/PROJECT_TESTING_SANDBOX_RULES.md` | TDD guidelines |
| **Commands** | `.project_development/USER_COMMAND_EXTENSION.md` | Extended commands |

---

## 🎮 User Commands

All commands start with `+`. Pipe results using `|`.

| Command | Arguments | Description                                                  |
|---------|-----------|--------------------------------------------------------------|
| `+reload` | - | Refresh context: check last 10 commits & reload this file    |
| `+fix` | `{bug info}` | Fix a recent bug. Check git history first.                   |
| `+issue` | `{issue desc}` | Update `CURRENT_ISSUE.md`                                    |
| `+solve` | - | Resolve the current issue (BIG TASK)                         |
| `+?` | `{question}` | Ask about the project (checks last 50 commits)               |
| `+find` | `{module/topic}` | Locate code using Navigation Routes                          |
| `+update` | - | Update navigation, issues, README.md files & docs (BIG TASK) |
| `+list` | - | List all rules in table format                               |
| `+focus` | `{module/topic}` | Focus attention on a specific area                           |
| `+tasks` | - | List current & past system tasks                             |
| `+tree` | - | Show project structure from Navigation Routes                |
| `+big` | - | Start a BIG TASK workflow                                    |
| `+` | - | List all available commands                                  |
| `+test` | - | Run tests in `tests_sandbox/`                                |
| `+tdd` | `{scope}` | Apply TDD for a feature in `tests_sandbox/`                  |
| `+refactor` | `{file} {strategy}` | AST-based refactoring (requires approval)                    |
| `+testgen` | `{module_path}` | Generate unit tests in `tests_sandbox/`                      |
| `+audit` | - | Scan for secrets & security issues                           |
| `+bench` | `{agent} {input}` | Run performance benchmark                                    |

---

## 📂 Project Navigation

The agent should use `.project_development/PROJECT_NAVIGATION_ROUTES.md` as the primary map for understanding project structure.

**Source code lives in `src/`** — all modules are installed as the `agent-x` package.

- **Entry Point**: `main.py` → `src/main.py`
- **Core App**: `src/app/` (REPL, models, security)
- **Agents**: `src/agents/` (chat, rag, react, graph)
- **LLM Managers**: `src/llm_managers/` (factory, providers)
- **LLM Models**: `src/llm_models/` (cloud, local, vectorstores)
- **App Modules**: `src/app_modules/` (langchain, langgraph, data stores)
- **MCP**: `src/local_mcp/` (Model Context Protocol servers)
- **Tests**: `tests/` (read-only)
- **Tests Sandbox**: `tests_sandbox/` (feature & integration tests)
