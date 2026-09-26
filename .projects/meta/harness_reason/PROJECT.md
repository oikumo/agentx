# PROJECT: harness_reason — Category Theory Reasoning Engine (harness.reason)

> Status: **active** · **v0.1 (2026-09-26)** — created by `project.py new --slug harness_reason` from `.sandbox/category_theory_meta_harness.md` (specification, 2026-09-26, 1197 lines). Iterate freely (non-gated); spawn features with `new_feature.py "<name>" --type <tt> --project harness_reason`; log sessions in CURRENT_STATE.md (newest on top).

---

## New Session Quick Start

> One line: typed interaction language + small categorical kernel + harness adapters as `harness.reason` — agent writes a program, interpreter checks it, kernel evaluates pure fragments, router calls existing adapters in `W` order, every run returns a digest-bound certificate or a named unknown.

**Next:** Stage 0 contract extraction — draft 6–10 versioned generator contracts (inputs/outputs/effects/validator_ref/unknown_if) pointing to authoritative sources + JSON IR for the §2 example and §3 three-row tables, then run probes 1–7 in sandbox. No engine, source, test, policy, net, or toolbox-registration change.

---

## Summary (one line)

**Typed interaction language (§2) evaluated by a small categorical kernel plus harness adapters, exposed as `harness.reason` via toolbox discovery — advisory only, never mints authority.**

---

## Purpose

### What this project is

- The **sole execution home** for the proposal (`.sandbox/category_theory_meta_harness.md`): one product — `schema/model/mapping/query/compute` program + three-stage interpreter (elaborator → kernel evaluator → effect router) + §5 certificate or named unknown.
- Normative core: §2 language (JSON IR first, no new `.omt` grammar), §3 single worked adjunction `Forget ⊣ Realize` on the staleness schema (unit/counit enumerated, concretize returns realizations + distinguishing info), §4 monadic `compute` in `IO_Fail` with one linear `W` wire + `Maybe` three-valued equalizer (`Aligned/Mismatched/Unresolved`), §5 certificate schema (mandatory `structural/premises/execution/goal` + digests + `derivation`, ~2 KB summary or `detail_ref` envelope, never truncation).
- Stage-1 subset is §§11–14 checker: `check` (query + named compute premises) / `explain` (slice by node ID) / `compare` (two programs under named observation contract) / `plan` (bounded hole-fill, withheld until stage 2).
- Integration path per §7 (proposal, no files created): Tier 0 prompt-side renderer (`reason_table.ts`, no `omt_` prefix, zero harness cost) → Tier 1 advisory pilot (`reason_check.ts`, closed `check|explain|compare|concretize` enum, thin proxy to `uv run scripts/reason/`, one `allow` line outside `harnessc` perm blocks) → Tier 2 full `omt_reason.ts` (promotion-only after §15 gates). Single-core rule: one Python SSOT owns semantics; every surface is a thin caller.
- Staged rollout (§13.3): 0 contract extraction → 1 advisory check+explain → 2 composition+replacement (reuse across ≥2 contexts, reject unsafe substitution with witness) → 3 paired agent experiment (harness vs enhanced typed planner vs kernel, same catalog/tasks/budgets/oracle) → 4 conditional promotion via existing toolbox review.
- Feasibility verdict (§15): **conditional-go stages 0–1, gated go stage 2, no-go broad platform** (no e-graph/prover/SMT/new `.omt` parser/Julia runtime in pilot).

### What this project is **not**

- NOT an engine implementation — the idea doc authorizes **research + design only**; stage 0 begins in sandbox with contracts/IR/probes, no `src/`/`scripts/reason/`/`toolbox/` creation by this document.
- NOT a new authority: programs advise via `harness.reason`; grants, leases, `Done`, phase/TDD decisions stay with existing enforcement. `compute` results are never read as grants; `fail` never coerced to `ok`; `unknown` never guessed.
- NOT a general prover/ontology: no toposes, higher categories, arbitrary rewrites, universal thought ontology; no natural-language `requires` as executable proof — every predicate resolves to a registered validator or returns `unknown`.
- NOT a schema-budget expansion: always-loaded `omt_*` surface stays closed (39 B headroom); pilot lives behind toolbox on-demand discovery with ~2 KB default summaries.
- NOT touching protected paths (`.env*`, `uv.lock`, `README.md`, `LICENSE` without `omt_skip{scope:all}`), bare `python/pip/pytest`, or `git push/pull/fetch/remote/clone`.

---

## Scope & success criteria

**Scope:** Stage 0 (6–10 contracts + JSON IR + probes 1–7 in sandbox) → Stage 1 (pure checker + immutable context import + premise slices; agree with existing authority on all 12 §14.1 cases) → Stage 2 (parameterized fragments + replayable rewrite certs for small law set; reuse across two task contexts + unsafe-substitution rejection) → Stage 3 paired measurement → Stage 4 promotion only on repeated utility + green budgets + user selection.

**Success:**

1. S0: every contract points to its authoritative source; unsupported behavior stays `unknown`; IR rejects §14.1 negatives as ill-typed or premise-failed; probes 1–7 pass in sandbox (probe 1 = cite both NEXT contracts + refuse comparison, never a bug diagnosis).
2. S1: mismatch (§11.6) and three-row (§3) examples replay from digests alone; truncation fails validation; `snapshot_inconsistent` returned on epoch mix, never a mixed-epoch plan; advisory boundary demonstrable (no net/ledger writes, no token movement).
3. S2: `verify_candidate` expands across two artifacts with fresh obligations per instantiation (refuses `h2`-with-`h1` evidence); `test;edit` rejected under completion-relevant contract with `(h1,h0)` witness while permitted under files-only contract.
4. S3: paired experiment reports per-case outcomes + variability (correctness, missed staleness/unsafe substitutions, interventions, calls/latency/tokens/runtime, maintenance cost, avoided steps); 15% median cost-reduction is a proposed decision threshold, not a prediction. If the enhanced typed planner matches at lower cost, keep the planner.
5. Kill/shrink on any §15.1 kill criterion, validator gaps outrunning predicates, or threshold miss — shrink to Tier 0 rather than promoting to Tier 2.

**Out of scope:** broad platform (general theories/rewrites/backends/large formalization); net compilation before projection preservation is proven; permission/applicability replay from cache (always re-import); confidence scores; `plan` in Tier 1 enum before stage-2 gates.

---

## Status

- [x] v0.1 (2026-09-26): created (`project.py new --slug harness_reason`, state: draft) from category-theory idea doc; this PROJECT.md drafted (non-gated iterate).
- [x] Stage 0 contract extraction (6–10 ops + JSON IR + §3 tables + probes 1–7 in sandbox) — Done via feature_122 (7/7 digest `6e355d71`).
- [x] First linked feature (header flips draft → active mechanically) — Done via feature_122 link.
- [x] Stage 1 checker (12/12 §14.1 agreement) — Done via feature_123.
- [x] Stage 2 composition (two-context reuse + U1–U5 witnesses) — Done via feature_124.
- [x] Stage 3 paired experiment (135-row report + threshold rule) — Done via feature_125; gate review conditional-go fixtures, hold promotion.
- [x] Held-out real tasks — Done via feature_126 (8/8).
- [x] Tier 0 renderer (optional first, zero harness cost — readable UC8/probe output) — Done via feature_127 (22/22).
- [x] Tier 1 pilot tool (only after S0–S1 gates; `plan` withheld to stage 2) — Done via feature_128 (13/13 + 14/14).
- [ ] Tier 2 promotion (only after §15 gates + toolbox review) — HOLD per 2026-09-26 gate review; no promotion on synthetic costs.

---

## Decisions log (locked — do not re-litigate without new evidence)

- **D1 — One product (`harness.reason` language + kernel + adapters), stage-1 checker subset:** Parts A/C take precedence over Part B on conflict. Rationale: proposal Product decision + §16 recommendation.
- **D2 — Advisory only; existing enforcement stays the execution boundary:** kernel advises, harness authorizes. Rationale: §§2/7/11 (W sequences, never locks; certs never mint grants/leases/Done).
- **D3 — JSON IR first; no new `.omt` grammar, prover, e-graph/SMT, `uv.lock` change, or second runtime in research:** representation bake-off (purpose-built vs DisCoPy prototype for diagrams only) before committing. Rationale: §§7/13.2/15.1.
- **D4 — Single MVP adjunction (`Forget ⊣ Realize` on staleness schema) + `W`-linear `compute` + `Maybe` equalizer are the normative core:** any other "abstraction" without unit/counit is documentation, not engine behavior. Rationale: §§3–4 + §15.3.
- **D5 — Tiers in order (0 → 1 → 2-promotion-only) with kill line:** if Tier 1 cannot carry probes 1–7 without widening the enum, adding `src/` imports, or touching net/ledger writes, shrink to Tier 0. Rationale: §7 + §15.9.
- **D6 — Fair comparison decides:** three arms share catalog/adapters/fragments/tasks/budgets/oracle; keep the enhanced typed planner if it matches at lower complexity. Rationale: §§14.2/15.6.

---

## References

- Proposal: `.sandbox/category_theory_meta_harness.md` (1197 lines, 2026-09-26; Part A §§1–7 product, Part B §§8–12 background/analysis, Part C §§13–16 delivery; §§3–5 normative core; §7 plugin tiers; §§14–15 evaluation + feasibility gates).
- Workflow: `.workflows/meta_harness/loops/meta_harness_evolution.md` (research portion followed by the proposal; source-code investigation prohibited).
- Capability baseline: `.meta/META_HARNESS.omt` + features 075/085 (receipt/dependency authority to preserve), feature 042 (net synthesis — not new work), toolbox baseline §8/§10.3 (6 tools, 39 B headroom → on-demand discovery).
- Sibling convention: `.projects/meta/meta_harness_12/PROJECT.md` (Tier/UTC pattern this home mirrors).
