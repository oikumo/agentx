# OMT SESSION STATE — feature_023.deep_harness_tests (2026-07-19, ~21:45 UTC)

> Resume point for the NEXT opencode session. Read this first, then WORK.md.
> Process state: `omt_phase{task_type:test, phase:Testing, feature:feature_023.deep_harness_tests}`
> + `omt_skip{scope:tests}` recorded (both have ~8h windows; re-declare if expired).

## Mission (user directives this session)

1. Understand `.meta/doc/opencode_plugins/OpenCode Plugin Creation Guide.md`.
2. "make a full test and new ones for feature_023 and meta harness in deep".
3. "opencode loads plugins automatically" + "use the real opencode with
   --print-logs" → deep tests must drive the REAL binary, not just node runners.

## What the full-suite run revealed (7 failures, 3 root causes)

- `test_omt_harness_e2e.py` + `test_omt_lifecycle_e2e.py`: stale
  `.opencode/plugin/` (singular) paths — dir was renamed to `plugins/` in
  commit a3ffb81. **FIXED.**
- `test_omt_hook_effects_production.py`: conceptually broken — importlib-loads
  `.ts` files as Python. **REWRITTEN** as a pytest wrapper around
  `npx tsx test_hook_effects_production.ts` (banner assertion).

## TWO LIVE-CONFIRMED DEAD GUARDS (F14-class) — FIXED, UNCOMMITTED

Proven by driving the real opencode 1.18.3 binary (`opencode run --format json`):

- **BUG-A (critical):** a3ffb81's "F14 fix" wrongly changed the BEFORE-hook
  edit chain to `input?.args?.filePath`. SDK d.ts: before-hook input has NO
  args (args on OUTPUT). `raw` was always undefined → `if (!raw) return` →
  ALL before-hook edit guards dead in production (protected files, e2e
  receipt, tests canary, src phase gate, TDD two-hats). Live proof pre-fix:
  README.md edit landed with no phase/skip. **Fixed:** restored
  `output?.args?...` + corrected comment in `.opencode/plugins/omt_enforcer.ts`
  (~:944). Live proof post-fix: README.md edit blocked with
  "⛔ OMT++ gate: 'README.md' is protected…".
- **BUG-B:** same commit renamed plugin→plugins but left
  `isOmtHarness` prefix `.opencode/plugin/omt_` (never matches). **Fixed:**
  → `.opencode/plugins/omt_` (~:499). Static-pinned; live probe was
  inconclusive BY DESIGN (see below).

## Files changed (git status at checkpoint)

```
 M .opencode/plugins/omt_enforcer.ts   (BUG-A + BUG-B + :609 comment)
 M tests/scripts/omt/test_omt_harness_e2e.py      (plural paths ×5)
 M tests/scripts/omt/test_omt_lifecycle_e2e.py    (plural path :876)
 M tests/scripts/omt/test_omt_hook_effects_production.py (tsx wrapper)
?? tests/scripts/omt/test_omt_enforcer_guard_source_pins.py  (10 pins, GREEN)
?? tests/scripts/omt/test_omt_live_opencode_guards.py        (6 live tests)
```

## Verified so far

- `test_omt_enforcer_guard_source_pins.py`: **10/10 GREEN** (was 9 RED pre-fix).
- Live README.md probe: guard fires post-fix ✓ (also proves opencode loads
  `.opencode/plugins/*.ts` directly — dist/ NOT rebuilt, fix took effect).
- Manual live probes (equivalents of the new live tests): nav reminder +
  THINK-ANYWHERE digest in first tool result ✓; omt_status callable ✓;
  `--pure` A/B control: zero injections ✓; no plugin errors in
  `--print-logs` ✓.

## OPEN — resume here (in priority order)

1. **Fix the BUG-B live test design** (TA: todo tagged at
   test_omt_live_opencode_guards.py:144): `omtHarnessE2eStatus` (enforcer
   :548-569) is a SECOND-EDIT guard — `if (!isGitDirty(rel)) return ok`.
   The current test only touches mtime → git-clean → guard correctly passes.
   Rewrite: dirty the plugin via Write (probe content) → attempt 2nd edit via
   real opencode → assert blocked with "unverified changes" message → restore
   from backup in `finally`.
2. **Run the new live module** (never run as a suite):
   `uv run pytest tests/scripts/omt/test_omt_live_opencode_guards.py -v`
   (~3-4 min, real LLM calls; consider `-k "not BUG-B"` until #1 lands).
3. **Run the FULL harness suite** (expect green; watch for tier_c/feature_022
   tests that drove the before-hook while guards were dead — they may now
   behave differently with guards alive):
   `uv run pytest tests/features/feature_023.meta_harness_improvement/ tests/scripts/omt/ -q`
4. **Refresh the e2e receipt** (paths fixed → e2e should pass; needed so
   future plugin edits aren't blocked once BUG-B live-confirmed):
   `uv run pytest tests/scripts/omt/test_omt_harness_e2e.py -q`
5. **dist/ decision:** `.opencode/dist/*.js` still carries BOTH bugs but is
   provably NOT what opencode loads (.ts fix went live without rebuild).
   No tsconfig exists. Decide: sync (tsc flags), delete, or leave with a note.
6. Update WORK.md (scratchpad + mark feature_023 line [x] when suite green).
7. Report to user; commit ONLY if explicitly asked.

## Gotchas learned this session (add to WORK.md scratchpad on resume)

- **F14 mirrored in the before-hook:** before-hook contract ≠ after-hook.
  before: args on OUTPUT; after: args on INPUT. a3ffb81 applied the after-hook
  fix to both — killing every edit guard while runner fixtures stayed green.
- **Runner fixtures can't catch contract drift** — only real-binary tests can.
  Recipe: `opencode run --format json "<prompt>"` + jq on tool_use events;
  `--pure` as A/B control; `--print-logs --log-level DEBUG` for bootstrap.
  Assert FILE-STATE (byte-identical), not just tool messages.
- **e2e receipt guard is a second-edit guard** (git-dirty based, enforcer :554).
- `python3` heredocs are denied by repo permissions — use `jq` or `uv run`.
- Probe hygiene: snapshot + restore any file a live probe may touch
  (README.md, omt_status.ts were both restored this session).
