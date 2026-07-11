# Operation Spec 001 — Changed Operations

> Feature: feature_015.agentx_security_and_quality_hardening
> Date: 2026-07-11

Operation specifications for the key methods changed by this feature (per OMT++ guide §10).

---

## FileSystemTool.validate()

```
Operation: Validate an actuator command's path against the sandbox.

Preconditions:
  - command.parameters["path"] is a non-empty string
  - self._root is a resolved Path

Exceptions:
  - Missing path → ValidationResult(valid=False, errors=["missing 'path' parameter"])
  - Path escapes sandbox (C1: is_relative_to check) → ValidationResult(valid=False, errors=["path escapes sandbox"])
  - Unknown action → ValidationResult(valid=False, errors=["unknown action: {action}"])

Postconditions:
  - Returns ValidationResult(valid=True) only if target is inside self._root
  - No filesystem mutation occurs during validation
```

---

## DefaultSafetyEvaluator.evaluate()

```
Operation: Evaluate a reflection proposal against the safety deny-list and autonomy level.

Preconditions:
  - proposal is a Proposal with type and content
  - ctx is a PolicyContext with autonomy_level

Exceptions:
  - None (never raises; always returns a ProposalVerdict)

Postconditions:
  - Destructive proposals (C2: inferred from content shape) → REJECTED regardless of autonomy
  - SUPERVISED/CONFIRMATION_REQUIRED/MANUAL_ONLY → NEEDS_CONFIRMATION
  - FULLY_AUTONOMOUS + non-destructive → APPROVED
  - The 'op' field is NOT trusted; op is inferred from content keys
```

---

## compile_condition()

```
Operation: Compile a condition DSL string into a validated AST.

Preconditions:
  - expr is a non-empty string

Exceptions:
  - Tokenizer error (unexpected character) → ConditionCompileError
  - Parser error (unexpected token, trailing tokens) → ConditionCompileError
  - Unknown identifier (M11) → ConditionCompileError("unknown identifier: {root}")
  - Unknown function (M11) → ConditionCompileError("unknown function: {name}")

Postconditions:
  - Returns a valid AST node
  - Subtraction expressions (C3: "5-3") compile correctly
  - Unary minus (C3: "-5") compiles to UnaryOp("-", Literal(5))
  - All identifiers are known roots (agent, environment, goal, memory, true, false)
  - All function calls are known (has_observation, goal_is_blocked, memory_contains)
```

---

## GoalManager._promote_next()

```
Operation: Promote the highest-priority pending goal to ACTIVE after one completes.

Preconditions:
  - completed_id is the id of a goal that just reached a terminal status
  - At least one goal may be PENDING

Exceptions:
  - None (silently no-ops if no pending goals)

Postconditions:
  - The PENDING goal with the highest priority is now ACTIVE (H1)
  - Ties broken by insertion order (first-inserted wins)
  - Repository is updated if present
```

---

## Agent.resume_session()

```
Operation: Rebuild the Agent from a persisted snapshot.

Preconditions:
  - snapshot_id refers to a persisted SessionSnapshot
  - Agent may have pre-existing in-memory state

Exceptions:
  - Snapshot not found → FileNotFoundError
  - Snapshot corrupted → state is restored to pre-call state (H7), error re-raised

Postconditions:
  - On success: config, policy rules, goal tree, volatile memory, reflection log restored
  - Policy rules loaded via add_rule_safely (H3: conflict-checked)
  - On failure: pre-existing in-memory state is preserved (H7)
```

---

## Agent.persist()

```
Operation: Persist the current state as a SessionSnapshot.

Preconditions:
  - Agent has in-memory state to persist

Exceptions:
  - SQLite write failure → returns "" (H4: caller detects failure)

Postconditions:
  - On success: returns the snapshot_id; snapshot row exists in DB
  - On failure: returns "" (H4); state is unchanged
  - Old snapshots beyond retention limit are deleted (M14)
```

---

## AIServiceAdapter.complete()

```
Operation: Send a prompt to the LLM with a timeout.

Preconditions:
  - prompt is a non-empty string
  - An AI provider is configured or configurable

Exceptions:
  - No provider available → RuntimeError
  - LLM invocation timeout (>60s) → RuntimeError("LLM invocation timed out") (H6)

Postconditions:
  - Returns the LLM response text
  - No thread blocks indefinitely (H6)
  - Retry is possible after a previous init failure (M2)
```

---

## MemoryManager.retrieve()

```
Operation: Retrieve memory entries matching a query, deduplicated by entry ID.

Preconditions:
  - query is a MemoryQuery

Exceptions:
  - None

Postconditions:
  - Results from volatile + persistent tiers are deduplicated by entry.id (M9)
  - Filters (source, tags, importance, time_range) applied
  - Sorted by importance desc, then recency
  - Limited to query.limit
```

---

## ReflectionEngine (log management)

```
Operation: Manage the reflection log with bounded growth.

Preconditions:
  - Engine has an entries list

Exceptions:
  - None

Postconditions:
  - Log capped at 1000 entries (M13)
  - Pruning removes oldest APPLIED/REJECTED entries first
  - NEEDS_CONFIRMATION proposals are never pruned
  - Old NEEDS_CONFIRMATION proposals can be expired via expire_old_proposals() (S7)
```
