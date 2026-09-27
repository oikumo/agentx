# Design 001 — Pilot launch path (promoted from 131/design_004 DRAFT)

> Feature: `feature_132.pilot_launch_path` · Phase: Design · Date: 2026-09-27 · Status: approved for build (no launches yet)
> Promotes: `feature_131/.../design_004_pilot_launch.md` (DRAFT) — full checklist §§1–8 applies here without duplication.
> Project: `meta_harness_13` reopened active (was complete) for this follow-up.

## Link

Canonical checklist lives at `4.design/features/feature_131.opencode_session_inspection_and_experiments/design_004_pilot_launch.md`.
This file is the §12 artifact that unblocks `src/` for `feature_132`; normative content stays in design_004 to avoid fork.

## Scope for feature_132 (Design only now)

- Approve §§3–4 pre-conditions: manifest/seed/digests/budgets, `/tmp` isolation, `omt_net` claims (no second scheduler), overhead + cancel/resume, reopen.
- `run` stays `no_safe_launch` until Programming implements §§4–5 with TDD + isolation/budget gates.
- No launches, no tokens in Design. Next: Programming declaration + TDD (`run` + bounds + collect/validate) only after this Design is reviewed.

## Resume

- design_004 §§1–8 → this file → PLAN.md → TDD → test_report addendum → `omt_complete` Design→Programming→Testing→Done.
