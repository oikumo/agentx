# Test Report — feature_154.skill_contract_v1

Date: 2026-10-12 · major_feature (TDD required, batch single-cycle).

## Changes (new-files-only, no harness-surface 2nd-edit)

- `scripts/omt/skill.py` (`doctor|new|test|list`, stdlib only, deterministic, no LLM/network).
- `.opencode/skills/omt-recover-block/{SKILL.md,skill.contract.json}` — first contracted pilot skeleton (manual-only `autoinvoke:false`).
- `tests/harness_meta/skill_contract_meta/test_skill_contract_meta.py` — 7 goldens (validator behaviors).
- Schema folded into validator (static allowlists, no separate `.meta/templates/skill.contract.schema.json` file — per analysis alternative A, design §Non-goals).

## TDD (batch-of-7 single-cycle, cf. feature_152 batch-of-10)

- Testlist 7 behaviors: minimal-valid accept, unknown-field reject, name-mismatch reject, missing-forbidden reject, empty-stop_when reject, doctor-green, list-sorted.
- RED then GREEN at same node `test_skill_contract_meta.py::TestSkillContract::test_accepts_minimal_valid` (same-node rule, GOTCHA top-1) — single cycle closed all 7 (no per-behavior red/green).
- `omt_tdd done` wrapper bug: passes `--test-node` but `tdd_check.py done` only accepts `--feature/--session` — retried without `test_node`, then `DONE ✅ all checklist verified`.
- `sync --feature` → no stranded REDs.

## Suites

| Gate | Result |
|---|---|
| `skill.py doctor omt-recover-block` | ✅ contract OK (deterministic) |
| `pytest tests/harness_meta/skill_contract_meta -q` | 7 passed (2.3–2.4s) |
| `tdd_check.py done --feature feature_154.skill_contract_v1` | ✅ DONE — feature_suite true, repo_hygiene true, refactor true, naming true; 16 drift tolerated (pre-existing at Programming baseline) |
| `pytest tests/harness_meta/omt/test_omt_docs_drift_pins.py::test_work_md_within_budget -q` | 1 passed after WORK trim (11263/11264; pause line 378B→short, detail lives in pause file) |
| `split_proof_meta` | deferred to commit gate (design acceptance: still 39/39 — run before commit) |

## Notes

- No `src/` edits; no receipts needed (new-files-only).
- No ad-hoc `*_PROOF.md` (folded here per FEATURE naming convention).
- WORK budget: pause line pushed 11428>11264, trimmed to 11263 (1B headroom) — restores `repo_hygiene_passes`; no budget growth needed.
- Next: `omt_complete Testing → Done` → commit Phase1 set → feature_155 envelope.
