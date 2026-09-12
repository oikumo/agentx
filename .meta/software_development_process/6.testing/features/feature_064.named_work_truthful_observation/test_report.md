# Test report — feature_064.named_work_truthful_observation (slice 1)

Date: 2026-09-12. Verdict: DONE (minor_feature, Programming→Testing→Done).

## Evidence

- New `tests/features/feature_064.named_work_truthful_observation/test_named_work_truthful_observation.py`
  (17 tests): registry round-trip (3) + validation matrix (7) + probe
  observation/menu/basis (7). All hermetic via `OMT_NET_DIR`/`OMT_LEDGER_PATH`
  tmp bundles; no live-bundle mutation.
- e2e check #23 (`tests/scripts/omt/test_omt_harness_e2e.py`): static pins for
  `validate_task_bindings`, sidecar `task_bindings`, `_task_observation`,
  `_task_menu`, basis label, empty/blocked meanings. e2e 1/1.
- `harnessc check` 0 errors + `build` OK (263 records, budgets green).
- Full suite: 2015 passed + 1 known live-flake
  (`test_nav_reminder_deferred_after_nav_first`, passes 2/2 in isolation —
  same family as iter 5 flakes, unrelated files).
- Net package suite: 417/417 (incl. existing probe/splice/sync/synthesize/
  invariant pins — additive-only confirmed).

## Behaviors pinned

Bindings⊆tokens per place with anonymous remainder (7-done legacy bundle
validates, no backfill); duplicate/bad-place/oversubscribed/non-list rejected;
save/load round-trip; legacy sidecar loads []; observation states
inconsistent>executing>ready>awaiting_capacity>drained_complete>idle_empty
with reasons; task-bound menu (`implement/verify/review <id>`) with transition
fallback; `advice.basis` labeled initial-marking analysis.

## Deferred (slices 2–3, not tested here)

Write path/CLI op, atomic claims, generation fencing, checkpoints/transfer/
recovery, serialized integration, objective-level acceptance. No task reaches
Done on self-report — specified in design_001, unenforced until slice 3.
