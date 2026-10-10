# Design 001 — split-proof Oracle firewall slice (feature_138)

> Parent FEATURE + Analysis 001 (same feature dirs). V7 canonical: `PROPOSAL_V7.md` §E (v2 hardening).

## E1 — CLI `scripts/omt/split_proof.py` (advisory, zero registry rows)

Verbs (v1, current-tree scan; `--overlay tmpfs` worktree lands with T3):
- `prove --lane product|harness|both` → runs the firewall scans (Python AST + TS imports
  + exemption manifest) and emits canonical JSON LOCKED v1 (field order fixed):
  `{oracle:"split_proof/v1", lane, file_rev, live_rev, ledger_sha, firewall_verdict,
  ta_ast_hash, newcomer, tokens_ms, cert_sha}` (cert ≤2 KiB; `cert_sha` = sha256 of the
  payload minus `cert_sha` itself; timestamps excluded from hash).
- `verify <cert.json>` → re-runs scan, asserts byte-identical modulo timestamps/excluded fields.
- `attest-bridge` → checks conforming `bridge:` format (standalone token in Decisions log) +
  reports backlog (expect: 0 conforming, 1 prose `meta_harness_11:50`).
- `newcomer-probe` → boots `uv run agentx`, sends `c`, asserts REPL answers with zero harness env.
- `ledger_sha` = sha256 of `.meta/.omt/ledger.jsonl` at prove time (chain link, Merkle-style;
  no new ledger kinds in this slice — E3 design-only).

## Exemption manifest (versioned, `scripts/omt/split_proof_exemptions.json` v1)

- Python `ast`-level: fixture-strings `scripts/omt/bench/tasks.py:32,44` (triple-quoted
  `CHAT_REGRESSION_APPEND` / `MAJOR_TEST_CONTENT`), path-strings `:11,:12,:35`
  (`MODEL_FILE`/`UI_FILE`/`MAJOR_SRC`). TS: `import` statements only (not comments/strings).
- Forbidden edges: `src/agentx/**` → `scripts.omt|scripts.session_inspect|scripts.reason|opencode`
  runtime imports; reverse `scripts/omt/**` → `src.agentx` runtime imports. Test files under
  `tests/` asserting the boundary are themselves exempt from the reverse edge (they must import
  both sides to test them) — pinned here, not discovered.

## E4 — Tests (repo-conventional home until T3 lanes land)

Goldens live at `tests/features/feature_138.split_proof_oracle_firewall_slice/`
(repo `feature_NNN.*` convention — keeps the Programming→Testing unit-tests gate
and the `omt_tdd done` feature-suite check real). They migrate to
`tests/harness_meta/split_proof_meta/` under the Oracle exemption manifest at T3
(planned, manifested — see implementation notes).

- `test_firewall_meta.py` — AST firewall golden: parses all `src/agentx/**/*.py` (`ast`) +
  `scripts/omt/**/*.py` + `tools/petri-net-studio/src/**/*.{ts,tsx}` imports; applies manifest;
  asserts zero non-exempt edges. Substring `rg agentx` must NOT be used (5-hit false-positive class).
- `test_newcomer_meta.py` — newcomer probe: `uv sync --frozen` state assumed; boots
  `uv run agentx`, sends `c`, asserts chat REPL answers within timeout, zero harness env vars.
- Deferred to later slices: `test_rename_away_meta.py` (needs T3 overlay + lanes),
  `test_ta_strip_meta.py` (T4), `test_ledger_contract_meta.py` (T2 Q4 pin of 12-file `.meta/.omt/`).

## Out of scope (explicit)

E2 predicate wiring (`.opencode/` 2nd-edit gate), E3 kinds, E5 nav SECTION, lane dirs,
any `tests/` moves, `test_omt_mvc_gate.py` disposition, UC8 promotion. `ta_ast_hash` in this
slice = sha256 of sorted `rg -c "# TA:"` per-file counts (placeholder until T4 AST strip test).

## Acceptance

`uv run scripts/omt/split_proof.py prove --lane both` → 2 certs green +
`verify` byte-identical + `attest-bridge` backlog == {0 conforming, 1 prose} +
`uv run pytest tests/harness_meta/split_proof_meta -q` green.
