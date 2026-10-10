# Implementation notes — feature_138 firewall slice

> Delivered (Programming, TDD done ✅): `scripts/omt/split_proof.py` (E1: `prove --lane
> product|harness|both`, `verify`, `attest-bridge`, `newcomer-probe`; LOCKED certs ≤2 KiB,
> hash-chained to ledger + file/live revs) + `scripts/omt/split_proof_exemptions.json` v1
> (8 pinned fixture/path-string lines: 5× `bench/tasks.py`, 3× `bench/sandbox.py`).
> Deferred by design: E2 predicate, E3 kinds, E5 nav SECTION, lane dirs, row #1, UC8.

## Homes (repo-convention wins until T3 lanes land)

- Goldens live at `tests/features/feature_138.split_proof_oracle_firewall_slice/`
  (repo convention: `tests/features/feature_NNN.*`, satisfies the Programming→Testing
  unit-tests gate + `omt_tdd done` feature-suite check for real instead of vacuously).
- `tests/harness_meta/split_proof_meta/` was the V7-E4 forward placement; the lanes do
  not exist yet, so the files move there under the Oracle exemption manifest at T3
  (a planned, manifested migration — not silent).
- No `src/` moves, no `tests/` moves of pre-existing files, no `omt_*` renames.

## Incidental harness repair (required enablement, e2e-receipted)

- `scripts/omt/tdd/state.py`: TDD runner now loads `xdist` explicitly (`-p xdist`;
  `-n0` for single-node runs). HEAD's parallel default (`-n auto --dist loadfile`)
  silently broke every TDD red/green/done with exit 4 (`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`
  suppresses the plugin the addopts require). Receipt: `test_omt_harness_e2e.py` green
  before each subsequent edit to the file (one-edit-per-file-per-round honored).
- `verify` carries a 3× retry + STALE-vs-mismatch distinction: the suite appends real
  `ledger.jsonl` rows on parallel workers (sha-verified), so a single compare is racy.

## Close-out addendum 2026-10-10 (resume session — row #1 + E3 + E2 + E5 shipped)

- **Row #1 DELETED:** `src/agentx/ui/test_omt_mvc_gate.py` (2-line dead code, stale
  `Session` import — collection ERROR, in no suite since `testpaths=["tests"]`).
  Verified: 10/10 goldens + `prove --lane both` clean + `verify` byte-identical.
  UC1 Post no longer self-falsified by this row.
- **E3 ledger kinds** (`split_proof.{cert,attest}`, V7 as-designed): `prove` appends one
  `split_proof.cert` row per cert (lane + cert_sha + prev-ledger_sha Merkle link),
  `attest-bridge` one `split_proof.attest` row; `--ledger` overrides the chain file
  (hermetic goldens pass tmp — real ledger never polluted by tests); missing ledger =
  empty-chain genesis; `verify` re-proves read-only (`record=False`), self-append
  growth lands honestly in STALE-valid. Kinds extend, schema doesn't (A9: no kind
  validation; `read_store`/`read_ledger_net_records` filter `net_*` — replay
  never sees these rows, so no `history.py` change, no feature_044-class gotcha).
- **E2 gate predicate** `g.split_proof` order=37 (after g.net/35, before g.phase/40):
  `.omt` @gate (hard=false, skip_ok=false, when=membrane scope) + @msg + IR build;
  TS IMPL in `gate_driver.ts` (pinned-cert read + cert_sha recompute + ledger
  prefix + chain-row presence — fs reads only, never shells out, never runs the
  suite); break-glass scope=all bypasses (mirrors g.net); fail-open advisory
  locally, fail-closed when CI=1/true/yes. Scope maps updated (preflight
  CLEARING_ACTIONS, omt_q escape-replay, harnessc+status SKIP_SCOPE_TO_GATES,
  Tier-1 drop like receipt). Trust split: gate = freshness signal, CI re-prove
  = authority. `harnessc check` 281 records 0 errors; gate budget 10→11/12.
- **E5 SECTION** `doc.sec.split_proof` (nav-indexed): derives at projection time
  from the `# SPLIT PROOF — …` framed banner (no hand record); states as-of
  denominators (11 omt_*/11 files/14-in-11, 14 CLIs, 20+1 net), ledger-count
  rule, rename-away dirs, manifest path, pinned-cert convention. Budgets grown
  deliberately in the same edits (ir_json →24064, nav_index →69120).
- **Deviations (honest):** E3/E2 implemented before their goldens (TDD order
  inversion — covered by logged tests-canaries, smoke-verified first, goldens
  assert the verified behavior with zero weakened assertions); `--ledger` is
  per-subcommand (global position confused real invocations); no preflight-text
  +0 (V7 cost) — the pin `test_clearing_actions_cover_every_gate` REQUIRES a
  clearing action per gate, so one line added deliberately; WORK.md `[~]` pause
  row relocated pre-Projects → `## Paused` (sync-safe; fixes a pre-existing
  `harnessc check` drift); Tier-1 drops g.split_proof (membrane class).
- **Receipt discipline:** every harness-surface edit preceded by a fresh
  `test_omt_harness_e2e.py` green (one edit per file per round); full suite
  2109 passed + 4 pre-existing triaged drift (net-history/dashboard/
  managed-ops/skip-audit — untouched by this diff).
- **UC8 promotion DONE this session** (user explicit go): `.projects/agentx/
  harness_wrapper_split/` scaffolded (PROJECT.md + CURRENT_STATE.md) +
  `link feature_138 → harness_wrapper_split --origin manual` (override roots,
  WORK.md byte-identical verified, agentx META draft preserved as hand section).
  Gap stated: the "4 pending-move links" conflate project-relocations with the
  feature-level `link` tool (inexpessible — same-slug re-links are no-ops);
  the 4 project DIRS are not moved (pre-T6 clobber); relocation rides T6.
- **NOT in this session:** lanes moves (~190 files — sign-off table
  `T1_SIGNOFF_V9.md` delivered, moves per-bucket next) + T2 goldens
  (rename_away/ta_strip/ledger_contract).
