# Operation Spec 001 — T5 per-mechanic receipts (feature_151)

Design→Programming exit artifact (§12). Consumer-facing operations for the new mechanic.

## O1. Resolve a file's slice

`receiptSlices()` (IR `@var receipt_slices`, TS fallback) → `receiptSliceFor(rel)`:
first slice whose `files` entry equals `rel` or is a `/`-suffixed prefix of it. Returns
`null` for unmapped files. Pure — no I/O.

## O2. Edit a mapped harness file (agent flow, unchanged ceremony)

`g.receipt` now checks the file's SLICE block: stage → edit → `uv run scripts/omt/receipt.py
mint --slice <name>` (runs ONLY the slice's tests) → edit again within the slice if needed.
Other slices' files remain editable under their own blocks. Policy edits
(`META_HARNESS.omt`) still require the full e2e + build (policy_ver global).

## O3. Mint a slice receipt

`uv run scripts/omt/receipt.py mint --slice q [--root <repo>] [--dry-run]`
- Runs the slice's `tests` via `uv run pytest <paths> -q` at `--root` (default: repo).
- Any failure → exit 1, receipt untouched (fail-closed: a red slice cuts no receipt).
- Success → compute sha256 for each slice `files` entry (missing file → empty digest,
  never blocks on absence), merge `slices.<name> = {passed_at: now_iso,
  results_passed: true, digests}` into `.meta/.omt/omt_harness_e2e_last_run.json`
  (atomic tmp+os.replace), print `{"slice": "...", "passed_at": "...", "tests": [...]}`.
- `--slice all` = every slice (does not touch the legacy global block).
- `--dry-run` = run tests, print the block, write nothing.

## O4. Verify receipt state (read-only)

`uv run scripts/omt/receipt.py status [--root <repo>]` — prints global `passed_at` (or
`absent`) + per-slice `passed_at`/`results_passed`/digest counts; never writes.

## O5. Gate semantics (enforcer, `.opencode/lib/omt_shared.ts`)

`omtHarnessE2eStatus(rel, abs)`:
- unchanged early exits (non-harness, e2e/receipt paths, missing, staged, clean-git);
- mapped file: `slices[name]` absent → legacy global branch; present → fresh requires
  `passed_at ≥ mtime(abs)` + `digests[rel]` match (when present in block) + `results_passed`;
- unmapped → legacy global branch byte-identically;
- `policy_ver` comparison stays global for ALL files.

## O6. Hermetic test surface

Goldens drive the real TS lib via bun probes with `--root`-injected seeded receipt JSONs
(slice resolution, per-slice freshness, digest content-binding, legacy compat) and drive
`receipt.py` via `--root` tmp copies (fail-closed mint, atomic merge, `status`, `all`).
No goldens write the real receipt (live-repo mutation banned — root-stray class).
