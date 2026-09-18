# 02 — Boundary model: principles, ownership, gate matrix

## 1. Boundary principles

1. **P1 — Different consumers, different correctness.** Product is correct when *users* can chat/RAG/agent/model-switch. Harness is correct when *the agent* cannot skip Analysis→Design→Programming→Testing without a logged override. Never judge one by the other's bar.
2. **P2 — Product never imports harness.** `src/agentx/**` and `tools/petri-net-studio/**` MUST NOT import from `scripts/omt/**`, `.opencode/**`, `.meta/**`. The harness *observes* product (MVC lint, TDD gates); product is *unaware* of the harness.
3. **P3 — Contracts, not imports, across implementations.** The ONLY legal product-internal coupling is `shared/petri-net/` (spec + schema + canonical examples). Python model ↔ TS studio stay byte-compatible through that dir, never through code imports (already the rule in `shared/META.md` — keep it).
4. **P4 — Harness is generated from one source.** `.meta/META_HARNESS.omt` → `AGENTS.md` + `opencode.jsonc` blocks + IR + nav index via `harnessc build`. Anything else claiming to be "the rule" is a comment, not authority.
5. **P5 — Workflows sit ABOVE the harness.** `.workflows/*.md` are human-authored markdown recipes. Each declares `Follow omt methodology` vs `Do not follow…` in `# Rules` line 1. The catalog never becomes a runtime engine without an explicit decision.
6. **P6 — Plans are namespaced, tasks are pooled (for now).** `.projects/` and `.sandbox/` hold both systems' plans; separation is by *directory namespace*, not by repo split. `WORK.md` remains the single pool until volume forces a split view.
7. **P7 — State is local, plans are committed.** `.meta/.omt/*` (ledger, thoughts, receipt, snapshots) is gitignored session state. Everything needed to resume *a project* lives in committed `.projects/**/CURRENT_STATE.md` + `.sandbox/` artifacts.

## 2. Ownership contract (target)

| Domain | Owner paths | May edit | MUST NOT touch |
|---|---|---|---|
| PRODUCT | `src/agentx/**`, `tools/petri-net-studio/**`, `tests/{controllers,model,views,unit}/`, `tests/features/feature_{007,010,013,015,018,019,024,025,027,029}*`, `pyproject.toml [project]` runtime deps | product features, console UX, providers, RAG, agents | harness plugins, engines, DSL, gates |
| CONTRACT | `shared/petri-net/**` | spec, schema, canonical examples/vectors only (no code) | implementations |
| HARNESS-DECL | `.meta/META_HARNESS.omt` | rules, gates, budgets, tool schemas, paths | generated projections (hand-edit = drift) |
| HARNESS-RT | `.opencode/plugins/**`, `.opencode/lib/**` | TS gates/tools (Bun) | product source |
| HARNESS-ENG | `scripts/omt/**` | Python engines (uv) | product source |
| HARNESS-STORE | `.meta/software_development_process/**`, `.meta/templates/**`, `.meta/.omt/*` | methodology artifacts + local state | product docs |
| HARNESS-DOC | `.meta/doc/{harness,opencode_plugins,tdd}/` | harness design | product arch |
| PRODUCT-DOC | `.meta/doc/{omt++,petri_nets}/`, `README.md` product chapters | product arch | harness rules |
| OPS | `.workflows/**` | markdown recipes + subject `META.md` | runtime behavior |
| PLAN | `.projects/meta/<ns>_*`, `.sandbox/*`, `sandbox/*` (see §4) | design logs, pauses, proposals | live code |
| POOL | `WORK.md`, `WORK_ARCHIVE.md` | task rows, project sync table | code |

## 3. Gate-applicability matrix (target — narrows today's blanket gates)

| Gate | `src/agentx/**`, `tools/**` (product) | `scripts/omt/**`, `.opencode/**` (harness surface) | `.meta/**`, `.workflows/**`, `.projects/**` (docs/plans) |
|---|---|---|---|
| `g.phase` (declare before edit) | YES — product work declares `bug_fix/minor_feature/major_feature…` | YES — harness work declares `refactor/minor_feature…` + e2e receipt cycle for 2nd edit | advisory (workflows declare stance line 1) |
| `g.tests` canary + TDD two-hats | YES for product `major_feature/new_screen` (RED `tests/` only, GREEN `src/` only) | YES — harness-surface 2nd-edit receipt + canary for `tests/` | no |
| `g.mvc` (block NEW hard violations) | YES (Python product) | no (TS plugins + engines exempt; own lints) | no |
| `g.kb` (AKB consult) | YES for `src/` edits | no | no |
| `g.think` (TA consult, NOT skip-bypassable) | YES where `TA:` present | YES where `TA:` present | no |
| `g.nav` (nav before doc grep) | YES for `.meta/`, `AGENTS.md`, `WORK.md` searches | same | same |
| `g.receipt` (2nd-edit guard) | no | YES (harness surface only) | no |
| `g.net` (concurrency permission) | engages only when `net_marking(active>1)`; solo → skip | same | no |
| `g.protect` (`.env*` hard; README/uv.lock/LICENSE via `scope:all`) | YES (repo-wide) | YES | YES |

## 4. Toolchain / test / doc / state rules

- **Toolchain:** product Python via `uv` only (`uv run agentx`, `uv run pytest`); studio via `bun`/`npm` in `tools/petri-net-studio/`; harness compile via `uv run scripts/omt/harnessc.py check|build`; never bare `python/pip/pytest` (deny-pinned).
- **Tests:** `tests/` splits by path — product tests assert *user behavior*; `tests/scripts/omt/` + harness feature dirs assert *gate/engine behavior*. One `pytest` run covers both; `-m "not opencode_live"` excludes the 17 live binary sessions. No harness test files inside `src/` (see violations).
- **Docs:** product truth = `.meta/doc/omt++/*` + README product chapters; harness truth = `.omt` + `AGENTS.md` (projection) + `.meta/doc/{harness,opencode_plugins,tdd}/`. Cross-links allowed, duplication not.
- **State:** `.meta/.omt/*` stays gitignored local state (except the 2 verified projections). Resume truth = `.projects/**/CURRENT_STATE.md`. Scratch truth = ONE root (see proposal §4).
- **Versioning:** product versions (`pyproject.toml 0.2.0`) independently of harness record count / `net_rev`. A harness change never bumps product version and vice versa.
