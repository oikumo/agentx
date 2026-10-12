# Operation Spec — omt-resume-work pilot (feature_157)

> Companion to `design_001_resume_pilot.md`. Exact operations, pinned surface.

## `.opencode/skills/omt-resume-work/SKILL.md`

- Frontmatter: `name: omt-resume-work`, `description: >` >=20 chars
  ("Reconcile a paused skills project across owners without inventing state."),
  `metadata.opencode/slash: "true"`, `metadata.opencode/autoinvoke: "false"`.
- Sections: `## Use when` (pause pointer present) / `## Do not use when`
  (no pause, or failure is not a resume task) / `## Procedure` (6 numbered steps,
  step 6 "Return `omt-skill-result/v1`.") / `## Stop` (3 conditions).

## `.opencode/skills/omt-resume-work/skill.contract.json`

- `schema_version:"1"`, `id:"omt-resume-work"`, `version:"0.1.0"`, `mode:"procedural"`,
  `inputs:["pause_pointer","project_slug","expected_head?"]` (>=1),
  `requires:["omt_status.preflight","omt_q.state","omt_nav.nav"]` (subset of KNOWN_OPS),
  `allowed_effects:["read_harness_state"]`,
  `forbidden_effects:[weaken_gate,forge_receipt,expand_scope_without_authority]`,
  `state_owner:"external"`, `result_schema:"omt-skill-result/v1"`,
  `stop_when:[reconciled,blocker_found,authorization_required,not_resumable]` (>=2).

## `references/resume_checklist.md`

- 6 sections in §0+§5 order, each with checkbox + expected command/artifact;
  no policy text (reference only, OMT is authority).

## Tests `test_resume_pilot_meta.py::TestResumePilot`

- `test_accepts_contract_valid` — `skill.validate_contract` [] on shipped contract.
- `test_doctor_greens_resume_work` — subprocess `doctor omt-resume-work` rc 0 + "contract OK".
- `test_checklist_covers_owners` — checklist mentions pause, HEAD/status, CURRENT_STATE,
  PROJECT, feature docs, WORK.
- `test_stop_when_maps_to_outcomes` — via `skill_result.from_stop_when`-style mapping
  (reconciled→succeeded etc.; implement `pilot_outcome(stop)` helper in test or reuse envelope).
- `test_stale_pause_yields_blocked` — `expected_head="deadbeef"` vs real HEAD →
  `make_blocked(GATE_DENIED,...)` envelope, `ok==False`.
- `test_rejects_unknown_field`, `test_rejects_short_stop_when` — validator pins.
