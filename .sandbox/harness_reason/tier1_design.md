# Tier-1 Design — reason_check.ts ops + SSOT + whitelist

> Feature: feature_128 (minor_feature, Design) · Pattern: `reason_table.ts` proxy + `startup_table.ts` tool shape · Stdlib only, no `omt_` prefix

## Ops (closed, advisory, no W, plan withheld)
- `check(programJson|programPath, contextRef): §5 envelope` — elaborates §2 program, type-checks, evaluates pure fragments via kernel, routes effects via read-only adapters in W order, returns structural/premises/execution/goal + issues (node/code/expected/observed/via/next_obligation) + unknowns + derivation + digests. Never mints grants, never writes net/ledger.
- `explain(certOrResultId, nodeId): slice` — minimal premise-to-conclusion slice + first unsupported + source refs + permitted acquisition path; unknown node → unknown; ≤2KB or detail_ref.
- `compare(programA, programB, observationContract): rewrite cert | counterexample | unknown` — structural rewrite check under named contract + law/catalog versions + digests; unsafe substitution returns witness, never silent allow.
- `concretize(abstractRow, bound): realizations[] + distinguishing_info[]` — bounded enumeration via Realize vocab bounds; over-bound → unknown(bound_exceeded|permission_gated) with bound + detail_ref, never silent cut.
- Withheld: `plan` (bounded hole-fill) stays out until stage-2 gates.

## TS shape (mirrors reason_table.ts + startup_table.ts)
- `tool({description, args:{op, programJson?, programPath?, certJson?, nodeId?, contract?, bound?}, execute})` → `{title:"Reason Check", output: §5 plain lines + detail_ref, metadata:{agent:{digests, verdicts, counts}}}`. Closed enum enforced in TS before argv build + mirrored in Python subparsers.
- Advisory guard (TS, before spawn): reject any op spelling/arg that would write net/ledger, move tokens, mint grants/leases/Done, touch protected paths (.env*, uv.lock without skip), or import src/; failures → `{ok:false, reason}` advisory JSON, never throw.
- Proxy: `uv run --no-sync scripts/reason/check.py <op> --args...` with per-op argv whitelist (exact flags per subparser + pinned tests); no shell interpolation of program JSON (temp file or stdin).
- File header: non-harness comment (no `omt_` prefix → outside harness_paths + e2e guard, no registry/perm/receipt) + TA: why line. Imports: `@opencode-ai/plugin` + `node:child_process`/`node:fs`/`node:path` only (stdlib). No `../lib/omt_shared` init.
- Output budgets: summary ≤2KB, IR ≤40 lines via reason_table reuse, cert ≤30, slice ≤15; overflow → detail_ref envelope, never truncate.

## Python SSOT shape (single-core rule)
- `scripts/reason/check.py` (argparse subparsers for 4 ops + --json envelope out) → `elaborate.py` (JSON IR load + type-check) → `kernel.py` (pure eval: equalizer Aligned/Mismatched/Unresolved + preserves + concretize bounds) → `router.py` (read-only adapters: existing receipt/context validators, unknown_if gaps) → `certs.py` (§5 envelope emit + digest + detail_ref).
- Reuse S0 contracts + IR + checker/composer fixtures for replay (no new semantics, no src/ imports, stdlib only).
- `opencode.jsonc`: one `reason_check: allow` line outside `harnessc:begin/end` blocks (e.g., beside `skill: allow`), short description (budget discipline).

## Tests (canary-gated under tests/)
- `tests/scripts/reason/test_argv_whitelist.py` (pinned per-op flags, reject widening + injection)
- `tests/scripts/reason/test_probes_fixtures.py` (§15.8 1–7 via SSOT, digest stable)
- `tests/scripts/reason/test_cert_replay.py` (byte-stable replay + truncation-fails + snapshot_inconsistent)
- Sandbox demo `.sandbox/harness_reason/tier1_demo.py` (stdlib only): exercises 4 ops via SSOT functions, asserts envelopes + budgets + guard rejects.

## Acceptance (Design → Programming)
- Ops + whitelist + guard + SSOT outline frozen above; Programming implements SSOT + proxy + tests + demo; Testing re-runs demo + S0 7/7 + S1 12/12 unchanged (advisory boundary).
