# Feature 011: Fast_Agent

> **Status:** [x] Done (Implementation + Testing complete)
> **Created:** 2026-07-04
> **WORK.md task:** Implement feature_011.fast_agent

---

## Summary

A new **"⚡ Fast Agent"** main-menu option (`f` key) that runs the existing
feature_007 Agent (`Agent` + `AgentController`, no Model-layer changes) through
a streamlined, modal-dialog-driven UX: a stack of Textual `ModalScreen`s
(`Goal` → `Running` → `Reflection` → `Result`). The user describes the goal in
natural language, the agent auto-runs perceive→decide→act→reflect cycles, and
the only thing that pauses forward progress is a self-improvement proposal from
the reflection engine (or an explicit Stop/Pause). The existing Agent screen is
relabeled "⚙️ Advanced Agent" for power users and remains unchanged.

This is the first use of `textual.screen.ModalScreen` in the codebase.

## Scope (one sentence — what "done" looks like)

From the main menu, pressing `f` opens the Fast Agent flow; the user types a
plain-English goal in a modal dialog → the agent auto-runs cycles displaying
live status (cycle #, phase, last tool, last action) → pauses only on a
reflection proposal (Approve / Dismiss / Stop) → ends with a Result modal
(Save session / New goal / Back); all backed by the existing feature_007
`Agent` facade via `AgentAdapter.create_agent(resume=True)`; an `mvc_check`
returns 0 errors on touched files; TUI-pilot e2e tests cover the modal flow.

## Task type

`new_screen` (per `omt_agent_guide.md §12` — requires design doc on disk +
operation spec).

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | FEATURE.md (this doc) | `2.requirements/.../feature_011.fast_agent/FEATURE.md` | [x] |
| Design | Design doc | `4.design/features/feature_011.fast_agent/design_001_fast_agent.md` | [x] |
| Design | Operation spec | `4.design/features/feature_011.fast_agent/operation_spec_001_fast_agent.md` | [x] |
| Implementation | Impl notes | `5.implementation/features/feature_011.fast_agent/impl_notes.md` | [x] |
| Testing | Test report | `6.testing/features/feature_011.fast_agent/test_report.md` | [x] (44 tests pass, 0 regressions) |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.

### Decisions log (from user option selections, 2026-07-04)

| Decision | Choice |
|---|---|
| Engine reuse | Reuse `Agent` + `AgentController` (no Model changes) |
| Simplicity targets | all four: one-goal-at-a-time, auto-run, no raw rule authoring, NL goals |
| UX style | Full Textual `ModalScreen` stack (first in codebase) |
| Existing Agent option | Relabel to "⚙️ Advanced Agent", both buttons visible |
| Sessions | Auto-resume latest snapshot; start fresh if none |
| Auto-run cadence | Cycles back-to-back; pause only on reflection proposal |
| Detail level in Running modal | Just current status (cycle #, phase, last tool, last action) |
| Naming | `⚡ Fast Agent` (key `f`) / `⚙️ Advanced Agent` (key `a`) |
