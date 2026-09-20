# Test report — feature_116 O6c wild payback measurement (Programming → Testing, docs-only)

> Date: 2026-09-20 · Phase: Programming → Testing · Type: `minor_feature` (no TDD).
> Scope: metric table + run-log template + thresholds; D1 locked, no `src/`/`tests/` edits.

## Evidence

- Analysis 001: `.meta/.../3.analysis/.../analysis_001_payback_metric.md` (G15/G16 reproducer + 093/098 oracle + sidecar budget).
- Design 001: `.meta/.../4.design/.../design_001_metric_template.md` (metric cols + template + O6a ≥15%/10% / O6b ≥25%/15% thresholds).
- Impl notes: `.meta/.../5.implementation/.../impl_notes.md` (template dry-run vs live rev 60 / suite 1880 baseline).
- `omt_phase` ledger: Analysis → Design → Programming (scopes recorded; `src/` unlocked but unused).

## Verification

- `harnessc check`: FAIL (pre-existing WIP, not this slice) — `budget work_md: 9758 B > 9728 B` from uncommitted feature_115 `WORK.md` row (+30 B). No new harness-surface edit in this slice; budget grow deferred to feature_115 commit per receipt discipline.
- `omt_q{drift}`: 0 net↔ledger drifts (hygiene only, same as resume baseline).
- Full suite: not re-run (docs-only; baseline 1880 + 2 deselected from feature_115 Done holds; no code touched).
- Goldens: none (measurement runs are evidence, not goldens; future hermetic pin needs tests/ canary).

## Residuals

- N≥10 wild runs pending (2 pilots first); threshold decision O6a/O6b/defer pending runs.
- Feature_115 WIP still uncommitted (user commit) — blocks `check` green, not this design.

## Decision

- Design_ready: metric + template + thresholds approved for pilot use; advance to Testing (user close/ship call for Done).
