# Implementation notes — feature_090.scaffolds_and_lsp_allowlist

> Date: 2026-09-13 · Scaffolded by `new_feature.py implementation` (feature_090).
> mh8 T2-7 (mh3 P3-10 + P3-11, Phase-C signal hygiene).

## What changed

- `scripts/omt/new_feature.py` (P3-10, shipped in the pre-pause session):
  - `testing` / `implementation` subcommands (`--feature <slug>`, `--date`, `--dry-run`)
    scaffolding `.meta/software_development_process/6.testing/features/<slug>/test_report.md`
    (rendered from `.meta/templates/test_plan.md`) and
    `5.implementation/features/<slug>/impl_notes.md` (inline stub, `build_impl_notes_stub`).
  - argv pre-scan in `main()` BEFORE the legacy positional argparse — exact-match
    `argv[0] in PHASE_TARGETS` only, so the legacy `name` path (incl. `--project`
    lifecycle hook) stays byte-identical; unknown-slug + refuse-overwrite → rc=2.
  - New monkeypatchable module global `PROCESS_ROOT` (hermetic-test idiom).
- `.opencode/lib/enforcer/lsp_filter.ts` (P3-11, NEW module):
  - `parseAllowlist` / `loadAllowlist` — read + validate `.meta/lsp_allowlist.json`
    (`{ "<repo-rel path>": ["<pyright code>", ...] }`); null on any surprise.
  - `applyLspAllowlist` (pure) — 3 passes: index severity-1 entries by (file,
    "L:C") position → decide suppressed positions (a position drops only when
    EVERY severity-1 entry at it is allowlisted — twin diagnostics over-show,
    never hide) + build filtered `metadata.diagnostics` → byte-preserving
    surgery on the rendered text section (groups = `ERROR [L+1:C+1]` line +
    multi-line message continuations; suppressed groups removed, emptied
    blocks dropped, all-suppressed section stripped to the base text).
    Fail-open → null on ANY surprise: text↔metadata desync, non-ERROR severity
    renders (`WARNING [..]`), missing header/separator, trailing junk.
  - `lspAfterEdit` (thin entry) — edit/write/patch only; mutates
    `output.output` + `output.metadata.diagnostics` in place (SDK contract);
    never blocks, never throws.
- `.meta/lsp_allowlist.json` (NEW, tracked DATA — not a harness surface): seeded
  with the 9 live pyright-1.1.408 entries — main_controller.py
  (`reportArgumentType` ×3 + `reportAttributeAccessIssue` ×1) and tui/provider.py
  (`reportMissingImports` ×5, lazy-import pattern).
- `.opencode/plugins/omt_enforcer.ts`: ONE registration edit — import + call
  `await lspAfterEdit(env, input, output)` in the after-hook AFTER
  `injectThoughtsOnRead` and BEFORE the `raw` early-return (the filter keys off
  `output.metadata.diagnostics`, not the edited path) + header module list.
- `tests/scripts/omt/test_omt_harness_e2e.py`: `.opencode/lib/enforcer/lsp_filter.ts`
  added to `HARNESS_FILES` (receipt coverage).
- Stray hygiene (found by `harnessc check`, root_allowlist): feature_089's
  mis-created repo-root `6.testing/features/feature_089.../test_report.md`
  (the exact §3.11 defect class this feature eliminates) git-mv'd to its
  canonical `.meta/software_development_process/6.testing/features/` path.
- Goldens: `tests/scripts/omt/test_scaffolds_lsp_allowlist.py` (25 tests —
  see the test report).

## Discipline notes

- Receipt round-robin respected for harness-surface files (ONE edit per file
  per e2e receipt; `uv run pytest tests/scripts/omt/test_omt_harness_e2e.py -q`).
  Registration batch (import + call + header list) + lsp_filter.ts creation +
  HARNESS_FILES entry landed inside ONE receipt round; e2e refreshed after
  (receipt now covers lsp_filter.ts via HARNESS_FILES).
- `uv` only (no bare python/pip/pytest).
- Tests/ canary recorded per D6 ordering (phase → skip → tests) in BOTH the
  pre-pause session and the resume session.
- Render contract pinned from live opencode.db samples (pyright 1.1.408);
  fixtures embedded in the goldens. If opencode's LSP render format changes,
  the strict parser fails OPEN (null → unfiltered output) — update parser +
  fixtures together (TA: thought at lsp_filter.ts).
- `opencode.jsonc` picked up an unrelated runtime permission addition
  (`"sqlite3 *": "allow"`, from the opencode.db evidence queries) — not part of
  this feature's surface; flagged for the user's commit decision.
