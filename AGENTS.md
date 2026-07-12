# System Rules

> **⚠️ MANDATORY FIRST STEP:** On the **first prompt**, read `WORK.md` and display it.
>
> **⚠️ MANDATORY SECOND STEP:** Read this `AGENTS.md` in full.
>
> **⚠️ MANDATORY THIRD STEP:** Read `.meta/META_HARNESS.md` (token-optimized quick reference).
>
> **⚠️ MANDATORY FOURTH STEP:** Follow the OMT++ methodology in
> `.meta/software_development_process/omt_agent_guide.md` for any programming task.
>
> **⚠️ MANDATORY:** Always use `uv` to run Python (including tests). Bare
> `python`/`pip`/`pytest` are denied by `opencode.jsonc`.

> **Harness:** This project is driven by **opencode only**. The **META HARNESS** enforces
> OMT++ process mechanically via `opencode.jsonc` (permissions) and
> `.opencode/plugin/omt_enforcer.ts` (the gate). Quick reference: `.meta/META_HARNESS.md`.

---

## 🚦 HOW ENFORCEMENT ACTUALLY WORKS

This process is **mechanically enforced**, not advisory. The `omt_enforcer` plugin gates
your tool calls:

1. **Before you edit anything under `src/`, declare your phase** by calling the
   **`omt_phase`** tool:
   ```
   omt_phase{ task_type: "...", scope: "<one sentence: what 'done' looks like>", phase: "..." }
   ```
   `task_type` ∈ `bug_fix | minor_feature | major_feature | new_screen | refactor | test | docs`.
   This *is* the real version of the old "PROCESS CHECK" — it records to the process ledger
   and unlocks `src/` edits for the session.

2. **The gate scales rigor to task size** (per `omt_agent_guide.md §12`):
   - `bug_fix` / `minor_feature` / `refactor` → a phase declaration is enough.
   - `major_feature` / `new_screen` → you must also pass `design_doc: "<path>"` to an
     artifact that **exists on disk**, or `src/` stays blocked. Scaffold one with:
     `uv run scripts/omt/new_feature.py "<name>" --type major_feature`.

3. **If you edit `src/` without a phase, the edit is blocked** with a message telling you
   exactly what to run. This is not reversible by ignoring it — satisfy the gate.

4. **Architecture is checked automatically.** After each `src/` edit and on idle, the gate
   runs `uv run scripts/omt/mvc_check.py` and surfaces MVC++ violations (View↔Model leaks,
   non-ABC Abstract Partners, SQL outside DP classes, god controllers, …). Run it yourself
   anytime: `uv run scripts/omt/mvc_check.py [path]`.

5. **Escape hatch (logged).** Genuine emergencies or approved canary tests:
   `omt_skip{ reason: "...", scope: "src|tests|all" }`. Every skip is recorded in
   `.meta/.omt/ledger.jsonl` for audit. Prefer doing the process over skipping it.

6. **TDD enforcement (feature_016).** For `major_feature` / `new_screen` tasks in the **Programming** phase, **TDD mode auto-activates**. You must follow the **Red → Green → Refactor** cycle using the TDD tools (`omt_testlist` → `omt_red` → `omt_green` → `omt_refactor` → `omt_done`). The **two-hats gate** mechanically enforces which layer you may edit:
- **RED state** → Only `tests/` edits allowed (write the failing test).
- **GREEN / REFACTOR state** → Only `src/` edits allowed (write/refactor the code).
The `tool.execute.after` hook **reverts REFACTOR edits that break tests automatically**.

### Enforcement Matrix
The gate adapts rigor to task size, including TDD enforcement:

| task_type       | `omt_phase` Required? | Artifact Gate Before `src/` Edit | TDD Enforced | `tests/` Edit | MVC++ Check |
|----------------|----------------------|----------------------------------|--------------|---------------|-------------|
| `bug_fix`      | Yes (1-line scope)  | None (warn only)                 | ❌ No        | Canary approval | Warn (toast) |
| `minor_feature`| Yes                  | Operation list                   | ❌ No        | Canary approval | Warn (toast) |
| `major_feature`| Yes                  | **Design doc on disk**            | ✅ Yes       | **RED state only** | **Block hard violations** |
| `new_screen`   | Yes                  | **Use case + design doc on disk**  | ✅ Yes       | **RED state only** | **Block hard violations** |
| `refactor`     | Yes                  | None                              | ❌ No        | Canary approval | **Block hard violations** |
| `test`         | Yes                  | N/A                               | ❌ No        | Canary approval | Warn (toast) |
| `docs`         | No                   | N/A                               | ❌ No        | N/A            | N/A |

See `omt_agent_guide.md §11.4` for the full TDD workflow.

---

## Core Directives

**NEVER** (enforced by `opencode.jsonc` / the gate — the action is blocked):
1. Commit or push code (`git commit` / `git push` are denied).
2. Read or modify `.env` / secrets.
3. Add dependencies without approval.
4. Modify `tests/` without approval (use canary tests + `omt_skip{scope:"tests"}`).
   - In TDD mode, `tests/` edits are allowed during RED state — the TDD gate replaces
     canary approval for the current test node.
5. Change `README.md`, `uv.lock`, or `LICENSE` (unless explicitly asked).
6. Edit `src/` without first declaring a phase via `omt_phase`.
   - In TDD mode, `src/` edits are allowed during GREEN/REFACTOR state only.

**ALWAYS:**
7. Check `git log` / `git status` before changes.
8. Understand the project by reading the `META.md` file in each directory.
9. Read `.meta/META_HARNESS.md` before any coding task (token-optimized reference).
10. Follow OMT++ (`omt_agent_guide.md`) for all code changes.
11. Declare your phase (`omt_phase`) before touching `src/`.
12. Produce the phase artifacts your task size requires (guide §12); scaffold features with
    `scripts/omt/new_feature.py` so artifacts stay consistently named (no ad-hoc `*_PROOF.md`).
13. For major features / new screens in Programming phase: follow the TDD cycle
    (`omt_testlist` → `omt_red` → `omt_green` → `omt_refactor` → `omt_done`).

---

## Tooling (opencode-native)

### Process Gate Tools

| Tool | Purpose |
|------|---------|
| `omt_phase` | Declare OMT++ phase; unlocks `src/` edits (plugin) |
| `omt_skip` | Logged process-override escape hatch (plugin) |
| `omt_complete` | Verify phase artifacts + advance to next phase |
| `uv run scripts/omt/mvc_check.py` | MVC++ architecture linter (guide §16) |
| `uv run scripts/omt/new_feature.py "<name>"` | Scaffold a feature's artifacts from `.meta/templates/` |

### TDD Enforcement Tools (feature_016)

| Tool | Purpose |
|------|---------|
| `omt_testlist` | Record the TDD test list (behaviors to implement). Sets state → TESTLIST. |
| `omt_red` | Declare a failing test (TDD Red). Runs pytest + AST true-RED verification. Sets state → RED (test hat). |
| `omt_green` | Declare a passing test (TDD Green). Runs pytest. Sets state → GREEN (code hat). |
| `omt_refactor` | Declare refactor state. Runs pytest. Sets state → REFACTOR (code hat, tests must stay green). |
| `omt_done` | Declare TDD completion. Runs full suite + checklist. Sets state → DONE. |
| `uv run scripts/omt/tdd_check.py` | TDD engine CLI (9 subcommands: testlist, start, green, refactor, done, gate, after-edit, status, validate-exit) |

### Status & Inspection

| Tool | Purpose |
|------|---------|
| `omt_status` | Returns full process context: phase, unlock state, artifacts, lint baseline, TDD state, WORK.md next task |

---

## 📖 References

- **META HARNESS quick reference:** `.meta/META_HARNESS.md` (read this first — 137 lines, ~1,400 tokens)
- **OMT++ methodology:** `.meta/software_development_process/omt_agent_guide.md` (source of truth)
- **Project / requirements / analysis / design / impl / testing:**
  `.meta/software_development_process/{1.project … 7.integration}/`
- **Process enforcement plan:**
  `.meta/software_development_process/2.requirements/features/feature_006.opencode_process_enforcement/plan/PLAN.md`
- **TDD enforcement feature:**
  `.meta/software_development_process/2.requirements/features/feature_016.tdd_enforcement/`
- **TDD spec (Kent Beck):** `.meta/doc/tdd/tdd-agent-spec.md`

**When in doubt: read `META_HARNESS.md` first, then `omt_agent_guide.md` §2 "Phase Model", §11.4 "TDD Workflow", and §12 "Essential vs. Optional".**
