# Analysis 001 — T3 overlay lane proofs (feature_147)

> Parent: `2.requirements/features/feature_139.feature_147_t3_overlay/FEATURE.md`
> Sources: `sandbox/orthogonality_001_wrapper_split/PROPOSAL_V7.md` (§6 T3 + §E1/E4),
> `scripts/omt/split_proof.py` header (v1 limits: current-tree scan, overlay lands with T3),
> `tests/harness_meta/split_proof_meta/test_rename_away_meta.py` (HARNESS_DIRS + SHARED_ROOTS pin),
> `T1_SIGNOFF_V9.md` (§1 lanes table), `.projects/agentx/harness_wrapper_split/CURRENT_STATE.md`
> (`2026-10-11e` Next), `sandbox/pause_2026-10-11.md` v3 §2.

## Problem

`prove --lane` is firewall-scans-only against the current tree (header: "worktree
overlay lands with T3"). Lanes exist and are green (`tests/agentx/` + `tests/harness_meta/`
mirror moves R1–R6 complete, `tests/features/` retired to `__pycache__` shells) but no
proof runs the lane suite with the other side renamed away. CI is unwired (no
`.github/workflows/` — split runs + nightly full are V7 §6 prose, not jobs).
TS TA-strip is deferred (`test_ta_strip_meta.py`: py `ast.dump`-identical pinned,
TS `// TA:` comment-only, `tsc --noEmit` deferred to T3 CI). Shared build-roots
(`tests/__init__.py`, `conftest.py`, `constants.py`, `testing_utils.py`) are declared
in T1_SIGNOFF §1 + pinned in `test_rename_away_meta.py` SHARED_ROOTS but not enforced
by `prove` (no overlay to depend on them staying put).

## Evidence (re-measured 2026-10-11 resume)

- Lanes baseline: 2112 passed + same stable 12 pre-existing + 9 skipped (T2 close-out
  `ca6a937`/`4bfb96c`; triaged: kb_akb×2, net_history, dashboard, 103 live-replay,
  omt_q_audit_t1_1 live probe, 054 bun-canary, 056 hygiene, 058 probe-live, 060×2, 062-parity).
- `tests/harness_meta/split_proof_meta/` 5 files: firewall / rename_away / ledger_contract /
  newcomer / ta_strip (R6 `6575842` + T2 `ca6a937`).
- `HARNESS_DIRS` (product-lane rename-away): `scripts/omt/`, `scripts/session_inspect/`,
  `.opencode/`, `.meta/` (V7 §7 acceptance). Harness-lane: frozen `src/agentx/` minus
  (PROPOSAL_V7 §E1: copy tree minus side, run lane suite, emit cert).
- Cert: LOCKED v1 10 fields, `cert_sha` = sha256(payload minus `cert_sha`), ≤2 KiB assert
  in `prove_lane` (`split_proof.py:311`). Kinds `split_proof.{cert,attest}` append-only (E3 landed).
- Ledger `157` rows via `wc -l .meta/.omt/ledger.jsonl`; phase ledger: Analysis
  `feature_147.t3_overlay_lane_proofs` declared 17:54:33Z, still valid (`omt_status`
  expires 8h, valid next Design/Testing). `src/` BLOCKED until design doc lands.
- CI: no `.github/workflows/`; `.workflows/` is catalog above harness (not CI jobs).
- Newcomer probe deviation (header): sends `help`, not `c` (0.2.0 console is command REPL).

## Decision

Build T3 as `prove --lane` ephemeral overlay (`git worktree` + tmpfs copy, never a rename
in the dev tree): product-lane = copy tree minus 4 harness dirs, run `pytest tests/agentx`;
harness-lane = copy minus frozen `src/agentx/`, run `pytest tests/harness_meta`;
emit ≤2 KiB LOCKED cert per lane + `verify` byte-identical/STALE-valid unchanged.
Wire CI: split runs (per-lane jobs on overlay) + nightly full kept green, shared build-roots
declared as prerequisite (neither lane claims them). Add TS `tsc --noEmit` for TA-strip
(py `ast.dump`-identical already pinned by T2). Advisory CLI only (`reason_check`
precedent — zero registry rows); predicate `g.split_proof` stays out of scope
until T5 slices land (global `g.receipt` still guards harness surface).
Defer: telemetry isolation, T4 strip-TA golden hardening beyond tsc, T5 per-mechanic
receipts, T6 multi-root sync + 4 project relocations, UC0 archival, `bridge:` backlog.
