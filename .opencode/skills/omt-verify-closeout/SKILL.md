---
name: omt-verify-closeout
description: >
  Re-run closeout evidence for a feature before DONE, return envelope.
metadata:
  opencode/slash: "true"
  opencode/autoinvoke: "false"
---

## Use when

A feature slug is in Testing and closeout verification is requested before DONE.

## Do not use when

The slug is unknown, or the commit already landed (verify the commit instead).

## Procedure

1. Preserve the feature slug.
2. Ask `omt_status.preflight` for the verify operation and `omt_q.state` for ledger health.
3. Treat the current OMT response as authority; do not restate policy from memory.
4. Check the 5 phase docs exist (FEATURE/analysis/design/impl/test_report).
5. Run `skill.py doctor` on related skills + feature goldens (subprocess) + WORK budget read (see `references/closeout_checklist.md`).
6. Return `omt-skill-result/v1`.

## Stop

Stop rather than approving closeout when docs are missing, doctor is red, goldens fail, or WORK is over budget.
