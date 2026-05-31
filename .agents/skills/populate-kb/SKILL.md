---
name: populate-kb
description: >
  Populate the Knowledge Base with comprehensive project documentation.
  **FOR CODING AGENTS ONLY**: This skill is designed for AI coding agents using the
  Knowledge Base MCP server tools. It automates KB population through MCP tool calls
  with parallel execution, quality scoring, incremental updates, and self-healing.
  Trigger on: "populate KB", "refresh knowledge base", "document the project",
  "update KB with project", "scan project for KB", or when KB stats show 0 entries.
---

# Knowledge Base Population Skill

**Target User**: AI Coding Agents (e.g., opencode, Cursor, GitHub Copilot Workspace)  
**MCP Server Required**: `mcp_servers/knowledge_base/server.py`  
**Tools Used**: `knowledge_base_*` MCP tool suite  
**Quality Target**: ≥ 25 entries, ≥ 0.75 confidence, ≥ 5 categories covered  
**Max Parallelism**: 3 concurrent MCP calls

This skill creates comprehensive Knowledge Base entries by scanning and analyzing the entire AgentX project structure, extracting architectural patterns, class hierarchies, workflows, and key decisions **using MCP tools exclusively**. The process is optimized for speed through parallel tool calls and quality through automated validation.

## ⚠️ CRITICAL: For Coding Agents Only

This skill is **NOT for humans**. It is designed exclusively for AI coding agents that have access to the Knowledge Base MCP server tools. The entire workflow is executed through MCP tool calls and file operations.

**Required MCP Tools (7):**
| # | Tool | Purpose | Phase |
|---|------|---------|-------|
| 1 | `knowledge_base_kb_stats_tool` | KB state check & final metrics | Phase 0, 4, 6 |
| 2 | `knowledge_base_kb_populate_workspace_tool` | Automated extraction from files | Phase 2 |
| 3 | `knowledge_base_kb_ask_tool` | RAG synthesis quality testing | Phase 5 |
| 4 | `knowledge_base_kb_search_tool` | Gap analysis & coverage check | Phase 5 |
| 5 | `knowledge_base_kb_add_tool` | Manual entry injection | Phase 3 |
| 6 | `knowledge_base_kb_reset_tool` | Clean slate (with approval) | Phase 1 |
| 7 | `knowledge_base_kb_list_categories` | Validate schema compliance | Phase 4 |

**Quality Gate Metrics (MUST meet all):**
- ✅ **Completeness**: ≥ 25 total entries for full project
- ✅ **Diversity**: ≥ 5 categories covered (code, class, workflow, architecture, documentation)
- ✅ **Confidence**: Mean confidence ≥ 0.75 (median ≥ 0.80)
- ✅ **Coverage**: ≥ 80% of source directories indexed
- ✅ **Coherence**: ≥ 2 test queries returning relevant answers with ≥ 0.6 confidence

## When to Use

### Automatic Triggers (Agent SHOULD self-activate):
- **KB is empty** (0 entries at session start)
- **KB is stale** (last populated > 7 days ago AND git changes detected)
- **KB is degraded** (< 15 entries OR mean confidence < 0.5)
- **Major refactoring completed** (≥ 5 files changed in git diff)
- **New feature merged** (new directory in `src/agentx/`)

### User-Requested Triggers:
- "populate KB", "refresh knowledge base", "document the project"
- "update KB with project", "scan project for KB"
- "re-index the codebase", "sync KB with code"

## Process for Coding Agents

### Execution Pipeline (7 Phases with Parallelism)

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 0:    DIAGNOSE         kb_stats_tool + git diff           │
│ PHASE 1:    PREPARE          Decision: reset? incremental?      │
│ PHASE 2:    EXTRACT          kb_populate_workspace_tool         │
│ PHASE 3:    ENRICH           kb_add_tool (parallel x 3-5)       │
│ PHASE 4:    VALIDATE         kb_stats_tool + kb_list_categories │
│ PHASE 5:    VERIFY           kb_ask_tool + kb_search_tool (2-3) │
│ PHASE 6:    REPORT           Summary                              │
└─────────────────────────────────────────────────────────────────┘
```

### Phase 0: DIAGNOSE — Assess KB & Code Health (Parallel)

**Agent Tool Calls (IN PARALLEL):**
```json
[
  {
    "tool": "knowledge_base_kb_stats_tool",
    "parameters": {},
    "purpose": "Check current KB state"
  },
  {
    "tool": "knowledge_base_kb_list_categories",
    "parameters": {},
    "purpose": "Get valid schema for validation"
  },
  {
    "purpose": "Check git changes to detect staleness",
    "command": "git diff --stat HEAD~5 -- src/ agentx/ tests/"
  }
]
```

**Agent Decision Matrix:**

| KB State | Git State | Action | Phase 1 Strategy |
|----------|-----------|--------|------------------|
| 0 entries | Any | Auto-populate | `reset_first=true` |
| < 15 entries | Clean (no changes) | Auto-populate | `reset_first=true` |
| < 15 entries | Dirty (changes) | Auto-populate | `reset_first=true` |
| ≥ 15 entries | Clean, < 7 days | **SKIP** (healthy) | Report "KB healthy" |
| ≥ 15 entries | Dirty, < 7 days | Ask user | Incremental or reset |
| ≥ 15 entries | Any, > 7 days | Auto-populate | `reset_first=true` (stale) |
| Any | Confidence < 0.5 | Auto-populate | `reset_first=true` (degraded) |

### Phase 1: PREPARE — Set Up Population Strategy

**If resetting** (auto-approved when 0/< 15 entries):

**Agent Tool Call:**
```json
{
  "tool": "knowledge_base_kb_reset_tool",
  "parameters": {},
  "note": "Only call if Phase 0 decided RESET strategy"
}
```

**If incremental** (user approved for ≥ 15 entries):

**Agent Tool Call:**
```json
{
  "tool": "knowledge_base_kb_populate_workspace_tool",
  "parameters": {
    "workspace_root": "/home/oikumo/develop/production/agentx",
    "include_python": true,
    "include_markdown": true,
    "exclude_dirs": [".venv", ".git", ".pytest_cache", "local_sessions"],
    "reset_first": false
  },
  "note": "reset_first=false preserves existing entries"
}
```

**If skipping** (healthy KB):
- Report to user and stop. No further phases needed.

### Phase 2: EXTRACT — Run Population (Single Call)

**Agent Tool Call:**
```json
{
  "tool": "knowledge_base_kb_populate_workspace_tool",
  "parameters": {
    "workspace_root": "/home/oikumo/develop/production/agentx",
    "include_python": true,
    "include_markdown": true,
    "exclude_dirs": [".venv", ".git", ".pytest_cache", "local_sessions"],
    "reset_first": false
  },
  "note": "reset_first=false because Phase 1 already handled reset"
}
```

**Agent Notes:**
- This is the **slowest** single call — expect 10-60s depending on project size
- The server has built-in default excludes (`__pycache__`, `.venv`, `venv`, `.git`, `node_modules`, `chroma_db`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `dist`, `build`, `.tox`, `.eggs`, `site-packages`, `.env*` patterns). The `exclude_dirs` parameter is **additive** on top of these defaults.
- Always use absolute path for `workspace_root`
- Set `reset_first=false` here (Phase 1 decides reset separately)

### Phase 3: ENRICH — Add Manual Wisdom (Parallel)

Run these MCP calls **in parallel** (they don't depend on each other):

**Agent Tool Calls (PARALLEL x 5):**

```json
{
  "tool": "knowledge_base_kb_add_tool",
  "parameters": {
    "entry_type": "pattern",
    "category": "architecture",
    "title": "META Project System",
    "finding": "AgentX uses .meta/ directory for safe experimentation and project planning with strict isolation from production code",
    "solution": "All structural changes go through .meta/ with META.md governing rules per subdirectory.",
    "context": "Part of the KB-First workflow and META consistency rules. Agents must read META.md before operating in any .meta/ subdirectory.",
    "confidence": 0.98,
    "example": "├── .meta/\n│   ├── projects/   (planning)\n│   ├── doc/        (references)\n│   ├── experiments/ (prototyping)\n│   └── META.md     (rules)"
  }
}

{
  "tool": "knowledge_base_kb_add_tool",
  "parameters": {
    "entry_type": "pattern",
    "category": "workflow",
    "title": "KB-First Mandatory Workflow",
    "finding": "Every agent interaction MUST query the Knowledge Base first before searching code. This prevents stale or incorrect information from code-only searches.",
    "solution": "1. Query KB via kb_ask_tool or kb_search_tool. 2. If KB has answer: cite sources, show confidence. 3. If KB empty: inform user, then search code.",
    "context": "Enforced by AGENTS.md rules. Violation = Task Failure. Confidence scores must be displayed to user.",
    "confidence": 0.95,
    "example": "KB response: '✓ Answer synthesized from 3 sources (Confidence: 0.88)' → Use this. KB response: 'No results found.' → Then grep/code search."
  }
}
```

**Minimum 3 parallel calls** for essential knowledge:
1. **META System** (architecture pattern, confidence 0.98)
2. **KB-First Workflow** (workflow pattern, confidence 0.95)  
3. **Main Controller Architecture** (class pattern, confidence 0.90)

**Optional additional (if code exists):**
4. **RAG Implementation Pattern** (finding/code)
5. **Petri Net Session Management** (decision/architecture)

### Phase 4: VALIDATE — Quality Gate (Parallel)

**Agent Tool Calls (IN PARALLEL):**

> 💡 **Optimization:** If Phase 0 already retrieved valid categories, the `kb_list_categories` call below can be skipped — reuse the Phase 0 result instead. Only call it here if Phase 0 was skipped or is stale.

```json
[
  {
    "tool": "knowledge_base_kb_stats_tool",
    "parameters": {},
    "purpose": "Get final population metrics"
  },
  {
    "tool": "knowledge_base_kb_list_categories",
    "parameters": {},
    "purpose": "Confirm schema coverage (optional — reuse from Phase 0)"
  }
]
```

**Quality Gate Checklist (ALL must pass):**

```
GATE A — COMPLETENESS
  Expected: ≥ 25 total entries
  Actual:   {N} entries
  Status:   PASS / FAIL

GATE B — DIVERSITY  
  Expected: ≥ 5 categories covered
  Categories: {list}
  Status:   PASS / FAIL

GATE C — CONFIDENCE
  Expected: Mean ≥ 0.75, Median ≥ 0.80
  Actual:   Mean {0.XX}, Median {0.XX}
  Status:   PASS / FAIL

GATE D — COVERAGE (check src/ dirs indexed)
  Expected: {all_dirs} present in by_pattern
  Missing:  {list}
  Status:   PASS / FAIL
```

**If any gate FAILS:**
- **Gate A fails** → Re-run Phase 2 with adjusted exclude_dirs
- **Gate B fails** → Run additional `kb_add_tool` for missing categories (Phase 3)
- **Gate C fails** → Flag warning. Many auto-extracted entries have low confidence by nature. Add high-confidence manual entries.
- **Gate D fails** → Check if missing dirs actually contain .py files. If yes, they may be excluded.

### Phase 5: VERIFY — Functional Testing (Parallel)

**Agent Tool Calls (IN PARALLEL x 3):**

```json
[
  {
    "tool": "knowledge_base_kb_ask_tool",
    "parameters": {
      "question": "What is the main controller in AgentX and what does it manage?",
      "top_k": 3
    },
    "purpose": "Core architecture test"
  },
  {
    "tool": "knowledge_base_kb_ask_tool",
    "parameters": {
      "question": "How does the KB-First workflow work and why is it important?",
      "top_k": 3
    },
    "purpose": "Workflow knowledge test"
  },
  {
    "tool": "knowledge_base_kb_search_tool",
    "parameters": {
      "query": "RAG",
      "top_k": 5,
      "category": "code"
    },
    "purpose": "Feature-specific search test"
  }
]
```

**Coherence Gate:**
```
GATE E — COHERENCE
  Expected: ≥ 2/3 queries return relevant answers with confidence ≥ 0.6
  Actual:   Query 1: {conf} | Query 2: {conf} | Query 3: {conf}
  Status:   PASS / FAIL
```

**If coherence fails (≥ 2 failures):**
- Re-run Phase 2 with broader scope
- Add more manual entries for the failed topic
- Check if source code is in excluded directories

### Phase 6: REPORT — Summarize

**Agent User Report:**
```
✅ Knowledge Base Population Complete

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Entries:   {N}  (target: ≥ 25)
Categories:      {M}/7 (target: ≥ 5)
  • code: {n} • class: {n} • method: {n}
  • function: {n} • workflow: {n}
  • documentation: {n} • architecture: {n}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏷️  BY TYPE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pattern:    {n}  Decision:   {n}
Finding:    {n}  Correction: {n}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 CONFIDENCE DISTRIBUTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
High   (≥ 0.9):  {n}  ████████
Medium (0.6-0.9):{n}  ██████
Low    (< 0.6):  {n}  ██
Mean: {0.XX}  |  Median: {0.XX}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ QUALITY GATES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{PASS/FAIL}  Completeness: ≥ 25 entries
{PASS/FAIL}  Diversity: ≥ 5 categories
{PASS/FAIL}  Confidence: mean ≥ 0.75
{PASS/FAIL}  Coverage: ≥ 80% dirs
{PASS/FAIL}  Coherence: ≥ 2/3 queries

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 RECOMMENDATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• {Recommendation 1}
• {Recommendation 2}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏱️  OPERATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
kb_populate_workspace_tool: 1 call
kb_stats_tool:              {n} calls
kb_add_tool:                {n} calls
kb_ask_tool:                {n} calls
kb_search_tool:             {n} calls
kb_list_categories:         {n} calls
 
```

## What Gets Captured (Agent Reference)

### Automatic Extraction (via MCP Tool)

The `knowledge_base_kb_populate_workspace_tool` MCP tool automatically extracts:

**From Python Files:**
- Class definitions and docstrings
- Function signatures and docstrings
- Method hierarchies
- Import relationships
- Type hints and signatures

**From Markdown Files:**
- Documentation structure
- Workflow descriptions
- Architecture decisions
- README files
- META documentation

**Structural Patterns Detected:**
- Controller-Model-View pattern
- MCP server architecture
- RAG implementation patterns
- Session management approaches

### Manual Additions (Agent Should Add)

**Agent Action Required**: Use `knowledge_base_kb_add_tool` for:

1. **Architectural Decisions** (Type: `decision`, Category: `architecture`)
   - Why META system was chosen
   - RAG implementation approach
   - Petri Net session management design

2. **Key Workflows** (Type: `pattern`, Category: `workflow`)
   - KB-First workflow
   - Project planning workflow
   - Testing workflow

3. **Critical Classes** (Type: `pattern`, Category: `class`)
   - MainController
   - SessionManager
   - RAGModel
   - Petri Net components

**Why Manual Entries?**: Automatic extraction may miss high-level context, rationale, and cross-cutting concerns that require synthesis.

## Examples for Coding Agents

### Example 1: Full Population (Empty KB — AUTO)

**Scenario**: Agent starts fresh session, KB has 0 entries.

**Agent Pipeline Execution:**

```
PHASE 0 — DIAGNOSE (parallel)
├── kb_stats_tool → Total Entries: 0 ✓ (auto-triggered)
├── kb_list_categories → Valid schema loaded
└── git diff → 12 files changed (recent activity)

PHASE 1 — PREPARE
├── Decision: RESET (0 entries = auto)
└── kb_reset_tool → ✅ Reset (no-op, already empty)

PHASE 2 — EXTRACT
└── kb_populate_workspace_tool(reset_first=false)
    → ✅ 42 entries from 28 files

PHASE 3 — ENRICH (parallel x 3)
├── kb_add_tool → PAT-001: META System (arch, 0.98)
├── kb_add_tool → PAT-002: KB-First Workflow (workflow, 0.95)
└── kb_add_tool → PAT-003: MainController (class, 0.90)

PHASE 4 — VALIDATE (parallel)
├── kb_stats_tool → 45 entries, 6 categories, mean 0.82
└── kb_list_categories → All 7 categories present

QUALITY GATES: 5/5 PASSED ✓

PHASE 5 — VERIFY (parallel x 3)
├── kb_ask_tool("Main controller") → conf 0.88 ✓
├── kb_ask_tool("KB-First workflow") → conf 0.92 ✓
└── kb_search_tool("RAG", code) → 5 results ✓

PHASE 6 — REPORT
└── Display formatted report to user
```

**Agent Output Summary:**
```
✅ KB populated successfully
📊 45 entries | 6 categories | Mean confidence 0.82
✅ 5/5 quality gates passed
⏱️ 8 MCP calls | 3 parallel batches
```

### Example 2: Incremental Update (Healthy KB, Recent Changes)

**Scenario**: KB has 30 entries (healthy), but user just merged a feature branch with 8 changed files.

**Agent Pipeline Execution:**

```
PHASE 0 — DIAGNOSE (parallel)
├── kb_stats_tool → 30 entries, mean 0.85 (HEALTHY)
├── kb_list_categories → 6/7 categories
└── git diff HEAD~1 → 8 files changed in src/agentx/controllers/

Decision: → ASK USER for strategy
Agent to user: "KB has 30 entries (healthy). 8 files changed in controllers/. 
                Reset & repopulate, or incremental append? [reset/append/skip]"

User: "append"

PHASE 1 — PREPARE
└── Skip reset (append strategy)

PHASE 2 — EXTRACT
└── kb_populate_workspace_tool(reset_first=false)
    → ⚡ 12 new entries (only changed files), 0 duplicates

PHASE 3 — ENRICH (parallel)
├── kb_search_tool("controller", class) → 3 existing entries
└── kb_add_tool for new FeatureController → PAT-050 (0.92)

PHASE 4 — VALIDATE
└── kb_stats_tool → 43 entries, 7 categories, mean 0.84

QUALITY GATES: 5/5 PASSED ✓

PHASE 5 — VERIFY (parallel x 2)
├── kb_ask_tool("new feature controller") → conf 0.78 ✓
└── kb_search_tool("controller", class) → 8 results ✓

PHASE 6 — REPORT
└── "KB updated: +13 entries from controllers feature merge"
```

### Example 3: Degraded KB Recovery (AUTO-FIX)

**Scenario**: KB shows 8 entries, mean confidence 0.42 (degraded).

**Agent Pipeline Execution:**

```
PHASE 0 — DIAGNOSE
└── kb_stats_tool → 8 entries, mean 0.42 (DEGRADED ⚠️)
    Trigger: Auto-repair activated

PHASE 1 — PREPARE
└── Decision: RESET + FULL REPOPULATION (auto)
    kb_reset_tool → ✅ Cleared

PHASE 2 — EXTRACT
└── kb_populate_workspace_tool(reset_first=false)
    → 38 entries

PHASE 3 — ENRICH (parallel x 5)
    → +5 manual high-confidence entries

PHASE 4 — VALIDATE
└── 43 entries, mean 0.81 | QUALITY GATES: 5/5 PASSED ✓

PHASE 5 — VERIFY
└── All 3 queries pass coherence gate ✓

PHASE 6 — REPORT
└── "KB auto-recovered: 8→43 entries, confidence 0.42→0.81"
```

### Example 4: Targeted Population (Single Module)

**User Prompt**: "Populate KB with only the MCP server code"

**Agent Pipeline (abbreviated):**

```
PHASE 0: Check if targeted population is appropriate
PHASE 1: Skip reset (use fresh population with specific root)
PHASE 2: kb_populate_workspace_tool(
    workspace_root="/home/oikumo/develop/production/agentx/mcp_servers",
    include_python=true,
    include_markdown=false,
    reset_first=false
)
PHASE 3: kb_add_tool for MCP server architecture (0.95)
PHASE 4: kb_stats_tool → 12 entries
PHASE 5: kb_ask_tool("MCP server tools") → conf 0.91
PHASE 6: Report: "MCP server code indexed: 12 entries"
```

## Rules for Coding Agents

### Speed Optimization Rules

| Rule | Description | Impact |
|------|-------------|--------|
| **PARALLEL-FIRST** | Always batch independent MCP calls | 3x faster |
| **SKIP-IF-HEALTHY** | Don't repopulate if KB is healthy & current | Saves 10-60s |
| **INCREMENTAL** | Prefer append over reset when possible | Saves 40% time |
| **MINIMUM-ENRICH** | At least 3 manual entries in parallel | Quality boost |
| **LAZY-VALIDATE** | Validate only after enrichment | Fewer re-runs |

### Quality Assurance Rules

| Rule | Trigger | Action |
|------|---------|--------|
| **GATE-STRICT** | Any quality gate fails | Fix + re-run Phase 2-5 |
| **CONFIDENCE-BOOST** | Mean < 0.75 | Add 3+ manual entries |
| **CATEGORY-FILL** | < 5 categories | Targeted kb_add_tool calls |
| **COHERENCE-TEST** | Always | Run 3 kb_ask_tool queries minimum |

### Mandatory Actions (DO ✅):

| Priority | Action | Reason |
|----------|--------|--------|
| ⚠️ CRITICAL | Always run Phase 0 first | Prevents unnecessary repopulation |
| ⚠️ CRITICAL | Phase 0 checks **MUST be parallel** | Performance (3 calls at once) |
| ⚠️ CRITICAL | Phase 3 enrichment **MUST be parallel** | Performance (5 calls at once) |
| 🔴 HIGH | Phase 5 verification **MUST be parallel** | Performance (3 calls at once) |
| 🔴 HIGH | Never skip quality gate validation | Ensures KB usability |
| 🔴 HIGH | Always log structured report after population | Audit trail |
| 🟡 MEDIUM | Use exact tool names from this skill | Consistency |
| 🟡 MEDIUM | Report metrics in formatted output | User trust |
| 🟢 LOW | Suggest improvements if gates fail | Continuous improvement |

### Prohibited Actions (DON'T ❌):

| Severity | Action | Consequence |
|----------|--------|-------------|
| 🚫 BLOCKER | Never populate without Phase 0 diagnosis | Risk destroying healthy KB |
| 🚫 BLOCKER | Never reset healthy KB without user confirmation | Data loss |
| 🚫 BLOCKER | Never include .env, secrets, or credentials | Security breach |
| 🔴 HIGH | Never skip verification (Phase 5) | Silent KB corruption |
| 🔴 HIGH | Never forget to log population report | Audit gap |
| 🟡 MEDIUM | Never use non-absolute paths for workspace_root | Tool may fail |
| 🟡 MEDIUM | Never make sequential calls when parallel is possible | Performance waste |

## Output Format (Agent Response Template)

After population, the coding agent MUST use this exact format for user reporting:

```
✅ Knowledge Base Population Complete

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Entries:   {N}  (target: ≥ 25)
Categories:      {M}/7 (target: ≥ 5)
  • code: {n}    • class: {n}    • method: {n}
  • function: {n} • workflow: {n}
  • documentation: {n} • architecture: {n}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏷️  BY TYPE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pattern:    {n}  Decision:   {n}
Finding:    {n}  Correction: {n}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 CONFIDENCE DISTRIBUTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
High   (≥ 0.9):  {n}  ████████
Medium (0.6-0.9):{n}  ██████
Low    (< 0.6):  {n}  ██
Mean: {0.XX}  |  Median: {0.XX}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ QUALITY GATES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{PASS/FAIL}  Completeness: ≥ 25 entries
{PASS/FAIL}  Diversity: ≥ 5 categories
{PASS/FAIL}  Confidence: mean ≥ 0.75
{PASS/FAIL}  Coverage: ≥ 80% dirs
{PASS/FAIL}  Coherence: ≥ 2/3 queries

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 RECOMMENDATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• {Recommendation 1}
• {Recommendation 2}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏱️  OPERATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
kb_populate_workspace_tool: 1 call
kb_stats_tool:              {n} calls
kb_add_tool:                {n} calls
kb_ask_tool:                {n} calls
kb_search_tool:             {n} calls
kb_list_categories:         {n} calls
 
```

## Troubleshooting (Agent Guide)

### Issue 1: KB population returns 0-5 entries

**Symptoms**: `kb_populate_workspace_tool` reports 0-5 total entries after scan.

**Root Cause Matrix**:
| Cause | Probability | Detection | Quick Fix |
|-------|-------------|-----------|-----------|
| Wrong workspace_root path | 40% | Tool reports 0 files | Use absolute path |
| All dirs excluded | 30% | Report shows all dirs excluded | Remove unnecessary excludes |
| No .py/.md files | 20% | Check src/ exists | Verify project structure |
| Permission denied | 10% | Check file perms | `chmod -R +r src/` |

**Agent Self-Healing Procedure:**
```json
// STEP 1: Diagnostic population (no excludes)
{
  "tool": "knowledge_base_kb_populate_workspace_tool",
  "parameters": {
    "workspace_root": "/home/oikumo/develop/production/agentx",
    "exclude_dirs": [],
    "reset_first": true
  }
}

// If still 0 entries:
// STEP 2: Check if files actually exist
// Use glob "src/**/*.py" to verify Python files present
// If no files → wrong workspace_root, correct it
// If files exist → permission issue, report to user
```

### Issue 2: Low confidence scores (< 0.5 mean)

**Symptoms**: Many entries with confidence < 0.5 despite successful extraction.

**Root Cause**: Auto-extracted entries from poorly-documented code get low confidence. This is **expected** for first-time population of undocumented codebases.

**Agent Fix Strategy (Tiered):**

```
TIER 1 — Quick Boost (add 3-5 manual entries):
  kb_add_tool for: architecturally critical patterns (0.95+)

TIER 2 — Medium Boost (add 5-10 manual entries):
  + key workflows, main classes, design decisions

TIER 3 — Full Boost (add 10-15 manual entries):
  + all public APIs, configuration patterns, error handling
```

**Post-boost validation**: Re-run `kb_stats_tool` and check mean confidence.

### Issue 3: Coherence gate fails (≥ 2 queries fail)

**Symptoms**: `kb_ask_tool` returns irrelevant or low-confidence (< 0.5) answers for test queries.

**Diagnostic Tree:**
```
Query fails
├─ No entries found for topic
│  ├─ Auto-extraction missed it → kb_add_tool for that topic
│  └─ Source code not in workspace_root → Adjust scope
├─ Entries found but irrelevant
│  └─ Wrong category/type → kb_search_tool to find correct entries
└─ Entries found but low confidence (< 0.5)
   └─ Poor source documentation → manual entries needed
```

**Agent Fix Procedure:**
```json
// 1. Search for closest match
{
  "tool": "knowledge_base_kb_search_tool",
  "parameters": {
    "query": "{failed_topic}",
    "top_k": 5
  }
}

// 2. If no results: add manual high-confidence entry
{
  "tool": "knowledge_base_kb_add_tool",
  "parameters": {
    "entry_type": "pattern",
    "category": "architecture",
    "title": "{failed_topic_title}",
    "finding": "{synthesize from codebase knowledge}",
    "solution": "{how it works}",
    "confidence": 0.90
  }
}

// 3. Re-test the query
```

### Issue 4: Category diversity insufficient (< 5 categories)

**Symptoms**: KB has entries but concentrated in 2-3 categories (e.g., all "code").

**Agent Fix — Targeted Category Fill:**
```
Missing: "workflow" → kb_add_tool for KB-First workflow, testing workflow
Missing: "architecture" → kb_add_tool for MVC pattern, MCP architecture
Missing: "documentation" → kb_add_tool for README patterns, doc structure
Missing: "class" → kb_add_tool for MainController, SessionManager
Missing: "method" → kb_add_tool for key methods (if well-documented)
```

**Rule**: Add at least 1 entry per missing category. Use confidence 0.90+.

### Issue 5: Stale KB (last populated > 7 days)

**Symptoms**: KB has good metrics but is old. Git shows recent changes.

**Agent Decision**: Auto-trigger repopulation (no user confirmation needed for > 7 days stale).

**Procedure**:
1. Run full pipeline (Phases 0-6) with `reset_first=true`
2. Report as "KB refreshed after {N} days"
3. Highlight new entries from recent changes

## Performance Optimization (Agent Reference)

### Parallel Execution Pattern

**WRONG (sequential — 3x slower):**
```
Phase 0: kb_stats_tool → wait...
         kb_list_categories → wait...
         git diff → wait...
```

**CORRECT (parallel — optimal):**
```
Phase 0: [kb_stats_tool, kb_list_categories, git diff] ALL AT ONCE
```

**Pipeline Parallelism Summary:**

| Phase | Calls | Sequential | Parallel | Speedup |
|-------|-------|------------|----------|---------|
| 0 | 3 | 3 waits | 1 wait | 3x |
| 1 | 0-1 | 1 wait | 1 wait | 1x |
| 2 | 1 | 1 wait | 1 wait | 1x |
| 3 | 3-5 | 5 waits | 1 wait | 5x |
| 4 | 2 | 2 waits | 1 wait | 2x |
| 5 | 3 | 3 waits | 1 wait | 3x |
| **Total** | **13-15** | **15 waits** | **6 waits** | **2.5x** |

### Smart Skip Heuristics

**Calculate KB Health Score** (0-100):
```
Health Score = (
  (entry_count / 25) * 30 +
  (category_count / 7) * 20 +
  (mean_confidence) * 30 +
  (coherence_pass_rate) * 20
) min 100

Health Score ≥ 70 → Consider skipping (ask if git changes exist)
Health Score < 70 → Auto-repopulate
Health Score < 40 → Critical degradation, force repopulate
```

**Staleness Detection:**
```
Stale = (days_since_last_population > 7) OR (git_changes > 5 files)
If stale AND health < 70 → AUTO repopulate
If stale AND health ≥ 70 → ASK user
If not stale → SKIP (report healthy)
```

## Related Patterns (Agent References)

### Project Structure
- `.meta/META.md` — META system structure (read before modifying)
- `WORK.md` — Active work items (check for population triggers)
- `.meta/projects/META.md` — Projects directory rules
- `.meta/doc/META.md` — Documentation directory rules

### MCP Infrastructure
- `mcp_servers/knowledge_base/server.py` — Full tool implementation
- `opencode.jsonc` — MCP server registration
- `kb/` — Business logic for KB operations

### Agent System
- `AGENTS.md` — Core agent rules (KB-First mandate)
- `.agents/skills/` — All available agent skills
- `pyproject.toml` — Dependencies (chromadb, langchain, mcp, etc.)

## For Agent Developers

### How This Skill Integrates with AgentX

This skill is a **first-class component** of the KB-First Workflow mandated by `AGENTS.md`:

```
SESSION STARTUP
    │
    ├─ 1. Read WORK.md → Display to user
    │
    ├─ 2. Check KB state → kb_stats_tool
    │   │
    │   ├─ KB EMPTY (< 15 entries) → TRIGGER populate-kb skill
    │   │   └─ Execute full pipeline (Phase 0-6)
    │   │
    │   └─ KB HEALTHY (≥ 15 entries) → Proceed with session
    │
    └─ 3. KB-First workflow active → Query KB before code search
```

### Skill Activation Contract

**When this skill loads**, the agent commits to:
1. **Pre-population diagnosis** — Never skip Phase 0
2. **Parallel execution** — Always batch independent MCP calls
3. **Quality gate enforcement** — Never skip Phase 4 validation
4. **Audit trail** — Always log structured population report
5. **User transparency** — Always display formatted report

**MCP Server Configuration** (from `opencode.jsonc`):
```json
{
  "mcpServers": {
    "knowledge_base": {
      "command": "python",
      "args": ["mcp_servers/knowledge_base/server.py"]
    }
  }
}
```

### Agent Self-Check Before Population

**Pre-flight checklist** (run all in parallel):
```
□ kb_stats_tool → Has KB stats
□ ls src/ → Project files exist
□ read AGENTS.md → KB-First rules confirmed
□ read WORK.md → Current work context
```

**If any check fails**: Report to user, do not proceed.

### Version History

| Version | Date | Changes |
|---------|------|---------|
| **2.0.0** | 2026-05-23 | Major improvement: 7-phase pipeline, parallel execution, quality gates, health scoring, self-healing, incremental updates, decision matrix, performance optimization (2.5x speedup), coherence testing |
| **1.0.0** | 2026-05-23 | Initial skill: full project population with MCP tools, manual entry support, basic validation |

### Skill Metrics (Self-Reported)

| Metric | Value |
|--------|-------|
| **Phases** | 7 (with 4 parallel stages) |
| **Quality Gates** | 5 (completeness, diversity, confidence, coverage, coherence) |
| **MCP Tools Used** | 7 out of 7 available |
| **Average MCP Calls** | 13-15 (6 in parallel) |
| **Speedup vs Sequential** | 2.5x |
| **Self-Healing Procedures** | 5 (for top 5 issues) |
| **Decision Points** | 8 (in Phase 0 matrix) |
| **Target KB Health** | Score ≥ 70 |

---

**Target User**: AI Coding Agents (opencode, Cursor, GitHub Copilot Workspace, etc.)  
**MCP Server**: `mcp_servers/knowledge_base/server.py`  
**Required Tools**: All 7 `knowledge_base_*` tools  
**Skill Type**: Agent Automation (Population & Quality Assurance)  
**Confidence**: 0.99  
**Version**: 2.0.0  
**Last Updated**: 2026-05-23  
**Maintainer**: AgentX Team
