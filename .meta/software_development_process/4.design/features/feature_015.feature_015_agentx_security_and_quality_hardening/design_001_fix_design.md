# Design 001 — Fix Design

> Feature: feature_015.agentx_security_and_quality_hardening
> Date: 2026-07-11
> Status: Design

This document specifies the exact code-level fix for every issue verified in
`analysis_001_issue_verification.md`. Fixes are grouped by priority phase.

**Architecture constraint**: All fixes stay within the existing MVC++ layer boundaries.
No new layers, no new Abstract Partners (except where an interface method is added to
support a fix). SQL changes stay in DP classes. View changes stay in View files.

---

## Phase 1 — Critical Fixes

### C1: Path-traversal sandbox bypass

**Files**: `filesystem_tool.py`, `scenarios.py`

**Fix** (both locations): Replace `str().startswith()` with `Path.is_relative_to()`:

```python
# filesystem_tool.py validate() — line 86
target = (self._root / path).resolve()
if not target.is_relative_to(self._root):
    return ValidationResult(valid=False, errors=["path escapes sandbox"])
```

`act()` (line 104) calls `validate()` first, so no second check needed — but we also
resolve `self._root` in `__init__` (already done at line 34). `is_relative_to` is
available since Python 3.9 (project minimum).

```python
# scenarios.py seed_sandbox_files() — line 193
root = Path(sandbox_root).resolve()  # resolve once
...
target = (root / relpath).resolve()
if not target.is_relative_to(root):
    raise ValueError(f"scenario file escapes sandbox: {relpath}")
```

Also fix `scenarios.py` to resolve `root` once (currently `root.resolve()` is called
inside the loop at line 193, but `root` itself is not resolved — only `Path(sandbox_root)`
without `.resolve()` at line 187).

**Tests**: 3 — sibling-dir escape, symlink, normal path.

---

### C2: Safety deny-list non-functional

**Files**: `safety_evaluator.py`

**Fix**: Derive `op` from the proposal's content shape, not the untrusted `op` field.

```python
def evaluate(self, proposal: Proposal, ctx: PolicyContext) -> ProposalVerdict:
    op = self._infer_op(proposal)
    key = f"{proposal.type.value}:{op}"
    if key in self.DANGEROUS:
        return ProposalVerdict(ProposalStatus.REJECTED, "deny-listed operation")
    ...

@staticmethod
def _infer_op(proposal: Proposal) -> str:
    """Infer the operation from the proposal's content shape (C2).

    Does NOT trust proposal.content.get('op') — derives the op from the
    content keys so a malicious or malformed proposal can't bypass the
    deny-list by omitting or mislabeling 'op'.
    """
    content = proposal.content
    ptype = proposal.type
    if ptype == ProposalType.POLICY_CHANGE:
        # The router's _apply_policy_change always calls add_rule_safely,
        # so every POLICY_CHANGE is an add/update. There's no 'delete' op
        # in the current router, but the deny-list guards against future
        # routers. Infer from content: if 'enabled' is False → 'disable'.
        if content.get("enabled") is False:
            return "disable"
        return "update"
    if ptype == ProposalType.MEMORY_UPDATE:
        if content.get("delete_all") or content.get("clear"):
            return "delete_all"
        return "add"
    if ptype == ProposalType.GOAL_ADJUSTMENT:
        status = content.get("status", "")
        if status == "ABANDONED":
            return "abandon_root"
        if status == "DELETED":
            return "delete"
        if content.get("priority") is not None and int(content.get("priority", 0)) < 0:
            return "demote"
        return "update"
    if ptype == ProposalType.TOOL_CONFIGURATION:
        return content.get("op", "noop")
    return ""
```

**Tests**: 4 — delete-rule rejected, delete-all-memory rejected, abandon-root rejected, tool-delete rejected.

---

### C3: DSL subtraction broken

**Files**: `rule.py`

**Fix**: Remove `-?` from the `NUMBER` pattern. Add a unary-minus production in `_primary()`.

Tokenizer change (line 87):
```python
# Before:  (?P<NUMBER>-?\d+\.?\d*)
# After:   (?P<NUMBER>\d+\.?\d*)
(?P<NUMBER>\d+\.?\d*) |
```

Parser change — add unary minus in `_primary()` (before the NUMBER case):
```python
def _primary(self) -> ASTNode:
    tok = self._peek()
    if tok is None:
        raise ConditionCompileError("unexpected end of expression")
    # C3: unary minus → Literal(0) - operand, or a UnaryOp("-", operand)
    if tok[0] == "OP" and tok[1] == "-":
        self._consume()
        return UnaryOp("-", self._primary())
    if tok[0] == "OP" and tok[1] == "+":
        self._consume()
        return self._primary()  # unary plus is a no-op
    ...
```

Evaluation change — handle `UnaryOp("-", ...)` in `_visit()`:
```python
if isinstance(node, UnaryOp):
    if node.op == "NOT":
        return not self._visit(node.operand, ctx)
    if node.op == "-":
        return -self._visit(node.operand, ctx)
```

This makes `5-3` tokenize as `NUMBER(5)`, `OP(-)`, `NUMBER(3)` → parsed as
`Arithmetic("-", Literal(5), Literal(3))` → evaluates to `2`. And `-5` tokenizes as
`OP(-)`, `NUMBER(5)` → `UnaryOp("-", Literal(5))` → evaluates to `-5`.

**Tests**: 3 — `5-3>1` evaluates True, `goal.priority-5>10` evaluates correctly, `-5` is a valid negative literal.

---

## Phase 2 — High-Severity Fixes

### H1: Goal promotion ignores priority

**File**: `goal/manager.py:84-91`

```python
def _promote_next(self, completed_id: str) -> None:
    pending = [g for g in self._tree.nodes.values() if g.status == GoalStatus.PENDING]
    if not pending:
        return
    goal = max(pending, key=lambda g: g.priority)
    goal.status = GoalStatus.ACTIVE
    goal.updated_at = datetime.now(timezone.utc)
    if self._repository is not None:
        self._repository.save(self._agent_id, goal)
```

**Tests**: 2 — priority-10 vs priority-90 promotion, equal-priority tie-break.

---

### H2: `start_session()` agent_id mismatch

**File**: `agent.py:142-149`

**Fix**: Propagate the id change to all subsystems:

```python
def start_session(self, config: AgentConfig) -> str:
    self.id = config.id
    self.config = config
    self.state = AgentState.PERCEIVING
    # H2: propagate the new id to all subsystems so repository saves use
    # the correct agent_id.
    self.policy_engine._agent_id = config.id
    self.memory._agent_id = config.id
    self.goal_manager._agent_id = config.id
    self._register_builtin_tools(config)
    self._persist_agent_row()
    return self.id
```

Note: `_agent_id` is a private attribute, but `start_session` is on the same facade that
owns the subsystems — this is internal wiring, not a cross-layer violation.

**Tests**: 1 — start_session changes id, subsystem saves use the new id.

---

### H3: `resume_session()` bypasses conflict resolution

**File**: `agent.py:186`

```python
# Before:  self.policy_engine.add_rule(rule)
# After:
if not self.policy_engine.add_rule_safely(rule):
    _log.warning("legacy snapshot rule %s skipped (conflict)", rule.id)
```

**Tests**: 1 — legacy snapshot with a conflicting rule skips it (not crashes).

---

### H4: `persist()` returns id on failure

**File**: `agent.py:300-304`

```python
ok = self._db.save_snapshot_with_retry(snapshot)
self.state = AgentState.PERCEIVING
if not ok:
    _log.error("persistence failed for agent %s", self.id)
    return ""  # H4: signal failure to caller
return snapshot.snapshot_id
```

**Tests**: 1 — persist returns "" when save fails (mock save_snapshot_with_retry → False).

---

### H5: Worker not joined on unmount

**File**: `fast_agent_modals.py:276-283`

```python
def on_unmount(self) -> None:
    super().on_unmount()
    self._auto_running = False
    self._stop_evt.set()
    self._pause_evt.set()
    # H5: join the worker so it doesn't race a new modal's worker.
    if self._worker is not None and self._worker.is_alive():
        self._worker.join(timeout=0.5)
        if self._worker.is_alive():
            _log.warning("FastAgent worker did not exit within 0.5s")
```

Add `import logging` + `_log = logging.getLogger(__name__)` at module top.

**Tests**: 1 — on_unmount joins the worker (worker thread exits within timeout).

---

### H6: No LLM invoke timeout

**File**: `ai_adapter.py:86-99`

```python
import concurrent.futures

_LLM_TIMEOUT = 60.0  # seconds

def complete(self, prompt: str) -> str:
    from langchain_core.messages import HumanMessage
    llm = self._ensure_llm()
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(llm.invoke, [HumanMessage(content=prompt)])
            response = future.result(timeout=_LLM_TIMEOUT)
    except concurrent.futures.TimeoutError:
        raise RuntimeError(f"LLM invocation timed out after {_LLM_TIMEOUT}s")
    if hasattr(response, "content"):
        return str(response.content)
    return str(response)
```

**Tests**: 1 — complete() raises RuntimeError on timeout (mock llm.invoke to sleep).

---

### H7: `resume_session()` clear-then-fail

**File**: `agent.py:151-208`

**Fix**: Snapshot pre-clear state; restore on failure.

```python
def resume_session(self, snapshot_id: str) -> None:
    snapshot = self._db.load_snapshot(snapshot_id)
    if snapshot is None:
        raise FileNotFoundError(f"snapshot not found: {snapshot_id}")

    # H7: snapshot pre-clear state so we can roll back on failure.
    saved_rules = dict(self.policy_engine.rules)
    saved_volatile = self.memory.export_volatile()
    saved_reflection = self.reflection_engine.get_log()

    try:
        self._do_restore(snapshot)
    except Exception:
        # Restore the pre-clear state.
        self.policy_engine.clear()
        for rule in saved_rules.values():
            self.policy_engine.add_rule(rule)
        self.memory.import_volatile(saved_volatile)
        self.reflection_engine.restore_log(saved_reflection)
        self.state = AgentState.PERCEIVING
        raise

def _do_restore(self, snapshot: SessionSnapshot) -> None:
    """The actual restore logic (extracted from resume_session for H7)."""
    self.policy_engine.clear()
    self.memory.import_volatile([])
    self.reflection_engine.restore_log([])
    ...  # (existing restore code, unchanged)
```

**Tests**: 1 — resume with corrupted snapshot restores pre-clear state.

---

## Phase 3 — Medium Fixes

### M1: `evict()` elif → if

**File**: `memory/manager.py:98-105` — replace `elif` with `if` for all criteria after the first.

### M2: AI service retry

**File**: `ai_adapter.py:45-47` — in `_ensure_llm`, reset `_init_attempted = False` at the top when `_llm is None`:

```python
def _ensure_llm(self) -> Any:
    if self._llm is not None:
        return self._llm
    # M2: allow retry after a previous failure (user may have added a key).
    self._init_attempted = False
    ...
```

### M3: Confidence cap + priority bounds

**File**: `evaluator.py:164` — `return min(1.0, base)`
**File**: `types.py` — add `__post_init__` to `PolicyRule`:

```python
def __post_init__(self) -> None:
    if not (0 <= self.priority <= 1000):
        raise ValueError(f"priority must be 0-1000, got {self.priority}")
```

### M4: `_NOOP` singleton

**File**: `evaluator.py:36,104` — replace `_NOOP` module constant with a factory:

```python
def _noop_action() -> PolicyAction:
    return PolicyAction(type=ActionType.PAUSE)
```

Use `_noop_action()` in `evaluate()` (line 104).

### M5: Goal revert doesn't undo promotion

**File**: `goal/manager.py:118-141` — capture promoted goal id in rollback token:

```python
def apply_adjustment(self, content: dict[str, Any]) -> str:
    ...
    promoted_id = ""
    if "status" in content:
        old_active = self.active_goal()
        self.update_status(goal_id, content["status"])
        new_active = self.active_goal()
        if new_active is not None and new_active.id != goal_id and (
            old_active is None or old_active.id != new_active.id
        ):
            promoted_id = new_active.id
    return f"{goal_id}:{old_priority}:{old_status.value}:{promoted_id}"

def revert_adjustment(self, token: str) -> None:
    try:
        parts = token.split(":")
        goal_id, old_prio, old_status = parts[0], parts[1], parts[2]
        promoted_id = parts[3] if len(parts) > 3 else ""
        goal = self._tree.get(goal_id)
        if goal is not None:
            goal.priority = int(old_prio)
            goal.status = GoalStatus(old_status)
        if promoted_id:
            promoted = self._tree.get(promoted_id)
            if promoted is not None and promoted.status == GoalStatus.ACTIVE:
                promoted.status = GoalStatus.PENDING
    except (ValueError, KeyError):
        pass
```

### M6: Policy revert deletes instead of restoring

**File**: `evaluator.py:137-139` — store previous rule, restore on revert:

```python
def revert_rule(self, rule_id: str, previous: PolicyRule | None = None) -> None:
    """Roll back a reflection-proposed rule (design §7.5).

    M6: if *previous* is provided, restore it instead of deleting.
    """
    if previous is not None:
        self.add_rule(previous)
    else:
        self.remove_rule(rule_id)
```

The `ProposalRouter` must capture the previous rule before applying:

```python
# proposal_router.py _apply_policy_change
existing = self._policy.rules.get(rule_id)
if self._policy.add_rule_safely(rule):
    # M6: return a token that encodes the previous rule for revert.
    return f"{rule_id}:{json.dumps(_rule_to_dict(existing)) if existing else ''}"
```

Actually, this is getting complex. Simpler approach: `revert_rule` takes an optional
previous-rule parameter. The ProposalRouter stores the previous rule in its own dict
(keyed by rule_id) and passes it on revert. But the current `revert` signature is
`Callable[[str], None]` — only takes a token string.

**Simpler design**: encode the previous rule's dict in the rollback token (JSON string).
On revert, deserialize and restore. This keeps the `Callable[[str], None]` signature.

### M7: Memory revert fails after consolidation

**File**: `memory/manager.py:179-181`:

```python
def revert_update(self, token: str) -> None:
    self._volatile.pop(token, None)
    # M7: also delete from persistent tier if consolidation moved it.
    if self._repository is not None:
        self._repository.delete(token)
```

### M8: ARCHIVED tier

**File**: `memory/manager.py:44-51`:

```python
def store(self, entry: MemoryEntry, tier: MemoryTier = MemoryTier.VOLATILE) -> None:
    entry.tier = tier
    if tier == MemoryTier.VOLATILE:
        self._volatile[entry.id] = entry
        self._volatile.move_to_end(entry.id)
        self._enforce_capacity()
    elif tier in (MemoryTier.PERSISTENT, MemoryTier.ARCHIVED) and self._repository is not None:
        self._repository.save(self._agent_id, entry)
```

### M9: Retrieve dedup

**File**: `memory/manager.py:53-56`:

```python
def retrieve(self, query: MemoryQuery) -> list[MemoryEntry]:
    seen: set[str] = set()
    results: list[MemoryEntry] = []
    for entry in list(self._volatile.values()):
        if entry.id not in seen:
            results.append(entry)
            seen.add(entry.id)
    if self._repository is not None:
        for entry in self._repository.load_by_agent(self._agent_id):
            if entry.id not in seen:
                results.append(entry)
                seen.add(entry.id)
    ...  # (rest of filtering unchanged)
```

### M10: Broad except in condition evaluation

**File**: `rule.py:376-384`:

```python
def evaluate(self, ctx: PolicyContext) -> bool:
    if self._ast is None:
        self._ast = compile_condition(self.expression)
    try:
        return bool(ConditionEvaluator().evaluate(self._ast, ctx))
    except ConditionCompileError:
        return False
    except (TypeError, ValueError, KeyError, AttributeError) as exc:
        # M10: log diagnosable errors instead of silently returning False.
        _log.warning("condition %r evaluation error: %s", self.expression, exc)
        return False
```

### M11: Unknown identifiers

**File**: `rule.py:232-237` — add identifier validation in `compile_condition`:

```python
_KNOWN_ROOTS = {"true", "false", "agent", "environment", "goal", "memory"}
_KNOWN_FUNCTIONS = {"has_observation", "goal_is_blocked", "memory_contains"}

def compile_condition(expr: str) -> ASTNode:
    tokens = tokenize(expr)
    if not tokens:
        return Literal(True)
    ast = _Parser(tokens).parse()
    _validate_identifiers(ast)
    return ast

def _validate_identifiers(node: ASTNode) -> None:
    """M11: fail-fast on unknown identifiers (docstring promise)."""
    if isinstance(node, Identifier):
        root = node.parts[0]
        if root not in _KNOWN_ROOTS:
            raise ConditionCompileError(f"unknown identifier: {root}")
    elif isinstance(node, FunctionCall):
        if node.name not in _KNOWN_FUNCTIONS:
            raise ConditionCompileError(f"unknown function: {node.name}")
        for arg in node.args:
            _validate_identifiers(arg)
    elif isinstance(node, UnaryOp):
        _validate_identifiers(node.operand)
    elif isinstance(node, BinaryOp):
        _validate_identifiers(node.left)
        _validate_identifiers(node.right)
    elif isinstance(node, Comparison):
        _validate_identifiers(node.left)
        _validate_identifiers(node.right)
    elif isinstance(node, Arithmetic):
        _validate_identifiers(node.left)
        _validate_identifiers(node.right)
```

### M12: Deserialization errors

**File**: `repositories_db.py` — wrap each `_row_to_*` in try/except:

```python
def _row_to_memory_entry(row: sqlite3.Row) -> MemoryEntry:
    try:
        return MemoryEntry(...)
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        _log.warning("corrupt memory row %s: %s", row["id"], exc)
        return None  # caller filters None
```

Update callers to filter `None`:
```python
return [e for e in (_row_to_memory_entry(r) for r in rows) if e is not None]
```

### M13: Reflection log growth

**File**: `engine.py:78` — add a cap:

```python
_MAX_LOG_ENTRIES = 1000

class ReflectionEngine:
    def __init__(self, ...):
        ...
        self._max_entries = max_log_entries if (max_log_entries := ...) else _MAX_LOG_ENTRIES

    def _append_entry(self, entry: ReflectionEntry) -> None:
        self._entries.append(entry)
        # M13: prune oldest APPLIED/REJECTED entries when over cap.
        if len(self._entries) > self._max_entries:
            excess = len(self._entries) - self._max_entries
            # Keep NEEDS_CONFIRMATION and PROPOSED; prune resolved first.
            prunable = [
                i for i, e in enumerate(self._entries)
                if not any(p.status == ProposalStatus.NEEDS_CONFIRMATION for p in e.proposals)
            ]
            for i in reversed(prunable[:excess]):
                del self._entries[i]
```

Replace `self._entries.append(entry)` calls (lines 97, 115, 120) with `self._append_entry(entry)`.

### M14: Snapshot retention

**File**: `agent_db.py:65-81` — add retention after save:

```python
_MAX_SNAPSHOTS_PER_AGENT = 50

def save_snapshot(self, snapshot: SessionSnapshot) -> bool:
    with sqlite3.connect(self.path) as conn:
        conn.execute(TableSessionSnapshots.INSERT, ...)
        conn.commit()
        # M14: retain only the last N snapshots per agent.
        conn.execute(
            f"DELETE FROM {TableSessionSnapshots.TABLE_NAME} "
            f"WHERE agent_id = ? AND snapshot_id NOT IN ("
            f"  SELECT snapshot_id FROM {TableSessionSnapshots.TABLE_NAME} "
            f"  WHERE agent_id = ? ORDER BY timestamp DESC LIMIT ?"
            f")",
            (snapshot.agent_id, snapshot.agent_id, _MAX_SNAPSHOTS_PER_AGENT),
        )
        conn.commit()
    return True
```

Add a `DELETE_OLD_BY_AGENT` statement to `schema_db.py TableSessionSnapshots`.

---

## Phase 4 — Low + Stubs

### L1-L4: ConflictResolver

- **L1**: Remove the stub `resolve_conflicts()` or implement it (delegate to `detect`).
- **L2**: Move `import re` to top of file.
- **L3**: Use `{"AND", "OR", "NOT", "TRUE", "FALSE", "True", "False", "true", "false"}` or `.upper()` the tokens before checking.
- **L4**: Add `SET_GOAL vs PAUSE`, `MODIFY_MEMORY vs PAUSE` to `_divergent()`.

### L5: Discovery logging

```python
import logging
_log = logging.getLogger(__name__)
...
except Exception as exc:
    _log.warning("plugin %s failed to load: %s", ep.name, exc)
    continue
```

### L6: Registry custom exception

```python
def get_sensor(self, sid: str) -> ISensor:
    sensor = self._sensors.get(sid)
    if sensor is None:
        raise ToolSchemaError(f"unknown sensor: {sid}")
    return sensor
```

(Same for `get_actuator`.)

### L7: Dead code

`agent.py:425` — remove the `and command is not None` part (command is always non-None).

### L8: Force re-register on config change

`agent.py:_register_builtin_tools` — unregister existing tools before re-registering:

```python
def _register_builtin_tools(self, config: AgentConfig) -> None:
    # L8: unregister stale tools so sandbox_root changes take effect.
    self.tool_registry.unregister("filesystem")
    self.tool_registry.unregister("rag_query")
    self.tool_registry.unregister("session")
    ...
```

### L9: GoalStatus enum safety

```python
if isinstance(status, str):
    try:
        status = GoalStatus(status)
    except ValueError:
        _log.warning("invalid goal status: %s", status)
        return
```

### L10: CritiqueParser TypeError

```python
else:
    try:
        confidence = float(confidence_raw)
    except (TypeError, ValueError):
        confidence = 0.5
```

### L11: Preserve created_at

`schema_db.py TableAgents.INSERT` — use `INSERT OR IGNORE` + `UPDATE` (upsert pattern), or
split into two statements. Simpler: change `INSERT` to not include `created_at` on replace:

Actually, the cleanest fix: use `INSERT OR IGNORE` then `UPDATE`:

```python
INSERT_OR_IGNORE = f"INSERT OR IGNORE INTO {TABLE_NAME} (id, name, version, autonomy_level, config_json, created_at) VALUES (?, ?, ?, ?, ?, ?)"
UPDATE = f"UPDATE {TABLE_NAME} SET name = ?, version = ?, autonomy_level = ?, config_json = ? WHERE id = ?"
```

`upsert_agent`:
```python
with sqlite3.connect(self.path) as conn:
    conn.execute(TableAgents.INSERT_OR_IGNORE, (agent_id, name, version, autonomy_level, config_json, _now_iso()))
    conn.execute(TableAgents.UPDATE, (name, version, autonomy_level, config_json, agent_id))
    conn.commit()
```

### L12: Only retry OperationalError

```python
except sqlite3.OperationalError:  # L12: only retry "database is locked"
    if attempt == max_retries - 1:
        return False
    time.sleep(1)
except sqlite3.Error:  # other errors — don't retry
    return False
```

### L13: Add indexes

`schema_db.py` — add `CREATE INDEX IF NOT EXISTS` statements:

```python
INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_snapshot_agent ON session_snapshots(agent_id)",
    "CREATE INDEX IF NOT EXISTS idx_memory_agent ON memory_entries(agent_id)",
    "CREATE INDEX IF NOT EXISTS idx_policy_agent ON policy_rules(agent_id)",
    "CREATE INDEX IF NOT EXISTS idx_goals_agent ON goals(agent_id)",
    "CREATE INDEX IF NOT EXISTS idx_reflection_agent ON reflection_entries(agent_id)",
]
```

Apply in `_ensure_schema`.

### L14: Foreign keys

Add `REFERENCES agents(id)` to `agent_id` columns. Enable `PRAGMA foreign_keys = ON` on
each connection. (Note: existing rows without matching agent rows would fail — so add FKs
as a separate `ALTER TABLE` migration, or just add to new tables. Since tables use
`CREATE TABLE IF NOT EXISTS`, existing tables won't get FKs. For safety, we'll add the FKs
to the schema for new databases and document that existing DBs need a migration. Actually,
since this is a single-user app with local SQLite, and the tables are already created, the
practical fix is to add `ON DELETE CASCADE` via a migration. But that's complex. **Decision**:
add FKs to the schema definitions for new databases; for existing databases, the indexes
(L13) are the practical improvement. Document the limitation.)

### L15: Remove broad except in agent_screen.py

Replace `except Exception: pass` with targeted exceptions + logging. At minimum, log the
error so it's diagnosable:

```python
except Exception as exc:
    _log.debug("agent_screen widget update failed: %s", exc)
```

### L16: Use interface for sandbox_root

Add `sandbox_root` property to `IAgentModelPartner`:

```python
@property
@abstractmethod
def sandbox_root(self) -> str: ...
```

Agent implements it: `return self.config.sandbox_root`.

AgentController uses `self._agent.sandbox_root` instead of `self._agent.config.sandbox_root`.

### L17: Fix grammar

```python
f"Proposal {outcome.status.value.lower()}"
```

### L18: Tighten return types

Change `Any` returns in `interfaces.py` to concrete types where they exist. Use
`TYPE_CHECKING` imports (already present). For example:

```python
def run_cycle(self) -> "CycleResult": ...
def list_rules(self) -> list["PolicyRule"]: ...
def list_goals(self) -> "GoalTree": ...
```

This is a non-breaking change (type hints only).

---

### S1: memory_pressure heuristic

```python
@property
def memory_pressure(self) -> float:
    """Heuristic 0.0-1.0 based on sensor reading count vs capacity."""
    if not self.sensor_readings:
        return 0.0
    return min(1.0, len(self.sensor_readings) / 100.0)
```

### S2: _full_count_hint — remove dead branch or implement

Since the caller always passes `proposals[:3]`, and `_full_count_hint` returns
`len(proposals)`, the "showing first N" branch is only dead when proposals > 3 but
the modal only receives 3. **Fix**: pass the full count from the caller:

```python
# RunningModal._poll, _MsgPending branch:
proposals_as_dicts = [... self._pending[:3] ...]
self.app.push_screen(
    ReflectionModal(proposals_as_dicts, full_count=len(self._pending)),
    ...
)
```

```python
# ReflectionModal.__init__:
def __init__(self, proposals: list[dict[str, Any]], full_count: int | None = None) -> None:
    super().__init__()
    self._proposals = proposals
    self._full_count = full_count if full_count is not None else len(proposals)
```

### S3: Constraints

Store constraints and pass them to the controller's `submit_goal`. Requires adding a
`constraints` parameter to `AgentController.submit_goal`. Since constraints are "not used
in v1" per design, we'll store them in the goal's metadata (no schema change needed) and
log them. This makes the capture non-dead.

Actually, the simplest meaningful fix: pass constraints as part of the goal description
or store them in a goal metadata field. Since `Goal` doesn't have a constraints field,
and adding one is a schema change, the practical fix is to append constraints to the
description: `f"{description}\n\nConstraints: {constraints}"`. This makes the constraint
visible to the AI reflection and the goal display.

### S4: Async save in FastAgentTUIScreen

Use `run_blocking` from the TUI framework (feature_014):

```python
def _on_result(self, action: str | None) -> None:
    ...
    if action == "save":
        if self._controller:
            self.run_blocking(
                self._controller.save_snapshot,
                on_result=self._on_save_done,
                on_error=self._on_save_error,
            )
    ...

def _on_save_done(self, snap_id: str) -> None:
    self.notify(f"Session saved ({snap_id[:8]}…)", timeout=3)
    self.app.push_screen(ResultModal(...), callback=self._on_result)

def _on_save_error(self, exc: Exception) -> None:
    self.notify(f"Save failed: {exc}", severity="error")
    self.app.push_screen(ResultModal(...), callback=self._on_result)
```

### S5: Batch proposal approval

`ReflectionModal` — add "Approve All" / "Dismiss All" buttons:

```python
with Horizontal():
    yield Button("✓ Approve All", id="btn-approve-all", variant="success")
    yield Button("✕ Dismiss All", id="btn-dismiss-all", variant="default")
    yield Button("⏹ Stop", id="btn-stop", variant="error")
```

Dismiss values: `"approve_all"`, `"dismiss_all"`. `RunningModal._on_reflection` handles
these by approving/dismissing all pending proposals.

### S6: Show policy condition + action

```python
def show_policy_editor(self, rules: list[PolicyRule]) -> None:
    self._log(f"[Policy] {len(rules)} rule(s)")
    for rule in rules:
        action = rule.action
        self._log(
            f"  {rule.id[:8]}…  pri={rule.priority}  enabled={rule.enabled}\n"
            f"    condition: {rule.condition_expr}\n"
            f"    action: {action.type.value}({action.parameters})"
        )
```

### S7: Expire old proposals

`ReflectionEngine` — add a method to dismiss old NEEDS_CONFIRMATION proposals:

```python
def expire_old_proposals(self, max_age_seconds: float = 3600.0) -> int:
    """S7: expire NEEDS_CONFIRMATION proposals older than max_age_seconds."""
    now = datetime.now(timezone.utc)
    expired = 0
    for entry in self._entries:
        for proposal in entry.proposals:
            if proposal.status == ProposalStatus.NEEDS_CONFIRMATION:
                age = (now - entry.created_at).total_seconds()
                if age > max_age_seconds:
                    proposal.status = ProposalStatus.REJECTED
                    expired += 1
    return expired
```

Call this in `reflect()` before processing new proposals.

### S8: Fix SuccessCriteria kind comment

The comment says `kind="manual"` but `SuccessCriteria()` defaults to `kind="always"`.
Since there's no `"manual"` kind in the `SuccessCriteria` docstring (only `always`,
`tool_success`, `expression`), and Fast Agent doesn't want auto-completion, the fix is
to add a `"manual"` kind to `SuccessCriteria` that never auto-completes, and use it:

```python
# types.py SuccessCriteria docstring:
# * ``"manual"`` — never auto-completes (used by Fast Agent; user presses Stop)

# fast_agent_screen.py:
self._controller.submit_goal(description, success_criteria=SuccessCriteria(kind="manual"))
```

And in `Agent.act()`, skip goal completion for `kind="manual"`:
```python
if active and active.success_criteria.kind == "tool_success":
    ...  # existing logic
# "manual" kind → never auto-complete
```

---

## Implementation Order

1. **C1, C2, C3** (critical security + broken feature) — must be first
2. **H1-H7** (data consistency + concurrency)
3. **M1-M14** (batch medium)
4. **L1-L18** (low polish)
5. **S1-S8** (stubs)

Each phase is followed by its regression tests. The full suite is run after all phases.
