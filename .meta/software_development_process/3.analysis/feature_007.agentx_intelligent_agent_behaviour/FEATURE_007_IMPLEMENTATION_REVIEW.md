# Feature_007 Implementation Review

> Author: AgentX Implementation Review Board
> Date: 2026-07-11 (revised)
> Status: ⚠️ **RE-REVIEWED — NOT shippable as-is**; 3 critical security defects + 1 broken DSL feature must be fixed before merge

## Revision History

| Date       | Author | Change                                                                       |
|------------|--------|------------------------------------------------------------------------------|
| 2026-07-11 | Agent  | Initial review — declared "shippable, zero critical defects" (6 minor issues) |
| 2026-07-11 | Agent  | **Full re-review** — prior assessment was inaccurate. Found 3 CRITICAL/SECURITY issues, 1 broken DSL feature, 13 logic bugs. Prior ISSUE-3 fix is wrong, ISSUE-4 is already fixed, ISSUE-6 is misdiagnosed. See §"Corrections to the Prior Review". |

---

## 🔍 Executive Summary

**Assessment**: The feature_007 implementation has a **solid MVC++ architecture** (0
violations, 169/169 tests pass) but the **prior review's "zero critical defects, shippable"
verdict was incorrect**. A line-by-line re-review of all 43 Python source files (4,862 LOC)
found **3 critical security defects**, **1 broken core feature** (the condition DSL cannot
express subtraction), and **13 logic bugs** with real runtime impact.

The prior review correctly identified the MVC++ compliance, test coverage, and graceful
degradation paths. However it:
1. **Missed 3 critical security issues** — a path-traversal sandbox bypass, a non-functional
   safety deny-list, and a broken arithmetic operator in the policy DSL.
2. **Proposed a wrong fix for ISSUE-3** — `target` is already `.resolve()`d, so
   `str(target.resolve()).startswith(...)` is a no-op; the real bug is that
   `str().startswith()` is a string-prefix check, not path-containment.
3. **Listed ISSUE-4 as an open bug** — the `_dismissed` guard already exists (lines 245,
   482-484); the double-dismiss is already prevented.
4. **Misdiagnosed ISSUE-6** as a "mutation race" — the real defect is that `_promote_next`
   ignores goal priority despite the class docstring promising "priority-based activation".
5. **Rated all 6 issues as minor/theoretical** — at least 2 of them (path traversal, worker
   not joined) are higher severity than claimed.

**Highlights (confirmed accurate)**:
- ✅ Architecture adheres strictly to MVC++ (0 violations — re-verified via `mvc_check.py`)
- ✅ Test suite: 169/169 feature_007 tests pass (re-verified)
- ✅ Abstract Partners are correct — contracts cleanly separate MVC++ components
- ✅ Graceful degradation: sensors, actuators, AI reflection all degrade safely
- ✅ Bug-fix history (34 prior bugs) was genuinely resolved

**Threat profile**: **NOT safe for production** until the 3 critical issues are fixed. The
safety deny-list being non-functional means `FULLY_AUTONOMOUS` mode can auto-apply
dangerous operations that the design explicitly intended to reject.

---

## 📋 Review Scope

| Area                     | Files | LOC   | MVC++ Compliance     |
|--------------------------|-------|-------|----------------------|
| Model                    | 28    | 2,850 | ✅ 0 violations       |
| View                     | 8     | 1,540 | ✅ 0 violations       |
| Controller               | 3     | 351   | ✅ 0 violations       |
| Persistence / Integration| 6     | 661   | ✅ stdlib sqlite3 only |
| Tests                    | 15    | 2,200 | ✅ 169/169 pass       |

**Total**: 43 source files, **4,862 production LOC**, **2,200 test LOC**

**Baseline re-verified**:
- `uv run scripts/omt/mvc_check.py src/agentx/agent/` → ✅ 0 violations
- `uv run pytest tests/features/feature_007.../` → ✅ 169 passed

---

## ✅ Strengths (confirmed)

### 1. Architecture & Correctness
- **Abstract Partners perfect**: Contracts cleanly separate MVC++ components — no implementations leak across the wire
- **"Goalless" Island survivability**: Agent degrades to idle when no goal is active (policy engine selects the NOOP action)
- **"AIless" Island survivability**: When AI service fails, reflection logs a non-fatal message and the agent continues acting
- **Cloudburst resilience**: Policy engine implements deterministic conflict resolution (source→creation→lex)
- **Sandbox safety (intent)**: FileSystemTool intends to guard against path escape; SessionTool blocks invalid snapshot reloads

### 2. Thread Safety (partial)
- **Worker-UI channel**: RunningModal + FastAgentTUIScreen use a thread-safe queue — no widget races in the common path
- **Detachment safety**: sqlite3 connections are opened/closed within the same thread context

### 3. Error Paths & Failure Handling
- **Sensor failure surface**: Failed sensor readings are recorded at confidence=0.0
- **Actuator failure tolerance**: `execute_safely()` wraps in try/except
- **Snapshot deserialization**: Partial snapshots degrade gracefully

---

## 🔧 Corrections to the Prior Review

The prior review listed 6 issues. Here is the status of each after re-verification:

### Prior ISSUE-1: `evict()` uses `elif` instead of `if` — ✅ VALID (kept as CRITICAL-4 below)
**Status**: Confirmed accurate. The `elif` chain at `manager.py:98-105` makes eviction criteria
mutually exclusive. Kept and expanded below.

### Prior ISSUE-2: `resume_session()` uses `add_rule` not `add_rule_safely` — ✅ VALID (kept as HIGH-3)
**Status**: Confirmed accurate. `agent.py:186` bypasses conflict resolution for legacy snapshots.

### Prior ISSUE-3: Path escape check — ❌ WRONG FIX, MISDIAGNOSED SEVERITY (replaced by CRITICAL-1)
**Status**: The prior review said the fix is `str(target.resolve()).startswith(str(root.resolve()))`.
But `target` is **already resolved** at `filesystem_tool.py:85`:
```python
target = (self._root / path).resolve()  # ← already resolved
if not str(target).startswith(str(self._root)):  # ← string-prefix check
```
So `target.resolve()` is a no-op. The **real bug** is that `str().startswith()` is a
**string-prefix** check, not a **path-containment** check. A sibling directory whose name
starts with the sandbox name (e.g. `sandbox_evil`) passes the guard. This is a **CRITICAL**
security defect, not "theoretical". See CRITICAL-1 below.

### Prior ISSUE-4: Double-dismiss race — ✅ ALREADY FIXED (not an open issue)
**Status**: The `_dismissed` guard **already exists**:
- `fast_agent_modals.py:245`: `self._dismissed: bool = False`
- `fast_agent_modals.py:368-369`: `if self._dismissed: return` (in `_poll`)
- `fast_agent_modals.py:482-484`: `if self._dismissed: return; self._dismissed = True` (in `_do_dismiss`)

This issue is already resolved in the current code. The prior review should not have listed it as open.

### Prior ISSUE-5: Worker thread not joined on unmount — ✅ VALID (kept as HIGH-5)
**Status**: Confirmed accurate. `on_unmount` (line 276-283) sets events but does not join
`self._worker`. Kept below.

### Prior ISSUE-6: `_promote_next()` mutation race — ❌ MISDIAGNOSED (replaced by HIGH-1)
**Status**: The prior review described a "diagram-traversal mutation race" with probability
"≈1:10,000 cycles". This is **misdiagnosed**. The `_tree.nodes` dict is **not mutated** during
`_promote_next` (no nodes are added/removed). The **real bug** is that `_promote_next`
**ignores goal priority** — it promotes the first-inserted pending goal (dict iteration order),
not the highest-priority one, despite the class docstring (line 27) promising
"priority-based activation". See HIGH-1 below.

---

## ‼️ Critical / Security Issues

### 🔴 CRITICAL-1: Path-traversal sandbox bypass via string-prefix check
**Files**: `src/agentx/agent/model/tools/filesystem_tool.py:85-87` AND `src/agentx/agent/demo/scenarios.py:193`
**Severity**: CRITICAL (security)
**CWE**: CWE-22 (Path Traversal)

**Fault**: The sandbox escape guard uses `str().startswith()`, which is a **string prefix**
check, not a **path containment** check:
```python
target = (self._root / path).resolve()
if not str(target).startswith(str(self._root)):
    return ValidationResult(valid=False, errors=["path escapes sandbox"])
```
If `sandbox_root` resolves to `/home/user/sandbox`, a path like `../sandbox_evil/secret`
resolves to `/home/user/sandbox_evil/secret`, and
`"/home/user/sandbox_evil/secret".startswith("/home/user/sandbox")` is **`True`** — the guard
passes but the path has escaped the sandbox. Any sibling directory whose name starts with the
sandbox directory name bypasses the guard.

The same pattern is repeated in `scenarios.py:193`.

**Effect**: An agent (or a crafted policy rule / reflection proposal) can read/write/delete
files **outside** the sandbox — the primary security boundary of the agent system.

**Fix**: Use `Path.is_relative_to()` (Python 3.9+) for true path-containment:
```python
target = (self._root / path).resolve()
if not target.is_relative_to(self._root):
    return ValidationResult(valid=False, errors=["path escapes sandbox"])
```
Apply the same fix in `act()` (line 104) and `scenarios.py:193`.

---

### 🔴 CRITICAL-2: Safety deny-list is non-functional
**File**: `src/agentx/agent/model/reflection/safety_evaluator.py:44-48`
**Severity**: CRITICAL (security — safety gate bypass)
**CWE**: CWE-693 (Protection Mechanism Failure)

**Fault**: The `DefaultSafetyEvaluator` builds a deny-list key from `proposal.content.get("op", "")`:
```python
op = proposal.content.get("op", "")
key = f"{proposal.type.value}:{op}"
if key in self.DANGEROUS:
    return ProposalVerdict(ProposalStatus.REJECTED, "deny-listed operation")
```
But the `ProposalRouter`'s apply methods **never set an `"op"` key** for 3 of 4 proposal types:
- `_apply_policy_change` (`proposal_router.py:78-107`): sets `id`, `action_type`, `condition`,
  `parameters`, `target_goal`, `priority`, `enabled` — **no `op`**.
- `_apply_memory_update` (`:109-110`): delegates to `memory.apply_update(content)` — **no `op`**.
- `_apply_goal_adjustment` (`:112-113`): delegates to `goals.apply_adjustment(content)` which
  reads `goal_id`, `priority`, `status` — **no `op`**.

So the deny-list entries `"POLICY_CHANGE:delete"`, `"MEMORY_UPDATE:delete_all"`,
`"GOAL_ADJUSTMENT:abandon_root"`, `"GOAL_ADJUSTMENT:delete"`, `"GOAL_ADJUSTMENT:demote"` can
**never match** — the `op` is always `""`. Only `TOOL_CONFIGURATION` proposals set `op`
(`:116-117`), and only to `"enable"`/`"disable"` (never `"delete"`/`"uninstall"`), so those
entries are also dead.

The entire `DANGEROUS` set is **effectively dead code**. In `FULLY_AUTONOMOUS` mode, every
proposal is auto-approved (line 54-55) regardless of how destructive it is.

**Effect**: The design's safety contract — "dangerous operations are always rejected
regardless of autonomy" — is **not enforced**. A reflection proposal that deletes all
memory, abandons the root goal, or disables all policy rules would be auto-applied.

**Fix**: The safety evaluator must derive `op` from the proposal's **content shape**, not
rely on an untrusted `op` field. Either:
- (a) Have the critique parser / router set `op` consistently for every proposal, and
  validate it in the evaluator; OR
- (b) Make the evaluator inspect content keys directly (e.g. if `content.get("status") ==
  "ABANDONED"` and type is `GOAL_ADJUSTMENT`, treat as `abandon_root`).

Option (b) is safer because it doesn't trust the proposer to self-classify.

---

### 🔴 CRITICAL-3: Condition DSL cannot express subtraction
**File**: `src/agentx/agent/model/policy/rule.py:87`
**Severity**: CRITICAL (broken core feature)

**Fault**: The tokenizer's `NUMBER` pattern allows an optional leading minus:
```python
(?P<NUMBER>-?\d+\.?\d*) |
```
The `NUMBER` alternative appears **before** the `OP` alternative in the regex, so for input
`5-3`, the tokenizer matches `NUMBER(5)` then `NUMBER(-3)` (the `-` is consumed as part of
the number, not as a subtraction operator). The parser then sees two consecutive `NUMBER`
tokens and raises `ConditionCompileError("trailing tokens")`.

**Effect**: Any condition using subtraction fails to compile:
- `goal.priority - 5 > 10` → compile error
- `memory.size - threshold < 0` → compile error

The `Arithmetic` AST node (`:72-76`) and the `_additive` parser rule (`:186-194`) exist
specifically to support `+`/`-`, but subtraction is unreachable due to the tokenizer.

**Fix**: Remove the `-?` from the `NUMBER` pattern and handle unary minus as a prefix
operator in the parser, OR reorder the regex so `OP` (`-`) is tried before `NUMBER` when
the `-` is preceded by a digit/identifier/closing paren. The cleanest fix is to remove
`-?` from `NUMBER` and add a unary-minus production in `_primary` / `_not_expr`.

---

## ⚠️ High-Severity Issues

### HIGH-1: Goal promotion ignores priority (misdiagnosed as ISSUE-6)
**File**: `src/agentx/agent/model/goal/manager.py:84-91`
**Severity**: High (correctness — violates documented contract)

**Fault**: `_promote_next` promotes the **first-inserted** pending goal (dict iteration
order), not the highest-priority one:
```python
def _promote_next(self, completed_id: str) -> None:
    for goal in self._tree.nodes.values():
        if goal.status == GoalStatus.PENDING:
            goal.status = GoalStatus.ACTIVE
            ...
            return
```
The class docstring (line 27) says "AND/OR goal-tree manager with **priority-based
activation**". A priority-10 goal inserted before a priority-90 goal is promoted first.

**Fix**: Sort pending goals by priority (descending) before promoting:
```python
pending = [g for g in self._tree.nodes.values() if g.status == GoalStatus.PENDING]
if pending:
    goal = max(pending, key=lambda g: g.priority)
    goal.status = GoalStatus.ACTIVE
    ...
```

---

### HIGH-2: `start_session()` changes `self.id` without updating subsystems
**File**: `src/agentx/agent/model/agent.py:142-149`
**Severity**: High (data consistency)

**Fault**: `start_session` overwrites `self.id = config.id`, but the subsystems
(`PolicyEngine._agent_id`, `MemoryManager._agent_id`, `GoalManager._agent_id`) were
initialized in `__init__` with the **original** `self.id`. After `start_session`, repository
saves use the **old** agent_id while the facade reports the new id. Data is split across two
agent identities.

**Fix**: Either re-initialize the subsystems with the new id in `start_session`, or propagate
the id change to all subsystems. Alternatively, deprecate `start_session` (it's not called by
any production path — `AgentAdapter` creates a fresh `Agent` per session).

---

### HIGH-3: `resume_session()` bypasses conflict resolution for legacy snapshots
**File**: `src/agentx/agent/model/agent.py:182-186`
**Severity**: High (safety — conflict detection bypassed)

**Fault** (confirmed from prior ISSUE-2): When the repository is empty, legacy snapshot rules
are loaded via `add_rule()` (no conflict check) instead of `add_rule_safely()`:
```python
loaded_rules = self.policy_engine.load_from_repository()
if not loaded_rules:
    for rule_data in snapshot.policy_store:
        rule = _dict_to_rule(rule_data)
        self.policy_engine.add_rule(rule)  # ← bypasses conflict detection
```

**Fix**: Replace `add_rule(rule)` with `add_rule_safely(rule)` (and handle the `False` return).

---

### HIGH-4: `persist()` returns a snapshot_id even on failure
**File**: `src/agentx/agent/model/agent.py:300-304`
**Severity**: High (silent data loss)

**Fault**: When `save_snapshot_with_retry` fails (`ok=False`), the method logs an error but
still returns `snapshot.snapshot_id` as if it succeeded. Callers (e.g.
`AgentController.save_snapshot`) have no way to detect the failure — they receive a valid UUID.

**Fix**: Return `""` or raise on failure; alternatively return `Optional[str]`.

---

### HIGH-5: `RunningModal._worker` not joined on unmount
**File**: `src/agentx/agent/view/tui/fast_agent_modals.py:276-283`
**Severity**: High (concurrency — zombie worker)

**Fault**: `on_unmount` sets `_stop_evt` and `_pause_evt` but does not call
`self._worker.join()`. The worker is a daemon thread, so it won't block process exit, but if
the user opens a new Fast Agent modal quickly, the old worker could still be running
`run_cycle()` concurrently with the new modal's worker — two workers racing on the same
`AgentController._cycle_count` and all agent subsystem state.

**Fix**: Add `self._worker.join(timeout=0.5)` in `on_unmount` after setting the events. If
the worker doesn't exit (stuck in `llm.invoke`), log a warning — it's a daemon so it won't
block exit, but the join prevents the race window.

---

### HIGH-6: No timeout on LLM invocation
**File**: `src/agentx/agent/model/ai_adapter.py:95`
**Severity**: High (availability — unresponsive agent)

**Fault**: `llm.invoke([HumanMessage(content=prompt)])` has no timeout. If the LLM HTTP call
hangs, the calling thread (Fast Agent worker or TUI worker) blocks **indefinitely**. The Stop
button sets `_stop_evt`, but the worker only checks it **between** cycles — a hung LLM call
inside `run_cycle()` cannot be interrupted.

**Fix**: Wrap the invoke in a thread-based timeout (e.g. `concurrent.futures` with a
configurable timeout, default 60s), or use LangChain's per-request timeout if the provider
supports it.

---

### HIGH-7: `resume_session()` clear-then-fail leaves agent empty
**File**: `src/agentx/agent/model/agent.py:166-169`
**Severity**: High (data loss on partial failure)

**Fault**: `resume_session` clears all in-memory state **before** attempting to restore:
```python
self.policy_engine.clear()
self.memory.import_volatile([])
self.reflection_engine.restore_log([])
```
If the subsequent restore fails (corrupted snapshot, deserialization error), the agent is left
**empty** — all pre-existing memory, policies, and reflection log are gone with no rollback.
`AgentAdapter.create_agent` wraps this in try/except but only logs the error.

**Fix**: Restore into temporary buffers, then swap atomically; or snapshot the pre-clear state
and restore it on failure.

---

## 🟡 Medium-Severity Issues

### MED-1: `evict()` criteria use `elif` instead of `if` (prior ISSUE-1, confirmed)
**File**: `src/agentx/agent/model/memory/manager.py:97-105`

The `elif` chain makes criteria mutually exclusive: if `max_age` is set but an entry is
younger than `max_age`, the `tags` criterion is **never checked**. Fix: replace `elif` with
`if` for OR semantics.

### MED-2: AI service never retries after initialization failure
**File**: `src/agentx/agent/model/ai_adapter.py:45-47`

Once `_init_attempted = True` (set before any provider is tried, line 47), all subsequent
`complete()` calls raise immediately — even if the user adds an API key later in the same
session. Fix: reset `_init_attempted = False` on each `complete()` call when `_llm is None`,
or add a `retry_initialization()` method.

### MED-3: `confidence` not capped for contested rules
**File**: `src/agentx/agent/model/policy/evaluator.py:158-164`

`base = winner.priority / 1000.0` has no `min(1.0, ...)` on the contested path (line 164). A
rule with priority 1500 (no bounds validation in `types.py:379`) produces confidence 1.5.
Fix: `return min(1.0, base)` and validate priority bounds in `PolicyRule.__post_init__`.

### MED-4: `_NOOP` shared mutable singleton
**File**: `src/agentx/agent/model/policy/evaluator.py:36`

Module-level `_NOOP = PolicyAction(...)` is returned directly in every no-op decision. Since
`PolicyAction` is a mutable dataclass, any caller that mutates `decision.selected_action.parameters`
corrupts the global default. Fix: return a fresh `PolicyAction(type=ActionType.PAUSE)` copy,
or make `PolicyAction` frozen.

### MED-5: `apply_adjustment` revert doesn't undo promotion side-effect
**File**: `src/agentx/agent/model/goal/manager.py:118-141`

`apply_adjustment` calls `update_status` which may call `_promote_next` (promoting another
goal to ACTIVE). `revert_adjustment` only restores the original goal's priority/status — it
does **not** demote the side-effected goal. Fix: capture and restore the promoted goal's id
in the rollback token.

### MED-6: Policy revert deletes instead of restoring
**File**: `src/agentx/agent/model/reflection/proposal_router.py:46-47` → `evaluator.py:137-139`

`revert_rule` calls `remove_rule(rule_id)`, which **deletes** the rule entirely. If the
proposal was an UPDATE to an existing rule, the revert deletes it instead of restoring the
previous version. Fix: store the previous rule in the rollback token and restore it.

### MED-7: Memory revert fails after consolidation
**File**: `src/agentx/agent/model/memory/manager.py:179-181`

`revert_update` only pops from `_volatile`. If `consolidate()` moved the entry to the
persistent tier before revert, the persistent copy remains. Fix: also delete from the
repository on revert.

### MED-8: `ARCHIVED` tier silently dropped in `store()`
**File**: `src/agentx/agent/model/memory/manager.py:44-51`

No `elif tier == MemoryTier.ARCHIVED:` branch. If `tier` is `ARCHIVED`, the entry's `tier`
field is set but it is **not stored anywhere** — silent data loss.

### MED-9: `retrieve()` can return duplicates
**File**: `src/agentx/agent/model/memory/manager.py:53-56`

Combines volatile + persistent without deduplication by entry ID. An entry in both tiers
appears twice. Fix: dedupe by `entry.id`.

### MED-10: Broad `except Exception` in condition evaluation
**File**: `src/agentx/agent/model/policy/rule.py:383-384`

`CompiledCondition.evaluate` catches **all** exceptions (including `AttributeError`,
`KeyError`, `TypeError`) and returns `False` with no logging. Programming errors in
conditions are silently converted to false negatives, making them extremely hard to debug.
Fix: catch only `ConditionCompileError` + `TypeError`/`ValueError` and log the rest.

### MED-11: Unknown identifiers silently return `None` (contradicts docstring)
**File**: `src/agentx/agent/model/policy/rule.py:285-320`

The module docstring (lines 5-7) says "Unknown identifiers / functions raise
`ConditionCompileError` at load time — fail-fast, never at `decide()` time." But
`compile_condition` only **parses** — it does not validate identifiers. Unknown identifiers
like `foo.bar` compile successfully and silently evaluate to `None` at runtime.

### MED-12: Deserialization errors not caught in repositories
**File**: `src/agentx/agent/persistence/repositories_db.py:241-272, 296`

`json.loads(row["..."] or "{}")` can raise `json.JSONDecodeError` on corrupted data. None of
the `_row_to_*` helpers have try/except. A single corrupted row would crash
`load_by_agent`/`load_tree`, blocking session resume entirely. Fix: wrap deserialization in
try/except, skip/log corrupt rows.

### MED-13: Unbounded reflection log growth
**File**: `src/agentx/agent/model/reflection/engine.py:78`

`self._entries` grows without bound. `pending_proposals()` (line 140-148) iterates the entire
list on every call. Fix: cap the log size (e.g. keep last 1000 entries) or prune applied/rejected proposals.

### MED-14: Snapshots never cleaned up
**File**: `src/agentx/agent/persistence/agent_db.py:65-81`

`save_snapshot` creates a new row every time; old snapshots are never deleted. No retention
policy. Fix: keep last N snapshots per agent, delete older ones on save.

---

## 🔵 Low-Severity / Minor Issues

| # | File | Issue |
|---|------|-------|
| L1 | `policy/conflict_resolver.py:37-42` | `resolve_conflicts()` is a stub — always returns `{}`. Dead code exposed to controllers. |
| L2 | `policy/conflict_resolver.py:65` | `import re` inside a method (should be top-level). |
| L3 | `policy/conflict_resolver.py:68-69` | Keyword exclusion set case-inconsistent: `{"AND","OR","NOT","true","false"}` — `"TRUE"`/`"FALSE"` not excluded. |
| L4 | `policy/conflict_resolver.py:80-93` | Contradiction detection incomplete — misses `SET_GOAL vs PAUSE`, `MODIFY_MEMORY vs PAUSE`, etc. |
| L5 | `tools/discovery.py:35` | `except Exception: continue` swallows all plugin errors with **no logging** (docstring says "logged"). No `logging` import. |
| L6 | `tools/registry.py:81-85` | `get_sensor`/`get_actuator` raise raw `KeyError` — no graceful `None` or custom exception. |
| L7 | `agent.py:425` | Dead code: `if result.success and command is not None:` — `command` is always non-None here (returned `None` at line 408 if None). |
| L8 | `agent.py:458-478` | `start_session` → `_register_builtin_tools` silently ignores `DuplicateToolError`, so `sandbox_root` config changes are ignored. |
| L9 | `goal/manager.py:72-73` | `GoalStatus(status)` raises `ValueError` on invalid string — no try/except. |
| L10 | `reflection/critique_parser.py:82-86` | `float(confidence_raw)` raises `TypeError` on non-numeric non-string values — crashes reflection. |
| L11 | `agent_db.py:55-61` | `upsert_agent` uses `INSERT OR REPLACE` with `_now_iso()` → `created_at` overwritten on every upsert. |
| L12 | `agent_db.py:87-94` | `save_snapshot_with_retry` retries on ALL `sqlite3.Error` — should only retry on `OperationalError` ("database is locked"). |
| L13 | `schema_db.py` | No indexes on `agent_id` columns — full table scans. |
| L14 | `schema_db.py` | No `FOREIGN KEY` constraints — orphaned rows on agent deletion. |
| L15 | `agent_screen.py:407-451` | Multiple `except Exception: pass` — silently swallows all errors with no diagnostic. |
| L16 | `agent_controller.py:229` | Controller reaches into `self._agent.config.sandbox_root` — not on the `IAgentModelPartner` interface. |
| L17 | `agent_controller.py:197` | Grammar: `"Proposal applied"` vs `"Proposal REJECTED"` — inconsistent capitalization. |
| L18 | `interfaces.py` | Pervasive `Any` return types where concrete types exist (`CycleResult`, `GoalTree`, etc.). |

---

## 🚧 Incomplete Features / Stubs

| # | File | Issue |
|---|------|-------|
| S1 | `types.py:264-267` | `EnvironmentModel.memory_pressure` always returns `0.0` — stub. Policy conditions on it always evaluate `False`. |
| S2 | `fast_agent_modals.py:574-576` | `_full_count_hint()` is a placeholder — always equals `len(proposals)`. The "showing first N" branch is dead. |
| S3 | `fast_agent_screen.py:97-99` | Goal constraints captured but never applied: `"Constraints noted (not used in v1)"`. |
| S4 | `fast_agent_screen.py:128-129` | `save_snapshot()` called synchronously on the UI thread — blocks TUI (unlike `AgentTUIScreen` which uses `run_blocking`). |
| S5 | `fast_agent_modals.py:439-443` | Only `self._pending[0]` is approvable — multi-proposal batch approval not supported; causes re-prompt loop. |
| S6 | `agent_screen.py:425-428` | `show_policy_editor` only prints id/priority/enabled — no condition or action (less useful than console view). |
| S7 | `reflection/engine.py:140-148` | Pending proposals never expire — accumulate forever; no dismiss-without-approve. |
| S8 | `fast_agent_screen.py:91-92` | Comment says `kind="manual"` but `SuccessCriteria()` defaults to `kind="always"` — misleading. |

---

## 🎯 Prioritized Fix Plan

### Phase 1 — Critical (must fix before merge)

| ID | Issue | File(s) | Fix LOC | Tests |
|----|-------|---------|---------|-------|
| C1 | Path-traversal bypass → `is_relative_to()` | `filesystem_tool.py:85-87,104`; `scenarios.py:193` | 4 | 3 (sibling-dir escape, symlink, normal path) |
| C2 | Safety deny-list non-functional → derive `op` from content | `safety_evaluator.py:44-48` | 15 | 4 (delete-rule, delete-all-memory, abandon-root, tool-delete all rejected) |
| C3 | DSL subtraction broken → remove `-?` from NUMBER, add unary minus | `rule.py:87,196-229` | 10 | 3 (`5-3>1`, `priority-5>10`, negative literal) |

**Phase 1 total**: ~29 LOC + 10 regression tests

### Phase 2 — High (fix before autonomous deployment)

| ID | Issue | File(s) | Fix LOC | Tests |
|----|-------|---------|---------|-------|
| H1 | Goal promotion ignores priority | `goal/manager.py:84-91` | 5 | 2 |
| H2 | `start_session` agent_id mismatch | `agent.py:142-149` | 8 | 1 |
| H3 | `resume_session` bypasses conflict check | `agent.py:186` | 1 | 1 |
| H4 | `persist()` returns id on failure | `agent.py:300-304` | 3 | 1 |
| H5 | Worker not joined on unmount | `fast_agent_modals.py:276-283` | 3 | 1 |
| H6 | No LLM invoke timeout | `ai_adapter.py:95` | 8 | 1 |
| H7 | `resume_session` clear-then-fail | `agent.py:166-169` | 12 | 1 |

**Phase 2 total**: ~40 LOC + 8 regression tests

### Phase 3 — Medium (batch after critical/high)

| IDs | Issues | Fix LOC | Tests |
|-----|--------|---------|-------|
| M1-M14 | evict elif, AI retry, confidence cap, _NOOP singleton, revert side-effects, ARCHIVED tier, dedup, broad except, unknown idents, deser errors, refl log growth, snapshot cleanup | ~80 | ~14 |

### Phase 4 — Low + Stubs (improvement roadmap)

| IDs | Issues | Fix LOC | Tests |
|-----|--------|---------|-------|
| L1-L18 | Minor polish (logging, imports, grammar, dead code) | ~30 | ~5 |
| S1-S8 | Complete stubs (memory_pressure heuristic, constraints, batch approval, async save) | ~60 | ~8 |

---

## 📈 Improvement Roadmap (beyond fixes)

These are **enhancements**, not bug fixes — proposed for future iterations:

### I1. Connection pooling for persistence
Every repository method opens a **new** `sqlite3.connect()`. Under high-frequency perception
stores (one entry per sensor per cycle), this is slow and risks FD exhaustion. Proposal:
introduce a per-agent connection (thread-local) or a small connection pool.

### I2. Snapshot retention policy
Add `max_snapshots_per_agent` config (default 50). On `save_snapshot`, delete older snapshots
beyond the limit. Prevents unbounded `session_snapshots` table growth.

### I3. Reflection log pruning
Cap `ReflectionEngine._entries` at a configurable limit (default 1000). Prune oldest
`APPLIED`/`REJECTED` entries first; keep `NEEDS_CONFIRMATION` indefinitely. Keeps
`pending_proposals()` O(1) amortized.

### I4. LLM invocation timeout + cancellation
Wrap `llm.invoke()` in a `concurrent.futures.ThreadPoolExecutor` with a configurable timeout
(default 60s). On timeout, surface a `ReflectionEntry` with `critique.confidence = 0.0` and a
"timeout" note. This also makes the Fast Agent Stop button responsive mid-LLM-call.

### I5. Priority bounds validation
Add `__post_init__` to `PolicyRule` validating `0 <= priority <= 1000`. Enforces the
documented range and prevents `confidence > 1.0`.

### I6. GoalTree cycle prevention
`GoalTree.add` should validate that `goal.parent` is not a descendant of `goal` (which would
create a cycle). `get_path`/`get_descendants` currently infinite-loop on cyclic trees.

### I7. Batch proposal approval
The ReflectionModal should support approving/dismissing all pending proposals at once, not
just `self._pending[0]`. This eliminates the re-prompt loop when multiple proposals are pending.

### I8. Async save in FastAgentTUIScreen
`FastAgentTUIScreen._on_result` calls `save_snapshot()` synchronously (line 128-129). Refactor
to use `run_blocking` (the pattern from feature_014) to avoid blocking the UI thread on SQLite I/O.

### I9. Fail-fast identifier validation in DSL
`compile_condition` should validate that all root identifiers (`agent`, `environment`, `goal`,
`memory`, `true`, `false`) and function names (`has_observation`, `goal_is_blocked`,
`memory_contains`) are known at compile time — fulfilling the docstring's "fail-fast, never at
`decide()` time" promise.

### I10. Snapshot integrity verification
Add a checksum/hash column to `session_snapshots`. On `load_snapshot`, verify the hash before
deserializing — detect corruption before it crashes resume.

---

## 🛡️ Verification Baseline (re-confirmed)

| Check | Result |
|-------|--------|
| `uv run scripts/omt/mvc_check.py src/agentx/agent/` | ✅ 0 violations, 45 files |
| `uv run pytest tests/features/feature_007.../` | ✅ 169 passed |
| Prior bug fixes (34 bugs) | ✅ All resolved (re-verified in code) |

> **Note**: All 169 existing tests pass, which means the critical issues are **not covered**
> by the current test suite. The fix plan above includes regression tests for each critical
> issue. The path-traversal bypass (C1) and non-functional deny-list (C2) in particular need
> new tests that prove the security boundary is enforced.

---

## Summary

```diff
- Status: ✅ REVIEWED — shippable, zero critical defects
+ Status: ⚠️ RE-REVIEWED — NOT shippable as-is
+   3 CRITICAL security defects (path traversal, deny-list bypass, broken DSL)
+   7 HIGH-severity logic/concurrency bugs
+   14 MEDIUM issues
+   18 LOW issues + 8 incomplete stubs
+
+  Phase 1 (critical): ~29 LOC + 10 tests — fixes security + broken feature
+  Phase 2 (high):     ~40 LOC + 8 tests  — fixes data consistency + concurrency
+  Phase 3 (medium):   ~80 LOC + 14 tests — batch polish
+  Phase 4 (low/stub): ~90 LOC + 13 tests — improvement roadmap
+
+  Architecture (MVC++ 0 violations) and test coverage (169/169) are genuine strengths.
+  The issues are in implementation correctness, not architecture.
```

| Action | Owner | Effort |
|--------|-------|--------|
| Phase 1 (critical fixes + tests) | Engineering | 1d |
| Phase 2 (high fixes + tests) | Engineering | 1.5d |
| Phase 3 (medium batch) | Engineering | 1d |
| Phase 4 (improvements) | Engineering | 2d |
| Re-review after Phase 1 | Review | 0.5d |
