# KB-First Quick Reference

## Quick Start

**User asks**: "What is MainController?"

**Agent should** (using KB-First):
```bash
python3 .meta/tools/meta-harness-knowledge-base/kb ask "What is MainController?" --top-k 3
```

**Result**: Synthesized answer from KB with citations

---

## Commands

### Populate KB (if empty)
```bash
python3 .meta/tools/populate_kb.py
```

### Query KB (Search)
```bash
python3 .meta/tools/meta-harness-knowledge-base/kb search "<query>" --top-k 3
```

### Query KB (Ask - Advanced RAG)
```bash
python3 .meta/tools/meta-harness-knowledge-base/kb ask "<question>" --top-k 3
```

### Run Tests
```bash
python3 .meta/tests_sandbox/test_kb_first_query.py
python3 .meta/experiments/kb-first-integration/test_opencode_integration.py
```

---

## Rules

**DO**:
- ✅ Use `python3` (NOT `python`)
- ✅ Query KB FIRST before grep/glob/read
- ✅ Use Advanced RAG (`kb ask`)
- ✅ Cite KB entries
- ✅ Show confidence scores

**DON'T**:
- ❌ Use `python` command
- ❌ Search code before KB
- ❌ Ignore KB results
- ❌ Skip KB citation

---

## Example Workflow

```
User: What is MainController?

Agent (thinking):
1. Project-specific question → KB-First skill
2. Run: python3 .meta/tools/meta-harness-knowledge-base/kb ask "What is MainController?" --top-k 3

KB Response:
✓ Answer synthesized from 3 sources
Confidence: 0.95
## Summary
MainController is the central controller class...

Agent (answer):
Based on the Knowledge Base (Advanced RAG):

**MainController** is the central controller class in AgentX that:
- Manages command registration and execution
- Partners with MainView for UI
- Uses SessionManager for session state

*Source: Knowledge Base (3 entries, confidence: 0.95)*
```

---

## Test Results

✅ 4/4 tests passing
- KB has MainController info
- Population script reads all files
- RAG CLI works (python3)
- Advanced RAG ask works

---

## Files

- **Skill**: `.agents/skills/kb-first-query/SKILL.md`
- **Tests**: `.meta/tests_sandbox/test_kb_first_query.py`
- **Integration**: `.meta/experiments/kb-first-integration/test_opencode_integration.py`
- **Report**: `.meta/experiments/kb-first-integration/EXPERIMENT_REPORT.md`

---

**Version**: 1.0.0 | **Status**: ✅ Complete
