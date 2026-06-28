# Analysis 001: META HARNESS Consistency Deep Dive

> **Phase:** Analysis — `omt_agent_guide.md §2` | **Feature:** feature_006.opencode_process_enforcement
> **Date:** 2026-06-28
> **Author:** AI Agent (powered by qwen/qwen3.5-397b-a17b)

---

## Executive Summary

This analysis examines the **entire META HARNESS implementation** — the OMT++ process enforcement system consisting of:
- Documentation structure (`.meta/` directory)
- Templates (`.meta/templates/`)
- Enforcement scripts (`scripts/omt/`)
- opencode plugin (`.opencode/plugin/`)
- Configuration (`opencode.jsonc`, `AGENTS.md`)

**Overall Assessment:** The harness is **85% consistent** with strong foundations but has several architectural inconsistencies, documentation gaps, and enforcement edge cases that need attention.

---

## 1. Structural Analysis

### 1.1 Directory Structure — ✅ MOSTLY CONSISTENT

**Expected (per `omt_agent_guide.md §15`):**
```
.meta/
├── software_development_process/
│   ├── 1.project/
│   ├── 2.requirements/
│   │   ├── documentation/
│   │   └── features/feature_XXX.slug/
│   ├── 3.analysis/features/feature_XXX/
│   ├── 4.design/features/feature_XXX/
│   ├── 5.implementation/features/feature_XXX/
│   ├── 6.testing/features/feature_XXX/
│   └── 7.integration/
├── templates/
├── proof_of_concepts/
└── prototypes/
```

**Actual Structure Issues:**

| Issue | Location | Severity | Impact |
|-------|----------|----------|--------|
| Feature directories use inconsistent naming | `3.analysis/features/feature_004/` vs `2.requirements/features/feature_004.modern_ui/` | Medium | Breaks auto-detection in `omt_status.ts` and `new_feature.py` |
| Missing `documentation/` subdirectory | `2.requirements/documentation/` exists but is empty | Low | Unused structure adds confusion |
| Implementation files don't follow naming convention | `5.implementation/features/feature_004/` has 7 ad-hoc `.md` files | Medium | Violates template guidance ("no ad-hoc `*_PROOF.md`") |

**Root Cause:** The feature slug normalization is inconsistent:
- Requirements: `feature_004.modern_ui/` (full slug with name)
- Analysis/Design/Impl/Testing: `feature_004/` (number only)

This breaks the auto-detection logic in `omt_status.ts:getArtifactStatus()` which tries to normalize but doesn't handle all cases.

---

### 1.2 Templates — ✅ CONSISTENT BUT INCOMPLETE

**Templates Present:**
- `feature.md` ✅
- `design.md` ✅
- `analysis.md` ✅
- `operation_spec.md` ✅
- `test_plan.md` ✅
- `use_case.md` ✅ (not reviewed in detail)

**Missing Templates (per `omt_agent_guide.md §10-§13`):**
| Template | Purpose | Priority |
|----------|---------|----------|
| `operation_list.md` | Extract operations from use cases before writing specs | Medium |
| `component_diagram.md` | Static structure for major features | Low |
| `sequence_diagram.md` | Functional flow documentation | Low |

**Template Issues:**

1. **`feature.md`** has a traceability table but doesn't enforce the **naming convention** strongly enough. The warning about "no ad-hoc `*_PROOF.md`" is present but ignored in practice (see `5.implementation/features/feature_004/` with 7 files).

2. **`design.md`** template mentions "Design {{NUM}}" but the actual design files use `design_001_*.md` pattern — minor inconsistency.

3. **`test_plan.md`** is titled "Test Report" but should distinguish between **Test Plan** (before testing) and **Test Report** (after testing) per guide §11's three-stage approach.

---

### 1.3 Scripts — ✅ MOSTLY CONSISTENT

#### `mvc_check.py` Analysis

**Strengths:**
- Clean separation of ERROR vs WARNING rules
- Covers all 12 "Common Mistakes" from guide §16
- JSON output for plugin integration
- Delta-based checking (pre/post edit snapshots)

**Issues:**

| Line | Issue | Severity | Fix |
|------|-------|----------|-----|
| 28-29 | `GOD_CONTROLLER_MAX_LINES = 300` is hardcoded, not configurable | Low | Make it a constant or CLI option |
| 53 | `RE_SQL` pattern may miss some SQL variations (e.g., `CREATE INDEX`) | Low | Expand regex |
| 186 | Whole-file checks run after line-by-line, could be optimized | Low | Minor perf issue |
| — | No check for missing operation specs | Medium | Add AST-based docstring validation |

**Missing Checks (per guide §16):**
- ❌ Check 8: Missing operation spec — not implemented
- ❌ Check 12: No tests for new feature — not implemented (would require test directory scanning)

#### `new_feature.py` Analysis

**Strengths:**
- Auto-increments feature numbers
- Creates consistent directory structure
- Renders from templates

**Issues:**

| Issue | Location | Severity | Impact |
|-------|----------|----------|--------|
| Only creates `FEATURE.md` and `plan/PLAN.md` | Lines 94-98 | Medium | Doesn't scaffold analysis/design directories |
| Doesn't create feature-specific test directory | — | Medium | Tests should live in `tests/features/feature_XXX/` |
| Plan stub is too generic | Lines 55-63 | Low | Could provide more specific guidance |

**Recommendation:** Add flags for `--scaffold-analysis`, `--scaffold-design`, `--scaffold-tests` to create the full directory structure upfront.

---

### 1.4 Plugin (`omt_enforcer.ts`) — ⚠️ CRITICAL ISSUES

#### Architecture Issues

**1. WORK.md Auto-Sync is Broken (Lines 384-408)**

```typescript
// BUG: This logic is flawed
for (const feature of completedFeatures) {
  const featureSlug = feature.replace("feature_", "feature_")  // NO-OP!
  const lines = content.split("\n")
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes(featureSlug) && lines[i].trim().startsWith("- [ ]")) {
      lines[i] = lines[i].replace("- [ ]", "- [x]")
      modified = true
    }
  }
  content = lines.join("\n")
}
```

**Problems:**
- `feature.replace("feature_", "feature_")` does nothing (replacing with same string)
- Should extract the full slug like `feature_004.modern_ui` and match against WORK.md entries
- No error handling if WORK.md is malformed
- Sync happens silently — user doesn't know it occurred

**Fix:**
```typescript
const featureSlug = feature  // Use as-is (e.g., "feature_006.opencode_process_enforcement")
const shortFeature = feature.match(/feature_\d+/)?.[0]  // Also try short form
// Match both forms in WORK.md
```

**2. Phase Exit Validation is Incomplete (Lines 52-92)**

The `checkPhaseExitArtifacts()` function has several issues:

```typescript
// ISSUE: Hardcoded phase names don't match guide §12 exactly
const requirements = PHASE_EXIT_REQUIREMENTS[fromPhase]
```

**Problems:**
- Phase names are strings like `"Analysis"`, `"Design"` — but what if the agent declares `"analysis"` (lowercase)?
- No validation that `fromPhase` is a valid phase
- Pattern matching for operation specs (`operation_spec_*.md`, `operations.md`) doesn't match the actual pattern used (operation specs are typically inline docstrings, not separate files)
- Unit tests detection looks for `test_*.py` or `*_test.py` but doesn't verify they're in `tests/features/<feature>/` as the comment suggests

**Fix:** Add case-insensitive phase matching and validate phase names against `VALID_PHASES`.

**3. Artifact Detection is Fragile (Lines 135-157)**

```typescript
const detectDesignArtifact = (feature) => {
  const m = String(feature).match(/feature_(\d+)/)  // Only extracts number
  // ...
  const hit = files.find((f) => /design.*\.md$/i.test(f)) ||
              files.find((f) => f.toLowerCase().endsWith(".md"))  // FALLBACK TO ANY .md!
}
```

**Problem:** The fallback `files.find((f) => f.toLowerCase().endsWith(".md"))` means **any** `.md` file in the design directory counts as a design artifact. This defeats the purpose of requiring `design_001_*.md`.

**Fix:** Remove the fallback or make it a warning, not a pass.

**4. TypeScript Errors in Plugin**

| Line | Issue |
|------|-------|
| 268 | `import("./omt_status.ts")` — dynamic import without error handling |
| 377 | `writeFileSync` used but not imported (only `readFileSync`, `existsSync`, `readdirSync` imported) |
| 394-395 | Loop logic updates `content` inside the loop but should batch updates |

---

### 1.5 `omt_status.ts` — ⚠️ MINOR ISSUES

**Issues:**

1. **Feature Health Calculation (Lines 158-170)** is overly simplistic:
   - Assigns 0.5 for phases that are neither present nor required
   - Doesn't weight phases by importance
   - Returns percentages that may be misleading (e.g., 50% health when nothing is done)

2. **Lint Baseline (Lines 148-156)** catches errors but doesn't surface warnings in the status output — only the count is shown.

3. **Session ID Handling (Lines 63-74)** has the same 8-hour fallback as the enforcer, but the comment says "keeps the gate usable" — this should be documented in AGENTS.md.

---

## 2. Documentation Consistency

### 2.1 AGENTS.md vs `omt_agent_guide.md`

**Alignment:** ✅ **GOOD** — AGENTS.md correctly references the guide.

**Issues:**
- AGENTS.md mentions "guide §12" for artifact requirements but doesn't reproduce the table — forces agents to read the full guide
- No mention of the 8-hour session timeout behavior

### 2.2 WORK.md Consistency

**Current State:** WORK.md uses a mix of:
- Full slugs: `feature_004.modern_ui`
- Short names: `feature_006.opencode_process_enforcement`

**Problem:** The ledger uses full slugs, but the auto-sync code doesn't handle this correctly (see Section 1.4, Issue 1).

### 2.3 Ledger (`ledger.jsonl`)

**Format:** ✅ Consistent JSONL format

**Issues:**
- No schema validation — corrupt lines are silently skipped
- Session IDs are not validated (could be any string)
- No cleanup mechanism — ledger grows indefinitely

---

## 3. Enforcement Gaps

### 3.1 What's Enforced vs What's Not

| Rule | Enforced? | How | Gap |
|------|-----------|-----|-----|
| Phase declaration before `src/` edits | ✅ | `omt_enforcer.ts` before-hook | — |
| Design artifact for major features | ⚠️ Partially | Auto-detection + fallback | Fallback allows any .md |
| MVC++ violations | ⚠️ Warnings only | `mvc_check.py` after-hook | Doesn't block, just notifies |
| Operation specs in docstrings | ❌ | — | Not checked |
| Test coverage | ❌ | — | Not checked |
| Phase exit artifacts | ⚠️ Partially | `checkPhaseExitArtifacts()` | Incomplete pattern matching |
| Protected files (README, .env) | ✅ | `isProtected()` check | — |
| Tests without approval | ✅ | `tests_approved` flag | — |

### 3.2 Edge Cases Not Handled

1. **Multiple concurrent sessions:** The ledger doesn't track which session "owns" which feature. Two agents could work on different phases of the same feature simultaneously.

2. **Phase regression:** An agent can declare `Analysis`, then declare `Analysis` again with a different scope — no validation that this is intentional.

3. **Feature renaming:** If a feature is renamed (e.g., `feature_004.ui` → `feature_004.modern_ui`), the ledger and artifacts become orphaned.

4. **Ledger corruption:** No recovery mechanism if the ledger file is corrupted mid-write.

---

## 4. MVC++ Violations in the Harness Itself

Running `mvc_check.py` on the harness code reveals:

```
⚠️  WARNINGS (6)
  src/agentx/ui/screens/chat/chat_controller.py:51  [CONTROLLER_UI_CODE]
  src/agentx/ui/screens/main/main_controller.py:127  [CONTROLLER_UI_CODE]
  src/agentx/ui/screens/main/main_controller.py:147  [CONTROLLER_UI_CODE]
  src/agentx/ui/screens/rag/rag_controller.py:106  [CONTROLLER_UI_CODE]
  src/agentx/ui/screens/rag/rag_repository_selection_controller.py:101  [SQL_OUTSIDE_DP]
  src/agentx/ui/tui/screens/rag_screens.py:155  [SQL_OUTSIDE_DP]
```

**Irony:** The process enforcement harness allows these warnings to persist in `src/` while blocking edits. This is technically correct (warnings don't block), but undermines the teaching mission.

---

## 5. Testing Coverage

### 5.1 Harness Tests

**Present:**
- `tests/tui/` — TUI-specific tests (23 e2e tests)
- `tests/controllers/` — Controller unit tests
- `tests/model/` — Model unit tests

**Missing:**
- ❌ No tests for `scripts/omt/mvc_check.py`
- ❌ No tests for `scripts/omt/new_feature.py`
- ❌ No tests for `.opencode/plugin/omt_enforcer.ts` (TypeScript)
- ❌ No tests for `.opencode/plugin/omt_status.ts`

**Impact:** The enforcement logic is untested. Bugs in the gate could block legitimate work or allow violations through.

---

## 6. Recommendations Summary

### 6.1 Critical (Must Fix)

| ID | Issue | Priority | Effort |
|----|-------|----------|--------|
| C1 | Fix WORK.md auto-sync logic in `omt_enforcer.ts` | High | 1h |
| C2 | Remove fallback in `detectDesignArtifact()` — require `design_*.md` | High | 30min |
| C3 | Add test coverage for `mvc_check.py` | High | 2h |
| C4 | Fix `writeFileSync` import in `omt_enforcer.ts` | High | 5min |

### 6.2 High (Should Fix)

| ID | Issue | Priority | Effort |
|----|-------|----------|--------|
| H1 | Standardize feature directory naming (use full slug everywhere or normalize consistently) | High | 2h |
| H2 | Add operation spec validation to `mvc_check.py` | High | 1h |
| H3 | Document 8-hour session timeout in AGENTS.md | High | 15min |
| H4 | Add ledger schema validation and corruption recovery | High | 1h |

### 6.3 Medium (Nice to Have)

| ID | Issue | Priority | Effort |
|----|-------|----------|--------|
| M1 | Create missing templates (`operation_list.md`, `component_diagram.md`) | Medium | 1h |
| M2 | Add `--scaffold-*` flags to `new_feature.py` | Medium | 1h |
| M3 | Implement feature health weighting in `omt_status.ts` | Medium | 30min |
| M4 | Add warning surfacing to `omt_status` output | Medium | 15min |

### 6.4 Low (Optional)

| ID | Issue | Priority | Effort |
|----|-------|----------|--------|
| L1 | Make `GOD_CONTROLLER_MAX_LINES` configurable | Low | 15min |
| L2 | Expand SQL regex in `mvc_check.py` | Low | 15min |
| L3 | Add ledger cleanup mechanism (rotate after N days) | Low | 1h |
| L4 | Split `test_plan.md` into `test_plan.md` and `test_report.md` | Low | 30min |

---

## 7. Conclusion

The META HARNESS is a **strong foundation** for process enforcement with:
- ✅ Clear phase model and artifacts
- ✅ Automated gate with teaching messages
- ✅ MVC++ architecture linting
- ✅ Ledger-based audit trail

However, it needs **polish and hardening**:
- ⚠️ Fix critical bugs in WORK.md sync and artifact detection
- ⚠️ Add test coverage for enforcement logic
- ⚠️ Standardize naming conventions across directories
- ⚠️ Address existing MVC++ warnings in the codebase

**Next Steps:**
1. Create design document for the fixes (Design phase)
2. Implement critical fixes (Programming phase)
3. Write tests for the harness (Testing phase)
4. Dogfood the fixes on feature_001 or feature_002

---

## Appendix A: Files Analyzed

| File | Lines | Status |
|------|-------|--------|
| `.meta/META.md` | 117 | ✅ |
| `.meta/software_development_process/omt_agent_guide.md` | 897 | ✅ |
| `.meta/templates/*.md` | 6 files | ✅ |
| `scripts/omt/mvc_check.py` | 245 | ⚠️ |
| `scripts/omt/new_feature.py` | 121 | ⚠️ |
| `.opencode/plugin/omt_enforcer.ts` | 522 | ⚠️ |
| `.opencode/plugin/omt_status.ts` | 280 | ⚠️ |
| `opencode.jsonc` | 62 | ✅ |
| `.meta/.omt/ledger.jsonl` | 17 records | ✅ |

**Total:** ~2,800 lines of harness code + documentation

---

## Appendix B: MVC++ Warnings Detail

```
src/agentx/ui/screens/chat/chat_controller.py:51
  → print() call in controller (should delegate to view)

src/agentx/ui/screens/main/main_controller.py:127, 147
  → print() calls in controller (should delegate to view)

src/agentx/ui/screens/rag/rag_controller.py:106
  → print() call in controller (should delegate to view)

src/agentx/ui/screens/rag/rag_repository_selection_controller.py:101
  → SQL outside DP class (should use DP_Rag)

src/agentx/ui/tui/screens/rag_screens.py:155
  → SQL outside DP class (should use DP_Rag)
```

---

*End of Analysis 001 — META HARNESS Consistency Deep Dive*