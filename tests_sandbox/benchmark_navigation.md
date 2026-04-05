# Benchmark: Agent Navigation via AGENTS.md

## Overview
Tests the opencode agent's ability to navigate the project structure using AGENTS.md rules and references.

## Tasks

| # | Task | Expected Answer |
|---|------|-----------------|
| 1 | Where is the project navigation map? | `/.project_development/PROJECT_NAVIGATION_ROUTES.md` |
| 2 | Where are the testing rules? | `/.project_development/PROJECT_TESTING_SANDBOX_RULES.md` |
| 3 | Where is the current issue tracked? | `/.project_development/CURRENT_ISSUE.md` |
| 4 | Where is the project roadmap? | `/.project_development/PROJECT_ROADMAP.md` |
| 5 | Where is the project documentation map? | `/.project_development/PROJECT_DOCUMENTATION.md` |
| 6 | Where is the user command extension? | `/.project_development/USER_COMMAND_EXTENSION.md` |
| 7 | What is the entry point of the application? | `main.py` |
| 8 | Where are the LLM providers implemented? | `llm_managers/providers/` |
| 9 | Where is the REPL system? | `app/repl/` |
| 10 | Where are the sandbox tests? | `tests_sandbox/` |
| 11 | What command checks the last 10 commits? | `+reload` |
| 12 | What command solves the current issue? | `+solve` |
| 13 | What command finds a module or topic? | `+find {module or topic}` |
| 14 | What is the line length limit? | 88 characters |
| 15 | What naming convention for constants? | UPPER_SNAKE_CASE |

## Metrics
- **Input tokens**: Total tokens sent to agent
- **Output tokens**: Total tokens received from agent
- **Latency**: Time per task (ms)
- **Success rate**: % of correct answers
- **Token efficiency**: Correct answers per 1000 tokens
