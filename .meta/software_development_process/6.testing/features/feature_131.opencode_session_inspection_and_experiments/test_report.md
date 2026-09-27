# Test Report — feature_131.opencode_session_inspection_and_experiments (Slice 1)

> Task type: major_feature · Slice 1 (schema · adapter · normalize · labels · hierarchy · usage · collect) · 2026-09-27
> Artifacts: `scripts/session_inspect/` (7 modules, 1301 lines) · `tests/scripts/session_inspect/` (6 files) · design_001 + operation_spec_001

## Verdict

**25/25 PASS, 2 skipped (env-gated live smoke)** — `uv run pytest tests/scripts/session_inspect/ -q` in 0.14s. TDD `done` green, `validate-exit` ok (no dangling REDs, no coverage gaps, no failing tests).

## What was verified (design §8 behaviors → tests)

| Behavior | Test | Result |
|---|---|---|
| schema.failure_vocabulary | test_schema.py | PASS — closed 21 names, Finding source_ref, unknown raises |
| adapter.readonly_open | test_adapter.py | PASS — mode=ro, missing → source_unreadable, write raises |
| adapter.capability_discovery | test_adapter.py | PASS — drizzle markers, missing table → schema_unsupported |
| adapter.bounded_selection | test_adapter.py | PASS — directory/id/time bounds, (time_created,id) order, unbounded refused |
| normalize.session_record | test_normalize.py | PASS — ms passthrough, model triple, incomplete on open tool |
| normalize.message_turn_pairing | test_normalize.py | PASS — parentID turn link, user None, zero kept |
| normalize.usage_variant | test_normalize.py | PASS — disjoint / output_includes_reasoning / empty / ambiguous |
| normalize.step_usage | test_normalize.py | PASS — step-finish basis + step-start snapshot |
| normalize.part_taxonomy | test_normalize.py | PASS — 9 types verbatim, unknown passes + finding |
| labels.v1_grammar | test_labels.py | PASS — trial_start identity, malformed → grammar_invalid + raw |
| labels.identity_rules | test_labels.py | PASS — agree/conflict/dedupe/orphan/reversed |
| labels.legacy_discharge | test_labels.py | PASS — 6-label grammar, mapping required, no invented reps |
| labels.echo_immunity | test_labels.py + test_pipeline.py | PASS — title/tool/assistant → echo_not_trial |
| hierarchy.forest | test_hierarchy_usage.py | PASS — direct vs subtree, missing_child, cycle refused, duplicate once-counted |
| usage.bases_and_reconciliation | test_hierarchy_usage.py | PASS — reconciled vs discrepancy + residual, double_counted_basis |
| usage.legacy_metric | test_hierarchy_usage.py | PASS — prompt/completion per variant, null+reason |
| labels.pipeline_end_to_end | test_pipeline.py | PASS — 8-trial mini-matrix → 7 usable + 1 trial_incomplete, echo + orphan findings, per-trial usage |
| adapter.live_smoke | test_adapter.py + test_labels.py (live) | SKIP ×2 by default, opt-in `MH13_LIVE_DB=1` |

## Regression suite

| Suite | Result |
|---|---|
| tests/scripts/session_inspect/ | 25 passed, 2 skipped |
| Full suite (`uv run pytest -q`) | pending at S1 closure — runs before `omt_complete` Testing→Done |

## Boundary check

`git status` at S1: modified `.projects/meta/META.md`, `meta_harness_13/PROJECT.md`, `WORK.md`, `toolbox/*` (pre-existing sync); untracked `feature_131/{req,analysis,design,impl,testing}`, `scripts/session_inspect/`, `tests/scripts/session_inspect/` — no `src/` change, no `129/130` edits, adapter read-only (`mode=ro` asserted by test).

## Limits / next (S2–S6)

S1 is read-only slice only. No query/inspect/trace/cli (S2), no profile/compare/exporter (S3), no manifest/run/collect-validate (S4), no Tier-2 registration or 39-byte budget discharge (S5), no AC1–AC12 acceptance (S6). Live-DB reasoning-bearing reconciliation (A2) needs `MH13_LIVE_DB=1` verification in S2.

---

## Addendum S2 — query / inspect / trace / cli (2026-09-27)

> Slice 2 (design_001 §Slice plan S2) · TDD testlist 5 → red/green per node → refactor → sync (closed orphaned `test_inspect_trace.py` RED via same-node alias) → done, validate-exit ok, no stranded REDs.

### Verdict

**32/32 PASS, 2 skipped (env-gated live smoke)** — `uv run pytest tests/scripts/session_inspect/ -q` in 0.14s. Bridge `tests/features/feature_131.../test_slice1_bridge.py` → **3 passed**. Full regression `uv run pytest -q` → **2041 passed, 2 skipped, 2 deselected** in 94.63s (S1 baseline 2031 passed; +10 S2 tests, no regressions).

### What was verified (design S2 → tests)

| Behavior | Test | Result |
|---|---|---|
| query.typed_query_and_cursor | test_slice2_query.py::test_typed_query_and_cursor | PASS — bounded limit, truncation flag, fetch_page, stale digest → `cursor_stale` |
| query.top_cost | test_slice2_query.py::test_top_cost_no_missing_duplicates | PASS — stable order ses_3 > ses_2, coverage n_sessions=3, no missing/duplicates |
| inspect.paged_content | test_slice2_inspect_trace.py::test_inspect_paged_content | PASS — 5000-char text paged 100/page, truncated flag + total_chars, page 1 ok |
| trace.event_seq_order | test_slice2_inspect_trace.py::test_trace_event_seq_order | PASS — event seq sorted, coverage n_events=3, skeleton messages+parts |
| cli.sessions_and_trace | test_slice2_cli.py::test_cli_sessions_and_trace | PASS — cmd_sessions total=1 ses_c, cmd_trace helper present |
| legacy alias close-out | test_inspect_trace.py (thin same-node alias) | PASS — rename orphan RED closed via sync, canonical tests are `test_slice2_*.py` |

### Boundary check (S2)

- `feature_129/130` scripts untouched; fixtures synthetic only; adapter read-only `mode=ro`.
- TDD same-node lint respected (GOTCHA_TDD_NODE): rename-induced orphan RED closed with same-path GREEN (sync), never by deleting the path.
- Live-DB reasoning-bearing reconciliation (A2) still needs `MH13_LIVE_DB=1` verification in S3.

---

## Addendum S3 — profile / compare / exporter (2026-09-27)

> Slice 3 (design_001 §Slice plan S3) · TDD testlist 5 → red/green per node → refactor (__init__ surface doc) → sync → done, validate-exit ok, no stranded REDs.

### Verdict

**37/37 PASS, 2 skipped (env-gated live smoke)** — `uv run pytest tests/scripts/session_inspect/ -q` in 0.15s (S2 baseline 32 passed; +5 S3 tests). Bridge `tests/features/feature_131.../` → **3 passed** (slice+bridge combined: 40 passed, 2 skipped). Full regression `uv run pytest -q` → **2046 passed, 2 skipped, 2 deselected** in 102.05s (S2 baseline 2041 passed; +5 S3, no regressions).

### What was verified (design S3 → tests)

| Behavior | Test | Result |
|---|---|---|
| profile.hotspots | test_slice3_profile.py::test_profile_hotspots | PASS — message-incremental ranking msg_2 > msg_1, user zero-usage rows skipped, stable order |
| profile.failures | test_slice3_profile.py::test_profile_failures | PASS — repeat bash error ×2 → repeat_tool_error finding with witnesses, facts vs heuristic diagnosis separated |
| compare.sessions | test_slice3_compare.py::test_compare_sessions | PASS — stable id order, delta input 200, warnings key present (drift checks) |
| exporter.bundle | test_slice3_exporter.py::test_exporter_bundle | PASS — atomic JSON/report/manifest write, digest-bound detail_ref, replay reproduces digest |
| profile.compare_integration | test_slice3_integration.py::test_s3_integration | PASS — hotspots → compare → export → replay end-to-end, span_usage explicitly `span_usage_unavailable` (never smeared) |

### Boundary check (S3)

- `feature_129/130` scripts untouched; fixtures synthetic only; adapter read-only `mode=ro` (exporter writes only to explicit `dest`, atomically via tmp+rename).
- TDD batch-N warning noted (2 tests in profile file, related behaviors grouped); same-node lint respected throughout.
- Stdlib-only guard holds (new modules: json/hashlib/os/pathlib/typing only).
- Live-DB reasoning-bearing reconciliation (A2) still needs `MH13_LIVE_DB=1` verification in S4.

---

## Addendum S4 — manifest / collect / evaluate (2026-09-27)

> Slice 4 (design_001 §Slice plan S4) · TDD testlist 5 → red/green per node → refactor (__init__ surface doc) → sync → done, validate-exit ok, no stranded REDs. `run` stays explicitly effectful and gated per PROJECT.md fallback clause.

### Verdict

**42/42 PASS, 2 skipped (env-gated live smoke)** — `uv run pytest tests/scripts/session_inspect/ -q` in 0.17s (S3 baseline 37 passed; +5 S4 tests). Bridge `tests/features/feature_131.../` → **3 passed** (slice+bridge combined: 45 passed, 2 skipped). Full regression `uv run pytest -q` → **2051 passed, 2 skipped, 2 deselected** in 101.60s (S3 baseline 2046 passed; +5 S4, no regressions).

### What was verified (design S4 → tests)

| Behavior | Test | Result |
|---|---|---|
| manifest.contract | test_slice4_manifest.py::test_manifest_contract | PASS — versioned create/validate, missing variants → `manifest_invalid` |
| manifest.dry_run | test_slice4_manifest.py::test_manifest_dry_run | PASS — 1×2×2 matrix → 4 trials, `[mh13.experiment]` label lines, `executed: False` |
| collect.binding | test_slice4_collect.py::test_collect_binding | PASS — 4-trial labeled fixture vs manifest: 3 usable, incomplete `case02_candidate_rep01`, N=3 |
| evaluate.comparison | test_slice4_evaluate.py::test_evaluate_comparison | PASS — case01 cheaper+quality-held → candidate_supported; case02 cheaper+FAILED → inconclusive/quality_not_held; overall inconclusive |
| run.gated | test_slice4_evaluate.py::test_run_gated | PASS — `request_run` → unavailable/no_safe_launch, executed False; `replay_n` recomputes N without increase |

### Boundary check (S4)

- `feature_129/130` scripts untouched; fixtures synthetic only; no model calls, no OpenCode launches in tests (dry-run plans only).
- TDD batch-N warnings noted (2 tests per file, related behaviors grouped); same-node lint respected; bootstrap skips logged (TDD_BOOTSTRAP ×2: profile S3, manifest S4).
- Stdlib-only guard holds (new modules: typing/json only + reuse of labels/collect/manifest).
- Live-DB reasoning-bearing reconciliation (A2) still needs `MH13_LIVE_DB=1` verification in S5.
- M4 pilot gate (2 variants × 2 cases × 3 independent reps = 12 trials) NOT yet run — needs explicit experiment invocation (S6 acceptance); `run` correctly returns unavailable until Tier-2 invocation path exists.
