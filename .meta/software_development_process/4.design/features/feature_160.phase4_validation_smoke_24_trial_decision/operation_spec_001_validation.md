# Operation Spec — Phase4 validation (feature_160)

> Companion to `design_001_validation.md`. Pinned surface, reuse-only cores.

## manifest.create

- `create(experiment="phase4_validation", run="smoke_24trial", cases=[4 ids], variants=["baseline","treatment"], reps=3, budgets={tokens,time_s,concurrency}, decision_rule="quality_gated_paired_compare")` → `version==1`, validates or raises `manifest_invalid` (never silent default).
- `validate` requires `experiment,run,cases,variants,reps` + `version==MANIFEST_VERSION(1)` + non-empty cases/variants + `reps>=1 int`.

## manifest.expand_matrix

- 24 trials deterministic in-order (seed 0 = in-order, fake slice): `for case × variant × rep` → `{trial,case,variant,rep}`; dry-run basis, no execution.

## run_gate.gate_run

- `check_manifest` → `manifest_invalid` if bad; `check_isolation` refuses dest containing `.env|opencode.db|.git/` → `isolation_unavailable`; `check_budgets` requires `tokens,time_s,concurrency` → `budget_missing`; without `claims` or `explicit_p=False` → `allowed:False reason:no_safe_launch executed:False`.
- This feature asserts refusals only — never passes `explicit_p=True` with claims (live run gated to future explicit pick).

## launcher (fake only)

- `plan_trials(mdoc)` = `expand_matrix` in-order; `dispatch_fake(trial, executor=fn)` calls injected fake once, `executed:False` preserved (live `executed:true` future slice, not used here).

## evaluate

- `validate_collection(manifest, report)` → `{n_expected:24, n_observed, n_usable, missing, unbound, incomplete}`; independent N = usable only.
- `compare(manifest, metrics)` per-case: needs full quality `pass` on every rep of both variants AND candidate cheaper to support; else `inconclusive quality_not_held|missing_variant_reps`; cheaper-failed never wins.

## skill.py + skill_result.py

- `list` → 3 pilots ok; `doctor <id>` → `contract-ok` ×3 (fast hermetic, no full suite).
- `from_session` maps experiment refusals (`MANIFEST_INVALID|MISSING_DB|...`) → `blocked` envelope with `blocker{gate,code,remediation}` + `validate_envelope` clean.

## Tests `test_validation_meta.py::TestValidation`

- 7 goldens as design: manifest-valid, matrix-24, budgets-gate, isolation-guard, smoke-doctor, compare-quality-gated, envelope-mapping. All stdlib, no network, no LLM, no live DB writes.
