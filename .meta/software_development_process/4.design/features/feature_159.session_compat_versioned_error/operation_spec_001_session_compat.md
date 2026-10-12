# Operation Spec — session-compat versioned error (feature_159)

> Companion to `design_001_session_compat.md`. Pinned surface.

## service.py `dispatch`

- `SERVICE_VERSION=1` (int, matches `BUNDLE_VERSION`/`MANIFEST_VERSION`).
- `_refuse(error, **extra)` always includes `version:1`.
- New `_versioned_error(code, remediation, evidence, retryable, extra)` returns `{ok:False, version:1, error:<lower>, code:<UPPER_SNAKE>, remediation, evidence[], retryable, read_only:True, ...extra}`.
- Sessions block:
  - `db==""` → `error:missing_db`, `code:MISSING_DB`, remediation mentions explicit `--db` + no-hardcode, `retryable:True`.
  - `FindingError` with `name in (source_unreadable, schema_unsupported, ...)` → `error:sessions_failed`, `detail:<name>`, `code:<NAME.UPPER>`, `source:{path}`, `read_only:True`, remediation per code.
  - `query_limit_exceeded` preserves `total/cap/cursor/detail_ref` + adds `version/code/remediation`.
  - Success adds `version:1`, `read_only:True`, preserves `result/detail_ref`.
- All other ops (`query/inspect/trace/profile/compare/export/experiment` refusals, `unknown_op`, `engine_error` in plugin) also carry `version:1` where produced in service.

## skill_result.py `from_session(res)`

- Signature `from_session(res:dict)->dict`; input is service dict (any shape, never raises).
- Mapping: `ok True` → `make_succeeded("OK", [detail_ref or "omt_session"])`; `ok False` → `make_blocked(code UPPER_SNAKE or SESSIONS_FAILED, blocker{gate:"omt_session",code,message:detail/error,remediation?,requiresApproval:False}, evidence[detail_ref/detail], retryable bool)`.
- Unknown/empty → `make_failed("SESSION_MAPPING_FAILED", ...)`.
- Codes produced: `MISSING_DB`, `SOURCE_UNREADABLE`, `SCHEMA_UNSUPPORTED`, `QUERY_LIMIT_EXCEEDED`, `SESSIONS_FAILED`, `OK`.

## plugin `omt_session.ts`

- No argv change (OP_ARGS pin preserved); comment records `SERVICE_VERSION=1` passthrough contract: service `version` returned unchanged; `unknown_op`/`no_safe_launch`/`engine_error` from plugin include `version:1`.
- `directory==""` drop preserved; `db==""` drop preserved (service owns `missing_db`).

## adapter.py

- Doc-only: `DEFAULT_DB_PATH` comment states explicit-`db` required, no auto-use on `""`; `connect()` `mode=ro` unchanged.

## Tests `test_session_compat_meta.py::TestSessionCompat`

- 7 goldens as in design: missing-db, source_unreadable, schema_unsupported (live), over-budget (live), read-only proof, no-secret-path, envelope mapping. All assert `version==1`, `code` UPPER_SNAKE, `validate_envelope` clean on mapped envelopes.
