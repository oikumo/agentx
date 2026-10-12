# Implementation 001 — skill.contract v1 + validator (feature_154)

## Files (new-files-only, no harness-surface 2nd-edit)

- `scripts/omt/skill.py` — CLI `doctor|new|test|list` (stdlib only). `validate_contract()` pure (returns [] or `ERR ...` lines); `load_frontmatter()` minimal YAML-frontmatter parse; `find_skill_dir()` searches `.opencode/skills` + `.agents/skills`; known ops allowlist static (mirrors DSL catalog), result_schema `omt-skill-result/v1` only.
- `.opencode/skills/omt-recover-block/SKILL.md` — frontmatter `name==dir`, `description>=20`, `autoinvoke:false`, sections Use when / Do not use when / Procedure(6) / Stop.
- `.opencode/skills/omt-recover-block/skill.contract.json` — id==dir, requires `omt_status.preflight`, allowed 3, forbidden 3 canonical, `state_owner=external`, `stop_when>=2` (4).
- `tests/harness_meta/skill_contract_meta/test_skill_contract_meta.py` — 7 goldens calling `validate_contract` directly + `doctor`/`list` via subprocess (hermetic, no LLM).

## Corrections (goldens drove)

- `forbidden_effects` must be superset of 3 canonical (not just non-empty) — golden `test_rejects_missing_forbidden` pins.
- `stop_when>=2` (not >=1) — golden `test_rejects_empty_stop_when` pins.
- `additionalProperties:false` enforced via unknown-field check — golden `test_rejects_unknown_field` pins.
- Schema files folded into validator (no separate `.meta/templates/*.schema.json`) — keeps Phase1 new-files-only.

## Consequence

- No `src/` edits; no receipts; `doctor` deterministic green; 7/7 green.
