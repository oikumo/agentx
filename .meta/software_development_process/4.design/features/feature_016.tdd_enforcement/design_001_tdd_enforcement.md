# Design — feature_016: TDD Enforcement

> Spec: `.meta/doc/tdd/tdd-agent-spec.md` (Kent Beck TDD v5)
> Pattern: follows `mvc_check.py` (Python script → JSON → TypeScript enforcer acts)
> Constraint: `omt_enforcer.ts` stays as the gate; Python script is the engine.

---

## 1. Architecture

```
omt_enforcer.ts (GATE)
  │
  ├── omt_testlist{behaviors}     ─┐
  ├── omt_red{test_node}          ─┤
  ├── omt_green{test_node}        ─┤── $`uv run scripts/omt/tdd_check.py <cmd>`
  ├── omt_refactor{test_node}     ─┤     .cwd(dir).quiet().nothrow()
  ├── omt_done{feature}           ─┘     → JSON response → tool return string
  │
  ├── tool.execute.before(src/)
  │     └── if tdd_mode: $`tdd_check.py gate --path X --session S`
  │           → {allowed: false} → throw OmtBlock(reason)
  │           → {allowed: true, warning} → notify(warning)
  │
  ├── tool.execute.before(tests/)
  │     └── if tdd_mode: $`tdd_check.py gate --path X --is-tests --session S`
  │           → same as above
  │
  ├── tool.execute.after(src/)
  │     └── if tdd_mode: $`tdd_check.py after-edit --path X --session S`
  │           → advisories → notify (non-blocking)
  │           → if REFACTOR + pytest fails → revert + block
  │
  └── omt_complete
        └── $`tdd_check.py validate-exit --feature F`
              → {ok: false} → block phase exit
```

---

## 2. tdd_check.py — Subcommands

### 2.1 `testlist --behaviors JSON --feature F --session S`
- Records behaviors to implement in the ledger
- Sets TDD state to TESTLIST
- No pytest, no AST
- Returns: `{ok, state:"testlist", message, behaviors_count}`

### 2.2 `start --test-node N --target-src T --feature F --session S`
- **pytest**: `subprocess.run([sys.executable, "-m", "pytest", N, "-x", "-q", "--no-header", "--tb=short"], timeout=30)`
- **Exit code interpretation**:
  - exit 1 (test failed) → RED VERIFIED ✅
  - exit 5 (no tests collected) → RED VERIFIED ✅ (test doesn't exist yet)
  - exit 0 (test passes) → WARNING: "test already passes"
  - exit 2/3/4 → error
- **AST analysis** (if target_src inferred or provided):
  - `infer_target_src(test_file)` → parse imports
  - `verify_true_red(test_file, test_name, src_files)` → missing references
  - `detect_red_anti_patterns(test_file, snapshot)` → batch-N-tests, naming, skip/xfail
- **Ledger write**: `{kind:"tdd", state:"red", test_node, target_src, verified, exit_code, feature}`
- **Returns**: `{ok, state:"red", verified, exit_code, is_true_red, missing, test_summary, message, warnings}`

### 2.3 `green --test-node N --feature F --session S`
- **pytest**: same subprocess call, require exit == 0
- If exit != 0 → BLOCK: "test still fails, write more code"
- **AST analysis**:
  - `snapshot_source(src_file)` → save to `.meta/.omt/tdd_snapshots/<stem>.json`
  - `check_law3_violations(src_file, test_file, test_name, prev_snapshot)` → new methods not in test refs
- **Ledger write**: `{kind:"tdd", state:"green", test_node, verified, exit_code, feature}`
- **Returns**: `{ok, state:"green", verified, exit_code, message, law3_violations}`

### 2.4 `refactor --test-node N --feature F --session S`
- **pytest**: require exit == 0 (must be green to start refactoring)
- **Ledger write**: `{kind:"tdd", state:"refactor", test_node, verified, exit_code, feature}`
- **Returns**: `{ok, state:"refactor", verified, message}`

### 2.5 `done --feature F --session S`
- **pytest full suite**: `subprocess.run([sys.executable, "-m", "pytest", "-q"], timeout=120)`
- **AST analysis**:
  - `find_untested_public_methods(src_files, test_files)` → coverage gaps
  - `find_partner_interfaces(src_files)` → untested abstract methods
  - `check_test_naming(test_files)` → `test_<subject>_<behavior>`
  - `get_tdd_cycles(feature)` → refactor recorded per cycle
- **Checklist** (spec done_checklist):
  1. test_list empty
  2. full suite 0 failed/error
  3. no new skip/xfail
  4. coverage gaps (AST)
  5. refactor recorded per GREEN cycle
  6. naming convention
- **Ledger write**: `{kind:"tdd", state:"done", feature, checklist}`
- **Returns**: `{ok, checklist:{...}, coverage_gaps, message}`

### 2.6 `gate --path P --session S [--is-tests]`
- **Ledger read only** — no pytest, no AST
- Reads latest TDD state for session
- **Two-hats gate** (lookup table):
  ```
  HAT_RULES = {
    "testlist":  {"src": False, "tests": False},
    "red":       {"src": False, "tests": True},
    "green":     {"src": True,  "tests": False},
    "refactor":  {"src": True,  "tests": False},
    "done":      {"src": False, "tests": False},
  }
  ```
- **Returns**: `{allowed, reason, state, tdd_mode, warning?}`

### 2.7 `after-edit --path P --session S`
- **Quick AST scan**: `extract_public_methods(path)` → compare to snapshot
- **REFACTOR state**: run pytest on current test_node (timeout 30s)
  - If pytest fails → `revert_file(path)` → return `{action:"reverted", reason}`
- **GREEN state**: `check_law3_violations` → advisory warnings
- **Returns**: `{action:"ok"|"reverted"|"warning", advisories?, reason?}`

### 2.8 `status --session S`
- Read ledger → current TDD state, cycles completed, testlist progress
- **Returns**: `{tdd_mode, state, test_node?, target_src?, cycles, testlist?}`

### 2.9 `validate-exit --feature F`
- Full AST scan: coverage gaps + partner gaps + dangling reds + orphan tests
- **Returns**: `{ok, dangling_reds, coverage_gaps, partner_gaps, orphan_tests, summary}`

---

## 3. Gate Logic (Two Hats Principle)

```python
HAT_RULES = {
    "testlist":  {"src": False, "tests": False},
    "red":       {"src": False, "tests": True},   # test hat
    "green":     {"src": True,  "tests": False},   # code hat
    "refactor":  {"src": True,  "tests": False},   # refactor hat
    "done":      {"src": False, "tests": False},
    "none":      {"src": True,  "tests": True},    # TDD not active
}

def gate(path, session, is_tests):
    state = get_tdd_state(session)  # ledger read
    rules = HAT_RULES.get(state, HAT_RULES["none"])
    allowed = rules["tests"] if is_tests else rules["src"]
    if not allowed:
        hat = {"red": "test", "green": "code", "refactor": "refactor"}.get(state, "")
        reason = (f"⛔ TDD two-hats: wearing the {hat} hat. "
                  f"{'Only tests/ edits allowed.' if hat == 'test' else 'Only src/ edits allowed.'} "
                  f"(spec: two_hats_never_same_time)")
        return {"allowed": False, "reason": reason, "state": state}
    return {"allowed": True, "state": state, "tdd_mode": state != "none"}
```

---

## 4. AST Functions

### 4.1 `infer_target_src(test_file: Path) -> list[str]`
Parse `ast.ImportFrom` and `ast.Import` nodes; filter `agentx.*` modules; convert to `src/...py` paths.

### 4.2 `extract_test_references(test_file: Path, test_name: str) -> set[str]`
Walk the test function's AST; collect `ast.Attribute.attr` names (method calls like `session.create` → `"create"`).

### 4.3 `extract_defined_names(src_file: Path) -> set[str]`
Walk source AST; collect `ast.ClassDef.name` + public `ast.FunctionDef.name` (skip `_`-prefixed).

### 4.4 `extract_public_methods(src_file: Path) -> list[dict]`
Walk source AST; for each `ClassDef`, collect non-`_` `FunctionDef`/`AsyncFunctionDef` with `{"class", "method", "line", "is_abstract"}`. Skip `@dataclass` fields.

### 4.5 `find_untested_methods(src_file: Path, test_files: list[Path]) -> list[dict]`
Cross-reference `extract_public_methods(src)` against attribute accesses in all test files.

### 4.6 `verify_true_red(test_file, test_name, src_files) -> dict`
`extract_test_references` - `extract_defined_names` = missing references. `{"is_true_red": len(missing)>0, "missing": [...]}`.

### 4.7 `detect_red_anti_patterns(test_file, snapshot) -> list[str]`
- Count new `def test_*` functions since snapshot → batch-N-tests if >1
- Check each test has ≥1 assertion (bare `assert` or `self.assert*`)
- Check naming: `test_<subject>_<behavior>`
- Check no `pytest.mark.skip`/`xfail` decorators

### 4.8 `snapshot_source(src_file: Path) -> dict`
`extract_public_methods` + file hash → JSON to `.meta/.omt/tdd_snapshots/<stem>.json`.

### 4.9 `diff_snapshots(before, after) -> list[dict]`
Methods in `after` but not `before` → new methods (law 3 / new-behavior-during-refactor check).

---

## 5. Revert Mechanism

```python
def revert_file(path: str) -> dict:
    # 1. git checkout (tracked files)
    result = subprocess.run(["git", "checkout", "--", path], capture_output=True, cwd=REPO_ROOT)
    if result.returncode == 0:
        return {"reverted": True, "method": "git"}
    # 2. snapshot restore (untracked files)
    snapshot = get_pre_edit_snapshot(path)
    if snapshot:
        Path(path).write_text(snapshot)
        return {"reverted": True, "method": "snapshot"}
    return {"reverted": False}
```

The enforcer's `tool.execute.before` saves pre-edit file content for src/ and tests/ edits when TDD mode is active. The after-edit hook can restore from this snapshot if a violation is detected.

---

## 6. omt_enforcer.ts Changes

### 6.1 omt_phase extension
Add `tdd` optional parameter. Records `tdd_mode: true` in the phase ledger record when:
- Agent passes `tdd: true`, OR
- `task_type ∈ {major_feature, new_screen}` AND `phase == "Programming"`

### 6.2 New tools (thin wrappers)
```typescript
const omt_red = tool({
  description: "Declare a failing test (TDD Red). ...",
  args: {
    test_node: tool.schema.string(),
    target_src: tool.schema.string().optional(),
  },
  async execute(args, context) {
    const session = context?.sessionID || ""
    const res = await $`uv run scripts/omt/tdd_check.py start`
      .cwd(directory).quiet().nothrow()
    // (args via env or temp file to avoid shell escaping)
    const data = JSON.parse(res.stdout.toString() || "{}")
    return data.message || JSON.stringify(data)
  }
})
// omt_testlist, omt_green, omt_refactor, omt_done: same pattern
```

### 6.3 Gate in tool.execute.before
After existing src/ checks:
```typescript
if (isSrc(rel)) {
  // ... existing checks ...
  const unlock = getActiveUnlock(session)
  if (unlock?.record?.tdd_mode) {
    const res = await $`uv run scripts/omt/tdd_check.py gate --path ${rel} --session ${session}`
      .cwd(directory).quiet().nothrow()
    const data = JSON.parse(res.stdout.toString() || '{"allowed":true}')
    if (!data.allowed) throw new OmtBlock(data.reason)
    if (data.warning) await notify(data.warning)
  }
}
```

For tests/:
```typescript
if (isTests(rel)) {
  const unlock = getActiveUnlock(session)
  if (unlock?.record?.tdd_mode) {
    const res = await $`uv run scripts/omt/tdd_check.py gate --path ${rel} --is-tests --session ${session}`
      .cwd(directory).quiet().nothrow()
    const data = JSON.parse(res.stdout.toString() || '{"allowed":true}')
    if (!data.allowed) throw new OmtBlock(data.reason)
    return  // TDD allows tests/ — skip canary approval
  }
  // ... existing canary check ...
}
```

### 6.4 After-edit advisory
```typescript
if (isSrc(rel) && rel.endsWith(".py")) {
  // ... existing mvc_check.py ...
  const unlock = getActiveUnlock(session)
  if (unlock?.record?.tdd_mode) {
    const res = await $`uv run scripts/omt/tdd_check.py after-edit --path ${rel} --session ${session}`
      .cwd(directory).quiet().nothrow()
    const data = JSON.parse(res.stdout.toString() || "{}")
    if (data.action === "reverted") throw new OmtBlock(data.reason)
    if (data.advisories?.length) await notify(data.advisories.join("\n"))
  }
}
```

### 6.5 omt_complete extension
After existing artifact checks:
```typescript
const tddRes = await $`uv run scripts/omt/tdd_check.py validate-exit --feature ${feature}`
  .cwd(directory).quiet().nothrow()
const tddData = JSON.parse(tddRes.stdout.toString() || '{"ok":true}')
if (!tddData.ok) {
  return `⛔ TDD phase exit blocked:\n` + formatGaps(tddData)
}
```

---

## 7. Scaling to Task Type

| Task Type | TDD Mode | Default |
|---|---|---|
| bug_fix | Optional (tdd:true) | Off |
| minor_feature | Optional | Off |
| major_feature | Required | On (auto) |
| new_screen | Required | On (auto) |
| refactor | N/A (starts at REFACTOR) | Off |
| test | N/A | Off |
| docs | N/A | Off |

---

## 8. File Inventory

**New files:**
| File | Purpose |
|---|---|
| `scripts/omt/tdd_check.py` | TDD engine (subcommands, AST, pytest, ledger) |
| `tests/scripts/omt/test_tdd_check.py` | Unit + integration tests for tdd_check.py |

**Modified files:**
| File | Changes |
|---|---|
| `.opencode/plugin/omt_enforcer.ts` | +5 tools, +TDD gate in before/after hooks, +tdd_mode in omt_phase, +validate-exit in omt_complete |
| `.opencode/plugin/omt_status.ts` | +TDD state section |
| `tests/scripts/omt/test_omt_harness_e2e.py` | +TDD contract checks |
