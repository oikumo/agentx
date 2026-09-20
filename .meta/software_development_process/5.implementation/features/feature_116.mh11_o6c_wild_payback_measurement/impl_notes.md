# Impl notes — feature_116 O6c wild payback measurement (Programming, docs-only)

> No `src/`/`tests/` edits. Programming = validate Design 001 template against live baselines + record pilot readiness.

## What was done

- Analysis 001 (`analysis_001_payback_metric.md`): G15/G16 reproducer + 093/098 oracle + sidecar budget.
- Design 001 (`design_001_metric_template.md`): metric table (wall/tokens/io/verify/success/check/build/suite/payback) + run-log template + pre-registered O6a/O6b/defer thresholds.
- Template dry-run vs live: rev 60 `drained_complete`, suite 1880 + 2 deselected, `check 265/0`, pool 0/0/7 — columns map 1:1 (no missing source; transcript fields exist in 093 probe).
- Pilot readiness: 2-run pilot (same pair serial→dispatch, ≤2 workers, disjoint files) can start without harness change; N≥10 deferred to wild sessions per budget.

## Sites touched

- `.meta/.../3.analysis/.../analysis_001_payback_metric.md` (new)
- `.meta/.../4.design/.../design_001_metric_template.md` (new)
- This file (new)

## Non-interference

- No places/transitions; no ledger kinds; `src/agentx/` untouched (D1); `uv` only.
