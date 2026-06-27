# WORK

Active development plan for Agentx software development tracking

---

# Legend
[ ] - Not started
[*] - Work in progress
[-] - Stopped
[x] - Done
[!] - Failing

---

## Tasks


[*] Implement feature_004.modern_ui
    [x] Infrastructure complete (TUI module, providers, adapters)
    [x] MainTUIScreen implemented with all widgets
    [x] Integration with main.py complete
    [x] Create tui automated end to end tests using pilot in `test_automated/tui/` python module folder
    [!] User acceptance testing PASSED (Chat working, RAG working)
    [ ] Summarize feature implementation in the feature documentation in a single file in `.meta/software_development_process/2.requirements/features/feature_004.modern_ui/FEATURE.md`
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
    [ ] **Remaining TUI Navigation Fix (next session):**
        [ ] Fix automated e2e tests - navigation not working in pilot tests (MainTUIScreen action_open_chat/action_open_rag call controller.show_chat/show_rag but controller methods don't push screens)
        [ ] Option 1: Update RecordingController in conftest.py to actually push screens in tests
        [ ] Option 2: Update MainTUIScreen to push screens directly (like fallback) while also calling controller
        [ ] Option 3: Update MainController.show_chat/show_rag to use provider to create and push TUI screens
    [ ] Verify end-to-end TUI navigation (Main → Chat → RAG)


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
