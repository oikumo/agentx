# Design 001: Think Anywhere V2 — Tier A Correctness Hotfixes

> **Phase:** Design — `omt_agent_guide.md §2`, §5–§10 | **Feature:** feature_022.meta_harness_think_anywhere_v2
> **Analysis:** `3.analysis/.../feature_022.meta_harness_think_anywhere_v2/analysis_001_tier_a_hotfixes.md`

Tooling/enforcement feature (no MVC++ screen) — same design idiom as feature_021: plugin
functions + pure deciders. MVC++ self-check N/A (no `src/` business code); the contracts that
apply (plugin loader, plain-string ToolResult, execFileSync safety, DEFECT-A no-named-exports)
are unchanged from feature_021 and remain enforced by the existing structural tests.

## Components / surfaces affected

| Surface | Change | Gated? |
|---|---|---|
| `.opencode/plugin/omt_think.ts` | MODIFY: anchored pattern const + excludes, extension map (deny unknown), string-guard, dedup, EOL join, filter fixes; DELETE dead `fileThoughts` | harness-e2e guard |
| `.opencode/plugin/omt_enforcer.ts` | MODIFY: `fileThoughtsIn` uses anchored pattern (one-line change + shared-pattern comment) | harness-e2e guard |
| `tests/features/feature_022.../` | NEW: `_think_runner.mjs` (copy of 021), `_think_gate_runner.mjs` (021 + `file-thoughts` mode), `test_omt_think_v2.py` | tests via TDD |
| `opencode.jsonc`, `AGENTS.md`, `.meta/META_HARNESS.md` | **unchanged** (tool surface and documented tag format are unaffected) | — |

## 1. A1 — Anchored thought pattern (single source, two copies)

```
THOUGHT_PATTERN = "^\\s*(#|//|/\\*|<!--)\\s*TA:"        // grep -E / JS RegExp compatible
```

- Matches exactly the forms `buildThoughtLine` can emit: `#`, `//`, `/*`, `<!--` openers,
  optional indent, optional space before `TA:`. Verified live: 220 → 5 hits (analysis §evidence).
- Stored as a string const so it serves BOTH `grep -E "<pat>"` and `new RegExp(pat)` (JS-side
  checks in `omt_think_remove`, dedup parser). `\s` is a GNU-grep ERE extension — confirmed
  working on the target box.
- **Duplicated** in `omt_think.ts` and `omt_enforcer.ts` (plugins are standalone — no
  cross-imports); each copy carries a `// keep in sync with <other file>` comment. A structural
  test asserts the two copies are byte-identical.
- Application sites:
  1. `omt_enforcer.ts fileThoughtsIn` — `grep -nHE -- THOUGHT_PATTERN <abs>` (add `-E`, swap pattern).
  2. `omt_think.ts grepThoughts` — add `-E`; callers pass anchored patterns only.
  3. `omt_think.ts thinkDigest` — `grepThoughts(THOUGHT_PATTERN, ".")`.
  4. `omt_think_list` — base pattern = `THOUGHT_PATTERN`; category ⇒ `THOUGHT_PATTERN + "\\s*" + esc(cat.toLowerCase()) + ":"`.
  5. `omt_think_remove` line check — `new RegExp(THOUGHT_PATTERN).test(lines[idx])` replaces `includes("TA:")`.
  6. DELETE `fileThoughts` (`omt_think.ts:124-141`) — dead code, third copy of the F3 bug.
- **A1b excludes:** `grepThoughts` gains `--exclude-dir=.venv --exclude-dir=__pycache__`.

Residual FP accepted (analysis): `omt_think.ts:64` prose line matching the anchor — file is
correctly gated anyway (real thought at `:316`).

## 2. A2 — Extension map (explicit; unknown → deny)

`commentSyntaxFor(ext)` (lowercased input):

| Family | Extensions | `{open, close}` |
|---|---|---|
| hash | `.py .toml .cfg .ini .sh .yml .yaml .rb .r .pl` | `{ "#", "" }` |
| slash | `.ts .js .mjs .cjs .tsx .jsx .jsonc .go .rs .java .c .cpp .h .hpp .cs .swift .kt .scala` | `{ "//", "" }` |
| html | `.md .mdx .html .xml .vue .svelte` | `{ "<!--", "-->" }` |
| css-block | `.css .scss .less` | `{ "/*", "*/" }` |
| sql | `.sql` | `{ "--", "" }` |
| `.json` | (existing) | `null` — dedicated refusal message |
| **unknown / none** | everything else | `null` — refusal |

Refusal (existing path, extended text):
`⛔ TA: refused — unsupported file type '<ext>'. Add an explicit mapping in commentSyntaxFor (omt_think.ts, feature_022) only if a real comment syntax exists.`

The false `// default: hash is safe for most text formats` comment is deleted. Denylist
(`.env*`, README.md, uv.lock, LICENSE) is unchanged and evaluated before the extension check.

## 3. A3 — String-context insertion guard

```
function inStringContext(lines: string[], insertAt: number, ext: string): boolean
```

- `ext === ".py"`: over `lines[0 .. insertAt-1]`, count occurrences of `"""` and of `'''`
  (naïve substring count, per delimiter, summed across lines). Odd for either ⇒ inside a
  triple-quoted string ⇒ `true`. Same-line open+close (`"""doc"""`) counts 2 ⇒ outside.
  Known limitation (accepted, analysis): a delimiter inside a single-quoted string fools
  parity — failure direction is *refuse*, which is safe.
- `ext === ".md" | ".mdx"`: count lines in range matching `/^\s*(```|~~~)/`; odd ⇒ inside a
  code fence ⇒ `true`.
- any other ext ⇒ `false` (Tier A scope; `.ts` template literals deferred — documented).

Call site: `omt_think.execute`, AFTER protected/extension/exists checks and AFTER `insertAt`
clamping, BEFORE `splice`. Refusal:
`⛔ TA: refused — insertion point <rel>:<insertAt+1> lies inside a string/code-fence (F1 class: broke Textual CSS via triple-quoted string). Choose a line outside the literal.`

## 4. A4 — Filters, dedup, EOL

- **escapeRegex:** `s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")` — applied to `query` and to the
  category token before pattern interpolation. Dead ternary deleted: `if (query) pattern += ".*" + escapeRegex(query)`.
- **category lowercase:** normalized at insert (`buildThoughtLine`) and at filter
  (`omt_think_list`) — `category.trim().toLowerCase()`.
- **dedup (omt_think):** normalize incoming thought (`\s+→" "`, trim, strip leading `TA:`),
  then scan the target file's lines: for each line matching `THOUGHT_PATTERN`, parse out
  `{cat, text}` (strip comment opener/`TA:`/optional `cat:`/trailing `-->`or`*/`, normalize
  whitespace). Refuse when `(cat, text)` pairs are equal:
  `⛔ TA: refused — duplicate of existing thought at <rel>:<n>.`
- **EOL (omt_think only):** `const eol = content.includes("\r\n") ? "\r\n" : "\n"`;
  `lines = content.split(/\r?\n/)`; write with `lines.join(eol)`. CRLF files get a CRLF
  thought line (no mixed endings); LF files byte-identical to v1 behavior. `omt_think_remove`
  already round-trips CRLF (split("\n") preserves `\r`) — left untouched apart from §1.5.

## 5. Test plan (TDD test list; suite `tests/features/feature_022.meta_harness_think_anywhere_v2/`)

Runners: `_think_runner.mjs` (verbatim copy of feature_021's — invokes the real plugin tools);
`_think_gate_runner.mjs` (feature_021's + mode `file-thoughts <absPath>` →
`JSON.stringify(mod.fileThoughtsIn(path))`).

1. **A1 prose rejection:** file containing prose `"the TA: marker"`, `META:`, `DATA:` lines →
   `omt_think_list{path}` reports 0 thoughts; `fileThoughtsIn` returns [].
2. **A1 real-tag acceptance:** `# TA:`/`// TA:`/`/* TA: */`/`<!-- TA: -->` all detected.
3. **A1 round-trip:** every `commentSyntaxFor` family: insert via `omt_think` → `fileThoughtsIn`
   finds it (gate can never be blind to what think wrote).
4. **A1b excludes:** tmp tree with `TA:` hits under `.venv/` and `__pycache__/` → not listed.
5. **A1 remove-check:** `omt_think_remove` on a prose-mention line refuses; on a real anchored
   line removes.
6. **A1 structural:** `THOUGHT_PATTERN` literal byte-identical in both plugin files.
7. **A2 mappings:** `.go/.rs/.java/.c/.sql/.html` → `//`, `//`, `//`, `//`, `--`, `<!-- -->`.
8. **A2 deny-unknown:** `.xyz` and extensionless paths refused; file bytes unchanged.
9. **A3 py guard:** insert at a line inside a triple-quoted string (F1/main_screen repro)
   refused, file unchanged; insert after a closed docstring allowed.
10. **A3 md guard:** insert inside a ```` ``` ```` fence refused; outside allowed.
11. **A4 category case:** `category:"Gotcha"` stored as `gotcha:`; filter `category:"GOTCHA"`
    matches it.
12. **A4 query escaping:** `query:"a.b["` is literal — no grep error, matches only literal text.
13. **A4 dedup:** identical (path, thought) refused with pointer to existing line; same text
    with different category allowed.
14. **A4 CRLF:** CRLF fixture → inserted line ends `\r\n`; no LF-only lines introduced.
15. **Regression:** feature_021 suite (30 tests) stays green.

## 6. Risks

| Risk | Mitigation |
|---|---|
| Pattern blind to a form think can emit → silent un-gating | test 3 (round-trip every family) |
| `\s` non-portable ERE | GNU grep confirmed on box; CI is same image |
| Parity heuristic false-refuses valid sites | safe direction; message explains; user picks another line |
| Two pattern copies drift | test 6 (byte-identical assertion) |

## 7. Token-budget note

Digest/list shrink from 220 polluting hits to the true count (today: 4 thoughts). Refusal
messages stay ≤2 lines. No new session.start output. Net token effect: **negative** (saves).
