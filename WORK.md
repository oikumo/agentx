# WORK

> Single‑developer + coding‑agent roadmap.  
> Machine‑parseable, minimal friction, git‑friendly.

---

## Convention

| Symbol | Meaning |
|--------|---------|
| `[ ]`  | Pending |
| `[~]`  | In progress (agent working on it) |
| `[x]`  | Done |
| `[!]`  | Blocked / needs decision |

**Hierarchy** – top‑level task → optional subtasks (indented 4 spaces).  
**Metadata** – optional inline comment: `<!-- id:T‑123 prio:medium agent:true -->`  
**Thoughts** – separate `---` line then bullet list; tools can strip it.

---

## Tasks

- [~] Implement feature_007.agentx_intelligent_agent_behaviour
    - [x] Complete the feature description with the User revision
    - [x] Create the feature implementation plan
    - [x] Validate the feature technical feasibility, fix the feature and it is plan if needed
    - [ ] Validate the feature end User usability, fix the feature and it is plan if needed
    - [ ] Develop the feature
    - [ ] User validate the feature implementation

- [x] Implement feature_004.modern_ui <!-- id:T-004 prio:high agent:true -->
    - [x] Infrastructure complete (TUI module, providers, adapters)
    - [x] MainTUIScreen implemented with all widgets
    - [x] Integration with main.py complete
    - [x] Create tui automated end to end tests using pilot in `test_automated/tui/`
    - [x] TUI Bug Fixes – Architecture Rewiring (2025-06-27)
        - [x] Fixed MainTUIScreen to delegate navigation to controller
        - [x] Updated IMainViewPartner interface with `show_chat()` and `show_rag()` abstract methods
        - [x] Updated ChatController to accept view in constructor (for TUI/Console swapping)
        - [x] Updated RagController to accept view in constructor (for TUI/Console swapping)
        - [x] Updated RagView to implement `IRagView` interface
        - [x] Updated `IChatViewPartner` and `IRagViewPartner` with full abstract method signatures
        - [x] Implemented `TUIChatAdapter.show()` to run Textual chat screen
        - [x] Implemented `TUIRagAdapter.show()` to run Textual RAG screen
        - [x] Updated `ChatTUIScreen` to work with `IChatViewPartner` controller
        - [x] Updated `RagTUIScreen` to work with `IRagViewPartner` controller
    - [x] Remaining TUI Navigation Fix (2026-06-27)
        - [x] Fix automated e2e tests – MainTUIScreen now pushes screens directly AND calls controller
        - [x] Solution: Option 2 – MainTUIScreen pushes screens directly for navigation while also calling controller.show_chat()/show_rag() for side effects (recording, logging)
        - [x] All navigation tests pass: `test_key_c_opens_chat`, `test_key_r_opens_rag`, `test_escape_returns_from_chat`, `test_chat_button_opens_chat`
    - [x] Verify end-to-end TUI navigation (Main → Chat → RAG)
    - [x] **TUI Chat Conversation Fix (2026-06-27)**
        - [x] Root cause: MainController.show_chat() created console ChatView blocking TUI event loop
        - [x] Fix: MainController now uses provider to create TUIChatAdapter; ChatTUIScreen implements IChatView
        - [x] ChatTUIScreen now has show_partial_message(), show_message(), show_stream_message() for streaming
        - [x] TUIChatAdapter delegates to ChatTUIScreen via set_screen() connection
        - [x] All navigation + chat conversation e2e tests pass
    - [x] **TUI RAG Screen Freeze Fix (2026-06-27)**
        - [x] Root cause: RagController.select_repository() used blocking console input loop (RagRepositorySelectionView.show())
        - [x] Fix: RagTUIScreen._select_repository() now always uses TUI RepositorySelectionScreen (non-blocking)
        - [x] Also fixed _create_repository() and _ingest_documents() to use TUI screens
        - [x] Updated legacy unit tests in tests/tui/ to match new TUI screen delegation behavior
        - [x] All 23 automated TUI e2e tests pass including rag_screen_repository_selection_and_chat
    - [x] Verify User acceptance test
    - [x] Write `FEATURE.md` summary in `.meta/.../feature_004.modern_ui/`
- [x] Update README.md with feature_006 and agentic workflow description <!-- id:T-006-readme prio:med agent:true -->
- [x] Update application design overview in `.meta/software_development_process/4.design/` <!-- id:T-006-design prio:med agent:true -->
    - [x] Update application design structure documentation
    - [x] Update application design behavior documentation
- [ ] Implement feature_001.session_user_objectives_driven_by_Petri_Net <!-- id:T-001-prio-high agent:false -->
    - [ ] Define scope & success criteria
- [x] Implement feature_006.opencode_process_enforcement <!-- id:T-006-prio-high agent:true -->
    - [x] Plan → `.meta/.../feature_006.opencode_process_enforcement/plan/PLAN.md`
    - [x] MVC++ linter → `scripts/omt/mvc_check.py`
    - [x] Feature scaffolder + templates → `scripts/omt/new_feature.py`, `.meta/templates/`
    - [x] Live permissions → `opencode.jsonc`
    - [x] Process gate plugin → `.opencode/plugin/omt_enforcer.ts`
    - [x] AGENTS.md rewritten to match real enforcement
    - [x] Step 0 spike: opencode plugin API confirmed
    - [x] Tuning: agent self‑skip (logged); hard‑errors block / soft warn
    - [x] Harden: auto‑detect feature design artifact from slug
    - [x] Dogfood one bug_fix + one feature through the gate
    - [x] Fix 2 legacy MVC++ errors so the gate guards a clean baseline
    - [x] Phase exit validation (P0) — enforce artifacts on phase transition <!-- id:T-006-phase-exit prio:high agent:true -->
        - [x] PHASE_EXIT_REQUIREMENTS mapping per guide §12
        - [x] checkPhaseExitArtifacts() function with feature-scoped paths
        - [x] Integration in omt_phase.execute() — blocks invalid transitions
        - [x] Fixed: Unit tests scoped to tests/features/<feature>/
        - [x] Fixed: Operation specs detection (operation_spec_*.md pattern)
        - [x] Added: omt_complete tool for phase completion verification
        - [x] Added: WORK.md auto-sync hook on phase completion
      - [x] Verify User acceptance test
        - [x] Source fix: make `omt_status.ts` a standalone plugin and remove dynamic status import from `omt_enforcer.ts`
        - [x] Source fix: repair `omt_complete` feature-phase lookup and phase transition constants
        - [x] Source fix: repair phase-exit artifact validation (`REPO_ROOT` → plugin `directory`)
        - [x] Source fix: keep `omt_complete` artifact checks scoped to feature-sized work (`major_feature` / `new_screen`), not bug-fix dogfood phases
        - [x] Source fix: align `omt_status` with strict `design_*.md` detection and no required artifacts for lightweight task types
        - [x] Source verification: `uv run pytest tests/scripts/omt/test_mvc_check.py -q` → 25 passed
        - [x] Source verification: `uv run scripts/omt/mvc_check.py --json` → 0 errors, 6 existing warnings
        - [x] Restart opencode so plugin changes are reloaded
        - [x] After restart, run `omt_status` and confirm it returns a status summary instead of `p.split` error
        - [x] After restart, run `omt_phase` then `omt_complete` for `feature_006.opencode_process_enforcement` and confirm completion/advance works
        - [x] If live tool smoke tests pass, mark this acceptance test complete
    - [x] OMT harness comprehensive e2e guard (2026-06-28)
        - [x] Added `tests/scripts/omt/test_omt_harness_e2e.py`
        - [x] Added `.meta/.omt/omt_harness_e2e_last_run.json` runtime receipt on passing e2e run
        - [x] Enforced fresh e2e receipt before repeated edits to OMT/META harness files
- [ ] Implement feature_002.rag_retrieval_augmented_generation <!-- id:T-002-prio-med agent:false -->
    - [ ] Scaffold design doc

---

## Agent Scratchpad (auto‑managed, do not edit manually)

```
[2026-06-27T18:26] Agent: Completed feature_004 navigation fixes, all tests pass.
[2026-06-27T18:30] Agent: Next action - write FEATURE.md for feature_004.
[2026-06-27T19:15] Agent: Fixed TUI RAG screen freeze on Select button - replaced blocking console input with TUI screens.
[2026-06-28] Agent: Moved feature_003 content to feature_007 (scaffolded via new_feature.py); Analysis phase started
```
