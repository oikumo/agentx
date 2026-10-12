# StateScope — ownership of skill memory (feature_156)

> Skills are stateless routers (`state_owner=external`). Memory lives in owners below.
> Skills own NOTHING — no `.skill-state.json`, no cached verdicts, no copied policy.

| Scope | Owner | Examples | Lifetime |
|---|---|---|---|
| invocation | single tool attempt | operation, path, observed result, envelope | ephemeral (one retry ≤1) |
| session | opencode session DB (read-only) | transcript, `omt_session` traces | session (8h resume digest) |
| feature | `.meta/.../features/<slug>/` | FEATURE.md, analysis/design/impl/test_report | feature lifecycle |
| project | `.projects/meta/<slug>/` | PROJECT.md, CURRENT_STATE.md | project lifecycle |
| harness | OMT authority | gates, ledger, net, receipts, `skill.py doctor` | permanent |

Rules:
- R1: Skills query current OMT response as authority (policy by reference, D5).
- R2: `state_owner` MUST be `external` (contract validator enforces).
- R3: No `.skill-state.json` anywhere under `.opencode/skills/` / `.agents/skills/` (`doctor` warns).
- R4: Envelopes carry `stateRevision?` + `evidence[]` pointers, never stores.
- R5: Resume reconciles owners (session→feature→project→harness), never invents state.

Pilots (`omt-recover-block`, `omt-resume-work` manual-only) reference owners only.
