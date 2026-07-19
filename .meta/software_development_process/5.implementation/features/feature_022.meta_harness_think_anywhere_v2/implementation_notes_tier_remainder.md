# Implementation Notes — feature_022 Tier Remainder (B2 + E1 + E2)

> **Date:** 2026-07-18
> **Design:** `design_004_tier_b2_e1_e2.md` + `operation_spec_tier_b2_e1_e2.md`
> **TDD:** RED 16F → GREEN 16/16 → refactor no-op → cycle closed via `omt_complete`

---

## What shipped

### B2 — `omt_think_suggest{path, top?}` (`.opencode/plugin/omt_think.ts`)
- Module-local `SITE_RANK` (Assign 1 > Return 2 > Expr 3 > If 4 > AugAssign 5, keep-in-sync
  comment with the embedded script) + `SUGGEST_PY_SCRIPT` (stdlib `ast`, emits
  `[{line, end, kind}]` JSON via `end_lineno`).
- Subprocess: `execFileSync("uv", ["run","--no-sync","python","-c",SCRIPT,abs])`, 60s
  timeout, array argv (H3-safe). `--no-sync`: existing venv only, never network.
  Any spawn/parse failure → clean refusal string carrying the last stderr line
  (fail-open; the tool is advisory and never blocks).
- Ranking `(rank, line)`; coverage exclusion via anchored `THOUGHT_PATTERN` at
  site.line ± 1 (excluded count reported); `top` default 5 clamped [1, 20].
- Output: numbered `L<line> <Kind> → insert after L<end>: \`<preview>\`` lines +
  `omt_think{path, line:<end>}` / `after:` footer (unique-match caveat).
- **end_lineno is the splice-safe insertion line** — live smoke on
  `main_screen.py` suggested `DEFAULT_CSS = """` (L60) as *insert after L74*
  (after the closing quotes): the multi-line-string case that caused F1's
  production accident is safe by construction.
- Read-only: no target writes, no index writes, no ledger records (test 8 pins).

### E1 — `omt_think_reindex{path?}` (`.opencode/plugin/omt_think.ts`)
- F8 strategy: **consume** the index via drift-repair (grep stays the gate's source
  of truth; anchors + verify history are index-only value).
- Dispositions: dedupe latest-wins per `path:line` → keep (same line+text+cat) /
  repair (unique text+cat match elsewhere; gains `repaired_from`) / drop (file
  missing, text vanished, or ambiguous >1 — no silent retarget, B1 philosophy).
- Verify records pruned when their slot loses its add-record; unknown kinds and
  out-of-filter records pass through untouched; unreadable files → path skipped
  (records kept, counted). Rewrite via the `reconcileIndex` `writeFileSync` pattern.
- Report: `kept K, repaired R, dropped D, verify-pruned V[; skipped S]` + ≤10
  repair detail lines. Idempotent (live-verified: 693→57 records on the real
  2026-07-16 test-polluted index — dropped 625 dead records, pruned 11 zombie
  verifies; second run all-keep).

### E2 — theory-doc fixes (`.meta/doc/harness/think_anywhere_langchain.md`)
- **F10:** closed paren `P(c | x, s)` (annotation caret line widened to match).
- **F11:** §7 rewritten — `build_sampler(temperature)` (ignored `k` param dropped);
  `pass_at_k(problem, n=20, k=5)` samples n ≥ k, returns unbiased
  `1 − math.comb(n−c, k)/math.comb(n, k)`; n=k degenerate case documented;
  naive-ratio caveat reworded (no literal old-expression text).
- **F12:** §8 rewritten — real per-block attribution: split raw output on
  `<thinkanywhere>` boundaries, parse each code prefix, descend to the innermost
  last statement (body/orelse/finalbody), histogram attributed node types;
  unparseable prefix → `"unattributed"` bucket (best-effort, documented).
- **F13:** §3 gains strip-safety warning (mid-statement token-merge example) +
  `assert_strip_safe` snippet (fence kept OUTSIDE the blockquote so the E2.R5
  extraction guard parses it); §7 gains sandbox warning (test_fn executes model
  code); §6 dead `stream_think_anywhere` stub deleted (`stream_raw_then_parse` kept).

### Wiring
- Factory tool map 4→6 (one literal — e2e:190 + feature_021:89 assert it);
  `opencode.jsonc` gains `"omt_think_suggest": "allow"`, `"omt_think_reindex": "allow"`.
- `_think_runner.mjs` exposes both new tools.

## Deviations / decisions
- **Chunked plugin edits instead of ONE write** (design's batching rule): the Write
  tool repeatedly aborted on large payloads in-session (small payloads fine).
  Sequence used: factory-map line → jsonc allows → e2e receipt refresh → suggest
  section → receipt → reindex section → receipt → header comment → receipt.
  The guard permits edits when receipt ≥ mtime; every chunk verified by a passing
  e2e between edits. One transient broken-plugin window existed (factory referencing
  not-yet-defined tools between chunk 1 and 3) — e2e is static-literal so it stayed
  green; final state fully validated by the 246-test harness set.
- **Coverage window ±1** around the site's first line — matches insertion semantics
  (thoughts land directly above a statement or after its first line).

## Gotchas for future tiers
- Large `write` payloads aborted in this environment; small chunked `edit`s +
  receipt refreshes are the working fallback for guarded files.
- The E2.R5 extraction guard requires ```python fences OUTSIDE blockquotes
  (`> ` prefixes break `ast.parse`).
- A marker string used in a *caveat* sentence still trips absence-asserts —
  keep old-expression literals out of the fixed doc entirely.
