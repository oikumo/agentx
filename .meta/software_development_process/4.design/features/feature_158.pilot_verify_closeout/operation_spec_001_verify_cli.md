# Operation Spec — omt-verify-closeout pilot (feature_158)

> Companion to `design_001_verify_pilot.md`. Pinned surface.

## SKILL.md

- Frontmatter `name: omt-verify-closeout`, `description>=20`
  ("Re-run closeout evidence for a feature before DONE, return envelope."),
  `metadata.opencode/slash:"true"`, `metadata.opencode/autoinvoke:"false"`.
- Sections Use when / Do not use when / Procedure (6 steps, step 6 returns envelope) / Stop (3).

## skill.contract.json

- `schema_version:"1"`, `id:"omt-verify-closeout"`, `version:"0.1.0"`, `mode:"procedural"`,
  `inputs:["feature_slug"]`, `requires:["omt_status.preflight","omt_q.state","omt_nav.nav"]`,
  `allowed_effects:["read_harness_state"]`,
  `forbidden_effects:[weaken_gate,forge_receipt,expand_scope_without_authority]`,
  `state_owner:"external"`, `result_schema:"omt-skill-result/v1"`,
  `stop_when:[verified,blocked,not_applicable,inconclusive]`.

## references/closeout_checklist.md

- 6 checks in order + envelope mapping table; reference only.

## Tests `test_verify_closeout_meta.py::TestVerifyCloseout`

- contract-valid (direct `validate_contract`), doctor-green (subprocess),
  checklist-covers (docs, doctor, goldens, WORK, TDD, split_proof keywords),
  stop→outcome via `make_*` (verified→succeeded, blocked→blocked, not_applicable,
  inconclusive), missing-report (bogus slug → `make_not_applicable` valid),
  red-doctor (tampered contract dict → errs non-empty),
  ok⇔succeeded (succeeded envelope ok True; blocked ok False).
