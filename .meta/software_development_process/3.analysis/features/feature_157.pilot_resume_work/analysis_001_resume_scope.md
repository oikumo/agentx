# Analysis 001 — resume-work pilot scope

Feature: feature_157.pilot_resume_work · Phase: Analysis · Date: 2026-10-12
Consumes: 154 (contract) + 155 (envelope) + 156 (StateScope). Companion: omt-recover-block skeleton.

## Problem

Resumption invents state: stale pause file treated as live, `NEXT` guessed from file
while live net says idle, baselines skipped, STATE reconciled from memory not owners.
Pause §0 already pins read-order + fingerprints — but no contracted procedure enforces it,
and no envelope tells `reconciled` from `blocked` machine-readably.

## Evidence

- Pause `pause_2026-10-12_meta_harness_skills.md` §0 read-order (THIS → log/status →
  CURRENT_STATE+PROJECT → feature docs → skill files → WORK rows) + §5 fingerprints
  (HEAD, `git status`, WORK size, greens) — manual today, untestable.
- Recover-block skeleton `.opencode/skills/omt-recover-block/` (manual-only
  `autoinvoke:false`, 6-step procedure, 4-way stop_when) — resume-work missing.
- PROJECT success: pilots pass positive/negative/bypass witnesses; resume reconciles
  without inventing state.
- Gates: pilot-functional 11-08; test pyramid (schema→contract→scenario→replay→integration→smoke).

## Constraints

- Manual-only `opencode/autoinvoke:false`; stateless; policy by reference (D5);
  return `omt-skill-result/v1`; no auto-fix (approval gate holds).
- New files only +1 skill dir: `.opencode/skills/omt-resume-work/{SKILL.md,skill.contract.json,
  references/resume_checklist.md}`; goldens `tests/harness_meta/feature_157.pilot_resume_work/`.
- Deterministic checks only (file exists, HEAD matches, WORK size, `doctor` green);
  no LLM, no network, no net_to_md (STALE owned elsewhere).

## Alternatives

- A) Contracted skill + checklist + `skill.py new` scaffold + 7 goldens incl. stale-pause
  negative + envelope-mapping (chosen — mirrors 154/155 batches).
- B) Auto-resume runtime (rejected — autonomy before contracts, violates D2).
- C) Prose-only checklist (rejected — untestable, drifts).

## Scope lock

Skill `omt-resume-work` v0.1.0: inputs[pause_pointer, project_slug, expected_head?];
requires[omt_status.preflight, omt_q.state, omt_nav.nav]; allowed[read_harness_state];
forbidden canonical 3; stop_when[reconciled, blocker_found, authorization_required,
not_resumable]. Procedure: preserve pointer → preflight → verify fingerprints (HEAD/status/
WORK/CURRENT_STATE) → reconcile owners session→feature→project→harness → return envelope
(`succeeded/OK` reconciled; `blocked/GATE_DENIED` on fingerprint mismatch;
`not_applicable` when nothing paused; `inconclusive` on conflicting owners).
Recover-block hardening OUT (separate 158 if needed); verify-closeout OUT (Phase3).
