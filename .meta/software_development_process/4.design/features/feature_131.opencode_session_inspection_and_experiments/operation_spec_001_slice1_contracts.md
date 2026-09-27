# Operation Spec 001 — feature_131 slice 1: public operation contracts

> Phase: Design companion to `design_001_core_architecture.md`. Slice-1 public surface of `scripts/session_inspect/` (schema · adapter · normalize · labels · hierarchy · usage). All ops stdlib-only; every op is **read-only**; every error is a `Finding(name, detail, source_ref)` from the closed vocabulary (design §2), never a bare string.

## `schema.py` — records + vocabulary (design §2)

| Op | Pre | Post / returns | Errors |
|---|---|---|---|
| `Finding(name, detail, source_ref)` | `name` ∈ closed vocabulary | Serializable dataclass; `source_ref` carries `{path, schema_markers, snapshot_digest?}` | `ValueError(unknown_failure_name)` on construction with a non-vocabulary name (keeps the vocabulary closed at runtime) |
| `FAILURE_NAMES` / `is_failure_name(name)` | — | Frozen tuple + predicate over the closed vocabulary (design §2 list) | — |

## `adapter.py` — read-only source access (design §3)

| Op | Pre | Post / effects | Errors |
|---|---|---|---|
| `OpenCodeSqliteAdapter(db_path: str)` | explicit path (documented candidate default `~/.local/share/opencode/opencode.db`) | Lazy connection; no I/O at construction | — |
| `.connect() -> sqlite3.Connection` | — | Opens `file:<path>?mode=ro` (uri); `immutable=1` is never used; connection is read-only (any write raises `sqlite3.OperationalError`) | `Finding(source_unreadable, {path, reason})` if the file is absent/unopenable |
| `.capability_report() -> dict` | connection open | `{ok, required_tables: {name: present}, schema_markers: {drizzle_count, drizzle_latest_ms, data_migrations: [names]}, db_path}` — verified DDL names per analysis §1 | `Finding(schema_unsupported, {missing: [...]})` naming every absent required table/column; never partial-silent |
| `.snapshot(selector: SessionSelector) -> Snapshot` | `selector` has ≥1 bound (directory \| session_ids \| time range); not unbounded | ONE deferred read transaction: consistent main+WAL view; returns `{sessions, messages, parts, events?, coverage}` with all source ids retained; rows ordered `(time_created, id)`; ties by id (A8) | `Finding(source_unreadable)`; `Finding(schema_unsupported)`; selector with no bound → `ValueError(unbounded_selector)` |
| `.event_cursor(session_id, after_seq) -> list[EventRow]` | session exists (else empty list) | Rows with `seq > after_seq` ordered by seq; idempotent replay (same range ⇒ same records) | — |
| `.assert_write_guard(conn)` (test hook) | — | Performs an `INSERT` inside a savepoint expecting failure; used by tests to prove read-only | — |

## `normalize.py` — source rows → normalized records (design §2, A-ambiguities)

| Op | Pre | Post / returns | Errors |
|---|---|---|---|
| `normalize_session(row) -> SessionRecord` | row from `session` table | Model JSON → `(model_id, provider_id, variant)`; epoch-ms passthrough (asserted int); counters/cost null-safe; `lifecycle.completion ∈ {complete, incomplete, unknown}` derived from open tool parts (A7) | non-int timestamps ⇒ `Finding(inclusion_semantics_ambiguous)` is NOT used; malformed row raises `ValueError(malformed_source_row, {field})` |
| `normalize_message(row) -> MessageRecord` | row from `message` table | `parentID` kept as turn link; user role ⇒ `tokens=None`; all-zero assistant counters preserved (A3) | malformed `data` JSON ⇒ `ValueError(malformed_source_row)` with field name |
| `normalize_part(row) -> PartRecord` | row from `part` table | Payload dict verbatim per type union; **unknown `type` passes through** with a coverage finding attached by the caller (never dropped) | malformed `data` JSON ⇒ `ValueError(malformed_source_row)` |
| `detect_usage_variant(counters) -> UsageVariant` | counters dict from message/step-finish tokens | Residual test (design §2): `disjoint` \| `output_includes_reasoning` \| `empty` \| `ambiguous` | — (pure) |

## `labels.py` — protocol v1 + legacy + echoes (design §5)

| Op | Pre | Post / returns | Errors |
|---|---|---|---|
| `parse_label_line(line: str) -> ParsedLabel \| Finding` | one message-text line | Byte-exact prefix `[mh13.experiment]` + one JSON object → `{identity, event, fields, raw}`; closed event set; `checkpoint` requires `checkpoint_id` | `Finding(label_grammar_invalid, {raw, reason})` — raw line always preserved in the finding |
| `bind_labels(snapshot, *, manifest=None) -> LabelBinding` | snapshot from adapter | Only `role=user` message parts are eligible emitters; establishes `TrialIdentity` at `trial_start`; later events must agree; identical payload repeats dedupe; spans paired; echoes (title/tool-output/assistant text) collected as `echo_not_trial` findings, never trials | `Finding(label_identity_conflict)` conflicting duplicate; `Finding(label_orphan_event)` span_end without open span; `Finding(span_reversed)` end≤start; unbound-to-manifest label ⇒ `Finding(label_unbound_to_manifest)` when a manifest is provided |
| `parse_legacy_discharge(first_user_line, *, run_mapping) -> ParsedLabel \| Finding` | line from a first user-message part | Grammar `^\[harness_reason:discharge arm=(harness\|planner\|kernel) case=(H1\|H3)\]$` (analysis §4); identity from explicit `run_mapping` (run id, rep/attempt reported **unavailable**) | no run_mapping ⇒ `Finding(label_unbound_to_manifest)`; grammar miss ⇒ `Finding(label_grammar_invalid)` |

## `hierarchy.py` — forest (design §6)

| Op | Pre | Post / returns | Errors |
|---|---|---|---|
| `build_forest(sessions: list[SessionRecord]) -> Forest` | — | Trees keyed by root id; nodes carry `{direct_usage, subtree_usage}` (separate bases); membership map for union counting | `Finding(missing_child, {referenced_id})` per absent child; `Finding(hierarchy_cycle, {cycle_ids})` — the cycle is reported and the subtree total refused |
| `subtree_union(roots: list[str], forest) -> UsageTotals` | — | Each session counted once across overlapping roots | `Finding(duplicate_membership)` recorded, usage still once-counted |

## `usage.py` — bases, metrics, reconciliation (design §4)

| Op | Pre | Post / returns | Errors |
|---|---|---|---|
| `sum_components(records, metric: MetricDefinition) -> Totals \| Finding` | metric declares `{name, version, components, variant_policy}` | Sums named components only, variant-aware; totals never taken from source `total` unless variant verified | mixed variants without a policy ⇒ `Finding(metric_variant_mismatch)`; cross-basis combination (session cumulative + message increments) ⇒ `Finding(double_counted_basis)` |
| `reconcile_session(session, messages) -> ReconciliationResult` | — | Variant-aware Σ(message components) vs session cumulative: equal ⇒ `{status: reconciled}`; else `{status: reconciliation_discrepancy, residual}` — residual exposed, never smeared | — |
| `legacy_feature130_metrics(records) -> {prompt, completion}` | disjoint-variant-aware per record (analysis §4 mapping) | `prompt = input + cache_read`; `completion = (output − reasoning) + reasoning` for `output_includes_reasoning` records else `output + reasoning`; zeros pass through; missing ⇒ `null` + reason | — |

## `collect.py` (slice-1 pipeline entry) — end-to-end binding

| Op | Pre | Post / returns | Errors |
|---|---|---|---|
| `collect_trials(adapter, selector, *, manifest=None) -> TrialReport` | adapter + bounded selector | snapshot → bind_labels → per-trial membership + per-trial usage (session cumulative basis of bound sessions) + all findings; usable/excluded trials classified with reasons; raw label lines retained | propagates adapter/label findings; never mints trials from echoes (AC7 seed) |

## tests/scripts/session_inspect/ — pytest suite (design §7)

| Op | Contract |
|---|---|
| fixture DB factory | builds schema-faithful tiny DBs in `tmp_path` (verified DDL, analysis §1) with sanitized synthetic rows only; every A-ambiguity has a fixture; no raw transcript bodies |
| live-DB tests | `@pytest.mark.skipif(not MH13_LIVE_DB)` — read-only structural checks only; default regression stays deterministic |
| stdlib guard | asserts no third-party imports inside `scripts/session_inspect/` |

## Global invariants

- **Read-only** — the adapter never writes; `mode=ro` URI; writes raise (asserted by test).
- **No basis mixing** — session-cumulative / message-incremental / step-incremental are never summed together; violation is a named finding, not a number.
- **Closed vocabularies** — failure names and event sets are frozen constants; runtime construction with unknown names fails.
- **Raw content stays out** — repo fixtures are synthetic/sanitized; live-DB checks are opt-in via `MH13_LIVE_DB=1` (+ `MH13_DB_PATH` override).
- **feature 129/130 scripts untouched** — their contracts are consumed (legacy adapter), their files unmodified.
