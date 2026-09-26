# Test Report — feature_129.harness_reason_real_token_measurement

> Task type: minor_feature · sandbox only · 2026-09-26
> Artifacts: `.sandbox/harness_reason/stage_real_tokens_analysis.md`, `stage_real_tokens_design.md`, `run_real_tokens.py`

## Verdict

**8/8 PASS** — `REAL_TOKENS_OK 40e6ab74b10b038a` (byte-stable across runs). Honest first-run reading: `host_usage_mode: unavailable`, measured 0/135, verdict `inconclusive_host_usage_unavailable`.

## What was built

- `run_real_tokens.py` (stdlib only): Alternative A span wrapper per user pick at the approval gate. Replays S3 verdicts verbatim (same handle H `f7e6b89317420fbd`, ORACLE, ORDERS R=3) while wrapping every `run_case` in `open_span`/`close_span`.
- Single host seam `_read_host_total()`: raises `HostUsageUnavailable` in this environment (no exporter wired); detected once at runtime, disclosed as `host_usage_mode` — never guessed.
- `--ledger` mode: hand-captured live-session rows (`{"<arm>:<case>": {prompt_tokens, completion_tokens, latency_ms?}}`) convert unmeasured spans into `measured: true, source: "ledger"` rows — a data change, not a design change.
- Named failures: `unknown(arm_outside_closed_set)` · `refusal(input_fork_breaks_parity)` · `snapshot_inconsistent` (manifest change OR usage rewind) · `inconclusive_host_usage_unavailable`.

## Validity checks

| Check | Result | Detail |
|---|---|---|
| V1 shared-inputs parity | PASS | handle H identical across 3 arms; fork refused |
| V2 oracle agreement | PASS | planner+kernel match harness on T01–T12 |
| V3 unknown discipline | PASS | named unknown, never impossible/proved |
| V4 contract-relative | PASS | (h1,h0) witness for test;edit under completion-relevant |
| V5 reuse freshness | PASS | h2-with-h1 refused with location |
| V6 report shape | PASS | 135 rows, `measured` flag every row, proxy=false\|mixed never silent, digest byte-stable within + across runs |
| V7 advisory boundary | PASS | sandbox-only paths; no src/net/toolbox writes |
| V8 span discipline | PASS | every row span-attributed; rewind → `snapshot_inconsistent`; no zero-token measured rows |

## Fix during test ( Programming→Testing handoff)

Wall-clock `latency_ms` from `time.time()` made the report digest vary across runs, breaking S3's byte-stable replay rule. Fixed: unmeasured spans carry `latency_ms: null` (no fake 0 ms precision when nothing was measured); ledger rows take latency from the ledger. Digest now byte-stable: `40e6ab74b10b038a` ×2 consecutive runs + smoke re-run.

## Ledger smoke test (mechanics only — synthetic numbers, deleted)

`--ledger` verified with a clearly-marked synthetic ledger (6 arm:case pairs × 3 reps = 18/135 measured rows): threshold evaluated on ledger medians, `proxy: mixed`, all checks green. Smoke file deleted after the run — synthetic numbers were never recorded as measured tokens anywhere. Note for real captures: ledger is keyed `arm:case` (one capture replayed across reps); per-rep captures would need `arm:case:rep` keys — future refinement if variability across reps is wanted from hand data.

## Regression suite (gate-review discipline)

| Suite | Result | Digest |
|---|---|---|
| run_real_tokens.py ×2 | 8/8 PASS | `40e6ab74b10b038a` stable |
| S0 run_probes.py | 7/7 PASS | `6e355d71` stable |
| S1 run_checker.py | 12/12 PASS | — |
| S2 run_composer.py | 7/7 PASS | `cfcc014071b10849` (rewrite) |
| S3 run_experiment.py | 7/7 PASS | `d476df80d71d829a` unchanged |
| tier0_demo.py | PASS | — |
| tier1_demo.py | PASS | — |
| tests/scripts/reason/ | 14 passed | — |

## Boundary check

`git status` shows only `.projects/meta`, `WORK.md`, `.meta/.../feature_129*`, `.sandbox/harness_reason/` — no src/tests/net/toolbox change (advisory boundary holds).

## Reading for the Tier-2 gate

- Tier-2 gate item (1) real-token measurement is now **mechanically ready but not yet discharged**: the seam, attribution rule, and threshold evaluation exist and replay byte-stable; no host exporter is wired in this environment, so the first honest report is `inconclusive_host_usage_unavailable`.
- To discharge: capture real H1/H3 sessions per arm by hand into `stage_real_tokens_ledger.json` (or wire the exporter through `_read_host_total`) and re-run with `--ledger`; threshold then evaluates on measured medians with the same ≥15% decision rule.
- Gate items (2) budgets w/ harness-surface cost, (3) `omt_reason.ts` surface, (4) user-selected implementation remain open — promotion still HOLD.
