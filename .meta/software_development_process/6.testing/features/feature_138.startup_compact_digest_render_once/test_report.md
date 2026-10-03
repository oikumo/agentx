# Test Report — feature_138.startup_compact_digest_render_once (mh16 slice 2)

> Task type: minor_feature · 2026-09-28 · RED (4 behaviors, `test_startup_digest.py` + bun `startup_digest.check.ts`) → GREEN (`.opencode/plugins/startup_table.ts`: `normalizeProbe`, `probeDigest` arg, shared `renderTables`) → REFACTOR (green held) → DONE. TDD cycle via `omt_tdd`.

## Verdict

**PASS.** Slice battery **4 passed** (`tests/scripts/omt/test_startup_digest.py`, bun-executed TS behavior + source pins). Full repo suite: **2108 passed, 2 skipped, 2 deselected, 0 failed**. `harnessc check` + `build`: **0 errors**, all budgets OK.

## What was verified

| Behavior | Test | Result |
|---|---|---|
| digest renders byte-identical menu | test_digest_renders_identical | PASS — markdown equal; metadata options + suggested_id equal |
| legacy envelope unchanged, malformed fails open | test_legacy_envelope_unchanged_and_digest_fail_open | PASS — envelope render intact; bad digest → file-only |
| digest call-turn bytes | test_digest_call_turn_bytes | PASS — measured below |
| STARTUP pins digest + verbatim | test_startup_text_pins_digest_and_verbatim | PASS — AGENTS.md carries both; single shared renderer pinned |

## Measured effect (bytes, not relabeled as tokens)

- Call-turn arg: full brief-probe envelope **583 B** → compact digest **81 B** (**7.2×**, conservative floor — non-brief probes are far larger).
- Render output unchanged (identical D19 OptionID map, pool/lanes/staleness preserved); the saving is the eliminated re-serialization roundtrip + zero hand-render variance (render-once: agent relays tool output verbatim per the new STARTUP line).
- Honest-reporting note: token-denominated savings require labeled-session measurement (mh13 contract); the byte figures above are transport sizes.

## Budget discipline (deliberate, dated)

- `@budget agents_md` 3584→3648 (STARTUP sentence +62B → 3575 live; diet headroom restored).
- `@budget nav_index` 67584→67648 (nav record +64B → 67539 live).
- `NAV_INDEX_CEIL` test pin 67475→67539 with payback note (re-pin convention).
- All changes carry same-edit rationale comments; `harnessc build` projections regenerated (AGENTS.md carries digest-first + verbatim).

## Supporting fix (repo hygiene, unblocked DONE)

- Full-suite red `test_cli_status_matches_live`: `check_tree`'s swapped-REPO_ROOT window leaked tmp sys.path entries + tmp-loaded modules (`lean_start_swap` resolved to the init-emitted copy). Fixed in `harnessc._restore`: scrub swapped-root path entries and modules on restore. Verified polluter→victim order green, then full suite 2108/0.

## Boundary

- `probeJson` path untouched (backward compat); `startup_table` stays non-harness (no registry/perm churn); lean_start_v1 variant mechanism untouched (mh14 keep-control stands).
- TS behavior runs under bun (repo `.opencode/node_modules` present); pytest skips if bun absent.

## Next

- Observe digest adoption in real sessions via `omt_session profile` (first-5 input) when the new STARTUP line goes live; token-denominated claim only after measured sessions.
