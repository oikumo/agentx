# USER_COMMMAND_EXTENDED.md

## Simplified, yet powerful LLM‑agent commands

The table below contains a **concise** set of high‑impact commands that cover the core needs of a coding‑assistant workflow (refactoring, testing, linting, auditing, benchmarking, and repo sync).  All commands keep the `+` prefix used throughout the project.

---

### Command Reference

| Command | Description | Example | Needs approval? |
|--------|-------------|---------|-----------------|
| `+refactor` | Apply an AST‑based refactor (`rename`, `extract_method`, `simplify`). Arguments: target **file path** and a **strategy** string (e.g., `rename OldName NewName`). | `+refactor app/models/user.py rename UserEntity` | ✅ |
| `+testgen` | Auto‑create `unittest` tests for the specified module. Argument: the module **file path**; tests are placed under `tests_sandbox/`. | `+testgen app/services/payment.py` | ✅ |
| `+audit` | Scan the repository for hard‑coded secrets, forbidden imports, and other security red flags; prints a concise report. No arguments required. | `+audit` | ❌ |
| `+benchmark` | Run a quick performance benchmark (latency, token usage) for a chosen agent. Arguments: **agent name** and **input file** (or data) to feed the agent. | `+benchmark chat prompts/hello.txt` | ❌ |

---

### Brief Behaviour Summary

- **`+refactor`**: Parses the target file with `ast`, applies the chosen strategy, and writes the transformed source back (confirmation required).
- **`+testgen`**: Generates a skeleton `unittest.TestCase` file mirroring the module’s public API; placeholders guide further test development.
- **`+audit`**: Looks for secret patterns (`*_KEY`, `*_TOKEN`) and disallowed imports (`subprocess`, `os.system`); reports findings without modifying any file.
- **`+benchmark`**: Calls the specified agent with the given input, measures average latency, token count (if available), and success flag; prints a markdown table.

---

### Integration Tips for the REPL

- Register each command in `app/repl/commands/` following the existing `Command` interface.
- Ensure every mutating command (`+refactor`, `+testgen`) **asks for user confirmation** before performing write actions, respecting the project rule *“Never commit files that likely contain secrets.”*
- Re‑use the `LLMProvider` strategy from `llm_managers.providers` for all LLM‑driven commands.
- Keep the implementation lightweight; rely on built‑in tools (`black`, `isort`, `ast`, `subprocess`, `gh`) rather than external heavy dependencies.

---

