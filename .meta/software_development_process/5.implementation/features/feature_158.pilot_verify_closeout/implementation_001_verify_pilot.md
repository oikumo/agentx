# Implementation 001 — omt-verify-closeout pilot (feature_158)

## Files (new files only, no harness-surface edits)

- `.opencode/skills/omt-verify-closeout/SKILL.md` — frontmatter `name==dir`,
  `description>=20`, `autoinvoke:false`, Use when / Do not use when / Procedure(6) / Stop.
- `.opencode/skills/omt-verify-closeout/skill.contract.json` — id==dir, 0.1.0, procedural,
  inputs[feature_slug], requires 3 (preflight, q.state, nav), allowed[read_harness_state],
  forbidden 3, state_owner external, result_schema omt-skill-result/v1,
  stop_when[verified, blocked, not_applicable, inconclusive].
- `.opencode/skills/omt-verify-closeout/references/closeout_checklist.md` — 6 evidence
  checks (docs → doctor → goldens → WORK → TDD claim → split_proof claim).
- `tests/harness_meta/feature_158.pilot_verify_closeout/test_verify_closeout_meta.py` — 7 goldens.

## Corrections (goldens drove)

- `requires` known-ops subset; `stop_when>=2`; no unknown fields (mirrors 154/157).
- Missing slug → `not_applicable` (not failure) — golden pins unknown-slug path.
- Tampered `state_owner` rejected — golden pins contract validator reuse.
- Verify envelopes obey `ok⇔succeeded` — golden pins mismatch reject.

## Consequence

- `doctor omt-verify-closeout` green; `list` shows 3 pilots sorted; 7/7 green;
  no shared code touched (154–157 unaffected).
