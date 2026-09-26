# Held-out Design — feature_126 (sandbox only)

Source: `stage_heldout_analysis.md` + proposal §§14.2/15.6 + S0–S3 artifacts. Rule: sandbox only; stdlib only; advisory boundary.

## Held-out ops (closed set for the probe)

- `register_arm(arm_id)` — one of `harness | planner | kernel`. Rejects unknown arm (`unknown(arm_outside_closed_set)`).
- `load_shared_inputs(catalog_digest, adapter_versions, fragment_digests, real_task_set, budgets, oracle_ref)` — all three arms receive the identical handle; any arm-specific input fork → `refusal(input_fork_breaks_parity, obligation: reload_shared)`.
- `capture_snapshot(manifest)` → `snapshot_digest`. Manifest = sorted [(name, sha256)] of real sandbox files in scope + catalog/fragment digests. Mid-run manifest change → `snapshot_inconsistent` (never mixed-epoch plan).
- `run_real_case(arm, case_id, order_slot)` → `verdict + cost_ledger + unknowns`. R1 reads real file bytes + edited copy; R2 expands over two real file digests; R3 snapshots real dir, mutates a copy, replays derivations; R4 interleaves a touch. Order slot varied per rep; cache key includes content + context deps + catalog version + contract.
- `score_real_case(arm, case_id)` → agreement with A0 oracle (match/missed-stale/unsupported/unsafe/intervention/false-blocker) + costs (wall-ms + checker-ms measured, tokens labeled proxy).
- `report(variability=True)` → per-case table + median/range + threshold-rule evaluation on R1–R3 (R4 discipline only) + proxy labels + digests; byte-stable for immutable inputs.

Withheld: `plan` (bounded hole-fill) stays withheld — held-out measures check/explain/expand/rewrite only, same as Tier-1 closed enum.

## `run_heldout.py` outline (stdlib only)

1. Load S0 contracts digest + S1/S2 digests (import, never copy semantics) — record shared-input handle H (same construction as `run_experiment.py` + real-task-set digest over R1–R4 file list).
2. Define real oracles: A0 verdicts per R1–R4 from deterministic rules over real bytes (R1 mismatch iff edited bytes differ; R2 refuse iff evidence digest != artifact digest; R3 stale iff mutated file in dependency closure; R4 inconsistent iff manifest changed mid-collection). A1/A2 scripted to match except injected deltas for report-shape testing (one missed-stale on R1-invalid, one unsafe-attempt-refused on R2, cost ledgers with varied order + measured ms).
3. Repetitions R=3 with rotated arm order [A0,A1,A2] → [A1,A2,A0] → [A2,A0,A1]; one snapshot per rep; assert snapshot/order discipline (mixed-epoch attempt returns `snapshot_inconsistent` in a negative check).
4. Validity checks (fail = non-zero exit):
   - V1 shared-inputs parity: all arms report handle H; fork attempt refused.
   - V2 agreement gate: A1/A2 match A0 on R1–R3 valid variants (or counted as miss with location).
   - V3 unknown discipline: validator-absent/bound-hit cases return named `unknown`, never impossible/proved.
   - V4 contract-relative: R2 files-only permits both orders, completion-relevant rejects `test;edit` with (h1,h0) (replay S2 rule on real digests).
   - V5 reuse freshness: R2 Ctx-B refuses h2-with-h1 evidence with location over real sha256.
   - V6 report shape: per-case rows (4 cases x 3 arms x 3 reps = 36 rows) + variability (median/range) + threshold evaluation + proxy labels + digests; byte-stable (probe-7 rule).
   - V7 boundary: no `src/`/`scripts/reason/`/net/ledger/toolbox writes (probe asserts only sandbox paths touched).
   - V8 regression: re-invoke S0 probes 7/7 + checker 12/12 + composer 7/7 + experiment 7/7 expectations (import + run, digests 6e355d71 / d476df80d71d829a stable).
5. Exit 0 + print `HELDOUT_DESIGN_OK <digest>` where digest = sha256 of canonical report bytes (stable across runs).

## Report envelope (JSON, ~2 KB summary default + detail_ref)

- `summary`: per-arm medians on R1–R3 (correctness, misses, interventions, calls/latency-ms/tokens-or-proxy/checker-ms, avoided-steps) + threshold evaluation (`meets_15pct_rule`, `proxy: true`, `verdict: keep-kernel | keep-planner | shrink-tier0 | inconclusive`).
- `per_case`: one row per (case, arm, rep): verdict, agreement, misses, interventions, costs (measured ms + proxy), unknowns, fragment hits, real file digests.
- `variability`: per-case range across R + order rotation note.
- `digests`: shared-input handle H, snapshot digests, catalog/fragment digests, real-file digest set, report digest.
- `derivation`: op digests + law/contract IDs (replayable from digests alone).
- `detail_ref`: pointer to full per-run ledgers (not inlined; never truncated cert).

## Failure outputs (named, never bare bool/score)

`subject_digest_mismatch` + expected/observed + next obligation; `different_under_declared_model` + (h1,h0) witness; `snapshot_inconsistent`; `no_candidate_within_bounds` + bounds; `unknown(<reason>)` with required cert/obligation. Truncation fails validation.

## Next

Implement `run_heldout.py` per outline → Programming → Testing (rerun S0/S1/S2/S3 + held-out validity checks) → Done.
