# KB-First Query Skill

**Purpose**: Automatically query the Knowledge Base using Advanced RAG before answering any project-specific question

**Target**: opencode agents

**Rule**: This skill MUST be used when user asks about project components, classes, features, or architecture

---

## Trigger Conditions

Use this skill when user asks questions like:
- "What is X?" (where X is a class, component, or feature)
- "How does X work?"
- "Explain X"
- "Tell me about X"
- Any question about project structure, architecture, or components

**Examples**:
- "What is MainController?"
- "How does SessionManager work?"
- "Explain the command pattern"
- "Tell me about the TDD workflow"

---

## Action Flow

### Step 1: Query KB using Advanced RAG
Run the KB ask command with python3:

```bash
python3 .meta/tools/meta-harness-knowledge-base/kb ask "<user_question>" --top-k 5
```

### Step 2: Check KB Response
- If KB returns synthesized answer (**✓ Answer synthesized from X sources**):
  - Use that answer as primary source
  - Cite the KB entries
  - Do NOT search code

- If KB returns no relevant results:
  - Inform user KB has no information
  - Proceed with normal code search (grep, glob, read)

### Step 3: Answer from KB
When KB has answer:
1. Present the KB-synthesized summary
2. List the sources (PAT-XXX IDs)
3. Show confidence scores
4. Do not search code unless user explicitly asks

---

## Implementation

### Tool Usage

**ALWAYS use python3** (not python):

```bash
# Query KB with Advanced RAG (RECOMMENDED)
python3 .meta/tools/meta-harness-knowledge-base/kb ask "<query>" --top-k 5

# Search KB entries
python3 .meta/tools/meta-harness-knowledge-base/kb search "<query>" --top-k 5
```

### Example Interaction

**User**: What is MainController?

**Agent** (thinking):
1. This is a project-specific question
2. MUST query KB first using Advanced RAG (AGENTS.md rule)
3. Running: `python3 .meta/tools/meta-harness-knowledge-base/kb ask "What is MainController?" --top-k 5`

**KB Response**:
```
✓ Answer synthesized from 3 sources
## Summary
MainController is the central controller class in AgentX...

## Sources:
1. [PAT-XXX] Class: MainController
2. [PAT-YYY] Source: Python: main_controller.py
3. [PAT-ZZZ] Session Management System
```

**Agent** (answer):
Based on the Knowledge Base (Advanced RAG):

**MainController** is the central controller class in AgentX that:
- Manages command registration and execution
- Partners with MainView for UI
- Uses SessionManager for session state
- Handles the main application loop

Methods: `__init__`, `showChat`, `run`, `get_commands`, `find_command`, `add_command`, `commands_history`, `close`, `error`, `run_command`

*Source: Knowledge Base - Advanced RAG (3 entries, confidence: 0.95)*

---

## Rules

**DO**:
- Query KB FIRST before any code search
- Use `python3` (NOT `python`) for KB commands
- Use Advanced RAG (`kb ask` / `kb search`)
- Cite KB entries in your response
- Show confidence scores
- Use KB as primary source
- Keep KB query results in context

**DON'T**:
- Use `python` command (use `python3` only)
- Use sqlite3 queries directly
- Search code (grep, glob) before querying KB
- Ignore KB results
- Modify KB entries without permission
- Assume KB is wrong without verification

---

## Testing

### Test Command
```bash
python3 .meta/tests_sandbox/test_kb_first_query.py
```

### Manual Tests

**Test 1: Direct KB Query with Advanced RAG**
```bash
python3 .meta/tools/meta-harness-knowledge-base/kb ask "What is MainController?" --top-k 3
```

**Test 2: KB Search with Advanced RAG**
```bash
python3 .meta/tools/meta-harness-knowledge-base/kb search "MainController" --top-k 3
```

**Test 3: Verify KB Population**
```bash
python3 .meta/tools/populate_kb.py
```

**Test 4: Test with opencode**
```bash
python3 -c "
import subprocess
result = subprocess.run([
    'python3', '.meta/tools/meta-harness-knowledge-base/kb', 'ask',
    'What is MainController?', '--top-k', '3'
], capture_output=True, text=True)
print(result.stdout)
"
```

---

## Advanced RAG Features

The KB tool uses Advanced RAG with:
- **Query variations**: Automatically generates related queries
- **Semantic search**: Finds conceptually similar entries
- **Synthesis**: Combines multiple sources into coherent answer
- **Confidence scoring**: Shows reliability of results
- **Source attribution**: Cites exact KB entries

### Performance
- KB query time: ~0.02-0.05s
- RAG synthesis: ~0.1-0.3s
- Total response: < 1s (vs 5-10s for code search)

---

## Error Handling

### KB Not Populated
If KB returns 0 results:
```
The Knowledge Base (Advanced RAG) has no information about "X".
Would you like me to:
1. Search the codebase directly?
2. Populate the KB from source code?

Run: python3 .meta/tools/populate_kb.py
```

### KB Tool Missing
If `kb` command not found:
```
Error: KB tool not available.
Location: .meta/tools/meta-harness-knowledge-base/kb

Please run: python3 .meta/tools/populate_kb.py
```

### Wrong Python Command
**NEVER use** `python` (may point to wrong version):
```bash
# WRONG - may fail or use wrong environment
python .meta/tools/meta-harness-knowledge-base/kb ask "query"

# CORRECT - always use python3
python3 .meta/tools/meta-harness-knowledge-base/kb ask "query"
```

---

## References

- AGENTS.md - KB-first mandate
- `.meta/knowledge_base/META.md` - KB documentation
- `.meta/tools/meta-harness-knowledge-base/README.md` - Advanced RAG tool docs
- `.meta/tools/meta-harness-knowledge-base/ADVANCED_FEATURES.md` - RAG features
- `.meta/tests_sandbox/test_kb_first_query.py` - Test suite

---

**Version**: 1.0.0  
**Created**: 2026-04-26  
**Updated**: 2026-04-26 (python3 + Advanced RAG)  
**Status**: Experimental
