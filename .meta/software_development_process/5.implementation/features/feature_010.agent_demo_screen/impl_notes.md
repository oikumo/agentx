# Implementation Notes — feature_010.agent_demo_screen

> **Phase:** Programming → Testing | **Feature:** feature_010.agent_demo_screen
> **Extends:** feature_007.agentx_intelligent_agent_behaviour

## What was built

A dedicated `AgentDemoScreen` that demonstrates feature_007's intelligent-agent
cycle with a single trigger. From the `AgentTUIScreen`, pressing `d` (or typing
`demo [a|b]`) opens the demo screen seeded with a ready-made goal + policy
rules + sandbox file, auto-runs one perceive → decide → act → reflect cycle, and
offers **Run Cycle**, **Reset (re-seed)**, and **Back to Agent** buttons.

## Files created

| File | Layer | Purpose |
|------|-------|---------|
| `src/agentx/agent/demo/__init__.py` | Model/data | package docstring |
| `src/agentx/agent/demo/scenarios.py` | Model/data | `DemoScenario`, `SCENARIO_A`/`SCENARIO_B`, `get_scenario`, `seed_sandbox_files` |
| `src/agentx/agent/view/tui/demo_screen.py` | View | `AgentDemoScreen` — buttons + live cycle log |

## Files modified

| File | Change |
|------|--------|
| `src/agentx/agent/model/goal/manager.py` | + `GoalManager.clear()` |
| `src/agentx/agent/model/memory/manager.py` | + `MemoryManager.clear_volatile()` |
| `src/agentx/agent/model/agent.py` | + `Agent.clear_state()` |
| `src/agentx/agent/controller/agent_controller.py` | + `reset_state()`, `load_demo_scenario_by_name()`, `get_demo_scenario_info()` |
| `src/agentx/agent/view/tui/agent_screen.py` | + `d` keybinding, `demo` command, `action_open_demo()` |
| `src/agentx/agent/model/tools/filesystem_tool.py` | bug fix: read `command.action` |
| `src/agentx/agent/model/tools/rag_sensor_tool.py` | bug fix: read `command.action` |
| `src/agentx/agent/model/tools/session_tool.py` | bug fix: read `command.action` |

## Scenarios

- **A — File Reader Agent:** goal "Read target.txt"; rule `goal.active →
  filesystem read`; seeded `target.txt`. Completes in one cycle.
- **B — Knowledge Assistant:** goal "Read notes and write summary"; rule 1
  `goal.active → read notes.txt`; rule 2
  `memory_contains("notes.txt") AND NOT memory_contains("summary.txt") → create
  summary.txt`. Cycle 1 reads notes (goal completes); cycle 2 writes summary
  (memory-driven); cycle 3 idles (summary exists). Demonstrates the condition
  DSL, memory-driven decisions, and multi-cycle orchestration.

## Bug fix (feature_007, unblocked by this feature)

The built-in tools (`FileSystemTool`, `RagSensorTool`, `SessionTool`) read the
action from `command.parameters.get("action")` instead of the canonical
`command.action` field. At runtime `_decision_to_command` strips `"action"` from
`parameters` and places it in `command.action`, so EXECUTE_TOOL actions other
than `read` silently degraded (filesystem `create`/`update` defaulted to
`read`; rag `query` failed validation). The existing tests masked this because
they set `"action"` in **both** places. Fix: `action = command.action or
command.parameters.get("action", ...)`. All 169 feature_007 tests still pass.

## MVC++ compliance

- `AgentDemoScreen` (View) imports no Model module — it receives a scenario
  *name* (str) and reads display data via controller query methods
  (`get_status`, `list_goals`, `list_rules`, `get_demo_scenario_info`) and the
  `run_cycle()` return value.
- `scenarios.py` is pure data + a filesystem-seeding helper (Model layer); the
  controller translates specs into real `Goal`/`PolicyRule`.
- `mvc_check.py` on `src/agentx/agent/`: **0 errors, 0 warnings**.

## Test results

- `tests/features/feature_010.agent_demo_screen/`: **34 tests, all pass**
  (scenarios, clear operations, controller demo methods, Textual pilot
  integration for mount/auto-cycle/run/reset buttons + AgentTUIScreen demo
  wiring).
- feature_007 regression: **169/169 pass** (tool bug fix safe).
