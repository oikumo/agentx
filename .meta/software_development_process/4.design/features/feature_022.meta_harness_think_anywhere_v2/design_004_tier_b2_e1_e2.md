# Design 004: Think Anywhere V2 — Tier Remainder (B2 Suggest + E1 Index Strategy + E2 Theory-Doc Fixes)

> **Date:** 2026-07-18
> **Analysis:** `analysis_004_tier_b2_e1_e2.md` (requirements B2.R1–R6, E1.R1–R6, E2.R1–R5, C1–C8)
> **TDD:** major_feature Programming → auto-TDD (testlist → red → green → refactor)
> **Batching rule (C5):** `omt_think.ts` gets ONE write carrying both new tools;
> the two tool-map literal asserts (e2e:190, feature_021:89) are updated during the
> RED-phase test bootstrap (tests hat) so the post-write e2e receipt refresh passes
> immediately.

---

## Components / surfaces affected

| Surface | Change |
|---|---|
| `.opencode/plugin/omt_think.ts` | +`omt_think_suggest`, +`omt_think_reindex` tools; module-local helpers `rankSitesPy`, `reindexRecords`; factory tool map 4→6 (ONE write) |
| `opencode.jsonc` | +`"omt_think_suggest": "allow"`, +`"omt_think_reindex": "allow"` |
| `.meta/doc/harness/think_anywhere_langchain.md` | F10–F13 fixes (E2) |
| `tests/.../feature_022.../test_omt_think_v2_tier_remainder.py` | NEW suite (16 tests) |
| `tests/.../feature_022.../_think_runner.mjs` | expose the 2 new tools |
| `tests/scripts/omt/test_omt_harness_e2e.py:190` | literal → six tools (RED-phase edit) |
| `tests/features/feature_021.../test_omt_think.py:83-89` | literal+name → six tools (RED-phase edit) |

No `omt_enforcer.ts` changes (analysis §5).

---

## 1. B2 — `omt_think_suggest{path, top?}`

### 1.1 Semantics (pinned from analysis B2.R1–R6)
Read-only advisor. Ranks candidate `TA:` insertion sites in a `.py` file by the
paper's entropy table **Assign(1) > Return(2) > Expr(3) > If(4) > AugAssign(5)**,
tie-break source order; excludes already-covered sites; never writes anything.

### 1.2 AST extraction (`uv run python`, stdlib only)
Embedded script passed inline via `execFileSync("uv", ["run", "--no-sync", "python", "-c", SCRIPT, absPath])`
(array argv — H3-safe, no shell; `--no-sync`: use the existing venv, never hit the network;
60s timeout, stdio pipe). Emits one JSON array to stdout:

```python
import ast, json, sys
RANK = {"Assign": 1, "Return": 2, "Expr": 3, "If": 4, "AugAssign": 5}
tree = ast.parse(open(sys.argv[1], encoding="utf-8").read())
out = [{"line": n.lineno, "end": n.end_lineno, "kind": type(n).__name__}
       for n in ast.walk(tree)
       if type(n).__name__ in RANK and getattr(n, "lineno", None)]
print(json.dumps(out))
```

- `end_lineno` (py3.8+) is the insertion-safe line: inserting after `lineno` of a
  **multi-line** statement would splice inside brackets (A3 covers only strings/fences).
  Suggestions therefore carry `insertAfter = end`.
- Failure modes → clean refusal strings (never throw): spawn error / non-zero exit /
  stderr `SyntaxError` → `⛔ TA: suggest refused — '<rel>' is not parseable Python
  (<first stderr line>)`; `uv` missing → same class with the spawn error message.

### 1.3 Ranking + coverage exclusion (TS side)
- Sort by `(RANK[kind], line)`; RANK map duplicated TS-side (single source is fine —
  the python script already filters to the 5 kinds; TS sorts by the same priority
  via a local const map, keep-in-sync comment).
- **Covered** = a real thought line (anchored `THOUGHT_PATTERN`, module const reused)
  exists at `line-1`, `line`, or `line+1` of the site's first line (thought placed
  above the statement or directly after its first line). Excluded sites are counted
  and reported, not listed.
- Take `top` (default 5; clamp 1..20, `Math.floor`).

### 1.4 Output (deterministic, test-asserted)
```
💡 TA: suggest — <rel>: <N> candidate site(s), <M> already covered.
 1. L<line> <Kind> → insert after L<end>: `<preview>`
 ...
→ omt_think{path:"<rel>", line:<end>, thought:"..."}  (or after:"<preview>" — unique-match caveat)
```
- `preview` = first source line of the statement, whitespace-collapsed, 60-char cap
  (reuse B1's preview convention).
- Zero candidates → `💡 TA: suggest — <rel>: 0 candidate sites (<M> covered). Nothing to suggest.`
- Non-`.py` → `⛔ TA: suggest refused — ranking is Python-AST-based (paper's table); got '<ext>'.`
  Protected/missing → same refusal strings as `omt_think` (reuse code path shape).
- No index writes, no consult records, no target writes (B2.R4).

## 2. E1 — `omt_think_reindex{path?}`

### 2.1 Semantics (pinned from analysis E1.R1–R6)
Reconciles `thoughts.jsonl` against live files. Add-records (no `kind`) get a
disposition; verify records (`kind:"verify"`) are pruned when their slot loses its
add-record. Unknown future kinds pass through untouched.

### 2.2 Disposition algorithm (module-local `reindexRecords`)
1. Read index (`readThoughtsIndex` reused). If `path` given, only records with that
   rel are candidates; all others pass through.
2. Dedupe adds by `path:line` — latest record (file order) wins; losers count as dropped.
3. Per surviving add-record:
   - File missing/unreadable-or-outside-repo → **drop** (+ its verify records).
     (Un readable file: skip path entirely — records pass through, counted `skipped`.)
   - `lines[line-1]` parses as thought AND `parsed.text === rec.thought` → **keep**.
   - Else search file for lines whose `parsed.text === rec.thought` (and `cat` matches):
     exactly 1 → **repair**: `line` updated, record gains `repaired_from: <old>`;
     0 → **drop**; >1 → **drop** (unresolvable ambiguity — never silently retarget,
     B1 philosophy; agent re-adds).
4. Verify-record prune: drop every verify whose `(path,line)` has no surviving
   add-record (includes repaired-from slots — verify is cheap to regenerate).
5. Rewrite index (same `writeFileSync` pattern as `reconcileIndex`, `\n` joins,
   trailing newline). Repaired records keep original `ts` + all fields.

### 2.3 Output
`🧹 TA: reindex — kept K, repaired R, dropped D, verify-pruned V[; skipped S path(s)].`
+ up to 10 detail lines `<path>: <old>→<new> (<60-char thought preview>)`.
Idempotent (E1.R5): second run reports `repaired 0, dropped 0`.

## 3. E2 — theory doc fixes (`.meta/doc/harness/think_anywhere_langchain.md`)

| Fix | Delta |
|---|---|
| F10 | line 12 → `P(c, s \| x) = P(s \| x) · P(c \| x, s)` |
| F11 | §7 rewritten: `build_sampler(temperature)` (drops ignored `k`); `pass_at_k(problem, n=20, k=5, test_fn)` samples **n**, returns `1 − math.comb(n-c, k)/math.comb(n, k)` + doc note (n=k degenerates to "any-pass"; recommend n ≥ 2k); requires `n ≥ k` (`ValueError`) |
| F12 | §8 rewritten: split raw output on `<thinkanywhere>` boundaries; per block, `ast.parse` the largest parseable code prefix; attribute block to the type of the statement ending that prefix (`tree.body[-1]` walk to last line, best-effort, documented); histogram attributed types; unparseable prefix → `"unattributed"` bucket |
| F13 | §3: post-strip `compile()` validation snippet + **mid-statement merge risk** warning (`x = fo<ta>…</ta>o(1)` → `x = oo(1)`); §7: **sandbox warning** (test_fn executes model code — container, no secrets, resource limits); §6: delete dead `stream_think_anywhere` stub, keep `stream_raw_then_parse` |
| Guard | every ```python fence must `ast.parse` (E2.R5 — pinned by test 16) |

## 4. Test plan (TDD test list — suite `tests/features/feature_022.meta_harness_think_anywhere_v2/test_omt_think_v2_tier_remainder.py`)

Infra: extend `_think_runner.mjs` tool map with `omt_think_suggest`, `omt_think_reindex`
(tests-hat bootstrap via `omt_skip{scope:tests}` — C6). Same subprocess pattern as
Tier C (node runner, `cwd=REPO_ROOT`, tmp_path fixtures, JSON-decoded string asserts).

| # | Test | Asserts |
|---|---|---|
| 1 | suggest_ranking_order | fixture with Assign/Return/Expr/If/AugAssign → output order = paper rank |
| 2 | suggest_top_clamp | `top:2` → exactly 2 sites; `top:0`/huge → clamped |
| 3 | suggest_excludes_covered | thought adjacent (±1) to a site → excluded; covered count reported |
| 4 | suggest_refuses_non_py | `.ts` fixture → refusal naming ext |
| 5 | suggest_refuses_protected_and_missing | protected rel + nonexistent → refusal strings |
| 6 | suggest_unparseable | syntax-error `.py` → clean refusal, no crash (exit 0) |
| 7 | suggest_multiline_end | multi-line call site → `insert after L<end>` = end_lineno, not first line |
| 8 | suggest_read_only | target bytes + index file unchanged after call |
| 9 | suggest_zero_candidates | pure-comment/pass file → "0 candidate sites" message |
| 10 | reindex_keep_idempotent | live at-line record → kept; second run all-keep |
| 11 | reindex_repairs_drift | lines inserted above thought → record repaired old→new, `repaired_from` set, old-slot verify pruned |
| 12 | reindex_drops_dead_files | record for nonexistent path (+its verify) dropped |
| 13 | reindex_drops_vanished | thought text removed from file → record dropped |
| 14 | reindex_path_filter | only the given path's records processed |
| 15 | reindex_ambiguous_drops | thought text duplicated in file → record dropped (no silent retarget) |
| 16 | doc_python_blocks_parse_and_fixed | every ```python fence `ast.parse`s; `math.comb` present; `passed / k` gone; closed paren; "sandbox" warning present; `stream_think_anywhere` stub gone |

RED-phase edits outside the new suite (tests hat, C2): e2e:190 literal →
`tool: { omt_think, omt_think_list, omt_think_remove, omt_think_verify, omt_think_suggest, omt_think_reindex }`;
feature_021:83-89 literal+rename `..._with_four_tools` → `..._with_six_tools`;
e2e jsonc assert gains the two new `"allow"` lines (extend :198 area).

Regression floor (C7): Tier A 15, B1+D1 19, C 22, 021 30 — all green post-GREEN.

## 5. Risks (from analysis §6, design responses)

| Risk | Design response |
|---|---|
| uv/python unavailable | fail-open refusal string (§1.2); advisory tool never blocks |
| duplicate-statement anchors unusable with `after:` | output leads with numeric `line:` guidance; caveat printed (§1.4) |
| reindex data loss | drop rules mirror `reconcileIndex`; ambiguity → drop (safe); idempotence tested (test 10) |
| doc code regresses | test 16 pins parse-ability + fix markers |

## 6. Token-budget note

Suggest output ≤ top(20) lines + header/footer; reindex detail ≤ 10 lines —
mirrors list/digest caps (token-minimal philosophy unchanged).
