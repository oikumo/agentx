# Improvement 006 — OUTCOME (Option A executed)

## Done
- `META_VISION.md` rewritten: 1 dense paragraph → 6 sections (Purpose / Single-source / Budgets+gates+concurrency / Self-evolution / Membrane / Newcomer) + SOURCE/WIRED header. All original claims preserved.
- `.meta/META_HARNESS.omt` (4 edits, e2e receipt refreshed between each):
  1. `@var root_allowlist` += `META_VISION.md` → stray-hygiene error FIXED.
  2. `@doc runtime` += `Vision: META_VISION.md (@doc vision).` → flows into AGENTS.md RUNTIME line (no `harnessc.py` code change).
  3. New `@doc vision tags="VISION"` (nav-indexed, 1-line + pointer).
  4. `@budget nav_index` 67584→67840 (+256 deliberate for vision record).
- `.workflows/meta_harness/META.md` scope += vision pointer (`META_VISION.md`, `@doc vision`).
- Verified render (no write): AGENTS 3549/3584 OK, IR 21699/22016 OK, NAV 67822/67840 OK; RUNTIME line carries vision pointer; VISION in nav index.

## Not done (pre-existing, out of scope)
- `harnessc build` still blocked by 27 pre-existing project-lifecycle drifts (missing lifecycle records + stale manifest). Attempted `project.py backfill+sync` → clobbered active/complete states to draft → reverted via `git checkout` + ledger truncate (13 lines kept). Vision change itself introduces ZERO new check errors (28→27).
- `AGENTS.md` regeneration pending that drift fix (needs state-preserving backfill, separate task).

## Resume
- To land AGENTS.md: fix project drift without clobbering states, then `uv run scripts/omt/harnessc.py build`.
- Proposal file: `IMPROVEMENT_OPTIONS.md` (this dir). Execution per `loops/meta_harness_evolution.md` steps 5-6.

## Follow-up fix (same session)
- `test_tight_budgets_unchanged` regressed (NAV 67822 > pin 67475) → re-pinned `NAV_INDEX_CEIL` 67475→67822 with comment (precedent style) under tests canary skip; now green.
- Full suite: 2085 passed + pin fix; remaining 11 failures verified pre-existing on clean tree (live-state/project-drift, incl. `check_has_zero_errors`, `projections_are_fresh`, `diet_warnings`, 7 live goldens).

## LANDING — "do it" (same session, bug_fix Programming)
- State-preserving lifecycle restore: 25 `create` + 118 `project_link` (origin backfill) + 16 `close` records written via `project_state.write_record` (timestamps ordered: create → links → close), states/features taken from committed WORK.md `## Projects` (1 draft / 8 active / 16 complete). All 118 `feature_\d+.` dirs verified present first.
- `project.py sync` → manifest regenerated, WORK.md `## Projects` byte-identical to HEAD (zero diff), no Status-header flips needed.
- `harnessc check OK — 278 records, 0 errors` (was 27). `harnessc build OK — 278 records → 5 projections`: AGENTS.md RUNTIME now carries `Vision: META_VISION.md (@doc vision).`, VISION nav-indexed.
- `test_budget_diet.py` live pin re-pinned (agents_md 3549 + nav_index 67822 in ≤64B zone) under fresh canary skip; gate tests 44/44 green.
- Full suite: **2091 passed, 6 failed** — all 6 verified pre-existing/flaky full-suite live-state issues (dashboard/managed/net_history bundle replays, thought_review stale, bootstrap_templates, lean_start order-dependent; each fails on clean tree or passes in isolation with changes applied).
- Deliberately NOT backfilled via `project.py backfill` (writes draft-only creates that clobber active/complete — attempted once, reverted).
