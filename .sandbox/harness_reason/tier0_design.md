# Tier-0 Design — reason_table.ts ops + envelope

> Feature: feature_127 (minor_feature, Design) · Pattern: `startup_table.ts` `parseCompiled + renderTables` · Stdlib only, no `omt_` prefix

## Ops (closed, pure, no W)
- `format_ir(irJson: string): plain lines` — schemas (name+sorts+arrows), models (HarnessObs rows d1/d2/d3 with verdicts + DetailedD three-row + forget_projection/unit/counit notes), mappings (F preserves), queries (aligned expected Aligned/Mismatched/Unresolved + concretize_C cases), computes (refresh IO_Fail steps + semantics). Rejects ill-typed (missing sorts/arrows) with location, never throws session.
- `format_cert(certJson: string): plain lines` — mandatory structural/premises/execution/goal + program_digest/catalog/model/interp/context/contract/unit_counit + issues[] (node/code/expected/observed/via/next_obligation) + unknowns[] (node/reason/needed) + derivation[] + certificate_digest. Over-budget → summary ≤2KB (verdict/unknowns/scope/stale deps preserved) + mandatory detail_ref, never truncate; truncation fails validation.
- `explain_slice(certJson: string, nodeId: string): plain lines` — minimal premise-to-conclusion slice for nodeId, first unsupported connection, source refs, permitted acquisition path; unknown node → `unknown`; stale cert → re-evaluate first note. ≤2KB or detail_ref envelope.
- `parse_digest(ref: string): {kind, digest}` — parses `sha256:*`, `cert:sha256:*`, `detail_ref`; byte-stable replay note (probe 7).

## TS shape (mirrors startup_table.ts)
- `tool({description, args:{irJson?, certJson?, nodeId?, detailRef?}, execute})` → `{title:"Reason Table", output: markdown plain lines, metadata:{agent:{digests, verdicts, counts}}}`. User sees INTRO+IR+CERT+SLICE plain lines; agent metadata holds full IDs/digests (D19-style, no invention).
- File header: non-harness comment (no `omt_` prefix → outside `harness_paths` + e2e guard, no registry/perm/receipt) + TA: why line. Imports: `@opencode-ai/plugin` + `node:fs`/`node:path` only (stdlib). No `../lib/omt_shared` if avoidable — stdlib only per §7; if repoRoot needed, use minimal relative join (startup uses `initOmtShared`; Tier-0 keeps stdlib-only, no shared init).
- Output budgets: IR ≤40 lines, cert ≤30 lines, slice ≤15 lines, summary ≤2KB; overflow → detail_ref envelope.

## Run outline (sandbox demo, no src)
- `.sandbox/harness_reason/tier0_demo.py` (stdlib only): loads `stage0_ir.json` + §5 example cert + UC8 slice for `accept_tests`/`d3`, feeds formatter logic (Python mirror for demo), asserts plain-line contains Aligned/Mismatched/Unresolved + structural/premises/execution/goal + detail_ref envelope + digest parse. PASS = Tier-0 carries probe replays readable.

## Acceptance (Design → Programming)
- Ops list frozen above; Programming implements `reason_table.ts` + demo; Testing re-runs demo + S0 7/7 + checker 12/12 unchanged (advisory boundary).
