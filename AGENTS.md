# AGENTS.md - Agent-X System Agent Rules

> **Your primary entry point. Read this FIRST before any task.**

---

## ⚠️ Core Directives (NON-NEGOTIABLE)

| # | Directive | What It Means |
|---|-----------|---------------|
| 1 | **NEVER commit or push** | Not even if user asks |
| 2 | **NEVER add dependencies** | Use what exists; explicit approval required for exceptions |
| 3 | **NEVER modify `.env`** | Or any file likely to contain secrets/credentials |
| 4 | **ALWAYS check `git log`** | Before making ANY changes |
| 5 | **NEVER modify `tests/`** | Use `.meta.tests_sandbox/` for new tests (requires approval) |
| 6 | **Use `uv` & `pyproject.toml`** | For all dependency management; avoid pin drift |

---

## What is the Meta Project Harness?

A structured development system optimized for AI-assisted development providing:
- **Safe spaces** to work without affecting production
- **Clear workflows** for consistent, high-quality output
- **Comprehensive documentation** at every level
- **Quality gates** to ensure correctness

### Directory Structure
```
agent-x/
├── META_HARNESS.md # Master documentation
├── AGENTS.md # This file
├── .meta.project_development/ # Rules, standards, workflows
├── .meta.sandbox/ # Your safe workspace
├── .meta.experiments/ # Experimental features
├── .meta.tests_sandbox/ # TDD workspace
├── .meta.development_tools/ # MCP tools, scripts
├── .meta.knowledge_base/ # RAG knowledge base
└── .meta.reflection/ # Test logs & capability assessment
```

**Rule:** All harness directories start with `.meta.` and contain a `META.md` file you must read first.

---

## Your Workflow

### 5-Step Workflow
```
1. UNDERSTAND: Read task + git log + relevant META.md
2. PLAN: Identify correct directory (see Decision Tree)
3. EXECUTE: Work in safe space, test frequently
4. VALIDATE: All tests pass, no production break
5. REPORT: Summarize + document + cleanup
```

---

## Decision Tree

```
Need to...
├─ Understand rules? → Read relevant META.md
├─ Modify code? → .meta.sandbox/
├─ Test new idea? → .meta.experiments/
├─ Write tests? → .meta.tests_sandbox/
├─ Use/create tools? → .meta.development_tools/
└─ Check workflows? → .meta.project_development/WORKFLOWS.md
```
Need to...
├─ Understand rules? → Read relevant META.md
├─ Modify code? → .meta.sandbox/
├─ Test new idea? → .meta.experiments/
├─ Write tests? → .meta.tests_sandbox/
├─ Use/create tools? → .meta.development_tools/
└─ Check workflows? → .meta.project_development/WORKFLOWS.md
```
Need to...
├─ Modify code?       → Work in .meta.sandbox/
├─ Write tests?       → Use .meta.tests_sandbox/ (TDD)
├─ Test new idea?     → Use .meta.experiments/
├─ Use/create tools?  → Check .meta.development_tools/
├─ Ask for guidance?  → Use kb_ask() from knowledge base
└─ Understand rules?  → Read META.md files first
```

---

## Quality Gates

Before reporting completion, verify:
- [ ] Read relevant META.md files
- [ ] Checked `git log`
- [ ] Worked in correct directory
- [ ] Followed TDD (if applicable)
- [ ] All tests pass
- [ ] Documented changes
- [ ] Stored new knowledge (if applicable)
- [ ] Cleaned workspace
- [ ] No secrets exposed
- [ ] No production code modified

---

## Tools Available

### Core Tools
`read`, `glob`, `bash`, `edit`, `write`, `task`

### Knowledge Base Tools

Tool: meta-harness-knowledge-base.

The User can query directly to this tool by asking to you: `?kb {User Query}`.

Call Python functions **ALLWAYS** using uv with python3.

```python
# Before task: Ask for guidance
result = rag_ask("Where should I implement this feature?")

# After task: Document discovery
result = rag_add_entry(
    entry_type="pattern",
    category="workflow",
    title="My Discovery",
    finding="What I found",
    solution="How to handle it"
)
```

---

## Common Scenarios

### Scenario 1: Add Feature
```bash
1. Read META_HARNESS.md
2. Ask KB: rag_ask("Where to implement this?")
3. Create experiment in .meta.experiments/
4. Write tests in .meta.tests_sandbox/
5. Implement in .meta.sandbox/
6. Document: rag_add_entry(...)
7. Report to user
```

### Scenario 2: Fix Bug
```bash
1. Check git log
2. Search KB: rag_search("similar bug")
3. Reproduce in .meta.sandbox/
4. Write failing test in .meta.tests_sandbox/
5. Fix in .meta.sandbox/
6. Document: rag_add_entry(type="finding", ...)
7. Report to user
```

### Scenario 3: Refactor Code
```bash
1. Copy to .meta.sandbox/
2. Write behavior tests
3. Refactor
4. Verify tests pass
5. Document: rag_add_entry(type="pattern", ...)
```

### Scenario 4: Maintenance
```bash
1. Run health check: rag_stats()
2. Run evolution: rag_evolve()
3. Review META.md files
4. Update as needed
5. Document changes
```

### Scenario 5: Capability Testing
```bash
1. Run reflection test: skill meta-harness-reflection
2. Review generated log: .meta.reflection/<timestamp>_log.md
3. Identify knowledge gaps
4. Update KB if needed
5. Re-test after improvements
```

---

## Available Skills

### optimize-meta-harness
Use to analyze and optimize the harness itself:
```bash
skill optimize-meta-harness
```
**Workflows:** Health Check → Documentation Analysis → Structure Optimization → Workflow Enhancement → Continuous Improvement

### meta-harness-reflection
Use to test agent's knowledge base usage and harness comprehension:
```bash
skill meta-harness-reflection
```
**Modes:** Interactive (manual answers) | Automated (KB search)
**Output:** Timestamped logs in `.meta.reflection/`
**Frequency:** Monthly or after KB updates

---

## Experiments

When the User ask for an experimient use the `.meta.experiments/` folder to create an isolated folder with the experiment.
If the experiment exists, use the existing folder in `.meta.experiments/{EXPERMIMENT-FOLDER}` and keep track of the findings and changes that you want to make

## Knowledge Base Integration

### Dual Knowledge Base System

Agent-X uses **two separate knowledge bases**:

| KB | Location | Purpose | Access |
|----|----------|---------|--------|
| **Meta Harness KB** | `.meta.data/kb-meta/knowledge-meta.db` | Meta project patterns & workflows | `meta_kb` |
| **Agent-X KB** | `.meta.data/kb-meta/agent-x/agent-x.db` | Agent-X project knowledge | `agentx_kb` |

### For AI Agents (opencode)

**Rule:** ALWAYS use the appropriate KB before starting work and after completing tasks.

```python
# Import both KBs
from .meta.tools import meta_kb, agentx_kb

# BEFORE task: Get guidance from Meta Harness KB
result = meta_kb.kb_ask("Where should I implement this feature?")
print(result)  # RAG-augmented answer with context

# AFTER task: Document in Agent-X KB
agentx_kb.kb_add_entry(
    entry_type="pattern",
    category="code",
    title="My Discovery",
    finding="What I found",
    solution="How I solved it",
    confidence=0.95
)
```

### For Human Users - Invokable Commands

**Important:** These commands are for use **during your conversation with the AI agent** (opencode). When you type these commands, the AI agent will execute them and show you the results.

| Command | Syntax | Example |
|---------|--------|---------|
| **Search KB** | `search kb "{query}"` | `search kb "TDD workflow"` |
| **Ask KB** | `ask kb "{question}"` | `ask kb "Where to write tests?"` |
| **Add to KB** | `add to kb {type} "{title}" "{finding}" "{solution}"` | `add to kb pattern "Chat Workflow" "Uses OpenRouter API"` |
| **Show KB stats** | `show kb stats` | `show kb stats` |
| **Evolve KB** | `evolve kb` | `evolve kb` |
| **Query KB (shorthand)** | `?kb {question}` | `?kb Where should I work?` |

**Examples:**

```bash
# Search for patterns
> search kb "REPL command"

# Ask a question (automatically routes to correct KB)
> ask kb "Where should I implement features?"

# Ask with shorthand
> ?kb Where should I write tests?

# Add new knowledge (AI will prompt for details if needed)
> add to kb pattern "Chat Workflow" "Uses OpenRouter API" "Call create() method"

# View statistics (shows both KBs)
> show kb stats

# Run evolution cycle (evolves both KBs)
> evolve kb
```

### Automatic KB Routing

The AI agent **automatically routes** your query to the appropriate KB:

| Your Query | Routes To | Why |
|------------|-----------|-----|
| "Where should I write tests?" | Meta Harness KB | General workflow question |
| "How does REPL work?" | Agent-X KB | Contains "REPL" (Agent-X keyword) |
| "TDD workflow" | Meta Harness KB | General methodology |
| "Chat command implementation" | Agent-X KB | Project-specific |
| "Meta Harness patterns" | Meta Harness KB | Explicit mention |

**To force a specific KB:**
- Use `in meta` or `in agentx` at the end of your query
- Example: `search kb "workflow" in agentx`

### Available Functions

| Function | KB | Use Case |
|----------|-----|----------|
| `kb_search(query, top_k=5, category=None)` | Both | Find specific patterns |
| `kb_ask(question, top_k=3)` | Both | Get RAG-augmented guidance |
| `kb_add_entry(type, category, title, finding, solution, ...)` | Both | Document discoveries |
| `kb_correct(entry_id, reason, new_finding)` | Both | Auto-correct knowledge |
| `kb_evolve()` | Both | Run evolution cycle |
| `kb_stats()` | Both | Monitor KB health |

### Example Usage (AI Agent)
```python
from .meta.tools import meta_kb, agentx_kb

# Search Meta Harness KB for workflows
result = meta_kb.kb_search("TDD workflow", top_k=3)
print(result)

# Ask Agent-X KB about project structure
result = agentx_kb.kb_ask("How does the REPL work?")
print(result)

# Add to Agent-X KB
agentx_kb.kb_add_entry(
    entry_type="pattern",
    category="workflow",
    title="Feature Implementation",
    finding="Work in .meta.sandbox/",
    solution="Copy → Modify → Test",
    confidence=0.95
)

# Get statistics
meta_stats = meta_kb.kb_stats()
agentx_stats = agentx_kb.kb_stats()
print(f"Meta KB: {meta_stats.split(chr(10))[0]}")
print(f"Agent-X KB: {agentx_stats.split(chr(10))[0]}")
```

### Response Format
All tools return standardized text responses:
- **Search**: Formatted entries with ID, type, category, confidence, finding, solution
- **Ask**: RAG-augmented prompt with retrieved knowledge context
- **Add**: Confirmation message with entry ID
- **Stats**: Formatted statistics report
- **Evolve**: Evolution cycle results

### When to Use Each KB

**Use Meta Harness KB (`meta_kb`) for:**
- Where to work (`.meta.sandbox/`, `.meta.tests_sandbox/`)
- How to structure code
- Testing methodologies
- Project organization
- Meta project patterns

**Use Agent-X KB (`agentx_kb`) for:**
- REPL interface details
- Command implementations
- Agent architecture
- Feature-specific patterns
- Project discoveries

---

### Response Format
All tools return standardized JSON:
```json
{
  "success": true,
  "message": "Human-readable message",
  ... (tool-specific fields)
}
```

---

## When Things Go Wrong

| Situation | Action |
|-----------|--------|
| **Unsure** | Stop → Re-read META.md → Check examples → Ask KB (`rag_ask()`) |
| **Made mistake** | Document → Don't hide → Propose fix → Learn |
| **Production affected** | Stop → Document → Propose rollback → Get approval |
| **No KB results** | Try broader query → Check spelling → Verify DB exists |

---

## Resources

| Resource | Purpose |
|----------|---------|
| [`AGENTS.md`](AGENTS.md) | Entry point (this file) |
| [`META_HARNESS.md`](META_HARNESS.md) | Complete harness documentation |
| [`DIRECTIVES.md`](.meta.project_development/DIRECTIVES.md) | Core rules (6 directives) |
| [`WORKFLOWS.md`](.meta.project_development/WORKFLOWS.md) | Workflow patterns |
| [`QUICK_REFERENCE.md`](.meta.project_development/QUICK_REFERENCE.md) | Quick decision guide |
| [`.meta.reflection/README.md`](.meta.reflection/README.md) | Reflection test documentation |
| `README.md` | Project overview |

---

## Quick Reference - KB Commands

### User Commands (Type to AI Agent)
These commands are executed by the AI agent (opencode) during your conversation:

```bash
?kb {question}              # Shorthand: Ask KB a question
search kb "{query}"         # Search knowledge base
ask kb "{question}"         # Ask KB question (verbose)
add to kb {type} "title" "finding" "solution"  # Add knowledge
show kb stats               # View statistics
evolve kb                   # Run evolution cycle
```

### AI Agent Python Usage
When working on tasks, the AI agent uses:
```python
from .meta.tools import meta_kb, agentx_kb

meta_kb.kb_ask("...")    # Meta Harness KB (workflows, patterns)
agentx_kb.kb_ask("...")  # Agent-X KB (project-specific)
```

---
> **READ META.md FIRST** · **WORK IN SAFE SPACES** · **TEST BEFORE PROPOSING** · **DOCUMENT EVERYTHING** · **STORE KNOWLEDGE** · **NEVER COMMIT WITHOUT PERMISSION**

---

**Version**: 2.2.0 (2026-04-25) - Added dual KB system with user commands
**Maintained by**: opencode AI agent
**License**: Apache 2.0
