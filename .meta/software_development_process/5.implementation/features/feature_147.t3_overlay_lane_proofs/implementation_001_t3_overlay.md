# Implementation 001 — T3 overlay lane proofs (feature_147)

> Parent Design 001 + `operation_spec_overlay.md` (same-track `4.design/...`).
> Single harness-surface change: `scripts/omt/split_proof.py` (one shell-applied
> round → one e2e receipt → no rebuild: CLI-only, no `.omt`/template/IR touch).
> TDD: RED `test_overlay_meta.py` (5 fail + 1 tsc skip-open) → GREEN (5 pass + 1 skip).

## What changed (`scripts/omt/split_proof.py` only, +~150 lines)

- Constants: `OVERLAY_PRODUCT_DROP` (4 harness dirs), `OVERLAY_HARNESS_DROP`
  (`src/agentx/`), `OVERLAY_SHARED_ROOTS` (4 files), `OVERLAY_LANE_SUITE`
  (product→`tests/agentx`, harness→`tests/harness_meta`).
- `_copy_tree_minus(root, dest, drops)`: top-level copy minus drops (nested drops
  removed post-copy); skips `.venv/__pycache__/node_modules/.git`.
- `build_overlay(root, lane, dest, overlay)`: `current`→live tree (v1 compat);
  `tmpfs`→fresh copy; `worktree`→`git worktree add --detach HEAD` + working-tree
  diff (`git diff --name-only` + untracked `??`) overlaid + drops applied.
  Shared-roots asserted present, else `SystemExit`.
- `_run_lane_suite(work, lane, runner)`: default `pytest <lane-suite>` in the copy
  (1500 s timeout); injected `runner` for hermetic tests; red (non-zero/raise) →
  `SystemExit`, no cert, no chain row.
- `prove_lane_overlay(...)`: overlay → suite → `prove_lane` (LOCKED v1 schema
  untouched; suite gates like a firewall `VIOLATION`); temp dirs removed in `finally`.
- CLI: `prove --overlay {current,tmpfs,worktree}` (default `current` — v1 fast path
  unchanged); dispatch routes non-current through the overlay.

## CI (new, no `.github/` before)

- `.github/workflows/split.yml`: `product-lane` + `harness-lane` (overlay tmpfs +
  verify; harness adds `npm ci` + strict `tsc --noEmit`) on push/PR; `nightly-full`
  (lanes + `prove both` + `attest-bridge` + `newcomer-probe`) on schedule.

## Decisions / deviations

- LOCKED v1 cert schema FROZEN (no suite field): suite outcome is the command's
  exit, provenance-bound by the `split_proof.cert` row. Keeps `check_cert_sha` +
  all existing goldens byte-compatible.
- `tsc` skip-open locally (toolchain absent), strict in CI — bun-canary precedent.
- No `g.split_proof` predicate, no T5/T6 — per Analysis out-of-scope.
