# Implementation Notes — feature_015

> Feature: agentx_security_and_quality_hardening
> Date: 2026-07-11
> Status: Programming complete

## Summary

All 50 issues from `FEATURE_007_IMPLEMENTATION_REVIEW.md` were fixed across 18 source
files. No new files were created — all fixes are in-place edits to existing modules.

## Files Changed (18)

| File | Issues Fixed |
|------|-------------|
| `model/tools/filesystem_tool.py` | C1 |
| `demo/scenarios.py` | C1 |
| `model/reflection/safety_evaluator.py` | C2 |
| `model/policy/rule.py` | C3, M10, M11 |
| `model/goal/manager.py` | H1, M5, L9 |
| `model/agent.py` | H2, H3, H4, H7, L7, L8, S8 |
| `view/tui/fast_agent_modals.py` | H5, S2, S5 |
| `model/ai_adapter.py` | H6, M2 |
| `model/memory/manager.py` | M1, M7, M8, M9 |
| `model/policy/evaluator.py` | M3, M4, M6, L1 |
| `model/reflection/proposal_router.py` | M6 |
| `model/policy/conflict_resolver.py` | L2, L3, L4 |
| `model/tools/discovery.py` | L5 |
| `model/tools/registry.py` | L6 |
| `model/reflection/critique_parser.py` | L10 |
| `persistence/schema_db.py` | L11, L13, L14, M14 |
| `persistence/agent_db.py` | L11, L12, L13, L14, M14 |
| `persistence/repositories_db.py` | M12 |
| `model/reflection/engine.py` | M13, S7 |
| `types.py` | M3, S1, S8 |
| `controller/agent_controller.py` | L16, L17, S3, S8 |
| `view/tui/agent_screen.py` | L15, S6 |
| `view/tui/fast_agent_screen.py` | S3, S4, S8 |
| `interfaces.py` | L16, L18 |

## Key Design Decisions

1. **C2 (safety deny-list)**: `_infer_op` checks content shape first, falls back to
   `op` field for backward compat with existing tests and explicit callers.
2. **C3 (DSL subtraction)**: Removed `-?` from NUMBER tokenizer; added unary minus
   in `_primary()`. The `_additive` parser rule was already correct — the tokenizer
   was the bottleneck.
3. **H7 (clear-then-fail)**: Extracted `_do_restore()` from `resume_session()` and
   wrapped it in try/except that restores pre-clear state on failure.
4. **M6 (policy revert)**: Token format changed to `rule_id:{json_of_previous}`.
   `_revert_policy_change` decodes and restores. The `revert_rule` method now accepts
   an optional `previous` parameter.
5. **M11 (unknown identifiers)**: `_validate_identifiers` is called in
   `compile_condition` but `CompiledCondition.evaluate` catches the
   `ConditionCompileError` gracefully (moved compile inside try/except).
6. **S5 (batch approval)**: Used keybindings (A/D) instead of extra buttons to avoid
   Textual layout issues with 5 buttons in a narrow modal.
7. **S8 (manual kind)**: Added `"manual"` to `SuccessCriteria` docstring. Agent.act()
   already only auto-completes `kind == "tool_success"` goals, so `"manual"` goals
   never auto-complete. The controller's `submit_goal` now accepts `manual=True`.

## Test Results

- **Full suite**: 678 passed, 1 failed (pre-existing `test_llm_initialization_attempted`)
- **MVC++**: 0 errors, 1 warning (pre-existing god_controller on agent_controller.py)
- **Zero regressions** from the pre-feature_015 baseline
