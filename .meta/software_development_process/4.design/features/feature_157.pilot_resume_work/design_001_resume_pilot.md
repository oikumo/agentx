# Design 001 — omt-resume-work pilot (manual-only)

Feature: feature_157.pilot_resume_work · Date: 2026-10-12
Supersedes: `analysis_001_resume_scope.md`.

## Artifacts (new files only)

1. `.opencode/skills/omt-resume-work/SKILL.md` — frontmatter `name: omt-resume-work`,
   `description>=20` (resume a paused skills project without inventing state),
   `metadata: {opencode/slash:"true", opencode/autoinvoke:"false"}`.
   Body: Use when (pause pointer + project slug present) / Do not use when
   (live failure is compiler/test error, or no pause exists) / Procedure 6 steps
   (preserve pointer → preflight exact op/path → verify fingerprints HEAD/status/WORK/
   CURRENT_STATE → reconcile owners → retry nothing (read-only) → return envelope) / Stop.
2. `.opencode/skills/omt-resume-work/skill.contract.json` — id==dir, version 0.1.0,
   mode procedural, inputs[pause_pointer, project_slug, expected_head?],
   requires[omt_status.preflight, omt_q.state, omt_nav.nav],
   allowed[read_harness_state], forbidden 3 canonical, state_owner external,
   result_schema omt-skill-result/v1, stop_when 4
   (reconciled, blocker_found, authorization_required, not_resumable).
3. `.opencode/skills/omt-resume-work/references/resume_checklist.md` — fingerprint
   checklist (§0 order + §5 baselines): pause file → `git log -2` + `git status` →
   CURRENT_STATE newest + PROJECT Status/Quick Start → feature FEATURE/analysis/design/
   impl/test_report → skill SKILL.md+contract → WORK Projects + Paused line.
4. `tests/harness_meta/feature_157.pilot_resume_work/test_resume_pilot_meta.py` — 7 goldens:
   contract-valid accept, doctor-green, checklist-exists (6 sections),
   stop_when→outcome mapping (reconciled→succeeded, blocker_found→blocked,
   authorization_required→blocked, not_resumable→not_applicable),
   stale-pause negative (expected_head mismatch → blocked envelope),
   unknown-field reject, envelope `ok⇔succeeded` on pilot results.

## Non-goals

- No autoinvoke, no recover-block edits, no `omt_session` compat, no net_to_md,
  no `.opencode/lib` wiring.

## Acceptance

- `skill.py doctor omt-resume-work` green; `skill.py list` shows both pilots sorted.
- 7 goldens green; 154/155/156 suites still green; split_proof_meta 39/39.
- TDD batch single-cycle RED→GREEN same node; WORK within budget.

## Rollout

- Land skill dir + checklist + goldens in one commit; Phase2 continues (recover-block
  hardening only if witnesses demand, else verify-closeout next).
