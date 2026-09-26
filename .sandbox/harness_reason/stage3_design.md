# Stage-3 Design — feature_125 (sandbox only)

Source: `stage3_analysis.md` + proposal §§14.2/15.6 + S0–S2 artifacts. Rule: sandbox only; stdlib only; advisory boundary.

## Experiment ops (closed set for the probe)

- `register_arm(arm_id)` — one of `harness | planner | kernel`. Rejects unknown arm (`unknown(arm_outside_closed_set)`).
- `load_shared_inputs(catalog_digest, adapter_versions, fragment_digests, task_set, budgets, oracle_ref)` — all three arms receive the identical handle; any arm-specific input fork → `refusal(input_fork_breaks_parity, obligation: reload_shared)`.
- `capture_snapshot(manifest)` → `snapshot_digest`. Mid-run manifest change → `snapshot_inconsistent` (never a mixed-epoch plan).
- `run_case(arm, case_id, variant, order_slot)` → `verdict + cost_ledger + unknowns`. Order slot varied per repetition; cache key includes content + context deps + catalog version + contract.
- `score_case(arm, case_id)` → agreement with A0 oracle (match/missed-stale/unsupported/unsafe/intervention/false-blocker) + costs.
- `report(variability=True)` → per-case table + median/p-range + threshold-rule evaluation (15% rule as decision rule, labeled proxy if bytes).

Withheld: `plan` (bounded hole-fill) stays withheld — experiment measures check/explain/expand/rewrite only, same as Tier-1 closed enum.

## `run_experiment.py` outline (stdlib only)

1. Load S0 contracts digest + S1 12-case list + S2 fragment digests (import, never copy semantics) — record shared-input handle H.
2. Define deterministic synthetic oracles: A0 verdicts per T01–T12/H1–H3 variants (from `run_checker.py` 12/12 + `run_composer.py` 7/7 expectations); A1/A2 scripted to match except injected deltas for report-shape testing (one missed-stale, one unsafe-attempt-refused, cost ledgers with varied order).
3. Repetitions R=3 with rotated arm order [A0,A1,A2] → [A1,A2,A0] → [A2,A0,A1]; one snapshot per repetition; assert snapshot/order discipline (mixed-epoch attempt returns `snapshot_inconsistent` in a negative check).
4. Validity checks (fail = non-zero exit):
   - V1 shared-inputs parity: all arms report handle H; fork attempt refused.
   - V2 agreement gate: A1/A2 match A0 on T01–T12 valid variants (or counted as miss with location).
   - V3 unknown discipline: validator-absent/bound-hit cases return named `unknown`, never impossible/proved.
   - V4 contract-relative: H2 files-only permits both orders, completion-relevant rejects `test;edit` with (h1,h0).
   - V5 reuse freshness: H1 Ctx-B refuses h2-with-h1 evidence with location.
   - V6 report shape: per-case rows + variability (median/range) + threshold evaluation + proxy labels + digests; byte-stable for immutable inputs (probe-7 rule).
   - V7 boundary: no `src/`/`scripts/reason/`/net/ledger/toolbox writes (probe asserts only sandbox paths touched; git-status advisory note in report).
5. Exit 0 + print `EXPERIMENT_DESIGN_OK <digest>` where digest = sha256 of canonical report bytes (stable across runs).

## Report envelope (JSON, ~2 KB summary default + detail_ref)

- `summary`: per-arm medians (correctness, misses, interventions, calls/latency/tokens-or-proxy/checker-ms, maintenance, avoided-steps) + threshold evaluation (`meets_15pct_rule: true/false`, `proxy: true/false`, `verdict: keep-kernel | keep-planner | shrink-tier0 | inconclusive`).
- `per_case`: one row per (case, variant, arm): verdict, agreement, misses, interventions, costs, unknowns, fragment hits.
- `variability`: per-case range across R + order rotation note.
- `digests`: shared-input handle H, snapshot digests, catalog/fragment digests, report digest.
- `derivation`: op digests + law/contract IDs (replayable from digests alone).
- `detail_ref`: pointer to full per-run ledgers (not inlined; never truncated cert).

## Failure outputs (named, never bare bool/score)

`subject_digest_mismatch` + expected/observed + next obligation; `different_under_declared_model` + (h1,h0) witness; `snapshot_inconsistent`; `no_candidate_within_bounds` + bounds; `unknown(<reason>)` with required cert/obligation. Truncation fails validation.

## Next

Implement `run_experiment.py` per outline → Programming → Testing (rerun checker 12/12 + composer 7/7 + probes 7/7 + experiment validity checks) → Done.
