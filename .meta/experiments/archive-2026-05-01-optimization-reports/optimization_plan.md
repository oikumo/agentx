# Meta Harness Optimization Plan

**Date**: 2026-04-25  
**Status**: Ready for execution  
**Estimated Savings**: 15,000-20,000 tokens (30-40%)

---

## Current State

### Token Metrics
| Category | Files | Tokens | % | Status |
|----------|-------|--------|---|--------|
| **Total** | 69 | 50,689 | 100% | - |
| Other | 39 | 29,479 | 58.2% | ⚠️ High |
| Skills | 18 | 17,201 | 33.9% | ⚠️ Duplicated |
| META.md | 6 | 1,540 | 3.0% | ✅ Good |
| Core | 6 | 2,469 | 4.9% | ✅ Good |

### Core Files Status
| File | Tokens | Budget | Status |
|------|--------|--------|--------|
| AGENTS.md | 443 | 1,500 | ✅ |
| META_HARNESS.md | 602 | 2,000 | ✅ |
| .meta/project_development/META.md | 174 | 500 | ✅ |
| .meta/sandbox/META.md | 174 | 500 | ✅ |
| .meta/experiments/META.md | 149 | 500 | ✅ |
| .meta/tests_sandbox/META.md | 303 | 500 | ✅ |
| .meta/tools/META.md | 68 | 500 | ✅ |

**All core files within budget!**

---

## Issues Identified

### High Priority (Token Impact >1000)

1. **Duplicate Skill Files** (Severity: High)
   - `.agents/skills/meta-harness-optimize/SKILL.md` (1,944 tokens)
   - `.meta/experiments/token-optimization-skill/SKILL.md` (2,187 tokens)
   - **Action**: Consolidate to single source
   - **Savings**: ~2,000 tokens

2. **Old Experiment Documentation** (Severity: High)
   - `.meta/experiments/agent-x-session-state-proposal/` (4,240 tokens)
   - `.meta/experiments/token-optimization-skill/` (6,000+ tokens)
   - **Action**: Archive or remove completed experiments
   - **Savings**: ~4,000 tokens

3. **Reflection Logs** (Severity: Medium)
   - 5 reflection logs (8,253 tokens total)
   - **Action**: Archive to dated subdirectory
   - **Savings**: N/A (archival, not deletion)

4. **Meta Evolution Doc** (Severity: Medium)
   - `.meta/doc/meta project harness evolution.md` (2,362 tokens)
   - **Action**: Summarize key points, archive full version
   - **Savings**: ~1,500 tokens

### Medium Priority (Token Impact 500-1000)

5. **KB Population Docs** (Severity: Medium)
   - `.meta/doc/KB_POPULATION.md` (1,652 tokens)
   - `.meta/tools/KB_POPULATION_GUIDE.md` (240 tokens)
   - **Action**: Consolidate into single guide
   - **Savings**: ~800 tokens

6. **README.md** (Severity: Low)
   - Main README (1,952 tokens) - too verbose
   - **Action**: Compress with tables and decision trees
   - **Savings**: ~800 tokens

---

## Proposed Changes

### Change 1: Remove Duplicate Skill Files
- **What**: Delete `.meta/experiments/token-optimization-skill/` (completed)
- **Why**: Duplicates `.agents/skills/meta-harness-optimize/`
- **Impact**: -2,000 tokens
- **Effort**: Low

### Change 2: Archive Old Experiments
- **What**: Move `.meta/experiments/agent-x-session-state-proposal/` to archive
- **Why**: Experiment completed, no longer needed for daily work
- **Impact**: -4,240 tokens (active)
- **Effort**: Low

### Change 3: Consolidate KB Docs
- **What**: Merge KB_POPULATION.md and KB_POPULATION_GUIDE.md
- **Why**: Redundant information
- **Impact**: -800 tokens
- **Effort**: Medium

### Change 4: Compress README.md
- **What**: Apply token compression techniques
- **Why**: Improve efficiency, reduce token usage
- **Impact**: -800 tokens
- **Effort**: Medium

### Change 5: Archive Reflection Logs
- **What**: Move to `.meta/reflection/archive/` subdirectory
- **Why**: Keep active directory clean
- **Impact**: Organizational (no token savings)
- **Effort**: Low

---

## Implementation Plan

### Phase 1: Quick Wins (30 min)
1. ✅ Run token analysis (completed)
2. ⏳ Delete duplicate skill experiment
3. ⏳ Archive old experiment proposals
4. ⏳ Archive reflection logs

### Phase 2: Documentation Compression (45 min)
1. ⏳ Compress README.md
2. ⏳ Consolidate KB documentation
3. ⏳ Update META.md files if needed

### Phase 3: Validation (15 min)
1. ⏳ Re-run token analysis
2. ⏳ Verify all tests pass
3. ⏳ Check navigation still works
4. ⏳ Document changes

---

## Expected Results

### Token Reduction
| Category | Before | After | Savings |
|----------|--------|-------|---------|
| Total | 50,689 | ~35,000 | **-30.6%** |
| Experiments | 6,000+ | ~2,000 | **-67%** |
| Documentation | 4,014 | ~2,500 | **-38%** |
| Core files | 2,469 | 2,469 | 0% (already optimized) |

### Quality Metrics
- ✅ All core files within token budgets
- ✅ META.md files under 500 tokens each
- ✅ Clear directory structure maintained
- ✅ No loss of critical information
- ✅ Improved navigation clarity

---

## Rollback Plan

If issues arise:
1. All changes in `.meta/sandbox/` or `.meta/experiments/`
2. No production code modified
3. Git can restore any deleted files
4. Archives can be restored from `.meta/reflection/archive/`

---

**Next Step**: Execute Phase 1 (Quick Wins)
