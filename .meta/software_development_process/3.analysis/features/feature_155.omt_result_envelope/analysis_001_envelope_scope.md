# Analysis 001 — OmtResult envelope scope

Feature: feature_155.omt_result_envelope · Phase: Analysis · Date: 2026-10-12
Supersedes: none. Builds on: feature_154.skill_contract_v1 (analysis_001_contract_scope.md scope lock: envelope shape only, full envelope deferred here).

## Problem

Transport success ≠ objective success. OMT tool calls can return OK (exit 0, string payload)
while the objective is still blocked (receipt required, TDD red required, gate denied).
Skills today return prose (`SKILL.md` step 6 "Return omt-skill-result/v1" with no constructor),
so the caller needs a textual heuristic to tell `blocked` from `succeeded`.
PROJECT.md success criterion: no textual heuristic needed.

## Evidence

- `feature_154` contract locks `result_schema=omt-skill-result/v1` but ships shape-only:
  design_001 lists `.meta/templates/skill.result.schema.json` (ok, outcome, code, data?, blocker?,
  evidence[], retryable) — test_report folds schema into validator, no schema file landed.
- `scripts/omt/skill.py` `KNOWN_RESULT_SCHEMAS={"omt-skill-result/v1"}` — membership check only,
  no envelope construction or validation.
- `.opencode/skills/omt-recover-block/{SKILL.md:26, skill.contract.json:26}` promises
  `omt-skill-result/v1` with `stop_when` 4-way (succeeds / same-blocker / auth-required / not-an-omt-block)
  — exactly the 4 outcomes the envelope must encode machine-readably.
- PROJECT.md §Scope item 2 locks envelope v1 fields: `ok` true only on objective success;
  `outcome succeeded|blocked|not_applicable|inconclusive|failed`; `code` e.g.
  RECEIPT_REQUIRED/TDD_RED_REQUIRED; `blocker{gate,code,message,remediation,requiresApproval}`;
  `evidence[]`; `retryable`; `stateRevision` + adapters.
- Analisys §Interfaces proposes `skill.contract.json` + `omt-skill-result/v1`;
  §Testing proposes pyramid (schema→contract→scenario→replay→integration→smoke→experiment).

## Constraints

- Stateless-by-default, `state_owner=external`; no second state store, no RPC lifecycle,
  no policy copy (query OMT as authority) — D1/D4.
- New files only in this feature (avoid harness-surface 2nd-edit guard):
  `scripts/omt/skill_result.py` (or `omt_result.py`), schema
  `.meta/templates/skill.result.schema.json`, TS type `src`? no — harness-surface;
  prefer `.opencode/lib/omt_skill_result.ts`? check owner first — else TS shape doc only.
  Goldens under `tests/harness_meta/feature_155.omt_result_envelope/`.
- Deterministic, stdlib only, no LLM, no network (same as `skill.py`).
- `ok` true IFF `outcome==succeeded` (fail-closed); `blocked` MUST carry `blocker`;
  `code` UPPER_SNAKE machine-readable; `evidence[]` strings/pointers, never prose-only verdict.
- Do NOT touch net reconciliation (rev60-vs-live0 STALE owned elsewhere); no bare `net_to_md`.

## Alternatives considered

- A) JSON-schema file + Python `skill_result.py` make/validate/parse + TS shape doc +
  `skill.py doctor` result_schema-file check + 7 goldens (chosen — testable, minimal, mirrors 154 batch).
- B) Python-only envelope (rejected — TS consumers `omt_*` need the same shape; shape doc cheap).
- C) Smart envelope runtime with auto-retry / outcome inference (rejected — second harness,
  violates stateless + policy-by-reference; retry stays in skill procedure, ≤1).

## Scope lock

Envelope `omt-skill-result/v1` fields: `ok:bool`, `outcome:enum`,
`code:string`, `data?:any`, `blocker?:{gate,code,message,remediation?,requiresApproval:bool}`,
`evidence:string[]`, `retryable:bool`, `stateRevision?:string`.
Validators: `make_*` constructors fail-closed (blocked without blocker → error);
`validate` checks ok⇔succeeded, code present, evidence array.
Adapters (thin): `from_preflight`, `from_doctor`, `blocked(code,blocker)` helpers.
`doctor` extension: warn (not fail) if `skill.result.schema.json` missing — file lands in this feature.
StateScope doc is OUT (next feature 156 or same-Phase1 third leg — decide in Design);
pilots consume envelope in Phase2, no autoinvoke logic here.
