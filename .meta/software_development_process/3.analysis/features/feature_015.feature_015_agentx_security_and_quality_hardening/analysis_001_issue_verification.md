# Analysis 001 — Issue Verification & Scope

> Feature: feature_015.agentx_security_and_quality_hardening
> Date: 2026-07-11
> Source: `FEATURE_007_IMPLEMENTATION_REVIEW.md` (3.analysis/feature_007.../)
> Method: line-by-line re-verification of all 43 Python source files against the review

---

## 1. Verification Method

Each issue listed in the review was verified by reading the actual source code and
confirming the fault exists at the stated line numbers. Below is the verified catalog,
organized by severity. Every entry includes:

- **ID** — matches the review's issue identifier
- **File:line** — verified source location
- **Fault** — one-sentence description (confirmed against code)
- **Fix approach** — high-level (detailed in design_001)
- **Verified** — ✅ confirmed / ❌ not confirmed (none were ❌)

---

## 2. Critical Issues (3) — Security / Broken Feature

### CRITICAL-1: Path-traversal sandbox bypass via string-prefix check
- **Files**: `src/agentx/agent/model/tools/filesystem_tool.py:86` AND `src/agentx/agent/demo/scenarios.py:193`
- **Fault**: `str(target).startswith(str(self._root))` is a string-prefix check, not path-containment. A sibling directory whose name starts with the sandbox name (e.g. `sandbox_evil`) passes the guard.
- **Fix**: Use `Path.is_relative_to()` (Python 3.9+) in both locations.
- **Verified**: ✅ — `filesystem_tool.py:86` and `scenarios.py:193` both use `str().startswith()`.

### CRITICAL-2: Safety deny-list is non-functional
- **File**: `src/agentx/agent/model/reflection/safety_evaluator.py:45-47`
- **Fault**: The deny-list key is `f"{proposal.type.value}:{proposal.content.get('op', '')}"`, but `op` is never set in proposal content for POLICY_CHANGE, MEMORY_UPDATE, or GOAL_ADJUSTMENT proposals (only TOOL_CONFIGURATION sets `op`, and only to `enable`/`disable`). The entire `DANGEROUS` set is dead code.
- **Fix**: Derive `op` from the proposal's content shape, not an untrusted `op` field. Inspect content keys directly (e.g. `content.get("status") == "ABANDONED"` for GOAL_ADJUSTMENT).
- **Verified**: ✅ — `proposal_router.py` `_apply_policy_change` (lines 78-107), `_apply_memory_update` (109-110), `_apply_goal_adjustment` (112-113) never set `op`. Only `_apply_tool_config` (115-125) sets `op`.

### CRITICAL-3: Condition DSL cannot express subtraction
- **File**: `src/agentx/agent/model/policy/rule.py:87`
- **Fault**: The tokenizer's `NUMBER` pattern `(?P<NUMBER>-?\d+\.?\d*)` appears before `OP` in the regex. For input `5-3`, the tokenizer matches `NUMBER(5)` then `NUMBER(-3)` (the `-` is consumed as part of the number). The parser sees two consecutive NUMBER tokens → `ConditionCompileError("trailing tokens")`.
- **Fix**: Remove `-?` from the `NUMBER` pattern. Add a unary-minus production in `_primary()` / `_not_expr()`.
- **Verified**: ✅ — `rule.py:87` has `-?` in NUMBER. The `_additive` parser (lines 186-194) handles `+`/`-` as binary ops, but the tokenizer never produces a standalone `-` OP token after a NUMBER.

---

## 3. High-Severity Issues (7) — Data Consistency / Concurrency

### HIGH-1: Goal promotion ignores priority
- **File**: `src/agentx/agent/model/goal/manager.py:84-91`
- **Fault**: `_promote_next` iterates `self._tree.nodes.values()` in dict insertion order and promotes the first PENDING goal, not the highest-priority one. The class docstring (line 27) promises "priority-based activation".
- **Fix**: Sort pending goals by priority (descending) before promoting.
- **Verified**: ✅

### HIGH-2: `start_session()` changes `self.id` without updating subsystems
- **File**: `src/agentx/agent/model/agent.py:142-149`
- **Fault**: `start_session` sets `self.id = config.id` but subsystems (`PolicyEngine._agent_id`, `MemoryManager._agent_id`, `GoalManager._agent_id`) were initialized with the original `self.id` in `__init__`. Repository saves use the old agent_id while the facade reports the new id.
- **Fix**: Propagate the id change to all subsystems in `start_session`, or deprecate `start_session` (not called by any production path — `AgentAdapter` creates a fresh Agent per session).
- **Verified**: ✅ — subsystems initialized at lines 105-115 with `agent_id=self.id`.

### HIGH-3: `resume_session()` bypasses conflict resolution for legacy snapshots
- **File**: `src/agentx/agent/model/agent.py:186`
- **Fault**: Legacy snapshot rules are loaded via `add_rule(rule)` (no conflict check) instead of `add_rule_safely(rule)`.
- **Fix**: Replace `add_rule(rule)` with `add_rule_safely(rule)` and handle the `False` return.
- **Verified**: ✅

### HIGH-4: `persist()` returns a snapshot_id even on failure
- **File**: `src/agentx/agent/model/agent.py:300-304`
- **Fault**: When `save_snapshot_with_retry` returns `False`, the method logs an error but still returns `snapshot.snapshot_id`. Callers cannot detect failure.
- **Fix**: Return `""` on failure.
- **Verified**: ✅

### HIGH-5: `RunningModal._worker` not joined on unmount
- **File**: `src/agentx/agent/view/tui/fast_agent_modals.py:276-283`
- **Fault**: `on_unmount` sets `_stop_evt` and `_pause_evt` but does not call `self._worker.join()`. If the user opens a new Fast Agent modal quickly, the old worker could still be running `run_cycle()` concurrently.
- **Fix**: Add `self._worker.join(timeout=0.5)` in `on_unmount` after setting the events.
- **Verified**: ✅

### HIGH-6: No timeout on LLM invocation
- **File**: `src/agentx/agent/model/ai_adapter.py:95`
- **Fault**: `llm.invoke([HumanMessage(content=prompt)])` has no timeout. If the LLM HTTP call hangs, the calling thread blocks indefinitely.
- **Fix**: Wrap the invoke in a `concurrent.futures.ThreadPoolExecutor` with a configurable timeout (default 60s).
- **Verified**: ✅

### HIGH-7: `resume_session()` clear-then-fail leaves agent empty
- **File**: `src/agentx/agent/model/agent.py:166-169`
- **Fault**: `resume_session` clears all in-memory state (policy, memory, reflection) before attempting to restore. If the restore fails, the agent is left empty with no rollback.
- **Fix**: Restore into temporary buffers, then swap atomically; or snapshot the pre-clear state and restore it on failure.
- **Verified**: ✅

---

## 4. Medium-Severity Issues (14)

### MED-1: `evict()` criteria use `elif` instead of `if`
- **File**: `src/agentx/agent/model/memory/manager.py:98-105`
- **Fault**: The `elif` chain makes eviction criteria mutually exclusive. If `min_importance` is set but an entry is above it, `tags` is never checked.
- **Fix**: Replace `elif` with `if` for OR semantics.
- **Verified**: ✅

### MED-2: AI service never retries after initialization failure
- **File**: `src/agentx/agent/model/ai_adapter.py:45-47`
- **Fault**: Once `_init_attempted = True` (set before any provider is tried), all subsequent `complete()` calls raise immediately.
- **Fix**: Reset `_init_attempted = False` on each `complete()` call when `_llm is None`.
- **Verified**: ✅

### MED-3: `confidence` not capped for contested rules
- **File**: `src/agentx/agent/model/policy/evaluator.py:161-164` AND `src/agentx/agent/types.py:379`
- **Fault**: `base = winner.priority / 1000.0` has no `min(1.0, ...)` on the contested path (line 164). A rule with priority 1500 produces confidence 1.5. No priority bounds validation in `PolicyRule`.
- **Fix**: `return min(1.0, base)` on both paths; add `__post_init__` to `PolicyRule` validating `0 <= priority <= 1000`.
- **Verified**: ✅ — line 162 has `min(1.0, base + 0.2)` for uncontested, but line 164 returns raw `base`.

### MED-4: `_NOOP` shared mutable singleton
- **File**: `src/agentx/agent/model/policy/evaluator.py:36`
- **Fault**: Module-level `_NOOP = PolicyAction(...)` is returned directly in every no-op decision. `PolicyAction` is mutable, so any caller that mutates `decision.selected_action.parameters` corrupts the global default.
- **Fix**: Return a fresh `PolicyAction(type=ActionType.PAUSE)` copy each time.
- **Verified**: ✅

### MED-5: `apply_adjustment` revert doesn't undo promotion side-effect
- **File**: `src/agentx/agent/model/goal/manager.py:118-141`
- **Fault**: `apply_adjustment` calls `update_status` which may call `_promote_next` (promoting another goal). `revert_adjustment` only restores the original goal's priority/status, not the side-effected goal.
- **Fix**: Capture and restore the promoted goal's id in the rollback token.
- **Verified**: ✅

### MED-6: Policy revert deletes instead of restoring
- **File**: `src/agentx/agent/model/reflection/proposal_router.py:47` → `src/agentx/agent/model/policy/evaluator.py:137-139`
- **Fault**: `revert_rule` calls `remove_rule(rule_id)`, which deletes the rule entirely. If the proposal was an UPDATE to an existing rule, the revert deletes it instead of restoring the previous version.
- **Fix**: Store the previous rule in the rollback token and restore it.
- **Verified**: ✅

### MED-7: Memory revert fails after consolidation
- **File**: `src/agentx/agent/model/memory/manager.py:179-181`
- **Fault**: `revert_update` only pops from `_volatile`. If `consolidate()` moved the entry to persistent tier, the persistent copy remains.
- **Fix**: Also delete from the repository on revert.
- **Verified**: ✅

### MED-8: `ARCHIVED` tier silently dropped in `store()`
- **File**: `src/agentx/agent/model/memory/manager.py:44-51`
- **Fault**: No `elif tier == MemoryTier.ARCHIVED:` branch. If `tier` is `ARCHIVED`, the entry's `tier` field is set but it is not stored anywhere.
- **Fix**: Add an `ARCHIVED` branch (store to persistent repository with tier=ARCHIVED, or treat as persistent).
- **Verified**: ✅

### MED-9: `retrieve()` can return duplicates
- **File**: `src/agentx/agent/model/memory/manager.py:53-56`
- **Fault**: Combines volatile + persistent without deduplication by entry ID. An entry in both tiers appears twice.
- **Fix**: Dedupe by `entry.id`.
- **Verified**: ✅

### MED-10: Broad `except Exception` in condition evaluation
- **File**: `src/agentx/agent/model/policy/rule.py:383-384`
- **Fault**: `CompiledCondition.evaluate` catches all exceptions and returns `False` with no logging. Programming errors in conditions are silently converted to false negatives.
- **Fix**: Catch only `ConditionCompileError` + `TypeError`/`ValueError`; log the rest.
- **Verified**: ✅

### MED-11: Unknown identifiers silently return `None`
- **File**: `src/agentx/agent/model/policy/rule.py:285-320`
- **Fault**: The module docstring says "Unknown identifiers raise `ConditionCompileError` at load time" but `compile_condition` only parses — it does not validate identifiers. Unknown identifiers like `foo.bar` compile and silently evaluate to `None` at runtime.
- **Fix**: Validate root identifiers at compile time; raise `ConditionCompileError` for unknown roots.
- **Verified**: ✅

### MED-12: Deserialization errors not caught in repositories
- **File**: `src/agentx/agent/persistence/repositories_db.py:225-272, 275-310`
- **Fault**: `json.loads(row["..."] or "{}")` can raise `json.JSONDecodeError`. None of the `_row_to_*` helpers have try/except. A single corrupted row crashes `load_by_agent`/`load_tree`, blocking session resume.
- **Fix**: Wrap deserialization in try/except; skip/log corrupt rows.
- **Verified**: ✅

### MED-13: Unbounded reflection log growth
- **File**: `src/agentx/agent/model/reflection/engine.py:78`
- **Fault**: `self._entries` grows without bound. `pending_proposals()` iterates the entire list on every call.
- **Fix**: Cap the log size (default 1000 entries); prune oldest APPLIED/REJECTED first.
- **Verified**: ✅

### MED-14: Snapshots never cleaned up
- **File**: `src/agentx/agent/persistence/agent_db.py:65-81`
- **Fault**: `save_snapshot` creates a new row every time; old snapshots are never deleted. No retention policy.
- **Fix**: Keep last N snapshots per agent (default 50); delete older ones on save.
- **Verified**: ✅

---

## 5. Low-Severity Issues (18)

| # | File:line | Issue | Verified |
|---|-----------|-------|----------|
| L1 | `conflict_resolver.py:37-42` | `resolve_conflicts()` is a stub — always returns `{}`. | ✅ |
| L2 | `conflict_resolver.py:65` | `import re` inside a method (should be top-level). | ✅ |
| L3 | `conflict_resolver.py:68-69` | Keyword exclusion set case-inconsistent: `{"AND","OR","NOT","true","false"}` — `"TRUE"`/`"FALSE"` not excluded. | ✅ |
| L4 | `conflict_resolver.py:80-93` | Contradiction detection incomplete — misses `SET_GOAL vs PAUSE`, `MODIFY_MEMORY vs PAUSE`, etc. | ✅ |
| L5 | `tools/discovery.py:35` | `except Exception: continue` swallows all plugin errors with no logging. No `logging` import. | ✅ |
| L6 | `tools/registry.py:81-85` | `get_sensor`/`get_actuator` raise raw `KeyError` — no graceful `None` or custom exception. | ✅ |
| L7 | `agent.py:425` | Dead code: `if result.success and command is not None:` — `command` is always non-None here. | ✅ |
| L8 | `agent.py:458-478` | `start_session` → `_register_builtin_tools` silently ignores `DuplicateToolError`, so `sandbox_root` config changes are ignored. | ✅ |
| L9 | `goal/manager.py:72-73` | `GoalStatus(status)` raises `ValueError` on invalid string — no try/except. | ✅ |
| L10 | `critique_parser.py:86` | `float(confidence_raw)` raises `TypeError` on non-numeric non-string values — crashes reflection. | ✅ |
| L11 | `agent_db.py:55-61` + `schema_db.py:31-35` | `upsert_agent` uses `INSERT OR REPLACE` with `_now_iso()` → `created_at` overwritten on every upsert. | ✅ |
| L12 | `agent_db.py:90` | `save_snapshot_with_retry` retries on ALL `sqlite3.Error` — should only retry on `OperationalError` ("database is locked"). | ✅ |
| L13 | `schema_db.py` | No indexes on `agent_id` columns — full table scans. | ✅ |
| L14 | `schema_db.py` | No `FOREIGN KEY` constraints — orphaned rows on agent deletion. | ✅ |
| L15 | `agent_screen.py:407,450` | Multiple `except Exception: pass` — silently swallows all errors with no diagnostic. | ✅ |
| L16 | `agent_controller.py:229` | Controller reaches into `self._agent.config.sandbox_root` — not on the `IAgentModelPartner` interface. | ✅ |
| L17 | `agent_controller.py:197` | Grammar: `"Proposal applied"` vs `"Proposal REJECTED"` — inconsistent capitalization. | ✅ |
| L18 | `interfaces.py` | Pervasive `Any` return types where concrete types exist (`CycleResult`, `GoalTree`, etc.). | ✅ |

---

## 6. Incomplete Features / Stubs (8)

| # | File:line | Issue | Verified |
|---|-----------|-------|----------|
| S1 | `types.py:264-267` | `EnvironmentModel.memory_pressure` always returns `0.0` — stub. Policy conditions on it always evaluate `False`. | ✅ |
| S2 | `fast_agent_modals.py:574-576` | `_full_count_hint()` is a placeholder — always equals `len(proposals)`. The "showing first N" branch is dead. | ✅ |
| S3 | `fast_agent_screen.py:97-99` | Goal constraints captured but never applied: `"Constraints noted (not used in v1)"`. | ✅ |
| S4 | `fast_agent_screen.py:128-129` | `save_snapshot()` called synchronously on the UI thread — blocks TUI (unlike `AgentTUIScreen` which uses `run_blocking`). | ✅ |
| S5 | `fast_agent_modals.py:439-443` | Only `self._pending[0]` is approvable — multi-proposal batch approval not supported; causes re-prompt loop. | ✅ |
| S6 | `agent_screen.py:425-428` | `show_policy_editor` only prints id/priority/enabled — no condition or action (less useful than console view). | ✅ |
| S7 | `reflection/engine.py:140-148` | Pending proposals never expire — accumulate forever; no dismiss-without-approve. | ✅ |
| S8 | `fast_agent_screen.py:91-92` | Comment says `kind="manual"` but `SuccessCriteria()` defaults to `kind="always"` — misleading. | ✅ |

---

## 7. Scope Decision

All 50 issues are in scope for feature_015. The implementation follows the review's
4-phase prioritized plan:

| Phase | Issues | Est. LOC (fix) | Est. Tests |
|-------|--------|----------------|------------|
| 1 — Critical | C1, C2, C3 | ~29 | 10 |
| 2 — High | H1–H7 | ~40 | 8 |
| 3 — Medium | M1–M14 | ~80 | 14 |
| 4 — Low + Stubs | L1–L18, S1–S8 | ~120 | 18 |
| **Total** | **50** | **~269** | **~50** |

**Constraint**: zero regressions on the existing 678/679 suite; MVC++ stays at 0 errors.
