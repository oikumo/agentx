# Design 001 — T3 overlay lane proofs (feature_147)

> Parent FEATURE (`2.requirements/features/feature_147.t3_overlay_lane_proofs/`) +
> Analysis 001 (same-track `3.analysis/.../feature_147.../analysis_001_t3_overlay.md`).
> V7 canonical: `PROPOSAL_V7.md` §6 T3 + §E1/E4. Companion ops spec:
> `operation_spec_overlay.md` (same dir — Design→Programming exit artifact).

## E1 — `prove --lane` ephemeral overlay (advisory CLI, zero registry rows)

New flag `--overlay {current,tmpfs,worktree}` (default `current` — v1 behavior
unchanged; T3 acceptance uses `tmpfs`, `worktree` follows the same copy contract
via `git worktree`):

- Product lane: copy tree minus the 4 harness dirs (`scripts/omt/`,
  `scripts/session_inspect/`, `.opencode/`, `.meta/`) into `$TMPDIR/split_proof/<lane>/,
  run `pytest tests/agentx -q` in the copy, then run the AST firewall scans against
  the copy. Harness lane: copy minus frozen `src/agentx/`, run
  `pytest tests/harness_meta -q`, then scan the copy.
- Shared build-roots stay in every copy and are asserted present, not copied around:
  `tests/__init__.py`, `tests/conftest.py`, `tests/constants.py`,
  `tests/testing_utils.py` (T1_SIGNOFF §1; pinned `SHARED_ROOTS` in
  `test_rename_away_meta.py`). `.venv/` + `pyproject.toml`/`uv.lock`/` .python-version`
  are the host toolchain (declared prerequisite, neither lane claims them).
- Cert: LOCKED v1 unchanged (10 fields, `cert_sha` = sha256 of payload minus
  `cert_sha`, ≤2 KiB assert stays). No schema change: the lane suite gates the exit —
  suite red raises `SystemExit` like a firewall `VIOLATION` (no cert cut); green cuts
  the cert exactly as today (scans clean AND lane green). `firewall_verdict` keeps its
  meaning; suite outcome is pass/fail of the command, provenance-bound by the
  `split_proof.cert` ledger row (E3 chain unchanged).
- `verify <cert>` unchanged (re-prove `record=False`, byte-identical minus `tokens_ms`,
  STALE-valid prefix branch). Verifying an overlay cert re-runs the overlay (slower,
  same contract) — document the cost in `--help`.
- Never a rename in the dev tree: all exclusion happens in the copy. `--out` still
  defaults to `.` for current-tree proves; overlay proves default `--out` to the
  overlay dir and copy the cert back (certs under `/tmp/opencode/` per the root-stray
  gotcha — never commit certs).
- Performance: full-lane suites in copies (~2112 tests) are minutes, not seconds —
  `prove --lane both --overlay tmpfs` is a CI/long-loop command; `prove --lane both`
  (current-tree scans) stays the fast local check.

## CI wiring (greenfield — no `.github/workflows/` today)

New `.github/workflows/split.yml` (repo's first CI jobs for the split):

- `product-lane`: checkout, `uv sync --frozen`, `prove --lane product --overlay tmpfs`,
  `verify` each cert, `tsc --noEmit` skipped here (no studio in product copy — by
  construction; note it in the job).
- `harness-lane`: same for `harness` + `tsc --noEmit` over `tools/petri-net-studio`
  (closes the T2 deferral; fail-closed in CI, advisory locally — bun-canary precedent:
  toolchain absence must fail-open locally with a clear skip reason, never red).
- `nightly-full`: full suite + `prove --lane both` (current-tree) + `attest-bridge`
  + `newcomer-probe`, nightly schedule, green kept per V7 §6.
- Jobs are thin shells over the CLI (no logic in YAML — logic lives in
  `split_proof.py`, tested by goldens). Cert artifacts uploaded per run (≤2 KiB each),
  never committed.

## E4 — Tests (TDD plan; canary minted, phase-then-skip)

- `test_overlay_meta.py` (new, `tests/harness_meta/split_proof_meta/`): hermetic
  overlay contract — tiny fixture trees (not the full repo): build a fake root with
  `src/agentx/`, `scripts/omt/`, `tests/agentx/`, `tests/harness_meta/`, shared roots;
  assert product overlay drops exactly the 4 harness dirs and keeps shared roots,
  harness overlay drops `src/agentx/`; assert suite-red → `SystemExit` no-cert,
  suite-green → cert cut ≤2 KiB with stable `cert_sha`; assert `--overlay current`
  behavior byte-identical to v1. Lazy CLI import (RED shape precedent: missing impl
  FAILS exit 1, never breaks collection exit 2).
- `test_ta_strip_meta.py` extension: add `tsc --noEmit` assertion (skip-open locally
  when toolchain absent with reason; strict in CI). Python `ast.dump`-identical +
  CLI `_ta_hash` pins unchanged.
- Lanes green gates per round: targeted `split_proof_meta` → full
  `tests/agentx tests/harness_meta` (2112+12+9 baseline) → `prove --lane both --out
  /tmp/opencode/` + `verify` + rm certs.

## Harness-surface discipline (first since R3)

`scripts/omt/split_proof.py` rides the receipt flow: stage → e2e from new home →
build; ONE edit per file per receipt round; TDD two-hats (RED tests/ only,
GREEN/REFACTOR `scripts/omt/` only — `scripts/` counts as harness surface, not
`src/`, but the same hats apply). `src/` untouched by T3 (no product edits).

## Out of scope (explicit)

E2 `g.split_proof` predicate wiring, T5 per-mechanic receipts, T6 multi-root sync +
4 project relocations, telemetry isolation (`omt_q` live-probe family), UC0 archival,
`bridge:` backlog, `newcomer-probe` `help`-vs-`c` narrative fix (header deviation stands).

## Acceptance

`uv run scripts/omt/split_proof.py prove --lane both --overlay tmpfs --out /tmp/opencode/`
→ 2 certs green + `verify` clean + `pytest tests/harness_meta/split_proof_meta -q` green
+ full lanes 2112+same 12+9 + `tsc --noEmit` clean in CI + no `src/` diff.
