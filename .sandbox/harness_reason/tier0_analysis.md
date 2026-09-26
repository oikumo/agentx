# Tier-0 Analysis — reason_table.ts prompt-side renderer

> Feature: feature_127.harness_reason_tier_0_renderer (minor_feature, Analysis) · Project: harness_reason · Date: 2026-09-26
> Spec: proposal §7 Tier-0 row + §2 language + §3 three-row + §4 Maybe + §5 cert + UC8 explain · Pattern: `.opencode/plugins/startup_table.ts` (269 lines, stdlib only, no `omt_` prefix)

## Objective
Ship `reason_table.ts` — pure formatter, zero harness cost (no registry row, no perm change, no receipt) — that renders §2 programs + §5 certificates/summaries + UC8 slices as plain text and parses digests + `detail_ref`s. Unblocks readable UC8 output + probe replays.

## Inputs (authoritative)
- `stage0_ir.json` (IR v1: Obs/D/A schemas, HarnessObs d1/d2/d3, DetailedD three-row, F preserves, aligned query, concretize_C, refresh compute, round_trip_probe7)
- `stage0_contracts.json` (8 generators v1, authority + validator_ref + unknown_if per contract)
- `stage0_probes.md` + `run_probes.py` 7/7 digest `6e355d71`, `run_checker.py` 12/12, `run_composer.py` 7/7, `run_experiment.py` 7/7
- §5 cert example (structural/premises/execution/goal + program_digest + catalog/model/interp versions + context_id + observation_contract + unit_counit + issues/unknowns/derivation + certificate_digest) + over-budget envelope (summary ≤2KB + mandatory detail_ref, never truncate)
- UC8: `explain` by result + node/obligation ID → minimal premise-to-conclusion slice, first unsupported connection, source refs, permitted acquisition path, ≤2KB or detail_ref envelope

## Gaps vs current
- No `reason_table.ts` exists (only `startup_table.ts` pattern). No `scripts/reason/` needed for Tier-0. No formatter for IR/cert/UC8 plain lines.
- Ad-hoc JSON dumps of IR/certs are unreadable; probe replays lack plain-text path.

## Exit criteria (Analysis → Design)
- IR fields to render fixed (schemas/models/queries/computes + verdicts Aligned/Mismatched/Unresolved)
- Cert fields to render fixed (4 verdicts + digests + issues/unknowns/derivation + detail_ref envelope)
- UC8 slice shape fixed (node slice + first unsupported + next_obligation)
- Design will list ops (format_ir/format_cert/explain_slice/parse_digest) + I/O + plain-line budgets

## Boundary (D2/D3/D5 holds)
- Sandbox + `.opencode/plugins/reason_table.ts` only. No `src/`, no `scripts/reason/`, no `tests/`, no net/ledger writes, no `omt_*` prefix, no `opencode.jsonc` perm change, no `uv.lock` change, stdlib only.
- If formatter cannot carry IR+cert+UC8 without widening surface, adding imports, or touching net/ledger → shrink scope, stay Tier-0 (kill line).
