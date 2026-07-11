# Feature 018: Chat_Screen_Improvements

> **Status:** [~] In progress
> **Created:** 2026-07-11
> **WORK.md task:** T-018 (new task - fix feature_017 chat screen issues)

---

## Summary

Fix visual and usability issues introduced by feature_017's chat screen enhancements. The current implementation has cluttered UI with timestamps on every message, insufficient visual separation between user and agent messages, and unnecessary complexity from the conversation sidebar feature. This feature simplifies the chat interface to focus on clear, solid conversation display.

## Scope (one sentence — what "done" looks like)

Remove timestamps, improve visual separation between user/agent messages with distinct styling, remove conversation sidebar complexity, and ensure all existing tests pass with zero regressions.

## Task type

bug_fix

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Design | Design doc | `4.design/features/feature_018.chat_screen_improvements/design_001_simplified_chat.md` | [~] |
| Implementation | Impl notes | `5.implementation/features/feature_018.chat_screen_improvements/` | [ ] |
| Testing | Test report | `6.testing/features/feature_018.chat_screen_improvements/` | [ ] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.
