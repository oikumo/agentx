# Improvement 006 — META_VISION wiring

Problem: `META_VISION.md` (repo root, untracked, 1 dense paragraph) is invisible to the harness workspace workflow. `harnessc check` fails: `'META_VISION.md' not in @var root_allowlist`. No `@doc` record, no AGENTS.md pointer, no `.workflows/meta_harness` reference. Agents never load the vision.

Current vision content (preserved, to be restructured):
- gates-not-willpower, Analysis→Design→Programming→Testing, auditable artifacts
- single-source DSL `.meta/META_HARNESS.omt` → compiler projections + drift-tests
- token budgets, IR-ordered gate chain, Petri-net concurrency fail-open
- Tier-2 self-evolution via `omt_session` on real sessions
- membrane: runtime-orthogonal/dev-coupled, ledger narrow waist, newcomer guard

## Option A — DSL pointer + structured vision (Recommended)
- Rewrite `META_VISION.md`: keep all claims, split into sections (Purpose / Single-source / Gates+Budgets / Concurrency / Self-evolution / Membrane / Newcomer), add `> SOURCE` + `> WIRED` header (where it is referenced).
- Edit ONLY `.meta/META_HARNESS.omt` in ONE batch: add `META_VISION.md` to `@var root_allowlist`, add `@doc vision tags="VISION"` (1-line vision + pointer), extend `@doc runtime` payload with `Vision: META_VISION.md (@doc vision).`
- `uv run scripts/omt/harnessc.py build` → AGENTS.md RUNTIME line picks up vision pointer automatically (no `harnessc.py` code change).
- Edit `.workflows/meta_harness/META.md` scope section (+1 line pointing to vision).
- Cost: 1× .omt edit (clean-file first edit, no receipt needed), 1× build. Stays in docs/task_type, no TDD, no e2e.

## Option B — Full AGENTS.md Vision section
- Everything in A, PLUS edit `scripts/omt/harnessc.py:render_agents()` to emit dedicated `- **Vision (META_VISION.md):** ...` line + add `vision` to required-docs check.
- Cost: harness-surface code edit (think-gate consult on `harnessc.py` + receipt-guard second-edit risk + e2e run). Heavier, touches code-gen. Only worth it if vision must be top-level in every turn's system prompt.

## Option C — Docs-only, no DSL change
- Rewrite `META_VISION.md` + reference from `.workflows/meta_harness/META.md` only.
- Still needs `@var root_allowlist` fix or `harnessc check` keeps failing → so not really "no DSL change". Minimal but leaves AGENTS.md blind to vision.

Approval gate: pick A / B / C. Execution follows `loops/meta_harness_evolution.md` step 5-6 (update canonical `.omt` → build, never edit `AGENTS.md` directly).
