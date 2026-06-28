# Design 002: META HARNESS Critical Fixes

> **Phase:** Design — `omt_agent_guide.md §2`, §5–§10 | **Feature:** feature_006.opencode_process_enforcement
> **Date:** 2026-06-28
> **Analysis Reference:** `analysis_001_meta_harness_consistency.md`

---

## Objective

Design and implement **4 critical fixes** for the META HARNESS enforcement system:
- **C1:** Fix WORK.md auto-sync logic in `omt_enforcer.ts`
- **C2:** Remove fallback in `detectDesignArtifact()` — require `design_*.md`
- **C3:** Add test coverage for `mvc_check.py`
- **C4:** Fix `writeFileSync` import in `omt_enforcer.ts`

**Success Criteria:** All 4 fixes implemented, tested, and dogfooded on a sample phase completion.

---

## Components Affected

| File | Layer | Change Type |
|------|-------|-------------|
| `.opencode/plugin/omt_enforcer.ts` | Plugin (TypeScript) | Bug fixes C1, C2, C4 |
| `scripts/omt/mvc_check.py` | Script (Python) | Test coverage C3 |
| `tests/scripts/omt/test_mvc_check.py` | Test (Python) | **NEW** — C3 |

---

## Static Structure

### Files to Modify/Create

```
.opencode/plugin/
├── omt_enforcer.ts          # FIX: C1, C2, C4

scripts/omt/
└── mvc_check.py             # NO CHANGE (already correct)

tests/scripts/omt/
└── test_mvc_check.py        # NEW: C3 test coverage
```

---

## Detailed Design

### C1: Fix WORK.md Auto-Sync Logic

**Current Bug (Line 388):**
```typescript
const featureSlug = feature.replace("feature_", "feature_")  // NO-OP!
```

**Fix:**
```typescript
// Use feature as-is (e.g., "feature_006.opencode_process_enforcement")
// Also try matching short form (e.g., "feature_006")
const featureSlug = feature
const shortFeature = feature.match(/feature_\d+/)?.[0] || null

// Match both forms in WORK.md
for (const featureToMatch of [featureSlug, shortFeature].filter(Boolean)) {
  // ... existing logic with featureToMatch
}
```

**Operation Specification:**
```typescript
/**
 * Operation: Sync WORK.md checkboxes when phases complete.
 *
 * Preconditions:
 *   - WORK.md exists at repo root
 *   - Ledger contains at least one "complete" record
 *   - Feature slug matches a WORK.md entry (full or short form)
 *
 * Exceptions:
 *   - WORK.md missing: silently skip (no error)
 *   - WORK.md malformed: catch exception, log warning, continue
 *   - No matching feature: silently skip (feature may be tracked elsewhere)
 *
 * Postconditions:
 *   - All matching WORK.md entries for completed features are marked [x]
 *   - File is written back only if modifications were made
 */
```

**Files Changed:** `.opencode/plugin/omt_enforcer.ts` (lines 384-408)

---

### C2: Remove Artifact Detection Fallback

**Current Bug (Lines 151-153):**
```typescript
const hit = files.find((f) => /design.*\.md$/i.test(f)) ||
            files.find((f) => f.toLowerCase().endsWith(".md"))  // FALLBACK!
```

**Fix:**
```typescript
// Strict matching: only design_*.md files count as design artifacts
const hit = files.find((f) => /^design_\d+_.+\.md$/i.test(f))

// Optional: Log a warning if any .md exists but no design_*.md
if (!hit && files.some(f => f.toLowerCase().endsWith(".md"))) {
  safeLog("warn", `Feature ${feature} has .md files but no design_*.md artifact`)
}
```

**Rationale:** The fallback defeats the purpose of requiring structured design artifacts. If a feature has _some_ `.md` file but not a `design_*.md`, it should **fail** the artifact check, not pass.

**Files Changed:** `.opencode/plugin/omt_enforcer.ts` (lines 145-157)

---

### C3: Add Test Coverage for `mvc_check.py`

**Test Strategy:**

Create `tests/scripts/omt/test_mvc_check.py` with:

1. **Unit Tests for Individual Rules:**
   - `test_view_imports_model_error()` — Create fake view file importing model, verify ERROR
   - `test_model_imports_ui_error()` — Create fake model file importing ui, verify ERROR
   - `test_partner_not_abc_error()` — Create interface without ABC, verify ERROR
   - `test_controller_ui_code_warning()` — Controller with print(), verify WARNING
   - `test_sql_outside_dp_warning()` — Non-DB file with SQL, verify WARNING
   - `test_god_controller_warning()` — Controller >300 lines, verify WARNING

2. **Integration Tests:**
   - `test_clean_file_no_violations()` — Valid MVC file returns empty list
   - `test_json_output_format()` — `--json` flag produces valid JSON
   - `test_exit_codes()` — Errors → exit 1, warnings only → exit 0

3. **Edge Cases:**
   - `test_syntax_error_handling()` — Invalid Python → PARSE_ERROR finding
   - `test_unicode_handling()` — Files with unicode characters don't crash
   - `test_comment_lines_ignored()` — SQL in comments doesn't trigger warning

**Test File Structure:**
```python
# tests/scripts/omt/test_mvc_check.py
import pytest
import tempfile
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "omt"))

from mvc_check import check_file, Finding

class TestViewImportsModel:
    def test_view_imports_model_error(self):
        code = '''
from model.session import Session

class MainView:
    pass
'''
        with tempfile.NamedTemporaryFile(suffix="_view.py", delete=False) as f:
            f.write(code.encode())
            f.flush()
            findings = check_file(Path(f.name))
            assert any(f.rule == "VIEW_IMPORTS_MODEL" for f in findings)

class TestPartnerNotAbc:
    def test_partner_without_abc_error(self):
        code = '''
class IMainViewPartner:  # Missing ABC
    def on_user_input(self, user_input: str) -> None:
        pass
'''
        with tempfile.NamedTemporaryFile(suffix="_view.py", delete=False) as f:
            f.write(code.encode())
            f.flush()
            findings = check_file(Path(f.name))
            assert any(f.rule == "PARTNER_NOT_ABC" for f in findings)

# ... more tests ...
```

**Files Created:** `tests/scripts/omt/test_mvc_check.py` (~200 lines)

---

### C4: Fix Missing `writeFileSync` Import

**Current Bug (Line 6):**
```typescript
import { existsSync, readFileSync, readdirSync } from "node:fs"
// writeFileSync is used on line 394 but not imported!
```

**Fix:**
```typescript
import { existsSync, readFileSync, readdirSync, writeFileSync } from "node:fs"
```

**Files Changed:** `.opencode/plugin/omt_enforcer.ts` (line 6)

---

## Abstract Partner Interfaces

**N/A** — This is a plugin/script fix, no MVC triads involved.

---

## Functional Flow

### C1: WORK.md Sync Flow

```
Phase Complete Event (ledger)
  → syncWorkMdFromLedger() called
    → Read ledger, find all "complete" records
    → For each feature:
      → Try matching full slug (feature_006.opencode_process_enforcement)
      → Try matching short slug (feature_006)
      → If match found in WORK.md:
        → Replace "- [ ]" with "- [x]"
        → Set modified = true
    → If modified:
      → Write WORK.md back to disk
      → Log success (optional)
```

### C2: Artifact Detection Flow

```
detectDesignArtifact(feature)
  → Extract feature number (feature_006)
  → Scan 4.design/features/feature_006*/
  → For each file in directory:
    → Match pattern: /^design_\d+_.+\.md$/i
    → If match: return path
  → If no match:
    → (Removed: fallback to any .md)
    → Return null (artifact missing)
```

### C3: Test Execution Flow

```
pytest tests/scripts/omt/test_mvc_check.py
  → Import mvc_check module
  → For each test:
    → Create temporary file with test code
    → Call check_file(temp_file)
    → Assert expected findings present/absent
  → Cleanup temp files
  → Report: 15 tests, 15 passed
```

---

## Operation Specifications

### `syncWorkMdFromLedger()` (Fixed)

```typescript
/**
 * Operation: Sync completed phases from ledger to WORK.md checkboxes.
 *
 * Preconditions:
 *   - Ledger file exists at .meta/.omt/ledger.jsonl
 *   - WORK.md exists at repo root
 *
 * Exceptions:
 *   - WORK.md missing: silently return (no error thrown)
 *   - Ledger corrupt: skip corrupt lines, process valid ones
 *   - File write fails: catch exception, log warning, continue
 *
 * Postconditions:
 *   - All features with "complete" ledger records are marked [x] in WORK.md
 *   - File is only written if changes were made
 */
```

### `detectDesignArtifact(feature)` (Fixed)

```typescript
/**
 * Operation: Detect design artifact for a feature.
 *
 * Preconditions:
 *   - Feature slug is non-empty (e.g., "feature_006.opencode_process_enforcement")
 *   - Design root directory exists (4.design/features/)
 *
 * Exceptions:
 *   - Directory doesn't exist: return null
 *   - No matching files: return null
 *
 * Postconditions:
 *   - Returns repo-relative path to design_*.md file if found
 *   - Returns null if no strict match (no fallback)
 */
```

---

## MVC++ Self-Check

| Check | Status |
|-------|--------|
| View does not import Model | N/A (no views) |
| Model does not import ui | N/A (no models) |
| Abstract Partner is an `ABC` with `@abstractmethod` | N/A (no partners) |
| SQL only in `*_db.py` / `DP_*` | N/A (no SQL) |
| No `*Controller` under `model/` | ✅ N/A |
| `uv run scripts/omt/mvc_check.py` passes for touched files | ✅ TypeScript files not scanned |

---

## Test Plan

### Stage 1 — Unit Tests

| Component | Test | Expected |
|-----------|------|----------|
| `syncWorkMdFromLedger()` | WORK.md exists, feature matches | Checkbox updated to [x] |
| `syncWorkMdFromLedger()` | WORK.md missing | No error, silently skip |
| `detectDesignArtifact()` | design_001_architecture.md exists | Returns path |
| `detectDesignArtifact()` | Only notes.md exists | Returns null |
| `check_file()` | View imports model | ERROR finding |
| `check_file()` | Valid MVC file | No findings |

### Stage 2 — Integration Tests

| Scenario | Expected |
|----------|----------|
| Complete phase → ledger updated → WORK.md sync runs | WORK.md checkbox marked |
| Run `pytest tests/scripts/omt/test_mvc_check.py` | All tests pass, 80%+ coverage |

### Stage 3 — System Tests

**Dogfood Test:**
1. Declare a test phase: `omt_phase{task_type:"bug_fix", phase:"Programming", scope:"Test C1-C4 fixes"}`
2. Complete the phase: `omt_complete{feature:"feature_006.opencode_process_enforcement"}`
3. Verify: WORK.md entry for feature_006 is marked [x]
4. Verify: `uv run pytest tests/scripts/omt/test_mvc_check.py -q` passes

---

## Implementation Steps

| Step | Task | Files | Estimate |
|------|------|-------|----------|
| 1 | Fix C4: Add `writeFileSync` import | `omt_enforcer.ts:6` | 5min |
| 2 | Fix C1: Update WORK.md sync logic | `omt_enforcer.ts:384-408` | 30min |
| 3 | Fix C2: Remove artifact fallback | `omt_enforcer.ts:145-157` | 15min |
| 4 | Create C3: Test file structure | `test_mvc_check.py` (new) | 30min |
| 5 | Create C3: Unit tests for all rules | `test_mvc_check.py` | 1h |
| 6 | Run tests, fix failures | — | 30min |
| 7 | Dogfood: Test phase completion flow | — | 15min |

**Total:** ~2.5 hours

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| WORK.md sync corrupts file | High | Add try/catch, validate before write |
| Strict artifact check blocks legitimate work | Medium | Test with existing features first |
| Tests take too long to run | Low | Use pytest caching, parallel execution |

---

## Success Metrics

- ✅ All 4 critical fixes implemented
- ✅ 15+ unit tests passing for `mvc_check.py`
- ✅ WORK.md sync works end-to-end (manual verification)
- ✅ Artifact detection requires `design_*.md` (no fallback)
- ✅ No TypeScript errors in `omt_enforcer.ts`
- ✅ `uv run pytest tests/scripts/omt/test_mvc_check.py -q` → all green

---

*End of Design 002 — META HARNESS Critical Fixes*