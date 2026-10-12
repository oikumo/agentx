# Analysis 001 — CI skills validation job

Feature: feature_161.ci_skills_validation_job (minor) · Date: 2026-10-12
Pick A execution (CI automation, no autoinvoke, no live run).

## Problem

`pr-critical` already runs full `pytest tests/agentx tests/harness_meta -q` (covers 160 goldens which include doctors + dry_run), but the skills validation is invisible — buried in the full suite with no named job, no explicit doctor/dry_run steps, no fast signal. The REVISE closeout (mini 8-trial) has no automated guard against regression.

## Evidence

- `split.yml pr-critical` (153): `uv sync --frozen`, `uv pip check`, full pytest — green, but 3+ min, no skills-named steps.
- 160 goldens already prove: manifest v1, matrix 24/8 dry_run, gate refusals, doctors via subprocess, compare quality-gating, envelope mapping.
- `skill.py list/doctor` deterministic, hermetic, <30s; `experiment dry_run` `executed:false` safe for CI.

## Constraints

- Additive only to `split.yml` (new job, no edits to lane jobs); stdlib + `uv` only; no live run, no tokens, no autoinvoke change; WORK budget (11242/11264, trim-while-adding if needed).

## Alternatives

- A) New `skills-validation` job (chosen): checkout + setup-python + `uv sync --frozen` + `pytest feature_160` + `skill.py list` + `doctor x3` + dry_run matrix check. Fast (<2 min), named, PR-gated (`if: github.event_name != 'schedule'` like pr-critical).
- B) Extend `pr-critical` steps in place (rejected — mixes fast skills signal into slow full suite; harder to read).
- C) Nightly-only (rejected — 153 moved critical checks to PR for a reason).

## Scope lock

161 ships: `skills-validation` job in `split.yml` + this analysis + test_report (CI yaml validated via python yaml parse + pytest 160 green + doctors green). No src/ core edits, no skill changes.
