# Real-Token Design — feature_129 (sandbox only, Alternative A span wrapper)

Source: `stage_real_tokens_analysis.md` (alternatives; user picked **A — host-usage span wrapper**) + `stage3_design.md` (closed ops reused) + `run_experiment.py` (V1–V7 shape).
Rule: sandbox only; stdlib only; advisory boundary; no src/net/ledger/toolbox change.

## Closed op set (delta vs S3)

- `register_arm(arm_id)` — unchanged: `harness | planner | kernel`; unknown → `unknown(arm_outside_closed_set)`.
- `load_shared_inputs(...)` — unchanged: identical handle H for all arms; fork → `refusal(input_fork_breaks_parity, obligation: reload_shared)`.
- `capture_snapshot(manifest)` → `snapshot_digest` — unchanged; mid-run change → `snapshot_inconsistent`.
- **`open_span(arm, case_id, order_slot)` → span_id** — NEW: starts a cost-attribution span.
- **`close_span(span_id)` → usage** — NEW: closes span; returns host usage deltas `{prompt_tokens, completion_tokens, total_tokens}` when host metadata available for the span, else `{measured: false, reason: "host_usage_unavailable"}`. Never zero-fills, never estimates from bytes.
- `run_case(arm, case_id, variant, order_slot)` — wrapped: verdict logic identical to S3 (deterministic oracle replay); costs recorded per span.
- `score_case` / `report(variability=True)` — report adds `measured` flags + `proxy: false | mixed` evaluation.

Withheld: `plan` stays withheld (same as S3/Tier-1 enum).

## Host usage adapter (single seam)

- `HOST_USAGE_MODE` env-free constant in the probe: `span-delta | unavailable`.
  - `span-delta`: a host session exports per-span token deltas (e.g. agent transcript usage between span open/close); the probe reads them via `read_host_span_usage(span_id)`.
  - `unavailable`: no host API in this environment (current state — this repo has no live host usage exporter wired to sandbox probes); all spans return `measured: false, reason: "host_usage_unavailable"`.
- Mode is **detected at runtime, not configured**: probe attempts `read_host_span_usage` once; on `HostUsageUnavailable` every span is `unmeasured`. Detection is disclosed in the report (`host_usage_mode`), never guessed.
- Attribution rule: usage delta = span-close minus span-open host totals; negative deltas → `snapshot_inconsistent` (usage rewind impossible in a consistent session).
- `unmeasured` rows never contribute to medians; they are listed with reason.

## `run_real_tokens.py` outline (stdlib only)

1. Reuse S3 building blocks by re-declaring them (same ORACLE table, CASES, ORDERS, shared_handle formula → identical H, deterministic run_case verdicts) — import file bytes for digest parity like S3 (`stage0_contracts.json`, `stage0_ir.json`).
2. Wrap every `run_case` in `open_span`/`close_span`; collect per-row `{measured, prompt_tokens, completion_tokens, total_tokens, calls, latency_ms, checker_ms, fragment_hits, avoided_steps, order_slot, snapshot_digest}`.
3. R=3 repetitions, rotated arm orders (same ORDERS as S3), one snapshot per rep; mixed-epoch negative check returns `snapshot_inconsistent`.
4. Validity checks (fail = non-zero exit):
   - V1 shared-inputs parity: handle H identical across arms; fork refused (same as S3).
   - V2 agreement gate: A1/A2 match A0 oracle on T01–T12 (same as S3).
   - V3 unknown discipline: named unknown, never impossible/proved (same as S3).
   - V4 contract-relative + V5 reuse freshness: same witnesses ((h1,h0), h2-with-h1 refusal).
   - V6 report shape: per-case rows (15×3×3), variability, `measured` flags present on every row, `proxy` evaluation correct (`false` iff all measured; `mixed` iff any unmeasured), threshold evaluated **on measured medians only**, digest byte-stable.
   - V7 sandbox boundary: only `.sandbox/harness_reason/` paths touched.
   - **V8 span discipline (NEW):** every row has a span; unmeasured rows carry `reason`; no row has zero/None tokens with `measured: true`; simulated rewind → `snapshot_inconsistent`.
5. Exit 0 + print `REAL_TOKENS_OK <digest>` (sha256 of canonical report bytes, stable across runs when host mode `unavailable` — deterministic).

## Report envelope delta vs S3

- `summary` adds: `host_usage_mode`, `measured_rows/total_rows`, `proxy: false|mixed` (never silent), per-arm measured-token medians `{prompt, completion, total}` + range, `meets_15pct_rule` computed on measured medians (if no measured rows → `inconclusive_host_usage_unavailable`, never a fake pass/fail).
- `per_case` rows add: `measured`, `reason?`, `prompt_tokens`, `completion_tokens`, `total_tokens`, `latency_ms`.
- `variability`/`digests`/`derivation`/`detail_ref`: unchanged shape; `digests` adds `s3_report_digest` (`d476df80d71d829a`) provenance link.

## Failure outputs (named)

`unknown(arm_outside_closed_set)` · `refusal(input_fork_breaks_parity)` · `snapshot_inconsistent` (manifest change OR usage rewind) · `inconclusive_host_usage_unavailable` (no measured rows). Truncation fails validation.

## Expected first-run outcome (honest reading)

This environment has no host usage exporter wired to sandbox probes → first run reports `host_usage_mode: unavailable`, all rows `measured: false`, `proxy: mixed`, verdict `inconclusive_host_usage_unavailable` + explicit next obligation: **wire a real host session (live agent transcript usage) through the span seam, or capture a live-session ledger by hand into `stage_real_tokens_ledger.json` and re-run with `--ledger`**. The probe's value: the seam, attribution rule, and threshold evaluation are now fixed and replayable; plugging real numbers in is a data change, not a design change.

## Next

Implement `run_real_tokens.py` per outline → Programming → Testing (re-run S0 7/7 + checker 12/12 + composer 7/7 + experiment 7/7 for regression) → Done.
