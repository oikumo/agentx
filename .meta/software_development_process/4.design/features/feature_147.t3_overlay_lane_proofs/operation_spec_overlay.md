# Operation spec — overlay (feature_147)

> Companion to `design_001_t3_overlay.md` (same dir). Satisfies the Design→Programming
> exit artifact (`operation_spec_*.md`). Source of truth for flags is
> `scripts/omt/split_proof.py --help` once implemented; this spec pins intent.

## `prove --lane {product,harness,both} [--overlay {current,tmpfs,worktree}] [--out DIR] [--ledger PATH]`

- `--overlay current` (default): v1 behavior — scan the live tree, cut cert per lane,
  append `split_proof.cert` row per cert. Fast local check.
- `--overlay tmpfs`: copy tree to `$TMPDIR/split_proof/<lane>/` minus the other side
  (product: minus 4 harness dirs; harness: minus `src/agentx/`), assert shared roots
  present, run that lane's suite in the copy (`pytest tests/agentx|tests/harness_meta -q`),
  then scan the copy; suite red → `SystemExit` (no cert, like `VIOLATION`); green → cut
  cert (LOCKED v1, ≤2 KiB) + append chain row. Cert copied back to `--out`.
- `--overlay worktree`: same contract via `git worktree` (clean HEAD required; worktree
  removed afterwards even on failure).
- `--out DIR`: cert destination (default `.`; overlay runs default to the overlay dir
  with copy-back; CI uses `/tmp/opencode/`).
- `--ledger PATH`: chain file override (hermetic tests pass tmp; default the real ledger).

## `verify <cert.json> [--ledger PATH]`

Re-prove the cert's lane with `record=False`; pass on byte-identical minus `tokens_ms`;
else STALE-valid if `ledger_sha` is a ledger prefix and all else agrees; else field-drift
failure. Overlay certs re-run the overlay (slow path documented in `--help`).

## `attest-bridge [--ledger PATH]`

Report `{conforming, prose_hits}` over `.projects/**/PROJECT.md` Decisions logs +
append one `split_proof.attest` row. Unchanged by T3.

## `newcomer-probe`

Boot `uv run agentx`, send `help`, assert REPL answers, clean EOF exit. Unchanged by T3
(`help`-not-`c` deviation stands).

## Errors (all `SystemExit`, CLI exit 1)

- `firewall VIOLATION (N edges)` — scans found non-exempt runtime edges (lists them).
- `suite RED in overlay (<lane>)` — lane suite failed in the copy (no cert cut).
- `cert exceeds 2 KiB` — schema-growth guard (assert in `prove_lane`).
- `verify: cert_sha MISMATCH / field drift` — tamper/drift (distinct from STALE-valid).
- `newcomer-probe: FAIL` — console boot/answer failure.
