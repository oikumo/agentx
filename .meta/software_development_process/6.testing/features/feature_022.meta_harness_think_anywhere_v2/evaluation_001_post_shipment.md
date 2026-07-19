# Evaluation 001: Post-Shipment Evaluation — Think Anywhere (feature_021 + feature_022)

> **Date:** 2026-07-18
> **Method:** `3.analysis/.../analysis_005_evaluation_plan.md` (full audit P0–P6, all defaults approved)
> **Evaluator:** build agent (opencode 1.18.3)
> **Verdict:** **SHIP-QUALITY WITH ONE LIVE DEFECT** — 7 of 8 tier mechanisms fully verified;
> **D1 read-time injection is dead code in production (F14)** — never fired since shipment.

---

## 1. Executive summary

The Think-Anywhere subsystem (6 tools + think-gate + digest + read-injection) was evaluated
against ~120 extracted doc claims via doc review, test execution (102/102 feature tests,
853/856 full set), full code review of `omt_think.ts` (796 lines) + the enforcer think
surface, 25 hermetic live-fire probes, and live-session observation.

**Every sandbox-verifiable claim passed.** Anchored gate pattern (A1), extension safety
(A2), string-guard (A3), filter/dedup/EOL correctness (A4), anchor insertion (B1), AST
suggest (B2), verify/stale lifecycle (C1), per-file consult + risk window-drop (C2),
index reindex (E1), theory-doc fixes (E2) — all confirmed empirically, most end-to-end.

**One claim class fails in production:** D1's read-time thought injection reads
`output.args.filePath` from the `tool.execute.after` hook — but per the opencode plugin
SDK contract (all cached versions 1.1.12–1.3.13), after-hook `output` is
`{title, output, metadata}` and `args` lives on **`input`** (≥1.2.16). The expression is
always `undefined`; the branch silently no-ops (fail-open). A first read of a
thought-carrying file in this live session showed no injection. The runner tests pass
because their fixtures place `args` in `output` — mirroring the code's wrong assumption,
not the SDK. **This is the second instance of the false-confidence pattern feature_021
cataloged as T2/DEFECT-A** (tests green, behavior absent in real opencode), now at the
hook-payload boundary instead of the loader boundary.

## 2. Scores per evaluation question

| # | Question | Verdict | Evidence |
|---|----------|---------|----------|
| Q1 | Claims coverage | ✅ ~95% | ~115/122 claim-rows verified; F14 contradicts D1's core claim |
| Q2 | F1–F13 resolved | ⚠️ 12/13 | F5's fix (D1) shipped but inert — see §3 |
| Q3 | Intent gap closed | ⚠️ partial | placement ✅ (B1+B2), validation ⚠️ structural-only (honestly scoped), point-of-use ❌ (F14) |
| Q4 | Test integrity | ⚠️ | 102/102 pass, true-RED per tier; but runner-contract blind spot produced F14 |
| Q5 | Live behavior | ⚠️ | all mechanisms verified except D1 (live negative) |
| Q6 | Adoption & net value | ⚠️ | 4 real thoughts (high-value), machinery healthy; writing habit is the bottleneck, not tooling |
| Q7 | Prior post-mortem quality | ✅ (with irony) | 13/13 flaws real, priorities correct, tiering worked; it missed F14 — the exact defect class it had itself cataloged |

## 3. Key finding — F14 (🔴 correctness)

**D1 read-time injection is dead code in production.**

- `omt_enforcer.ts:1033`: `const raw = output?.args?.filePath ?? output?.args?.path ?? output?.args?.file`
- SDK contract (`@opencode-ai/plugin` `dist/index.d.ts`, verified across all 9 cached
  versions): `"tool.execute.after"?: (input: {tool; sessionID; callID; args}, output: {title; output; metadata})`.
  `output.args` **never exists**; `args` is on `input` since SDK 1.2.16 (absent entirely before).
- Consequence: `raw` is always `undefined` → read branch no-ops → fail-open catch never even
  runs → zero user-visible effect since shipment (2026-07-18).
- **Live confirmation:** first read this session of `main_screen.py` (3 thoughts) returned
  no `💡 TA: thoughts in …` block.
- **Why tests stayed green:** `_think_gate_runner.mjs` after-hook fixtures are
  `{input:{tool,sessionID}, output:{args:{filePath}, output}}` — encoding the wrong contract.
  The batch drives the real hook, so hook *logic* is tested; the *payload shape* is fabricated.
- **Same class as DEFECT-A/T2:** the 021 test report documented "29 tests pass while plugin
  broken in real opencode" and fixed the *loader* boundary. F14 is the *hook-payload* boundary.
  The meta-lesson was learned one boundary too narrowly.
- **Fix (one line):** `const raw = input?.args?.filePath ?? input?.args?.path ?? input?.args?.file`
  (before-hook's `output.args` access is correct per the same contract — `output:{args}` there).
- **Test gap to close with it:** the harness e2e proves plugin *load*; nothing proves a hook
  *effect* in a real serve session. Add a serve-mode read-injection probe and/or a
  contract-pin test asserting runner fixture shapes against the SDK `index.d.ts`.

## 4. F1–F13 resolution matrix

| Flaw | Fix | Verdict | Evidence |
|------|-----|---------|----------|
| F1 string-unaware insertion | A3 | ✅ | probe: insert into triple-quoted CSS refused with F1 citation; file unchanged |
| F2 unsafe `#` default | A2 | ✅ | probe: `.xyz` + extensionless refused; `.go/.sql/.html` map correctly |
| F3 gate substring false-positives | A1 | ✅ | probe: prose fixture (`"TA:"`, `META:/DATA:`, `# See TA:`) → 0 hits, gate sees `[]`; repo hits 220→6 |
| F4 consult session-global + cross-session | C2 | ✅ | probe: consult covers only listed files; risk: file stays blocked cross-session |
| F5 reactive-only delivery | D1 | ❌ | **F14 — inert in production** |
| F6 fragile anchoring | B1 | ✅ | probe: after:/symbol: resolve; ambiguity refuses naming candidates; anchor stored in index |
| F7 sloppy filters | A4 | ✅ | probe: category `GOTCHA`→`gotcha:` round-trips; code: `escapeRegex` both filters |
| F8 write-only index | C1+E1 | ✅ | probe: verify consumes index; reindex keep/repair/drop/prune + idempotent |
| F9 dedup/CRLF | A4 | ✅ | probe: duplicate refused citing line; CRLF fixture byte-clean (`od -c`) |
| F10 formula typo | E2 | ✅ | doc:12 `P(c, s \| x) = P(s \| x) · P(c \| x, s)` |
| F11 pass@k estimator | E2 | ✅ | `math.comb` present; `passed / k` gone |
| F12 position-analysis mismatch | E2 | ✅ | `unattributed` bucket + block-boundary attribution present |
| F13 mid-statement/sandbox warnings | E2 | ✅ | doc:247-248 Sandbox warning present; dead stub gone |

## 5. Tier verdicts

| Tier | Verdict | Notes |
|------|---------|-------|
| A (A1–A4) | ✅ | all probes pass; 2 admitted residual anchored-prose FPs (§7 F16) |
| B1 | ✅ | ambiguity-refusal philosophy sound (forces drift-resistant anchors) |
| B2 | ✅ | mechanical entropy proxy, honestly labeled; `.py`-only (admitted) |
| C1 | ✅ | full lifecycle probed: verified→drift→stale→reindex-repair→restore→verified; live verify on 3 real thoughts (`basis: exists`, disclosed) |
| C2 | ✅ | per-file + risk window-drop + exact-session recovery all probed |
| **D1** | ❌ | **F14** — code matches spec; spec targets the wrong payload field |
| E1 | ✅ | idempotent; verify-prune correct; live 693→57 cleanup reproduced in sandbox semantics |
| E2 | ✅ | all 4 doc fixes present; 9 python fences parse (test green) |

## 6. Test integrity (Q4)

- 102/102 feature tests pass (25.5s); full harness surface 853/856 — the 3 failures are the
  documented pre-existing feature_018 react_screen Textual/mock issues, unrelated.
- True-RED verified per tier in the test reports (12F/3P, 17F/2P, 20F/2P, 16F/0P) —
  consistent with observed test quality (real plugin via node runners, hermetic tmpdirs,
  no self-mocking spotted in spot-audit of ~10 tests).
- **Systemic blind spot:** runners fabricate the opencode-side payload. Load-boundary drift
  caused DEFECT-A (021); payload-shape drift caused F14 (022). Structural guard exists for
  the first; nothing pins the second. → Recommendation R1/R5.

## 7. Adoption, friction, process (Q6)

- **Census:** 6 anchored `TA:` lines, 3 files → **4 genuine thoughts**
  (`main_screen.py:77-79` — the F1 incident triad; `omt_think.ts:796` xref pointer) +
  **2 accidental** anchored prose matches (`omt_think.ts:88`, `omt_enforcer.ts:1026` —
  admitted residual; WORK.md's "~965" reference has itself drifted to 1026 — a live F6
  illustration). Low volume, high value-per-thought: the gotcha triad directly informed
  this evaluation.
- **Index:** 189 add + 15 verify records; ~178 point at ephemeral pytest tmpdirs — the
  admitted "runner tests pollute the real index/ledger" precedent. Harmless to gate/list
  (grep-based) and to digest (stale-lookup joins on live hits); E1 reindex is the hygiene
  valve (run after test-heavy sessions).
- **Ledger:** 344 think_consult (mostly runner pollution), 34 phase, 21 complete, 14 tdd,
  **9 omt_skip — all legitimate**: 4 TDD chicken-and-egg bootstraps (documented prior art),
  canary approvals, README-with-user-request, nav-gate src exemption. Zero TDD two-hats
  violations. Process conformance: **good**.
- **Friction:** the think-specific cost is one `omt_think_list` per thought-file per
  session — negligible. The heavy gotchas in WORK.md (receipt churn, Write-tool chunking)
  belong to the guarded-plugin surface (feature_006/016), not to think tools.

## 8. Prior evaluation quality (Q7)

The 021→022 post-mortem was **sound**: all 13 flaws reproduced as real during this audit;
prioritization (correctness→placement→feedback→delivery→housekeeping) was right; tiering
shipped cleanly 4× with regressions green throughout. Its one miss is F14 — shipped D1
with an admitted "not verified in a real opencode conversation" caveat that turned out to
conceal a contract defect. The miss is the same *class* the post-mortem cataloged
(false-confidence at a fabricated boundary), applied one boundary too narrowly.

## 9. New findings

| # | Class | Finding |
|---|-------|---------|
| **F14** | 🔴 | D1 read-injection reads `output.args` (never exists) — dead in production since shipment; runner fixtures encode the wrong contract (§3) |
| F15 | 🟡 residual | `omt_enforcer.ts` named-exports 3 functions (`thinkGateDecision`, `hasConsultedThoughts`, `fileThoughtsIn`) — load-safe *by accident* (throw-safe on garbage input); the DEFECT-A guard pins only `omt_think.ts` (admitted as future work; re-flagged) |
| F16 | 🟢 hygiene | 2 accidental anchored prose `TA:` comments self-gate the plugins and pollute census/digest counts (admitted-accepted; trivially fixable by rewording) |
| F17 | 🟢 hygiene | each runner-test suite run appends ~45 tmp-path records to the real index/ledger (admitted precedent); current index is ~87% ephemeral pollution |

## 10. Recommendations

| # | Priority | Action |
|---|----------|--------|
| R1 | **immediate** | `bug_fix`: F14 one-line fix (`input?.args…`) + extend e2e with a serve-mode hook-**effect** probe + contract-pin test (fixture shapes vs SDK `index.d.ts`). Guarded file → single batched write + receipt refresh |
| R2 | minor | extend the no-named-exports structural guard to all 4 plugins (F15) |
| R3 | trivial | reword the 2 accidental anchored prose comments (F16); bundle with R1 (same files) |
| R4 | hygiene | run `omt_think_reindex` after test-heavy sessions (F17); longer-term: isolate runner cwd so tests never touch the real index/ledger |
| R5 | process | harness doctrine addition: *runner fixtures must be pinned against the SDK contract* — the generalized lesson of DEFECT-A → F14 |
| R6 | adoption | no tooling gap; optionally have `omt_complete` nudge "drop a TA: thought?" on bug_fix completion |
| R7 | future | B2 suggest for the TS family; semantic (truth) verification stays out of scope — correct call |

## 11. Bottom line

feature_021+022 deliver a **well-engineered, honestly-documented** subsystem: 7 of 8 tier
mechanisms verified end-to-end, guardrails hold, process ledger is clean, and the design
docs admit their own limitations accurately. The single live defect (F14) is high-severity
but one-line; its recurrence after DEFECT-A is the strategically important signal — the
harness needs contract-pinning at every fabricated boundary, which R1/R5 address.

---

### Appendix — probe log (all hermetic, `/tmp/opencode/think_eval/`)

P1 after-anchor unique ✅ · P2 symbol-anchor ✅ · P3 ambiguity refusal (2,9) ✅ ·
P4 string-guard F1 refusal ✅ · P5 unknown ext refusal ✅ · P6 mode conflict refusal ✅ ·
P7 `.go`/`//`, `.sql`/`--` ✅ · P8 dedup refusal ✅ · P9 category case round-trip ✅ ·
P10 CRLF byte-clean ✅ · P11 prose/META:/DATA: 0 hits ✅ · P12 sql gate round-trip ✅ ·
P13 verify lifecycle (verified→stale→repair→stale→restore→verified) ✅ ·
P14 reindex idempotent (kept 7, repaired 0 ×2) ✅ · P15 suggest ranking + end_lineno +
refusals + clamp ✅ · P16 D1 sandbox (once/session, re-inject new session, edit untouched) ✅ ·
P17 gate block (risk-first order), cross-session allow non-risk, risk blocked, exact-session
allow ✅ · P18 digest `⚠️ 1 stale` ✅ · **P19 live D1: no injection on first read ❌ (F14)** ·
P20 live verify ×3 (`basis: exists`) ✅ · E2 doc spot-checks ✅.
