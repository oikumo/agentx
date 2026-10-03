# Test Report — feature_139.compaction_aware_resume_startup (mh16 slice 3)

> Task type: minor_feature · 2026-09-28 · RED (3 behaviors, `test_startup_resume.py`, same bun harness as 138) → GREEN (`normalizeResume`, `resumeDigest` arg, pickup-first INTRO/SUGGESTED, fail-open) → REFACTOR (TDZ hoist fix, fail-open threshold) → DONE. TDD cycle via `omt_tdd`.

## Verdict

**PASS.** Slice battery **3 passed** (`tests/scripts/omt/test_startup_resume.py`). Full repo suite: **2108 passed, 2 skipped, 2 deselected, 0 failed**. `harnessc check`: **0 errors** (no .omt change needed — documented in the tool description, no budget touched).

## What was verified

| Behavior | Test | Result |
|---|---|---|
| pickup-first resume menu | test_resume_pickup_first | PASS — "pick up: <next_task>" leads SUGGESTED, Resume INTRO, TASKS options identical |
| missing/malformed fails open | test_resume_fail_open | PASS — bad/blank digest renders byte-identical normal menu |
| documented + compact | test_resume_documented_and_compact | PASS — `resumeDigest` + `normalizeResume` in tool; fixture digest <2KB |

## Design notes (fail-open rules)

- Schema: JSON `{"next_task","summary","rev"}` (e.g. `omt_status{op:resume}` digest) or plain text (= summary, next falls back to suggested default); caps 160/240 chars so output stays small.
- Plain-text fallback requires ≥16 chars — short garbage fails open instead of becoming a bogus "summary" (caught by the fail-open test during GREEN).
- No STARTUP protocol change: discovery via the tool description; resume sessions pass held context, fresh sessions omit it.

## Boundary

- TASKS map + S mechanics unchanged in resume mode; normal path byte-identical to pre-feature render (138 tests still green).
- Compaction sessions (session totals to 91k, cache_read to 3.6M in the mh14 baseline) now get pickup-first orientation instead of a cold menu; token-denominated claims await labeled-session measurement.

## Next

- Wire `resumeDigest` into the STARTUP line only after real-session evidence (needs .omt edit + budget headroom — agents_md now 3575/3648).
- Adopt feature_136's shipped transport work + close remaining ledger gaps when the line resumes.
