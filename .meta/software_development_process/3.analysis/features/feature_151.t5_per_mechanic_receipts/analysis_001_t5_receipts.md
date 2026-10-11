# Analysis 001 — T5 per-mechanic receipts (feature_151)

## Problem

`g.receipt` (order 20, `when: path_in(@var.harness_paths)`) enforces one global e2e receipt
(`omtHarnessE2eStatus` in `.opencode/lib/omt_shared.ts`): any git-dirty harness file with
mtime newer than `omt_harness_e2e_last_run.json.passed_at` blocks the edit (plus feature_074
T4-2 staged-batch bypass, D-bar content digests, policy_ver, and feature_075 results-passed).
Consequence observed all through harness_wrapper_split R1–R3 and T4: a single-mechanic edit
(e.g. `omt_q.ts`) forces a FULL e2e re-run before ANY further harness edit — the receipt
couples all mechanics into one global validity window (PROPOSAL_V7 §3: "Per-mechanic
receipts are T5 design, not current fact"; §6 T5: "replace global rebuild gate slice by
slice").

## Evidence

- `gate_driver.ts` FALLBACK_GATES `g.receipt` → `guardHarnessReceipt(rel, abs)` →
  `omtHarnessE2eStatus` — single `receiptTimestampMs()` compared against the target file's
  mtime; no per-file or per-mechanic granularity beyond the staged-batch bypass.
- Receipt JSON `.meta/.omt/omt_harness_e2e_last_run.json`: flat `{passed_at, checks,
  results?, digests?, policy_ver?}` — no slices field (verified 2026-10-11).
- Receipt round-robin fired in practice: R2 needed 2 mid-round e2e mints (`state.py` +
  `lsp_filter.ts` second edits); T4 (feature_150) needed one full e2e for 5 single edits.
- Ledger receipts are already slice-shaped in kind (e2e runs record what they exercised),
  but the GATE cannot consume per-slice freshness because the receipt has no slice blocks.

## Decision (mirrors PROPOSAL_V7 §8.3 proposal: ledger/receipt kinds, single append path)

1. **Slices are mechanic groups**: v1 ships three seed slices — `q` (`.opencode/plugins/omt_q.ts`
   → omt_q probe tests), `net` (`.opencode/plugins/omt_net.ts`, `scripts/omt/net/**`,
   `scripts/omt/net_check.py` → net gate goldens), `split_proof` (`scripts/omt/split_proof.py`
   → split_proof_meta suite). Everything else stays legacy-global; migration continues
   slice-by-slice after v1 (T5's own wording).
2. **Functional source** for the slice map: `.meta/META_HARNESS.omt` `@var receipt_slices`
   (JSON: `{"q": {"files": [...], "tests": [...]}, ...}`), compiled into the IR by
   `harnessc build`; `.opencode/lib/omt_shared.ts` reads IR vars with a pinned TS fallback
   (never die open) — the improvement007/OPT-E pattern.
3. **Receipt JSON grows an optional `slices` map**: `slices.<name> = {passed_at, results_passed,
   digests: {rel: sha256}}`. Top-level fields stay the legacy global block (byte-compat for
   existing readers/minters).
4. **Gate semantics** (`omtHarnessE2eStatus`): resolve `receiptSliceFor(rel)` — first matching
   slice by file list wins; unmapped → legacy global check unchanged. Mapped → the SLICE block
   must be fresh (passed_at ≥ mtime, digest match, results_passed). `policy_ver` stays global
   (a policy edit re-receipts everything, by design). Staged-batch bypass unchanged.
5. **Mint**: new `scripts/omt/receipt.py` (`mint --slice <name> [--root R] [--dry-run]`) runs
   the slice's test set via pytest and writes/merges the slice block (atomic tmp+os.replace —
   GOTCHA_RECEIPT_ATOMIC_MINT). `--slice all` = legacy full-e2e semantics (the existing
   `tests/harness_meta/omt/test_omt_harness_e2e.py` keeps minting the global block).
6. **Slice test sets exclude the 12 triaged failures** (owned outside split, feature_149):
   each slice's `tests` list is green-at-HEAD today; the mint fails loudly if its set goes
   red (fail-closed — a red slice mint cuts no receipt).

## Alternatives rejected

- Sidecar `receipts/` dir per file (Q3 alternative): two append paths, drift-prone; the single
  receipt JSON with slice blocks keeps one atomic write site + one reader.
- Full slice table for every mechanic in v1: unreviewable blast radius; seed 3 slices prove
  the mechanic, migrate the rest later (T5's own "slice by slice").
