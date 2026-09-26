# Stage-2 Design — feature_124 (sandbox only, minor_feature quick op list)

Inputs: `stage2_analysis.md` (fragments + law set + two-context cases + U1–U5) + S0 contracts/IR + S1 checker (12/12) + probes (7/7).
Outputs (next phase): `.sandbox/harness_reason/run_composer.py` → two-context reuse + U1–U5 rejection + byte-stable replay, sandbox only.
Non-goals: `plan` hole-fill, Tier-1/2 promotion, any src/net/ledger/toolbox change.

## Ops (closed enum for this sandbox composer)

1. `import_snapshot(paths, policy_v, catalog_v, net_rev, ledger_pos) -> ObservationContext`
   - Reuse S1 op; epochs must match or `snapshot_inconsistent`; never replay permission/applicability from cache.
2. `expand_verify_candidate(macro_digest, bindings[task,artifact,acceptance,validator], context_id) -> ReplayedCert + FreshObligations | Refusal`
   - Exact defining-diagram match + boundary check; fresh binds per instantiation; replay defining cert D (digest-cited) + emit fresh obligations O (evidence for artifact, env-applicability, validator acceptance).
   - Refuse h2-with-h1 (U1), inexact match (U4), validator substitution without equivalence (U3) with location + reason + obligation.
3. `rewrite(program, law_id, contract_id, context_id) -> RewrittenProgram + RewriteCert | Refusal`
   - Laws: `identity | regroup | wire-perm | macro-expand | domain-eq` only; side conditions checked per analysis; contract named in cert.
   - `test;edit` under completion-relevant-v1 → reject + `(h1,h0)` witness (U2); under files-only-v1 → permit (contract-relative equality).
4. `check_composed(program_ref, context_id, premises[]) -> Certificate`
   - Reuse S1 `check` (query + named compute premises over immutable context); verdicts ok / premise_failed / ill_typed / stale / unknown.
5. `explain(cert_id | node_id) -> Slice`
   - Reuse S1 `explain`; slices include rewrite chain (law IDs + step digests), U-witnesses, stale causes, bounds.

Withheld: `plan`, `concretize` beyond S0 bounded enumeration, Tier-1 enum widening.

## Rewrite cert envelope (mandatory, never truncated)

```
{ program, context_manifest_digest, catalog_v, model_digest,
  defining: { macro_digest, boundary },
  bindings: { task, artifact, acceptance, validator },
  structural: valid|invalid(location),
  premises: ok | failed[{premise, location, obligation}] | unknown(reason),
  execution: not_attempted (stage-2 has no execution),
  goal: established | not_established | unknown,
  rewrites: [{ from, to, law_id, contract_id, step_digest }],
  stale: [] | [{result, cause, reimport}],
  refusals: [] | [{location, reason, obligation, witness}],
  derivation: [step digests + law/contract IDs],
  summary_2KB: "..." | detail_ref: "node_id -> slice" }
```

- Truncation fails validation (summary + mandatory detail_ref instead).
- Byte-stable replay for immutable inputs (probe-7 rule); two-context replay cites same defining digest, different binding digests.

## run_composer.py outline (two contexts × valid/reuse/invalid variants)

- Reuse `run_checker.py` patterns (stdlib only, pure fixtures, no harness imports).
- Ctx-A (h1): expand → ok + fresh O1; rewrite `edit;test` under both contracts → permit (files-only) + permit-or-check (completion, h1==h1).
- Ctx-B (h2): expand same digest → ok + fresh O2 (no O1 carry); U1 probe (submit h1 receipt for h2) → Refusal with location; U2 probe (`test;edit` under completion) → reject + `(h1,h0)`; U3/U4 probes → unknown/refuse; byte-stability probe (re-run Ctx-A immutable) → identical digest.
- Pass = reuse across two contexts + U1–U5 rejected with witnesses + replay from digests + advisory boundary demonstrable.

## Boundaries / kill line

- Advisory only: certs never mint grants/leases/Done; compute never read as grant; unknown never guessed.
- Kill/shrink per §15.1: reuse needs enum widening, src imports, or net/ledger writes → shrink to Tier 0 renderer, no Tier-2 work.
