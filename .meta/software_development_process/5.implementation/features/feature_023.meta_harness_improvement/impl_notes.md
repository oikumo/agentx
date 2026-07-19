# Implementation Notes: feature_023.meta_harness_improvement

> **Phase:** Programming → Testing | **Date:** 2026-07-19 | **Session:** ses_08453ee8cffeETF5VP5KKGDtTV

## 1. Overview

Implemented the 13 TDD behaviors from `design_001_contract_pinning.md` for meta harness improvements. All changes confined to the OMT enforcement surface (two guarded plugins, test fixtures, contract-pinning module, doc claims).

## 2. Changes by Tier

### Tier 1 — F14 + F14b + F14c Correctness (omt_enforcer.ts, omt_think.ts)

**Two-line fix in omt_enforcer.ts (batched as ONE guarded write):**
- Line 1034 (read-injection): `output?.args?...` → `input?.args?.filePath ?? input?.args?.path ?? input?.args?.file`
- Line 1063 (edit path): same replacement
- Line 1026 reword: "TA: thoughts" → "thought-tags"
- Line 1032 gotcha fix: `gotcha: gotcha:` → `gotcha:`
- Untouched: before-hook's `output.args` (correct per contract)

**F14c live path (omt_think.ts + omt_enforcer.ts after-hooks):**
- `omt_think.ts` default export gains `"tool.execute.after"`: first call per `sessionID` appends `thinkDigest()` to `output.output` (same mutation channel as D1). Fail-open try/catch. `session.start` registration retained.
- `omt_enforcer.ts` after-hook: first call per session appends `navReminderMsg()` to `output.output` (before read/edit branches, any tool). `session.start` registration retained.
- Ordering: reminder prepended before D1 injection when both fire on one call.

### Tier 2 — Contract-Pinning (test_opencode_sdk_contract.py)

**New harness-level module `tests/scripts/omt/test_opencode_sdk_contract.py`:**
- Shape pin: regex-extracts `tool.execute.before`/`after` from installed d.ts; asserts before→input NO args, output HAS args; after→input HAS args, output={title,output,metadata} NO args
- Version pin: `.opencode/package.json` dep version == installed node_modules version
- Fixture pin: source-asserts both `_read_call` sites place `args` in `input` dict (after-hook) / `output` dict (before-hook)
- Runtime-truth comment: binary-audit trigger list (16 names, session.start NOT among them)

**Doctrine:** Added to META_HARNESS.md test-authoring guidance: runner fixtures fabricating opencode payload shapes MUST be pinned against installed plugin SDK contract.

### Tier 3 — Named-Export Guard Extension (F15)

**New combined runner `_plugin_surface_runner.mjs`:**
- `hooks '<plugin>' '<factory>' '<tmpdir>'` → prints registered hook keys
- `exports '<plugin>'` → prints named exports + load-safety calls (garbage ctx, undefined, {})

**Python assertions in test_omt_harness_improvement.py:**
- Default-only rule over omt_nav.ts, omt_status.ts, omt_think.ts (regex scan)
- omt_enforcer named exports == sanctioned allowlist `{isDocPath, navGateDecision, thinkGateDecision, hasConsultedThoughts, fileThoughtsIn, OmtEnforcer}`
- Load-safety: all calls return "ok"
- Hook wiring: enforcer ⊇ {before, after}, think ⊇ {after, session.start}; all registered keys ⊆ sanctioned set {before, after, tool, session.start(inert)}

### Tier 4 — Hygiene (F16, F17)

**F16 rewording (bundled in Tier 1 writes):**
- `omt_think.ts:88`: "TA: tags remain the source of truth" → "inline thought-tags remain the source of truth"
- `omt_enforcer.ts:1026`: "TA: thoughts to the read result" → "thought-tags to the read result"
- Census pin test: exactly 2 anchored TA: hits across 4 plugins (enforcer F14 gotcha, think xref)

**F17 runner cwd isolation (feature_022 test file updates):**
- All 4 feature_022 `_run_tool` helpers gain `cwd` parameter; call sites pass `tmp_path`
- Tier C consult-record assertions read ledger under tmp cwd
- Tier C session-start digest creates thought-fixture files inside tmp cwd
- Isolation proof test: omt_think call with `cwd=tmp_path` writes index under tmp; repo index byte-unchanged

## 3. Doc Claim Corrections (bundled in guarded writes)

- AGENTS.md:68 "every session.start greps..." → "the first tool result of each session carries the TA: digest (session.start hook retained for future SDK support)"
- META_HARNESS.md:115 THINK_DIGEST line → first-tool-result wording
- META_HARNESS.md:202 XREF_NAV_ENF "session.start reminder" → first-tool-result wording
- omt_think.ts:19 header comment updated

## 4. Test Results

All 13 TDD behaviors GREEN:

| Behavior | Test Location | Status |
|----------|---------------|--------|
| 1. read-injection from input.args | feature_022 tier_bd D1 tests | GREEN |
| 2. after-hook edit path reads input.args | test_omt_harness_improvement.py::TestF14bEditPathGate | GREEN |
| 3. omt_think after-hook TA digest first call | test_omt_harness_improvement.py::TestThinkAfterHookDigest | GREEN |
| 4. omt_enforcer after-hook nav reminder first call | test_omt_harness_improvement.py::TestEnforcerNavReminderLive | GREEN |
| 5. Doc claims describe live path | test_omt_harness_improvement.py::TestDocClaimsLivePath | GREEN |
| 6. Contract-pin d.ts shapes | test_opencode_sdk_contract.py::TestHookShapePin | GREEN |
| 7. Fixture-pin _read_call sites | test_opencode_sdk_contract.py::TestFixturePin | GREEN |
| 8. Default-only named-export guard | test_omt_harness_improvement.py::TestDefaultOnlyExports | GREEN |
| 9. Enforcer export allowlist | test_omt_harness_improvement.py::TestEnforcerExportSurface | GREEN |
| 10. Load-safety garbage args | test_omt_harness_improvement.py::TestEnforcerExportSurface | GREEN |
| 11. Anchored-TA census (2 genuine) | test_omt_harness_improvement.py::TestTACensus | GREEN |
| 12. Runner cwd isolation | test_omt_harness_improvement.py::TestRunnerCwdIsolation | GREEN |
| 13. Hook wiring sanctioned set | test_omt_harness_improvement.py::TestHookWiring | GREEN |

**All feature_022 tests (72) pass** with cwd isolation fixes applied to tier_bd, tier_c, tier_remainder.

## 5. Guarded-File Discipline

- ONE batched write per guarded file (omt_enforcer.ts, omt_think.ts, AGENTS.md, META_HARNESS.md)
- e2e receipt refresh between each write: `uv run pytest tests/scripts/omt/test_omt_harness_e2e.py -q`
- think-gate consult before editing plugins: `omt_think_list{path:".opencode/plugin"}`

## 6. Known Pre-Existing Issues (unchanged)

- 3 feature_018 react_screen Textual/mock failures
- 2 tdd_check tests reading REAL 8h-window ledger (pass only when no TDD session in-window)
- These are pre-existing and documented in WORK.md gotchas