# Design 001: Meta Harness Improvement — F14/F14b/F14c fixes, contract-pinning, export guard, hygiene

> **Phase:** Design — `omt_agent_guide.md §3` | **Feature:** feature_023.meta_harness_improvement
> **Source:** analysis_001_f14_contract_pinning.md (+ F14c addendum); FEATURE.md (F14–F17, R5)
> **User decisions (2026-07-19):** F14b fixed with F14 in Tier 1; T1.3 serve-mode probe replaced
> by deterministic substitute; F14c fixed via live path (first `tool.execute.after` per session),
> `session.start` registrations kept, 3 doc claims corrected.

## 1. Architecture overview

All fixes are confined to the OMT enforcement surface: two guarded plugins
(`omt_enforcer.ts`, `omt_think.ts`), four feature_022 test files (fixture + cwd corrections),
one new feature_023 test module + one combined node runner, one new harness-level contract-pin
module, and three doc claims. No `src/` production code is touched (the harness IS the product
here); TDD still applies (major_feature → auto-TDD), with `tests/` standing in for `src/`
two-hats semantics per feature_022 prior art (bootstrap via `omt_skip{scope:"tests"}`).

```
SDK d.ts (installed 1.17.11)          opencode 1.18.3 binary
  before: output{args}                  trigger("tool.execute.after", {…,args}, {title,output,metadata})
  after:  input{…,args}, output{…}      16 hook names; session.start NOT among them
        │                                        │
        ▼ T2.1 contract-pin test                 ▼ hook-wiring shape test (registration ⊆ sanctioned)
tests/scripts/omt/test_opencode_sdk_contract.py   _plugin_surface_runner.mjs (hooks mode)
        │                                        │
        └──────────► corrected fixtures (input.args) drive REAL hooks via _think_gate_runner.mjs
```

## 2. Tier 1 — F14 + F14b correctness (omt_enforcer.ts, ONE batched guarded write)

### 2.1 The fix (two lines)
- `omt_enforcer.ts:1034` (read-injection): `output?.args?…` →
  `input?.args?.filePath ?? input?.args?.path ?? input?.args?.file`
- `omt_enforcer.ts:1063` (edit path): same replacement.
- **Untouched:** before-hook's `output.args` (correct: before-hook `output:{args}` per contract,
  runtime-verified in binary call sites).
- F14b behavior change (user-acknowledged): a src `.py` edit introducing a NEW mvc_check hard
  error now throws OmtBlock post-write (correct-forward). This is feature_006's documented
  intent, live for the first time.

### 2.2 Fixture migration (T1.2)
- `test_omt_think_v2_tier_bd.py::_read_call` (:73-83) and `test_omt_think_v2_tier_c.py` (:115):
  move `"args": {"filePath": …}` from `output` into `input`
  (`{"tool", "sessionID", "args"}`), output becomes `{title, output, metadata}` exactly.
- All existing D1 assertions (once/session, cap 10, no consult record, fail-open) carry over —
  they now fail on unfixed code (true RED) and pass post-fix.

### 2.3 F14b runner test mechanics
`_think_gate_runner.mjs` after-hook mode drives the REAL hook; the edit path calls
`lintFindings` via `` $`uv run scripts/omt/mvc_check.py …` `` — the runner's throwing
`dollarStub` is replaced **per-batch** with a canned-mvc stub:
```js
const mvcStub = (strings, ...vals) => ({ cwd: () => ({ quiet: () => ({ nothrow: async () =>
  ({ stdout: Buffer.from(JSON.stringify({ findings: CANNED })) }) }) }) })
```
New runner mode `after-hook-edit '<directory>' '<json:{findings, calls}>'` (CANNED injected
per batch). Cases: (a) 1 new error finding on `src/x.py` edit → OmtBlock thrown naming the rel
path; (b) 0 errors → no throw; (c) warnings only → no throw (notify is client-null-safe).
`hardSnapshot` empty (no before-hook driven) → any error counts as introduced — correct for
the test. filePath is `<directory>/src/x.py` (need not exist; `relOf` only joins).

### 2.4 Tier 1c — session digest / nav reminder live path (F14c)
- **omt_think.ts** default export gains `"tool.execute.after": async (input, output) => {…}`:
  module-level `digestSessions = new Set()`; on first call per `input?.sessionID`, append
  `thinkDigest()` to `output.output` (same mutation channel as D1 — guaranteed agent-visible;
  `notify()`/toast rejected: no-op headless). Fail-open try/catch. `session.start`
  registration RETAINED (inert today; future SDKs may dispatch).
- **omt_enforcer.ts** after-hook: `navRemindedSessions = new Set()`; first call per session
  appends `navReminderMsg()` to `output.output` (before the read/edit branches, any tool).
  `session.start` registration retained.
- Ordering: reminder prepended before D1 injection content when both fire on one call —
  independent appends, no coordination needed.
- Doc corrections (same write batch where guarded): `AGENTS.md:68` ("every session.start …")
  → "the first tool result of each session carries the TA: digest (session.start hook retained
  for future SDK support)"; `.meta/META_HARNESS.md:115` THINK_DIGEST mechanism line and `:202`
  XREF_NAV_ENF "session.start reminder" → first-tool-result wording. `omt_think.ts:19` header
  comment updated in the same plugin write.

## 3. Tier 2 — Contract-pinning (mechanize the meta-lesson)

### 3.1 New module `tests/scripts/omt/test_opencode_sdk_contract.py`
Harness-level (environment pin, not feature-scoped). `skipif` when
`.opencode/node_modules/@opencode-ai/plugin/dist/index.d.ts` absent (CI without `npm i`).
- **Shape pin:** regex-extract the `"tool.execute.before"` and `"tool.execute.after"` blocks;
  assert before → input block has NO `args`, output block HAS `args`; after → input block HAS
  `args`, output block has NO `args` (and has `title`, `output`, `metadata`).
- **Version pin:** `.opencode/package.json` dependency version == installed
  `node_modules/.../package.json` version (drift alarm on SDK upgrade).
- **Fixture pin:** source-assert both `_read_call` sites place `"args"` in the `"input"` dict
  (`"input":\s*\{[^}]*"args"` within the function body) — a regression to `output.args`
  fixtures fails here even if behavior tests are somehow skipped.
- **Runtime-truth comment:** the test header records the binary-audit trigger list (16 names,
  analysis_001 addendum) as the ground truth the d.ts pin proxies.

### 3.2 Doctrine (T2.2)
One line in `.meta/META_HARNESS.md` test-authoring guidance: *runner fixtures that fabricate
opencode payload shapes MUST be pinned against the installed plugin SDK contract
(`test_opencode_sdk_contract.py`) — DEFECT-A → F14 lesson.*

## 4. Tier 3 — Named-export guard extension (F15)

New combined runner `tests/features/feature_023.meta_harness_improvement/_plugin_surface_runner.mjs`
(modes share one plugin-import harness):
- `hooks '<plugin-abs-path>' '<factory:default|OmtEnforcer>' '<tmpdir>'` → prints
  `{"hooks": [...registered hook/tool keys...]}` after instantiation.
- `exports '<plugin-abs-path>'` → prints `{"named": [...], "calls": {name: "ok"|"ERR: …"}}` —
  every named FUNCTION export (except the `OmtEnforcer` factory) invoked with the
  plugin-context-shaped garbage arg `{client:null, $:noop, directory:""}`, then `undefined`,
  then `{}`; no-throw required (the property the opencode loader relies on).

Python assertions (in `test_omt_harness_improvement.py`):
- **Default-only rule** parametrized over `omt_nav.ts`, `omt_status.ts`, `omt_think.ts`
  (regex scan, mirrors feature_021 `test_no_named_exports_except_default`).
- **Enforcer sanctioned-export allowlist** — exact set match:
  `{isDocPath, navGateDecision, thinkGateDecision, hasConsultedThoughts, fileThoughtsIn,
  OmtEnforcer}`; any NEW named export fails (T3.2 decision: sanctioned-export + load-safety
  pin, since un-exporting breaks 3 runner fixtures + lifecycle e2e).
- **Load-safety:** all `calls` results `"ok"`.
- **Hook wiring:** enforcer hooks ⊇ `{tool.execute.before, tool.execute.after}`; think hooks
  ⊇ `{tool.execute.after}`; every registered key ∈ `{tool.execute.before, tool.execute.after,
  tool, session.start}` where `session.start` is the documented INERT allowlist entry
  (comment cites the binary audit — if a future SDK dispatches it, the allowlist comment is
  updated, not the code).

## 5. Tier 4 — Hygiene (F16, F17)

### 5.1 F16 rewording (bundled into the Tier 1 guarded writes — same two files)
- `omt_think.ts:88`: `// TA: tags remain the source of truth).` →
  `// inline thought-tags remain the source of truth).`
- `omt_enforcer.ts:1026`: `// TA: thoughts to the read result (point-of-use awareness, strictly`
  → `// thought-tags to the read result (point-of-use awareness, strictly`
  (THOUGHT_PATTERN `^\s*(#|//|/\*|<!--|--)\s*TA:` requires opener+whitespace only — any
  leading word breaks the match.)
- Cosmetic: the genuine `omt_enforcer.ts:1032` F14 gotcha's `gotcha: gotcha:` double prefix →
  single `gotcha:` (same write).
- **Census pin test:** run the REAL `THOUGHT_PATTERN` over all 4 plugin files; assert exactly
  2 anchored hits — one in `omt_enforcer.ts` (content contains `F14`), one in `omt_think.ts`
  (content contains `xref`) — drift-resistant (pin by file+substring, not line).

### 5.2 F17 runner cwd isolation
Root cause: `omt_think.ts:28` `REPO_ROOT = process.cwd()`; the 4 feature_022 test files invoke
`_think_runner.mjs` with `cwd=REPO_ROOT` → real `.meta/.omt/{thoughts,ledger}.jsonl` appended.
- `_run_tool` helpers (tier A `test_omt_think_v2.py`, tier_bd, tier_c, tier_remainder) gain a
  `cwd` parameter; call sites pass the per-test `tmp_path`. No runner change needed
  (`process.cwd()` picks it up; fixture paths are already absolute).
- **Assertion migrations:** tier_c consult-record assertions read the ledger under the tmp cwd
  (`<tmp>/.meta/.omt/ledger.jsonl`) instead of the repo one; tier_c session-start digest tests
  (:313+) create their thought-fixture files INSIDE the tmp cwd (digest greps cwd).
- **Isolation proof test (feature_023):** invoke `omt_think` via runner with `cwd=tmp_path`;
  assert `<tmp>/.meta/.omt/thoughts.jsonl` exists AND the repo index is byte-unchanged.
- Residual: document in the test report that pre-feature_023 pollution is cleaned by one
  `omt_think_reindex` run (E1 valve) — no periodic step needed once isolation lands.

## 6. Test plan (TDD behaviors — `omt_testlist` JSON array)

1. `read-injection fires from input.args (real SDK shape): first read appends TA block, second read in session does not, cap 10, no think_consult record, fail-open on garbage`
2. `after-hook edit path reads input.args: src .py edit with new canned mvc error → OmtBlock naming rel; zero errors → no throw; warnings-only → no throw`
3. `omt_think tool.execute.after appends TA digest to the FIRST tool result per session only; session.start registration retained`
4. `omt_enforcer after-hook appends nav reminder to the FIRST tool result per session only`
5. `AGENTS.md + META_HARNESS.md describe digest/reminder as first-tool-result emission (no "session.start greps" live claim)`
6. `contract-pin: installed d.ts — before output{args} & input args-free; after input{args} & output{title,output,metadata}; package version == installed version`
7. `fixture-pin: both _read_call sites place args in the input dict (source assertion)`
8. `default-only named-export guard over omt_nav.ts, omt_status.ts, omt_think.ts`
9. `omt_enforcer named exports == sanctioned allowlist {isDocPath, navGateDecision, thinkGateDecision, hasConsultedThoughts, fileThoughtsIn, OmtEnforcer}`
10. `load-safety: enforcer helper exports invoked with garbage plugin-context args ({client…}, undefined, {}) never throw`
11. `anchored-TA census over the 4 plugins == exactly 2 genuine thoughts (enforcer F14 gotcha; think xref)`
12. `runner cwd isolation: omt_think tool call with tmp cwd writes index under tmp; repo .meta/.omt/thoughts.jsonl byte-unchanged`
13. `hook wiring: enforcer ⊇ {tool.execute.before, tool.execute.after}, think ⊇ {tool.execute.after}; registered keys ⊆ {before, after, tool, session.start(inert-allowlist)}`

**RED strategy:** behaviors 1–4 fail on current code (wrong arg source; missing hooks) — true
RED. 6–7, 13 fail pre-fix (fixtures wrong shape; think lacks after-hook). 8–10 pass today
(guards — they pin the absence of regression; written first anyway). 11 fails pre-T4.1 (4 hits).
12 fails pre-T4.2 (repo index grows).

## 7. Implementation sequencing (guarded-file discipline)

| Step | Action | Gate |
|------|--------|------|
| 1 | `omt_phase{major_feature, Programming, feature_023}` + `omt_testlist` (JSON array of §6) | — |
| 2 | `omt_skip{scope:"tests"}` (TESTLIST bootstrap, prior art) | ledger |
| 3 | RED: new feature_023 test module + runner + contract-pin module; feature_022 fixture migration (1,2,6,7,13 RED; 8–10 green) | `omt_red` per node |
| 4 | `omt_think_list{path:".opencode/plugin"}` — think-gate consult (NOT skip-able) | think-gate |
| 5 | ONE batched write `omt_enforcer.ts` (F14+F14b+Tier1c reminder+1026 reword+gotcha: fix) → `uv run pytest tests/scripts/omt/test_omt_harness_e2e.py -q` (receipt) | guarded |
| 6 | ONE batched write `omt_think.ts` (Tier1c after-hook+88 reword+:19 comment) → e2e receipt | guarded |
| 7 | `AGENTS.md` + `META_HARNESS.md` doc fixes (AGENTS.md is in HARNESS_FILES) → e2e receipt | guarded |
| 8 | Tier 4.2 cwd isolation across the 4 feature_022 test files | tests/ |
| 9 | `omt_green` / `omt_refactor` per behavior; full feature_022+023 sets green | TDD |
| 10 | Test report `6.testing/.../test_report.md`; `omt_complete{advance_to:Testing→Done}` (never `omt_done` — WORK.md gotcha) | — |

Pre-existing out-of-scope failures: 3 feature_018 react_screen Textual/mock + 2 tdd_check
real-ledger-window tests (WORK.md gotcha #2) — unchanged.

## 8. Traceability

| Behavior | Tier | Finding | Primary files |
|----------|------|---------|---------------|
| 1 | T1.1/1.2 | F14 | omt_enforcer.ts, tier_bd/tier_c fixtures |
| 2 | T1.1 | F14b | omt_enforcer.ts, _think_gate_runner.mjs (new mode) |
| 3, 4, 5 | T1c | F14c | omt_think.ts, omt_enforcer.ts, AGENTS.md, META_HARNESS.md |
| 6, 7 | T2 | systemic R5 | test_opencode_sdk_contract.py (new) |
| 8, 9, 10, 13 | T3 | F15 | test_omt_harness_improvement.py + _plugin_surface_runner.mjs (new) |
| 11 | T4.1 | F16 | the two plugin writes (step 5/6) |
| 12 | T4.2 | F17 | 4 feature_022 test files |
