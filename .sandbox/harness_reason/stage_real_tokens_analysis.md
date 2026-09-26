# Real-Token Analysis — feature_129 (sandbox only)

Source: `.sandbox/category_theory_meta_harness.md` §§14.2 (fair comparison), 14.3 (token discipline), 15.6 (cost-benefit gate) + S3 `stage3_analysis.md` + `stage3_design.md` + `run_experiment.py` (7/7, digest `d476df80d71d829a`, `proxy:true`) + Tier-2 HOLD verdict (2026-09-26: fixtures sound, no real-token measurement, no toolbox review).
Rule: sandbox only; no src/net/ledger/toolbox change; advisory-only holds.

## Problem

S3 paired experiment proves fixture soundness but costs are synthetic `tokens_proxy` bytes (harness 1205 / planner 905 / kernel 805 medians → 33.2% reduction, `proxy:true`, verdict `keep-kernel-candidate` as decision rule, not prediction). Tier-2 promotion gate requires (PROJECT.md ## Status): (1) real-token paired measurement, (2) budgets with explicit harness-surface cost (39B headroom), (3) `omt_reason.ts` + `@tool` row + harnessc build + e2e receipt, (4) user-selected implementation. This feature covers (1) only.

## What stays identical from S3

- Three arms A0 harness / A1 planner / A2 kernel, same 8-generator catalog v1 + adapters v1 + fragments + T01–T12+H1–H3 + budgets + oracle (existing receipt/dependency authority, features 075/085).
- Shared-handle H parity (`H=f7e6b89317420fbd` pattern), fork→`reload_shared` refusal, one snapshot per rep, order rotation R=3, `snapshot_inconsistent` on mid-run change, agreement gate on T01–T12, U1–U5 reuse/contract-relative witnesses, named `unknown` discipline, ~2KB summary + `detail_ref` envelope, byte-stable digests.

## What changes: cost ledger `tokens_proxy` → measured tokens

Per-case per-arm per-rep must record:
- `prompt_tokens`, `completion_tokens`, `total_tokens` as reported by the host for the reasoning + tool-call spans attributable to that case (not whole-session totals).
- `calls`, `latency_ms`, `checker_ms` (unchanged), `fragment_hits`, `avoided_steps`, `order_slot`, `snapshot_digest`.
- Attribution rule: each `run_case` opens a span, logs host usage deltas on close; any span without host usage metadata is marked `unmeasured`, never zero-filled, never estimated from bytes.
- Report adds `proxy:false` when all rows measured, else `proxy:mixed` with per-row `measured: true/false` + reason (e.g. `host_usage_unavailable`).

## Alternatives (approval gate — pick one)

### A — Host-usage span wrapper (recommended)
- Small stdlib `run_real_tokens.py` that replays the same deterministic verdicts as `run_experiment.py` but wraps each `run_case` in a span that reads host token-usage metadata (e.g. agent transcript usage deltas) when available, else marks `unmeasured`.
- Pros: same shared-inputs/order/snapshot discipline, minimal new code, report shape reuses V6, works even if host exposes no per-span API (degrades to `proxy:mixed` honestly).
- Cons: if host never exposes per-span usage, first run stays `proxy:mixed`; needs 2–3 sampled real sessions to calibrate.
- Effort: 1 probe file + analysis/design (this file + 1 design), R=3 replay, threshold re-evaluated on measured subset.

### B — Manual sampled ledger (fallback, zero code)
- Run H1/H3 (the only reuse-sensitive cases per §15.6) as live agent sessions once per arm, copy host-reported token totals by hand into `stage_real_tokens_ledger.json`, compute medians + variability manually.
- Pros: zero probe code, honest real tokens immediately, smallest scope.
- Cons: no R=3 rotation discipline in code, no byte-stable digest, harder to replay from digests alone (weakens S1/S2 replay guarantee).
- Effort: ledger JSON + analysis note, no runner.

### C — Calibrated proxy (shrink, no new measurement)
- Keep `run_experiment.py` as-is, add calibration factor from 2–3 real runs (e.g. `tokens_per_proxy_byte` per arm) and report `proxy:calibrated` with factor + sample IDs.
- Pros: no harness change, unblocks threshold discussion fastest.
- Cons: still `proxy:true` family — does NOT satisfy Tier-2 gate (1); gate will HOLD again.
- Effort: 1-page note, no runner.

## Metrics + threshold reading (unchanged rule, new units)

- Per-arm medians on `total_tokens` (measured rows only) + range across R=3; correctness/miss/intervention counters identical to S3 V2–V5.
- `meets_15pct_rule` evaluated on measured medians: `(median_harness - median_kernel)/median_harness >= 0.15` with no correctness loss + no authority divergence. Verdict enum unchanged: `keep-kernel | keep-planner | shrink-tier0 | inconclusive`. If `proxy:mixed`, verdict is `inconclusive (unmeasured spans)` unless measured subset alone meets R=3 + agreement gates — stated explicitly, never silently promoted.
- Maintenance cost + harness-surface cost noted (39B headroom) but not re-measured here — belongs to gate item (2).

## Exit criteria (Design gate)

- This analysis covers arms/inputs/tasks/oracle/metrics/keep-conditions with proposal refs + 3 alternatives.
- Design (`stage_real_tokens_design.md`) lists closed ops + `run_real_tokens.py` outline + report envelope delta (`measured` flags, `proxy:false|mixed`).
- Probe passes: V1 parity + V2 agreement + V5 reuse + V6 shape (with `measured` flags) + V7 sandbox-only boundary; threshold evaluated on measured tokens.
- No src/tests/net/toolbox change — `git status` shows only `.projects/meta`, `WORK.md`, `.meta/.../feature_129/`, `.sandbox/harness_reason/`.

## Recommendation

A (span wrapper): preserves S3 validity checks, degrades honestly when host usage is unavailable, and is the only option that can reach `proxy:false` without weakening replay guarantees.
