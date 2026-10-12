# Design 001 — skill.contract.json v1 + validator + scaffolder

Feature: feature_154.skill_contract_v1 · Date: 2026-10-12
Supersedes: analysis_001_contract_scope.md (scope locked there).

## Artifacts (new files only)

1. `.meta/templates/skill.contract.schema.json` — JSON-Schema draft-07 for contract.
   Required: schema_version="1", id (^[a-z0-9-]+$, == skill dir name), version (semver),
   mode="procedural", inputs[]>=1, requires[] (omt_* op names), allowed_effects[],
   forbidden_effects[] (must include weaken_gate|forge_receipt|expand_scope_without_authority
   or equivalents), state_owner="external", result_schema="omt-skill-result/v1",
   stop_when[]>=2. Forbid unknown top-level fields (`additionalProperties:false`).
2. `scripts/omt/skill.py` — CLI `doctor|new|test|list` (stdlib only):
   - `doctor <skill>`: load SKILL.md frontmatter (name==dir, description>=20 chars),
     load sibling `skill.contract.json`, validate vs schema, check requires[] ops exist
     (static allowlist from `.meta/META_HARNESS.omt` tool catalog, no imports),
     check result_schema file exists, report machine-readable errors (exit!=0).
   - `new <id>`: scaffold `.opencode/skills/<id>/{SKILL.md,skill.contract.json,references/}`.
   - `test <id>`: run contract goldens (calls validator, no LLM).
   - `list`: enumerate skills with contract status.
3. `.opencode/skills/omt-recover-block/{SKILL.md,skill.contract.json}` — first
   contracted pilot skeleton (manual-only `opencode/autoinvoke:false`), procedure
   per analisys §pattern (preserve op → preflight → smallest clearance → retry≤1 → result).
4. `tests/harness_meta/skill_contract_meta/test_skill_contract_meta.py` — goldens:
   valid minimal, unknown-field reject, name-mismatch reject, forbidden-effects-missing
   reject, empty stop_when reject, doctor on scaffolded skill green.
5. `omt-skill-result/v1` shape doc: `.meta/templates/skill.result.schema.json`
   (ok, outcome{succeeded|blocked|not_applicable|inconclusive|failed}, code, data?,
   blocker?{gate,code,message,remediation?,requiresApproval}, evidence[], retryable).

## Non-goals

- No OmtResult TS envelope (feature_155), no session compat, no autoinvoke logic,
  no edits to existing harness files (new-only → no receipt 2nd-edit triggered).

## Acceptance

- `uv run scripts/omt/skill.py doctor omt-recover-block` green, deterministic.
- Goldens green; `split_proof_meta` still 39/39; full harness suite no-new-failures.
- `omt_complete advance Design→Programming→Testing→Done` with TDD testlist (validator
  behaviors) — RED in tests/ only, GREEN in scripts/ only.

## Rollout

- Land contract + doctor + recover-block skeleton + goldens in one commit.
- Envelope (feature_155) consumes result_schema; pilots (Phase2) consume contracts.
