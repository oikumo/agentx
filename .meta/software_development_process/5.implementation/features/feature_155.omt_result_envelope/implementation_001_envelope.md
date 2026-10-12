# Implementation 001 — OmtResult envelope v1 (feature_155)

## Files (new +1 surgical edit)

- `scripts/omt/skill_result.py` — stdlib only. `make_succeeded/blocked/not_applicable/inconclusive/failed` constructors fail-closed; `validate_envelope()` pure (returns [] or `ERR ...`); `parse_envelope()`; adapters `from_preflight/from_doctor/from_stop_when`; CLI `validate <json>` + `make-succeeded/make-blocked` (exit 0 JSON, exit 2 machine errors).
- `.meta/templates/skill.result.schema.json` — draft-07, `required [ok,outcome,code,evidence,retryable]`, `code ^[A-Z][A-Z0-9_]+$`, `ok⇔succeeded` + `blocked→blocker` enforced in validator (not pure schema).
- `.meta/templates/skill.result.types.ts` — shape doc `OmtOutcome/OmtBlocker/OmtResult<T>`, not wired (avoids harness-surface 2nd-edit).
- `tests/harness_meta/feature_155.omt_result_envelope/test_omt_result_meta.py` — 7 goldens (direct `validate_envelope` + `validate` CLI via subprocess + `from_stop_when` mapping), hermetic.
- SURGICAL EDIT `scripts/omt/skill.py` (1 edit): `doctor` fails `ERR result_schema_file` when `skill.result.schema.json` missing; `KNOWN_RESULT_SCHEMAS` unchanged.

## Corrections (goldens drove)

- `ok:true IFF outcome==succeeded` cross-check — golden `test_rejects_ok_outcome_mismatch` pins (transport≠objective).
- `blocked→blocker` required + blocker fields pinned — golden `test_rejects_blocked_without_blocker` pins.
- Unknown-field + missing-code reject — goldens pin `additionalProperties:false` + `code` required on all outcomes.
- `from_stop_when` 4-way mapping pins recover-block `stop_when` → envelope outcomes.

## Consequence

- `skill_result.py validate` deterministic green; `doctor` green post-edit; 7/7 green, 154 7/7 still green; no new suite failures vs 17 baseline.
