# Feature 119: Ledger Backed Fix Preview

> **Status:** [x] Done 2026-09-20
> **Created:** 2026-09-20
> **Project:** agentx_concurrent_development (linked at scaffold, origin: scaffold)
> **WORK.md task:** NEXT pick `proj:agentx_concurrent_development` (startup OPT-B menu)

---

## Summary

`omt_q fix_preview(filter?)` no longer returns a hardcoded drift map: it folds
live `foldProjectDrift()`, pins the WORK.md stamped `net_rev`, signs the
envelope with the live HEAD sha, and emits rev-pinned `project.py link` apply
cmds — still strictly read-only (ledger byte-identical across calls).

## Scope (one sentence — what "done" looks like)

Live drift plus stamped-rev-backed read-only fix_preview with filter, 6 goldens green, neighbors green, check/build/e2e green.

## Task type

minor_feature

---

## Summary

<!-- One paragraph: what this feature is and why it exists. -->

## Scope (one sentence — what "done" looks like)

<!-- If you cannot fill this in, you are still in Analysis. -->

## Task type

<!-- bug_fix | minor_feature | major_feature | new_screen | refactor -->

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_119.ledger_backed_fix_preview/` | [x] |
| Analysis | Analysis doc | toolbox analysis (foldProjectDrift/headSha/net_rev sources; in-chat) | [x] |
| Design | Design doc | not required (minor_feature, decl-only) | [x] |
| Implementation | Impl notes | `.opencode/plugins/omt_q.ts` omt_fix_preview live impl | [x] |
| Testing | Test report | `6.testing/features/feature_119.ledger_backed_fix_preview/` | [x] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.
