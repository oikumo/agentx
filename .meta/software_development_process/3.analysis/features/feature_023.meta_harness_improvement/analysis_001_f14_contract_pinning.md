# Analysis 001: Meta Harness Improvement — F14 fix, contract-pinning, export guard, hygiene

> **Phase:** Analysis — `omt_agent_guide.md §2` | **Feature:** feature_023.meta_harness_improvement
> **Source:** `2.requirements/.../feature_023.meta_harness_improvement/FEATURE.md` (F14–F17 + systemic R5)
> **Origin evidence:** `6.testing/.../feature_022.../evaluation_001_post_shipment.md` (2026-07-18)
> **Date:** 2026-07-19 — every claim below re-verified against source this session.

## Scope decision

**All four tiers** of FEATURE.md, in order T1 → T4 (tiers independently shippable; T1 is the
correctness hotfix, T2 mechanizes the meta-lesson, T3/T4 are risk/hygiene). One analysis pass
suffices: the tiers touch disjoint surfaces (enforcer after-hook / new test module / one
existing guard test / two comments + runner cwd), so a single design doc can sequence them.

## Verified evidence (re-checked 2026-07-19)

| Item | Finding | Verified evidence |
|------|---------|-------------------|
| **F14** | D1 read-injection dead | `omt_enforcer.ts:1034` — `const raw = output?.args?.filePath ?? output?.args?.path ?? output?.args?.file` inside `"tool.execute.after"`. Installed SDK `.opencode/node_modules/@opencode-ai/plugin@1.17.11/dist/index.d.ts:249-258`: after-hook `input: {tool; sessionID; callID; **args**}`, `output: {title; output; metadata}`. `output.args` **never exists in any of the 9 cached SDK versions** (1.1.12–1.3.13) nor the installed 1.17.11 — the code was never correct against ANY SDK, not just drifted ones. |
| **F14b (NEW)** | **Edit-path after-hook is dead too** | `omt_enforcer.ts:1063` — the MVC++ post-edit gate (`EDIT_TOOLS` branch: hard-violation block + advisory notify) reads the SAME `output?.args?.filePath ?? …` → equally dead against every SDK version. The evaluation flagged only the read branch (§3); the sibling expression two dozen lines below is the identical defect. **No test drives the plugin's edit after-hook with any payload shape** — `test_omt_lifecycle_e2e.py:497-519` exercises `tdd_check.py after-edit` (Python side), not the plugin hook. Scope implication: FEATURE.md's "one-line fix" is really **two one-line fixes** in the same guarded file; fixing F14b makes the feature_006 MVC++ hard-block live for the first time (intended behavior, but a real behavior change — Design must decide staging). |
| T1.2 | Runner fixtures encode wrong shape | `test_omt_think_v2_tier_bd.py:73-83` (`_read_call`: `args` inside `output`) and `test_omt_think_v2_tier_c.py:115` — both fabricate `{input:{tool,sessionID}, output:{…, args:{filePath}}}`. Correct per SDK: `input.args`. These are the ONLY two fixture sites (grep `args.*filePath` over tests/). |
| T1.3 | Serve-mode probe **impractical as proposed** | feature_020 already established: "opencode serve has no model-free direct-tool-call HTTP endpoint (`/tool*` return the SPA; `/session/{id}/message` requires an LLM)" (`tests/features/feature_020.../test_omt_nav.py:355-360`). Hooks fire only inside a real session processed by an LLM → a deterministic serve-mode hook-EFFECT e2e is not achievable without a live model. FEATURE.md's motivation ("e2e proves plugin load only; that gap is why F14 survived") stands, but the remedy must be the feature_020-pattern substitute: (a) **contract-pin test** (T2.1) making fixture-shape drift fail loudly, (b) **hook-wiring shape test** — instantiate the plugin via its real export and assert the registered hook keys match the SDK's `Hooks` interface (a renamed/missing hook fails), (c) corrected fixtures driving the REAL hook logic with the REAL shape (T1.2). Together these cover every link in the chain except opencode's own dispatch loop (opencode's responsibility). |
| T2.1 | Contract source for pinning | Live-parse `.opencode/node_modules/@opencode-ai/plugin/dist/index.d.ts` (installed, 1.17.11, pinned in `.opencode/package.json`). Vendoring rejected: a vendored copy pins against a snapshot that itself drifts silently; live-parse + `skipif` when node_modules absent (CI without `npm i`) is honest. Pin target shapes: `tool.execute.before → output:{args}`, `tool.execute.after → input:{…,args}, output:{title,output,metadata}`. Regex-parse is sufficient (the .d.ts format is stable across all 9 cached versions — verified by inspection). |
| T3 | Export landscape (wider than F15 states) | `omt_enforcer.ts` has **6 named exports, NO `export default`**: `isDocPath:159`, `navGateDecision:171`, `thinkGateDecision:192`, `hasConsultedThoughts:211`, `fileThoughtsIn:252`, `OmtEnforcer:317` (F15 said 3 — it's 6). The opencode loader calls every function export with the plugin context (WORK.md gotcha #1); the helpers survive via defensive `typeof` guards (e.g. `isDocPath:160` `if (typeof rel !== "string") return false`, annotated "Defensive (DEFECT B)"). The other 3 plugins are default-only (`omt_nav.ts:274`, `omt_status.ts:364`, `omt_think.ts:792`). Existing guard `test_no_named_exports_except_default` (`feature_021/test_omt_think.py:93-115`) pins omt_think ONLY. Un-exporting the 5 helpers breaks 3 runner fixtures + the lifecycle e2e → **sanctioned-export + load-safety pin** is confirmed as the outcome (FEATURE.md T3.2's predicted decision). |
| F16 | 2 accidental anchored TA: | `omt_think.ts:88` (`// TA: tags remain the source of truth).`) and `omt_enforcer.ts:1026` (`// TA: thoughts to the read result …`) — both match `THOUGHT_PATTERN` (`^\s*(#|//|/\*|<!--|--)\s*TA:`). Any word between opener and `TA:` breaks the match (`\s*` only). NOTE: `omt_enforcer.ts:1032` is a GENUINE thought (the evaluation's own F14 gotcha, keep; cosmetic `gotcha: gotcha:` double-prefix may be cleaned in the same write). |
| F17 | Runner pollution path | `test_omt_think_v2_tier_bd.py:43-46` `_run_tool` runs `_think_runner.mjs` with `cwd=REPO_ROOT`; the plugin writes `.meta/.omt/thoughts.jsonl` under the repo → ~45 ephemeral tmp-path records per suite run. The after-hook runner already takes an isolated `directory` (tmpdir ledger); the tool runner does not. Fix channel: pass an isolated `directory` to the plugin factory in `_think_runner.mjs` (same pattern as `_think_gate_runner.mjs` after-hook mode) — check `_think_runner.mjs` instantiation in Design. |

## Problem analysis per tier

### Tier 1 — F14 + F14b (correctness)

- **Fix:** both after-hook arg extractions read `input?.args?.filePath ?? input?.args?.path ?? input?.args?.file`
  (L1034 read-branch, L1063 edit-branch). Before-hook's `output.args` (before-hook `output:{args}`
  per contract) is correct — untouched.
- **F14b staging risk:** making the edit-branch live means a src `.py` edit introducing a NEW
  mvc_check hard error now throws OmtBlock AFTER the write (correct-forward doctrine). That is
  feature_006's documented intent, never before live. Recommendation: fix in the same batched
  write (same guarded file, same defect class — splitting would need two receipt-refresh
  cycles), but give it its own testlist behaviors so a surprise is attributable.
- **Fixture migration (T1.2):** move `args` from `output` to `input` in the two `_read_call`-style
  fixtures; assert injection fires from `input`-carried args. Existing D1 assertions (once per
  session, cap 10, fail-open) carry over unchanged.
- **Hook-effect substitute (T1.3 revised):** three deterministic links instead of serve-mode:
  contract-pin (T2.1) + hook-wiring shape test + real-shape fixture tests. Design specifies the
  wiring test mechanics (registered hook names vs SDK `Hooks` keys).

### Tier 2 — Contract-pinning

- New test module (suggest `tests/scripts/omt/test_opencode_sdk_contract.py` — harness-level,
  not feature-level, since it pins the environment all features rely on).
- Parses installed `dist/index.d.ts`; asserts the two hook signatures' arg carriers.
- Doctrine line for META_HARNESS.md / AGENTS.md (T2.2): *runner fixtures must be pinned against
  the SDK contract* — one sentence in the test-authoring guidance, citing F14.

### Tier 3 — Named-export guard (F15)

- Parametrize the existing regex-scan guard over the 3 default-only plugins (unchanged rule).
- For `omt_enforcer.ts`: pin the sanctioned-export allowlist (exactly the 6 current names —
  any NEW named export fails) + a load-safety invocation test: call each of the 5 helpers via
  node runner with the plugin-context-shaped garbage arg (`{client:null,$:fn,directory:""}`)
  and assert no throw (the property the loader actually relies on).

### Tier 4 — Hygiene

- **T4.1:** reword the two comments so a word precedes `TA:` (e.g. `// (TA: tags remain …)` →
  still matches! `//` + `\s*` + `(` — `(` is not `TA:` → OK, safe). Simplest: `// Inline thought
  tags remain the source of truth).` Verify with `THOUGHT_PATTERN` grep post-edit. Bundle with
  Tier 1's guarded writes (same two files) to save receipt-refresh cycles.
- **T4.2:** isolate `_think_runner.mjs` plugin `directory` to a tmpdir (per-test or per-session
  tmp), so omt_think tool calls from tests never append to the real index/ledger. Design checks
  whether `_think_runner.mjs` can take a directory argv (gate runner already does).

## Open questions for Design

1. F14b: same-write fix (recommended) vs deferred separate tier?
2. Hook-wiring shape test: assert hook-key set equality against SDK-parsed `Hooks` keys, or a
   static allowlist (`tool.execute.before`, `tool.execute.after`, …)? (Former pins drift; latter
   is simpler.)
3. Contract-pin module location: `tests/scripts/omt/` (recommended — environment-level) vs
   feature_023 dir?
4. Load-safety invocation granularity: one node call per helper, or one batch runner printing
   per-export results (recommended — mirrors existing runner batch pattern)?
5. F17 isolation: session-scoped tmpdir shared by a suite vs per-test (recommended:
   per-invocation env var → per-test tmpdir; no cross-test state needed for tool calls).

## Addendum — F14c (NEW, found 2026-07-19 during Analysis): `session.start` hook is never dispatched

Binary audit of the installed runtime (`opencode-linux-x64`, opencode-ai@1.18.3):
`grep -ao 'trigger("[a-z._]*"'` over the binary yields exactly 16 dispatched hook names —
`chat.message`, `chat.params`, `chat.headers`, `command.execute.before`,
`tool.execute.before` (×7 call sites), `tool.execute.after` (×7), `shell.env`,
`tool.definition`, `file.open` (×2), `tab.new`, and 5 `experimental.*`.
**`session.start` is not among them**, and `grep -aob "session\.start"` finds zero
occurrences; no SDK version (1.1.12–1.3.13) types it in `Hooks` either. Consequences:

- `omt_enforcer.ts:883-886` — feature_020 **nav reminder** (`navReminderMsg`): dead since shipment.
- `omt_think.ts:794` — feature_021/022 **TA: session digest** (`thinkDigest`): dead since
  shipment (the evaluation verified it via runner only — the same fabricated-boundary blind
  spot, one level up: the runner called the hook directly, nothing checked that opencode
  ever would).
- Doc claims now known-false: `AGENTS.md:68` ("every session.start greps TA: … surfaces a
  capped digest"), `.meta/META_HARNESS.md:115` (THINK_DIGEST), `:202` (XREF_NAV_ENF
  "session.start reminder").
- Runtime proof of the F14 contract, stronger than the .d.ts: call sites dispatch
  `trigger("tool.execute.after", {tool, sessionID, callID, args}, {title, metadata, output})`
  — args on input, exactly as the SDK types say.

**Decision (user-approved 2026-07-19):** fix the live path — emit digest + nav reminder once
per session via the first dispatched `tool.execute.after` (same once-per-session pattern as
D1); KEEP the `session.start` registrations (inert today, future SDKs may dispatch); correct
the 3 doc claims. This becomes **Tier 1c** in design_001.

## Risks

- **Guarded-file churn:** Tier 1 + T4.1 touch both guarded plugins → batch ONE write per file,
  e2e receipt refresh between files (WORK.md gotcha #4). Order: omt_enforcer.ts (F14+F14b+1026
  reword) → receipt → omt_think.ts (88 reword) → receipt.
- **Think-gate:** both files carry TA: → `omt_think_list` consult required before editing
  (whole-repo consult covers; NOT skip-able).
- **TDD bootstrap:** testlist state blocks tests/ creation → `omt_skip{scope:"tests"}` prior art.
- **F14b live behavior change** may surprise mid-session edits with new hard-error blocks;
  mitigated by correct-forward doctrine + this being the documented feature_006 intent.
- **Receipt self-reference:** `test_omt_harness_e2e.py` is itself in HARNESS_FILES — extending
  the e2e (if Design adds checks there) changes its own hash; receipt written at pass-time
  covers it.
