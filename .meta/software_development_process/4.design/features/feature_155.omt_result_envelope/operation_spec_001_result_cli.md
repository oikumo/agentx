# Operation Spec — OmtResult envelope v1 (feature_155)

> Companion to `design_001_envelope.md`. Exact operations, signatures, stdout/exit contracts.
> All stdout strings are pinned surface.

## `scripts/omt/skill_result.py` (stdlib only, no imports from repo)

### CLI

```text
uv run scripts/omt/skill_result.py validate <json-file>
uv run scripts/omt/skill_result.py make-succeeded --code OK --evidence e1,e2
uv run scripts/omt/skill_result.py make-blocked --code RECEIPT_REQUIRED --gate omt_complete --code2 RECEIPT_REQUIRED --message "..." --requires-approval
```

- `validate <file>` exit 0 + `✅ omt-skill-result/v1 OK` when valid; exit 2 + machine lines
  `ERR <check>: <detail>` per failure (checks: ok-boolean, outcome-enum, code-UPPER_SNAKE>=1,
  ok⇔succeeded, blocked→blocker, blocker-fields, evidence-array, retryable-boolean,
  no-unknown-top-fields).
- `make-*` prints JSON envelope to stdout, exit 0; exit 2 on missing required flag.

```python
def main(argv: list[str] | None = None) -> int
def make_succeeded(code: str, evidence: list[str], data=None, stateRevision: str | None = None) -> dict
def make_blocked(code: str, blocker: dict, evidence: list[str], retryable: bool) -> dict
def make_not_applicable(code: str, evidence: list[str]) -> dict
def make_inconclusive(code: str, evidence: list[str]) -> dict
def make_failed(code: str, message: str, evidence: list[str]) -> dict
def validate_envelope(obj: dict) -> list[str]
def parse_envelope(text: str) -> tuple[dict | None, list[str]]
def from_preflight(preflight: dict) -> dict
def from_doctor(rc: int, skill_id: str) -> dict
```

- `validate_envelope` returns [] when valid, else `ERR ...` strings (pure, no I/O).
- `CODE_RE = ^[A-Z][A-Z0-9_]+$`; `OUTCOMES = {succeeded,blocked,not_applicable,inconclusive,failed}`.
- `from_preflight`: preflight `{"ok":true}` → succeeded/OK; `{"ok":false, ...}` → blocked with
  `blocker{gate,code,message,remediation,requiresApproval}` passthrough.
- `from_doctor`: rc 0 → succeeded/OK; rc!=0 → failed/DOCTOR_FAILED, retryable False.

## `.meta/templates/skill.result.schema.json` (draft-07)

- `$schema`, `title: omt-skill-result/v1`, `type: object`,
  `required: [ok,outcome,code,evidence,retryable]`,
  `properties.ok.type: boolean`, `outcome.enum: [succeeded,blocked,not_applicable,inconclusive,failed]`,
  `code.pattern: ^[A-Z][A-Z0-9_]+$`, `evidence.type: array,minItems:0`,
  `retryable.type: boolean`, `blocker.type: object (required when blocked)`,
  `blocker.required: [gate,code,message,requiresApproval]`,
  `additionalProperties: false` top-level and blocker-level.

## `.meta/templates/skill.result.types.ts` (shape doc, not wired)

- `export type OmtOutcome = "succeeded"|"blocked"|"not_applicable"|"inconclusive"|"failed";`
- `export interface OmtBlocker { gate:string; code:string; message:string; remediation?:string; requiresApproval:boolean }`
- `export interface OmtResult<T=unknown> { ok:boolean; outcome:OmtOutcome; code:string; data?:T; blocker?:OmtBlocker; evidence:string[]; retryable:boolean; stateRevision?:string }`

## `scripts/omt/skill.py` surgical edit (1 edit this round)

- `cmd_doctor`: after contract valid, check `REPO/.meta/templates/skill.result.schema.json` exists;
  missing → `ERR result_schema_file: missing skill.result.schema.json`, exit 2.
- No change to `KNOWN_RESULT_SCHEMAS`, no change to `validate_contract` signature.
