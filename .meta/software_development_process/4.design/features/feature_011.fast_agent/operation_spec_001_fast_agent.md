# Operation Spec 001: Fast Agent Operations

> **Phase:** Design — `omt_agent_guide.md §10` | **Feature:** feature_011.fast_agent

Operation specifications for the new Controller method introduced by Fast
Agent, plus the View-side contracts for the four modals. Existing methods
(`submit_goal`, `run_cycle`, `list_pending_proposals`, `approve_proposal`,
`list_goals`, `get_status`, `save_snapshot`) are unchanged and not repeated
here — see `operation_spec_001_agent_operations.md` (feature_007).

---

## Controller operations

### `AgentController.get_cycle_summary() -> dict[str, Any]`
**Operation:** Return a read-only dict bundling the display data the Fast
Agent `RunningModal` needs after each cycle. Keeps the View free of Model-type
imports (`CycleResult`, `PolicyDecision`, `ActuatorResult`, `Proposal`).

- **Preconditions:** Controller is wired to an Agent.
- **Exceptions:** None — best-effort. If the Agent has run zero cycles, returns
  a summary with `cycle=0`, `phase="IDLE"`, `last_tool=None`,
  `last_action="(none)"`, `goal_status="PENDING"`, `pending_proposals=0`.
- **Postconditions:** No state change (pure query).
- **Returns:**
  ```python
  {
      "cycle": int,                    # number of cycles run so far (len of reflection log position heuristic)
      "phase": str,                    # agent.state.value, e.g. "PERCEIVING", "REFLECTING"
      "last_tool": str | None,         # tool_id from the last CycleResult.action_result, or None
      "last_action": str,              # human-readable: f"{action.type.value} {action.parameters}" truncated to 80 chars
      "goal_status": str,              # root goal status value, or "NONE" if no root goal
      "pending_proposals": int,        # len(list_pending_proposals())
  }
  ```
- **Implementation note:** `cycle` is derived from a counter the controller
  maintains (a new `self._cycle_count` int incremented in `run_cycle()`), since
  `CycleResult` does not carry a cycle index. This is a Controller-side display
  counter, not Model state — it is **not** persisted and resets when the
  controller is reconstructed (e.g. on session resume). Acceptable for Fast
  Agent's "current run" display. (If persistence of cycle count is later
  needed, that's a feature_007 Model change, out of scope here.)

---

## View operations (Fast Agent modals)

The View contains **no business logic** — each modal delegates to a controller
method and renders the result. All `dismiss(value)` payloads are plain dicts
or strings (no Model types cross the modal boundary).

### `GoalModal` — `ModalScreen[dict]`
**Purpose:** Capture the user's natural-language goal (+ optional constraints).

- **Widgets:**
  - `Static` — prompt: "What do you want the agent to do?"
  - `Input(id="goal-input")` — the goal description (required, non-empty).
  - `Collapsible(title="Advanced")` containing `Input(id="constraints-input")`
    — optional free-text constraints (default empty; Fast Agent does not parse
    these into policy rules in v1 — they are stored as a memory fact via
    `controller.remember_constraint(text)` if a future iteration adds it; for
    now they are captured but unused, with a `(optional, not used yet)` hint).
  - `Button("Start", id="btn-start", variant="success")`
  - `Button("Cancel", id="btn-cancel", variant="default")`
- **Bindings:** `escape` → `action_cancel` (dismiss with `None`).
- **Dismiss values:**
  - Start: `dismiss({"description": str, "constraints": str})`
  - Cancel / escape: `dismiss(None)`
- **Validation:** Start button disabled (or shows a notify error) if
  `goal-input` is empty.

### `RunningModal` — `ModalScreen[dict]`
**Purpose:** Auto-run cycles and show live status.

- **Widgets:**
  - `Static#goal-display` — "Goal: <description>"
  - `Static#status-line` — refreshed each tick: "Cycle N · PHASE · tool: X · last: Y"
  - `Button("Pause", id="btn-pause", variant="default")` ↔ toggles to "Resume"
  - `Button("Stop", id="btn-stop", variant="error")`
- **Bindings:** `escape` → `action_stop` (same as Stop button).
- **Internal state:**
  - `_paused: bool = False`
  - `_cycle_count: int = 0` (mirrors controller's count for display)
  - `_last_summary: dict` (for the Result modal)
- **Lifecycle:**
  - `on_mount()` → `self._tick()`
  - `_tick()`:
    1. If `_paused` or not running → return.
    2. `result = controller.run_cycle()`; `_cycle_count += 1`.
    3. `summary = controller.get_cycle_summary()`; `_last_summary = summary`.
    4. Refresh `#status-line`.
    5. If `controller.list_pending_proposals()` non-empty → push
       `ReflectionModal(pending_proposals_as_dicts)` with
       `callback=self._on_reflection`; return (pause).
    6. Read root goal status from `controller.list_goals()`. If terminal
       (COMPLETED/FAILED/ABANDONED) → `dismiss({"outcome": status.lower(),
       "summary": summary})`; return.
    7. If `_cycle_count >= MAX_CYCLES (50)` → `dismiss({"outcome": "capped",
       "summary": summary})`; return.
    8. Else `self.call_after_refresh(self._tick)` (schedule next cycle).
  - `action_pause_resume()` — toggle `_paused`; if resuming, call
    `self.call_after_refresh(self._tick)`.
  - `action_stop()` — `dismiss({"outcome": "stopped", "summary": _last_summary})`.
  - `_on_reflection(choice)` — `choice ∈ {"approve", "dismiss", "stop"}`:
    - `"approve"`: `entry_id, idx = pending[0]["entry_id"], pending[0]["idx"]`;
      `controller.approve_proposal(entry_id, idx)`; resume (`call_after_refresh(_tick)`).
    - `"dismiss"`: resume.
    - `"stop"`: `dismiss({"outcome": "stopped", "summary": _last_summary})`.
- **Dismiss value:** `{"outcome": str, "summary": dict}`.

### `ReflectionModal` — `ModalScreen[str]`
**Purpose:** Show a pending self-improvement proposal and ask the user what to
do.

- **Constructor:** `ReflectionModal(proposals: list[dict])` where each dict is
  `{"entry_id": str, "idx": int, "type": str, "rationale": str, "content": dict}`.
  (The `RunningModal` converts `controller.list_pending_proposals()` tuples
  into these dicts so this modal imports no Model types.)
- **Widgets:**
  - `Static` — "The agent wants to improve itself:"
  - `Static` (per proposal, first 3 shown) —
    `#{n} {type}: {rationale}` + dim `{content}`.
  - `Button("Approve", id="btn-approve", variant="success")`
  - `Button("Dismiss", id="btn-dismiss", variant="default")`
  - `Button("Stop", id="btn-stop", variant="error")`
- **Bindings:** `escape` → `action_dismiss_choice` (Dismiss).
- **Dismiss values:** `"approve"` | `"dismiss"` | `"stop"`.

### `ResultModal` — `ModalScreen[str]`
**Purpose:** Show the run outcome and offer next actions.

- **Constructor:** `ResultModal(outcome: str, summary: dict)` where `outcome ∈
  {"completed", "failed", "abandoned", "stopped", "capped"}`.
- **Widgets:**
  - `Static` — outcome line:
    - `completed` → "✓ Goal achieved in {cycle} cycles."
    - `failed` → "✗ Goal failed after {cycle} cycles."
    - `abandoned` → "○ Goal abandoned."
    - `stopped` → "■ Goal stopped after {cycle} cycles."
    - `capped` → "⏸ Reached cycle cap (50)."
  - `Static` — last action summary.
  - `Button("Save session", id="btn-save", variant="primary")`
  - `Button("New goal", id="btn-new", variant="success")`
  - `Button("Back to menu", id="btn-back", variant="default")`
- **Bindings:** `escape` → `action_back` (Back to menu).
- **Dismiss values:** `"save"` | `"new"` | `"back"`.
- **Note on Save:** `FastAgentTUIScreen._on_result("save")` calls
  `controller.save_snapshot()`, shows a notify "Session saved", and **re-pushes
  the same ResultModal** (so the user still picks New/Back to leave). Save does
  not dismiss. This keeps the modal flow simple (Save is a side-effect, not an
  exit).

---

## FastAgentTUIScreen (host) operations

### `FastAgentTUIScreen.on_mount() -> None`
Pushes `GoalModal` with `callback=self._on_goal`.

### `FastAgentTUIScreen._on_goal(value: dict | None) -> None`
- `None` (Cancel) → `self.app.pop_screen()` (pop the host → back to Main).
- `dict` → `controller.submit_goal(value["description"],
  success_criteria=SuccessCriteria(kind="manual"))`; push `RunningModal(controller)`
  with `callback=self._on_running`.

### `FastAgentTUIScreen._on_running(value: dict) -> None`
Push `ResultModal(value["outcome"], value["summary"])` with
`callback=self._on_result`.

### `FastAgentTUIScreen._on_result(action: str) -> None`
- `"save"` → `controller.save_snapshot()`; `self.notify("Session saved")`;
  re-push `ResultModal(current_outcome, current_summary)` (store them on self).
- `"new"` → push `GoalModal` again (fresh goal, same agent/controller — the
  previous goal remains in the tree but is no longer the root focus; a new
  root goal is submitted. Acceptable for Fast Agent v1; advanced goal-tree
  management lives in the Advanced Agent screen).
- `"back"` → `self.app.pop_screen()` (pop FastAgentTUIScreen → Main).

### `FastAgentTUIScreen.action_back() -> None`
`self.app.pop_screen()` — bound to `escape` on the host screen (not the
modals). Because modals sit on top, `escape` hits the modal first; the host's
`escape` only fires when no modal is pushed (edge case: between modals).

---

## Adapter operations

### `AgentAdapter.create_fast(config, ai_service=None, resume=True) -> tuple[Agent, AgentController, FastAgentTUIScreen]`
**Operation:** Build a wired Fast Agent triad. Mirrors `AgentAdapter.create`
but uses `FastAgentTUIScreen` + `FastAgentTUIView` instead of `AgentTUIScreen`.

- Calls `create_agent(config, ai_service, resume)` → `(agent, controller)`.
- Builds `view = FastAgentTUIView()`.
- `controller.set_view(view)`.
- Builds `screen = FastAgentTUIScreen(controller)`.
- Returns `(agent, controller, screen)`.

No new Model-side logic; the no-op `FastAgentTUIView` swallows the controller's
`show_status`/`show_reflection_log`/`show_memory_view`/`show_policy_editor`/
`refresh_goal_tree`/`show_message` callbacks during `run_cycle()` — the
`RunningModal` queries the controller explicitly for display data instead.
