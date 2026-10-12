# Design 001 — omt-verify-closeout pilot (manual-only)

Feature: feature_158.pilot_verify_closeout · Date: 2026-10-12
Supersedes: `analysis_001_verify_scope.md`.

## Artifacts (new files only)

1. `.opencode/skills/omt-verify-closeout/SKILL.md` — frontmatter `name: omt-verify-closeout`,
   `description>=20` (re-run closeout evidence before DONE, return envelope),
   `metadata: {opencode/slash:"true", opencode/autoinvoke:"false"}`.
   Body: Use when (feature slug in Testing, closeout requested) / Do not use when
   (slug unknown, or commit already landed) / Procedure 6 steps
   (preserve slug → preflight → check 5 phase docs exist → `doctor` related skills →
   run feature goldens subprocess → WORK budget read → return envelope) / Stop.
2. `.opencode/skills/omt-verify-closeout/skill.contract.json` — id==dir, 0.1.0,
   procedural, inputs[feature_slug], requires[omt_status.preflight, omt_q.state, omt_nav.nav],
   allowed[read_harness_state], forbidden 3, state_owner external,
   result_schema omt-skill-result/v1,
   stop_when[verified, blocked, not_applicable, inconclusive].
3. `.opencode/skills/omt-verify-closeout/references/closeout_checklist.md` — evidence
   checklist (docs → doctor → goldens → WORK → TDD-done claim → split_proof claim).
4. `tests/harness_meta/feature_158.pilot_verify_closeout/test_verify_closeout_meta.py` — 7 goldens:
   contract-valid, doctor-green, checklist-exists, stop→outcome mapping,
   missing-report negative (bogus slug → `not_applicable` envelope shape),
   red-doctor negative (tampered contract copy → validator errs),
   envelope `ok⇔succeeded` on verify results.

## Non-goals

- No auto-commit, no `omt_session` compat, no full-suite re-run, no net_to_md.

## Acceptance

- `doctor omt-verify-closeout` green; `list` shows 3 pilots sorted.
- 7 goldens green; 154–157 suites green; split_proof 39/39; WORK in budget.
- TDD single-cycle RED→GREEN same node.

## Rollout

- Land skill + checklist + goldens in one commit; Phase3 continues with session-compat leg.
