# PLAN — feature_012: TUI Framework

> Task type: **major_feature** · See `omt_agent_guide.md §12` for the required artifacts.

## Objective

Extract a reusable TUI base-class library under `src/agentx/ui/tui/framework/`
and refactor the 9 existing TUI screens/adapters to inherit from it, with zero
regressions (516 tests green, MVC++ 0/0).

## Steps

- [x] Analysis (overview/current-state, use cases, analysis class diagram)
- [x] Design (design_001_tui_framework.md + operation_spec_001_tui_framework.md)
- [x] Implementation (framework package + refactor 9 screens/adapters)
- [x] Testing (unit tests for framework + full regression suite + MVC++)

## Decisions (locked with user)

- **Scope:** Library + refactor existing (truly centralise, prove reuse).
- **Location:** `src/agentx/ui/tui/framework/` package.

## Refactor plan (per-screen, incremental)

Framework package (new):
1. `framework/__init__.py` — public API re-exports
2. `framework/base_screen.py` — `BaseAgentXScreen` + `NavigationMixin`
3. `framework/base_modal.py` — `BaseAgentXModalScreen[T]`
4. `framework/base_app.py` — `BaseAgentXApp`
5. `framework/base_adapter.py` — `BaseScreenAdapter`
6. `framework/partner.py` — `register_partner()` helper
7. `framework/widgets.py` — `SessionStatusBar`, `WelcomePanel`, `MenuGrid`, `CommandInput`, `ChatMessage`

Refactor (edit existing, one at a time + run tests):
8. `ui/tui/screens/main_screen.py` — MainTUIScreen + extract widgets → framework
9. `ui/tui/screens/chat_screen.py` — ChatTUIScreen + extract ChatMessage → framework
10. `ui/tui/screens/rag_screen.py` — RagTUIScreen
11. `ui/tui/app.py` — TUIApplication
12. `ui/tui/adapters/{main,chat,rag}_adapter.py` — 3 adapters
13. `agent/view/tui/agent_screen.py` — AgentTUIScreen
14. `agent/view/tui/demo_screen.py` — AgentDemoScreen
15. `agent/view/tui/fast_agent_screen.py` — FastAgentTUIScreen
16. `agent/view/tui/fast_agent_modals.py` — 4 modals (skeleton only; keep worker/queue in RunningModal)

## Artifacts produced

- Requirements: `feature_012.tui_framework/FEATURE.md`
- Analysis: `3.analysis/features/feature_012.tui_framework/analysis_001..003_*.md`
- Design: `4.design/features/feature_012.tui_framework/design_001_tui_framework.md` + `operation_spec_001_*.md`
- Implementation: `5.implementation/features/feature_012.tui_framework/impl_notes.md`
- Testing: `6.testing/features/feature_012.tui_framework/test_report.md`

## Verification gates

- After each src/ edit: `uv run scripts/omt/mvc_check.py src/agentx/ui/tui`
- After full refactor: `uv run pytest tests/tui tests/features/feature_011.fast_agent tests/features/feature_007.agentx_intelligent_agent_behaviour -q`
- Final: full suite `uv run pytest -q` (expect 516/517, 1 pre-existing)
