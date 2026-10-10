# Feature 138: Split Proof Oracle Firewall Slice

> **Status:** [x] Programming done (TDD done ✅, 0 regressions, 5 drift) → Testing
> **Created:** 2026-10-10
> **WORK.md task:** sandbox `orthogonality_001_wrapper_split` V7 §E (Oracle `split_proof_meta` v2, firewall slice)

---

## Summary

First falsifiable slice of the V7 Oracle: an advisory CLI (`scripts/omt/split_proof.py`
with `prove --lane product|harness|both`, `verify`, `attest-bridge`, `newcomer-probe`) plus
AST import-firewall goldens and a newcomer REPL probe under `tests/harness_meta/`
(canary). Runs against the current mixed layout with a versioned exemption manifest
(bench fixture-strings + path-strings); zero `src/`/`tests/` moves, zero `omt_*` renames,
CI-strict/local-advisory. Gate predicate (E2), ledger kinds (E3) and nav SECTION (E5)
stay design-only in this slice.

## Scope (one sentence — what "done" looks like)

`prove --lane both` emits two byte-identical-verifiable certs, firewall golden pins the
import-statement regex with exemptions, newcomer probe boots `uv run agentx` → `c` clean.

## Task type

major_feature

---

## Phase artifacts (traceability)

Per `omt_agent_guide.md §12`, fill only the rows your task type requires. Link each
artifact as it is produced so WORK.md → this file → every phase doc stays navigable.

| Phase | Artifact | Path | Status |
|-------|----------|------|--------|
| Requirements | Use case | `2.requirements/.../feature_138.split_proof_oracle_firewall_slice/` | [x] |
| Analysis | Analysis doc | `3.analysis/features/feature_138.split_proof_oracle_firewall_slice/analysis_001_*.md` | [x] |
| Design | Design doc | `4.design/features/feature_138.split_proof_oracle_firewall_slice/design_001_*.md` | [x] |
| Implementation | Impl notes | `5.implementation/features/feature_138.split_proof_oracle_firewall_slice/` | [x] slice = `scripts/omt/split_proof.py` + manifest (E1), no E2/E3/E5 wiring |
| Testing | Test report | `6.testing/features/feature_138.split_proof_oracle_firewall_slice/` | [x] |

**Naming convention (enforced by `new_feature.py`):** phase docs are
`analysis_NNN_<topic>.md`, `design_NNN_<topic>.md` — incrementing `NNN`, lower_snake topic.
Do **not** create ad-hoc `*_PROOF.md` / `*_SUMMARY.md` files; fold proofs into the test report.
