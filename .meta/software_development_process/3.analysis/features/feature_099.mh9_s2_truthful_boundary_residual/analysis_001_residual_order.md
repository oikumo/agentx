# analysis_001 — S2 truthful-boundary residual (ordered F09→F05-caller→F02→F03)

> Feature `feature_099` · HEAD `f1be918` · smallest diffs, copy line-512 fail-closed pattern · positive controls required.

## Order + smallest diffs (disjoint from S1 bench files)

1. **F09** (`.opencode/lib/omt_shared.ts:154-159`): authority writes report failure; advisory stays best-effort. Change `appendJsonl` to return boolean / throw on authority paths (`ledger`, `thoughts index`, phase/complete records); keep silent catch only for advisory (`notify`, bootstrap). Goldens: failed-write refuses (ENOSPC/EROFS mock) on authority; advisory still passes.
2. **F05-caller** (`.opencode/lib/enforcer/phase_gate.ts:455`): change `|| '{"ok":true}'` → `|| '{"ok":false}'` (copy `:512`). Empty/malformed/nonzero → `TDD validate-exit error — blocked`. Python verifier behavior unchanged (caller contract only). Goldens: empty stdout, malformed JSON, nonzero-exit envelope each block; valid `ok:true` passes (positive control).
3. **F02** (`.opencode/plugins/omt_enforcer.ts:100-103`): split advice (nav/kb/bootstrap tracks — may fail open) from authority resolution (phase/protect/receipt/net/think — must refuse on unknown/error). Handler rethrows `OmtBlock` AND authority-path errors; advisory paths keep warn+allow. Goldens: injected nav-track throw still allows; injected authority-resolve throw refuses.
4. **F03** (`.opencode/lib/enforcer/gate_driver.ts:219-221 + :349 vs :408-410`): compose obligations on live path — no `stop` suppression of unrelated gates. Either live adopts dry continue-all (collect all blocks, throw first) or divergence is documented UNKNOWN in S3. Smallest diff: live collects decisions like dry, then throws. Goldens: tests-canary target still stops the edit BUT later-gate obligations are evaluated + reported (no silent suppression).

## Live-surface discipline

Harness-surface second-edit guard: ONE edit per file per e2e receipt (parallel OK), ONE refresh per round; e2e test file receipt-EXEMPT. Stage (snapshot → allow → single e2e → clear) + `check`/`build`/suite green before AND after. Host-qualification limits documented (no new authority claims).

## Exit

Allow/deny matrix on real edits (protected, harness-surface, tests-canary, src/phase) incl. all four seeded invalid classes rejected + valid controls accepted.
