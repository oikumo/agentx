# META_VISION.md — the META HARNESS vision (canonical)

> SOURCE: this file is the human-readable vision. WIRED: `@doc vision` in `.meta/META_HARNESS.omt` (nav-indexed) + `Vision:` pointer in `@doc runtime` → `AGENTS.md` RUNTIME line + scope pointer in `.workflows/meta_harness/META.md`. Edit this file freely; to change the wiring edit the `.omt` and rebuild (`uv run scripts/omt/harnessc.py build`), never the projections.

## 1. Purpose — gates, not willpower

Prove a coding agent can be mechanically constrained to follow rigorous Analysis → Design → Programming → Testing with visible, auditable artifacts at every step.

## 2. Single source — declare once, project everywhere

Declared once as DSL (`.meta/META_HARNESS.omt`), projected by compiler into rules, permissions, IR and indexes, with drift-tests. See `@doc comp.hdl`, `AGENTS.md` (GENERATED), `.workflows/`, `.projects/`.

## 3. Budgets + gate chain + concurrency

Every token-costing surface is budgeted; every edit passes an IR-ordered gate chain (nav, protect, receipt, tests-canary, net, phase, think, knowledge-base before; architecture and TDD after). Concurrent work is Petri-net-gated and degrades fail-open.

## 4. Self-evolution only on evidence

The harness evolves itself only on evidence via Tier-2 self-inspection (`omt_session` over real sessions: usage/cost hotspots, traces, failure witnesses, gated labeled experiments with provenance-bound export).

## 5. Membrane — runtime-orthogonal, dev-coupled

Kept runtime-orthogonal yet dev-coupled from the AgentX product by a falsifiable membrane: product builds, tests and ships with the wrapper absent and vice versa; they talk only through an append-only ledger narrow waist plus named read-only projections and one declared comment-line inversion, verified by proof-carrying ephemeral-overlay certificates.

## 6. Newcomer guard — zero ceremony by default

`uv sync && uv run agentx` needs zero harness knowledge. Strict in CI, advisory locally, so product developers pay zero ceremony for process rigor.
