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
- [x] **feature_020.e2e_tests_opencode_driven** <!-- id:T-020e2e prio:high agent:true -->

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
[2026-07-12] feature_020 ENFORCEMENT: opencode.jsonc allows nav tools, AGENTS.md has MANDATORY section, omt_enforcer.ts has session.start reminder, META_HARNESS.md has SECTION:NAV, 22/22 tests pass
[2026-07-16] Fixed feature_019 coding screen input layout bug: invalid CSS properties (font-family, white-space) caused entire DEFAULT_CSS to fail parsing; removed invalid properties, input now docks at bottom correctly; 72/72 tests pass
[2026-07-16] feature_020 e2e investigation: `opencode serve` reveals BOTH plugins fail to load — omt_nav.ts ("Plugin export is not a function", nav tools never registered in real session → nav-gate catch-22) and omt_enforcer.ts ("rel.startsWith is not a function" in isDocPath via getSearchPath non-string path, serve-mode crash). Existing tests are function-level (call plugin fns via _nav_runner.mjs), never run opencode → missed both. Plan saved below; scope=tests+fix, mechanism=deterministic serve-load.
[2026-07-16] feature_020 e2e COMPLETE: Wrote test_opencode_e2e.py (real `opencode serve` spawn → /config bootstrap → assert no "failed to load plugin"). TDD: confirmed RED (3 defect-detectors failed, 2 controls passed), then fixed both defects. DEFECT A fix: omt_nav.ts — opencode's loader (sk/nk) checks ALL module exports must be functions; tool objects aren't functions → removed named exports, kept only `export default async () => ({tool:{...}})` (mirrors omt_status.ts); updated _nav_runner.mjs to retrieve tools via mod.default().tool. DEFECT B fix: omt_enforcer.ts — getSearchPath() passed non-string (array/object) path to relOf()→isAbsolute/join causing crash; made isDocPath/navGateDecision/getSearchPath defensive (typeof guard, array→first-string-element). Also restored nav tool permissions in opencode.jsonc (were removed during investigation). 54/54 feature_020 tests pass; 1030/1033 full suite (3 pre-existing feature_018 react_screen Textual/mock failures unrelated). Live serve verify: zero plugin-load errors, bootstrap completes, nav tools callable.
```
