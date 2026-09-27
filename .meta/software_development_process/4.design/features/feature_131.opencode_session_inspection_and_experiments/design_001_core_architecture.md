# Design 001 — Core architecture and contracts (slice 1: read · normalize · label · tree · usage)

Feature: `feature_131.opencode_session_inspection_and_experiments` · Phase: Design · Date: 2026-09-26
Inputs: `analysis_001_real_log_inventory.md` (verified schema, A1–A10 ambiguity register) · project proposal `.projects/meta/meta_harness_13/PROJECT.md` (capability table, label protocol v1, token/attribution contract, experiment lifecycle).

## 1. Architecture

One Python package owns adapters, normalized evidence, queries, attribution, labels, and experiment evaluation. **Stdlib only** (sqlite3/json/dataclasses/hashlib/re/typing) — no `src/agentx/` dependency, no second runtime; the future Tier-2 plugin (`omt_session`) proxies this core. Home (finalized per proposal §architecture):

```
scripts/session_inspect/
  __init__.py      # public API re-exports
  schema.py        # normalized records + closed failure vocabulary
  adapter.py       # OpenCodeSqliteAdapter: read-only source access + capability discovery + snapshot
  normalize.py     # source rows → normalized records (model triple, ms assertion, A1 variant detection)
  labels.py        # [mh13.experiment] v1 parser/binder + legacy [harness_reason:discharge] adapter + echo immunity
  hierarchy.py     # session tree: direct vs subtree usage, missing children, cycles, duplicate membership
  usage.py         # token bases, variant-aware component sums, reconciliation, versioned metric definitions
  query.py         # typed query documents, bounded execution, cursors           (slice 2)
  inspect.py       # deep drill-down + pagination                               (slice 2)
  trace.py         # timeline reconstruction from event seq                      (slice 2)
  profile.py       # usage hotspots, retry/failure witnesses                     (slice 3)
  compare.py       # session/span/trial comparison                               (slice 3)
  manifest.py      # experiment manifest contract + validation                   (slice 4)
  collect.py       # label→trial binding, membership, evidence snapshot          (slice 4)
  evaluate.py      # quality-aware comparison, predeclared decision rule         (slice 4)
  exporter.py      # versioned JSON/JSONL export + digests                      (slice 3)
  cli.py           # local dev surface (M1–M3); Tier-2 plugin reuses the core    (slice 2)
```

Slice plan (each slice = one TDD pass, all inside feature_131): **S1 (this design)** schema+adapter+normalize+labels+hierarchy+usage → S2 query/inspect/trace/cli → S3 profile/compare/exporter → S4 manifest/collect/evaluate (experiment lifecycle; `run` stays explicitly effectful and gated) → S5 Tier-2 registration (plugin, `.omt`, budget plan — separate design addendum for the 39-byte `tool_args` headroom problem) → S6 acceptance.

## 2. Normalized records (`schema.py`)

Dataclasses, JSON-serializable, epoch-ms asserted at the adapter boundary (A5):

- `SourceRef{path, schema_markers, snapshot_digest?}` — provenance on every finding (proposal §capture contract 6).
- `SessionRecord{id, parent_id?, directory, title, agent, model(ModelTriple|None), time{created,updated,compacting?,archived?}, tokens(TokenCounters|None), cost, lifecycle{is_child, has_compaction_part, completion}}`. `completion ∈ {complete|incomplete|unknown}` — `incomplete` when open tool parts / absent completion evidence (A7).
- `MessageRecord{id, session_id, role, parent_id (turn link), time_created, tokens(TokenCounters|None), cost?, model?}` — user messages carry `tokens=None` (keys absent), assistant messages carry per-generation increments; all-zero counters are **valid data** (A3).
- `PartRecord{id, message_id, session_id, type, time{created,updated}, payload(dict)}` — payload preserved verbatim per type union (`step-start|step-finish|tool|text|reasoning|patch|file|compaction|agent`).
- `TokenCounters{input, output, reasoning, cache_read, cache_write, total?}` with `UsageVariant`:
  `disjoint` (total = in+out+reas+cr+cw) · `output_includes_reasoning` (total = in+out+cr+cw) · `empty` (all zero) · `ambiguous` (neither) — **computed at normalize time by residual test** (A1), never assumed.
- `LabelRecord{raw, protocol, identity(TrialIdentity), event, fields, source{session_id,message_id,part_id}, verified}`.
- `TrialIdentity{protocol_version, experiment, run, trial, case, variant, rep, attempt}`.

**Failure vocabulary (closed, frozen in S1):** `source_unreadable` · `schema_unsupported` · `inclusion_semantics_ambiguous` · `deletion_coverage_unavailable` · `session_incomplete` · `missing_child` · `hierarchy_cycle` · `duplicate_membership` · `label_grammar_invalid` · `label_identity_conflict` · `label_orphan_event` · `span_reversed` · `label_unbound_to_manifest` · `echo_not_trial` · `query_limit_exceeded` · `cursor_stale` · `metric_variant_mismatch` · `reconciliation_discrepancy` · `double_counted_basis` · `trial_incomplete` · `manifest_invalid`. Findings carry `{name, detail, source_ref}`; no stringly-typed errors.

## 3. Adapter (`adapter.py`) — capture and evidence contract

1. **Explicit source selection:** constructor takes an explicit DB path (default documented candidate `~/.local/share/opencode/opencode.db`); bounded selectors only (directory, ids, time interval) — never unbounded scans.
2. **Read-only, WAL-safe (A10):** open via `sqlite3.connect("file:<path>?mode=ro", uri=True)`; each capture/read runs in ONE deferred transaction so main+WAL are read consistently; `immutable=1` is forbidden for live DBs. A write attempt inside the adapter raises (assert in tests).
3. **Capability discovery before extraction:** verify required tables/columns; report `__drizzle_migrations` count + latest `created_at` and `data_migration` names as `schema_markers`; missing surface → `schema_unsupported` listing what's absent. Never silently drop unknown record types — pass through with a coverage finding.
4. **Identity:** retain all source ids; timestamp ties break by stable id, never by invented causal order (A8).
5. **Incremental capture (event stream):** `event(aggregate_id=session, seq)` rows carry full part/message payloads → cursor = per-session max seq; replay is idempotent (same seq range → same records; re-reading replaces, never double-counts). Deletion detection is **unavailable** (A6) and reported as such.
6. **Labels bind from `role=user` message part text** (verified path — `session_input` is empty in the real DB). Title echoes and tool-output echoes are recorded as `echo_not_trial`, never as trials. Reasoning text is data, never re-labeled (proposal §capture 5).

## 4. Usage and attribution (`usage.py`)

- **Three bases, never mixed:** `session_cumulative` (session columns) · `message_incremental` · `step_incremental` (step-finish). Any API that could combine bases (e.g. subtree totals + message sums) detects the double count and emits `double_counted_basis` instead of a number.
- **Variant-aware component sums:** derived totals sum *named components* under a declared `MetricDefinition{name, version, components, variant_policy}` — never the source `total` unless the record's variant is verified compatible; mixed-variant aggregation requires the policy to say how each variant contributes, else `metric_variant_mismatch`.
- **Legacy metric (explicit, versioned):** `legacy_feature130_prompt = input + cache_read`, `legacy_feature130_completion = output_disjoint + reasoning | output` (per record variant). Historical comparisons reproduce the feature-130 numbers; nothing else uses this name.
- **Reconciliation:** per session, compare `session_cumulative` vs variant-aware Σ(message components) → equal ⇒ `reconciled`; else `reconciliation_discrepancy` with the residual exposed, never smeared (A2 tracked; the real-DB reasoning-bearing case is exercised by the env-gated live test).
- **Subtree accounting:** direct-session totals and inclusive subtree totals are separate; a session is counted once per subtree union; overlapping selected roots must not duplicate usage (`duplicate_membership` finding).
- **Spans:** exact span attribution requires compatible boundaries; session-level measurement otherwise, `span_usage_unavailable` — no smearing. Wall time = recorded; prices are never synthesized (A4: cost null with reason).

## 5. Label protocol v1 (`labels.py`)

- **Grammar:** one standalone message-text line, byte-exact prefix `[mh13.experiment]` + one JSON object. Required trial identity fields on `trial_start`: `{v:1, experiment, run, trial, case, variant, rep, attempt, event}`; events are the closed set `trial_start|trial_end|span_start|span_end|checkpoint` (`checkpoint` requires `checkpoint_id`); later events must agree with the established identity; `trial_end` carries observed `outcome ∈ {completed|aborted|...}` — outcome ≠ correctness.
- **Validation failures → named findings:** bad JSON/prefix ⇒ `label_grammar_invalid`; conflicting duplicate identity (same key, differing payload) ⇒ `label_identity_conflict`; `span_end` without open span ⇒ `label_orphan_event`; end-before-start ⇒ `span_reversed`; label not matching any manifest entry ⇒ `label_unbound_to_manifest` (collect stage). Idempotent repeats (identical payload) are deduped, not errors.
- **Legacy adapter:** `^\[harness_reason:discharge arm=(harness|planner|kernel) case=(H1|H3)\]$` (first user-message part line, verified) with a mandatory explicit run mapping; absent rep/attempt/span boundaries reported unavailable — no invented repetitions.
- **Emitter eligibility:** only `role=user` message parts mint/complete trials; anything else (titles, tool outputs, assistant text) ⇒ `echo_not_trial` finding.

## 6. Hierarchy (`hierarchy.py`)

`build_forest(sessions)` → trees keyed by root; walk yields `{node, depth, direct_usage, subtree_usage}`; children referenced but absent ⇒ `missing_child` finding (coverage, not silence); parent cycles ⇒ `hierarchy_cycle` (report the cycle, refuse the subtree total); duplicate membership across selected roots is detected on union queries.

## 7. Testing strategy (drives the TDD list)

- **Deterministic fixtures, schema-faithful, sanitized:** tests construct tiny SQLite DBs in `tmp_path` from the verified DDL (analysis §1) with synthetic content only — no raw transcript bodies in the repo (fixture policy; proposal §capture 8).
- **Every A-ambiguity gets a fixture:** A1 disjoint + output_includes_reasoning + ambiguous rows; A3 valid zeros; A7 running tool ⇒ incomplete; missing tables ⇒ schema_unsupported; echo immunity; cycle/missing-child forests.
- **Live-DB smoke (env-gated, opt-in):** `MH13_LIVE_DB=1` (and path override `MH13_DB_PATH`) unlocks read-only structural checks against the real DB (counts > 0, directory filter, schema markers, one legacy label session parses). Default regression (`uv run pytest -q`) stays deterministic — the live DB is user data, not a fixture.
- **Boundary assertions:** adapter writes raise; read-only URI; no env mutation; stdlib-only imports (test asserts no third-party imports in package).

## 8. TDD behavior list (slice 1 — fed to omt_tdd)

1. `schema.failure_vocabulary` — closed vocabulary constants; names stable; findings serialize with source_ref.
2. `adapter.readonly_open` — opens real/fixture DB via mode=ro; missing path ⇒ `source_unreadable`; internal write attempt raises.
3. `adapter.capability_discovery` — returns schema_markers (drizzle count/latest, data_migration names); fixture missing `part` table ⇒ `schema_unsupported` naming it.
4. `adapter.bounded_selection` — directory/id/time selectors produce bounded queries; ordering by (time_created, id) stable; ties by id (A8).
5. `normalize.session_record` — row → SessionRecord: ms passthrough, model JSON → triple, counters/cost, null-safe; completion `incomplete` on open tool part (A7).
6. `normalize.message_turn_pairing` — assistant.parent_id = user message id; user tokens None; all-zero assistant tokens kept (A3).
7. `normalize.usage_variant` — **A1 core:** disjoint / output_includes_reasoning / empty / ambiguous fixtures each classified correctly; variant stored on record.
8. `normalize.step_usage` — step-finish tokens + reason + snapshot extracted as step basis; step-start snapshot captured.
9. `normalize.part_taxonomy` — all 9 part types round-trip with payload verbatim; unknown type passes through with coverage finding (never dropped).
10. `labels.v1_grammar` — valid trial_start parses to full TrialIdentity; malformed JSON/fuzzy prefix/unknown event/checkpoint-without-id ⇒ `label_grammar_invalid` (named, with the raw line preserved).
11. `labels.identity_rules` — later events must agree with trial_start identity; conflicting duplicate ⇒ `label_identity_conflict`; idempotent identical repeat dedupes; orphan span_end ⇒ `label_orphan_event`; reversed span ⇒ `span_reversed`.
12. `labels.legacy_discharge` — the 6-label grammar parses under explicit run mapping; without mapping ⇒ `label_unbound_to_manifest`; no repetitions invented.
13. `labels.echo_immunity` — label text in title / tool-output / assistant text ⇒ `echo_not_trial`, no trial minted; only role=user parts bind.
14. `hierarchy.forest` — 3-level fixture: direct vs subtree usage separate and correct; missing child ⇒ `missing_child`; parent cycle ⇒ `hierarchy_cycle`; duplicate membership across roots detected once-counted.
15. `usage.bases_and_reconciliation` — variant-aware Σ(message components) == session cumulative on consistent fixture ⇒ reconciled; tampered fixture ⇒ `reconciliation_discrepancy` with exposed residual; cross-basis sum ⇒ `double_counted_basis`.
16. `usage.legacy_metric` — legacy_feature130_prompt/completion reproduce the documented mapping on a disjoint-variant fixture; valid zeros pass through; missing counters ⇒ null+reason.
17. `labels.pipeline_end_to_end` — labeled fixture DB (mini-matrix 2 variants × 2 cases × 2 reps = 8 trials, one contaminated echo, one orphan) → collect/bind produces exactly the expected usable trial set with per-trial usage + exclusion findings.
18. `adapter.live_smoke` — env-gated: real DB opens read-only; schema markers present; ≥1 session in this repo's directory; ≥1 legacy discharge label parses. Skipped unless `MH13_LIVE_DB=1`.

## 9. Boundaries and non-goals (this slice)

Read-only everything; no experiment `run` (S4), no plugin/`.omt` registration (S5), no scheduler, no second token-accounting implementation (feature-129/130 scripts stay untouched; their contracts are *consumed*, not edited — extraction into shared code is deferred to when S3/S4 actually needs overlap). Protected-path rules unaffected: the adapter never writes; output artifacts (exports) are a later slice with explicit destinations.

## 10. Next

`omt_phase{major_feature, Programming}` with this design doc → `omt_tdd testlist` (behaviors §8) → red → green → refactor per cycle → slice-1 test report + `uv run pytest -q` regression.
