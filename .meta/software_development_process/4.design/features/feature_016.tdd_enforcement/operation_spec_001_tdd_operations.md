# Operation Specifications — feature_016: TDD Enforcement

> Spec: `.meta/doc/tdd/tdd-agent-spec.md`

---

## 1. omt_testlist

```
Operation: Record the test list (behaviors to implement).

Preconditions:
  - Agent is in Programming phase with tdd_mode active
  - No TDD cycle currently in progress (state is "none" or "done")

Parameters:
  - behaviors: list[str] — behavior descriptions to implement

Exceptions:
  - TDD mode not active → "TDD mode is not active. Call omt_phase{...,tdd:true} first."
  - TDD cycle in progress → "Cannot set test list while in RED/GREEN/REFACTOR state."

Postconditions:
  - Ledger records {kind:"tdd_testlist", behaviors, remaining, feature}
  - TDD state set to TESTLIST
  - src/ and tests/ both BLOCKED (planning only)
```

## 2. omt_red

```
Operation: Declare a failing test (TDD Red state).

Preconditions:
  - TDD mode active
  - State is TESTLIST, GREEN, or REFACTOR (not RED or DONE)
  - Test file exists and contains the test function

Parameters:
  - test_node: str — pytest node ID (e.g. "tests/test_foo.py::test_bar")
  - target_src: str (optional) — source file being tested (auto-inferred if omitted)

Exceptions:
  - State is GREEN → "Call omt_refactor or omt_red for next behavior first."
  - pytest exit == 0 → "Test already passes. Fix the test or remove this cycle."
  - pytest exit == 2/3/4 → "pytest error. Check the test node ID."

Postconditions:
  - Ledger records {kind:"tdd", state:"red", test_node, target_src, verified, exit_code}
  - TDD state set to RED
  - src/ BLOCKED, tests/ ALLOWED (test hat)
  - If target_src inferred: teaching message includes inferred targets
  - If true RED: message includes missing references
```

## 3. omt_green

```
Operation: Declare passing test (TDD Green state).

Preconditions:
  - TDD mode active
  - State is RED (must have a failing test first)

Parameters:
  - test_node: str — pytest node ID (must match the current RED cycle)

Exceptions:
  - State is not RED → "Call omt_red first to write a failing test."
  - pytest exit != 0 → "Test still fails. Write more production code (L3: min-to-pass)."

Postconditions:
  - Ledger records {kind:"tdd", state:"green", test_node, verified, exit_code}
  - TDD state set to GREEN
  - src/ ALLOWED (code hat), tests/ BLOCKED
  - Source snapshot saved to .meta/.omt/tdd_snapshots/<stem>.json
  - If law 3 violations detected: advisory warning (new methods not in test refs)
```

## 4. omt_refactor

```
Operation: Declare refactor state (TDD Refactor).

Preconditions:
  - TDD mode active
  - State is GREEN (must have passing tests first)

Parameters:
  - test_node: str — pytest node ID (must match the current GREEN cycle)

Exceptions:
  - State is not GREEN → "Call omt_green first to get tests passing."
  - pytest exit != 0 → "Tests are failing. Fix before refactoring."

Postconditions:
  - Ledger records {kind:"tdd", state:"refactor", test_node, verified, exit_code}
  - TDD state set to REFACTOR
  - src/ ALLOWED (refactor hat), tests/ BLOCKED
  - Each subsequent src/ edit triggers pytest verification (after-edit hook)
  - If pytest fails after edit: edit auto-reverted, state stays REFACTOR
```

## 5. omt_done

```
Operation: Declare completion (TDD Done).

Preconditions:
  - TDD mode active
  - State is GREEN or REFACTOR (not RED — can't finish mid-cycle)
  - Test list empty (all behaviors implemented)

Parameters:
  - feature: str — feature slug

Exceptions:
  - Test list not empty → "Test list has N remaining behaviors. Continue with omt_red."
  - Full suite fails → "Suite has failures. Fix before declaring done."
  - Coverage gaps → "N untested public methods. Write tests or omt_skip."

Postconditions:
  - Ledger records {kind:"tdd", state:"done", feature, checklist}
  - TDD state set to DONE
  - src/ and tests/ BLOCKED
  - Phase exit unblocked (omt_complete can proceed)
```

## 6. gate (internal, called by enforcer hook)

```
Operation: Should this file edit be allowed under current TDD state?

Preconditions:
  - Called from tool.execute.before for src/ or tests/ paths
  - TDD mode active (enforcer checks tdd_mode flag first)

Parameters:
  - path: str — file path being edited
  - session: str — session ID
  - is_tests: bool — is this a tests/ file?

Postconditions:
  - Returns {allowed, reason, state, tdd_mode, warning?}
  - No ledger write (read-only)
  - No pytest, no AST (fast path, <100ms)
```

## 7. after-edit (internal, called by enforcer hook)

```
Operation: Post-edit TDD verification and advisory.

Preconditions:
  - Called from tool.execute.after for src/ paths
  - TDD mode active

Parameters:
  - path: str — file path that was edited
  - session: str — session ID

Postconditions:
  - REFACTOR state: runs pytest on current test_node
    - If fails → reverts file, returns {action:"reverted", reason}
    - If passes → returns {action:"ok"}
  - GREEN state: AST law 3 check → advisory warnings
  - Other states: no-op
```

## 8. validate-exit (internal, called by omt_complete)

```
Operation: Full TDD validation for phase exit.

Preconditions:
  - Called from omt_complete before advancing Programming → Testing

Parameters:
  - feature: str — feature slug

Postconditions:
  - AST scan: coverage gaps, partner gaps, orphan tests
  - Ledger scan: dangling reds (red without matching green)
  - Returns {ok, dangling_reds, coverage_gaps, partner_gaps, orphan_tests, summary}
  - If !ok → omt_complete blocks phase exit
```
