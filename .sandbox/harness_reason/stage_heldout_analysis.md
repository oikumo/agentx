# Held-out Analysis — feature_126 (sandbox only)

Source: `.sandbox/category_theory_meta_harness.md` §§14.1 (12 cases, lines 974-993), 14.2 (fair comparison, 995-1014: held-out real tasks after fixtures stable, same catalog/adapters/fragments/inputs/budgets/oracle, snapshot+order, per-case+variability, 15% decision rule), 14.3 (token discipline, 1016-1023: ~2KB summary, never truncate), 15.6 (cost-benefit gate, 1120-1124), 15.1/15.9 (verdict+gates, 1029-1042/1152-1159) + S0 `stage0_contracts.json` (8 generators v1) + `stage0_ir.json` + S1 `run_checker.py` (12/12) + S2 `run_composer.py` (7/7) + S3 `run_experiment.py` (7/7 digest d476df80d71d829a stable).
Rule: sandbox only; no src/net/ledger/toolbox change; advisory-only holds (certs never mint grants/leases/Done; `compute` never read as grant; `unknown` never guessed).

## Three arms (same inputs, different reasoning — unchanged from S3)

| Arm | What it is | Receives (identical) | Produces |
|---|---|---|---|
| A0 current harness | existing receipt/dependency authority as-is | real task inputs + budgets + oracle | harness verdict (grant/block/unknown) — the oracle baseline |
| A1 enhanced typed planner | conventional typed functions/templates + contracts, no categorical kernel | same generator catalog (8 v1) + evidence adapters + candidate fragments + real inputs + model/tool budgets + acceptance oracle | plan + per-step obligations + cost ledger |
| A2 categorical kernel | S1 checker + S2 composer (check/explain/expand/rewrite) | identical catalog/adapters/fragments/inputs/budgets/oracle as A1 | plan + cert (structural/premises/execution/goal + digests + derivation) or named unknown |

Fairness rule (§14.2): any improvement must come from structure, not better inputs. All three share catalog version, adapter versions, fragment digests, task inputs, budgets, oracle. Order varied R=3; one initial snapshot per run.

## Held-out real tasks (R1–R4, real files/digests, real checker runtime)

- R1 stale-receipt, real artifact: `stage0_contracts.json` vs edited copy in tmp. Require `subject_digest_mismatch` to agree with existing receipt authority on expected/observed/next-obligation (§14.1 stale; §15.5 cert-rot digest binding).
- R2 reuse across two real contexts: expand `verify_candidate` for `stage0_contracts.json` (Ctx-A) → `stage0_ir.json` (Ctx-B). Require fresh obligations per instantiation; refuse h2-with-h1 evidence with location (S2 U1 on real digests; §14.1 shared-immutable vs exclusive-lease distinction).
- R3 interruption/resume, real mutate: snapshot manifest of `.sandbox/harness_reason/` (name+sha256 per file + catalog digest + net rev note), mutate one file copy, re-run: unaffected immutable derivations preserved (digest-equal), affected marked stale + re-import, count avoided derivation/review steps. Only place token savings may appear (§15.6/H3). Measure actual host checker-ms + wall latency; tokens as labeled proxy bytes unless host tokens available (§14.2 proxy rule).
- R4 snapshot race, real concurrent touch (optional but gated): background touch during collection → `snapshot_inconsistent`, never mixed-epoch plan (§14.1 context-change; §15.1 highest-risk gate). If inconsistent-rate makes stage-1 unusable on real tasks, stop before stage 2 per kill table.

Out: synthetic T01–T12/H1–H3 ledgers remain as regression (must still pass), but threshold rule is evaluated on R1–R3 (+R4 discipline check, not costed).

## Oracle + snapshot/order discipline (carried from S3)

- Oracle: existing harness authority (features 075/085 receipt/dependency) + named validators per predicate; unsupported → `unknown` (never guessed).
- Agreement gate: A1/A2 verdicts must match A0 on R1–R3 validity (mismatch = missed stale/unsupported/unsafe, counted against the arm with location).
- Snapshot: one initial manifest digest per run (file sha256 set + catalog/fragment digests); mid-collection change → `snapshot_inconsistent`, never mixed-epoch plan.
- Order: rotate arm order across R=3 reps; cache key = content + context deps + catalog version + observation contract (immutable vs permission/applicability split).

## Metrics (per-case + variability, real measurements first)

Per case per arm per rep: correctness + final result; missed stale/unsupported/unsafe (U1–U5 counters); interventions + false blockers; calls, wall-ms, checker-ms, tokens-or-proxy (labeled), maintenance cost note; avoided steps via reuse (fragment hits, R3). Report: per-case table + median/range across reps + threshold-rule evaluation. Never toolbox run-count as quality (§14.2).

## Keep/shrink conditions (agreed before experiment — decision rule, not prediction)

- Keep kernel (toward Tier 1/2 only via toolbox review) iff ≥15% median cost reduction on R1–R3 with no correctness loss + no authority divergence, repeated + green budgets + user selection.
- Keep planner (D6): if A1 matches A2 at lower complexity, keep A1, retain category theory as explanation.
- Shrink to Tier 0: validator gaps outrun predicates, signatures mostly hand assertions, reuse needs enum widening/src imports/net writes, or threshold miss.
- Kill/shrink per §15.1 throughout (notably snapshot-incoherence rate, adapter divergence, uncheckable ontology).

## Exit criteria (held-out design gate)

- Analysis (this file) covers arms/shared-inputs/R1–R4/oracle/metrics/keep-conditions with proposal refs.
- Design (`stage_heldout_design.md`) lists held-out ops + `run_heldout.py` outline + report envelope (per-case + variability + threshold rule on real tasks).
- Probe (`run_heldout.py`, stdlib only) passes validity checks: shared-inputs parity, snapshot/order, agreement, unknown discipline, contract-relative (via S2 replay), reuse freshness on real digests, report shape byte-stable, boundary (sandbox-only).
- No src/tests/net/toolbox change — `git status` shows only `.projects/meta`, `WORK.md`, `.meta/.../feature_126/`, `.sandbox/harness_reason/`.
