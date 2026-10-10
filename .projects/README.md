# .projects/ — Homes separation (hand-written convention, not GENERATED)

> Rule: `.projects/meta/` = meta-harness only. `.projects/agentx/` = AgentX product only.
> `project.py` still operates on `.projects/meta/` by default (single-root).
> For `agentx` use `OMT_PROJECTS_ROOT=.projects/agentx` — but do NOT run `sync`
> with override yet (it would rewrite WORK.md `## Projects` to one home only).
> Multi-root `sync` is deferred to `harness_wrapper_split` T6.

## Naming

- Harness-only: suffix `_meta` for new projects (legacy `meta_*` prefix accepted as-is, no renames).
  Examples: `net_gate_meta`, `tdd_hats_meta`. Legacy: `meta_harness_14`, `meta_harness_15`.
- Product-only: no `meta` affix. Examples: `rag_v2`, `agentx_concurrent_development`, `petri_net_studio`.
- Bridge (touches both): put under the owner side + tag `bridge:` in PROJECT.md Decisions log. No third home.

## What lives where

- `.projects/meta/{PROJECT.md,CURRENT_STATE.md}` — harness process, gates, net, tdd, session, think, kb, workflows-harness.
- `.projects/agentx/{PROJECT.md,CURRENT_STATE.md}` — product domain: agent, model, ui, rag, petri-net product use.
- `.projects/archive/` — closed homes from either side (existing mechanic, unchanged).

## Testing separation (target, pending canary — no moves yet)

- Today mixed: `tests/{controllers,views,model,unit}` (product) beside
  `tests/scripts/{omt,session_inspect,toolbox,reason}` (71+ harness files) and
  `tests/features/feature_*` (mixed).
- Target: `tests/agentx/**` (product) vs `tests/harness_meta/**` (harness, `_meta` suffix on new files).
  Legacy files grandfathered with a mapping table in `harness_wrapper_split` T1 audit.
- Runs: `uv run pytest tests/agentx` (product lane, no harness) vs
  `uv run pytest tests/harness_meta` (wrapper lane, contract-pinned).
- Gate: any move under `tests/` needs canary approval (`omt_skip{scope:"tests"}`) —
  this README proposes the layout, it does not move files.
