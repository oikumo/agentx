# Design 001 — T5 per-mechanic receipts (feature_151)

## Data model

### Slice map (functional source: `.meta/META_HARNESS.omt` `@var receipt_slices`)

```json
{
  "q":           {"files": [".opencode/plugins/omt_q.ts"],
                 "tests": ["tests/harness_meta/omt/test_omt_q.py",
                            "tests/harness_meta/omt/test_omt_q_audit.py"]},
  "net":         {"files": [".opencode/plugins/omt_net.ts", "scripts/omt/net/",
                            "scripts/omt/net_check.py"],
                 "tests": ["tests/harness_meta/feature_050.net_as_gate/test_net_gate.py",
                            "tests/harness_meta/feature_053.net_gate_concurrency_predicate/"]},
  "split_proof": {"files": ["scripts/omt/split_proof.py"],
                 "tests": ["tests/harness_meta/split_proof_meta/"]}
}
```

- `files` entries: repo-relative paths; a trailing `/` = directory prefix.
- `tests` entries: pytest paths (file or dir); must be green-at-HEAD (fail-closed mint).
- (impl correction 2026-10-11) the net slice's drafted `tests` paths were pre-R1
  ghosts (`omt/test_net_gate.py`, `.../test_net_gate_feature.py` do not exist) — the
  live mint's fail-closed exit exposed the miss; real green-at-HEAD homes:
  `feature_050.net_as_gate/test_net_gate.py` + `feature_053.net_gate_concurrency_predicate/`.
- TS fallback constant mirrors this JSON (IR-missing safety, OPT-E pattern).

### Receipt JSON (additive, LOCKED-shape compatible)

```json
{
  "passed_at": "...", "checks": [...],            // legacy global block (unchanged readers)
  "slices": {
    "q": {"passed_at": "...", "results_passed": true,
           "digests": {".opencode/plugins/omt_q.ts": "<sha256>"}}
  }
}
```

## Components (one mechanic = five parts; here the receipt mechanic extends)

1. **Map**: `@var receipt_slices` in META_HARNESS.omt → `harnessc build` → IR vars; TS
   `receiptSlices()` in omt_shared.ts (IR first, fallback const).
2. **Gate**: `omtHarnessE2eStatus` — add `receiptSliceFor(rel)` + slice-fresh branch:
   mapped file requires `slices[name].passed_at >= mtime(abs)` AND digest match AND
   `results_passed`; unmapped → legacy global (byte-identical). policy_ver + staged-batch +
   e2e-test-path exemptions unchanged. Slice block ABSENT for a mapped file → fall back to
   legacy global (deploy-compat: old receipts stay valid until each slice's first mint).
3. **Mint CLI**: `scripts/omt/receipt.py` — `mint --slice q [--root R] [--dry-run]`:
   run slice tests (pytest -q, fail → exit 1, NO receipt write), compute sha256 digests of
   slice files, merge slice block (atomic tmp+os.replace), print JSON summary.
   `--slice all` → run every slice's tests + write all slice blocks (does NOT touch the
   global block — the e2e test remains its mint).
4. **Tests**: `tests/harness_meta/feature_151.t5_per_mechanic_receipts/test_receipt_slices_meta.py`
   (bun probes against the real lib + hermetic seeded receipt JSONs; receipt.py mint via
   `--root` hermetic runs) — see operation spec.
5. **Doc**: T1_SIGNOFF note + SECTION pointer via this feature's artifacts (nav-indexed by
   harnessc build automatically).

## Gate flow (mapped file, e.g. `.opencode/plugins/omt_q.ts`)

```
g.receipt fires → guardHarnessReceipt → omtHarnessE2eStatus(rel, abs)
  ├─ not harness / e2e paths / missing / staged / clean-git → ok (unchanged)
  ├─ receiptSliceFor(rel) → "q"
  │    ├─ slices.q absent → legacy global branch (compat)
  │    └─ slices.q present → passed_at ≥ mtime? digests match? results_passed? → ok/stale
  └─ unmapped → legacy global branch (byte-identical v1 behavior)
  policy_ver check: global, unchanged (policy edit re-receipts everything).
```

## Invariants (pinned by goldens)

- I1 slice resolution: mapped files resolve to their slice; directory prefixes match
  descendants; unmapped harness files → null.
- I2 per-slice freshness: slice `q` fresh + global stale + other-slice file dirty-newer →
  `q` file editable, other-slice file blocked (the decoupling win).
- I3 content-bound: digest mismatch inside a slice block blocks even with fresh passed_at
  (feature_074 D-bar carried into slices).
- I4 fail-closed mint: red slice test set → no block written, exit 1.
- I5 atomicity: block merge is tmp+os.replace (GOTCHA_RECEIPT_ATOMIC_MINT).
- I6 legacy compat: receipts WITHOUT `slices` behave byte-identically for every file
  (global branch), including staged/digest/policy_ver paths.

## Rollout

Stage → policy edit (@var) → build → omt_shared.ts slice branch (staged, single round) →
receipt.py (new file, no receipt needed) → goldens (tests canary) → single e2e at batch
boundary → slice self-mints (`receipt.py mint --slice q` etc.) → harnessc check → lanes →
prove → close-out.
