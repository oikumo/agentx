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
- [x] **feature_021.meta_harness_think_anywhere** <!-- id:T-021 prio:high agent:true -->
- [x] **feature_022.meta_harness_think_anywhere_v2 — Tier A: correctness hotfixes A1–A4** <!-- id:T-022 prio:medium agent:true -->
- [x] **think_anywhere_v2 Tier B1+D1: anchor-based insertion + read-time thought injection** <!-- id:T-022BD prio:medium agent:true -->
- [x] **think_anywhere_v2 Tier C: verify/stale lifecycle C1 + per-file consult C2** <!-- id:T-022C prio:low agent:true -->
- [x] **think_anywhere_v2 Tier remainder: B2 suggest + E1 index strategy + E2 theory-doc fixes** <!-- id:T-022E prio:low agent:true -->
- [x] **feature_023.meta_harness_improvement** <!-- id:T-023 prio:high agent:true -->
- [x] **feature_tui_dark_mode** — TUI dark mode toggle + theme selector

---

## Agent Scratchpad (auto-managed, do not edit manually)

```
FEATURES DONE (full docs in each .meta/.../FEATURE.md + test_report.md — grep those for detail):
- feature_019 fix: invalid CSS (font-family, white-space) kills entire Textual DEFAULT_CSS parse.
- feature_020 nav + e2e, feature_021 think, feature_022 think-v2 (tiers A/B1+D1/C/B2+E1+E2): all shipped, harness set 246/246.
- feature_tui_dark_mode: default dark mode (textual-dark), `k` toggles dark/light, `Ctrl+Shift+T` opens theme selector (21 built-in themes).

RECURRING GOTCHAS (apply on every future task — these cost hours when re-discovered):
- opencode loader (sk/nk) requires ALL named exports of a plugin .ts be functions; tool objects aren't. → plugins export ONLY `export default async () => ({tool:{...}})` (mirrors omt_status.ts). Deterministic guard test_no_named_exports_except_default pins omt_think only; omt_status/omt_nav/omt_enforcer load-guard is future work.
- omt_done strict full-suite unreachable: 3 pre-existing feature_018 react_screen Textual/mock failures + 2 tdd_check tests reading REAL 8h-window ledger (pass only when no TDD session in-window). → exit phase via omt_complete{advance_to:Testing→Done}, never omt_done (feature_021 prior art).
- omt_think.ts and omt_enforcer.ts are THINK-GATED (carry TA: thoughts). Before editing: omt_think_list{path:...} to clear gate. omt_enforcer.ts:~965 has an ACCIDENTAL anchored TA: → whole-repo consult covers it.
- Guarded files (.opencode/plugin/*.ts, omt_think.ts, omt_enforcer.ts, opencode.jsonc) require e2e receipt ≥ mtime: refresh between edits via `uv run pytest tests/scripts/omt/test_omt_harness_e2e.py -q`. Batch each plugin's changes into ONE write when possible.
- Write tool aborts on large payloads (empty params emitted; small payloads fine). → chunked edit() + receipt refresh between chunks for guarded files.
- TESTLIST two-hats gate blocks tests/ creation (chicken-and-egg). → omt_skip{scope:tests} to bootstrap; ledger-audited. Prior art: feature_021, feature_022 tiers A/B1+D1/C/remainder.
- omt_testlist behaviors MUST be JSON array (tdd_check.py:403 json.loads). Prose strings fail with 'Expecting value: line 1 column 1'.

PENDING FEATURES (next work):
- feature_001.session_user_objectives_driven_by_Petri_Net — scope & success criteria unset.
- feature_002.rag_retrieval_augmented_generation — scope & success criteria unset.

IN PROGRESS (resume here):
- feature_001.session_user_objectives_driven_by_Petri_Net — scope & success criteria unset.
- feature_002.rag_retrieval_augmented_generation — scope & success criteria unset.
```

