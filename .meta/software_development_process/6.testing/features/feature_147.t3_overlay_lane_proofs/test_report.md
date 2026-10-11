# Test report — T3 overlay lane proofs (feature_147)

> Testing phase exit artifact. Parent: Design 001 + operation_spec_overlay + implementation_001. HEAD `4bfb96c` + uncommitted T3 work (this session's mvc + manifest-filter + harness-src + verify-overlay amendments).

## Targeted (hermetic goldens + gate)

`uv run pytest tests/harness_meta/split_proof_meta tests/harness_meta/feature_147.t3_overlay_lane_proofs -q`
- **33 passed** (6 `test_overlay_meta` incl. real `tsc --noEmit` exit 0 + 3 `test_overlay_feature_gate` + 24 firewall/rename_away/ledger/newcomer/ta_strip) — stable across all 4 shell rounds.

## Full lanes (live tree)

`uv run pytest tests/agentx tests/harness_meta -q`
- **12 failed / 2125 passed / 5 skipped** — exactly the 12 pre-existing triaged in v5 (kb_akb×2, net_history, dashboard, 103, omt_q_audit_t1_1, 054 bun-canary, 056 hygiene, 058 probe-live, 060×2, 062-parity). No receipt flake this run. No new failures vs v5 baseline.

## Overlay acceptance (`prove --overlay tmpfs`)

- **Product**: GREEN — `prove --lane product --overlay tmpfs --out /tmp/opencode/` → 1 cert (199+37 files, exempted 0, `cert_sha 1a57e4b5…`), `verify` → **STALE-valid via overlay** (cut at ledger row 224; ledger grew by own cert row — honest, matches STALE-valid precedent). Fix: stage stdlib-only `scripts/omt/mvc_check.py` for SUITE only, remove before SCANS.
- **Harness**: RED with **same 12 pre-existing** (harness-only run: 12 failed / 1218 passed / 7 skipped) — no new vs live. Staging `src/agentx` for SUITE only removed 10 product-coupled extras (newcomer×2, ta_strip×2, e2e, kb_ast_extract real-tree, etc.), back to baseline 12. Scans clean after manifest-filter (missing pinned bench files ≠ drift in copy).
- **Manifest-filter**: product copy drops `scripts/omt/bench/*` (pinned), filter to files present in copy (hermetic empty-manifest goldens unaffected).
- **Verify-overlay**: `verify_cert` falls back to `prove_lane_overlay tmpfs` when current-tree drifts (LOCKED v1 has no overlay field — heuristic: current first, overlay second; slower same contract per design).

## Harness gates

- `test_omt_harness_e2e`: **1 passed**, receipt fresh (`.meta/.omt/omt_harness_e2e_last_run.json` > `split_proof.py` mtime each round; 4 shell-disciplined rounds, ONE receipt refresh per round).
- `harnessc check`: **OK 281 records, 0 errors** (`.github` allowlist from v5 holds).
- `tsc --noEmit`: clean via `test_tsc_clean_skip_open` (real run, `node_modules` present).

## Triage / out of scope

- Harness overlay cannot cut cert until the 12 pre-existing (owned by kb_akb, net_history, dashboard, 103, omt_q, 054/056/058/060/062) go green — same as live lanes. Overlay isolation holds (no new drift); product GREEN proves the mvc + manifest fixes.
- Certs under `/tmp/opencode/` only, rm'd after verify (never commit certs, never `node_modules/`).
- No `src/` diff (T3 touches `scripts/omt/split_proof.py` only + CI + tests + docs).

## Close-out

- WORK.md `[~]`→`[x]` DONE + rotation, T1_SIGNOFF T3 note, CURRENT_STATE `2026-10-11f`, `omt_complete` → Done.
- Commit (free-commit ask-free; push denied): `scripts/omt/split_proof.py`, `test_overlay_meta.py`, `feature147/test_overlay_feature_gate.py`, `.github/workflows/split.yml`, `.meta/.../feature_147...`, `META_HARNESS.omt`, `harness.ir.json`, WORK.md, T1_SIGNOFF, CURRENT_STATE.
