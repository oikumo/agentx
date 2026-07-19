# Feature 023: Meta Harness Improvement

> **Status:** [ ] Not started
> **Created:** 2026-07-18
> **WORK.md task:** `feature_023.meta_harness_improvement`
> **Origin:** post-shipment evaluation of feature_021+022 —
> `6.testing/features/feature_022.meta_harness_think_anywhere_v2/evaluation_001_post_shipment.md`
> (plan: `3.analysis/.../analysis_005_evaluation_plan.md`). Fixes findings F14–F17 + closes the
> systemic test-integrity gap (R1–R5 of that report).

---

## Summary

The 2026-07-18 full audit of the Think-Anywhere subsystem verified 7 of 8 tier mechanisms
end-to-end — but found that **D1 read-time thought injection is dead code in production**
(F14): `omt_enforcer.ts:1033` reads `output.args.filePath` from the `tool.execute.after`
hook, while the opencode plugin SDK contract (verified across all 9 cached versions,
1.1.12–1.3.13) defines after-hook `output` as `{title, output, metadata}` with `args` on
**`input`** (≥1.2.16). The branch silently no-ops; the feature never fired since shipment.
The runner tests stayed green because their fixtures encode the same wrong payload shape —
the **second instance of the false-confidence pattern** feature_021 cataloged as
T2/DEFECT-A (tests green, behavior absent in real opencode), this time at the hook-payload
boundary instead of the loader boundary. This feature fixes F14, mechanizes the
meta-lesson (contract-pinning at every fabricated test boundary), and clears the minor
hygiene findings.

## Scope (one sentence — what "done" looks like)

D1 read-injection fires in a real opencode session (proven by a serve-mode hook-**effect**
e2e probe, not just unit runners), runner fixture shapes are pinned against the plugin SDK
contract so this defect class fails loudly, the named-export load-guard covers all four
plugins, and the two accidental anchored `TA:` prose comments are reworded — with the
harness set green throughout.

## Task type

`major_feature` (touches the OMT enforcement surface: enforcer plugin + e2e + test infra)
→ **TDD auto-activates** in Programming (omt_testlist → omt_red → omt_green → omt_refactor).

---

## Findings to fix (evidence-backed, from the evaluation)

| # | Class | Finding | Evidence |
|---|-------|---------|----------|
| **F14** | 🔴 correctness | D1 after-hook reads `output.args` (never exists) → read-injection inert in production since 2026-07-18. Fix is one line: `input?.args?.filePath ?? input?.args?.path ?? input?.args?.file`. | `omt_enforcer.ts:1033`; SDK `dist/index.d.ts` contract; live session read of `main_screen.py` showed no injection; evaluation §3 |
| F15 | 🟡 residual risk | `omt_enforcer.ts` named-exports 3 functions (`thinkGateDecision`, `hasConsultedThoughts`, `fileThoughtsIn`) — load-safe *by accident* (throw-safe on garbage input); the DEFECT-A structural guard pins only `omt_think.ts`. | evaluation §9; WORK.md gotcha #1 |
| F16 | 🟢 hygiene | 2 accidental anchored prose `TA:` comments self-gate the plugins and pollute census/digest: `omt_think.ts:88`, `omt_enforcer.ts:1026`. | evaluation §7 |
| F17 | 🟢 hygiene | Each runner-test suite run appends ~45 ephemeral tmp-path records to the real index/ledger (accepted precedent); index is ~87% pollution. | evaluation §7, §9 |
| — | 🔴 systemic | Runner fixtures fabricate opencode payload shapes with **nothing pinning them to the SDK contract** — the generalized DEFECT-A → F14 lesson. | evaluation §6, §10 R5 |

## Proposed improvements (tiered; tiers are independently shippable)

### Tier 1 — F14 correctness fix + live-effect proof
- **T1.1** One-line fix at `omt_enforcer.ts:1033`: read args from `input` (keep
  `output.args` fallbacks harmless or remove; before-hook's `output.args` access is
  correct per the same contract — `output:{args}` there — do **not** touch it).
- **T1.2** Regression test: after-hook runner fixtures corrected to the real contract
  (`input.args`), asserting the injection fires from `input`-carried args.
- **T1.3** Serve-mode hook-**effect** e2e: extend `tests/scripts/omt/test_omt_harness_e2e.py`
  (or the lifecycle e2e) to prove a plugin hook *produces an observable effect* in a real
  `opencode serve` session — e.g. drive a read of a thought-carrying fixture and assert
  the injected block appears. The current e2e proves plugin *load* only; that gap is why
  F14 survived.

### Tier 2 — Contract-pinning (mechanize the meta-lesson)
- **T2.1** Contract-pin test: parse the installed `@opencode-ai/plugin` `index.d.ts` (or a
  vendored copy with an update procedure) and assert the shapes the runners fabricate
  (`tool.execute.before` → `output:{args}`, `tool.execute.after` → `input:{args},
  output:{title,output,metadata}`). Fails loudly on SDK upgrade drift.
- **T2.2** Doctrine: add the rule "runner fixtures must be pinned against the SDK contract"
  to `META_HARNESS.md` / AGENTS.md test-authoring guidance.

### Tier 3 — Named-export guard extension (F15)
- **T3.1** Extend the deterministic `test_no_named_exports_except_default` guard to
  `omt_enforcer.ts`, `omt_nav.ts`, `omt_status.ts` (currently pins `omt_think.ts` only).
- **T3.2** Decide per plugin: un-export (match doctrine) or pin as explicitly-sanctioned
  exports with a load-safety test. The 3 enforcer exports are consumed by the gate runner —
  un-exporting breaks runners, so the sanctioned-export + load-safety pin is the likely
  outcome; the Design phase decides.

### Tier 4 — Hygiene (F16, F17)
- **T4.1** Reword the 2 accidental anchored prose comments so they no longer match
  `THOUGHT_PATTERN` (e.g. drop the `TA:` token); keep their meaning. Bundle with Tier 1
  edits (same two guarded files).
- **T4.2** Runner-pollution strategy: prefer `cwd` isolation so runner-driven tool calls
  never write the real `.meta/.omt/{thoughts,ledger}.jsonl`; if any real-cwd cases must
  stay, document a periodic `omt_think_reindex` hygiene step in the test report.

### Explicit non-goals (deferred)
- R6 `omt_complete` "drop a thought?" nudge (optional adoption aid — revisit after Tier 1
  makes D1 live, since D1 is the adoption surface).
- R7 B2 suggest for the TS family (future value, independent).
- Semantic (truth) verification of thoughts — correctly out of scope per feature_022.

## Use case

### Actor
opencode coding agent (the `build` agent) — next session implements; future sessions
benefit (D1 surfaces thoughts at read time, the actual point of need).

### Goal
Restore the shipped-but-inert D1 mechanism, and convert the DEFECT-A → F14 recurrence
into a mechanical guard so no fabricated-boundary defect ships green again.

### Preconditions
- Evaluation artifacts exist (evaluation_001 + analysis_005, linked above).
- Files in scope are **guarded** (`.opencode/plugin/*.ts`, `opencode.jsonc` — e2e receipt
  ≥ mtime between edits) and **think-gated** (`omt_think.ts`, `omt_enforcer.ts` carry
  `TA:` — run `omt_think_list{path}` before editing; whole-repo consult covers).

### Main flow
1. `omt_phase{task_type:"major_feature", phase:"Analysis", feature:"feature_023", scope:"…"}`
2. Analysis/Design per tier (artifact per §12); Programming with TDD (behaviors as a
   **JSON array** in omt_testlist — prose fails tdd_check.py:403).
3. TESTLIST bootstrap: `omt_skip{scope:"tests"}` (chicken-and-egg prior art: feature_022
   all tiers, ledger-audited).
4. Guarded-file edits batched ONE write per file where possible; refresh the e2e receipt
   between files: `uv run pytest tests/scripts/omt/test_omt_harness_e2e.py -q`.
5. Exit Testing→Done via `omt_complete` (never `omt_done` — known-unreachable, see
   WORK.md gotchas).

### Guardrails
- F14 fix must not alter before-hook behavior (its `output.args` access is correct).
- No new named exports in any plugin (DEFECT-A doctrine).
- All four tiers keep the harness set green; the 3 pre-existing feature_018 failures are
  out of scope (documented, unrelated).

## Operations extracted (candidate; final set decided in Design)
- `omt_enforcer.ts` after-hook arg extraction fix (T1.1)
- e2e hook-effect probe (T1.3)
- SDK contract-pin test module (T2.1)
- named-export guard parametrization over 4 plugins (T3.1)

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_023.meta_harness_improvement/FEATURE.md` | [x] |
| Analysis | Analysis doc | `3.analysis/features/feature_023.meta_harness_improvement/analysis_001_f14_contract_pinning.md` | [x] |
| Design | Design doc | `4.design/features/feature_023.meta_harness_improvement/design_001_contract_pinning.md` | [x] |
| Implementation | Impl notes | `5.implementation/features/feature_023.meta_harness_improvement/` | [ ] |
| Testing | Test report | `6.testing/features/feature_023.meta_harness_improvement/` | [ ] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.
