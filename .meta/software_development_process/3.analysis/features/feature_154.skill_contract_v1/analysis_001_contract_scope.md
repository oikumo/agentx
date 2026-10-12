# Analysis 001 — skill contract v1

Feature: feature_154.skill_contract_v1 · Phase: Analysis · Date: 2026-10-12

## Problem

`SKILL.md` alone is linguistic (description → load → interpret). Promises like
"clear only the legitimate prerequisite, retry once, never weaken a gate" live
in prose and are not testable. Policy copied into skill text drifts (test-count
precedent: README 2085+283 vs pyproject 2103).

## Evidence

- Existing skill: `.agents/skills/mermaid-in-markdown/SKILL.md` (name+description
  frontmatter, body procedural, no contract, no validator).
- OpenCode discovers `.opencode/skills/*/SKILL.md` + `.agents/skills/*/SKILL.md`,
  `allow/ask/deny` on skill-load only — effects still gated by OMT/tools.
- Analisys §Interfaces proposes `skill.contract.json` + `omt-skill-result/v1`;
  §Testing proposes pyramid (schema→contract→scenario→replay→integration→smoke→experiment).
- Risks: semantic-contract unequal (transport ok + body=reject), `schema_unsupported`
  in `omt_session`, skills-as-instruction-surface.

## Constraints

- Skills stateless-by-default; state owners: invocation/session/feature/project/harness.
- No second state store, no RPC lifecycle, no policy copy (query OMT as authority).
- New files only in this feature (avoid harness-surface 2nd-edit guard):
  `scripts/omt/skill.py`, `scripts/omt/skill_contract.py` (or fold into skill.py),
  schema ` .meta/templates/skill.contract.schema.json`, goldens under
  `tests/harness_meta/skill_contract_meta/`.
- Validator deterministic, no LLM, no network.

## Alternatives considered

- A) JSON contract + JSON-schema + `skill.py doctor|new|test|list` (chosen — testable, minimal).
- B) Markdown-frontmatter-only contract (rejected — weak typing, hard to version).
- C) Full skill runtime with init/invoke/close (rejected — overengineering, second harness).

## Scope lock

Contract fields: schema_version, id, version, mode=procedural, inputs[],
requires[], allowed_effects[], forbidden_effects[], state_owner=external,
result_schema=omt-skill-result/v1, stop_when[]. Plus `skill-result` envelope
(shape only here; full OmtResult envelope is feature_155).
`doctor` checks: discoverability, name==dir, frontmatter, contract valid,
OMT ops exist, no unknown top-level fields, tests present.
