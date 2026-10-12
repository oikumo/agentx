# Implementation 001 — omt-resume-work pilot (feature_157)

## Files (new files only, no harness-surface edits)

- `.opencode/skills/omt-resume-work/SKILL.md` — frontmatter `name==dir`, `description>=20`,
  `autoinvoke:false`, sections Use when / Do not use when / Procedure(6, step 6 returns envelope) / Stop.
- `.opencode/skills/omt-resume-work/skill.contract.json` — id==dir, version 0.1.0,
  mode procedural, inputs 3 (pause_pointer, project_slug, expected_head),
  requires 3 (`omt_status.preflight`, `omt_q.state`, `omt_nav.nav` — subset of KNOWN_OPS),
  allowed[read_harness_state], forbidden 3 canonical, state_owner external,
  result_schema omt-skill-result/v1, stop_when 4.
- `.opencode/skills/omt-resume-work/references/resume_checklist.md` — 7-item fingerprint
  checklist in pause §0+§5 order (reference only, OMT is authority).
- `tests/harness_meta/feature_157.pilot_resume_work/test_resume_pilot_meta.py` — 7 goldens
  (contract-valid, doctor-green, checklist-covers-owners, stop→outcome mapping via
  `skill_result.make_*`, stale-pause blocked via real HEAD vs deadbeef, unknown-field,
  short-stop_when).

## Corrections (goldens drove)

- `requires` must be known-ops subset — golden `test_accepts_contract_valid` pins via `validate_contract`.
- Checklist must name all owners/fingerprints — golden `test_checklist_covers_owners` pins
  (pause, HEAD, status, CURRENT_STATE, PROJECT, feature, WORK).
- Stale HEAD must yield `ok==False/blocked` valid envelope — golden `test_stale_pause_yields_blocked` pins.
- `stop_when>=2` + no unknown fields — goldens pin (mirrors 154).

## Consequence

- `doctor omt-resume-work` green; `list` shows both pilots sorted; 7/7 green;
  154/155/156 suites unaffected (no shared code touched).
