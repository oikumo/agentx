# Stage-1 Analysis — feature_123 (sandbox only)

Source: `.sandbox/category_theory_meta_harness.md` §14.1 (lines 980-991) + S0 `stage0_contracts.json` (8 generators v1) + `stage0_ir.json` (Obs/D/A, HarnessObs d1/d2/d3).
Rule: sandbox only; no src/net/toolbox change; advisory-only holds.

## 12-case table + S0 reuse

| # | §14.1 case | Required result | S0 contract reuse | check behavior | explain slice |
|---|---|---|---|---|---|
| 1 | hypothesis where evidence required | reject + name missing validator/premise | mapping.preserves_check, next.discrepancy_model | ill-typed or premise-failed with location | missing premise + validator_ref |
| 2 | receipt names old digest | stale + exact mismatch | evidence.accept_existing_test_result + query.aligned_equalizer | Mismatched witness (expected vs observed) | digest pair + via adapter |
| 3 | fabricated passed:true | require trusted producer | evidence.accept_existing_test_result | reject caller assertion | producer/record obligation |
| 4 | two slots same exclusive claim/lease | reject duplication | elaborator capability typing (§4 line 9) | type error, not runtime pass | duplicate slots + labels |
| 5 | two consumers share immutable ref | allow + per-consumer obligations | compare.two_programs_under_contract | allow under both contracts | shared ref + per-consumer obligations |
| 6 | test timeout/fail | preserve, no success established | evidence.accept_existing_test_result | preserve outcome | outcome + next_obligation |
| 7 | plan moves test before edit | reject under completion-relevant | compare.two_programs_under_contract | split: files-only permit, completion reject + (h1,h0) witness | contract named + witness |
| 8 | approved macro same bindings | replay defining cert, preserve | macro.verify_candidate_expand | replay + fresh obligations | defining digest + boundary |
| 9 | unrelated input changes | preserve unaffected immutables | context.import_snapshot_manifest + macro | invalidate only changed deps | preserved derivation IDs |
| 10 | relevant dirty/policy/generation/validator change | stale + re-import | context.import_snapshot_manifest | mark stale, re-import authoritative | stale causes + re-import list |
| 11 | context changes during collection | snapshot_inconsistent, never mixed-epoch | context.import_snapshot_manifest | snapshot_inconsistent or bounded retry | epoch pair |
| 12 | bound reached / validator absent | specific unknown | concretize.realize_forget | unknown(reason), never impossible/proved | bounds + missing validator |

Each case runs valid + invalid/unknown variant per §14.2.

## check / explain subset (§§11-14)

- `check`: query + named compute premises over immutable ObservationContext; returns verdict + certificate (~2KB summary or detail_ref envelope, digest-bound).
- `explain`: slice by node/result ID (premise chain, witness, stale causes, bounds).
- Withheld to stage 2: `plan` (bounded hole-fill), full `compare` promotion (compare stays probe-only via existing contract).
- Immutable import: manifest covers all relevant inputs (paths, policy/catalog versions, net rev, ledger pos); epochs must match or snapshot_inconsistent; never replay permission/applicability from cache.

## Exit criteria (Stage-1 gate)

- 12/12 agreement with existing authority (features 075/085 receipt checks, omt_q/ledger/probe surfaces) in sandbox.
- Mismatch (§11.6) + three-row (§3) replay from digests alone; truncation fails validation.
- Advisory boundary demonstrable: no net/ledger writes, no token movement, no src/toolbox registration.
- Kill/shrink per §15.1: predicates outrun validators → shrink to Tier 0.
