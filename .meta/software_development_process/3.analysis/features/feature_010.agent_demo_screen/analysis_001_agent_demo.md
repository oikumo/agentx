# Analysis 001: Agent Demo Screen

> **Phase:** Analysis — `omt_agent_guide.md §2`, §12 | **Feature:** feature_010.agent_demo_screen
> **Extends:** feature_007.agentx_intelligent_agent_behaviour (reuses its Agent/Controller/tools)

## 1. Problem statement

feature_007's intelligent agent ships empty (no goals, no rules). Demonstrating
its perceive → decide → act → reflect cycle requires a user to manually type
several commands (`goal …`, `rule …`, `run`). We need a **single trigger** that
populates the agent with a ready-made goal + policy rules + sandbox data and
visualises the cycle, so the capability can be shown in one keystroke.

## 2. Use case

**UC-1: Run an agent demo**
- **Actor:** Developer / demonstrator.
- **Preconditions:** The app is running; the user is on the Agent screen.
- **Main flow:**
  1. User presses `d` (or types `demo` / `demo b`).
  2. System clears prior demo state, seeds a sandbox file, submits the scenario
     goal, and installs the scenario policy rules.
  3. System opens the demo screen showing the scenario summary (goal + rules)
     and auto-runs one cycle, narrating perceive/decide/act/reflect.
  4. User presses **Run Cycle** to step further.
  5. User presses **Reset** to clear + re-seed the same scenario.
  6. User presses **Back** (or `Escape`) to return to the Agent screen.
- **Alternative flows:**
  - 1a. User types `demo b` → scenario B (multi-step) is loaded instead of A.
  - 2a. Unknown scenario key → error shown, no state change.
- **Postconditions:** The agent holds the scenario goal/rules; the sandbox file
  exists; the demo screen displays cycle results.

## 3. Operations extracted (→ Controller methods)

| Operation | Controller method | New? |
|-----------|-------------------|------|
| Load + apply a demo scenario | `load_demo_scenario_by_name(name)` | yes |
| Clear agent state for re-seed | `reset_state()` | yes |
| Run one cycle | `run_cycle()` | existing |
| Query status / goals / rules | `get_status` / `list_goals` / `list_rules` | existing |
| Scenario display info | `get_demo_scenario_info(name)` | yes |

## 4. Domain concepts

No new domain concepts. The demo reuses feature_007's `Goal`, `PolicyRule`,
`SuccessCriteria`, `PolicyAction`, and the built-in tools (`FileSystemTool`).
A lightweight `DemoScenario` data class holds the seeded recipe (pure data,
translated to real types by the controller).

## 5. UI dialog structure

```
AgentTUIScreen
  └─ d / "demo [a|b]"  →  push AgentDemoScreen
        ├─ Status bar (scenario · state · goals · rules · memory)
        ├─ Summary panel (scenario name + description + goals + rules)
        ├─ Activity log (cycle narration)
        ├─ [▶ Run Cycle] [↻ Reset] [← Back to Agent]
        └─ Footer (r / x / Esc)
```

## 6. Non-functional

- **Usability:** one keystroke to a working demo; no manual setup.
- **Robustness:** reset is idempotent (clear + re-seed); unknown scenarios fail
  gracefully; cycle errors are caught and logged, never crashing the TUI.
- **MVC++:** the demo screen is a pure View (no Model imports); scenario data
  lives in the Model layer; the controller orchestrates.
