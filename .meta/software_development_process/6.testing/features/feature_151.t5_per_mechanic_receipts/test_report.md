# Test Report — feature_151.t5_per_mechanic_receipts (T5 per-mechanic receipts)

Run date: 2026-10-11 (resume session per pause v8 §v8.2; gates re-verified after a mid-close server
restart — state re-read from ledger/git before continuing, nothing re-done blindly).

## Hermetic goldens (10) — `tests/harness_meta/feature_151.t5_per_mechanic_receipts/`

- Final run: **10 passed** (9.37s; first full-green run 11.02s). Bun probes drive the REAL
  `omt_shared.ts` with `initOmtShared(root)`-injected seeded trees; receipt.py driven via `--root` tmp
  copies + `--tests` overrides; no golden writes the real receipt (root-stray class banned).
- Coverage per the 8-behavior testlist: I1 resolution (exact + dir-prefix + unmapped null), I2 decoupling
  (real-git-root strong pin + no-git fail-open weak pin), I3 digest content-binding, I4 fail-closed mint,
  I5 atomic merge + status read-only, I6 legacy compat (+0.5h-future-mtime stale pin — receipt-file
  mtime floor documented in the test), 3 CLI goldens (mint green/red, status, all-mint leaves global).

## TDD cycle

- RED verified exit 1 at the pinned node (ledger row 270, 19:52Z); goldens re-shaped in the RED hat
  (real git-dirty roots) while staying red; GREEN 22:08, REFACTOR 22:09, DONE 22:11 — same node
  throughout (node-granularity gotcha honored).

## Live proofs

- Boundary e2e `tests/harness_meta/omt/test_omt_harness_e2e.py`: 1 passed (receipt minted for the batch).
- Self-mints (real repo, real slice test sets): `q` → test_omt_q.py + test_omt_q_audit.py green;
  `net` → feature_050/test_net_gate.py + feature_053 dir (24 passed); `split_proof` →
  split_proof_meta/ green. All 3 blocks minted; digests q=1 / net=3 / split_proof=1; `receipt.py status`:
  global + 3 slices, all results_passed true.
- Fail-closed proof (unplanned but load-bearing): the net slice's drafted ghost test paths → pytest
  exit 5 → mint exit 1, NO write — the I4 contract observed live, before the manifest correction.

## Regression + lanes + oracle

- split_proof_meta regression: 39 passed.
- Lanes `tests/agentx tests/harness_meta`: **12 failed / 2144 passed / 5 skipped** — the 12 are the SAME
  pre-existing triaged set (058, kb_akb×2, 054, net_history, 056, 103, 062-parity, 060×2, t1_1-bootstrap,
  dashboard/043 — owned outside split per feature_149), **zero new failures**; 2144 = 2134 baseline + 10
  new goldens.
- `prove --lane both --out /tmp/opencode/`: product + harness clean (files=268+37, exempted=8), 2 certs
  cut; `verify` both STALE-valid (cut at ledger rows 275/276; ledger only grew since — cert-growth-only,
  the accepted honest verdict); certs rm'd, no root strays.
- `harnessc check`: **282 records / 0 errors** (was 281; +1 @var record).
