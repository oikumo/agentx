# RAG Knowledge Base Improvement Plan

**Version**: 1.0.0  
**Status**: Proposal  
**Created**: 2026-05-01  
**Priority**: High  
**Estimated Effort**: 3-5 hours (Phase 1), 5-8 hours (Phase 2), 8-12 hours (Phase 3)

---

## Executive Summary

The Meta Harness Knowledge Base RAG system is functional but has several critical issues affecting its effectiveness:

1. **Duplicate entries** reducing result quality
2. **Poor query relevance** for specific questions
3. **Confidence score inflation** making scoring meaningless
4. **Lack of deduplication** during population
5. **Missing quality gates** for entry validation

This plan addresses these issues through a phased approach aligned with Meta Harness principles.

---

## Problem Analysis

### Current State (as of 2026-05-01)

```
Total entries: 1,662
- Patterns: 820 (avg confidence: 0.94)
- Findings: 842 (avg confidence: 0.85)
- Categories: 5 main categories
- Confidence distribution:
  * High (>=0.9): 821 (49.4%)
  * Medium (0.6-0.9): 1,125 (67.7%)
  * Low (<0.6): 2 (0.1%)
```

### Critical Issues Identified

#### 1. Duplicate Content Problem
**Symptom**: Multiple entries with identical content but different IDs  
**Example**: Query "current work" returns 3 identical entries (PAT-FBDF, PAT-9967, PAT-9A4E)  
**Root Cause**: No deduplication during population process  
**Impact**: 
- Wasted storage (estimated 30-40% duplication rate)
- Confusing search results
- Inflated entry counts
- Poor user experience

#### 2. Confidence Score Inflation
**Symptom**: 99.4% of entries have confidence >= 0.6, average 0.89  
**Expected Distribution**: Should follow more natural distribution  
**Root Cause**: Default confidence too high, no decay mechanism  
**Impact**:
- Confidence scores meaningless
- Cannot prioritize high-quality entries
- Evolution system ineffective

#### 3. Query Relevance Issues
**Symptom**: Query "current work" returns general Meta Harness info  
**Expected**: Specific workflow information  
**Root Cause**: 
- Over-reliance on keyword matching
- Insufficient semantic understanding
- No query intent classification

#### 4. Population Quality Control
**Symptom**: Duplicate and low-quality entries in KB  
**Root Cause**: 
- No pre-population validation
- No duplicate detection
- No quality scoring before insertion

---

## Improvement Phases

### Phase 1: Critical Fixes (3-5 hours)
**Priority**: CRITICAL  
**Goal**: Fix duplicate entries and confidence scoring

#### 1.1 Deduplication Engine
**Files to Create/Modify**:
- `.meta/tools/meta-harness-knowledge-base/src/dedup.py` (NEW)
- `.meta/tools/meta-harness-knowledge-base/knowledge_base.py` (MODIFY)

**Implementation**:
```python
# Deduplication algorithm
def detect_duplicates(entries, similarity_threshold=0.85):
    """
    Detect duplicate entries using:
    1. Exact match on (type, title, finding, solution)
    2. Semantic similarity on content
    3. Fuzzy matching on title
    """
    # Implementation plan:
    # - Hash-based exact match detection
    # - Levenshtein distance for fuzzy matching
    # - Group duplicates, keep highest confidence
    pass
```

**Quality Gates**:
- [ ] No duplicate entries after population
- [ ] Deduplication runs before each population cycle
- [ ] Duplicate report generated

#### 1.2 Confidence Score Recalibration
**Files to Modify**:
- `.meta/tools/meta-harness-knowledge-base/src/rag_tool.py`
- `.meta/tools/meta-harness-knowledge-base/src/populate_kb.py`

**Changes**:
```python
# New confidence assignment rules
CONFIDENCE_DEFAULTS = {
    'pattern': 0.75,      # Was 0.90+
    'finding': 0.70,      # Was 0.85+
    'decision': 0.65,     # Was 0.80+
    'correction': 0.60    # Was 0.50+
}

# Add confidence decay
def apply_confidence_decay(entry, days_threshold=90):
    """Decay confidence for unused entries"""
    pass
```

**Quality Gates**:
- [ ] Confidence distribution more natural (bell curve)
- [ ] High confidence entries (<10% of total)
- [ ] Low confidence entries (10-20% of total)

#### 1.3 Emergency Cleanup Script
**Files to Create**:
- `.meta/tools/meta-harness-knowledge-base/cleanup_duplicates.py` (NEW)

**Purpose**: One-time cleanup of existing duplicates

---

### Phase 2: Relevance Improvements (5-8 hours)
**Priority**: HIGH  
**Goal**: Improve search and query relevance

#### 2.1 Query Intent Classification
**Files to Create**:
- `.meta/tools/meta-harness-knowledge-base/src/query_intent.py` (NEW)

**Implementation**:
```python
class QueryIntentClassifier:
    """
    Classify query intent to improve relevance:
    - WORKFLOW: "how do I...", "workflow for..."
    - DEFINITION: "what is...", "define..."
    - LOCATION: "where is...", "which file..."
    - COMPARISON: "difference between...", "vs..."
    - TUTORIAL: "step by step...", "guide for..."
    """
    
    INTENT_PATTERNS = {
        'WORKFLOW': [r'how do i', r'workflow', r'steps?'],
        'DEFINITION': [r'what is', r'define', r'meaning'],
        'LOCATION': [r'where', r'which file', r'location'],
        # ...
    }
```

**Quality Gates**:
- [ ] Query intent correctly identified >80% accuracy
- [ ] Intent used to boost relevant results

#### 2.2 Enhanced Semantic Boosting
**Files to Modify**:
- `.meta/tools/meta-harness-knowledge-base/src/rag_tool.py`
- `.meta/tools/meta-harness-knowledge-base/src/advanced_rag.py`

**Changes**:
```python
# Current scoring (line 217-228 in rag_tool.py):
# 0.30 * BM25 + 0.25 * Keyword + 0.20 * Semantic + 0.15 * Confidence + 0.10 * Recency

# Proposed enhanced scoring:
def calculate_enhanced_score(entry, query, intent):
    scores = {
        'bm25': 0.25,           # Reduced from 0.30
        'keyword': 0.20,        # Reduced from 0.25
        'semantic': 0.20,       # Same
        'intent_match': 0.15,   # NEW: Intent alignment
        'confidence': 0.10,     # Reduced from 0.15
        'recency': 0.05,        # Reduced from 0.10
        'user_feedback': 0.05   # NEW: User interaction history
    }
    return weighted_sum(scores)
```

**Quality Gates**:
- [ ] Relevant results rank higher for test queries
- [ ] Intent-based boosting working

#### 2.3 Multi-Hop Enhancement
**Files to Modify**:
- `.meta/tools/meta-harness-knowledge-base/src/advanced_rag.py`

**Current Issue**: Multi-hop retrieval exists but not optimized  
**Improvement**:
```python
def multi_hop_retrieval_enhanced(query, max_hops=2):
    """
    Enhanced multi-hop with:
    1. Entity extraction from query
    2. Concept graph traversal
    3. Cross-reference validation
    4. Result merging with diversity
    """
    pass
```

---

### Phase 3: Quality Assurance (8-12 hours)
**Priority**: MEDIUM  
**Goal**: Implement quality gates and monitoring

#### 3.1 Pre-Population Validation
**Files to Create**:
- `.meta/tools/meta-harness-knowledge-base/src/validator.py` (NEW)

**Implementation**:
```python
class KBEntryValidator:
    """
    Validate entries before insertion:
    - Required fields present
    - Confidence in valid range (0.0-1.0)
    - No duplicates (fuzzy match)
    - Content quality (min length, no empty fields)
    - Category validation
    """
    
    def validate_entry(self, entry):
        checks = [
            self._check_required_fields,
            self._check_confidence_range,
            self._check_duplicates,
            self._check_content_quality,
            self._check_category
        ]
        return all(check(entry) for check in checks)
```

**Quality Gates**:
- [ ] All entries validated before insertion
- [ ] Validation errors logged
- [ ] Invalid entries rejected with clear error

#### 3.2 Post-Population Quality Report
**Files to Create**:
- `.meta/tools/meta-harness-knowledge-base/quality_report.py` (NEW)

**Features**:
```python
def generate_quality_report():
    """
    Generate comprehensive quality report:
    - Duplicate rate
    - Confidence distribution
    - Category balance
    - Empty field analysis
    - Orphan entries (no references)
    - Stale entries (not used in X days)
    """
    pass
```

**Output Example**:
```
KB Quality Report - 2026-05-01
================================
Total Entries: 1,662
Duplicate Rate: 12.3% ⚠️
Confidence Distribution:
  - High (>=0.9): 49.4% ⚠️ (too many)
  - Medium (0.6-0.9): 50.5% ✓
  - Low (<0.6): 0.1% ⚠️ (too few)
Category Balance:
  - documentation: 1,278 (76.9%) ⚠️
  - workflow: 289 (17.4%) ✓
  - code: 1 (0.1%) ⚠️
  - test: 4 (0.2%) ⚠️
  - directives: 90 (5.4%) ✓
Recommendations:
  1. Run deduplication
  2. Recalibrate confidence scores
  3. Add more code/test examples
```

#### 3.3 Continuous Monitoring
**Files to Create**:
- `.meta/tools/meta-harness-knowledge-base/src/monitor.py` (NEW)

**Features**:
```python
class KBMonitor:
    """
    Continuous monitoring:
    - Track query patterns
    - Monitor result quality (user feedback)
    - Detect performance degradation
    - Alert on quality issues
    - Automatic evolution triggers
    """
    
    def track_query(self, query, results, user_selected=None):
        """Track query and result selection"""
        pass
    
    def detect_anomalies(self):
        """Detect quality anomalies"""
        pass
```

---

### Phase 4: Advanced Features (Optional, 10-15 hours)
**Priority**: LOW  
**Goal**: Add advanced RAG features

#### 4.1 Embedding-Based Search
**Files to Create**:
- `.meta/tools/meta-harness-knowledge-base/src/embeddings.py` (NEW)

**Implementation**: Use sentence-transformers for semantic search

#### 4.2 Cross-Encoder Re-ranking
**Files to Create**:
- `.meta/tools/meta-harness-knowledge-base/src/reranker.py` (NEW)

**Implementation**: Use cross-encoder for final result re-ranking

#### 4.3 Conversational Memory
**Files to Create**:
- `.meta/tools/meta-harness-knowledge-base/src/memory.py` (NEW)

**Implementation**: Track conversation context for better multi-turn answers

---

## Implementation Timeline

### Week 1: Critical Fixes
- [ ] Day 1-2: Deduplication engine (1.1)
- [ ] Day 3: Confidence recalibration (1.2)
- [ ] Day 4: Emergency cleanup script (1.3)
- [ ] Day 5: Testing and validation

### Week 2: Relevance Improvements
- [ ] Day 1-2: Query intent classification (2.1)
- [ ] Day 3-4: Enhanced semantic boosting (2.2)
- [ ] Day 5: Multi-hop enhancement (2.3)

### Week 3: Quality Assurance
- [ ] Day 1-2: Pre-population validation (3.1)
- [ ] Day 3: Quality report generation (3.2)
- [ ] Day 4: Continuous monitoring (3.3)
- [ ] Day 5: Documentation and testing

### Week 4+: Advanced Features (Optional)
- [ ] Embedding-based search (4.1)
- [ ] Cross-encoder re-ranking (4.2)
- [ ] Conversational memory (4.3)

---

## Testing Strategy

### Test Cases for Deduplication
```python
def test_deduplication():
    # Test exact duplicate detection
    # Test fuzzy duplicate detection
    # Test duplicate merging
    # Test confidence-based selection
    pass

def test_confidence_recalibration():
    # Test default confidence assignment
    # Test confidence decay
    # Test confidence distribution
    pass

def test_query_relevance():
    # Test intent classification accuracy
    # Test result ranking improvement
    # Test multi-hop retrieval
    pass
```

### Validation Queries
```bash
# Test duplicate removal
python kb search "Meta Project Harness" -k 5
# Expected: No duplicate entries

# Test confidence distribution
python kb stats
# Expected: Natural distribution

# Test query relevance
python kb ask "what is the current work"
# Expected: Specific workflow information

# Test intent classification
python kb ask "how do I write tests"
# Expected: Workflow results boosted
```

---

## Success Metrics

### Phase 1 Metrics
- [ ] Duplicate rate < 2%
- [ ] Confidence distribution:
  - High (>=0.9): 10-20%
  - Medium (0.6-0.9): 60-70%
  - Low (<0.6): 10-20%

### Phase 2 Metrics
- [ ] Query relevance score > 0.8 (user-rated)
- [ ] Intent classification accuracy > 80%
- [ ] Result diversity score > 0.7

### Phase 3 Metrics
- [ ] 100% entries validated
- [ ] Quality report generated after each population
- [ ] Zero invalid entries in KB

### Overall Metrics
- [ ] User satisfaction > 85%
- [ ] Query response time < 100ms
- [ ] Answer synthesis accuracy > 90%

---

## Risk Assessment

### High Risk
1. **Data Loss**: Deduplication might remove valid entries
   - **Mitigation**: Backup before cleanup, reversible operations
   
2. **Breaking Changes**: API changes might break existing tools
   - **Mitigation**: Maintain backward compatibility, version API

### Medium Risk
1. **Performance Degradation**: Additional validation might slow population
   - **Mitigation**: Optimize algorithms, use caching
   
2. **False Positives**: Deduplication might flag valid similar entries
   - **Mitigation**: Manual review for borderline cases

### Low Risk
1. **User Resistance**: Users might resist confidence score changes
   - **Mitigation**: Clear communication, gradual rollout

---

## Rollback Plan

If issues arise:
1. **Immediate**: Restore from backup
2. **Short-term**: Disable problematic feature
3. **Long-term**: Fix and re-test

**Backup Strategy**:
```bash
# Before any changes
cp .meta/data/kb-meta/knowledge-meta.db \
   .meta/data/kb-meta/knowledge-meta.db.backup.$(date +%Y%m%d)
```

---

## Documentation Updates

### Files to Update
- [ ] `.meta/knowledge_base/META.md` - Add new workflows
- [ ] `.meta/tools/meta-harness-knowledge-base/README.md` - Update features
- [ ] `.meta/tools/meta-harness-knowledge-base/USAGE.md` - Add examples
- [ ] `ADVANCED_FEATURES.md` - Document new features
- [ ] `QUALITY_GUIDE.md` - New quality guidelines (CREATE)

### Training Materials
- [ ] Migration guide for users
- [ ] Best practices for entry creation
- [ ] Troubleshooting guide

---

## Resource Requirements

### Tools/Dependencies
- No new external dependencies (Phase 1-3)
- Optional: sentence-transformers (Phase 4)

### Time Investment
- Phase 1: 3-5 hours
- Phase 2: 5-8 hours
- Phase 3: 8-12 hours
- Phase 4: 10-15 hours (optional)

### Skills Required
- Python programming
- SQLite database knowledge
- RAG/Information retrieval concepts
- Meta Harness workflow understanding

---

## Approval Process

### Required Approvals
1. [ ] Technical review (architecture changes)
2. [ ] User impact assessment
3. [ ] Performance validation
4. [ ] Documentation review

### Stakeholders
- Project maintainers
- End users (AI agents)
- Documentation team

---

## Next Steps

1. **Immediate** (Today):
   - [ ] Review and approve this plan
   - [ ] Create backup of current KB
   - [ ] Set up development environment

2. **Short-term** (This week):
   - [ ] Implement Phase 1 (Critical Fixes)
   - [ ] Test deduplication
   - [ ] Validate confidence recalibration

3. **Medium-term** (Next 2 weeks):
   - [ ] Implement Phase 2 (Relevance)
   - [ ] Implement Phase 3 (Quality)
   - [ ] User testing

4. **Long-term** (Optional):
   - [ ] Implement Phase 4 (Advanced)
   - [ ] Continuous improvement

---

## Appendix A: Current Implementation Issues

### Issue 1: Duplicate Detection Code
**Location**: `.meta/tools/meta-harness-knowledge-base/src/rag_tool.py`  
**Problem**: No duplicate detection during population  
**Fix**: Add `detect_duplicates()` function

### Issue 2: Confidence Assignment
**Location**: `.meta/tools/meta-harness-knowledge-base/src/populate_kb.py`  
**Problem**: Default confidence too high (0.90+)  
**Fix**: Recalibrate to realistic values

### Issue 3: Query Processing
**Location**: `.meta/tools/meta-harness-knowledge-base/src/rag_tool.py` line 144-238  
**Problem**: Over-reliance on keyword matching  
**Fix**: Add intent classification and semantic boosting

---

## Appendix B: Reference Implementation

### Deduplication Algorithm
```python
def detect_duplicates(entries, threshold=0.85):
    """
    Detect duplicates using multiple strategies:
    1. Exact hash match
    2. Fuzzy string matching
    3. Semantic similarity
    """
    from difflib import SequenceMatcher
    
    duplicates = []
    seen = {}
    
    for entry in entries:
        # Create content signature
        signature = f"{entry['type']}|{entry['title']}|{entry['finding']}|{entry['solution']}"
        content_hash = hash(signature)
        
        # Check exact match
        if content_hash in seen:
            duplicates.append((entry, seen[content_hash]))
            continue
        
        # Check fuzzy match
        for prev_hash, prev_entry in seen.items():
            similarity = SequenceMatcher(None, signature, 
                f"{prev_entry['type']}|{prev_entry['title']}|{prev_entry['finding']}|{prev_entry['solution']}").ratio()
            if similarity >= threshold:
                duplicates.append((entry, prev_entry))
                break
        
        seen[content_hash] = entry
    
    return duplicates
```

---

**Document End**
