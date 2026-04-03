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
| `+bench` | Run a quick performance benchmark (latency, token usage) for a chosen agent. Arguments: **agent name** and **input file** (or data) to feed the agent. | `+benchmark chat prompts/hello.txt` | ❌ |

---

### Brief Behaviour Summary

- **`+refactor`**: Parses the target file with `ast`, applies the chosen strategy, and writes the transformed source back (confirmation required).
- **`+testgen`**: Generates a skeleton `unittest.TestCase` file mirroring the module’s public API; placeholders guide further test development.
- **`+audit`**: Looks for secret patterns (`*_KEY`, `*_TOKEN`) and disallowed imports (`subprocess`, `os.system`); reports findings without modifying any file.
- **`+bench`**: Calls the specified agent with the given input, measures average latency, token count (if available), and success flag; prints a markdown table.
