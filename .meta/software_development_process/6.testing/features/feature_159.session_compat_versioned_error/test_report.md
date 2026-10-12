# Test Report — feature_159.session_compat_versioned_error

Date: 2026-10-12 · major_feature (TDD required, batch single-cycle).

## Changes

- `scripts/session_inspect/service.py` versioned envelope (`version:1`, UPPER_SNAKE `code`, remediation, `read_only:true`).
- `scripts/omt/skill_result.py from_session` adapter to envelope v1.
- `.opencode/plugins/omt_session.ts` versioned own refusals + passthrough comment.
- `tests/.../test_session_compat_meta.py` — 7 goldens.

## TDD (batch-of-7 single-cycle)

- Testlist 7: missing-db, source_unreadable, schema_unsupported (live), over-budget (live 1758>20), read-only proof, no-secret-path, envelope mapping.
- RED at `test_missing_db_versioned` (None==1, sessions_failed bare), GREEN same node after service+skill_result patch, REFACTOR plugin comment green. `tdd done ✅` (17 baseline tolerated).
- `omt_skip{scope:tests}` for RED batch.

## Suites

| Gate | Result |
|---|---|
| `pytest feature_159 -q` | 7 passed |
| `dispatcher/adapter/schema/plugin-args` | 13 passed 1 skipped, no regression |
| `doctor` x3 + `list` | ✅ recover/resume/verify OK; 3 pilots |
| `skill_result.validate_envelope` on mapped | clean, ok-succeeded invariant |
| `split_proof_meta` | CI-owned, not re-run in goldens (additive) |

## Notes

- Read-only preserved (`mode=ro`, no immutable=1); no skill-side DB path (grep pin).
- WORK trim-while-adding to hold 11264 (pause-line discipline).
- Next: `Testing → Done` → commit `159` → Phase3 doctor hardening → Phase4 validation.
