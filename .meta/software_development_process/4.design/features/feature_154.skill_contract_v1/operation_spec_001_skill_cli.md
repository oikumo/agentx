# Operation Spec — skill contract v1 (feature_154)

> Companion to `design_001_contract_validator.md`. Exact operations, signatures,
> stdout/exit contracts. All stdout strings are pinned surface.

## `scripts/omt/skill.py` (stdlib only, no imports from repo)

### CLI

```text
uv run scripts/omt/skill.py doctor <skill-id>
uv run scripts/omt/skill.py new <skill-id>
uv run scripts/omt/skill.py test <skill-id>
uv run scripts/omt/skill.py list
```

- `doctor <id>` exit 0 + `✅ <id> contract OK` when valid; exit 2 + machine lines
  `ERR <check>: <detail>` per failure (checks: frontmatter, name==dir, description>=20,
  contract JSON parses, schema valid, requires[] known ops, result_schema known).
- `new <id>` exit 0 creates `.opencode/skills/<id>/{SKILL.md,skill.contract.json,references/.gitkeep}`;
  exit 2 if dir exists (`ERR exists: .opencode/skills/<id>`).
- `test <id>` exit 0 runs validator + goldens for that skill (no LLM, deterministic).
- `list` exit 0 prints `<id> <contract-ok|contract-missing|contract-invalid>` per line, sorted.

```python
def main(argv: list[str] | None = None) -> int
def cmd_doctor(skill_id: str) -> int
def cmd_new(skill_id: str) -> int
def cmd_test(skill_id: str) -> int
def cmd_list() -> int
def load_frontmatter(path: Path) -> dict
def validate_contract(contract: dict, skill_dir_name: str) -> list[str]
```

- `validate_contract` returns [] when valid, else `ERR ...` strings (pure, no I/O).
- Known `requires[]` ops allowlist (static, mirrors DSL catalog):
  `omt_status.preflight`, `omt_q.state`, `omt_q.plan`, `omt_nav.nav`,
  `omt_kb_nav.nav`, `omt_phase.declare`, `omt_tdd.testlist`, `omt_net.probe`.
- Known `result_schema`: `omt-skill-result/v1` only in v1.

## `.meta/templates/skill.contract.schema.json` (draft-07)

- `$schema`, `title: skill.contract/v1`, `type: object`,
  `required: [schema_version,id,version,mode,inputs,requires,allowed_effects,forbidden_effects,state_owner,result_schema,stop_when]`,
  `properties.schema_version.const: "1"`, `mode.const: procedural`,
  `state_owner.const: external`, `result_schema.const: omt-skill-result/v1`,
  `id.pattern: ^[a-z0-9-]+$`, `version.pattern: ^0\.[0-9]+\.[0-9]+$`,
  `inputs.minItems:1`, `stop_when.minItems:2`,
  `forbidden_effects.contains weaken_gate|forge_receipt|expand_scope_without_authority`
  (enforced in validator, not pure JSON-Schema contains — validator checks superset),
  `additionalProperties: false`.

## `.meta/templates/skill.result.schema.json` (draft-07, shape only)

- `required: [schemaVersion,ok,outcome,code,evidence,retryable]`,
  `outcome.enum: [succeeded,blocked,not_applicable,inconclusive,failed]`,
  `ok.type: boolean` (validator does not cross-check ok vs outcome — runtime does in feature_155).

## Skill skeleton `.opencode/skills/omt-recover-block/`

- `SKILL.md` frontmatter `name: omt-recover-block`, `description: >=20 chars`,
  body sections `Use when / Do not use when / Procedure(6 steps) / Stop`.
- `skill.contract.json`: id==`omt-recover-block`, requires includes
  `omt_status.preflight`, allowed includes `read_harness_state`,
  `invoke_existing_authorized_omt_tool`, `retry_original_operation`,
  forbidden includes the three canonical, stop_when>=2.
