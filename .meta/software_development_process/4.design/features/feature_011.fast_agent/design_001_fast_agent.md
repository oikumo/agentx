# Design 001: Fast Agent

> **Phase:** Design — `omt_agent_guide.md §2`, §5–§10 | **Feature:** feature_011.fast_agent
> **Extends:** feature_007.agentx_intelligent_agent_behaviour (reuses its Agent/Controller/tools)
> **Task type:** new_screen

## 1. Purpose & Scope

A new **"⚡ Fast Agent"** main-menu option (`f` key) that exposes the existing
feature_007 `Agent` through a **modal-dialog-driven UX** — a stack of Textual
`ModalScreen`s (`Goal` → `Running` → `Reflection` → `Result`). The user types a
plain-English goal, the agent auto-runs perceive→decide→act→reflect cycles, and
forward progress pauses **only** when the reflection engine emits a
self-improvement proposal (or the user presses Pause/Stop). This is the first
use of `textual.screen.ModalScreen` in the codebase.

**Done =** from the main menu, pressing `f` (or clicking `⚡ Fast Agent`)
opens a goal modal; the user enters a natural-language goal and clicks Start;
the agent auto-runs cycles showing live status (cycle #, phase, last tool,
last action); if a reflection proposal appears, a Reflection modal pauses the
run until the user Approves/Dismisses/Stops; when the goal reaches a terminal
status (COMPLETED/FAILED/ABANDONED) or the user Stops, a Result modal offers
Save session / New goal / Back; the existing `🤖 Agent` button is relabeled
`⚙️ Advanced Agent` and its behaviour is unchanged.

**Out of scope:** new tools, new persistence schema, changes to the Agent cycle
algorithm, changes to `AgentController`'s existing API, changes to the Advanced
Agent screen. Fast Agent is a **View-only addition** that drives the existing
controller. The single Model-side concession is a read-only helper
`AgentController.get_cycle_summary()` (§7) that bundles display data so the
View does not reach into Model types — this is a thin query method, not
business logic.

## 2. Use Case (lightweight analysis, §12 new_screen)

**UC-1: Run a fast agent goal**
1. User is on the Main screen and presses `f` (or clicks `⚡ Fast Agent`).
2. `MainController.show_fast_agent()` builds the agent triad via
   `AgentAdapter.create_agent(config, resume=True)` (auto-resume latest
   snapshot; start fresh if none) and pushes `FastAgentTUIScreen`.
3. `FastAgentTUIScreen.on_mount()` pushes `GoalModal`.
4. User types a goal description (e.g. "find python files with TODO and list
   them") and optionally toggles `[Advanced]` to enter constraints. Clicks
   **Start**. `GoalModal.dismiss({"description": ..., "constraints": ...})`.
5. `FastAgentTUIScreen` receives the callback, calls
   `controller.submit_goal(description, success_criteria=SuccessCriteria())`
   (no policy rules by default; constraints under Advanced map to at most one
   `EXECUTE_TOOL`-free `INFORM` rule, kept out of the user's view), then pushes
   `RunningModal`.
6. `RunningModal.on_mount()` starts an auto-run loop. Each iteration:
   `controller.run_cycle()` → `RunningModal` refreshes its 4 status fields
   (cycle #, phase, last tool, last action) from
   `controller.get_cycle_summary()` → checks `controller.list_pending_proposals()`
   → if non-empty, pushes `ReflectionModal` and pauses → checks
   `controller.list_goals()` root status → if terminal, dismisses with
   `{"outcome": "completed"|"failed"|"abandoned"}` → else loops.
7. If `ReflectionModal` is shown: user clicks **Approve** (applies the first
   pending proposal via `controller.approve_proposal(...)`, dismisses), **Dismiss**
   (dismisses without applying — the proposal remains pending but the run
   resumes), or **Stop** (dismisses with `{"outcome": "stopped"}`).
8. `RunningModal` dismisses with the outcome. `FastAgentTUIScreen` pushes
   `ResultModal(outcome, summary)`.
9. User clicks **Save session** (`controller.save_snapshot()`),
   **New goal** (pops `ResultModal`, re-pushes `GoalModal`), or **Back**
   (pops `ResultModal` then pops `FastAgentTUIScreen` → back to Main).

**Operations extracted (existing):** `submit_goal`, `run_cycle`,
`list_pending_proposals`, `approve_proposal`, `list_goals`, `get_status`,
`save_snapshot`.
**Operations extracted (new, View-facing query):** `get_cycle_summary`.

## 3. Components / screens affected

| Component | Layer | Change |
|-----------|-------|--------|
| `agent/view/tui/fast_agent_screen.py` | View (new) | `FastAgentTUIScreen(Screen)` — modal-stack host; `escape` → pop_screen |
| `agent/view/tui/fast_agent_modals.py` | View (new) | `GoalModal`, `RunningModal`, `ReflectionModal`, `ResultModal` — all `ModalScreen` subclasses |
| `agent/view/tui/fast_agent_view.py` | View (new) | `FastAgentTUIView` — no-op `IAgentViewPartner` impl (virtual-subclass-registered) so controller UI callbacks don't crash during a cycle |
| `agent/controller/agent_controller.py` | Controller (edit) | add `get_cycle_summary() -> dict[str, Any]` (read-only query bundling display data) |
| `agent/adapter.py` | View/wiring (edit) | add `AgentAdapter.create_fast(config, ai_service=None, resume=True) -> tuple[Agent, AgentController, FastAgentTUIScreen]` |
| `ui/screens/main/main_controller.py` | Controller (edit) | add `show_fast_agent()`, `get_fast_agent_controller()`; relabel existing agent button text to "Advanced Agent" (display only — method name `show_agent` unchanged for backward compat with typed `agent` command) |
| `ui/tui/screens/main_screen.py` | View (edit) | add `Binding("f", "open_fast_agent", "Fast Agent")`, 5th button `⚡ Fast Agent` (variant="warning"), `action_open_fast_agent()`, `on_button_pressed` mapping; relabel `btn-agent` text to `⚙️ Advanced Agent`; relabel its binding description to "Advanced Agent" |

No new Abstract Partner interface: `FastAgentTUIView` implements the existing
`IAgentViewPartner` (as a virtual subclass, same pattern as `AgentTUIScreen` /
`AgentDemoScreen`). `FastAgentTUIScreen` itself is **not** an
`IAgentViewPartner` — it is a plain `Screen` that owns the modal stack and
talks to the controller directly; the no-op `FastAgentTUIView` is the partner
the controller calls back into during `run_cycle()`.

## 4. Static structure (classes & files)

| File | Layer | Responsibility |
|------|-------|----------------|
| `agent/view/tui/fast_agent_screen.py` | View | `FastAgentTUIScreen(Screen)` — owns controller, pushes modals, handles their dismiss callbacks |
| `agent/view/tui/fast_agent_modals.py` | View | 4 `ModalScreen` subclasses; each `dismiss(value)` with a typed dict; no Model imports |
| `agent/view/tui/fast_agent_view.py` | View | `FastAgentTUIView` — no-op `IAgentViewPartner` (registered via `IAgentViewPartner.register(FastAgentTUIView)`) |
| `agent/controller/agent_controller.py` | Controller | `+ get_cycle_summary() -> dict` |
| `agent/adapter.py` | wiring | `+ AgentAdapter.create_fast(...)` |
| `ui/screens/main/main_controller.py` | Controller | `+ show_fast_agent()`, `+ get_fast_agent_controller()` |
| `ui/tui/screens/main_screen.py` | View | `+ Binding f`, `+ btn-fast-agent`, `+ action_open_fast_agent()`; relabel existing agent button |

### Design class diagram

```
┌────────────────────────────────────┐        ┌───────────────────────────────────┐
│ MainTUIScreen  (existing, edit)    │        │ FastAgentTUIScreen (Screen, new)  │
│  + Binding("f","open_fast_agent")  │        │  - _controller: AgentController   │
│  + btn-fast-agent ("⚡ Fast Agent") │───────▶│  - _view: FastAgentTUIView        │
│  + btn-agent    ("⚙️ Advanced …")   │ push   │  on_mount(): push GoalModal       │
│  action_open_fast_agent()          │        │  _on_goal(value): submit_goal;    │
└────────────────────────────────────┘        │     push RunningModal             │
                                              │  _on_running(outcome):            │
                                              │     push ResultModal              │
                                              │  _on_result(action):              │
                                              │     save | new_goal | back        │
                                              │  action_back(): app.pop_screen()  │
                                              └───────────────┬───────────────────┘
                                                              │ pushes (ModalScreen stack)
                              ┌───────────────────────────────┼───────────────────────┐
                              ▼                               ▼                       ▼
              ┌───────────────────────────┐     ┌─────────────────────────┐ ┌─────────────────────┐
              │ GoalModal (ModalScreen)   │     │ RunningModal (ModalScreen)│ │ ResultModal         │
              │  - Input#goal-input       │     │  - Static#status-line    │ │  (ModalScreen)      │
              │  - Input#constraints (adv)│     │  - cycle #, phase,       │ │  outcome, summary   │
              │  - [Start] [Cancel]       │     │    last tool, last action│ │  [Save][New][Back]  │
              │  dismiss({"description",  │     │  - [Pause][Stop]         │ │  dismiss("save"|    │
              │           "constraints"}) │     │  on_mount: auto-run loop │ │     "new"|"back")   │
              │                           │     │  dismiss({"outcome":…})  │ │                     │
              └───────────────────────────┘     │ ┌──────────────────────┐ │ └─────────────────────┘
                              ▲                 │ │ ReflectionModal      │ │
                              │                 │ │  (ModalScreen, pushed│ │
                              │                 │ │   by RunningModal    │ │
                              │                 │ │   when proposals)    │ │
                              │                 │ │  [Approve][Dismiss]  │ │
                              │                 │ │  [Stop]              │ │
                              │                 │ │  dismiss("approve"|  │ │
                              │                 │ │     "dismiss"|"stop")│ │
                              │                 │ └──────────────────────┘ │
                              │                 └─────────────────────────┘
                              │ calls (View → Controller)
                              ▼
              ┌───────────────────────────────────────────────────────────┐
              │ AgentController (existing, +1 method)                     │
              │  submit_goal / run_cycle / list_pending_proposals /        │
              │  approve_proposal / list_goals / get_status / save_snapshot│
              │  + get_cycle_summary() -> dict   ← NEW (View-facing query) │
              └─────────────────────────┬─────────────────────────────────┘
                                        │ delegates
                                        ▼
              ┌───────────────────────────────────────────────────────────┐
              │ Agent (existing facade, UNCHANGED)                        │
              │  perceive / decide / act / reflect / persist / resume_…   │
              └───────────────────────────────────────────────────────────┘

              ┌───────────────────────────────────────────────────────────┐
              │ FastAgentTUIView  (no-op IAgentViewPartner, new)          │
              │  show_status/show_reflection_log/show_memory_view/        │
              │  show_policy_editor/refresh_goal_tree/show_message → pass │
              │  (registered: IAgentViewPartner.register(FastAgentTUIView))│
              └───────────────────────────────────────────────────────────┘
```

## 5. Modal flow & state machine

```
                 ┌─────────────────────┐
                 │ FastAgentTUIScreen  │  (host Screen; owns controller + view)
                 │   on_mount →        │
                 └─────────┬───────────┘
                           ▼
                 ┌─────────────────────┐
                 │      GoalModal      │   ← Input: description (+ optional Advanced constraints)
                 │   dismiss(          │
                 │     {"description", │
                 │      "constraints"})│
                 └─────────┬───────────┘
                           │ callback: submit_goal → push RunningModal
                           ▼
                 ┌─────────────────────┐  auto-run loop (set_interval-free; driven by
                 │    RunningModal     │   a textual worker / call_later chain)
                 │   on_mount:         │
                 │     _tick() →       │
                 │       run_cycle()   │
                 │       refresh status│
                 └─────────┬───────────┘
                           │ each tick checks:
                           │   1. list_pending_proposals() non-empty?  → push ReflectionModal (pause)
                           │   2. root goal terminal?                  → dismiss({"outcome": status})
                           │   3. user pressed Pause/Stop?             → dismiss({"outcome": "stopped"})
                           │   4. otherwise                           → schedule next _tick
                           │
                           ▼
              ┌────────────────────────┐   user choice:
              │   ReflectionModal      │   "approve"  → approve_proposal(entry_id, idx); resume
              │  (pushed by Running)   │   "dismiss"  → resume (proposal stays pending)
              │  dismiss("approve"|    │   "stop"     → RunningModal dismisses with {"outcome":"stopped"}
              │         "dismiss"|     │
              │         "stop")        │
              └────────────────────────┘
                           │
                           ▼ (when RunningModal dismisses)
                 ┌─────────────────────┐
                 │     ResultModal     │   ← outcome ∈ {completed, failed, abandoned, stopped}
                 │  dismiss("save" |   │     + summary (cycles run, proposals applied, last action)
                 │         "new"  |    │
                 │         "back")     │
                 └─────────┬───────────┘
                           │ callback:
                           │   "save" → controller.save_snapshot(); stay on ResultModal? → re-push ResultModal
                           │           (or: save then dismiss to "back"). Decision: save just notifies; user
                           │           then picks New/Back to actually leave. Simpler: Save is a side-effect
                           │           button that calls save_snapshot() and notifies; it does NOT dismiss.
                           │   "new"  → pop ResultModal, push GoalModal again (fresh goal, same agent)
                           │   "back" → pop ResultModal, pop FastAgentTUIScreen → Main
                           ▼
                      (back to Main, or new GoalModal)
```

### Goal terminal-status detection

After each `run_cycle()`, `RunningModal` calls `controller.list_goals()` and
inspects the root goal's `status`. The agent's reflection engine may set a
goal to `COMPLETED`/`FAILED`/`ABANDONED` based on `SuccessCriteria` (C6 fix
scoped completion via `SuccessCriteria.tool_id`). If the root goal is
terminal, the run stops and `ResultModal` is shown. If the user has not
configured success criteria (the Fast Agent default — `SuccessCriteria()` with
`kind="manual"`), **the goal never auto-completes**; the run continues until
the user presses Stop. This is the intended Fast Agent behaviour: the user
decides when the goal is "done enough" by pressing Stop.

> **Design note:** to keep the UX honest, `GoalModal`'s default is
> `SuccessCriteria(kind="manual")`. The Result modal for a "stopped" run uses
> the label "Goal stopped" (not "failed") so the user understands stopping is
> the normal termination path in Fast Agent.

## 6. Functional flow (sequence)

```
UC-1 trigger (f key / "⚡ Fast Agent" button)
  MainTUIScreen.action_open_fast_agent()
    └─ self._controller.show_fast_agent()           # builds triad, resume=True
         └─ AgentAdapter.create_agent(config, resume=True)
         └─ FastAgentTUIView()  (no-op partner)
         └─ controller.set_view(view)
    └─ fast_controller = self._controller.get_fast_agent_controller()
    └─ self.app.push_screen(FastAgentTUIScreen(fast_controller))

  FastAgentTUIScreen.on_mount()
    └─ self.app.push_screen(GoalModal())            # first modal

  GoalModal: user types goal → clicks Start
    └─ modal.dismiss({"description": "...", "constraints": ""})

  FastAgentTUIScreen._on_goal(value)  [push_screen callback]
    └─ controller.submit_goal(value["description"],
    │                            success_criteria=SuccessCriteria(kind="manual"))
    └─ self.app.push_screen(RunningModal(controller))

  RunningModal.on_mount()
    └─ self._tick()                                 # start auto-run

  RunningModal._tick()
    └─ result = controller.run_cycle()
    └─ summary = controller.get_cycle_summary()     # cycle #, phase, last tool, last action
    └─ self._refresh(summary)
    └─ pending = controller.list_pending_proposals()
    │   if pending:
    │     self.app.push_screen(ReflectionModal(pending), callback=self._on_reflection)
    │     return  # pause; _tick resumes from _on_reflection
    └─ root_status = controller.list_goals().root goal status
    │   if root_status in {COMPLETED, FAILED, ABANDONED}:
    │     self.dismiss({"outcome": root_status.value.lower(), "summary": summary})
    │     return
    └─ self.call_after_refresh(self._tick)          # schedule next cycle (back-to-back)

  [User presses Stop in RunningModal]
    └─ self.dismiss({"outcome": "stopped", "summary": last_summary})

  [ReflectionModal: user clicks Approve]
    └─ modal.dismiss("approve")
  RunningModal._on_reflection(choice)
    └─ if choice == "approve":
    │     entry_id, idx, _ = pending[0]
    │     controller.approve_proposal(entry_id, idx)
    │   # "dismiss": do nothing (proposal stays pending)
    │   # "stop": self.dismiss({"outcome":"stopped", ...}); return
    └─ self.call_after_refresh(self._tick)          # resume

  [RunningModal dismisses → FastAgentTUIScreen._on_running(outcome)]
    └─ self.app.push_screen(ResultModal(outcome, summary))

  ResultModal: user clicks Back
    └─ modal.dismiss("back")
  FastAgentTUIScreen._on_result(action)
    └─ if action == "save": controller.save_snapshot(); re-show ResultModal (or notify)
    │   if action == "new": self.app.push_screen(GoalModal())   # fresh goal
    │   if action == "back": self.app.pop_screen()              # pop FastAgentTUIScreen → Main
```

## 7. Operation specifications

(See `operation_spec_001_fast_agent.md` for the full pre/post-conditions.)

**New operations:**
- `AgentController.get_cycle_summary() -> dict[str, Any]` — read-only query
  returning `{"cycle": int, "phase": str, "last_tool": str|None,
  "last_action": str, "goal_status": str, "pending_proposals": int}`. Bundles
  display data so the View never imports `CycleResult`/`PolicyDecision`/
  `ActuatorResult` Model types.

**Reused operations (unchanged):** `submit_goal`, `run_cycle`,
`list_pending_proposals`, `approve_proposal`, `list_goals`, `get_status`,
`save_snapshot`, `AgentAdapter.create_agent`.

## 8. MVC++ self-check

- [x] **View imports no Model.** `fast_agent_screen.py`, `fast_agent_modals.py`,
      `fast_agent_view.py` import nothing from `agentx.agent.model.*` or
      `agentx.agent.types`. They talk to `AgentController` only, and receive
      display data as plain dicts via `get_cycle_summary()` / `get_status()`.
      The `Goal`/`Proposal` types from `list_goals()`/`list_pending_proposals()`
      are accessed only for their `.status`/`.description`/`.type`/`.rationale`
      string attributes — never constructed or imported by the View (the
      controller returns them; the View reads attributes duck-typed). To be
      fully MVC++-clean, `get_cycle_summary()` also returns the pending
      proposals as plain dicts so the ReflectionModal doesn't touch `Proposal`.
      See operation_spec §"ReflectionModal data".
- [x] **Model imports no ui.** No Model file is edited.
- [x] **No new Abstract Partner.** `FastAgentTUIView` implements the existing
      `IAgentViewPartner` (virtual subclass registration, same as
      `AgentTUIScreen` / `AgentDemoScreen`).
- [x] **SQL only in `*_db.py` / repositories** (unchanged).
- [x] **No `*Controller` under `model/`** (unchanged).
- [x] **No blocking console input inside Textual screens.** All user input is
      via modal widgets (Input, Button). The auto-run loop uses
      `call_after_refresh` (Textual's cooperative scheduler), not `time.sleep`
      or blocking `input()`.
- [x] **`uv run scripts/omt/mvc_check.py` passes** for touched files (verified
      in T-phase).

## 9. Auto-run loop design (Textual worker)

`RunningModal._tick()` is **not** a `set_interval` callback. It is a
cooperative chain: each `_tick` runs one `controller.run_cycle()` synchronously
(cycles are fast — local tool calls + optional AI reflection), refreshes the
display, then schedules the next `_tick` via `self.call_after_refresh(self._tick)`.
This yields control back to the Textual event loop between cycles so the UI
stays responsive (the user can press Pause/Stop, and the ReflectionModal can
interrupt).

**Pause** sets a `self._paused = True` flag; `_tick` checks it at the top and
returns without scheduling. **Resume** (from `_on_reflection` or a Resume
button) clears the flag and calls `self.call_after_refresh(self._tick)`.

**Stop** calls `self.dismiss({"outcome": "stopped", ...})` — Textual pops the
modal and the host's `_on_running` callback fires.

**Max cycles safety:** a hard cap `MAX_CYCLES = 50` prevents an infinite loop
if the goal never terminates and the user walks away. At the cap,
`RunningModal` dismisses with `{"outcome": "capped"}` and `ResultModal` shows
"Reached cycle cap (50) — stop or continue?" with a Continue button that
re-pushes `RunningModal` with the counter reset. (This is a safety valve, not
normal UX.)

## 10. Testing plan (T-phase)

- **Unit** (`tests/features/feature_011/test_fast_agent_modals.py`):
  - `GoalModal` dismiss value shape (description + constraints).
  - `ResultModal` dismiss value ∈ {"save", "new", "back"}.
- **Unit** (`tests/features/feature_011/test_controller_summary.py`):
  - `AgentController.get_cycle_summary()` returns the expected keys before/after
    a cycle; `last_tool`/`last_action` populate correctly.
- **Integration** (`tests/features/feature_011/test_fast_agent_flow.py`):
  Textual pilot e2e:
  - Mount `FastAgentTUIScreen` → `GoalModal` is shown.
  - Type a goal → click Start → `RunningModal` shown → at least one cycle runs.
  - With a stubbed AI service that emits a proposal → `ReflectionModal` shown.
  - Click Approve → proposal applied → `RunningModal` resumes.
  - Press Stop → `ResultModal` shown with outcome "stopped".
  - Click Back → back to host (Main or test harness).
  - Click New goal → `GoalModal` re-shown.
- **MVC++** (`tests/features/feature_011/test_mvc_fast_agent.py`):
  - `mvc_check.py` returns 0 errors on touched files.
  - `fast_agent_*.py` View files import no `agentx.agent.model.*` /
    `agentx.agent.types` symbols (static import scan).
  - `FastAgentTUIView` is a virtual subclass of `IAgentViewPartner`
    (`issubclass(FastAgentTUIView, IAgentViewPartner) is True`).

## 11. Risks & mitigations

| Risk | Mitigation |
|---|---|
| `call_after_refresh` chain stalls if the modal is popped mid-cycle | `_tick` checks `self.is_running` (set False in `on_unmount`); bails out cleanly. |
| Reflection proposals pile up if user keeps Dismissing | Each cycle re-checks `list_pending_proposals()`; if non-empty, it re-pushes `ReflectionModal` rather than running another cycle. So at most one cycle runs between reflection prompts. |
| User confusion: goal never auto-completes (manual success criteria) | `GoalModal` shows hint text: "The agent runs until you press Stop." `ResultModal` labels the outcome "Goal stopped" (neutral), not "failed". |
| Existing `agent` typed command and `a` key still open the Advanced Agent screen | Unchanged — only the button *label* changes from "🤖 Agent" to "⚙️ Advanced Agent". The `a` key binding description changes to "Advanced Agent" but the action (`action_open_agent`) is untouched. |
| 5th menu button wraps the 4×1 grid awkwardly | Change `MenuGrid` grid-size from `4 1` to `3 2` (3 cols × 2 rows) so 5 buttons lay out as 3+2. CSS-only change in `main_screen.py`. |
| `ModalScreen` first-use in codebase — unknown Textual API shape | Verified against Textual docs: `ModalScreen` is a `Screen` subclass; `app.push_screen(ModalScreen(...), callback=fn)` and `modal.dismiss(value)` are the standard patterns. No new dependency. |
