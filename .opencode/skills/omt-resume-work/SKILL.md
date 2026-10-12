---
name: omt-resume-work
description: >
  Reconcile a paused skills project across owners without inventing state.
metadata:
  opencode/slash: "true"
  opencode/autoinvoke: "false"
---

## Use when

A pause pointer (sandbox file) plus project slug are present and resumption is requested.

## Do not use when

No pause exists, or the failure is a compiler/runtime/test error rather than a resume task.

## Procedure

1. Preserve the pause pointer, project slug, and expected head (if any).
2. Ask `omt_status.preflight` for the resume operation and `omt_q.state` for ledger health.
3. Treat the current OMT response as authority; do not restate policy from memory.
4. Verify fingerprints: pause file → `git log`/`git status` → CURRENT_STATE + PROJECT → feature docs → skill files → WORK rows (see `references/resume_checklist.md`).
5. Reconcile owners session→feature→project→harness; perform no writes (read-only).
6. Return `omt-skill-result/v1`.

## Stop

Stop rather than inventing state when fingerprints mismatch, authorization is missing, or owners conflict.
