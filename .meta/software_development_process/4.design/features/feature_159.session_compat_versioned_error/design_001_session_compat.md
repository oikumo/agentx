# Design 001 — session-compat versioned error (manual-only harness fix)

Feature: feature_159.session_compat_versioned_error · Date: 2026-10-12
Supersedes: `analysis_001_session_compat_scope.md`.

## Artifacts (additive only, no renames)

1. `scripts/session_inspect/service.py` — add `SERVICE_VERSION=1`; `_refuse()` always includes `version:1`; new `_versioned_error(code, remediation, evidence, retryable, extra)` helper mapping closed-vocabulary lowercase → UPPER_SNAKE `code`. Sessions block:
   - `db==""` → `missing_db` versioned (`code:MISSING_DB`, remediation:`pass explicit --db /path/to/opencode.db read-only mode=ro; skills must not hardcode path`, `retryable:true`, `read_only:true`, `evidence:["service dispatch sessions"]`).
   - `FindingError(source_unreadable|schema_unsupported)` → preserve `detail` name + add `code` UPPER_SNAKE mirror, `source:{path}`, `schema_markers` when available, `read_only:true`, remediation per code (absent→check path + perms; unsupported→pin drizzle 21 + missing table list, do NOT create tables).
   - `query_limit_exceeded` → add `version:1`, `code:QUERY_LIMIT_EXCEEDED`, remediation with `session_ids`/`time_from` bounding, keep `total/cap/cursor/detail_ref`.
   - Success paths add `version:1` + `read_only:true` + `detail_ref` preserved.
2. `scripts/omt/skill_result.py` — add `from_session(res:dict)->dict`: maps service dict → envelope v1 (`succeeded/OK` on `ok True`; `blocked/SOURCE_UNREADABLE|SCHEMA_UNSUPPORTED|QUERY_LIMIT_EXCEEDED|MISSING_DB|SESSIONS_FAILED` with `blocker{gate:"omt_session",code,message,remediation?,requiresApproval:False}`, `retryable` from service, `evidence` from `detail_ref`/`evidence`). Fail-closed: unknown shape → `failed/SESSION_MAPPING_FAILED`.
3. `.opencode/plugins/omt_session.ts` — no logic change (passthrough preserved for OP_ARGS pin); add comment pinning `SERVICE_VERSION=1` + version passthrough assert in tests (plugin returns service `version` unchanged; `engine_error`/`unknown_op` also carry `version:1`).
4. `scripts/session_inspect/adapter.py` — doc-only: `DEFAULT_DB_PATH` comment clarifies explicit-`db` required (no auto-use when `""`); `connect()` already `mode=ro` — add `read_only:true` note for error callers (no behavior change to avoid 2nd-edit churn).
5. `tests/harness_meta/feature_159.session_compat_versioned_error/test_session_compat_meta.py` — 7 goldens:
   - version-present on missing-db (no `db` → `version:1`, `code:MISSING_DB`, `read_only:true`).
   - source_unreadable versioned (bogus path → `code:SOURCE_UNREADABLE`, remediation mentions explicit `--db`).
   - schema_unsupported versioned (live DB + single `session_ids` → `code:SCHEMA_UNSUPPORTED`, no traceback leak, `detail` ≤200).
   - over-budget versioned (live DB + agentx directory → `QUERY_LIMIT_EXCEEDED`, `total>cap`, cursor present).
   - read-only proof (live DB `mode=ro` write attempt fails; adapter `connect` URI contains `mode=ro`).
   - no-secret-path (all `.opencode/skills/*/SKILL.md` + `skill.contract.json` contain no `opencode.db`, no `/home/`, no `sqlite` path).
   - envelope mapping (`from_session` on 4 failure shapes → `validate_envelope` clean, `ok⇔succeeded`, `blocked` carries `blocker`).

## Non-goals

- No auto-use of default DB, no `data_migration` creation, no skill-side SQLite open, no `omt-session-evidence` skill, no net_to_md, no full-suite re-run in goldens.

## Acceptance

- `service.dispatch` all paths carry `version:1`; existing dispatcher tests still green (additive).
- `skill_result.from_session` 4 shapes validate; `doctor` x3 still green; `list` 3 pilots ok.
- 7 goldens green; 154–158 suites green; split_proof_meta 39/39 (CI-owned, not re-run in goldens); WORK ≤11264.
- TDD single-cycle RED→GREEN same node.

## Rollout

- Land service + adapter doc + skill_result + plugin comment + goldens in one commit; Phase3 continues with verify-closeout doctor hardening, then Phase4 validation (smoke + 24-trial).
