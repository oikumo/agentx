# Test report — feature_088.g_kb_per_file_read_recency (T2-5)

Date: 2026-09-13 · Type: minor_feature · Project: meta_harness_8

## Shipped

- **NEW substrate:** `session_state.ts` — `reads: Map<session, Map<rel, ms>>` + `recordRead` + `hasRecentRead` (window = `UNLOCK_WINDOW_MS`, session-matched with cross-session drift fallback; null rel → false). Explicitly NOT a mirror of think-consult `recent_consults` (mh3 R2).
- **Instrumentation:** `nav_gate.trackRead` — after-hook on completed `read` tool calls, records `{rel: now}`; fail-open throughout; ignores non-read tools; tolerates missing/array/odd `filePath` shapes; sessionless reads land in the `""` bucket.
- **Predicate:** `gate_driver.ts SESSION_FLAGS.kb_consulted` — order: session flag → fast-path → sticky → `hasRecentRead(reads, session, rel)` (per-file, cheapest-last among ledger-free checks). Session-wide semantics untouched for non-read paths.
- **Wiring:** `omt_enforcer.ts` after-hook calls `trackRead` before thought-injection.

## Goldens (7, all green) — `tests/scripts/omt/test_gkb_read_recency.py`

Hermetic bun probes drive TS modules directly; wiring pins assert source.

- same-file recent read passes; other file blocks; never-read blocks; null rel blocks
- expired read blocks; fresh read passes; cross-session drift fallback passes
- trackRead records only reads (edit ignored; array filePath handled; malformed args no-crash)
- wiring pins: substrate exports, nav_gate trackRead shape, gate_driver consults `hasRecentRead(reads, session, rel)`, enforcer wires after-hook

## Acceptance (T2-5)

- read-then-edit same turn passes g.kb for THAT file — ✅
- never-read file still blocks — ✅
- NOT a recent_consults mirror — ✅ (separate substrate, pinned)

## Checks

- `harnessc check` — 263 records, 0 errors
- `harnessc build` — OK, 5 projections; budgets green (no tool-surface change → no re-pin)
- Full suite: 2167 passed / 1 failed = pre-existing environmental live-opencode hang (`test_omt_live_opencode_guards.py::test_plugins_load_and_tools_execute`; same pre-existing failure noted at feature_077/080 ships, unrelated to this slice)

## Incidental notes

- Session resumed mid-flight: scaffold + implementation + test file existed uncommitted from a prior session; this session verified, fixed a duplicate-scaffold slip (feature_089 dir removed; ledger project_link deduped to feature_088; `project.py sync` regenerated META.md/WORK.md).
