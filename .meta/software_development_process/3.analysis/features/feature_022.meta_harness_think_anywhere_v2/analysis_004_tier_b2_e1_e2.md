# Analysis — feature_022 Tier Remainder (B2 + E1 + E2)

> **Date:** 2026-07-18
> **Tier scope:** B2 `omt_think_suggest` (placement intelligence), E1 index strategy
> (consume or delete), E2 theory-doc fixes (F10–F13)
> **Predecessors:** analysis_001 (Tier A), analysis_002 (B1+D1), analysis_003 (C) — all shipped
> **Evidence policy:** every claim below re-verified against the live tree on 2026-07-18.

---

## 1. B2 — `omt_think_suggest{path}` (fixes the placement half of the intent gap)

### 1.1 Paper requirement
FEATURE.md §Tier-B: *"`omt_think_suggest{path}`: AST-walk ranking candidate sites using the
paper's table (Assign > Return > If…) — mechanical high-entropy position targeting."*

### 1.2 Evidence (re-verified)
- Paper's entropy table lives in the theory doc `.meta/doc/harness/think_anywhere_langchain.md:47-53`:
  **Assign (1) > Return (2) > Expr (3) > If (4) > AugAssign (5)** — Python `ast` node type names.
- `omt_think.ts` already shells out via `execFileSync` (grep, H3-safe array argv) — a Python
  subprocess is the same operation class. `uv run python -c "import ast"` verified working on
  box (stdlib `ast` only — no deps).
- Test infra: `_think_runner.mjs` is driven by pytest with `cwd=REPO_ROOT` (real repo),
  tools receive absolute tmp paths → a `uv run python` subprocess inherits the repo cwd and
  resolves the project venv deterministically in both production and tests.
- True token entropy requires a model — not available to a mechanical plugin. B2 is the
  documented mechanical proxy: **rank by the paper's node-type priority, tie-break by source
  order**. Deviation from "entropy" is explicit and recorded here.
- AST-walk is inherently string-safe (walks statements, never lines inside string literals) —
  composes with A3's F1 guard by construction.
- Language scope: the paper's table is Python-AST node types. Non-`.py` extensions → refusal
  with a clear message (mirrors B1 `symbol:` refusal philosophy, A2 deny-unknown philosophy).
- Current production adoption: exactly one thought-carrying source file
  (`src/agentx/ui/tui/screens/main_screen.py`) — B2's near-term value is agent workflow
  (suggest-then-insert) on any file, exercised via fixtures in tests.

### 1.3 Requirements
- **B2.R1** New tool `omt_think_suggest{path, top?}` — ranks candidate insertion sites in a
  `.py` file by the paper's table; returns up to `top` (default 5) sites as
  `line | kind | preview` plus a ready-to-use `after:` anchor string per site.
- **B2.R2** Real AST: `uv run python` subprocess running an embedded stdlib-`ast` script that
  emits JSON `[{line, kind}]`; fail-open error string (never a crash) if python/uv is
  unavailable or the file is unparseable (SyntaxError → clean refusal, file untouched).
- **B2.R3** Sites already covered by a `TA:` line (immediately above or below the statement)
  are excluded, with the excluded count reported — suggestions target *uncovered* sites.
- **B2.R4** Non-`.py` → refusal naming the extension; protected/missing file → same refusals
  as `omt_think`. Read-only: never writes the target file or the index.
- **B2.R5** Output composes with B1: each suggestion's anchor is the stripped statement text
  (60-char preview rule reused) — directly passable as `omt_think{after:…}` (unique-match
  caveat: identical statements are ambiguous by B1 design; the suggest output shows line
  numbers precisely so the agent can fall back to `line:`).
- **B2.R6** Module-local helper (no named exports — DEFECT-A class); tool registered in the
  default factory's tool map; `opencode.jsonc` gains `"omt_think_suggest": "allow"`.

## 2. E1 — Index strategy: consume via drift-repair (closes F8 residual)

### 2.1 Evidence (re-verified)
- Index read-consumers shipped in Tier C: digest stale count (`omt_think.ts:585`),
  verify anchor lookup (`:539`), enforcer `staleLinesFor` (`omt_enforcer.ts:272`).
- **Live pollution evidence:** `.meta/.omt/thoughts.jsonl` currently holds dozens of dead
  add-records pointing at `../../../../../tmp/pytest-of-oikumo/...` files (test runs from
  2026-07-16) — files long deleted, records never pruned. No mechanism repairs line drift
  or prunes dead records; `omt_think_verify` only *flags* stale one thought at a time.
- FEATURE.md §Tier-E: *"Index: consume it (gate lookup, drift repair, analytics) or delete it."*

### 2.2 Decision (analysis-level; mechanics in design)
**Consume — do not delete.** The index now carries B1 anchors and C1 verify history that grep
cannot reconstruct; deleting would regress Tier B1/C1 value. Gate lookup stays grep-based
(inline tags are the source of truth — v1 guardrail, unchanged). The missing consumer is
**drift repair**, which also delivers the analytics surface (repair report = counts).

### 2.3 Requirements
- **E1.R1** New tool `omt_think_reindex{path?}` — reconciles the JSONL index against live
  files (default: all recorded paths; `path` restricts to one file).
- **E1.R2** Per add-record disposition: live thought at recorded line → **keep**; thought
  text found elsewhere in the same file (unique match) → **repair** line number; file
  missing/outside-repo or thought gone → **drop** (with its verify records, same rule as
  `reconcileIndex`). Duplicate add-records per `(path,line)` → latest wins.
- **E1.R3** Zombie verify records (no surviving add-record at their slot) → pruned.
- **E1.R4** Report = analytics surface: counts `{kept, repaired, dropped, verify_pruned}`
  plus per-repair `path: old→new` detail lines (capped, mirrors list cap philosophy).
- **E1.R5** Idempotent: second run reports all-keep. Fail-open best-effort I/O like all
  index writers; never touches source files. `opencode.jsonc` gains
  `"omt_think_reindex": "allow"`.
- **E1.R6** Test-pollution records (`../../tmp/...` outside-repo paths) are dropped by the
  file-missing rule — verified live as part of Testing.

## 3. E2 — Theory-doc fixes (F10–F13) — `.meta/doc/harness/think_anywhere_langchain.md`

### 3.1 Evidence (re-verified against live doc)
| # | Defect | Live evidence |
|---|--------|---------------|
| F10 | Unclosed paren in core formula | line 12: `P(c, s \| x) = P(s \| x) · P(c \| x, s` |
| F11 | `pass_at_k` returns `passed/k` — not pass@k; `build_sampler(k=…)` ignores `k` | lines 206–229 |
| F12 | `analyze_thinking_positions` docstring claims per-block syntactic attribution; code only histograms AST of *stripped* code | lines 240–259 |
| F13 | Mid-statement strip can change semantics; syntax-only validation; no sandbox warning for `test_fn` executing model code; dead `stream_think_anywhere` stub (`pass` body) | lines 124-127, 180–186, 267–275 |

### 3.2 Requirements
- **E2.R1** (F10) Close the paren: `P(c, s | x) = P(s | x) · P(c | x, s)`.
- **E2.R2** (F11) `pass_at_k(problem, n, k, test_fn)`: sample **n ≥ k** solutions, return the
  unbiased estimator `1 − C(n−c, k)/C(n, k)` via `math.comb`; document the n=k degenerate
  case (estimator → "any pass", high variance; recommend n ≥ 2k…e.g. n=20,k=5);
  `build_sampler` drops the ignored `k` param.
- **E2.R3** (F12) Rewrite `analyze_thinking_positions` to do what the docstring claims:
  attribute each `<thinkanywhere>` block to a syntactic context by parsing the code prefix
  preceding the block (largest parseable prefix; best-effort, documented) and reporting the
  enclosing/last statement's node type per block; histogram over those attributed types.
- **E2.R4** (F13) Parser section: post-strip syntax-validation snippet with an explicit
  **mid-statement merge risk** note (`x = fo<ta>…</ta>o(1)` → `x = oo(1)`) and guidance to
  place blocks at statement/token boundaries; **sandbox warning** that `test_fn` executes
  model-generated code (container/VM, no secrets, resource limits); delete the dead
  `stream_think_anywhere` stub (keep `stream_raw_then_parse`).
- **E2.R5** Every ```python block in the fixed doc must `ast.parse` cleanly — guarded by a
  deterministic extraction test (docs defect class is doc/code mismatch; the test pins it).

## 4. Cross-cutting constraints (carried, re-verified)

- **C1** DEFECT-A: no named tool-object exports from `omt_think.ts` — new helpers module-local;
  tools registered only in the default factory. Structural guard test exists
  (`test_no_named_exports_except_default`) and will cover the enlarged module.
- **C2** e2e literal asserts track the tool map: `tests/scripts/omt/test_omt_harness_e2e.py:190`
  and `tests/features/feature_021.../test_omt_think.py:89` assert the four-tool literal → must
  be updated to six tools (Tier C prior art: update *before* the post-write receipt refresh).
- **C3** `opencode.jsonc` tool permissions: add both new tools (mirrors Tier C's
  `omt_think_verify` addition).
- **C4** `omt_think.ts` carries a `TA:` annotation at EOF (`:607`) → think-gate requires an
  `omt_think_list` consult in-session before editing it (whole-repo consult covers it).
- **C5** harness-e2e receipt rule: batch each plugin's changes into ONE write; refresh receipt
  (`uv run pytest tests/scripts/omt/test_omt_harness_e2e.py -q`) between edits to the same
  guarded file; jsonc edit also guarded.
- **C6** Two-hats TDD: test bootstrap needs `omt_skip{scope:tests}` (TESTLIST blocks tests/ —
  Tier A/B1+D1/C prior art).
- **C7** Regression floor: Tier A 15/15, B1+D1 19/19, Tier C 22/22, feature_021 30/30 must
  stay green (combined harness set 230/230 at Tier C close).
- **C8** `omt_done` strict full-suite unreachable (Tier A gotcha: 3 pre-existing feature_018
  react_screen failures + 2 ledger-window-sensitive tdd_check tests) → phase exit via
  `omt_complete`; verify the 2 state-sensitive tests green post-advance.

## 5. Out of scope (explicit)

- True model-based entropy scoring (needs an LLM in the loop) — B2 is the mechanical proxy.
- Non-Python suggest support (would need per-language AST tooling; B1's `symbol:` regex
  family is insertion-only, not ranking).
- Semantic verification of thought truthfulness (agent's job — C1 boundary, unchanged).
- B2/E1 in `omt_enforcer.ts` — no enforcer changes required by this tier (stale surfacing
  shipped in Tier C; suggest/reindex are operator tools).

## 6. Risks

| Risk | Mitigation |
|------|-----------|
| `uv run python` subprocess unavailable/slow in some env | fail-open error string (B2.R2); suggest is advisory, never blocks |
| Suggest anchors non-unique (identical statements) | line numbers in output; B1 ambiguity refusal already guides (B2.R5) |
| Reindex over-aggressive drop loses verify history | drop only on file-missing/thought-gone (same rule as remove); idempotence test (E1.R5) |
| Doc code blocks regress silently | E2.R5 extraction test pins `ast.parse` on every ```python block |
