# Experiment: KB-First Integration for Opencode

**Date**: 2026-04-26  
**Status**: Experimental  
**Objective**: Make opencode automatically query the Knowledge Base FIRST when users ask project-specific questions

---

## Problem Statement

Currently, when a user asks:
```
opencode run "What is MainController?"
```

Opencode does NOT automatically query the KB first, even though AGENTS.md mandates it.

**Expected behavior**:
1. User asks question
2. Opencode queries KB via `.meta/tools/meta-harness-knowledge-base/kb ask`
3. KB returns synthesized answer
4. Opencode presents answer with KB citation

**Actual behavior**:
1. User asks question
2. Opencode searches code directly (grep, glob)
3. KB is ignored
4. No KB citation in response

---

## Hypothesis

We can make opencode query KB first by:

1. **Creating an opencode skill** that intercepts questions and routes them to KB
2. **Adding a pre-prompt** that forces KB queries before any tool use
3. **Creating a wrapper script** that queries KB before passing to opencode

---

## Proposed Solutions

### Solution 1: Opencode Skill (RECOMMENDED)

Create a skill in `.agents/skills/kb-first-query/` that:
- Triggers on project-specific questions
- Runs `python3 kb ask <query>` automatically (Advanced RAG)
- Injects KB results into context

**File**: `.agents/skills/kb-first-query/SKILL.md`
```markdown
# KB-First Query Skill

## Trigger
When user asks about project components, classes, or features

## Action
1. Run: `python3 .meta/tools/meta-harness-knowledge-base/kb ask "<user_query>" --top-k 5`
2. Inject KB response into context
3. Answer based on KB results

## Examples
User: "What is MainController?"
→ KB Query: "MainController"
→ KB Response (Advanced RAG): "MainController is the central controller class..."
→ Answer: "Based on the Knowledge Base (Advanced RAG), MainController is..."
```

### Solution 2: Pre-prompt Injection

Add to `AGENTS.md` or opencode config:
```
BEFORE using ANY tool (grep, glob, read), you MUST:
1. Run: .meta/tools/meta-harness-knowledge-base/kb ask "<user_query>"
2. If KB returns results, answer from KB
3. If KB returns nothing, proceed with tool search
```

### Solution 3: Wrapper Script

Create `opencode-kb` wrapper (uses python3):
```bash
#!/bin/bash
# Extract user query
query="$*"

# Query KB first using Advanced RAG (python3!)
kb_result=$(python3 .meta/tools/meta-harness-knowledge-base/kb ask "$query" --top-k 3)

# Check if KB has answer
if echo "$kb_result" | grep -q "Answer synthesized"; then
    echo "$kb_result"
    echo ""
    echo "---"
    echo "(Answer from Knowledge Base - Advanced RAG)"
else
    # KB has no answer, run normal opencode
    opencode run "$query"
fi
```

---

## Test Plan

### Test 1: Direct KB Query
```bash
.meta/tools/meta-harness-knowledge-base/kb ask "What is MainController?"
```
**Expected**: Returns synthesized answer about MainController

### Test 2: Opencode with KB-first
```bash
opencode run "What is MainController? Query KB first."
```
**Expected**: Opencode queries KB and cites it

### Test 3: Wrapper Script
```bash
./opencode-kb "What is MainController?"
```
**Expected**: Returns KB answer with citation

---

## Implementation Steps

1. ✅ **Create test suite** - `.meta/tests_sandbox/test_kb_first_query.py`
2. ⏳ **Create KB-first skill** - `.agents/skills/kb-first-query/`
3. ⏳ **Test with opencode** - Verify behavior change
4. ⏳ **Document usage** - Update AGENTS.md with examples
5. ⏳ **Validate** - Run test suite again

---

## Success Criteria

- [ ] User asks "What is MainController?"
- [ ] Opencode automatically queries KB (no manual intervention)
- [ ] Response includes KB citation
- [ ] Response matches KB content
- [ ] No direct code search if KB has answer

---

## Current Status

### ✅ Completed
- KB population script fixed (reads all .meta files + src/agentx/)
- 371 entries populated in KB
- RAG CLI tool working (`kb ask`, `kb search`)
- Test suite created and passing

### ⏳ In Progress
- Opencode integration (skill or pre-prompt)

### ⏸️ Pending
- User testing with real questions
- Performance optimization
- Documentation updates

---

## Next Steps

1. Create opencode skill for KB-first behavior
2. Test with actual opencode run commands
3. Refine based on results
4. Document in AGENTS.md

---

## References

- AGENTS.md - KB-first mandate
- `.meta/tools/meta-harness-knowledge-base/` - RAG implementation
- `.meta/tests_sandbox/test_kb_first_query.py` - Test suite
