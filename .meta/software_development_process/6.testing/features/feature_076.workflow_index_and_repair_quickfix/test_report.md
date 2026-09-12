# Test report — feature_076.workflow_index_and_repair_quickfix (T1-6)

> Date: 2026-09-12 · Type: minor_feature · Status: PASS

## Scope verified

- Contradiction repair: `meta_harness_evolution.md` step 6 now targets `.meta/META_HARNESS.omt` + `harnessc.py build` (no more `./meta/META_HARNESS.md`).
- Machine authority markers (`<!-- authority: follow|override -->`) on line 1 of the 6 manifest-backed workflow files.
- `harnessc check_workflows`: (a) listed file without valid marker → error; (b) manifest row without file → error; (c) on-disk workflow not in its subject manifest → drift **warning** (live tree: `meta_harness_development_self_evaluation.md` flagged — deliberate, left for a later repair decision); (d) projection-edit instruction (update/edit/modify/write META_HARNESS.md/AGENTS.md without safeguard wording) → error pointing at the canonical `.omt` source; wrong path `meta/META_HARNESS.md` (no leading dot) → error.
- `harnessc workflows [--subject X] [--plan W]`: list returns exactly the 6 catalog workflows with authority + path; `--subject` filters; `--plan` prints the LAST non-Rules/non-Result strategy section (so `# … rules` blocks don't win).

## Tests

- New: `tests/scripts/omt/test_harnessc_workflows.py` — **16 goldens, all green** (live-catalog pins + synthetic-tree negative goldens via `_swap_root` + subcommand surface).
- Boundary e2e: `tests/scripts/omt/test_omt_harness_e2e.py` → **1/1 pass** (validates the staged batch: harnessc.py + test file).
- `harnessc check` → 0 errors, 1 warning (intentional drift flag above); all budgets green.
- Full suite (`uv run pytest tests/ -q`, live-opencode file deselected per user direction — it times out spawning a real `opencode run` subprocess, environmental, unrelated): **2079 passed / 1 failed**; the failure is the pre-existing, known `feature_059.test_tight_budgets_unchanged` (071–073 WORK.md drift, documented in the pause note — left untouched as instructed).

## Notes

- LSP reports 6 pre-existing diagnostics in `harnessc.py` (lines ~430/1495/1869/1893/2000) older than this change; untouched.
- `harnessc workflows` runs corpus-free (short-circuited in `main()` like `stage`/`init`) and ignores `.workflows`-absent template trees in `check_workflows` via `check_tree` no-op (D6).
