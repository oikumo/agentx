# Feature 135: Lean Start V1 Variant

> **Status:** [x] Done (implementation shipped; pilot launch is human-gated, mh13 D7)
> **Created:** 2026-09-27
> **WORK.md task:** proj:meta_harness_14 (project home: `.projects/meta/meta_harness_14/PROJECT.md`)

---

## Summary

Reversible single-surface config-swap for the mh14 run001 experiment: flips the
SESSION STARTUP line of `.agents_prompts/build.md` (the `{file:}` include that
rides the system prompt) between the byte-pinned `control` variant and
`lean_start_v1` — control + `LEAN_START_V1` marker + one direct-render clause
that forbids the `startup_table` roundtrip (F4 double-render diet).
`.meta/META_HARNESS.omt` and `AGENTS.md` stay byte-identical across variants:
AGENTS.md "Show ..." is render-agnostic and `@budget agents_md` headroom is
only 73 B (3511/3584), so the variant differs in exactly one factor (D5).

## Scope (one sentence)

DONE = swap script with pinned constants + drift-guard tests green + live
control→lean→control roundtrip byte-clean on the real repo + run001 manifest
and 8 rendered label lines persisted in the project home.

## Task type

minor_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_135.lean_start_v1_variant/` | [x] this file |
| Analysis | Analysis doc | — (PROJECT.md F1–F4 baseline evidence, meta_harness_14) | [x] |
| Design | Design doc | — (minor_feature: `.projects/meta/meta_harness_14/PROJECT.md` D1–D5) | [x] |
| Implementation | Impl notes | `scripts/omt/lean_start_swap.py` | [x] |
| Testing | Test report | `tests/features/feature_135.lean_start_v1_variant/test_lean_start_swap.py` (5 passed) | [x] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.

## Test evidence (2026-09-27)

- `uv run pytest tests/features/feature_135.lean_start_v1_variant/ -q` → **5 passed**
  (pinned-control drift guard · single-factor strip-variant proof · byte-identical
  roundtrip on temp copies · idempotence · unknown-content refusal exit 2 no-write).
- Live: `--status` control → `--variant lean_start_v1` (marker present, `harnessc check`
  OK — 277 records 0 errors, projections untouched) → `--variant control` →
  `git diff` clean on `.agents_prompts/build.md` + `.meta/META_HARNESS.omt` + `AGENTS.md`.
- Harness e2e receipt refreshed before the second harness-surface edit:
  `uv run pytest tests/scripts/omt/test_omt_harness_e2e.py -q` → 1 passed.
