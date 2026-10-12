# Analysis 001 — session-compat versioned error scope

Feature: feature_159.session_compat_versioned_error · Phase: Analysis · Date: 2026-10-12
Consumes: 154 + 155 + 156 + 157 + 158. Opens Phase3 evidence remainder, unblocks deferred `omt-session-evidence`.

## Problem

`omt_session` either reads the live OpenCode SQLite DB read-only or it must return a
versioned machine-readable error — PROJECT.md success criterion. Today it does neither
machine-readably:

- `omt_session{op:sessions}` with no `db` → `{"ok":false,"error":"sessions_failed","detail":"source_unreadable"}` — bare lowercase error, no version, no code, no remediation, no read-only proof.
- With explicit live DB (`~/.local/share/opencode/opencode.db`, 3.6 GB, exists) + `session_ids` → same shape with `detail:"schema_unsupported"` (live DB lacks `data_migration`, has `migration`; `REQUIRED_TABLES` demands `data_migration`).
- With explicit DB + `directory=/home/oikumo/develop/production/agentx` → `query_limit_exceeded` with `total:1758 cap:20` — bounded but still unversioned, no envelope code.
- `service.py dispatch` defaults `db` to `""` (empty string), so `OpenCodeSqliteAdapter("")` never hits `DEFAULT_DB_PATH` (`None`-only default) — the documented candidate is unreachable by default.
- Plugin `.opencode/plugins/omt_session.ts` drops empty `db`/`directory` and passes through raw stdout — no version pin, no envelope mapping.
- No `skill_result.py` adapter for session failures; skills today have no DB path (grep clean) but nothing pins that invariant.

Caller needs a textual heuristic to tell `absent DB` vs `unsupported schema` vs `over-budget` — same confusion envelope v1 solved for blocked vs succeeded.

## Evidence

- `scripts/session_inspect/service.py:166-227` sessions block: `db=str(args.get("db",""))`, `SessionSelector`, `normalize_snapshot(ad.snapshot(sel))`, catch-all `except Exception as e: _refuse("sessions_failed", detail=str(e)[:200])`.
- `scripts/session_inspect/adapter.py:70-84` `connect()` raises `FindingError(source_unreadable)` on absent path; `capability_report()` raises `schema_unsupported` on missing `data_migration`.
- `scripts/session_inspect/schema.py:15` closed failure vocabulary (21 names incl. `source_unreadable`, `schema_unsupported`, `query_limit_exceeded`).
- Live probe 2026-10-12: DB exists (`-rw------- 3696566272`), tables include `session,message,part,event,event_sequence,__drizzle_migrations,migration` but NOT `data_migration`; `drizzle_count 21`; `session` rows for agentx exist (`ses_23500dd8...`).
- `scripts/session_inspect/exporter.py:15 BUNDLE_VERSION=1`, `manifest.py:14 MANIFEST_VERSION=1` — int-version precedent; service has none.
- `.opencode/plugins/omt_session.ts:76-92` argv passthrough, `execFileSync uv run python -m session_inspect.service`, no version field.
- `scripts/omt/skill_result.py` has `from_preflight/from_doctor/from_stop_when` but no `from_session` — envelope mapping gap.
- `.opencode/skills/omt-*/SKILL.md` grep for `opencode.db|sqlite|session_inspect` empty — clean baseline to pin.
- `tests/harness_meta/omt/test_omt_session_plugin_args.py` pins OP_ARGS parity — version addition must not break this pin (additive only).

## Constraints

- Read-only preserved: `mode=ro` URI, never `immutable=1` on live DB, one deferred tx per snapshot (adapter doc) — surface `read_only:true` in versioned errors, prove write fails in goldens.
- No secret skill-side SQLite path: skill text must never hardcode `~/.local/.../opencode.db`; DB path comes only via explicit `omt_session{db}` arg from OMT authority (D1/D4, StateScope R3).
- Versioned + envelope-compatible: every `dispatch` return carries `version:1` (int, matches bundle/manifest); failures carry UPPER_SNAKE `code` (mirrors closed vocabulary), `remediation`, `evidence[]`, `retryable`, `read_only`, `source` provenance — mappable via `skill_result.py` without prose parsing.
- Additive only: existing `ok/error/detail` fields stay (goldens + dispatcher tests assert subsets); add `version/code/remediation/...`, never rename.
- stdlib-only, deterministic, no LLM, no network; new files only + service/plugin/adapter additive edits (harness-surface 2nd-edit guard: one edit per file per e2e receipt round).
- Do NOT run bare `net_to_md` (STALE owned elsewhere); WORK budget 3B headroom — trim-while-adding.

## Alternatives

- A) Versioned service envelope + `from_session` adapter + read-only proof + no-secret-path pin + 7 goldens (chosen — minimal, testable, unblocks evidence).
- B) Skill-side SQLite path with hardcoded default (rejected — violates D4, secret path, second state store).
- C) Auto-create `data_migration` / guess schema / silently fall back to default DB (rejected — invents state, writes to live DB risk, violates fail-closed).

## Scope lock

`feature_159` ships: `service.py` versioned returns (`version:1` on all paths, `code` UPPER_SNAKE mirror, `remediation`, `read_only:true`, explicit `missing_db` when `db==""`), `skill_result.py from_session()` adapter (sessions_failed/source_unreadable/schema_unsupported/query_limit_exceeded → `blocked/failed` envelope with `code`), plugin passthrough preserved + version asserted, adapter `DEFAULT_DB_PATH` documented-candidate note (no auto-use), read-only proof, no-secret-path goldens, 7 goldens under `tests/harness_meta/feature_159.session_compat_versioned_error/`. Session reads on live DB stay bounded (`DIRECTORY_CAP`, `limit`, `detail_ref`). `omt-session-evidence` skill itself OUT — deferred to next leg after compat lands.
