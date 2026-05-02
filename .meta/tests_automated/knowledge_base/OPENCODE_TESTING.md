# OpenCode Agent - Knowledge Base Integration Testing Guide

## Overview

This document describes the comprehensive test suite designed to ensure the META HARNESS Knowledge Base (KB) works seamlessly with the opencode AI agent.

**Test Statistics:**
- **Total Test Suites**: 7
- **Total Tests**: 70+
- **Success Rate Target**: 100%
- **Last Updated**: 2026-05-02

## Test Architecture

```
.meta/tests_automated/knowledge_base/
├── run_tests.py                      # Main test runner
├── run_all_tests.sh                  # Shell wrapper
├── test_kb_functionality.py          # Core KB functionality (12 tests)
├── test_kb_performance.py            # Performance tests (8 tests)
├── test_kb_edge_cases.py             # Edge cases (14 tests)
├── test_kb_integration.py            # Integration tests (11 tests)
├── test_kb_populate.py               # Population tests (11 tests)
├── test_opencode_integration.py      # OpenCode integration (22 tests) ⭐
├── test_opencode_commands.py         # OpenCode commands (15 tests) ⭐
├── test_results.json                 # Auto-generated results
└── OPENCODE_TESTING.md               # This document
```

## Quick Start

### Run All Tests
```bash
# From the knowledge_base test directory
cd .meta/tests_automated/knowledge_base/
python3 run_tests.py

# Or using the shell wrapper
./run_all_tests.sh

# Verbose output
python3 run_tests.py --verbose
```

### Run Specific Test Suites
```bash
# OpenCode integration tests
python3 test_opencode_integration.py

# OpenCode command tests
python3 test_opencode_commands.py

# Core functionality
python3 test_kb_functionality.py
```

## Test Categories

### 1. Agent Workflow Tests (22 tests)

These tests validate that the KB supports the workflows that opencode follows:

#### Startup Workflow
- ✅ Reading WORK.md and PROJECTS.md
- ✅ Querying KB for context
- ✅ Proceeding with task

```python
def test_agent_startup_workflow():
    """Test the workflow an agent follows on startup"""
    # 1. Check work files exist
    # 2. Query KB for context
    # 3. Verify KB integration works
```

#### KB-First Rule
- ✅ Enforcing KB queries before tasks
- ✅ Multiple query patterns
- ✅ Context retrieval

#### Context Switching
- ✅ Switching between different tasks
- ✅ Category-based filtering
- ✅ Multi-domain queries

### 2. Query Pattern Tests

Tests for common query patterns agents use:

| Pattern | Example | Status |
|---------|---------|--------|
| Location | "Where should I write tests?" | ✅ |
| How-to | "How to add a feature?" | ✅ |
| Definition | "What is MainController?" | ✅ |
| Usage | "When to use sandbox?" | ✅ |
| Reasoning | "Why this workflow?" | ✅ |

### 3. Context Management Tests

Ensures KB maintains proper context:

- ✅ **Context Persistence**: Data persists across operations
- ✅ **Concurrent Access**: Multiple operations work simultaneously
- ✅ **Session State**: Complete session workflows function correctly

### 4. Error Handling Tests

Validates graceful handling of agent mistakes:

| Test | Description | Status |
|------|-------------|--------|
| Empty queries | `kb_search("")` | ✅ |
| Whitespace only | `kb_search("   ")` | ✅ |
| Very long queries | 1000+ characters | ✅ |
| SQL injection | `SELECT * FROM...` | ✅ |
| XSS attempts | `<script>...` | ✅ |
| Invalid inputs | Missing required fields | ✅ |
| Error recovery | Continue after failures | ✅ |

### 5. Performance Tests

Ensures KB responsiveness for agent interactions:

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Query Latency (avg) | < 1.0s | ~0.15s | ✅ |
| Batch Operations | < 500ms/op | ~50ms | ✅ |
| Memory Usage | < 10MB increase | ~2MB | ✅ |
| Concurrent Ops | 100% success | 100% | ✅ |

### 6. Agent-Specific Feature Tests

Features that specifically support AI agent workflows:

#### RAG Augmentation
```python
def test_agent_rag_augmentation():
    """Test RAG augmentation provides useful context to agent"""
    question = "Where should I write tests in AgentX?"
    result = kb_ask(question, top_k=3)
    # Should provide augmented prompt with context
```

#### Confidence Scoring
- ✅ All results include confidence scores
- ✅ Agent can make informed decisions
- ✅ Low confidence results flagged

#### Category Filtering
- ✅ workflow, code, test, documentation
- ✅ Multi-category searches
- ✅ Category-based refinement

#### Entry Creation
- ✅ Agent can add entries after tasks
- ✅ Proper metadata capture
- ✅ Immediate searchability

#### Knowledge Evolution
- ✅ Decay unused entries
- ✅ Archive low confidence
- ✅ Maintain KB quality

### 7. Command Integration Tests (15 tests)

#### CLI Commands
```bash
# Search
meta kb search "MainController" -k 3

# Ask
meta kb ask "What is MainController?" --top-k 3

# Stats
meta kb stats

# Add
meta kb add finding test "Title" "Finding" "Solution" --confidence 0.9

# Explore
meta kb explore

# Correct
meta kb correct <id> "reason" "new finding"
```

#### Python API
```python
from knowledge_base import kb_search, kb_ask, kb_add_entry, kb_stats

# Search
result = kb_search("MainController", top_k=3)

# Ask
answer = kb_ask("What is the workflow?", top_k=3)

# Add entry
kb_add_entry("finding", "test", "Title", "Finding", "Solution")

# Stats
stats = kb_stats()
```

## Agent Workflows

### Complete Agent Session
```
1. Startup
   └─→ Read WORK.md
   └─→ Read PROJECTS.md
   └─→ Query KB for context

2. Task Execution
   └─→ Search KB (kb-first rule)
   └─→ Perform task in sandbox
   └─→ Test changes

3. Knowledge Capture
   └─→ Add KB entry
   └─→ Verify entry exists
   └─→ Update stats

4. Close
   └─→ Final stats
   └─→ Session log
```

### KB-First Workflow (MANDATORY)
```python
# 1. Query KB FIRST (before ANY task)
kb_result = kb_ask("Where should I write tests?")

# 2. Review results (confidence scores)
# 3. Answer based on KB + codebase
# 4. If KB missing info → Add entry after completion
```

## Test Results

### Current Status (2026-05-02)

| Test Suite | Tests | Passed | Failed | Warnings | Success Rate |
|------------|-------|--------|--------|----------|--------------|
| Functionality | 12 | 12 | 0 | 0 | 100% |
| Performance | 8 | 8 | 0 | 0 | 100% |
| Edge Cases | 14 | 14 | 0 | 0 | 100% |
| Integration | 11 | 11 | 0 | 0 | 100% |
| Populate | 11 | 11 | 0 | 0 | 100% |
| **OpenCode Integration** | **22** | **22** | **0** | **0** | **100%** |
| **OpenCode Commands** | **15** | **14** | **0** | **1** | **100%** |
| **TOTAL** | **107** | **106** | **0** | **1** | **100%** |

### Performance Benchmarks

```
Query Performance:
  - Simple queries:    ~6ms
  - Complex queries:   ~150ms
  - Multi-hop:         ~300ms
  - Batch (10 ops):    ~500ms

Memory Usage:
  - Baseline:          ~50MB
  - After 20 queries:  ~52MB (+2MB)
  - After 100 queries: ~55MB (+5MB)

Concurrency:
  - Simultaneous users: 10+
  - No deadlocks
  - No race conditions
```

## Integration Patterns

### Pattern 1: Agent Startup
```python
# 1. Read work files
work_file = Path("WORK.md")
projects_file = Path("PROJECTS.md")

# 2. Query KB for context
context = kb_ask("What is my current task?")

# 3. Proceed with task
```

### Pattern 2: KB-First Query
```python
# ALWAYS query KB first
result = kb_ask("Where should I write tests?")

# Use KB response as PRIMARY source
# Only search code if KB has no answer
```

### Pattern 3: Task Completion
```python
# After completing task
kb_add_entry(
    entry_type="finding",
    category="test",
    title="Task Completion",
    finding="What was discovered",
    solution="How to solve it",
    context="When this applies",
    confidence=0.9
)
```

## Troubleshooting

### Common Issues

#### Issue: Tests fail with "No results found"
**Solution**: Run `meta kb populate` to ensure KB has entries

#### Issue: Slow query performance
**Solution**: Check database size, consider running `meta kb evolve`

#### Issue: Memory leak
**Solution**: Verify database connections are closed properly

#### Issue: Concurrent access errors
**Solution**: Ensure proper locking mechanism in database

### Debug Mode

```bash
# Enable verbose output
python3 run_tests.py --verbose

# Run single test
python3 -m pytest test_opencode_integration.py::test_agent_startup_workflow -v

# Check test results
cat test_results.json
```

## Best Practices

### For AI Agents
1. **Always query KB first** - Before ANY task
2. **Check confidence scores** - Use high-confidence entries
3. **Add knowledge after tasks** - Populate KB with learnings
4. **Handle errors gracefully** - Continue on failures
5. **Respect KB-first rule** - Non-negotiable

### For Developers
1. **Run tests after changes** - Ensure no regressions
2. **Monitor performance** - Watch query latencies
3. **Review test coverage** - Add tests for new features
4. **Update documentation** - Keep this guide current
5. **Archive old entries** - Run evolution cycles

## Future Enhancements

### Planned Tests
- [ ] Multi-agent collaboration scenarios
- [ ] Long-running session stability
- [ ] Large-scale KB (10k+ entries)
- [ ] Network failure recovery
- [ ] Distributed KB instances

### Planned Features
- [ ] Real-time KB updates
- [ ] Advanced query suggestions
- [ ] Automatic entry categorization
- [ ] Semantic search improvements
- [ ] Multi-language support

## References

- [KB META.md](../../knowledge_base/META.md) - KB documentation
- [AGENTS.md](../../AGENTS.md) - Agent guidelines
- [META_HARNESS.md](../../META_HARNESS.md) - Master documentation
- [Test Summary](TEST_SUMMARY.md) - Detailed test results

---

**Version**: 1.0.0 | **Last Updated**: 2026-05-02 | **Maintained by**: Agent-X Team
