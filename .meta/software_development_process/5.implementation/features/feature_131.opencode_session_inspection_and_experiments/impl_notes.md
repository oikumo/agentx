# Implementation notes — feature_131.opencode_session_inspection_and_experiments (Slices 1–3)

> S1: 2026-09-27 · design_001 + operation_spec_001 slice 1 · testlist 18 → 12 cycles → refactor → done.
> S2: 2026-09-27 · slice 2 (query · inspect · trace · cli) · testlist 5 → RED→GREEN (query/inspect-trace/cli) → REFACTOR → SYNC (closed orphaned test_inspect_trace.py RED via same-node alias) → DONE green 32 passed.
> S3: 2026-09-27 · slice 3 (profile · compare · exporter) · testlist 5 → RED→GREEN per node → REFACTOR (__init__ surface doc) → SYNC → DONE green 37 passed (slice) / 40 (slice+bridge) / 2046 (full).
> S4: 2026-09-27 · slice 4 (manifest · evaluate; collect binding via existing pipeline) · testlist 5 → RED→GREEN per node → REFACTOR (__init__ surface doc) → SYNC → DONE green 42 passed (slice) / 45 (slice+bridge) / 2051 (full). `run` gated unavailable per fallback clause.

> S1: 2026-09-27 · design_001 + operation_spec_001 slice 1 · testlist 18 → 12 cycles → refactor → done.
> S2: 2026-09-27 · slice 2 (query · inspect · trace · cli) · testlist 5 → RED→GREEN (query/inspect-trace/cli) → REFACTOR → SYNC (closed orphaned test_inspect_trace.py RED via same-node alias) → DONE green 32 passed.

## What changed (NEW, stdlib-only, read-only)

- `scripts/session_inspect/schema.py` (185) — closed `FAILURE_NAMES` (21 names, frozen), `Finding` (unknown name raises), `SourceRef`, `TokenCounters` + `UsageVariant` (disjoint/output_includes_reasoning/empty/ambiguous), `Session/Message/Part/StepUsage` records.
- `scripts/session_inspect/adapter.py` (195) — `OpenCodeSqliteAdapter`: explicit path, `file:?mode=ro` (never immutable=1), one deferred read transaction per snapshot (WAL-safe), `capability_report` (drizzle count/latest + data_migration names), `snapshot(selector)` requires ≥1 bound, `(time_created,id)` ordering, `event_cursor` idempotent, `deletion_coverage_unavailable` coverage.
- `scripts/session_inspect/normalize.py` (174) — rows → records: model JSON → triple, ms passthrough, user tokens None, valid-zero kept (A3), A1 residual `detect_usage_variant`, `step_usage` third basis, unknown part types pass through (`is_known=False` + `schema_unsupported` finding, never dropped).
- `scripts/session_inspect/labels.py` (365) — `[mh13.experiment]` exact-prefix JSON v1 parser (closed events, checkpoint requires id), `parse_legacy_discharge` (requires explicit run_mapping, no invented reps), `bind_labels` (only role=user mints; titles/tool-output/assistant → `echo_not_trial`; trial_start establishes identity, later events must agree; idempotent repeats dedupe; orphan/reversed/conflict → named findings).
- `scripts/session_inspect/hierarchy.py` (140) — `build_forest` (direct vs subtree separate, missing_child → root + finding, cycle → finding + refused None propagated), `subtree_union` (once-counted, duplicate_membership on overlapping roots).
- `scripts/session_inspect/usage.py` (134) — three bases never mixed (`double_counted_basis`), `MetricDefinition` variant-aware `sum_components` (`metric_variant_mismatch`), `reconcile_session` (variant-aware Σ messages vs session cumulative, residual exposed), `legacy_feature130_metrics` (prompt=input+cache_read, completion variant-aware).
- `scripts/session_inspect/collect.py` (99) — slice-1 pipeline: snapshot → normalize → bind → per-trial usage (session-cumulative basis) + usable/excluded classification (`trial_incomplete`), echoes never mint trials.
- `tests/scripts/session_inspect/` (6 files, 25 tests) — schema-faithful tiny SQLite fixtures in `tmp_path`, every A-ambiguity covered, stdlib-guard, env-gated live smoke (`MH13_LIVE_DB=1`) skipped by default.

- S2 (NEW, read-only): `query.py` (135) typed docs + bounded limit + digest-bound cursor (`cursor_stale` on stale/query-mismatch) + `top_cost`; `inspect.py` (65) exact session/part drill-down with addressable text pages; `trace.py` (43) event-seq timeline + skeleton; `cli.py` (51) `cmd_sessions` + `cmd_trace` dev surface. Tests: `test_slice2_query.py` (2), `test_slice2_inspect_trace.py` (2), `test_slice2_cli.py` (1) + legacy alias `test_inspect_trace.py` (2, same-node close-out for rename orphan) — 32 passed total with S1. Rename `test_query.py` → `test_slice2_query.py` closed via GREEN at old node before rename; `test_inspect_trace.py` orphan closed 2026-09-27 via alias + `omt_tdd sync` → `done` green.

## Discipline notes

- `uv` only (no bare python/pip/pytest); `feature_129/130` scripts untouched (contracts consumed, not edited).
- TDD two-hats respected (RED tests/ only, GREEN src/ only); bootstrap skips logged (TDD_BOOTSTRAP ×2); `refactor` + `done` green, `validate-exit` ok.
- Fixture policy: synthetic sanitized rows only, no raw transcript bodies in repo.
- S2–S6 deferred: query/inspect/trace/cli (S2 ✅), profile/compare/exporter (S3 ✅), manifest/collect/evaluate run-gated (S4 ✅), Tier-2 registration + 39-byte budget plan (S5), acceptance (S6).

## S4 modules (NEW, stdlib-only; collect reused from S1)

- `scripts/session_inspect/manifest.py` — `create`/`validate` (strict, `manifest_invalid`), `expand_matrix`, `dry_run` (rendered `[mh13.experiment]` label lines, `executed: False`).
- `scripts/session_inspect/evaluate.py` — `validate_collection` (expected vs observed, missing/unbound/incomplete, independent N = usable only), `compare` (paired per-case quality-gated rule; cheaper failures never win), `request_run` (named unavailable `no_safe_launch`, never launches), `replay_n` (N recompute, never increases).
- Tests: `test_slice4_manifest.py` (2), `test_slice4_collect.py` (1), `test_slice4_evaluate.py` (2) — 5 new, all green.

## S3 modules (NEW, stdlib-only)

- `scripts/session_inspect/profile.py` — `hotspots` (message-incremental ranking, zero-usage user rows skipped, stable order) + `failures` (repeat error-status tool grouping with witness part ids, heuristic retry-loop diagnosis labeled as such).
- `scripts/session_inspect/compare.py` — `compare_sessions` (stable id order, per-session input sums, delta, directory/agent drift warnings) + `span_usage` (explicit `span_usage_unavailable`, never smeared).
- `scripts/session_inspect/exporter.py` — `export_bundle` (versioned snapshot/report/manifest, atomic tmp+rename to explicit dest, digest-bound detail_ref) + `replay_bundle` (digest recompute, no model calls).
- Tests: `test_slice3_profile.py` (2), `test_slice3_compare.py` (1), `test_slice3_exporter.py` (1), `test_slice3_integration.py` (1) — 5 new, all green; TDD batch-N warning (2 tests/file) noted, same-node lint respected.
