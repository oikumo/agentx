# Analysis 002 — Use Cases & Operations

> Feature: feature_015.agentx_security_and_quality_hardening
> Date: 2026-07-11

This feature is a hardening/bugfix feature — it does not add new user-facing screens or
commands. The "use cases" below describe the **behaviors that must work correctly after
the fixes**. They are derived from the design intent of feature_007, not from new user
requirements.

---

## Use Case UC-1: Sandboxed filesystem access cannot escape the sandbox

**Actor**: Agent (autonomous or supervised) / Policy rule / Reflection proposal

**Preconditions**: Agent is initialized with a `sandbox_root` directory.

**Main flow**:
1. Agent decides to read/write/delete a file via `FileSystemTool`
2. The file path includes a relative traversal (`../sibling_dir/file`)
3. `FileSystemTool.validate()` rejects the path with "path escapes sandbox"
4. No file outside `sandbox_root` is touched

**Postconditions**: No file outside `sandbox_root` is read, written, or deleted.

**Covers**: CRITICAL-1

---

## Use Case UC-2: Dangerous reflection proposals are always rejected

**Actor**: ReflectionEngine (autonomous mode)

**Preconditions**: Agent is in `FULLY_AUTONOMOUS` mode; reflection produces a proposal
that deletes all memory, abandons the root goal, or disables all policy rules.

**Main flow**:
1. AI critique produces a proposal with destructive intent (e.g. `MEMORY_UPDATE` with
   `delete_all`, `GOAL_ADJUSTMENT` with `abandon_root`)
2. `DefaultSafetyEvaluator.evaluate()` inspects the proposal's content shape
3. The evaluator recognizes the destructive operation regardless of the `op` field
4. The proposal is rejected with `ProposalStatus.REJECTED` ("deny-listed operation")
5. The proposal is not routed to any subsystem

**Postconditions**: Destructive proposals are never auto-applied, even in FULLY_AUTONOMOUS.

**Covers**: CRITICAL-2

---

## Use Case UC-3: Policy DSL supports subtraction expressions

**Actor**: User / ReflectionEngine (policy rule author)

**Preconditions**: A policy rule condition uses subtraction, e.g. `goal.priority - 5 > 10`.

**Main flow**:
1. `PolicyEngine.add_rule(rule)` compiles the condition
2. `compile_condition("goal.priority - 5 > 10")` produces a valid AST:
   `Comparison(">", Arithmetic("-", Identifier(["goal","priority"]), Literal(5)), Literal(10))`
3. At evaluation time, the expression evaluates correctly

**Postconditions**: Subtraction conditions compile and evaluate without error.

**Covers**: CRITICAL-3

---

## Use Case UC-4: Goal promotion respects priority

**Actor**: Agent cycle (perceive → decide → act → reflect)

**Preconditions**: Two goals are PENDING: goal_A (priority=10) and goal_B (priority=90).
goal_A was inserted first.

**Main flow**:
1. The active goal completes → `_promote_next` is called
2. `_promote_next` selects goal_B (priority 90) over goal_A (priority 10)
3. goal_B becomes ACTIVE

**Postconditions**: The highest-priority pending goal is promoted, not the first-inserted.

**Covers**: HIGH-1

---

## Use Case UC-5: Session resume is atomic (no data loss on failure)

**Actor**: User (resume a saved session)

**Preconditions**: Agent has in-memory state (policies, memory, reflection log). A snapshot
exists but is corrupted.

**Main flow**:
1. `resume_session(corrupted_snapshot_id)` is called
2. The restore attempt fails (deserialization error)
3. The agent's pre-existing in-memory state is **restored** (not lost)
4. An error is surfaced to the caller

**Postconditions**: Agent state is unchanged if resume fails.

**Covers**: HIGH-7, MED-12

---

## Use Case UC-6: Persist failure is detectable

**Actor**: AgentController / FastAgentTUIScreen

**Preconditions**: SQLite write fails (disk full, locked).

**Main flow**:
1. `Agent.persist()` calls `save_snapshot_with_retry` → returns `False`
2. `persist()` returns `""` (empty string)
3. Caller detects the empty string and shows an error to the user

**Postconditions**: Caller can distinguish success from failure.

**Covers**: HIGH-4

---

## Use Case UC-7: LLM invocation does not hang indefinitely

**Actor**: Agent reflection cycle (Fast Agent worker thread)

**Preconditions**: LLM HTTP call hangs.

**Main flow**:
1. `AIServiceAdapter.complete(prompt)` wraps `llm.invoke()` in a timeout
2. After 60s, the timeout fires
3. `complete()` raises `TimeoutError`
4. `ReflectionEngine` catches it and produces a low-confidence "AI timeout" entry
5. The agent cycle continues (does not block forever)

**Postconditions**: No thread blocks indefinitely on LLM calls.

**Covers**: HIGH-6

---

## Use Case UC-8: Fast Agent worker is cleaned up on dismiss

**Actor**: User (dismisses Fast Agent modal, immediately re-opens it)

**Preconditions**: RunningModal worker is mid-`run_cycle()`.

**Main flow**:
1. User presses Stop → `on_unmount` sets `_stop_evt`, `_pause_evt`
2. `on_unmount` calls `self._worker.join(timeout=0.5)`
3. The worker exits (or is logged as stuck)
4. User immediately opens a new Fast Agent modal
5. No two workers race on the same controller state

**Postconditions**: Old worker is joined before new one starts.

**Covers**: HIGH-5

---

## Use Case UC-9: Memory operations are correct and bounded

**Actor**: Agent cycle (memory store/retrieve/evict/consolidate/revert)

**Preconditions**: Agent is running multiple cycles with memory operations.

**Main flow**:
1. `evict()` with multiple criteria evicts entries matching ANY criterion (OR semantics)
2. `retrieve()` returns no duplicates (dedup by entry.id)
3. `store()` with `ARCHIVED` tier persists the entry
4. `revert_update()` removes the entry from both volatile and persistent tiers
5. `_NOOP` action cannot be corrupted by mutation

**Postconditions**: Memory operations are correct, bounded, and idempotent.

**Covers**: MED-1, MED-4, MED-7, MED-8, MED-9

---

## Use Case UC-10: Condition DSL fails fast on unknown identifiers

**Actor**: User / ReflectionEngine (policy rule author)

**Preconditions**: A policy rule condition references an unknown identifier, e.g. `foo.bar > 5`.

**Main flow**:
1. `PolicyEngine.add_rule(rule)` compiles the condition
2. `compile_condition("foo.bar > 5")` raises `ConditionCompileError("unknown identifier: foo")`
3. The rule is not added (or `add_rule_safely` returns `False`)
4. The error is logged with context

**Postconditions**: Unknown identifiers are caught at compile time, not silently at runtime.

**Covers**: MED-10, MED-11

---

## Use Case UC-11: System resources are bounded

**Actor**: Agent running long autonomous sessions

**Preconditions**: Agent runs 1000+ cycles.

**Main flow**:
1. Reflection log caps at 1000 entries (oldest APPLIED/REJECTED pruned first)
2. Snapshots are retained (last 50 per agent); older ones deleted on save
3. `upsert_agent` does not overwrite `created_at` on re-save

**Postconditions**: Database and memory growth is bounded.

**Covers**: MED-13, MED-14, L11

---

## Operations List

The following operations (controller/model methods) are changed or added by this feature.
Detailed specs are in `operation_spec_001_changed_operations.md`.

| Operation | Owner | Change |
|-----------|-------|--------|
| `FileSystemTool.validate()` | Model | Fix path-containment check (C1) |
| `FileSystemTool.act()` | Model | Re-check path containment (C1) |
| `seed_sandbox_files()` | Model (demo) | Fix path-containment check (C1) |
| `DefaultSafetyEvaluator.evaluate()` | Model | Derive `op` from content shape (C2) |
| `compile_condition()` / tokenizer | Model | Fix subtraction (C3) |
| `GoalManager._promote_next()` | Model | Sort by priority (H1) |
| `Agent.start_session()` | Model | Propagate id to subsystems (H2) |
| `Agent.resume_session()` | Model | Use `add_rule_safely` (H3); atomic restore (H7) |
| `Agent.persist()` | Model | Return `""` on failure (H4) |
| `RunningModal.on_unmount()` | View | Join worker (H5) |
| `AIServiceAdapter.complete()` | Model | Timeout (H6) |
| `MemoryManager.evict()` | Model | `if` not `elif` (M1) |
| `MemoryManager.store()` | Model | ARCHIVED tier (M8) |
| `MemoryManager.retrieve()` | Model | Dedup (M9) |
| `MemoryManager.revert_update()` | Model | Also delete from repo (M7) |
| `PolicyEngine._confidence()` | Model | Cap at 1.0 (M3) |
| `PolicyEngine.revert_rule()` | Model | Restore previous rule (M6) |
| `PolicyRule.__post_init__` | Model | Priority bounds (M3) |
| `CompiledCondition.evaluate()` | Model | Narrow exception (M10) |
| `compile_condition()` | Model | Validate identifiers (M11) |
| `ReflectionEngine` | Model | Log cap (M13) |
| `SessionDatabase.save_snapshot()` | Model | Retention policy (M14) |
| Repository `_row_to_*` helpers | Model | Catch deser errors (M12) |
| `GoalManager.apply_adjustment/revert` | Model | Capture promotion side-effect (M5) |
| `AIServiceAdapter._ensure_llm()` | Model | Retry init (M2) |
| `ConflictResolver` | Model | Fix stub, import, case, contradictions (L1-L4) |
| `discover_tools()` | Model | Add logging (L5) |
| `ToolRegistry.get_sensor/actuator` | Model | Custom exception (L6) |
| `Agent.act()` | Model | Remove dead code (L7) |
| `Agent._register_builtin_tools` | Model | Force-re-register on config change (L8) |
| `GoalManager.update_status` | Model | Catch invalid enum (L9) |
| `CritiqueParser._parse_critique` | Model | Catch TypeError (L10) |
| `SessionDatabase.upsert_agent` | Model | Preserve created_at (L11) |
| `SessionDatabase.save_snapshot_with_retry` | Model | Only retry OperationalError (L12) |
| `schema_db.py` | Model | Add indexes + FKs (L13, L14) |
| `AgentTUIScreen` | View | Remove broad except (L15) |
| `AgentController.load_demo_scenario` | Controller | Use interface for sandbox_root (L16) |
| `AgentController.approve_proposal` | Controller | Fix grammar (L17) |
| `interfaces.py` | Model | Tighten return types (L18) |
| `EnvironmentModel.memory_pressure` | Model | Heuristic (S1) |
| `ReflectionModal` | View | Batch approval (S5) |
| `FastAgentTUIScreen._on_result` | View | Async save (S4) |
| `AgentTUIScreen.show_policy_editor` | View | Show condition+action (S6) |
| `ReflectionEngine` | Model | Expire old proposals (S7) |
| `FastAgentTUIScreen._on_goal` | View | Fix SuccessCriteria kind (S8) |
