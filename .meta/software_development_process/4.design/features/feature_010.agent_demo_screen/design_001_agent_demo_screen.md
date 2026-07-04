# Design 001: Agent Demo Screen

> **Phase:** Design — `omt_agent_guide.md §2`, §5–§10 | **Feature:** feature_010.agent_demo_screen
> **Extends:** feature_007.agentx_intelligent_agent_behaviour (reuses its Agent/Controller/tools)
> **Task type:** new_screen

## 1. Purpose & Scope

A dedicated Textual screen that demonstrates feature_007's intelligent-agent
behaviour with **one trigger**. When the `demo` command (or `d` key) is fired,
the agent is populated with a ready-made **goal + policy rules + sandbox file**
(scenario A or B, selectable at runtime) and one cycle auto-runs so the user
immediately sees perceive → decide → act → reflect.

**Done =** from the Agent screen, pressing `d` (or typing `demo [a|b]`) opens a
demo screen seeded with a scenario; the screen offers **Run Cycle**, **Reset
(re-seed)**, and **Back to Agent** buttons; Reset clears goals/rules/memory and
reloads the scenario; Back returns to the `AgentTUIScreen` (the agent main
screen).

**Out of scope:** new tools, new persistence schema, changes to the Agent cycle
algorithm. The demo only orchestrates existing controller APIs.

## 2. Use Case (lightweight analysis, §12 new_screen)

**UC-1: Run an agent demo**
1. User opens the Agent screen (`a` from MainTUIScreen).
2. User presses `d` (or types `demo` / `demo b`).
3. System loads the chosen scenario: clears prior demo state, seeds a sandbox
   file, submits the scenario goal, adds the scenario policy rules.
4. System opens `AgentDemoScreen` showing the scenario summary (goal + rules)
   and auto-runs one cycle, narrating perceive/decide/act/reflect in the log.
5. User presses **Run Cycle** to step further, **Reset** to re-seed, or
   **Back**/`Escape` to return to the Agent screen.

**Operations extracted:** `load_demo_scenario(name)`, `reset_state()`,
`run_cycle()`, `get_status()`, `list_goals()`, `list_rules()`.

## 3. Components / screens affected

| Component | Layer | Change |
|-----------|-------|--------|
| `agent/demo/scenarios.py` | Model/data (new) | `DemoScenario` dataclass + `SCENARIO_A/B` + `seed_sandbox_files()` |
| `agent/model/goal/manager.py` | Model (edit) | add `clear()` |
| `agent/model/memory/manager.py` | Model (edit) | add `clear_volatile()` |
| `agent/model/agent.py` | Model (edit) | add `clear_state()` |
| `agent/controller/agent_controller.py` | Controller (edit) | add `reset_state()`, `load_demo_scenario_by_name(name)` |
| `agent/view/tui/demo_screen.py` | View (new) | `AgentDemoScreen(Screen)` — buttons + live log |
| `agent/view/tui/agent_screen.py` | View (edit) | add `demo [a|b]` command + `d` keybinding → push demo screen |

No new Abstract Partner interface is required: `AgentDemoScreen` is a View that
talks to the existing `AgentController` only (no new controller is created — the
demo reuses the C5-shared agent controller). The screen is registered as a
virtual subclass of `IAgentViewPartner` (same pattern as `AgentTUIScreen`) so the
controller's `set_view` cast passes (m9).

## 4. Static structure (classes & files)

| File | Layer | Responsibility |
|------|-------|----------------|
| `agent/demo/__init__.py` | package | docstring + triad map |
| `agent/demo/scenarios.py` | Model/data | `DemoScenario` dataclass; `SCENARIO_A`, `SCENARIO_B`; `seed_sandbox_files(scenario, sandbox_root)` |
| `agent/model/goal/manager.py` | Model | `GoalManager.clear()` — reset tree to empty |
| `agent/model/memory/manager.py` | Model | `MemoryManager.clear_volatile()` — empty volatile cache |
| `agent/model/agent.py` | Model | `Agent.clear_state()` — clear goals + rules + volatile memory; state→PERCEIVING |
| `agent/controller/agent_controller.py` | Controller | `reset_state()`; `load_demo_scenario_by_name(name)` |
| `agent/view/tui/demo_screen.py` | View | `AgentDemoScreen` — render scenario + log; buttons call controller |
| `agent/view/tui/agent_screen.py` | View | `demo` command dispatch + `d` binding → push `AgentDemoScreen` |

### Design class diagram

```
┌───────────────────────────────┐        ┌──────────────────────────────┐
│ DemoScenario  (dataclass)     │        │ AgentDemoScreen (Screen)     │
│  name: str                    │        │  <<IAgentViewPartner>>       │
│  description: str             │        │  - _controller               │
│  goal: GoalSpec               │        │  - _scenario_name            │
│  rules: list[RuleSpec]        │        │  compose(): Header, summary, │
│  files: dict[str,str]         │        │    RichLog, ButtonBar,Footer │
│  SCENARIO_A, SCENARIO_B       │        │  action_run_cycle()          │
│  seed_sandbox_files(scn,root) │        │  action_reset()              │
└───────────────────────────────┘        │  action_back()               │
                 ▲                       └──────────────┬───────────────┘
                 │ uses (by name, via                  │ calls
                 │ controller)                          ▼
                 │                       ┌──────────────────────────────┐
                 └───────────────────────│ AgentController (existing)   │
                                         │  + reset_state()             │
                                         │  + load_demo_scenario_by_name│
                                         │  run_cycle()/list_goals()/..│
                                         └──────────────┬───────────────┘
                                                        │ delegates
                                                        ▼
                                         ┌──────────────────────────────┐
                                         │ Agent (existing facade)      │
                                         │  + clear_state()             │
                                         └──────────────────────────────┘
```

## 5. Scenarios (seeded content)

### Scenario A — "File Reader Agent" (simple, 1 cycle)
- **Goal:** "Read target.txt and report its contents"
  (`SuccessCriteria(kind="tool_success", tool_id="filesystem")`)
- **Rule:** `goal.active` → `EXECUTE_TOOL {tool_id:"filesystem", action:"read", path:"target.txt"}` (priority 900)
- **File:** `target.txt` ← "AgentX demo: this file was read by the intelligent agent."

### Scenario B — "Knowledge Assistant" (multi-step)
- **Goal:** "Gather and summarize knowledge from notes"
  (`SuccessCriteria(kind="tool_success")`)
- **Rule 1:** `goal.active` → `EXECUTE_TOOL {tool_id:"filesystem", action:"read", path:"notes.txt"}` (priority 900)
- **Rule 2:** `memory_contains("notes")` → `EXECUTE_TOOL {tool_id:"rag", action:"query", query:"summary"}` (priority 800)
- **File:** `notes.txt` ← multi-line sample notes.

## 6. Functional flow (sequence)

```
UC-1 trigger (d key / "demo b")
  AgentTUIScreen.action_open_demo(name)
    └─ self.app.push_screen(AgentDemoScreen(controller, name))

  AgentDemoScreen.on_mount()
    └─ controller.load_demo_scenario_by_name(name)
         ├─ agent.clear_state()              # clear goals/rules/volatile mem
         ├─ seed_sandbox_files(scn, sandbox) # write target.txt/notes.txt
         ├─ controller.submit_goal(...)      # scenario goal
         └─ controller.update_policy(...)    # scenario rules
    └─ self._refresh()                       # render summary (goals/rules)
    └─ self.action_run_cycle()               # auto-run 1 cycle, narrate

Run Cycle button (r)
  └─ controller.run_cycle() → render decision/action/reflection in log

Reset button (x)
  └─ controller.load_demo_scenario_by_name(current)  # clear + re-seed
  └─ self._refresh()

Back button / Escape
  └─ self.app.pop_screen()   # → back to AgentTUIScreen (agent main screen)
```

## 7. Operation specifications

### `Agent.clear_state() -> None`
**Operation:** Clear all volatile agent state (goals, policy rules, volatile memory).
- Preconditions: agent initialized.
- Exceptions: none (best-effort; repositories are not cleared — only in-memory
  state, so a persisted snapshot is unaffected).
- Postconditions: `list_goals()` empty, `list_rules()` empty, volatile memory
  empty, `state == PERCEIVING`.

### `AgentController.reset_state() -> None`
**Operation:** Clear agent state for re-seeding a demo.
- Preconditions: controller wired to an Agent.
- Exceptions: delegates to Agent; swallows none (View logs errors).
- Postconditions: agent state cleared; view refreshed.

### `AgentController.load_demo_scenario_by_name(name: str) -> bool`
**Operation:** Load + apply a named demo scenario (clear → seed files → goal → rules).
- Preconditions: `name` ∈ {"a","b"} (case-insensitive); controller wired.
- Exceptions: unknown name → returns False; file write / rule compile failure →
  returns False (View shows error).
- Postconditions: scenario goal active, scenario rules installed, sandbox file
  exists; returns True.

## 8. MVC++ self-check
- [x] View (`demo_screen.py`) does not import Model (`agent.model.*`, `scenarios`)
      — it receives only a scenario *name* (str) and reads display data via
      controller query methods (`list_goals`, `list_rules`, `get_status`).
- [x] Model does not import ui.
- [x] No new Abstract Partner needed; `AgentDemoScreen` reuses `IAgentViewPartner`
      (virtual subclass registration, same as `AgentTUIScreen`).
- [x] SQL only in existing `*_db.py` / repositories (unchanged).
- [x] No `*Controller` under `model/`.
- [x] `uv run scripts/omt/mvc_check.py` passes for touched files (verified in T-phase).

## 9. Testing plan (T-phase)
- Unit: `scenarios.py` (SCENARIO_A/B shape, `seed_sandbox_files` writes files);
  `GoalManager.clear()` / `MemoryManager.clear_volatile()` / `Agent.clear_state()`;
  `AgentController.reset_state()` / `load_demo_scenario_by_name("a"|"b"|invalid)`.
- Integration: `AgentDemoScreen` via Textual pilot — mount, auto-cycle runs,
  Run/Reset/Back buttons work, reset re-seeds.
- MVC++: `mvc_check.py` 0 errors on touched files.
