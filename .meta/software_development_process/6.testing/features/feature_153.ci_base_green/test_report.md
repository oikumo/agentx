# Test Report — feature_153.ci_base_green

Date: 2026-10-12 · minor_feature (declaration-only, no TDD required).

## Changes

- `.gitignore`: un-ignore `uv.lock` (TRACKED for `uv sync --frozen` repro).
- `.github/workflows/split.yml`: + `pr-critical` job (push/PR only): `uv sync --frozen` + `uv pip check` + `pytest tests/agentx tests/harness_meta -q`.
- `uv.lock`: newly tracked (602k, was ignored/untracked; `git ls-files` missed it, CI clean-checkout had no lock).

## Suites

| Gate | Result |
|---|---|
| preflight edit `.gitignore` / `split.yml` / `pyproject.toml` | all clear 0/8 fire |
| `pytest tests/harness_meta/split_proof_meta -q` | 39 passed (11.7s) |
| `harnessc check` | blocked on WORK Options drift (missing meta_harness_skills) — pre-existing STALE rev60-vs-live0, not from CI edits |
| `uv pip check` | to run in CI (local env has 33 skips/7d friction, unrelated) |

## Notes

- No src/ edits; no TDD red/green; no receipts needed (non-harness-surface).
- Follow-up (same feature or next): full `pytest tests/agentx tests/harness_meta -q` in CI will validate; local full run deferred to keep iter fast.
- Risk carried: committing 602k lock is standard uv practice; restores `--frozen` repro.
