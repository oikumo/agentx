---
name: omt-recover-block
description: >
  Diagnose an OMT refusal, clear only the specific legitimate prerequisite,
  retry once when justified, and return evidence.
metadata:
  opencode/slash: "true"
  opencode/autoinvoke: "false"
---

## Use when

The most recent attempted operation returned an OMT prerequisite refusal.

## Do not use when

The failure is a compiler/runtime/test error unrelated to OMT.

## Procedure

1. Preserve the original operation, path, feature identity and result.
2. Ask `omt_status.preflight` for that exact operation/path.
3. Treat the current OMT response as authority; do not restate policy from memory.
4. Perform only the smallest authorized clearing action.
5. Retry at most once for the same diagnosed blocker.
6. Return `omt-skill-result/v1`.

## Stop

Stop rather than bypassing when authorization is missing, a gate cannot be
legitimately cleared, or the failure class changes.
