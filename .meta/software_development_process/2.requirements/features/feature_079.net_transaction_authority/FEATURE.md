# Feature 079: Net Transaction Authority

> **Status:** [x] Done 2026-09-13 (mh8 T5-1 2A)
> **Created:** 2026-09-12
> **Project:** meta_harness_8 (T5-1 2A `net_transaction_authority` → 2B claims)

---

## Summary

T5-1 2A (`net_transaction_authority`, mh8 strict T5 slice order, D10 lock-first):
close the TOCTOU race in every authoritative net/binding mutation path by
routing them through one local transaction authority — a shared
`CoordinationLock` (flock advisory, `OMT_COORDINATION_ROOT`-scoped) with the
revision check moved INSIDE the critical section, plus `command_id`
idempotency (same ID + same payload = same result; same ID + different
payload = `command_id_conflict`) and stable refusal codes. Solo behavior is
frozen (no `expected_revision`/`command_id` → today's path, D8); managed
callers pass both. Later slices (2B claims/generation, 2C worktrees, 3B
journal) build on this primitive — no worker orchestration in this slice.

## Scope (one sentence — what "done" looks like)

T5-1 2A delivers net transaction authority: shared CoordinationLock with
in-lock revision check on every net/binding mutation path plus command_id
idempotency and stable refusal codes, proven by a two-process same-revision
race test (exactly 1 commit + 1 `stale_revision`) and idempotency goldens.

## Task type

minor_feature (decl-only per §12; short lock design note folded into the test
report per PROJECT.md §Scope)

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_079.net_transaction_authority/` | [ ] |
| Analysis | Analysis doc | `3.analysis/features/feature_079.net_transaction_authority/analysis_001_*.md` | [ ] |
| Design | Design doc | `4.design/features/feature_079.net_transaction_authority/design_001_*.md` | [ ] |
| Implementation | Impl notes | `5.implementation/features/feature_079.net_transaction_authority/` | [ ] |
| Testing | Test report | `6.testing/features/feature_079.net_transaction_authority/` | [ ] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.
