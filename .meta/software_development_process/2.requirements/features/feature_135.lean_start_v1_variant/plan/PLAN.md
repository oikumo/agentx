# PLAN — feature_135: Lean Start V1 Variant

> Task type: **minor_feature** · See `omt_agent_guide.md §12` for the required artifacts.

## Objective

DONE = reversible lean_start_v1 STARTUP config-swap (build.md line only),
drift-guarded + roundtrip-proven, with the run001 manifest and 8 label lines
persisted so the user can launch the human-gated pilot.

## Steps

- [ ] Analysis — (pre-done) mh14 baseline F1–F4 in `.projects/meta/meta_harness_14/PROJECT.md`
- [x] Design — D5 surface decision recorded in PROJECT.md (build.md-only swap; budget evidence)
- [x] Implementation — `scripts/omt/lean_start_swap.py` (+ tests canary for the new test dir)
- [x] Testing — 5 unit tests green; live control→lean→control roundtrip byte-clean; harnessc check OK

## Artifacts produced

- Requirements: `feature_135.lean_start_v1_variant/FEATURE.md` (this dir)
- Design: `.projects/meta/meta_harness_14/PROJECT.md` (D1–D5) — canonical project home
- Implementation: `scripts/omt/lean_start_swap.py`
- Testing: `tests/features/feature_135.lean_start_v1_variant/test_lean_start_swap.py` (5 passed)
- Experiment assets: `.projects/meta/meta_harness_14/run001_manifest.json` + `run001_labels.jsonl`
