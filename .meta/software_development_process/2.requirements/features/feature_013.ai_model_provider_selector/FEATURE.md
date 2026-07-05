# Feature 013: Ai Model Provider Selector

> **Status:** [x] Done
> **Created:** 2026-07-05
> **WORK.md task:** `- [x] Implement feature_013.ai_model_provider_selector`

---

## Summary

A "Models" module on the Main screen that lets the user select the current AI
model provider (OpenRouter, OpenAI, Google Gemini, Ollama, LlamaCpp). The choice
is persisted (`~/.agentx/model_selection.json`) and every feature that builds an
LLM (Chat, RAG, Agent) now consults the selection instead of a hardcoded
`openrouter_llm_provider()`.

## Scope (one sentence — what "done" looks like)

From the Main screen the user presses `m` (or clicks "🎛️ Models"), picks a
provider from the list, and all subsequent Chat/RAG/Agent operations use that
provider; the choice survives app restarts.

## Task type

new_screen

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | FEATURE.md | `2.requirements/.../feature_013.ai_model_provider_selector/` | [x] |
| Analysis | Use case | `3.analysis/.../use_case_001_select_model_provider.md` | [x] |
| Analysis | Analysis doc | `3.analysis/.../analysis_001_model_provider_selection.md` | [x] |
| Design | Design doc | `4.design/.../design_001_model_selector.md` | [x] |
| Design | Operation spec | `4.design/.../operation_spec_001_model_selector.md` | [x] |
| Implementation | Impl notes | `5.implementation/.../impl_notes.md` | [x] |
| Testing | Test report | `6.testing/.../test_report.md` | [x] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.

---

## Result

- feature_013 tests: **56 passed**.
- Full suite: **635 passed, 1 failed** (1 pre-existing `test_llm_initialization_attempted`,
  unrelated — `chat_screen.py` not touched).
- MVC++ `mvc_check.py`: **0 errors, 6 warnings** (all pre-existing baseline).
- 0 regressions.
