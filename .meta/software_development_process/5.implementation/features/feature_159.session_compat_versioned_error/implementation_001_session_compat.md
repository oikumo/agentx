# Implementation 001 — session-compat versioned error (feature_159)

## Files (additive only)

- `scripts/session_inspect/service.py` — `SERVICE_VERSION=1`, `_upper_code`, `_refuse` adds `version/code/read_only`, `_versioned_error` helper; sessions `missing_db` early return, `query_limit_exceeded` versioned, success adds `version/read_only`, exception maps `source_unreadable/schema_unsupported/query_limit_exceeded/sessions_failed` with remediation + source path; tail fallback versioned.
- `scripts/omt/skill_result.py` — `from_session(res)` maps service dict to envelope v1 (succeeded OK / blocked with gate omt_session / failed mapping fallback), fail-closed.
- `.opencode/plugins/omt_session.ts` — comment pins `SERVICE_VERSION=1` passthrough; own refusals (`unknown_op/no_safe_launch/engine_error`) carry `version:1/code/read_only`.
- `tests/harness_meta/feature_159.session_compat_versioned_error/test_session_compat_meta.py` — 7 goldens.

## Corrections (goldens drove)

- Empty `db=""` never hit `DEFAULT_DB_PATH` (None-only default) — now explicit `MISSING_DB` with `--db` remediation, no auto-use.
- Live DB lacks `data_migration` — surfaces as `SCHEMA_UNSUPPORTED` (no table creation, no traceback).
- `query_limit_exceeded` keeps `total/cap/cursor/detail_ref` + version/code.
- `mode=ro` already present — pinned + write-fail proof; skills grep clean pinned.

## Consequence

- 7/7 green; dispatcher/adapter/schema/plugin-args 13 passed 1 skipped; doctors x3 green; no renames (additive).
