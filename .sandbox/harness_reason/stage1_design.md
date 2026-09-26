# Stage-1 Design — feature_123 (sandbox only, minor_feature quick op list)

Inputs: `stage1_analysis.md` (12-case table) + S0 `stage0_contracts.json` + `stage0_ir.json`.
Outputs (next phase): `.sandbox/harness_reason/run_checker.py` → 12/12 §14.1 agreement, sandbox only.
Non-goals: `plan` (withheld to stage 2), full `compare` promotion, any src/net/ledger/toolbox change.

## Ops (closed enum for this sandbox checker)

1. `import_snapshot(paths, policy_v, catalog_v, net_rev, ledger_pos) -> ObservationContext`
   - Requires manifest covers all relevant inputs + epochs consistent; else `snapshot_inconsistent` (case 11) or `unknown(hidden_dependency)`.
   - Never replays permission/applicability from cache; protected inputs excluded → unknown.
2. `check(program_ref, context_id, premises[]) -> Certificate`
   - Pure over immutable context; query (aligned equalizer) + named compute premises (refresh/validate via S0 validator_refs, PROPOSED adapters only as agreement oracle, never registered).
   - Verdicts: ok / premise_failed(location, obligation) / ill_typed(location) / stale(witness) / unknown(reason+bounds).
3. `explain(cert_id | node_id) -> Slice`
   - Premise chain + witness (expected/observed digests, contract named, stale causes, bounds, distinguishing info for concretize cases).
   - Detail addressable by ID; default summary ≤ ~2KB.

Withheld: `plan`, `concretize` beyond S0 bounded enumeration, `compare` beyond probe-2 contract-relative verdicts.

## Certificate envelope (mandatory, never truncated)

```
{ program, context_manifest_digest, catalog_v, model_digest,
  structural: valid|invalid(location),
  premises: ok | failed[{premise, location, obligation}] | unknown(reason),
  execution: not_attempted (stage-1 has no execution),
  goal: established | not_established | unknown,
  stale: [] | [{result, cause, reimport}],
  derivation: [step digests + law/contract IDs],
  summary_2KB: "..." | detail_ref: "node_id -> slice" }
```

- Truncation fails validation (emit summary + mandatory detail_ref instead).
- Byte-stable replay for immutable inputs (same rule as probe 7).

## run_checker.py outline (12 cases × valid/invalid variants)

- Reuse `run_probes.py` patterns (stdlib only, pure fixtures, no harness imports).
- Per case: valid fixture → ok/allow/replay/preserve; invalid fixture → reject/stale/unknown with location + obligation; agreement oracle = S0 expected values + features 075/085 semantics (stale verdict, exact mismatch) cited, never executed.
- Case → contract map (from analysis): 1→preserves/next, 2+3+6→evidence+equalizer, 4→capability typing, 5+7→compare, 8→macro, 9+10+11→snapshot manifest, 12→concretize.
- Pass = 12/12 agree with existing authority + mismatch/three-row replay from digests + advisory boundary demonstrable (no writes, no token movement).

## Boundaries / kill line

- Advisory only: certs never mint grants/leases/Done; compute never read as grant; unknown never guessed.
- Kill/shrink per §15.1: validators outrun predicates or snapshot_inconsistent unusable → shrink to Tier 0 renderer, no Tier-2 work.
