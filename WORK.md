# WORK

> Single-developer + coding-agent roadmap. Machine-parseable, minimal friction, git-friendly.

---

## Convention

| Symbol | Meaning |
|--------|---------|
| `[ ]`  | Pending |
| `[~]`  | In progress (agent working on it) |
| `[x]`  | Done |
| `[!]`  | Blocked / needs decision |

**Hierarchy** - top-level task -> optional subtasks (indented 4 spaces).
**Metadata** - optional inline comment: `<!-- id:T-123 prio:medium agent:true -->`
**Thoughts** - separate `---` line then bullet list; tools can strip it.

---

## Tasks

- [x] **feature_007.agentx_intelligent_agent_behaviour**
- [x] **Fix feature_007 bugs per BUG_FIX_PLAN.md**
- [x] **feature_004.modern_ui**
- [x] **Update README.md with feature_006 and agentic workflow**
- [x] **Update application design overview in .meta/.../4.design/**
- [ ] **feature_001.session_user_objectives_driven_by_Petri_Net**
- [x] **feature_006.opencode_process_enforcement**
- [ ] **feature_002.rag_retrieval_augmented_generation**
- [x] **feature_012.tui_framework**
- [x] **feature_010.agent_demo_screen**
- [x] **feature_011.fast_agent**
- [x] **feature_013.ai_model_provider_selector**
- [x] **feature_014.tui_nonblocking_runner**
- [x] **Fix feature_011.fast_agent UI freeze**
- [x] **feature_016.tdd_enforcement**
- [x] **Fix feature_017.chat_screen_conversation_history_bug**
- [x] **feature_017.improve_chat_screen**
- [x] **feature_018.chat_screen_improvements**
- [x] **Fix chat screen "no assistant message" bug**
- [x] **Fix chat screen "no conversation history" bug**
- [x] **feature_018.react_screen**
- [x] **feature_019.coding_agent_screen**
- [x] **feature_020.meta_harness_navigation** <!-- id:T-020 prio:high agent:true -->

---

## Agent Scratchpad (auto-managed, do not edit manually)

```
[2026-07-11] Fixed "no assistant message": _run_llm_async used self.call_from_thread() on Screen; fix: self.app.call_from_thread(); MVC++ 0
[2026-07-11] Fixed "no conversation history": throwaway local history; fix: worker uses controller.history + on_mount calls start_new_conversation(); MVC++ 0
[2026-07-12] Compressed all .md files for agent token efficiency: AGENTS.md, META_HARNESS.md, STRUCTURE.md, BEHAVIOR.md, omt_agent_guide.md, all 6 doc/omt++/*.md files
[2026-07-12] META_HARNESS.md restructured for grep-navigability (SECTION:, CMD_, ERR_, WRN_, TT_, QUICK_, XREF_ prefixes)
[2026-07-12] All .meta META.md files updated with grep-friendly SECTION: headers
[2026-07-12] Declared feature_020.meta_harness_navigation in Analysis phase (major_feature, requires design doc before Programming)
[2026-07-12] feature_020 COMPLETE: Implemented omt_nav plugin tools (omt_nav, omt_list_sections, omt_cross_ref, omt_quick_ref), 18/18 tests pass, all META HARNESS docs grep-optimized
```
