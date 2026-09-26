# Stage-2 Analysis — feature_124 (sandbox only)

Source: `.sandbox/category_theory_meta_harness.md` §§11.7, 12.2–12.3, 15.9 + S0 `stage0_contracts.json` (8 generators v1) + `stage0_ir.json` + S1 `stage1_analysis.md` (12 cases) + `run_checker.py` (12/12) + `run_probes.py` (7/7, digest 6e355d71).
Rule: sandbox only; no src/net/ledger/toolbox change; advisory-only holds (certs never mint grants/leases/Done).

## Fragments (parameterized)

| Fragment | Params | Binds fresh per instantiation | Reuses |
|---|---|---|---|
| `verify_candidate` macro | `MacroDigest[verify_candidate] + Bindings[task, artifact, acceptance, validator]` | artifact digest, acceptance predicate, validator ref, context manifest digest | defining cert replay (digest + boundary) + S0 `macro.verify_candidate_expand/v1` |
| `aligned` query | `Model[HarnessObs] + ComputePremises[refresh*]` | recorded vs current per artifact | S0 `query.aligned_equalizer/v1` (d1 Aligned / d2 Mismatched / d3 Unresolved) |
| `refresh` compute | `IO_Fail` steps: import manifest → validate each Mismatched via receipt adapter → witnesses + unknowns | fresh `W` per run, no fail→ok | S0 `evidence.accept_existing_test_result/v1` |
| `compare` under contract | `Program[A], Program[B], ObservationContract[completion-relevant-v1 \| files-only-v1]` | contract named per cert | S0 `compare.two_programs_under_contract/v1` |

Exact-match rule: macro expansion requires exact defining-diagram match; fresh binds per instantiation; no grant/lease/test-success carryover (type error at elaboration on carryover attempt).

## Small law set (§11.7 allow-list only)

1. `identity` — `p ; id = p` (side: type-preserving, no epoch change).
2. `regroup` (assoc) — `(a;b);c = a;(b;c)` (side: same `W` thread, no fail-masking).
3. `wire-perm` — reorder independent wires (side: contract-relative; forbidden where order is completion-relevant).
4. `macro-expand` — `verify_candidate(bindings) = replayed defining cert + fresh obligations` (side: exact digest match + boundary check + fresh validator binds).
5. `domain-eq` — `stale_eq: rec == cur o src` via `finite_table_check` (side: total mapping, per-equation evidence; S0 `mapping.preserves_check/v1`).

Outside allow-list → `unknown(law_outside_allow_list)`, never default-permit.

## Two-context reuse cases

- **Ctx-A (h1):** artifact h1 + acceptance P1 + validator V1 + manifest M1 → `verify_candidate` expands → replay defining cert D + fresh obligations O1 (evidence for h1, env-applicability for M1).
- **Ctx-B (h2):** same macro digest, new bindings (artifact h2, acceptance P2, validator V2, manifest M2) → replay D + fresh obligations O2. Pass = O2 freshly validated, D replayed byte-stable, no O1/E1 carried.
- **IR grounding:** d1/d2/d3 rows re-evaluated per context; `aligned` query re-run (d1 Aligned only if recorded==current in that context); `refresh` runs fresh `W`.
- **Second reuse axis (programs):** `edit;test=(h1,h1)` vs `test;edit=(h1,h0)` under two contracts — files-only permits both, completion-relevant rejects `test;edit` with `(h1,h0)` witness.

## Unsafe-substitution witnesses (must reject)

| # | Substitution | Expected | Witness shape |
|---|---|---|---|
| U1 | h2-with-h1 evidence (carry receipt/grant for h1 to h2) | refuse with location | `Refusal[location: premise h_receipt==h_artifact, reason: h2-with-h1, obligation: obtain applicable test evidence for h2]` |
| U2 | `test;edit` under completion-relevant contract | reject | `(h1,h0) + contract named (completion-relevant-v1)`; files-only permits same program (contract-relative) |
| U3 | validator substitution without equivalence (V2 for V1, no equiv proof) | unknown/refuse | `unknown(validator_substitution_without_equivalence) + required: equivalence cert` |
| U4 | similar-steps substitution (near-miss diagram, non-exact match) | refuse | `Refusal[location: macro boundary, reason: inexact defining-diagram match]` |
| U5 | permission/applicability replay from cache | re-import, never replay | `snapshot_inconsistent` or fresh import obligation |

## Exit criteria (Stage-2 gate, §15.9 proceed-2)

- `verify_candidate` expands across two artifacts with fresh obligations per instantiation (refuses h2-with-h1 with location).
- `test;edit` rejected under completion-relevant with `(h1,h0)` witness while permitted under files-only (contract named in both certs).
- Rewrite certs replayable from digests alone (derivation = step digests + law/contract IDs; defining digest + boundary cited); byte-stable for immutable inputs (probe-7 rule).
- Advisory boundary demonstrable: no net/ledger writes, no token movement, no src/toolbox registration.
- Kill/shrink per §15.1: validators outrun predicates or reuse needs enum widening → shrink to Tier 0, no Tier-2 work.
