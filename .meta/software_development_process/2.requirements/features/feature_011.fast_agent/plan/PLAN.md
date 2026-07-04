# PLAN — feature_011: Fast_Agent

> Task type: **new_screen** · See `omt_agent_guide.md §12` for the required artifacts.

## Objective

A new "⚡ Fast Agent" main-menu option (`f`) that drives the existing feature_007
`Agent` via a stack of `ModalScreen` dialogs (Goal → Running → Reflection →
Result), giving the user a much simpler UX than the full Agent screen. The
existing Agent screen is relabeled "⚙️ Advanced Agent".

## Steps

- [x] Requirements — FEATURE.md (decisions log from user option selections)
- [ ] Design — `design_001_fast_agent.md` + `operation_spec_001_fast_agent.md`
- [ ] Implementation — View (+ thin FastAgentView facade) + MainController wiring
- [ ] Testing — TUI-pilot e2e + MVC++ check (0 errors on touched files)

## Design boundary (no Model changes)

The `Agent` facade, `AgentController`, persistence, tools, policy engine,
reflection engine and demo scenarios are **unchanged**. Fast Agent is purely a
*View* addition. To suppress the controller's IAgentViewPartner messages that
are unused in the modal flow (refresh_goal_tree / show_policy_editor /
show_memory_view / show_reflection_log), the Fast Agent View provides a
no-op `IAgentViewPartner` implementation that swallows thoseView-side calls;
the modal flow queries the controller explicitly when it needs data.

## Steps (Implementation phase — Preview)

1. `src/agentx/agent/view/tui/fast_agent_screen.py` — `FastAgentTUIScreen`
   (regular `Screen`, modal-stack host; keybinding `escape` → pop_screen)
2. `src/agentx/agent/view/tui/fast_agent_modals.py` — 4 `ModalScreen` subclasses:
   `GoalModal`, `RunningModal`, `ReflectionModal`, `ResultModal`
3. `src/agentx/agent/view/tui/fast_agent_view.py` — `FastAgentTUIView` —
   no-op `IAgentViewPartner` (virtual-subclass-registered) implementation, so
   the controller does not raise when the Agent emits UI events during a cycle.
4. `src/agentx/agent/adapter.py` — add `FastAgentAdapter` (or static
   `AgentAdapter.create_fast(config, resume=True)` → returns
   `(Agent, AgentController, FastAgentTUIScreen)`)
5. `src/agentx/ui/screens/main/main_controller.py` — add
   `show_fast_agent()` + `get_fast_agent_controller()`; relabel existing
   `show_agent()`/button text to "Advanced Agent"
6. `src/agentx/ui/tui/screens/main_screen.py` — add `Binding("f", "open_fast_agent", "Fast Agent")`,
   a 5th button `⚡ Fast Agent` (variant="warning"), `action_open_fast_agent()`,
   and `on_button_pressed` mapping for `btn-fast-agent`; relabel existing
   `btn-agent` text from "🤖 Agent" to "⚙️ Advanced Agent" and add "Advanced Agent"
   label to its binding.
7. Tests — Textual pilot e2e covers Goal → dismiss(goal) → Running auto-runs →
   Reflection (proposal) → Result → Back/Save/New-goal; MVC++ check on touched
   files.

## Artifacts produced

- Requirements: `feature_011.fast_agent/FEATURE.md`
- Design: `4.design/features/feature_011.fast_agent/design_001_fast_agent.md`
- Design: `4.design/features/feature_011.fast_agent/operation_spec_001_fast_agent.md`
- Implementation: `5.implementation/features/feature_011.fast_agent/impl_notes.md`
- Testing: `6.testing/features/feature_011.fast_agent/test_report.md`
