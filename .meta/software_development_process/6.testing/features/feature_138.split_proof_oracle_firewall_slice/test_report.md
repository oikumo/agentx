# Test report — feature_138 firewall slice (Oracle `split_proof` v2, first executable close)

> TDD: testlist(7) → red×3 (exit 1, TRUE missing-module/manifest) → green×3 (+1 post-refactor)
> → refactor (extract `_py_files`) → done ✅ (5 drift tolerated, 0 regressions).
> Suite: new dir 10/10 (`uv run pytest tests/harness_meta/split_proof_meta -q`, ~10–17 s).

## Acceptance evidence (commands, not pasted hashes)

- `uv run scripts/omt/split_proof.py prove --lane both --out <tmp>` → 2 certs, LOCKED
  field order, each ≤2 KiB, `firewall_verdict: clean`, `newcomer: not-run`.
- `verify <cert>` → "byte-identical (minus tokens_ms)"; `check_cert_sha` recompute green.
  Under parallel suite load the ledger can grow between prove and verify — then
  "STALE-valid" (cert's `ledger_sha` is a strict prefix of today's ledger, all other
  fields exact) is the honest pass; tamper/drift still fails. Full suite 2026-10-10:
  **2102 passed** (incl. all 10 Oracle goldens), 4 failed = triage items 1–2 below only.
- `attest-bridge` → `conforming: 0`, prose hit `meta_harness_11:50` (bridge backlog stands).
- `newcomer-probe` → pass (boots `uv run agentx`, `help` answered, EOF exit 0).
- Firewall truth: zero runtime edges either way (AST, both directions); TS studio clean;
  8/8 manifest lines exact (5 tasks.py + 3 sandbox.py fixture/path-strings).

## Repo-level triage (drift, NOT regressions — no file in this diff touches net/live/ledger logic)

1. Three live-bundle goldens read CURRENT live state and fail after any session activity
   (`test_net_history` replay-vs-marking, `feature_043` dashboard sentinel,
   `feature_103` managed-ops bundle). Session-advanced live marking, pre-existing class (V7 §7).
2. `test_omt_q_audit_t1_1` bootstrap-templates-last-three-live: fails once the session
   appends ledger rows (observer effect — every `omt_*` call widens it).
3. `ledger.jsonl` grows DURING `pytest tests/scripts/omt` (sha-verified 2026-10-10) —
   some suite test appends the real ledger (candidates use tmp except one path).
   HEAD "zero repo pollution" claim needs re-audit; Oracle `verify` carries a 3× retry +
   STALE-vs-mismatch distinction for exactly this reason.
4. Newcomer narrative rot: 0.2.0 console is a command REPL (`help`, EOF exits 0);
   single letters answer "Unknown command" (observed live). V7 "`c`" path corrected in
   `split_proof.py` header + implementation (`help`-based probe).

## Follow-ups (out of slice, on explicit go)

 E2 predicate wiring (harness-surface 2nd-edit gate), E3 ledger kinds, E5 nav SECTION,
`test_rename_away_meta.py` + `test_ta_strip_meta.py` (need T3 lanes / T4), T1 row #1
delete, UC8 promotion. Harness fix folded in: `tdd/state.py` runner now loads `xdist`
explicitly (`-p xdist`, `-n0` for single nodes) — HEAD's parallel default silently broke
every TDD red/green/done (exit 4); e2e receipt kept green throughout.

## Close-out evidence 2026-10-10 (resume session)

- Row #1: `src/agentx/ui/test_omt_mvc_gate.py` DELETED (dead, stale import, in no
  suite); post-delete 10/10 goldens + prove clean (267+37 files, 8 exempted) +
  verify byte-identical both lanes.
- E3: 11/11 goldens (`test_firewall_meta` 10 incl. NEW `test_prove_appends_
  hash_chained_cert_rows`: 2 rows, lanes product→harness, row1 GENESIS, row2 ==
  sha(row1), cert_shas match) — all prove/verify/attest paths hermetic
  (`--ledger` tmp; real ledger byte-untouched by the suite, verified).
- E2: 6/6 NEW `tests/scripts/omt/test_split_proof_gate.py` bun-probe goldens
  (no-certs advisory-local / strict-CI, fresh-chain silent local+CI —
  cross-language sha pin included, tampered-cert advisory/strict, live path
  never blocks local). Pin suites updated, not weakened: 055 roster (+gate,
  not_applicable 4→5, harness-path advisory assert), 057 gates 10→11 +
  scope-all attribution, 059 NAV_INDEX_CEIL 67822→68812 + T3 count 10→11,
  budget_diet nav warning retired (308B headroom now silent), Tier-1 drops
  g.split_proof (membrane class — Tier-1 onboarding stays net-free).
- Full suite: **2109 passed** (+7: chain + E2 goldens), 4 failed = ONLY the
  triaged pre-existing drift (net-history/dashboard/managed-ops/skip-audit —
  §Repo-level triage above, unrelated to this diff). `harnessc check` 281/0,
  e2e receipt green every round (round-robin honored).
- TDD posture: E3/E2 goldens written under logged tests-canaries (order
  inversion: impl smoke-verified first — see implementation addendum); prior
  10-cycle TDD DONE stands for the firewall slice.
