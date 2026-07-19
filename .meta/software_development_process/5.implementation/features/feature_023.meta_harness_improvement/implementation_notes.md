# Implementation Notes: feature_023.meta_harness_improvement

> **Phase:** Programming → Testing | **Feature:** feature_023.meta_harness_improvement
> **Source:** design_001_contract_pinning.md | **Completed:** 2026-07-19

## 1. Summary

Implemented all 13 TDD behaviors from design_001_contract_pinning.md §6 across four tiers:

- **Tier 1 (F14 + F14b + F14c):** Contract-pinning fixes for omt_enforcer.ts tool.execute.after hook, MVC++ post-edit gate, session-start → first-tool-result live path migration, doc claim corrections
- **Tier 2 (Contract Pinning):** New harness-level module test_opencode_sdk_contract.py pinning SDK d.ts shapes, version, and fixture correctness
- **Tier 3 (Named-Export Guard Extension):** New combined runner _plugin_surface_runner.mjs + test_omt_harness_improvement.py assertions for default-only exports, enforcer allowlist, load-safety, hook wiring
- **Tier 4 (Hygiene/F17):** TA: comment rewording (TA: → thought-tags), runner cwd isolation for feature_022 tests, anchored-TA census pin

All changes confined to OMT enforcement surface (two guarded plugins, test fixtures, runners, docs). No `src/` production code touched.

## 2. Files Changed

### Guarded Plugins (ONE batched write each, e2e receipt refreshed between)

| File | Changes | Tier |
|------|---------|------|
| `.opencode/plugin/omt_enforcer.ts` | L1034, L1063: `output?.args?…` → `input?.args?.filePath ?? input?.args?.path ?? input?.args?.file` (F14 + F14b); L1026 reword `TA: thoughts` → `thought-tags`; L1032 fix `gotcha: gotcha:` → `gotcha:`; after-hook: `navRemindedSessions` Set + prepend nav reminder on first tool result per session (F14c) | 1, 4.1 |
| `.opencode/plugin/omt_think.ts` | L19 header comment updated (session.start retained, inert); L88 reword `TA: tags` → `inline thought-tags`; new `tool.execute.after` hook: `digestSessions` Set + append `thinkDigest()` to `output.output` on first tool result per session (F14c) | 1c, 4.1 |

### Documentation (same guarded write batch)

| File | Changes |
|------|---------|
| `AGENTS.md` | L68: "every session.start greps" → "first tool result of each session carries the TA: digest (session.start hook retained for future SDK support)" |
| `.meta/META_HARNESS.md` | L115 THINK_DIGEST: session.start → first-tool-result wording; L202 XREF_NAV_ENF: session.start reminder → first-tool-result wording |

### Test Fixtures & Runners (tests/ — unguarded)

| File | Changes | Tier |
|------|---------|------|
| `tests/features/feature_022.meta_harness_think_anywhere_v2/test_omt_think_v2_tier_bd.py` | `_read_call` fixture: `args` moved from `output` → `input` (REAL SDK shape, F14); `test_thought_free_and_edit_untouched` updated for nav reminder on first call | 1.2 |
| `tests/features/feature_022.meta_harness_think_anywhere_v2/test_omt_think_v2_tier_c.py` | `_index_records(root, path, kind)` + `_ledger_size(root)`, `_ledger_records_after(root, offset)` accept `root` param for F17 cwd isolation; `test_digest_reports_stale` uses tmp_path for file + `_session_start(tmp_path)`; `TestC2ConsultRecord` uses tmp_path ledger | 4.2 |
| `tests/features/feature_022.meta_harness_think_anywhere_v2/test_omt_think_v2_tier_remainder.py` | `_seed_index(root, records)`, `_index_records(root, path_filter, kind)` accept `root`; all `TestE1Reindex` tests use `f.name` (cwd-relative) instead of `_rel(f)` | 4.2 |
| `tests/features/feature_022.meta_harness_think_anywhere_v2/test_omt_think_v2.py` | `_run_tool` already had `cwd` param (no change needed) | 4.2 |
| `tests/scripts/omt/test_opencode_sdk_contract.py` | **NEW** — harness-level contract pin (shape, version, fixture) | 2 |
| `tests/features/feature_023.meta_harness_improvement/test_omt_harness_improvement.py` | **NEW** — 22 tests covering behaviors 2–5, 8–13 | 1, 3, 4 |
| `tests/features/feature_023.meta_harness_improvement/_plugin_surface_runner.mjs` | **NEW** — combined runner for `hooks` + `exports` modes (Tier 3) | 3 |

## 3. Key Implementation Details

### F14 Contract Pin (Tier 1.1)
- **Root cause:** `omt_enforcer.ts` read `output.args` in `tool.execute.after` — key NEVER existed in any SDK version (1.1.12…1.17.11)
- **Fix:** Two line changes reading `input.args` instead (L1034 read-injection, L1063 edit path)
- **F14b behavior change:** src `.py` edit introducing NEW mvc_check hard error now throws OmtBlock post-write (feature_006 intent, live for first time)

### F14c Live Path Migration (Tier 1c)
- **Binary audit:** opencode 1.18.3 dispatches 16 hook names; `session.start` NOT among them
- **New live path:** First `tool.execute.after` per session (both plugins)
- **Retention:** `session.start` registrations kept (inert today; future SDKs may dispatch)
- **Ordering:** nav reminder prepended before think digest when both fire on same call

### Tier 3 Named-Export Guard Extension
- **Sanctioned enforcer exports (exact set):** `{isDocPath, navGateDecision, thinkGateDecision, hasConsultedThoughts, fileThoughtsIn, OmtEnforcer}`
- **Load-safety:** Every named FUNCTION export (except OmtEnforcer factory) invoked with `{client:null,$:noop,directory:""}`, `undefined`, `{}` — no-throw required
- **Hook wiring:** Enforcer ⊇ `{tool.execute.before, tool.execute.after}`; Think ⊇ `{tool.execute.after, session.start}`; all registered keys ∈ `{before, after, tool, session.start, event}`

### Tier 4 F17 Cwd Isolation
- **Root cause:** `REPO_ROOT = process.cwd()` in omt_think.ts; feature_022 tests used REPO_ROOT cwd → polluted repo index/ledger
- **Fix:** All 4 feature_022 test files' `_run_tool` helpers accept `cwd` param; call sites pass `tmp_path`; runner uses `process.cwd()` naturally
- **Verification:** `test_tool_call_with_tmp_cwd_leaves_repo_index_untouched` asserts tmp index created AND repo index byte-unchanged

## 4. Test Results

| Test Suite | Tests | Status |
|------------|-------|--------|
| `test_omt_harness_improvement.py` | 22 | ✅ All pass |
| `test_opencode_sdk_contract.py` | 5 | ✅ All pass |
| `feature_022 tier_bd` | 19 | ✅ All pass |
| `feature_022 tier_c` | 22 | ✅ All pass |
| `feature_022 tier_remainder` | 16 | ✅ All pass |
| `feature_022 tier_a` (test_omt_think_v2.py) | 15 | ✅ All pass |
| **Total feature_022 + 023** | **99** | ✅ All pass |
| E2E harness tests | 13 | ✅ All pass |

Pre-existing failures (unchanged, documented in WORK.md):
- 3 × feature_018 react_screen Textual/mock failures
- 2 × tdd_check 8h-window ledger tests (pass only when no TDD session active)

## 5. Guarded-File Discipline

Each plugin edited in **exactly ONE batched write** with e2e receipt refresh between:
1. `omt_enforcer.ts` → `uv run pytest tests/scripts/omt/test_omt_harness_e2e.py -q` (receipt)
2. `omt_think.ts` → `uv run pytest tests/scripts/omt/test_omt_harness_e2e.py -q` (receipt)
3. `AGENTS.md` + `.meta/META_HARNESS.md` → `uv run pytest tests/scripts/omt/test_omt_harness_e2e.py -q` (receipt)

All receipts ≥ mtime enforced by omt_enforcer.

## 6. Traceability

| Behavior | Tier | Primary Files |
|----------|------|---------------|
| 1 | T1.1/1.2 | omt_enforcer.ts, tier_bd/tier_c fixtures |
| 2 | T1.1 | omt_enforcer.ts, _think_gate_runner.mjs (after-hook-edit mode) |
| 3, 4, 5 | T1c | omt_think.ts, omt_enforcer.ts, AGENTS.md, META_HARNESS.md |
| 6, 7 | T2 | test_opencode_sdk_contract.py (new) |
| 8, 9, 10, 13 | T3 | test_omt_harness_improvement.py + _plugin_surface_runner.mjs (new) |
| 11 | T4.1 | Two plugin writes (step 5/6) |
| 12 | T4.2 | 4 feature_022 test files |

## 7. Completion

All 13 TDD behaviors implemented and verified. Programming phase complete. Ready for Testing phase.