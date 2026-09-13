# Analysis — feature_090.scaffolds_and_lsp_allowlist (mh8 T2-7)

> **Origin:** mh3 P3-10 + P3-11 (Phase-C signal hygiene), condensed into mh8 T2-7.
> **Task type:** minor_feature (§12 decl-only). D5 overlap-clear: nothing shipped
> touches `new_feature.py` subcommands or LSP-diagnostic filtering (grep: no
> `lsp`/`diagnostic` refs in scripts/omt or .opencode outside tsserver noise).

## Problem 1 (P3-10) — phase-artifact scaffolds

`new_feature.py` scaffolds only `2.requirements/features/<slug>/{FEATURE.md,plan/PLAN.md}`.
The later-phase artifact paths (`5.implementation/features/<slug>/impl_notes.md`,
`6.testing/features/<slug>/test_report.md`) are hand-typed every session — and drift
happens: **feature_089 shipped with its CURRENT_STATE auto-log pointing at
`6.testing/features/feature_089.conventions_and_lints_structural_pin_date_literal/test_report.md`,
which does not exist on disk** (§3.11 mis-creation class: wrong root / never created).

Shapes verified on disk:
- `6.testing/features/<slug>/test_report.md` — canonical name (075–088 all use it);
  template exists: `.meta/templates/test_plan.md` ("Test Report: {{TITLE}}",
  `{{SLUG}}` placeholders — currently unused by any scaffolder).
- `5.implementation/features/<slug>/impl_notes.md` — canonical per
  `.meta/software_development_process/META.md:87` (029/kb_akb); TDD-era features
  used `implementation_001_<topic>.md` (035/050) — keep `impl_notes.md` default.
- Neither phase dir exists for features ≥ 060 (only 059-and-older have
  5.implementation dirs) — scaffolding is currently pure manual labor.

## Problem 2 (P3-11) — known-LSP-error allowlist

opencode (`"lsp": true` in opencode.jsonc) runs Pyright (cached at
`~/.cache/opencode/packages/pyright`, v1.1.408) and appends LSP diagnostics to
edit/write tool results. Contract pinned from live evidence:

1. SDK (`@opencode-ai/plugin` 1.17.11 `index.d.ts`): `tool.execute.after` receives
   `output: { title: string; output: string; metadata: any }`; documented
   mechanism is **mutate output in place** (same idiom as `output.args` in before).
2. Recorded tool results (opencode.db) show the exact render:
   - text: `"Edit applied successfully.\n\nLSP errors detected in this file, please fix:\n<diagnostics file=\"/abs.py\">\nERROR [157:55] <msg>\n</diagnostics>"`
     (variant: `"LSP errors detected in other files:"`; `Wrote file successfully.`)
   - `metadata.diagnostics`: `{ "<abs path>": [ { range:{start:{line,character}}, message, severity(1=err), code, source:"Pyright", codeDescription } ], ... }`
     — related files appear with empty arrays.
3. Plugin after-hook ordering: `omt_enforcer.ts` after-hook runs
   sessionBootstrap → trackRead → injectThoughtsOnRead → runAfterGates; a filter
   step slots in before/independent of these (fail-open).

**Noise cluster is live TODAY** (pyright 1.1.408 on the two mh3-named files, 9 errors):
- `src/agentx/ui/screens/main/main_controller.py`: `reportArgumentType` ×3 (L199/244/268)
  + `reportAttributeAccessIssue` ×1 (L269) — feature_024 console-partner typing.
- `src/agentx/ui/tui/provider.py`: `reportMissingImports` ×5 (L76–124) — lazy-import
  pattern (`agentx.ui.tui.adapters.*_adapter` imported inside methods).

Cost: every edit to these (hot) files re-prints the same 4–9 errors → token noise
+ attention misdirection; NEW errors drown in the known ones.

## Approach

- **P3-10:** `new_feature.py` gains subcommands `testing` / `implementation`
  (`--feature <slug>`, `--dry-run`); argv pre-scan keeps the legacy positional
  `name` path byte-identical (phase_gate.ts guidance text + tests unaffected).
  Validation: slug must exist under `2.requirements/features/`; refuse overwrite.
  Paths derived from a new module global `PROCESS_ROOT` (monkeypatchable, test idiom
  `_mod("new_feature")` + `main(argv)` per test_project_lifecycle.py).
- **P3-11:** new lib module `.opencode/lib/enforcer/lsp_filter.ts` — pure
  `filterLspDiagnostics(env, input, output)`:
  1. Applies to edit/write/patch completions whose `metadata.diagnostics` has
     severity-1 entries.
  2. Loads allowlist `.meta/lsp_allowlist.json` (`{ "<repo-rel path>": ["<code>", ...] }`).
  3. Drops allowlisted `(file, code)` entries from `metadata.diagnostics` (abs→rel
     mapping via env.directory).
  4. String-surgery on the trailing `<diagnostics>` blocks in `output.output`:
     line↔metadata entries are joinable via `range.start.line+1:character+1` +
     message equality; suppressed lines removed, empty blocks dropped, orphaned
     header line removed. Fail-open on ANY surprise (leave output untouched).
  5. Registration: one call in `omt_enforcer.ts` after-hook + module added to
     `HARNESS_FILES` (e2e) — receipt round-robin respected (each harness file one
     edit per round; e2e file itself receipt-EXEMPT).
- Allowlist file `.meta/lsp_allowlist.json` is DATA (tracked, git-reviewed), NOT in
  `@var.harness_paths` → no receipt round-robin to update it; seeded with the 9
  live entries above.
- Static allowlist tradeoff accepted (mh3 wording): a NEW error with the SAME
  (file, code) pair stays hidden; different code/message in the same file surfaces.
  The planted-new-error golden uses a different code.

## Acceptance (mh3 §3.11/§3.12 verbatim + goldens)

1. `new_feature.py testing|implementation --feature <slug>` create the correct
   `.meta/software_development_process/<phase>/features/<slug>/` paths + stubs;
   repo-root mis-creation impossible; unknown slug → error rc=2.
2. Pre-existing 4–9 errors on main_controller.py / tui/provider.py no longer appear
   in post-edit reports; a planted new error does. Goldens: bun-probe pure-function
   tests on recorded output shapes (from opencode.db samples) + source pins +
   e2e receipt; live pyright seed recorded in the test report.
