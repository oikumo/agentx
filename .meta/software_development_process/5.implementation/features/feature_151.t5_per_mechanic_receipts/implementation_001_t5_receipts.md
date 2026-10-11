# Implementation 001 — T5 per-mechanic receipts (feature_151)

> Landed 2026-10-11 (resume session per `sandbox/pause_2026-10-11.md` v8 §v8.2 build order).
> One staged batch, one shell round for omt_shared.ts, single boundary e2e + 3 real-repo self-mints.

## What landed

- **Policy** (`.meta/META_HARNESS.omt`): +`@var receipt_slices_path : .meta/templates/receipt_slices.json`
  — scalar pointer only (JSON never inside an @var payload; DSL colon-handling unverified).
  Build → 282 records (was 281; the new @var is the +1), check 282/0.
- **Manifest** (`.meta/templates/receipt_slices.json`, NEW): 3 seed slices per design_001 §Data model —
  `q`, `net`, `split_proof`. **Impl correction:** the design's drafted net test paths were pre-R1 ghosts
  (`omt/test_net_gate.py`, `.../test_net_gate_feature.py` — nonexistent); the live mint's fail-closed exit
  (pytest 5 "no tests ran" → exit 1, no write) exposed the miss; corrected to the real green-at-HEAD homes
  `feature_050.net_as_gate/test_net_gate.py` + `feature_053.net_gate_concurrency_predicate/` (24 passed).
  Design doc annotated at the data model.
- **`omt_shared.ts`** (+95 lines, 3 anchored hunks, ONE python shell round, uniqueness-asserted):
  - `FALLBACK_RECEIPT_SLICES` pinned const + `receiptSlices()` — IR `@var receipt_slices_path` →
    read+JSON.parse at the injected root; manifest/IR missing → fallback const (never die open, OPT-E;
    hermetic goldens depend on it: seeded tmp roots carry the IR copy but not the manifest).
  - `receiptSliceFor(rel)` — first slice whose files entry equals rel or is a `/`-suffixed prefix;
    unmapped → null. Pure, no receipt I/O.
  - `receiptSliceBlock(name)` — `slices.<name>` reader; absent/corrupt → null (→ legacy global branch).
  - `omtHarnessE2eStatus` slice branch, inserted between `stale()` and the global timestamp check — the
    v1 tail below it is byte-identical. Mapped + block present → **pure** `Date.parse(block.passed_at) ≥ mtime`
    (deliberately NOT `receiptTimestampMs()`: its receipt-file mtime floor would re-couple slices — any
    other slice's mint would refresh this file's validity window) + digest match-if-present +
    `results_passed === true` (strict, fail-closed) + policy_ver checked inside the branch (stays GLOBAL
    for every file — a policy edit re-receipts everything). Block absent → legacy global branch
    (deploy-compat: old receipts stay valid until each slice's first mint). Unmapped → legacy global
    byte-identically.
- **`scripts/omt/receipt.py`** (NEW): `mint --slice <name|all> [--tests PATH] [--root R] [--dry-run]` +
  `status [--root R]`. Manifest read from the CLI's REAL repo (never --root); pytest always `cwd=REPO`
  (uv needs the project; --root gates only receipt path + digest targets); fail-closed (red → exit 1,
  no write); atomic merge tmp+os.replace (GOTCHA_RECEIPT_ATOMIC_MINT); missing digest target → `""`
  (never blocks on absence); `--slice all` never touches the legacy global block; single-line JSON output
  (a multi-line indent form broke the status golden's last-line-JSON idiom).
- **Goldens** (re-shaped in the RED hat before green, per build order step 8): `_seed_tree` builds REAL
  git-dirty tmp roots (git init + config + commit + append marker + utime; `git=False` preserves the
  no-git fail-open pin for the weak golden); receipt writes moved after seeding (digest-bearing blocks
  hash post-append content); legacy-compat golden seeds +0.5h future mtimes (the global branch's
  receipt-file mtime floor makes a stale passed_at alone un-pinnable); probe maps `message`→`msg` (the
  gate returns `{ok, message}`); stale-msg assert pins the baked e2e refresh command ("e2e"), not the
  word "receipt" (the @msg receipt_stale teaching text never says it).

## Round discipline honored

- Stage FIRST (META_HARNESS.omt + omt_shared.ts; re-staged + receipt.py + manifest after the policy edit
  rebound policy_ver — R3 protocol); ONE shell round for omt_shared.ts (zero edit-tool touches);
  `stage --clear` at the boundary (per-file guard resumes fail-closed).
- Boundary e2e 1 passed → self-mints q/net/split_proof MINTED (real slice suites green) → receipt end
  state: global fresh + 3 slice blocks (digests q=1 / net=3 / split_proof=1).
- TDD: RED (ledger row 270) → GREEN 22:08 → REFACTOR 22:09 → DONE 22:11, all at node
  `TestSliceResolution::test_receipt_slice_for_resolves_mapped_and_unmapped`. Note: the done-op's own
  e2e re-mint clobbered the slice blocks (the e2e writer owns the global block) — re-minted after;
  receipt.py's merge preserves the global block by design.
