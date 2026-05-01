# RAG Improvement Plan - Quick Reference

## Critical Issues (Current State)

1. **Duplicate Entries** (~30-40% duplication rate)
   - Same content, different IDs
   - Wasted storage, confusing results

2. **Confidence Inflation** (99.4% >= 0.6)
   - Average: 0.89 (should be ~0.75)
   - Scores meaningless for prioritization

3. **Poor Query Relevance**
   - "current work" → general info
   - Missing intent understanding

4. **No Quality Gates**
   - No pre-population validation
   - No duplicate detection

## Improvement Plan Summary

### Phase 1: Critical Fixes (3-5 hours) ✅ PRIORITY
- [ ] Deduplication engine
- [ ] Confidence recalibration  
- [ ] Emergency cleanup script

**Expected Result**: Duplicate rate < 2%, natural confidence distribution

### Phase 2: Relevance (5-8 hours)
- [ ] Query intent classification
- [ ] Enhanced semantic boosting
- [ ] Multi-hop enhancement

**Expected Result**: Relevance score > 0.8, intent accuracy > 80%

### Phase 3: Quality Assurance (8-12 hours)
- [ ] Pre-population validation
- [ ] Quality report generation
- [ ] Continuous monitoring

**Expected Result**: 100% validated entries, zero invalid entries

### Phase 4: Advanced (Optional, 10-15 hours)
- [ ] Embedding-based search
- [ ] Cross-encoder re-ranking
- [ ] Conversational memory

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Duplicate Rate | ~35% | < 2% |
| Avg Confidence | 0.89 | 0.75 |
| High Conf (>=0.9) | 49% | 10-20% |
| Low Conf (<0.6) | 0.1% | 10-20% |
| Query Relevance | Poor | > 0.8 |

## Files to Create/Modify

### New Files
- `.meta/tools/meta-harness-knowledge-base/src/dedup.py`
- `.meta/tools/meta-harness-knowledge-base/src/query_intent.py`
- `.meta/tools/meta-harness-knowledge-base/src/validator.py`
- `.meta/tools/meta-harness-knowledge-base/src/monitor.py`
- `.meta/tools/meta-harness-knowledge-base/quality_report.py`
- `.meta/tools/meta-harness-knowledge-base/cleanup_duplicates.py`

### Modified Files
- `.meta/tools/meta-harness-knowledge-base/src/rag_tool.py`
- `.meta/tools/meta-harness-knowledge-base/knowledge_base.py`
- `.meta/tools/meta-harness-knowledge-base/src/advanced_rag.py`
- `.meta/tools/meta-harness-knowledge-base/src/populate_kb.py`

## Quick Test Commands

```bash
# Test current state
python kb stats
python kb search "current work"
python kb ask "what is the current work"

# After Phase 1, expect:
# - Fewer total entries (duplicates removed)
# - Better confidence distribution
# - More relevant results

# Test commands
python kb search "Meta Project Harness" -k 5  # Check duplicates
python kb stats  # Check confidence distribution
python kb ask "how do I write tests"  # Check relevance
```

## Risk Mitigation

**Before starting**:
```bash
# Backup KB database
cp .meta/data/kb-meta/knowledge-meta.db \
   .meta/data/kb-meta/knowledge-meta.db.backup.$(date +%Y%m%d)
```

**Rollback if needed**:
```bash
cp .meta/data/kb-meta/knowledge-meta.db.backup.YYYYMMDD \
   .meta/data/kb-meta/knowledge-meta.db
```

## Next Steps

1. **Review** this plan and get approval
2. **Backup** current KB database
3. **Start Phase 1** (Critical Fixes)
4. **Test** after each phase
5. **Document** learnings

## Full Plan Location

See complete plan: `.meta/sandbox/rag-improvement-plan/IMPROVEMENT_PLAN.md`

---

**Entry ID**: PAT-70AD  
**Created**: 2026-05-01  
**Status**: Proposal  
**Priority**: High
