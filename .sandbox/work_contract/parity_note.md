# parity_note — S3 dry/live parity + UNKNOWNs (feature_100, S2-green input)

> HEAD `3490fd5` (S0 base `f1be918` + S2 4-file diffs). S3 records parity, changes nothing.

## 1. What S2 changed (live path only)

- F03 `gate_driver.ts:342-361`: live `runBeforeGates` now evaluates every applicable
  gate (dry continue-all contract); `stopped` recorded, no early return; first
  `OmtBlock` still refuses. Verified: 32 source pins + e2e 1/1 + bench fixture
  identical 2238B (S1/S2 disjoint held) — feature_099 test_report.
- F02 `omt_enforcer.ts:78-104`: advice (nav/kb) may fail open; authority resolution
  fails closed. F05-caller `phase_gate.ts:455`: empty verifier output fail-closed.
  F09 `omt_shared.ts`: authority writes can refuse (`appendJsonlOrThrow`).

## 2. Parity statement

- **Block agrees:** live refusal and dry `op:plan` prediction agree on
  allow-vs-block (S2 goldens assert both sides of each residual + positive controls).
- **Report shape UNKNOWN:** dry `runBeforeGatesDry` continues-all and reports every
  firing; live post-S2 evaluates all but still throws the FIRST block. A consumer
  comparing full dry vs live obligation lists may see ordering/report differences
  on multi-blocker edits — recorded as UNKNOWN, never papered over. S3 demo B
  exercises exactly this (would_block=2, first=g.receipt).
- **Preflight caveat stands:** `preflight.ts` `DRY_CAVEATS[g.net]` — dry cannot verify
  the live net verdict; under concurrency `fire(work_start)` first; solo auto-skips (C1).

## 3. Labels every S3/S4 artifact carries (S1 + S0 residuals)

1. Cost fields are PROXY (no host per-call token usage; `tokens_est = io_bytes // 4`).
2. First-numbers pinned rev `3478bb2` ≠ HEAD — delta stated, no economy claim past proxies.
3. C6 open: lifecycle ops bypass the transition relation — no Petri execution
   guarantee may be claimed (parked S5, gated on S4-keep + S2-green).
4. C1 window open: clear-before-record crash gap — S0–S4 must not depend on replay
   surviving it (parked S6a).
5. 072/073 `6.testing` reports absent on disk (ledger Done, live code present) —
   S3 reuses live code, certifies nothing about the missing reports.

## 4. S3 projection contract with the parity gap

- `blocked`/`first_blocker` in every contract EQUAL the preflight dry values
  (single engine, asserted by `check_invariants`).
- The contract's `stale_or_unknown` always carries the dry/live report-parity
  UNKNOWN (renderer injects it when the caller omits it; never dropped to fit cap).
- S4 re-renders at dispatch revision and rechecks stale revision/generation even
  though S4 never dispatches (frozen profile, PROJECT.md §3 S4).
