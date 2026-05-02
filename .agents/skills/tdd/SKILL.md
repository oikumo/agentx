---
name: tdd
description: >
  Start a small feature development following TDD rules as defined by Kent Beck.
  Implements RED → GREEN → REFACTOR cycle with associated quality practices.
version: 1.0.0
author: agentx
---

# TDD (Test-Driven Development)

Implement features using Test-Driven Development methodology as defined by Kent Beck. This skill guides you through the RED → GREEN → REFACTOR cycle with strict quality gates.

## Quick Start

**Load**: `skill tdd`
**Time**: 1-3 hours per feature
**Outcome**: Working feature with comprehensive test coverage

## Core Philosophy

TDD is not just about testing — it's about **design**. As Kent Beck says:

> "Test-Driven Development is about taking the information you learn from tests and using it to drive the design of your system."

### The Three Rules of TDD

1. **RED**: Write a failing test BEFORE any production code
2. **GREEN**: Write the minimum code to make the test pass
3. **REFACTOR**: Clean up while keeping all tests green

### TDD Mantras

- "Red/Green/Refactor" — The core cycle
- "Fake it till you make it" — Start simple, evolve complexity
- "Once and only once" — Eliminate duplication
- "Tell, don't ask" — Object-oriented design principle

## When to Use

### ✅ Ideal For TDD

- New feature development
- Bug fixes (write test that reproduces bug first)
- Learning unfamiliar codebases
- Improving code quality
- Building confidence in changes

### ❌ Not Suitable For

- UI/visual design work
- Exploratory prototypes (use `.meta/experiments/` instead)
- One-off scripts
- Performance tuning (test after implementation)

## Workflow (TDD Cycle)

### Step 1: Load Skill

```bash
skill tdd
```

### Step 2: Query Knowledge Base (MANDATORY)

Before starting, check if pattern exists:

```bash
meta kb ask "<feature> implementation patterns"
```

If KB is empty, populate it first:
```bash
meta kb populate
```

### Step 3: RED Phase — Write Failing Test

**Location**: `.meta/tests_sandbox/<date>-<feature>/test_<feature>.py`

Write the SMALLEST failing test:

```python
# test_feature.py
def test_should_do_something():
    """Test one specific behavior"""
    # Arrange - set up preconditions
    # Act - perform action  
    # Result - assert expected outcome
    assert actual == expected
```

**RED Phase Rules:**
- Write ONE test at a time
- Test must fail (RED)
- Failure must be meaningful (not syntax error)
- Test name describes the behavior
- Use AAA pattern (Arrange-Act-Assert)

**Example RED Test:**
```python
# test_calculator.py
def test_add_two_numbers():
    """Should add two positive numbers correctly"""
    # Arrange
    calc = Calculator()
    
    # Act
    result = calc.add(2, 3)
    
    # Assert
    assert result == 5
```

### Step 4: GREEN Phase — Implement Minimum Code

**Location**: `.meta/sandbox/<feature>/`

Write the MINIMUM code to pass the test:

```python
# calculator.py
class Calculator:
    def add(self, a, b):
        return 5  # Fake it - just pass the test
```

**GREEN Phase Rules:**
- Write code ONLY for current test
- Don't anticipate future tests
- "Fake it" if needed (return constants)
- Run test immediately after changes
- Stop when test passes (GREEN)

**GREEN means:**
- ✅ Test passes
- ✅ No new failures
- ✅ Code compiles/runs

### Step 5: REFACTOR Phase — Clean Up

With all tests GREEN, improve the code:

```python
# calculator.py
class Calculator:
    def add(self, a, b):
        return a + b  # Real implementation
```

**REFACTOR Phase Rules:**
- ALL tests must stay GREEN
- Remove duplication (yours and mine)
- Improve names
- Extract methods/classes
- Apply SOLID principles
- One refactoring at a time

**Refactoring Checklist:**
- [ ] Remove code duplication
- [ ] Improve variable/function names
- [ ] Extract repeated patterns
- [ ] Apply design patterns if appropriate
- [ ] Check for null safety
- [ ] Verify error handling

### Step 6: Repeat Cycle

```
RED (new test) → GREEN (implement) → REFACTOR (clean)
           ↓
    Next test case
           ↓
    Repeat until feature complete
```

### Step 7: Document in Knowledge Base

After completing feature, add to KB:

```bash
meta kb add "TDD session: <feature> - <key learnings>"
```

Query to verify:
```bash
meta kb ask "<feature> patterns"
```

## TDD Session Structure

### Directory Layout

```
.meta/
├── tests_sandbox/
│   ├── META.md
│   └── 2026-05-02-calculator/
│       ├── test_calculator.py      # Test file
│       └── session.log             # Session log (optional)
├── sandbox/
│   └── calculator/
│       ├── calculator.py           # Implementation
│       └── README                  # Feature info
└── knowledge_base/
    ├── META.md
    └── entries/
        └── <timestamp>-calculator.md  # KB entry
```

### Session Log Format (in KB)

After session, record in KB:

```
Feature: Calculator - Basic arithmetic
Date: 2026-05-02
TDD Cycles: 5

Test Cases (RED → GREEN → REFACTOR):

Cycle 1: Add two positive numbers
- RED: test_add_two_numbers() - FAIL ✓
- GREEN: Return constant 5 - PASS ✓
- REFACTOR: Implement real addition - PASS ✓

Cycle 2: Add negative numbers
- RED: test_add_negative_numbers() - FAIL ✓
- GREEN: Handle negative values - PASS ✓
- REFACTOR: No changes needed - PASS ✓

Cycle 3: Add zero
- RED: test_add_zero() - FAIL ✓
- GREEN: Handle zero case - PASS ✓
- REFACTOR: Simplify logic - PASS ✓

Patterns Discovered:
- Use AAA pattern consistently
- Test edge cases early
- Name tests descriptively

Code Quality Metrics:
- Test coverage: 100%
- Duplication: 0%
- Complexity: Low
```

## Quality Gates

### RED Phase Quality

| Criteria | Pass | Fail |
|----------|------|------|
| Test written first | ✓ | ✗ |
| Test fails meaningfully | ✓ | ✗ |
| Test describes behavior | ✓ | ✗ |
| One assertion per test | ✓ | ✗ |

### GREEN Phase Quality

| Criteria | Pass | Fail |
|----------|------|------|
| Minimum code written | ✓ | ✗ |
| No over-engineering | ✓ | ✗ |
| Test passes | ✓ | ✗ |
| No new failures | ✓ | ✗ |

### REFACTOR Phase Quality

| Criteria | Pass | Fail |
|----------|------|------|
| All tests still green | ✓ | ✗ |
| Duplication removed | ✓ | ✗ |
| Names improved | ✓ | ✗ |
| Code simpler | ✓ | ✗ |

## Kent Beck's TDD Principles

### 1. The Four Rules of Simple Design

1. **Runs all tests** — System must pass all tests
2. **Reveals intent** — Code clearly expresses purpose
3. **No duplication** — Once and only once (OAOO)
4. **Fewest elements** — Minimal complexity

### 2. TDD is Design

> "TDD is not about testing. TDD is about design."

- Tests drive the design
- Design emerges from tests
- Refactoring improves design

### 3. Test-First Programming

- Write test BEFORE code
- Test defines the interface
- Implementation follows test

### 4. Economic Value of TDD

- Catches bugs early (cheaper to fix)
- Documents expected behavior
- Enables confident refactoring
- Reduces debugging time

## Best Practices

### Writing Good Tests

✅ **DO:**
- Use descriptive names: `test_should_add_two_positive_numbers()`
- Follow AAA pattern (Arrange-Act-Assert)
- Test one thing per test
- Use meaningful variable names
- Keep tests independent
- Test edge cases

❌ **DON'T:**
- Test multiple behaviors in one test
- Use vague names: `test1()`, `test_stuff()`
- Create test dependencies
- Skip the RED phase
- Write tests after code

### Managing the Cycle

**Keep cycles short:**
- RED: 1-5 minutes
- GREEN: 1-10 minutes
- REFACTOR: 1-5 minutes

**If cycle takes longer:**
- Break test into smaller pieces
- Simplify the test case
- Don't anticipate future complexity

### Test Organization

```python
# Group related tests
class TestCalculator:
    """Tests for Calculator.add()"""
    
    def test_add_two_positive_numbers(self):
        pass
    
    def test_add_positive_and_negative(self):
        pass
    
    def test_add_zeros(self):
        pass

# Use fixtures for setup
@pytest.fixture
def calculator():
    return Calculator()

def test_add(calculator):
    assert calculator.add(2, 2) == 4
```

## Common Patterns

### Pattern 1: Triangulation

When unsure of implementation:

1. Write test for specific case → GREEN
2. Write test for another case → RED
3. Generalize implementation → GREEN
4. Repeat

```python
# Test 1: Specific case
def test_add_2_and_3():
    assert calc.add(2, 3) == 5

# Test 2: Another case (forces generalization)
def test_add_1_and_1():
    assert calc.add(1, 1) == 2
```

### Pattern 2: Fake It Till You Make It

```python
# Test: Should return sum of 2 and 3
# GREEN 1: Return constant
def add(a, b):
    return 5

# Test 2: Add 1 and 1 (expects 2)
# GREEN 2: Still fake
def add(a, b):
    if a == 1 and b == 1:
        return 2
    return 5

# Test 3: Force real implementation
# GREEN 3: Real code
def add(a, b):
    return a + b
```

### Pattern 3: Transform-by-Expansion

```python
# Test: Return constant
# Code: return 5

# Test: Return different constant
# Code: return 7

# Test: Add two numbers
# Code: return a + b  # Generalized
```

## Integration with META HARNESS

### Knowledge Base Commands

**Query before starting:**
```bash
meta kb ask "<feature> patterns"
```

**Add after completion:**
```bash
meta kb add "TDD: <feature> - <summary>"
```

**Verify entry:**
```bash
meta kb ask "<feature> implementation"
```

### With Other Skills

- `python-static-analysis` — Run static analysis after GREEN
- `meta-health-check` — Verify TDD process health
- `meta-archive-experiments` — Archive completed TDD sessions

### With Tools

- `pytest` — Test runner
- `unittest` — Built-in Python testing
- `coverage` — Measure test coverage

## Troubleshooting

### Problem: Test won't fail (RED phase)

**Causes:**
- Test has bug
- Implementation already exists
- Test doesn't assert anything

**Solution:**
- Verify test assertions
- Check if feature already implemented
- Make test more specific

### Problem: Can't make test pass (GREEN phase)

**Causes:**
- Test too complex
- Missing dependencies
- Unclear requirements

**Solution:**
- Simplify the test
- Break into smaller tests
- Clarify requirements

### Problem: Refactoring breaks tests

**Causes:**
- Refactoring changed behavior
- Tests too coupled to implementation

**Solution:**
- Revert changes
- Refactor in smaller steps
- Test behavior, not implementation

## Resources

### Books by Kent Beck

- "Test-Driven Development: By Example" (2002)
- "Extreme Programming Explained" (1999)
- "Implementation Patterns" (2007)

### Key Concepts

- **Red/Green/Refactor** — The core TDD cycle
- **Simple Design** — Four rules of simplicity
- **Refactoring** — Improving design without changing behavior
- **Emergent Design** — Design that emerges from TDD

### Online Resources

- Kent Beck's Twitter: @KentBeck
- TDD Wikipedia: https://en.wikipedia.org/wiki/Test-driven_development
- Python pytest: https://docs.pytest.org/

## Version History

- **1.0.0** (2026-05-02): Initial version with complete TDD workflow, Kent Beck principles, quality gates, and KB META HARNESS integration

---

**Maintained by**: agentx  
**Methodology**: Kent Beck TDD  
**Target**: Small feature development with test-first approach
