# Feature 076: Workflow Index And Repair Quickfix

> **Status:** [x] Done
> **Created:** 2026-09-12
> **WORK.md task:** meta_harness_8 → Paused/T1-6

---

## Summary

The `.workflows/` catalog is agent-read markdown with no machine checking: `meta_harness_evolution.md` step 6 directs edits at the **generated projection** `./meta/META_HARNESS.md` (wrong path — canonical source is `.meta/META_HARNESS.omt`), and each workflow's OMT stance (`follow`/`override`) lives only as prose in `# Rules` line 1. This feature (T1-6 of `meta_harness_8`; user picked a `harnessc` CLI subcommand over a new `omt_workflow` tool — tool budget ~99% full) repairs the contradiction, adds machine-readable authority markers, and makes the compiler enforce the catalog contract plus a discoverability command.

## Scope (one sentence — what "done" looks like)

`harnessc.py check` rejects a workflow file that lacks a valid `<!-- authority: follow|override -->` marker or that instructs editing generated projections (`META_HARNESS.md`/`AGENTS.md`), and `harnessc.py workflows [--subject X] [--plan <workflow>]` lists the 6 manifest-backed catalog workflows and prints a workflow's strategy steps.

## Task type

minor_feature

---

## Design note (decisions)

- **D1 — marker format:** HTML comment `<!-- authority: follow|override -->` on line 1 of each workflow file (machine-parsable, invisible in rendered markdown, sits next to the human prose `# Rules` line 1 it mirrors).
- **D2 — authority values:** `agentx/feature_fix` → follow; `agentx/consistency_enforcement`, `meta_harness` (evolution, project, pause one-shot) → override. Stance must agree with existing prose `# Rules` line 1.
- **D3 — discovery source:** filesystem scan of subject dirs cross-checked against each subject `META.md`'s workflow-table rows (path cell, backticked, ending in `.md`). Manifest-listed files without valid markers → **error**; on-disk `.md` files absent from the subject manifest (e.g. `meta_harness_development_self_evaluation.md` — no `# Rules`, not indexed) → **warning** (drift flag, not failure).
- **D4 — projection-edit rule:** a workflow file line matching `(update|edit|modify|write) … (META_HARNESS.md|AGENTS.md)` — or the wrong path `./meta/META_HARNESS.md` — is an error pointing at the `.omt` canonical source + `harnessc.py build`.
- **D5 — `workflows` subcommand output:** list mode prints `<subject>/<name>  authority=<follow|override>  <rel path>`; `--subject X` filters; `--plan <name>` prints the strategy section's numbered steps. No corpus parse needed (short-circuited in `main()` like `stage`/`init`).
- **D6 — template-tree immunity:** `check_workflows` no-ops when `<root>/.workflows` is absent (init-emitted tier trees have no catalog).

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | this file (Summary + Scope) | [x] |
| Analysis | Analysis doc | this file (sizing evidence: contradiction in `.workflows/meta_harness/loops/meta_harness_evolution.md` step 6; user picked harnessc CLI over `omt_workflow` tool) | [x] |
| Design | Design doc | this file (§Design note, D1–D6) | [x] |
| Implementation | Impl notes | `scripts/omt/harnessc.py` ("workflow catalog (feature_076 T1-6)" block) + 6 workflow files under `.workflows/` | [x] |
| Testing | Test report | `6.testing/features/feature_076.workflow_index_and_repair_quickfix/test_report.md` | [x] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.
