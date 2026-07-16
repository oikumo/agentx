# Feature 021: Meta Harness Think Anywhere

> **Status:** [x] Done
> **Created:** 2026-07-16
> **WORK.md task:** `feature_021.meta_harness_think_anywhere`
> **Source theory:** `.meta/doc/harness/think_anywhere_langchain.md`

---

## Summary

Adapts the Think-Anywhere paper's *inline on-demand reasoning* to the META HARNESS as a
**persistent, grep-friendly agent annotation/memory layer**. Where the paper interleaves
ephemeral `<thinkanywhere>` blocks inside generated code, this feature lets opencode drop
compact `TA:` thought-tags **inline in real files** (META HARNESS docs, agentx source, the
opencode plugin/config surface) so hard-won context survives across sessions and context
windows. Thoughts are retrieved token-minimally via the standard `grep`/`glob` tools (and a
dedicated `omt_think_list`), indexed in a compact JSONL sidecar, and **enforced**: every
session mechanically surfaces a digest of existing thoughts, and a blocking *think-gate*
refuses to edit any file that carries `TA:` warnings until the agent has consulted them.
Thoughts are allowed **anywhere except protected files** (`.env*`, `README.md`, `uv.lock`,
`LICENSE`) and JSON (would break syntax).

## Scope (one sentence — what "done" looks like)

opencode can add (`omt_think`), retrieve (`omt_think_list`), and remove (`omt_think_remove`)
inline `TA:` thought-tags in any non-protected file, with a synced JSONL index, a per-session
mechanical digest, and a blocking think-gate — all token-minimal and covered by TDD + e2e.

## Task type

`major_feature` (touches the OMT enforcement surface: new plugin + enforcer gate + config + docs)

---

## Use case

### Actor
opencode coding agent (the `build` agent) across sessions / context windows.

### Goal
Recover and contribute non-obvious context about the codebase cheaply, without re-reading
whole files or relying on volatile conversation memory.

### Preconditions
- A repo with the META HARNESS installed (plugins + enforcer active).

### Main flow
1. Session starts → enforcer/plugin greps `TA:` across the repo, returns a capped digest
   (count + `file:line: TA: …` lines) so the agent recovers prior thoughts immediately.
2. Agent edits a file that contains `TA:` thoughts → think-gate blocks the first such edit
   until the agent has consulted thoughts this session (`omt_think_list`); block message
   shows the file's own `TA:` lines.
3. Agent learns a non-obvious fact (gotcha, "why this is here", risk, cross-ref) → calls
   `omt_think{path, thought, line?, category?}` → a language-aware `TA:` comment is inserted
   inline and the JSONL index is appended.
4. Agent later searches → `omt_think_list{path?, category?, query?}` (or plain `grep TA:`)
   returns matching `file:line: TA: …` lines.

### Alternate / exception flows
- **Protected target** → `omt_think` refuses (`.env*`, `README.md`, `uv.lock`, `LICENSE`).
- **JSON / unsupported syntax** → `omt_think` refuses with a hint (no inline comment possible).
- **No thoughts exist** → session digest reports `0 thoughts` and reminds how to add one.
- **Escape needed** → `omt_skip{scope:"all"}` does NOT bypass the think-gate (thoughts are
  safety-relevant warnings); only `omt_think_list` / the block's own surfacing clears it.

### Postconditions
- Every `TA:` tag is a valid single-line comment in its host language.
- The JSONL index is append-only consistent with inline tags (best-effort; inline is source of truth).
- Each session sees the digest; edits to thought-carrying files are gated.

## Operations extracted
- `omt_think(path, thought, line?, category?)` → insert inline `TA:` comment + index append
- `omt_think_list(path?, category?, query?)` → grep-backed retrieval + mark session consulted
- `omt_think_remove(path, line?)` → remove a `TA:` comment + index reconcile
- `session.start` → digest (mechanical, every session)
- `thinkGateDecision({hasThoughts, consulted})` → "allow" | "block" (pure, in omt_enforcer.ts)

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_021.meta_harness_think_anywhere/FEATURE.md` | [x] |
| Analysis | Analysis doc | `3.analysis/features/feature_021.meta_harness_think_anywhere/analysis_001_think_anywhere.md` | [x] |
| Design | Design doc | `4.design/features/feature_021.meta_harness_think_anywhere/design_001_think_anywhere.md` | [x] |
| Implementation | Impl notes | `5.implementation/features/feature_021.meta_harness_think_anywhere/implementation_notes.md` | [x] |
| Testing | Test report | `6.testing/features/feature_021.meta_harness_think_anywhere/test_report.md` | [x] |

**Naming convention:** phase docs are `analysis_NNN_<topic>.md`, `design_NNN_<topic>.md`.
