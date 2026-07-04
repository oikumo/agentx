# Operation Spec 001: Agent Demo Operations

> **Phase:** Design — `omt_agent_guide.md §10` | **Feature:** feature_010.agent_demo_screen

Operation specifications for the new Controller/Model methods introduced by the
demo screen. Existing methods (`run_cycle`, `submit_goal`, `update_policy`,
`list_goals`, `list_rules`, `get_status`) are unchanged and not repeated here.

---

## Model operations

### `Agent.clear_state() -> None`
**Operation:** Clear all volatile agent state so a demo scenario can be re-seeded.

- **Preconditions:** Agent is initialized (constructors have run).
- **Exceptions:** None — best-effort. Only in-memory state is cleared; persisted
  snapshots/repositories are not modified, so saving before/after is unaffected.
- **Postconditions:** `list_goals()` returns an empty tree; `list_rules()`
  returns `[]`; volatile memory is empty; `agent.state == AgentState.PERCEIVING`.

### `GoalManager.clear() -> None`
**Operation:** Reset the goal tree to empty.
- **Preconditions:** none.
- **Exceptions:** none.
- **Postconditions:** `get_tree().nodes` is empty; `get_tree().root is None`.

### `MemoryManager.clear_volatile() -> None`
**Operation:** Empty the volatile memory cache.
- **Preconditions:** none.
- **Exceptions:** none.
- **Postconditions:** `count_volatile() == 0`.

---

## Controller operations

### `AgentController.reset_state() -> None`
**Operation:** Clear agent state in preparation for re-seeding a demo.

- **Preconditions:** Controller is wired to an Agent.
- **Exceptions:** Delegates to `Agent.clear_state()`; any error is raised to the
  caller (the View catches and logs it).
- **Postconditions:** Agent state cleared (see `Agent.clear_state()`); the view
  is refreshed via `show_status` / `refresh_goal_tree`.

### `AgentController.load_demo_scenario_by_name(name: str) -> bool`
**Operation:** Load and apply a named demo scenario:
clear → seed sandbox files → submit scenario goal → add scenario rules.

- **Preconditions:** Controller wired to an Agent; `name` is a non-empty string.
- **Exceptions:**
  - Unknown scenario name (`name` not in {"a","b"}, case-insensitive) → returns
    `False` without modifying state.
  - Sandbox file write failure → returns `False` (partial clear may have
    occurred; logged).
  - Policy rule compile/conflict rejection → the offending rule is skipped and
    the scenario still loads the remaining rules; returns `True` if the goal was
    installed.
- **Postconditions:** On success (`True`): scenario goal is ACTIVE, scenario
  rules are installed, the scenario's sandbox file(s) exist under
  `agent.config.sandbox_root`. On failure (`False`): an error message is sent to
  the view via `show_message`.

---

## View operations (AgentDemoScreen)

The View contains **no business logic** — each action delegates to a controller
method above and renders the result.

### `AgentDemoScreen.action_run_cycle() -> None`
Calls `controller.run_cycle()`; renders decision / action / reflection into the
log widget; refreshes the status bar.

### `AgentDemoScreen.action_reset() -> None`
Calls `controller.load_demo_scenario_by_name(self._scenario_name)` (clear +
re-seed); refreshes the summary + log.

### `AgentDemoScreen.action_back() -> None`
Calls `self.app.pop_screen()` → returns to the `AgentTUIScreen` (agent main
screen).
