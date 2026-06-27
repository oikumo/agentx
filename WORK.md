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
