# Test Report: Resume Digest

> **Phase:** Testing — `omt_agent_guide.md §11` | **Feature:** feature_092.resume_digest
> Run everything with `uv run pytest ...` (AGENTS.md MANDATORY).
> Design: `4.design/features/feature_092.resume_digest/design_001_resume_digest.md`.

## Stage 1 — Unit / component
| Component | Normal path | Exception paths | Result |
|-----------|-------------|-----------------|--------|
| `buildResumeDigest` (op:resume) | seeded post-compaction session → ≤2048B digest with banner (task_type/phase/feature/expires), project + Quick-Start Next (≤200 chars), WORK.md next task + valid phases, session trail (≤12 kinds oldest→newest), doc pointers with byte sizes + line anchors, artifacts line | no unlock (empty-ish ledger) → `no unlock (src/ blocked)` banner + WORK.md next still present | [x] |
| Byte-precise cap (`RESUME_DIGEST_CAP=2048`) | under-cap output byte-identical full content (no marker) | pathological seed (long trail + long task lines) → still ≤2048B, drop-optional-then-hard-cut, truncation marker `… digest capped at 2048B — detail: omt_q{op:state} · WORK.md` present | [x] |
| Read-only pin | ledger.jsonl byte-identical before/after `op:resume` (omt_status A4 ledger-clean holds) | — | [x] |
| Fast path | `op:resume` skips the lint subprocess (no `mvc_check` line in output; resume is process-state not code-state) | TDD status subprocess still runs (one digest line) | [x] |
| Op surface | `op:"resume"` accepted; unknown-op error shape unchanged (now lists status \| preflight \| resume) | unknown op → same error shape | [x] |
| Fail-open line drops | missing project home / WORK.md / CURRENT_STATE → that line silently drops, rest of digest intact | — | [x] |

## Stage 2 — Integration
`op:resume` branch lives in `.opencode/plugins/omt_status.ts` execute BEFORE the
default path's subprocesses (preflight-style placement); reuses existing
`deriveActiveProject` + `phaseTransitions` + ledger session reads — no new tool,
no gate, no substrate (design §2 boundary). Bun probes (feature_071 pattern):
real IR copied to tmp root, seeded ledger.jsonl + WORK.md + project home.

Budget integration (zero-sum, design §5): op describe `| resume` +9B paid by
include_ledger describe diet −8B (tool_args 2455/2464); @tool omt_status
description −15B/+43B (tool_schemas 1840/1856). Both measured live.

## Stage 3 — System (use-case driven)
Use case: "post-compaction resume = 1 small read" (mh8 success criterion #3).
Dogfooded in-session: `omt_status{op:"resume"}` oriented this very resume
session (paused mid-Programming → one 432B digest replaced the ~58KB
WORK.md + PROJECT.md + CURRENT_STATE.md re-read set; follow-up reads become
bounded partial `Read(offset, limit)` via the doc-anchor line).

## Evidence

```
$ uv run pytest tests/scripts/omt/test_resume_digest.py -q
.......                                                                  [100%]
7 passed in 1.19s

$ uv run pytest tests/scripts/omt/test_omt_harness_e2e.py -q
.                                                                        [100%]
1 passed in 0.82s

$ uv run pytest -q
2214 passed, 10 warnings in 169.12s (0:02:49)
```

Baseline 2207 + 7 new goldens = **2214/2214, 0 failures**. `harnessc check`
0 errors (265 records), `build` OK (5 projections); budgets green: tool_args
2455/2464, tool_schemas 1840/1856, nav_index 64990/65536. Staged receipt batch
(T4-2: 4 files) → boundary e2e green → `stage --clear`.

### Mid-Programming pause/resume
Paused 2026-09-13 (`.sandbox/pause_2026-09-13b.md`), resumed same day: one-line
probe fix (below) + 3 follow-on pin re-pins, then green. Pause protocol
(workflow `pause_dev_for_resume_later.md`) exercised end-to-end.

### Probe serialization gotcha (root cause of the paused session's 7 failures)
omt_status `execute` returns a plain object (omt_q returns a JSON *string*) —
bun `console.log(obj)` prints inspect format (unquoted keys, multi-line) so
`json.loads` fails. Probe templates MUST `console.log(JSON.stringify(result))`
(task_prep_slice.py:29 precedent). TA'd at the `_probe` def:
GOTCHA_PROBE_SERIALIZATION.

### Follow-on pin re-pins (same batch, feature_059 pin discipline)
This batch's budget/description moves staled 3 pins the design note's edit
surface missed; re-pinned with dated comments:
- `feature_055/test_gate_preflight.py` static pin: `ordered gates that will
  fire + clearing action` → `ordered gates + clearing action each` (the −15B
  describe diet).
- `test_budget_diet.py` live pin: tool_args 2454→2455 (10B→9B), tool_schemas
  1812→1840 (44B→16B); agents_md 26B unchanged; nav_index/ir_json still silent.
- `feature_059/test_budget_pins.py` NAV_INDEX_CEIL 64956→64990 — design §5
  predicted "nav_index unchanged" but nav records carry @tool description text
  (+34B measured; kinds unchanged, budget 64990/65536 green).
