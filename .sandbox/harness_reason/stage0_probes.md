# Stage 0 probes 1–7 (sandbox only — §15.8, no production change)

Source: `.sandbox/category_theory_meta_harness.md` §15.8 + §§12.1–12.3, 11.6, 11.5.
Inputs: `stage0_contracts.json` (8 generators) + `stage0_ir.json` (§2 example + §3 rows).
Rule: passing 1–7 does not prove broad value; failing any fails feasibility for the dependent stage.

1. NEXT-discrepancy (ill-typedness only) — contract `next.discrepancy_model/v1`
   - Encode compiled-NEXT vs live-next as distinct types + O1–O3/H1–H3 from §12.1.
   - Pass = cites both NEXT contracts, refuses equality until explicit alignment, reports missing premise (semantic contract of each NEXT field).
   - Pass is NOT: bug diagnosis, menu repair authorization, H1/H2/H3 claim.

2. Reorder rejection — contract `compare.two_programs_under_contract/v1`
   - Run §12.2 edit/test model through `compare` under files-only vs completion contracts.
   - Pass = split verdicts (files-only permits, completion rejects `test;edit`) + `(h1,h0)` witness + contract named in result.

3. Stale-receipt agreement — contracts `evidence.accept_existing_test_result/v1` + `query.aligned_equalizer/v1`
   - Submit §11.6 mismatch program (artifact h2 vs receipt-subject h1).
   - Pass = pilot `subject_digest_mismatch{expected:h2, observed:h1, via, next_obligation: obtain applicable test evidence for h2}` agrees with existing receipt adapter (features 075/085).

4. Lease non-duplication — elaborator typing (capability threading, §4 line 9)
   - Submit two slots sharing one exclusive claim under different labels.
   - Pass = rejection as type error (duplicating exclusive lease), not runtime check pass.

5. Snapshot race — contract `context.import_snapshot_manifest/v1`
   - Interleave a relevant dirty-file change during context collection.
   - Pass = `snapshot_inconsistent` or bounded retry; never a mixed-epoch plan. Unchanged net_rev alone does not cover filesystem edits.

6. Reuse across two contexts — contract `macro.verify_candidate_expand/v1`
   - Expand `verify_candidate` (§12.3) for two artifacts.
   - Pass = fresh obligations per instantiation + replayed defining cert + refusal to carry old receipt/grant (refuse h2-with-h1 evidence with location).

7. IR round-trip — contracts `mapping.preserves_check/v1` + `concretize.realize_forget/v1` + `stage0_ir.json`
   - Serialize §2 example to JSON IR, re-elaborate, re-evaluate, replay cert from digests alone.
   - Pass = byte-stable replay for immutable inputs + unit/counit checks pass + `preserves stale_eq` verified.

Gates (§15.9): proceed 0–1 if contracts exist + probes 1–5 pass + output/caching discipline + advisory-only demonstrable. Proceed 2 if 12/12 §14.1 agreement + probes 6–7 + reuse in 2 contexts + unsafe substitution rejected with witness.
