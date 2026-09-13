# Design Note — T3-3 Resume Digest (feature_092.resume_digest)

> mh8 T3-3 (source mh3 P3·T3, design-needed per mh3 PROJECT.md Phase-C). This note fixes the
> mechanism BEFORE implementation, per `.projects/meta/meta_harness_8/PROJECT.md` §Scope
> ("T3-3 digest … get a short design note").

## 1. Problem (measured, mh3 §Token evidence)

- opencode.db audit (1009 agentx sessions, 2026-04-19→2026-08-16): **reads = 66% of all
  tool-result bytes** (45.5MB of 68.8MB); worst case the **same file re-read 29×** within one
  session (`meta_harness_2/PROJECT.md` 26× ≈ 520KB in one session).
- Root cause: **context-compaction eviction** — after compaction the agent re-reads the big
  orientation docs it already read. Harness leverage is INDIRECT: we cannot stop compaction,
  but we can make re-orientation ONE small read.
- Typical resume re-read set today (live sizes 2026-09-13): WORK.md 6.5KB + mh8 PROJECT.md
  34KB + CURRENT_STATE.md 17KB ≈ **58KB per resume** → target **≤2KB** (−97%).
- mh8 success criterion #3: "post-compaction resume = 1 digest".

## 2. Non-goals / boundary (mh3 v1.2 D-boundary: "no new features via the token axis")

- **No new tool, no gate, no substrate.** The digest is a new `op` on the EXISTING
  `omt_status` tool (mh3 T3 named `omt_status` resume-digest explicitly).
- **Not** a compaction hook (opencode internals), **not** automatic injection — the agent
  calls `omt_status{op:"resume"}` when re-orienting (discoverable via the updated tool
  description; the op enum is the only API delta).
- Read-only: no ledger writes (omt_status A4 ledger-clean pin holds).

## 3. D5 overlap check (done 2026-09-13, pre-scaffold)

- `omt_q{op:state}` (T3-1 escape fold, T3-2 delegate fold): **feature-scoped** — gate
  decisions, TDD cycle, `last_escape`, `delegate_hint`. No process digest, no doc pointers.
  Complementary; no re-implementation.
- `omt_status` default `status` op: full process context (~1.5–2.5KB text) but includes the
  lint subprocess, skip-hygiene/gate-budget/ceremony lines, and NOT the resume-critical
  session trail / Quick-Start Next / doc anchors. `op:resume` is the deliberately capped,
  resume-shaped single read — not a duplicate of the default render.
- `thinkDigest` (omt_shared.ts, `@budget digest_cap`): TA thought-tags digest for the nav
  gate hint — different concept, untouched.
- feature_069 nav caps: **mechanism precedent** (constant cap + truncation marker + narrowing
  hint; under-cap byte-identical) — reused in shape, different surface.

## 4. Mechanism

`omt_status{op:"resume"}` (no new args; session from plugin context):

Digest lines in priority order (all fail-open — a missing source drops its line):

1. **Banner** — `🧭 RESUME DIGEST — <task_type> <phase> (<scope>) · <feature> · expires <t>`
   or `… no unlock (src/ blocked)`.
2. **Project** — active project (deriveActiveProject) + the project home's
   `## New Session Quick Start` first `**Next:**` line (regex-extracted, markdown stripped,
   capped 200 chars) — this is the distilled "what's next" the agent would otherwise re-read
   a 34KB PROJECT.md to find.
3. **Next** — WORK.md first pending task (`[ ]`/`[~]`) + valid next phases (phaseTransitions).
4. **TDD** — one line (state + test_node + cycles), only when a cycle is active.
5. **Trail** — THIS session's ledger records (`kind` + compact phase/feature/test suffix),
   oldest→newest, capped 12 entries + `… +N more` — the "what did I already do"
   anti-duplicate signal (directly counters the 29× re-read pattern).
6. **Docs** — pointer line with byte sizes + line anchors: `WORK.md <B>B`,
   `PROJECT.md <B>B QuickStart@L<k>`, `CURRENT_STATE.md <B>B newest@L<k>` — so any follow-up
   read is a bounded partial `Read(offset, limit)`, never a full re-read.
7. **Artifacts** — the active feature's phase-artifact dirs, only when a feature is active.

Cap enforcement: `RESUME_DIGEST_CAP = 2048` bytes on the output text. Under-cap output is
byte-identical full content (no marker). Over-cap: drop optional lines from the end
(artifacts → trail items) while > cap; if still over, hard-cut with marker
`… digest capped at 2048B — detail: omt_q{op:state} · WORK.md`.

Fast path: `op:resume` skips the lint subprocess (`runLintBaseline`) — resume is
process-state, not code-state; keeps the read fast. TDD status subprocess stays (one digest
line). Preflight-style: op branch runs BEFORE the default path's subprocesses.

## 5. Budgets (zero-sum, measured 2026-09-13)

| budget | change | bytes | result |
|---|---|---|---|
| tool_args (2454/2464) | op describe `"\| resume"` +9B; `include_ledger` describe diet `include last 5 ledger entries`→`last 5 ledger entries` −8B | net +1 | **2455/2464** (9B headroom) — 059 TOOL_ARGS_CEIL re-pin 2454→2455 |
| tool_schemas (1812/1856) | @tool omt_status description: drop `that will fire ` (−15B), add `\| resume → ≤2KB post-compaction digest` (+43B UTF-8) | net +28 | **1840/1856** (16B headroom) — 059 TOOL_SCHEMAS_CEIL re-pin 1812→1840 |
| agents_md (2918/2944) | @tool payloads not rendered into AGENTS.md (count only) | 0 | unchanged |
| ir_json (~401B headroom) | description lives in compiled IR | +~28B | under cap |
| nav_index | no new .omt records | 0 | unchanged |

Budget-diet-bot will warn (≤64B headroom is advisory; it already warns today at 10B/44B) —
accepted, documented here.

## 6. Acceptance (golden: simulated post-compaction resume = 1 digest read)

`tests/scripts/omt/test_resume_digest.py` — bun probes (feature_071 delegate-fold pattern:
real IR copied to tmp root, seeded ledger.jsonl, seeded WORK.md + project home):

1. **1-read resume**: seeded session (think_consult → tdd_testlist → phase Programming,
   feature linked to a project with Quick Start Next + CURRENT_STATE newest entry) →
   `op:resume` output ≤ 2048B AND contains: task_type/phase/feature, project name +
   Quick-Start Next content, WORK.md next task, trail kinds, doc pointers with sizes+anchors.
2. **Read-only pin**: ledger.jsonl byte-identical before/after the call.
3. **Over-cap**: pathological seed (long trail + long task lines) → still ≤ 2048B with the
   truncation marker present.
4. **No unlock**: empty-ish ledger → `no unlock` banner + WORK.md next task still present.
5. **Fast path**: output carries no lint line (no mvc_check subprocess on resume).
6. **Op surface**: `op:"resume"` accepted; unknown op error message unchanged in shape
   (now lists status | preflight | resume).

## 7. Edit surface (ONE staged batch, T4-2 stage discipline)

| file | edit |
|---|---|
| `tests/scripts/omt/test_resume_digest.py` | new goldens (tests canary, phase declared first) |
| `.opencode/plugins/omt_status.ts` | op:resume branch + digest builder (+ describe diet) |
| `.meta/META_HARNESS.omt` | @tool omt_status description (**LAST** in batch, then re-stage — 089 policy_ver gotcha) |
| `tests/features/feature_059.harness_tiered_template/test_budget_pins.py` | TOOL_ARGS_CEIL 2454→2455, TOOL_SCHEMAS_CEIL 1812→1840 (dated comments) |

Order: `harnessc.py stage --feature feature_092.resume_digest <4 files>` → TS + tests edits →
`.omt` edit LAST → re-stage (refresh digests+policy_ver) → `harnessc check && build` →
boundary e2e (`test_omt_harness_e2e.py`) → `stage --clear` → full suite.
