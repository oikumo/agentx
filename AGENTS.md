# System Rules

> **⚠️ MANDATORY FIRST STEP:** On the **first prompt**, read `WORK.md` and display it.
>
> **⚠️ MANDATORY SECOND STEP:** Read this `AGENTS.md` in full.
>
> **⚠️ MANDATORY THIRD STEP:** Follow the OMT++ methodology in
> `.meta/software_development_process/omt_agent_guide.md` for any programming task.
>
> **⚠️ MANDATORY:** Always use `uv` to run Python (including tests). Bare
> `python`/`pip`/`pytest` are denied by `opencode.jsonc`.

> **Harness:** This project is driven by **opencode only**. Enforcement lives in
> `opencode.jsonc` (permissions) and `.opencode/plugin/omt_enforcer.ts` (the OMT++ gate).

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

---

## Core Directives

**NEVER** (enforced by `opencode.jsonc` / the gate — the action is blocked):
1. Commit or push code (`git commit` / `git push` are denied).
2. Read or modify `.env` / secrets.
3. Add dependencies without approval.
4. Modify `tests/` without approval (use canary tests + `omt_skip{scope:"tests"}`).
5. Change `README.md`, `uv.lock`, or `LICENSE` (unless explicitly asked).
6. Edit `src/` without first declaring a phase via `omt_phase`.

**ALWAYS:**
7. Check `git log` / `git status` before changes.
8. Understand the project by reading the `META.md` file in each directory.
9. Follow OMT++ (`omt_agent_guide.md`) for all code changes.
10. Declare your phase (`omt_phase`) before touching `src/`.
11. Produce the phase artifacts your task size requires (guide §12); scaffold features with
    `scripts/omt/new_feature.py` so artifacts stay consistently named (no ad-hoc `*_PROOF.md`).

---

## Tooling (opencode-native)

| Tool | Purpose |
|------|---------|
| `omt_phase` | Declare OMT++ phase; unlocks `src/` edits (plugin) |
| `omt_skip` | Logged process-override escape hatch (plugin) |
| `uv run scripts/omt/mvc_check.py` | MVC++ architecture linter (guide §16) |
| `uv run scripts/omt/new_feature.py "<name>"` | Scaffold a feature's artifacts from `.meta/templates/` |

---

## 📖 References

- **OMT++ methodology:** `.meta/software_development_process/omt_agent_guide.md` (source of truth)
- **Project / requirements / analysis / design / impl / testing:**
  `.meta/software_development_process/{1.project … 7.integration}/`
- **Process enforcement plan:**
  `.meta/software_development_process/2.requirements/features/feature_006.opencode_process_enforcement/plan/PLAN.md`

**When in doubt: read `omt_agent_guide.md` §2 "Phase Model" and §12 "Essential vs. Optional".**
