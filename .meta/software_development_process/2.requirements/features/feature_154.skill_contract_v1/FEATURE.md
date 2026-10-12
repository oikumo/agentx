# Feature 154: Skill Contract V1

> **Status:** [x] Done (2026-10-12)
> **Created:** 2026-10-11
> **WORK.md task:** proj:meta_harness_skills / Phase1 contracts

---

## Summary

Verifiable contract for procedural OpenCode skills: `skill.contract.json` v1 (trigger, near-misses, requires, allowed/forbidden effects, state_owner=external, result_schema, stop_when) + validator + `skill.py doctor|new|test|list` scaffold. Makes "recover-block / resume-work" promises testable without turning skills into a runtime.

## Scope (one sentence — what "done" looks like)

Every skill has a validated contract, `doctor` is deterministic green, and pilots consume only contracted authority.

## Task type

major_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_154.skill_contract_v1/` | [x] |
| Analysis | Analysis doc | `3.analysis/features/feature_154.skill_contract_v1/analysis_001_*.md` | [x] |
| Design | Design doc | `4.design/features/feature_154.skill_contract_v1/design_001_*.md` | [x] |
| Implementation | Impl notes | `5.implementation/features/feature_154.skill_contract_v1/` | [x] |
| Testing | Test report | `6.testing/features/feature_154.skill_contract_v1/` | [x] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.
