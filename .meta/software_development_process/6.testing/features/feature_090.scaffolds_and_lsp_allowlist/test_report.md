# Test Report: Scaffolds And Lsp Allowlist

> **Phase:** Testing — `omt_agent_guide.md §11` | **Feature:** feature_090.scaffolds_and_lsp_allowlist
> Run everything with `uv run pytest ...` (AGENTS.md MANDATORY).

## Stage 1 — Unit / component
| Component | Normal path | Exception paths | Result |
|-----------|-------------|-----------------|--------|
| `new_feature.py testing` | creates `6.testing/features/<slug>/test_report.md` from the template (TITLE/SLUG rendered) | unknown slug → rc=2 "unknown feature"; existing target → rc=2 "already exists", content untouched; `--dry-run` creates nothing | [x] |
| `new_feature.py implementation` | creates `5.implementation/features/<slug>/impl_notes.md` (slug + `--date` honored) | same rc=2 guards as `testing` | [x] |
| argv pre-scan | legacy positional `name` path byte-identical; exact-match only ("testing framework" stays a NAME → `feature_008.testing_framework`) | — | [x] |
| `lsp_filter.parseAllowlist` | valid JSON → map (backslash-normalized keys) | invalid JSON / non-object / non-string-array values / number → null | [x] |
| `lsp_filter.loadAllowlist` | reads `<root>/.meta/lsp_allowlist.json` | missing file → null (no caching — DATA edits apply next result) | [x] |
| `lsp_filter.applyLspAllowlist` | suppressed entries vanish from text+metadata; survivors byte-preserved (incl. multi-line `\u00a0` messages, block order, headers, trailing newline) | fail-open → null on: desync (text ERROR line w/o metadata entry), `WARNING [..]` renders, missing header, missing separator, non-severity-1 entries never suppressed | [x] |

## Stage 2 — Integration
- Recorded live fixtures (opencode.db, pyright 1.1.408):
  - **Sample A** — edit of `main_controller.py` (this-file, 4 errors, 2 codes):
    full seed → `text == "Edit applied successfully."`, `diags == {}`, `dropped == 4`.
  - **Sample B** — write with `tui/provider.py` (5) + `main_controller.py` (4) +
    `rag_v2_tools.py` control (1): full seed → 9 dropped, control block
    byte-identical; provider-only allowlist → 5 dropped, the other two blocks
    byte-preserved.
- Planted-new-error acceptance: extra `reportGeneralTypeIssues` entry at a new
  position in `main_controller.py` SURFACES (alone in its block, header kept,
  trailing-newline variant byte-preserved) while the 4 seeded errors vanish.

## Stage 3 — System (use-case driven)
- Registration chain: `omt_enforcer.ts` after-hook → `lspAfterEdit` (source
  pins: import + call present; `lsp_filter.ts` in e2e `HARNESS_FILES`;
  `.meta/lsp_allowlist.json` seed == live noise cluster).
- Dogfood (this feature's own artifacts): `new_feature.py implementation` /
  `testing --feature feature_090.scaffolds_and_lsp_allowlist` created the
  phase docs this report lives in — the §3.11 mis-creation class
  (wrong root / never created) is impossible by construction.
- Stray repair validated: repo-root `6.testing/` (feature_089's mis-created
  report) relocated to the canonical path; `harnessc check` root_allowlist
  hygiene error gone.

## Evidence

```
$ uv run pytest tests/scripts/omt/test_scaffolds_lsp_allowlist.py -q
25 passed in 0.74s
$ uv run scripts/omt/harnessc.py check && uv run scripts/omt/harnessc.py build
harnessc: check OK — 265 records, 0 errors        (nav_index 64956/65536 OK)
harnessc: build OK — 265 records → 5 projections
$ uv run pytest tests/scripts/omt/test_omt_harness_e2e.py -q
1 passed in 0.94s                                 (receipt refreshed post-registration)
$ uv run pytest -q
2198 passed, 10 warnings in 171.15s (0:02:51)     (2173 baseline + 25 new; 0 failed)
```

Live-noise seed recorded here: `src/agentx/ui/screens/main/main_controller.py`
→ `reportArgumentType`, `reportAttributeAccessIssue`;
`src/agentx/ui/tui/provider.py` → `reportMissingImports` (pyright 1.1.408).
