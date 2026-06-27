# WORK

Active development plan for Agentx software development tracking

---

# Task State Legend
- `[ ]` - Not started
- `[*]` - Work in progress
- `[-]` - Stopped
- `[x]` - Done
- `[!]` - Failing

# Task Format

```
[TASK-STATE] <TASK-DESCRIPTION>
    [TASK-STATE] <SUB-TASK-DESCRIPTION>
    [TASK-STATE] <SUB-TASK-DESCRIPTION>
    ...
    ----Thoughts----
    - <TASK-THOUGHT>
    - <TASK-THOUGHT>
    ...
```
---

## Tasks

[*] Implement feature_004.modern_ui
    [x] Infrastructure complete (TUI module, providers, adapters)
    [x] MainTUIScreen implemented with all widgets
    [x] Integration with main.py complete
    [x] Create tui automated end to end tests using pilot in `test_automated/tui/` python module folder
    [x] **TUI Bug Fixes - Architecture Rewiring (2025-06-27):**
        [x] Fixed MainTUIScreen to delegate navigation to controller (show_chat, show_rag)
        [x] Updated IMainViewPartner interface with show_chat() and show_rag() abstract methods
        [x] Updated ChatController to accept view in constructor (for TUI/Console swapping)
        [x] Updated RagController to accept view in constructor (for TUI/Console swapping)
        [x] Updated RagView to implement IRagView interface
        [x] Updated IChatViewPartner and IRagViewPartner with full abstract method signatures
        [x] Implemented TUIChatAdapter.show() to run Textual chat screen
        [x] Implemented TUIRagAdapter.show() to run Textual RAG screen
        [x] Updated ChatTUIScreen to work with IChatViewPartner controller
        [x] Updated RagTUIScreen to work with IRagViewPartner controller
    [x] **Remaining TUI Navigation Fix (2026-06-27):**
        [x] Fix automated e2e tests - MainTUIScreen now pushes screens directly AND calls controller
        [x] Solution: Option 2 - MainTUIScreen.action_open_chat/action_open_rag push screens directly for proper navigation while also calling controller.show_chat/show_rag for side effects (recording, logging)
        [x] All navigation tests pass: test_key_c_opens_chat, test_key_r_opens_rag, test_escape_returns_from_chat, test_chat_button_opens_chat
    [x] Verify end-to-end TUI navigation (Main → Chat → RAG) - ALL TESTS PASS
    [!] User acceptance testing PASSED (Chat working, RAG working)
    [ ] Summarize feature implementation in the feature documentation in a single file in `.meta/software_development_process/2.requirements/features/feature_004.modern_ui/FEATURE.md`
    

[x] Update the main README.md file, including feature_006.opencode_process_enforcement and opencode agentic workflow development process description

[x] Update application design overview in `.meta/software_development_process/4.design/`
    [x] Update application design structure documentation
    [x] Update application design behavior documentation

[-] Implement feature_001.session_user_objectives_driven_by_Petri_Net
    [*] Define scope


[x] Implement feature_006.opencode_process_enforcement
    [x] Plan -> `.meta/.../features/feature_006.opencode_process_enforcement/plan/PLAN.md`
    [x] MVC++ linter -> `scripts/omt/mvc_check.py`
    [x] Feature scaffolder + templates -> `scripts/omt/new_feature.py`, `.meta/templates/`
    [x] Live permissions -> `opencode.jsonc`
    [x] Process gate plugin -> `.opencode/plugin/omt_enforcer.ts`
    [x] AGENTS.md rewritten to match real enforcement
    [x] Step 0 spike: opencode plugin API confirmed in a live session (test successful)
    [x] Tuning: agent self-skip (logged); hard-errors block / soft warn (introduced-only)
    [x] Harden: auto-detect feature design artifact from slug
    [x] Dogfood one bug_fix + one feature through the gate
    [x] (optional) Fix 2 legacy MVC++ errors so the gate guards a clean baseline

[x] Implement feature_002.rag_retrieval_augmented_generation

---
