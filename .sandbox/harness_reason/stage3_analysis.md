# Stage-3 Analysis — feature_125 (sandbox only)

Source: `.sandbox/category_theory_meta_harness.md` §§14.1 (12 cases), 14.2 (fair comparison), 14.3 (token discipline), 15.6 (cost-benefit gate), 15.1/15.9 (verdict + gates) + S0 `stage0_contracts.json` (8 generators v1) + `stage0_ir.json` + S1 `stage1_analysis.md` + `run_checker.py` (12/12) + S2 `stage2_analysis.md` + `run_composer.py` (7/7) + `run_probes.py` (7/7, digest 6e355d71).
Rule: sandbox only; no src/net/ledger/toolbox change; advisory-only holds (certs never mint grants/leases/Done; `compute` never read as grant; `unknown` never guessed).

## Three arms (same inputs, different reasoning)

| Arm | What it is | Receives (identical) | Produces |
|---|---|---|---|
| A0 current harness | existing receipt/dependency authority as-is | task inputs + budgets + oracle | harness verdict (grant/block/unknown) — the oracle baseline |
| A1 enhanced typed planner | conventional typed functions/templates + contracts, no categorical kernel | same generator catalog (8 v1) + evidence adapters + candidate fragments (`verify_candidate`, `aligned`, `refresh`, `compare`) + task inputs + model/tool budgets + acceptance oracle | plan + per-step obligations + cost ledger |
| A2 categorical kernel | S1 checker + S2 composer (check/explain/expand/rewrite) | identical catalog/adapters/fragments/inputs/budgets/oracle as A1 | plan + cert (structural/premises/execution/goal + digests + derivation) or named unknown |

Fairness rule (proposal §14.2): any improvement must come from structure, not better inputs. All three share catalog version, adapter versions, fragment digests, task inputs, budgets, oracle. Order varied across runs; one initial snapshot per run.

## Task set (fixtures first, held-out after)

- T01–T12: 12 §14.1 cases, each valid + invalid/unknown variant where appropriate (reuse S1 12-case table + S0 IR rows d1/d2/d3). Covers: missing validator, stale digest, fabricated metadata, exclusive-claim dup, shared immutable ref, failed/timeout test, reorder under completion-relevant contract, macro replay, unrelated-input change, relevant-change staleness, epoch mix, bound/validator-absent unknown.
- H1 reuse-across-contexts: `verify_candidate` Ctx-A (h1) → Ctx-B (h2), fresh obligations per instantiation, refuse h2-with-h1 (S2 U1).
- H2 contract-relative replacement: `edit;test` vs `test;edit` under files-only (permit both) vs completion-relevant (reject `test;edit` with (h1,h0) witness) (S2 U2 + §12.2).
- H3 interruption/resume: avoid re-deriving why a workflow is valid after artifact change (the only place token savings may appear, §15.6/token-economics).
- Held-out real tasks added only after fixtures stable (proposal §14.2). This analysis designs the harness for them; the sandbox probe models T01–T12 + H1–H3 with synthetic cost ledgers.

## Oracle + snapshot/order discipline

- Oracle: existing harness authority (features 075/085 receipt/dependency) + named validators per predicate; unsupported → `unknown` (never guessed).
- Agreement gate carried from S1: A1/A2 verdicts must match A0 on T01–T12 validity (mismatch = missed stale/unsupported/unsafe, counted against the arm).
- Snapshot: capture one initial manifest digest per run; any mid-collection context change → `snapshot_inconsistent`, never a mixed-epoch plan (S0 probe 5).
- Order: vary arm execution order across repeated runs so warm caches/reused context do not favor one arm; cache key = content + context deps + catalog version + observation contract (immutable derivations separate from permission/applicability).

## Metrics (per-case + variability, never toolbox run-count as quality)

Per case per arm per run: correctness of accepted plan + final result; missed stale / unsupported conclusions / unsafe substitutions (U1–U5 counters); extra interventions + false blockers; calls, latency, tokens (actual host tokens when available, else labeled proxy bytes), checker runtime; signature/adapter/cert maintenance cost; avoided derivation/review steps via reuse (fragment hits).
Report: per-case table + median/p range across runs (variability required; small pilot proves nothing universal). Token proxy labeling mandatory (§14.2/15.6).

## Keep/shrink conditions (agreed before experiment — decision rule, not prediction)

- Keep kernel (promote toward Tier 1/2 only via existing toolbox review) iff: material end-to-end effort reduction on composition/reuse tasks (proposed rule: ≥15% median cost reduction) with no correctness loss and no authority divergence, repeated + green budgets + user selection.
- Keep planner (D6): if A1 matches A2 at lower complexity, keep A1, retain category theory as explanation.
- Shrink to Tier 0 (renderer only): validator gaps outrun predicates (many unknowns), signatures mostly hand-written assertions validators cannot establish, reuse needs enum widening / src imports / net writes, or threshold miss.
- Kill/shrink triggers per §15.1 apply throughout.

## Exit criteria (Stage-3 design gate)

- Analysis (this file) covers arms/shared-inputs/tasks/oracle/metrics/keep-conditions with proposal line refs.
- Design (`stage3_design.md`) lists experiment ops + `run_experiment.py` outline + report envelope (per-case + variability + threshold-rule evaluation).
- Probe (`run_experiment.py`, stdlib only) passes validity checks: shared-inputs parity, snapshot/order discipline, per-case report shape, threshold rule evaluated as decision rule, advisory boundary (no net/ledger writes).
- No src/tests/net/toolbox change — `git status` shows only `.projects/meta`, `WORK.md`, `.meta/.../feature_125/`, `.sandbox/harness_reason/`.
