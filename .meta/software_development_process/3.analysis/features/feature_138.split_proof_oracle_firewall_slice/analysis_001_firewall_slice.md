# Analysis 001 — split-proof Oracle firewall slice (feature_138)

> Parent: `2.requirements/features/feature_138.split_proof_oracle_firewall_slice/FEATURE.md`
> Sources: `sandbox/orthogonality_001_wrapper_split/PROPOSAL_V7.md` (§0 boundary, §E Oracle),
> `T1_AUDIT_V8.md` (§0 file→tool map, §2 mapping), `EXECUTE_V8.md` (§1 re-measure 2026-10-10).

## Problem

V4/v5 prove nothing executable: boundary clean "by discipline, not by test" (zero runtime
imports either way modulo exemptions, but no golden enforces it); substring `rg agentx`
yields 5 hits (`scripts/omt/bench/tasks.py:11,12` path-strings, `:32,:44` fixture-strings,
`:35` path-string) so any naive substring golden false-positives on day one.

## Evidence (re-measured 2026-10-10T17:40Z)

- `tests/scripts/` 104 files (all-harness: `omt/` 71 + `toolbox/` 6 + `reason/` + `session_inspect/`);
  `tests/features/` 100 files in 52 dirs (mixed); lanes `tests/agentx`, `tests/harness_meta` absent.
- Studio is the only leg with proofs (`tools/petri-net-studio`: 15 test files incl.
  `independence.test.ts` + `check-independence` script) — the template to generalize.
- File→tool map closed (T1_AUDIT_V8 §0): `phase/skip/complete/tdd` all enforcer-owned
  (`omt_enforcer.ts:17,28-29,47` + `tdd_hats` import) — no separate plugin files to wire.

## Decision

Build the firewall slice first: AST import firewall (Python `ast` + TS imports, versioned
exemption manifest) + newcomer REPL probe + advisory `prove/verify/attest-bridge` CLI.
Defer: gate predicate E2 (harness-surface 2nd-edit gate), ledger kinds E3 (append-only
design first), nav SECTION E5 wiring, all lane migrations, row #1 delete, UC8 promotion.
Advisory-only (`reason_check` precedent — zero registry rows), CI-strict/local-advisory,
ephemeral overlay in v1 = current-tree scan (worktree overlay lands with T3).
