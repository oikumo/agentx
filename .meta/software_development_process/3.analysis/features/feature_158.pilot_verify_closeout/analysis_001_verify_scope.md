# Analysis 001 — verify-closeout pilot scope

Feature: feature_158.pilot_verify_closeout · Phase: Analysis · Date: 2026-10-12
Consumes: 154 + 155 + 156 + 157. Closes Phase2 pilots, opens Phase3 evidence.

## Problem

Closeout invents DONE: `omt_complete Testing→Done` clicked while test_report claims
unverified suites, WORK over budget, `doctor` red, or TDD `done` never ran.
Each feature's test_report lists gates — but no contracted procedure re-runs the
claims and returns `verified` vs `blocked` machine-readably before commit.

## Evidence

- 154/155/157 test_reports pin gates: `doctor`, feature goldens, no-regression set,
  `tdd done`, WORK budget, `split_proof_meta` 39/39.
- `omt_complete` verifies phase artifacts (docs exist) — not live suite results.
- `omt_tdd done` verifies TDD checklist + 17-baseline no-new-failures — scoped to TDD.
- PROJECT Phase3: evidence-reliable 11-15; pilots pass positive/negative/bypass witnesses.

## Constraints

- Manual-only `autoinvoke:false`; read-only checks (no writes except envelope);
  commit stays separate mechanical step after pick (free-commit carve-out).
- New files only +1 skill dir: `.opencode/skills/omt-verify-closeout/{SKILL.md,
  skill.contract.json,references/closeout_checklist.md}`; goldens under
  `tests/harness_meta/feature_158.pilot_verify_closeout/`.
- Checks must be fast + hermetic: `doctor`, file-exists (FEATURE/analysis/design/impl/
  test_report), `validate_envelope` on test_report claims?, WORK size ≤ budget,
  goldens green for the feature under test (subprocess, no full suite).
  `split_proof_meta` NOT re-run in skill (too heavy — test_report claim + CI owns it).

## Alternatives

- A) Contracted skill + closeout checklist + 7 goldens incl. red-doctor negative +
  missing-report negative + envelope mapping (chosen).
- B) Auto-closeout gate blocking `omt_complete` (rejected — second harness, autonomy
  before evidence; D2).
- C) Prose-only checklist (rejected — untestable).

## Scope lock

Skill `omt-verify-closeout` v0.1.0: inputs[feature_slug]; requires[omt_status.preflight,
omt_q.state, omt_nav.nav]; allowed[read_harness_state]; forbidden 3; stop_when[verified,
blocked, not_applicable, inconclusive]. Procedure: preserve slug → preflight →
check FEATURE+4 phase docs exist → `doctor` on related skills → run feature goldens
(subprocess q) → WORK budget read → return envelope (`succeeded/OK` verified;
`blocked/*` naming the failed check with remediation; `not_applicable` for unknown slug).
Session-compat (`omt_session` versioned error) OUT — separate Phase3 leg.
