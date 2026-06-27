# PLAN — feature_006: opencode Process Enforcement Harness

> **Objective of the META HARNESS:** make every coding agent move through the OMT++
> process (Analysis → Design → Programming → Testing) producing visible artifacts,
> with strict MVC++ / Abstract Partner / DP discipline.
>
> **Objective of THIS improvement:** turn that process from *theatrical* (voluntary text
> checkpoints the agent may ignore) into *real* — mechanically enforced by **opencode
> plugins + permissions** — while staying a **solo-dev learning scaffold**: it gates and
> *teaches*, it does not punish, and it always offers a logged escape hatch.

---

## 1. Problem Statement (why this improvement)

The current harness is well-designed on paper but its enforcement is **not connected to
anything**:

| # | Finding | Evidence | Consequence |
|---|---|---|---|
| 1 | Enforcement is voluntary | `AGENTS.md` threatens "code will be reverted entirely" and demands 3 checkpoint outputs, but no mechanism checks or reverts anything | An agent can ignore the whole process and nothing happens |
| 2 | `AGENTS.md` contradicts the guide | `AGENTS.md` demands full checkpoints for **ANY** change; `omt_agent_guide.md §12` says bug fixes/minor changes skip most artifacts | The strict reading is annoying; the lenient reading is ignored; agents pick whichever suits them |
| 3 | `opencode.jsonc` is inert | First line: `// THIS OPENCODE CONFIGURATION FILE IS JUST FOR REFERENCE PURPOSE` | The one file opencode could enforce with is explicitly disabled |
| 4 | MVC++ rules are unchecked | `omt_agent_guide.md §16` lists grep checks for layer violations; nothing runs them | Architecture erodes silently |
| 5 | Artifact sprawl, no templates | `feature_004/` has 8 ad-hoc `TUI_*` docs; `feature_003/FEATURE.md` is empty; naming is inconsistent | The artifact store becomes noise, defeating "visible artifacts" |
| 6 | No task ↔ artifact traceability | `WORK.md` tasks don't link to their phase artifacts | Can't tell what's been analysed/designed/tested for a given task |

**Scope restriction (confirmed):** the harness targets **opencode only**. Claude Code /
other harnesses are out of scope. Stray `.claude/` config and Claude-format skills are
*not* part of this harness and are treated as cleanup, not integration targets.

**Audience (confirmed):** a single developer using OMT++ as a learning scaffold.
Therefore enforcement is **guiding + gating**, never silently destructive, and every block
carries an OMT++ explanation + the exact next action.

---

## 2. Design Principles for a Solo Learning Scaffold

1. **Gate, don't punish.** Block the *edit that would skip a phase*, with a teaching error
   message. Never auto-revert or delete the developer's work (drop the `AGENTS.md`
   "automatic revert" threat — it is both impossible to honor and hostile to learning).
2. **Scale rigor to task size** (resolves Finding #2). The gate reads the declared
   `task_type` and only demands the artifacts `omt_agent_guide.md §12` requires for that
   size. A bug fix needs a one-line checkpoint; a major feature needs a design doc on disk.
3. **Always an escape hatch — but a logged one.** The developer (or agent, with consent)
   can `skip` the gate; the skip is appended to a ledger with a reason and timestamp. This
   replaces `AGENTS.md`'s "ask Y/N to skip" with something auditable.
4. **Teach on every interaction.** Blocks and warnings quote the relevant OMT++ section so
   the scaffold reinforces the methodology instead of just obstructing.
5. **opencode-native only.** All enforcement lives in `opencode.json(c)` + `.opencode/`.
   No dependency on any other harness.

---

## 3. Target Architecture

```
opencode session
      │
      ├─ opencode.jsonc  ──────────►  permission gates (coarse, declarative)
      │                                 • edit deny: README.md, .env*, uv.lock
      │                                 • edit ask : tests/**           (canary approval)
      │                                 • bash     : enforce `uv run`, deny git commit/push
      │
      └─ .opencode/plugin/omt_enforcer.ts  ──►  process gate (fine, programmatic)
              │
              │  custom tool:  omt_phase   ── agent declares phase/task_type → writes ledger
              │  custom tool:  omt_skip    ── logged escape hatch
              │
              ├─ tool.execute.before(edit|write|patch on src/**)
              │       └─ require a valid ledger entry for THIS session
              │             else throw  ►  teaching message (which checkpoint to run)
              │       └─ if task_type ∈ {major_feature,new_screen}: require design artifact
              │             else throw  ►  point at the missing template
              │
              ├─ tool.execute.after(edit|write on src/**)
              │       └─ run MVC++ linter (uv) on touched file
              │             violations ►  tui.toast.show (non-blocking, guiding)
              │
              └─ event(session.idle)
                      └─ full MVC++ sweep + "phase artifact missing?" reminder toast

ledger:  .meta/.omt/ledger.jsonl   (gitignored, per-session phase declarations + skips)
scripts: scripts/omt/mvc_check.py  (implements omt_agent_guide §16 as runnable checks)
         scripts/omt/new_feature.py (scaffolds a feature's phase artifacts from templates)
templates: .meta/templates/{use_case,design,operation_spec,feature,test_plan}.md
```

---

## 4. Deliverables

### D1 — Make `opencode.jsonc` authoritative (coarse permission gate)
Remove the "reference only" banner. Encode the `AGENTS.md` "NEVER" rules as real
permissions so they cannot be violated even if the plugin is off:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "edit": "allow",
    "read":  { "*": "allow", "*.env": "deny", "*.env.*": "deny" },
    "bash": {
      "*": "ask",
      "uv run *": "allow",
      "uv sync": "allow",
      "git status": "allow", "git log *": "allow", "git diff *": "allow",
      "git commit *": "deny", "git push *": "deny",
      "python *": "deny", "python3 *": "deny", "pip *": "deny", "pytest *": "deny"
    }
  }
}
```

Notes:
- `python*/pytest*` denied so the agent is forced onto `uv run *` (AGENTS.md MANDATORY rule).
- Fine-grained path denies for `edit` (README.md, tests/, uv.lock) are handled in the
  plugin gate (D2), because opencode `edit` permission is coarse; the plugin gives per-path
  control + teaching messages.

### D2 — `.opencode/plugin/omt_enforcer.ts` (the real gate)
The heart of the improvement. Responsibilities:

1. **`omt_phase` custom tool** — the agent calls this to declare its OMT++ position:
   `{ task_type, phase, scope_sentence, files }`. It validates the declaration, writes a
   ledger entry keyed by `sessionID`, and (for feature-sized work) scaffolds missing
   artifact templates via D4. Returns a confirmation the agent shows the user — this is the
   *real* version of `AGENTS.md`'s "PROCESS CHECK / ARTIFACT CHECK / COMPLIANCE" output.
2. **`omt_skip` custom tool** — records `{ reason, scope }` to the ledger and unlocks edits
   for the session. The auditable escape hatch.
3. **`tool.execute.before`** for `edit|write|patch`:
   - Resolve target path from `output.args` (`filePath`/`path`).
   - If path under `tests/**` → require `tests_approved` flag in ledger, else throw the
     canary-test approval message.
   - If path is `README.md`, `.env*`, `uv.lock`, or `LICENSE` → throw (deny).
   - If path under `src/**` → require an active ledger phase for this session; if
     `task_type` demands a design/analysis artifact (per §12 matrix) and it's absent →
     throw a message naming the exact template to fill.
   - All throws are **teaching messages**: what rule, which OMT++ section, the one command
     to satisfy it.
4. **`tool.execute.after`** for `edit|write` on `src/**`: run `scripts/omt/mvc_check.py`
   on the touched file via `$`; if violations, `tui.toast.show` a concise warning (does
   **not** block — guiding).
5. **`event` / `session.idle`**: full `mvc_check.py` sweep + reminder if the active task's
   phase artifacts are still missing.

> **Spike (do first, see §7 step 0):** confirm `input.sessionID` is present on
> `tool.execute.before`, confirm the plugin dir is `.opencode/plugin/` vs `.opencode/plugins/`
> on the installed opencode version, and confirm custom-tool registration shape. These are
> the only API assumptions; everything else is verified.

### D3 — `scripts/omt/mvc_check.py` (runnable MVC++ linter)
Implements `omt_agent_guide.md §16` as a real check (run with `uv run`):
- View imports Model (`from .*model` in `*_view.py`)
- Controller contains UI/`print`/`console` code
- Model imports `ui`
- Abstract Partner not an `ABC` / missing `@abstractmethod`
- SQL outside `*_db.py` / `DP_*`
- `*Controller` class living under `model/`
- God controller (`*_controller.py` > 300 lines)

Output: machine-readable (JSON) for the plugin + human-readable for direct CLI use.
Exit non-zero on violation so it can also serve as a pre-flight the agent runs manually.

### D4 — Artifact templates + scaffolder (resolves Findings #5, #6)
- `.meta/templates/`: `use_case.md`, `analysis.md`, `design.md`, `operation_spec.md`,
  `feature.md`, `test_plan.md` — each mirrors the structures already in
  `omt_agent_guide.md` (§10 operation spec, §11 test plan, etc.).
- `scripts/omt/new_feature.py`: `uv run scripts/omt/new_feature.py "<name>"` creates
  `feature_00N.<name>/` with `FEATURE.md` + `plan/PLAN.md` from templates and a **naming
  convention** (`analysis_NNN_*.md`, `design_NNN_*.md`) so sprawl like the 8 `TUI_*` files
  can't recur. `omt_phase` calls this automatically for feature-sized tasks.
- **Traceability:** `FEATURE.md` template has a "Phase artifacts" table linking to each
  phase doc; `omt_phase` appends the active task's artifact paths back into `WORK.md` under
  the task line.

### D5 — Rewrite `AGENTS.md` to match reality (resolves Finding #2)
Slim it down. Replace the unenforceable revert theatre + duplicated checklists with:
- A short "How enforcement actually works here" section pointing at the plugin + `omt_phase`.
- The single source of process truth stays `omt_agent_guide.md`.
- The adaptive rule stated once: *"Run `omt_phase` before editing `src/`. The gate asks
  only for the artifacts your task size needs (see guide §12)."*
- Keep `omt_agent_guide.md` unchanged — it is the strong asset.

### D6 — Cleanup (opencode-native consolidation)
- Move `.agents/skills/python-static-analysis` into opencode's skill mechanism (or fold its
  checks into `mvc_check.py`); remove the Claude-format copy.
- Note `.claude/` as out-of-harness in `.gitignore` or delete if unused.
- Add `.meta/.omt/` to `.gitignore` (runtime ledger, not an artifact).

---

## 5. Enforcement Matrix (what the gate requires, by task type)

Derived directly from `omt_agent_guide.md §12` so the gate and the guide agree:

| task_type        | `omt_phase` required? | Artifact gate before `src/` edit | tests/ edit |
|------------------|----------------------|----------------------------------|-------------|
| bug_fix          | Yes (1-line)         | none (warn only)                 | ask + canary |
| minor_feature    | Yes                  | operation list (quick)           | ask + canary |
| major_feature    | Yes                  | design doc on disk               | ask + canary |
| new_screen       | Yes                  | use case + design doc on disk    | ask + canary |
| refactor         | Yes                  | none, but MVC++ check must pass  | ask + canary |
| test             | Yes                  | n/a                              | ask + canary |
| docs             | No                   | n/a                              | n/a |

`tui.toast` MVC++ warnings fire for **all** `src/` edits regardless of type (guiding).

---

## 6. UX Walkthrough (solo dev, learning)

```
dev: "fix the RAG repository selection returning None"

agent calls omt_phase {task_type: "bug_fix", phase: "Testing",
                        scope_sentence: "selection returns a repo, never None",
                        files: ["src/agentx/model/rag/rag.py"]}
   → ledger entry written; gate unlocked for bug_fix
   → tool returns a tidy PROCESS CHECK block (the real one)

agent edits rag.py
   → tool.execute.before: bug_fix + src/ + active ledger ⇒ ALLOW
   → tool.execute.after: mvc_check finds no violation ⇒ no toast

dev: "now add a Settings screen"
agent edits src/.../settings_view.py WITHOUT omt_phase
   → tool.execute.before THROWS:
     "⛔ OMT++ gate: editing src/ for a new screen needs a use case + design doc first
      (guide §7, §12). Run omt_phase{task_type:'new_screen'} — I'll scaffold the templates.
      To override: omt_skip{reason:...}."
```

The agent is *taught*, handed the next command, and never loses work.

---

## 7. Implementation Steps (incremental, each independently testable)

**Step 0 — API spike (½ day).** In a throwaway `.opencode/plugin/probe.ts`, log
`tool.execute.before` `input`/`output` shapes; confirm `sessionID`, plugin dir name,
custom-tool registration, and that a thrown error blocks the call + reaches the model.
Adjust §3/§4 details to the installed opencode version. *Gate the rest of the plan on this.*

**Step 1 — Permissions (D1).** Make `opencode.jsonc` live. Verify `uv run` allowed,
`git commit`/`python` denied. Lowest-risk, immediate value.

**Step 2 — MVC++ linter (D3).** Pure Python, no opencode dependency. Validate against the
current `src/` (it should flag real issues or pass clean). Reusable on its own.

**Step 3 — Templates + scaffolder (D4).** Generate a throwaway feature, confirm structure +
naming + WORK.md back-link.

**Step 4 — Plugin gate (D2).** Wire `omt_phase`, `omt_skip`, the before/after hooks, and
`session.idle`. Test: edit `src/` with and without a checkpoint; confirm block + teaching
message + skip path.

**Step 5 — Docs (D5) + cleanup (D6).** Rewrite `AGENTS.md`, consolidate skills, update
`.gitignore`.

**Step 6 — Dogfood.** Run one real bug_fix and one real feature end-to-end through the gate;
capture friction; tune the §5 matrix.

---

## 8. Acceptance Criteria

- [ ] Editing a file in `src/` **without** a prior `omt_phase` is **blocked** with a teaching
      message (not a passive instruction).
- [ ] A `bug_fix` checkpoint unlocks `src/` edits with no artifact demand; a `new_screen`
      checkpoint is blocked until the design/use-case artifact exists.
- [ ] `git commit`, `git push`, bare `python`/`pytest`, and edits to `README.md`/`.env` are
      denied by config/plugin.
- [ ] An MVC++ violation introduced into a `*_view.py` raises a non-blocking toast and is
      reported by `uv run scripts/omt/mvc_check.py`.
- [ ] `omt_skip` unlocks edits and writes an auditable ledger entry.
- [ ] `AGENTS.md` no longer contains unenforceable claims; the §12 matrix and the gate agree.
- [ ] A new feature scaffolded by `new_feature.py` has consistent, named artifacts and a
      `WORK.md` back-link — no ad-hoc `*_PROOF.md` sprawl.

---

## 9. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| opencode plugin API differs from docs on the installed version | Step 0 spike gates everything; keep D1/D3 (config + linter) working even if the plugin is unavailable |
| Gate becomes annoying → developer disables it | Solo-scaffold tuning: cheap `omt_phase`, always-available `omt_skip`, teaching (not nagging) messages; toasts not blocks for style issues |
| `sessionID` not exposed in `before` hook | Fall back to a single project-level ledger with a short TTL instead of per-session keying |
| Plugin throws block legitimate emergency fixes | `omt_skip` escape hatch + config-level allowance is never destructive |
| Over-engineering for a solo learner | Steps are independently valuable; can stop after Step 2 (linter) or Step 4 (gate) and still gain |

---

## 10. Out of Scope

- Claude Code / other harness integration (harness is opencode-only).
- CI/remote enforcement (local opencode session only).
- Changing the OMT++ methodology itself (`omt_agent_guide.md` stays the source of truth).
- Auto-reverting agent work (explicitly rejected as hostile to a learning scaffold).

---

## 11. Open Questions for the Developer — RESOLVED (2026-06-27)

1. **Escape-hatch trust** → **Agent may self-skip, logged.** `omt_skip` stays an
   agent-callable tool; every use is recorded in `.meta/.omt/ledger.jsonl`.
2. **Linter severity** → **Block hard-errors, warn soft ones.** The after-hook blocks an
   edit that *introduces* a hard MVC++ error (View↔Model leak, non-ABC partner,
   controller-in-model, view-creates-controller, syntax error); soft findings
   (SQL-outside-DP, god controller, controller-UI) stay advisory toasts. Pre-existing
   legacy errors do **not** block — the gate snapshots hard errors pre-edit and blocks only
   newly introduced ones (verified by delta tests).
3. **Stop point** → **Full gate shipped and live-tested; now hardening.** The gate works in
   a real opencode session. Hardening done: the gate **auto-detects** a feature's design
   artifact from its slug under `4.design/features/feature_<n>/`, so `major_feature`/
   `new_screen` gating no longer depends on the agent passing `design_doc` by hand.

Remaining: dogfood through real tasks; consider fixing the 2 legacy violations
(`IMainViewPartner` → ABC, `SessionController` → out of `model/`) so the gate guards a clean
baseline.
```
