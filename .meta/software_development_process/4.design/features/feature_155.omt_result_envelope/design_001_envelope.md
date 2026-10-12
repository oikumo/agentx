# Design 001 — OmtResult envelope v1 + validator + adapters

Feature: feature_155.omt_result_envelope · Date: 2026-10-12
Supersedes: `analysis_001_envelope_scope.md` (scope locked there).

## Artifacts (new files only, +1 surgical edit)

1. `.meta/templates/skill.result.schema.json` — JSON-Schema draft-07 for `omt-skill-result/v1`.
   Required: `ok:boolean`, `outcome:enum[succeeded,blocked,not_applicable,inconclusive,failed]`,
   `code:string UPPER_SNAKE >=1`, `data?:any`, `blocker?:{gate:string,code:string,message:string,
   remediation?:string,requiresApproval:boolean}`, `evidence:string[]`, `retryable:boolean`,
   `stateRevision?:string`. Rules: `additionalProperties:false` top-level;
   `ok==true IFF outcome==succeeded`; `outcome==blocked → blocker required`;
   `code` required on all outcomes (e.g. `OK`, `RECEIPT_REQUIRED`, `TDD_RED_REQUIRED`,
   `GATE_DENIED`, `NOT_APPLICABLE`, `INCONCLUSIVE`, `FAILED`).
2. `scripts/omt/skill_result.py` — stdlib only, no LLM/network. API:
   `make_succeeded(code, data?, evidence, stateRevision?)`,
   `make_blocked(code, blocker, evidence, retryable)`,
   `make_not_applicable/inconclusive/failed(...)`, `validate(obj)->list[str]`,
   `parse(json_str)->(obj,errs)`, adapters `from_preflight(preflight_dict)`,
   `from_doctor(doctor_rc, skill_id)`. CLI: `validate <json-file>` (exit!=0 + machine errors).
   Fail-closed: `blocked` without `blocker` → error; `ok:true` + `outcome!=succeeded` → error.
3. `.meta/templates/skill.result.types.ts` — TS shape doc (non-gated, not wired into
   `.opencode/lib` to avoid harness-surface 2nd-edit; copy-paste source for TS consumers).
   Same fields as schema, `OmtResult<T>` generic over `data`.
4. `tests/harness_meta/feature_155.omt_result_envelope/test_omt_result_meta.py` — 7 goldens:
   minimal-succeeded accept, ok-vs-outcome mismatch reject, blocked-without-blocker reject,
   unknown-field reject, missing-code reject, `validate` CLI green on golden file,
   recover-block stop_when→outcome mapping (4 stop_when → succeeded/blocked/not_applicable/inconclusive).
5. SURGICAL EDIT (1 file, 1 edit this round): `scripts/omt/skill.py` — `doctor` also checks
   `.meta/templates/skill.result.schema.json` exists (fail if missing post-155);
   `KNOWN_RESULT_SCHEMAS` unchanged. Receipt discipline: ONE edit per file per e2e receipt.

## Non-goals

- No `omt_session` compat, no autoinvoke logic, no retry engine (retry stays in skill procedure ≤1),
  no StateScope doc (next feature), no `.opencode/lib` wiring (shape doc only).

## Acceptance

- `uv run scripts/omt/skill_result.py validate <golden-succeeded.json>` green, deterministic.
- `uv run scripts/omt/skill.py doctor omt-recover-block` green after edit.
- Goldens 7 passed; `split_proof_meta` 39/39; full suite no-new-failures.
- `omt_complete Design→Programming→Testing→Done` with TDD batch single-cycle (mirror 154):
  RED in `tests/` only, GREEN in `scripts/` only, same-node rule.

## Rollout

- Land schema + `skill_result.py` + TS shape + goldens + `skill.py` 1-line doctor check in one commit.
- Envelope consumed by Phase2 pilots (`omt-recover-block`, `omt-resume-work` manual-only).
