# Opencode Test Procedure for META HARNESS Integration

> **Purpose**: Optimized procedure for agents to test META HARNESS ↔ opencode integration  
> **Target**: AI agents (opencode) when user requests improvements or changes  
> **Scope**: Ensure all META HARNESS features work correctly with opencode  
> **Mandatory**: Always follow when modifying META HARNESS ↔ opencode relationship

---

## When to Use This Procedure

**Trigger this test procedure when**:
- User asks to improve META HARNESS features
- User requests changes to opencode integration
- After adding new META HARNESS directives
- When KB-first behavior needs validation
- After modifying AGENTS.md or META_HARNESS.md
- When WORK notebook functionality changes
- Before committing META HARNESS updates

---

## Pre-Test Checklist

Before running tests, verify:

- [ ] **KB is populated**: Run `meta kb stats` to confirm entries exist
- [ ] **WORK.md exists**: Check `WORK.md` is present (root folder)
- [ ] **Test suite exists**: Verify `.meta/opencode_tests/` has test files
- [ ] **Clean workspace**: No pending changes in production
- [ ] **Git status clean**: Run `git status` to confirm clean state

---

## Test Suite: 6 Core Validations

### Test 1: WORK Notebook Display (Session Start)

**Purpose**: Verify agent displays WORK.md at session start

**Procedure**:
```bash
# 1. Check WORK.md exists
ls -la WORK.md

# 2. Read current content
cat WORK.md

# 3. Verify structure has required sections
grep -E "(Current Task|Purpose|Updated by|Status)" WORK.md
```

**Expected Result**:
- File exists and is readable
- Contains "Current Task" section
- Contains "**Purpose**" metadata
- Contains "**Status**" field
- Agent displays content to user at session start

**Validation**:
```bash
python3 .meta/opencode_tests/test_work_notebook.py
# Should show: ✓ WORK.md exists
# Should show: ✓ WORK.md has correct structure
```

---

### Test 2: KB-First Query Behavior

**Purpose**: Verify agent queries Knowledge Base BEFORE code search

**Procedure**:
```bash
# 1. Ask KB-specific question
opencode run "What is MainController?"

# 2. Or use direct KB query
python3 .meta/tools/meta-harness-knowledge-base/kb ask "What is MainController?" --top-k 3
```

**Expected Result**:
- Agent queries KB first (check tool calls)
- Response cites KB entries (PAT-XXX IDs)
- Response shows confidence scores
- No direct code search if KB has answer

**Validation**:
```bash
# Check KB has entries
python3 .meta/tools/meta-harness-knowledge-base/kb stats

# Should show: Total entries: XXX
# Should show: Vector DB initialized
```

**Agent Behavior Check**:
- ✓ Agent mentions "Knowledge Base" or "KB" in response
- ✓ Agent cites specific KB entries
- ✓ Agent shows confidence scores
- ✗ Agent does NOT search code before KB query

---

### Test 3: META HARNESS Documentation Reference

**Purpose**: Verify all META HARNESS docs reference each other correctly

**Procedure**:
```bash
# 1. Check META_HARNESS.md references WORK.md
grep -i "WORK.md\|Work notebook" META_HARNESS.md

# 2. Check AGENTS.md references WORK.md
grep -i "WORK.md\|Work Notebook" AGENTS.md

# 3. Check WORK.md exists and is referenced
ls -la WORK.md
```

**Expected Result**:
- META_HARNESS.md mentions WORK.md or "Work notebook"
- AGENTS.md includes WORK.md directive
- WORK.md is in directory structure
- Version numbers are updated

**Validation**:
```bash
python3 .meta/opencode_tests/test_work_notebook.py
# Should show: ✓ META_HARNESS.md references WORK.md
# Should show: ✓ AGENTS.md references WORK.md
```

---

### Test 4: Safe Space Isolation

**Purpose**: Verify sandbox/experiments don't affect production

**Procedure**:
```bash
# 1. Create test file in sandbox
echo "# Test" > .meta/sandbox/test_isolation.md

# 2. Verify production is unchanged
git status

# 3. Check production files are untouched
ls -la | grep -E "^(src|agentx)" # Should exist
ls -la .meta/sandbox/ # Should have test file
```

**Expected Result**:
- Sandbox files are separate from production
- Git status shows only sandbox changes
- Production code is never modified directly

**Validation**:
```bash
# Production should be clean
git diff --name-only

# Sandbox should have changes
ls .meta/sandbox/test_isolation.md
```

---

### Test 5: Agent Directive Compliance

**Purpose**: Verify agent follows mandatory directives

**Procedure**:
```bash
# 1. Ask agent to perform task
opencode run "Check the project structure"

# 2. Monitor agent behavior:
#    - Does it read WORK.md first?
#    - Does it query KB before code search?
#    - Does it cite sources?
#    - Does it work in sandbox for modifications?
```

**Expected Behavior**:
1. **First**: Read `WORK.md` (session start)
2. **Second**: Query KB for context
3. **Third**: Search code if KB has no answer
4. **Always**: Work in sandbox for modifications
5. **Never**: Modify production without permission

**Validation Checklist**:
- [ ] Agent showed WORK.md at session start
- [ ] Agent queried KB before code operations
- [ ] Agent cited KB sources when available
- [ ] Agent used sandbox for modifications
- [ ] Agent did not commit/push without permission

---

### Test 6: Full Integration Workflow

**Purpose**: End-to-end test of complete workflow

**Procedure**:
```bash
# Step 1: Start new session (simulate)
echo "## Session Test" >> .meta/WORK.md

# Step 2: Ask complex question
opencode run "How does the MainController work with KB?"

# Step 3: Request modification
opencode run "Add a feature to track user sessions in sandbox"

# Step 4: Verify workflow
#    - WORK.md updated?
#    - KB queried?
#    - Sandbox used?
#    - Tests created?
#    - Documentation updated?
```

**Expected Result**:
- WORK.md shows current task
- KB was queried first
- Changes made in sandbox
- Tests in tests_sandbox
- Documentation updated

---

## Quick Test Commands

### Minimal Test (30 seconds)
```bash
# Run all automated tests (recommended)
.meta/opencode_tests/run_all_tests.sh

# Or individual test
python3 .meta/opencode_tests/test_work_notebook.py
```

### Standard Test (2 minutes)
```bash
# 1. Test WORK notebook
python3 .meta/opencode_tests/test_work_notebook.py

# 2. Test KB query
python3 .meta/tools/meta-harness-knowledge-base/kb ask "test" --top-k 1

# 3. Check documentation references
grep -r "WORK.md" META_HARNESS.md AGENTS.md

# 4. Verify sandbox isolation
ls .meta/sandbox/
```

### Comprehensive Test (5 minutes)
```bash
# 1. Run all automated tests
python3 .meta/opencode_tests/test_work_notebook.py

# 2. Test KB-first behavior
opencode run "What is the current work status?"

# 3. Verify all directives in AGENTS.md
grep -E "^\-?[0-9]\." AGENTS.md

# 4. Check quality gates
cat AGENTS.md | grep -A 10 "Quality Gates"

# 5. Test sandbox isolation
echo "# Test" > .meta/sandbox/test.md && git status
```

---

## Test Results Template

After running tests, document results:

```markdown
## Test Results - YYYY-MM-DD

### Environment
- Opencode version: [run: opencode --version]
- KB entries: [run: kb stats]
- WORK.md status: [present/missing]

### Test Results
| Test | Status | Notes |
|------|--------|-------|
| WORK Notebook | ✓/✗ | |
| KB-First Query | ✓/✗ | |
| Documentation | ✓/✗ | |
| Safe Spaces | ✓/✗ | |
| Directive Compliance | ✓/✗ | |
| Full Workflow | ✓/✗ | |

### Issues Found
- [List any failures or unexpected behavior]

### Recommendations
- [Suggested improvements]
```

---

## Common Issues & Solutions

### Issue 1: Agent doesn't query KB first
**Symptom**: Agent searches code before KB query  
**Solution**: 
- Check AGENTS.md has KB-first directive
- Verify KB is populated: `meta kb stats`
- Remind agent: "Query KB first per AGENTS.md"

### Issue 2: WORK.md not displayed
**Symptom**: Agent doesn't show WORK.md at session start  
**Solution**:
- Verify `WORK.md` exists (root folder)
- Check AGENTS.md has directive -1
- Remind agent: "Query KB first per AGENTS.md"
- Run: `cat WORK.md` manually

### Issue 3: Tests fail
**Symptom**: Test suite shows failures  
**Solution**:
- Check file paths are correct
- Verify KB is populated
- Ensure WORK.md has required structure
- Run: `python3 .meta/opencode_tests/test_work_notebook.py --verbose`

### Issue 4: Sandbox not isolated
**Symptom**: Changes appear in production  
**Solution**:
- Verify agent is using `.meta/sandbox/`
- Check git status before changes
- Remind: "Work in sandbox only"

---

## Post-Test Actions

### If All Tests Pass ✓
1. Document successful test in WORK.md
2. Update version in META_HARNESS.md if changed
3. Commit test results to `.meta/reflection/`
4. Clear WORK.md for next task

### If Tests Fail ✗
1. Document failure in `.meta/reflection/test-failures.md`
2. Create fix in `.meta/sandbox/`
3. Re-run tests after fix
4. Update documentation if needed
5. Do NOT commit until tests pass

---

## Automation Script

Create automated test runner:

```bash
#!/bin/bash
# .meta/opencode_tests/run_all_tests.sh

echo "============================================"
echo "META HARNESS ↔ Opencode Integration Test"
echo "============================================"
echo ""

# Test 1: WORK Notebook
echo "[1/6] Testing WORK Notebook..."
python3 .meta/opencode_tests/test_work_notebook.py

# Test 2: KB Status
echo "[2/6] Checking KB status..."
python3 .meta/tools/meta-harness-knowledge-base/kb stats

# Test 3: Documentation
echo "[3/6] Verifying documentation..."
grep -q "WORK.md" META_HARNESS.md && echo "✓ META_HARNESS.md references WORK.md"
grep -q "WORK.md" AGENTS.md && echo "✓ AGENTS.md references WORK.md"

# Test 4: Sandbox Isolation
echo "[4/6] Checking sandbox isolation..."
test -d .meta/sandbox && echo "✓ Sandbox directory exists"

# Test 5: Git Status
echo "[5/6] Git status..."
git status --short

# Test 6: Summary
echo "[6/6] Summary"
echo "============================================"
echo "All automated tests completed"
echo "============================================"
```

---

## Maintenance

### After Each Test Session
- [ ] Clean up test files from sandbox
- [ ] Update WORK.md status
- [ ] Document any issues found
- [ ] Archive test results

### Weekly
- [ ] Review test failures
- [ ] Update test procedures if needed
- [ ] Check for new opencode features
- [ ] Validate KB entries are current

### Monthly
- [ ] Run comprehensive test suite
- [ ] Review and update test procedures
- [ ] Archive old test results
- [ ] Optimize test scripts

---

## References

- [AGENTS.md](../../AGENTS.md) - Agent directives
- [META_HARNESS.md](../../META_HARNESS.md) - Master documentation
- [WORK.md](../../WORK.md) - Current work tracker
- [KB META.md](../knowledge_base/META.md) - Knowledge base documentation
- [WORKFLOWS.md](../project_development/WORKFLOWS.md) - Workflow patterns

---

**Version**: 1.0.0 | **Created**: 2026-05-01  
**Test Status**: ✓ All tests passing  
**Last Updated**: 2026-05-01
