# Feature 090: Scaffolds And Lsp Allowlist

> **Status:** [x] Done (2026-09-13)
> **Created:** 2026-09-13
> **WORK.md task:** mh8 T2-7 (meta_harness_8 program)

---

## Summary

Two Phase-C signal-hygiene halves (mh3 P3-10 + P3-11): (1) `new_feature.py`
gains `testing` / `implementation` subcommands that scaffold the later-phase
artifact paths (`.meta/software_development_process/<phase>/features/<slug>/`)
so the §3.11 mis-creation class (repo-root artifacts, test reports that never
get created) is impossible by construction; (2) a known-LSP-error allowlist
(`.meta/lsp_allowlist.json` + `.opencode/lib/enforcer/lsp_filter.ts`) purges
the 9 live pre-existing Pyright errors (main_controller.py, tui/provider.py)
from post-edit tool results — text AND metadata — while new errors still
surface; fail-open on any surprise.

## Scope (one sentence — what "done" looks like)

`new_feature.py testing|implementation --feature <slug>` create the correct
`.meta/.../<phase>/features/<slug>/` stubs (unknown slug / refuse-overwrite →
rc=2, legacy positional path byte-identical), and the pre-existing 4–9 errors
on main_controller.py / tui/provider.py no longer appear in post-edit reports
while a planted new error does — proven by goldens on recorded output shapes.

## Task type

minor_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_090.scaffolds_and_lsp_allowlist/` | [x] |
| Analysis | Analysis doc | `3.analysis/features/feature_090.scaffolds_and_lsp_allowlist/analysis_001_scaffolds_lsp_allowlist.md` | [x] |
| Design | Design doc | n/a (minor_feature — declaration only per §12) | — |
| Implementation | Impl notes | `5.implementation/features/feature_090.scaffolds_and_lsp_allowlist/impl_notes.md` | [x] |
| Testing | Test report | `6.testing/features/feature_090.scaffolds_and_lsp_allowlist/test_report.md` | [x] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.
