# CURRENT_STATE: harness_wrapper_split

> Session-by-session log + resume point. Companion to `PROJECT.md` (canonical).
> Newest entry on top. One `## <date>` block per session.

---

## 2026-10-11b (R4 session — harness-features bucket LANDED, unit feature_143 complete)

### Done

- Declared `omt_phase` test Analysis `feature_143.r4_harness_features_bucket` + fresh `omt_skip` tests canary; verified all 35 src dirs present, dest clear, no `feature_143` collision.
- **R4 `568afdb`:** 35 dirs/39 files mirror `tests/features` → `tests/harness_meta/` (R4a 22 SYS-heavy + R4b 13 LIT-heavy, pure renames) + 5 same-commit fixes (016 run-path docstring, 131/132/134 bridge prose → `harness_meta`, 016 `validate-exit` pin split-args form — stale pin proven failing at HEAD via stash check).
- LIT review per dry-run (inspect each, no blind sed): fixed 4 docstrings + 1 pin; left golden fixtures/placeholders untouched (054 own-dir/evil, 055 fake path, 056 guard path, 062 message format, sentinel `<feature>` patterns).
- Failure triage via stash-check at HEAD old homes: 7 newly-collected failures (054/056/058/060×2/062-parity/103) fail identically pre-move (v2-plugin-migration fallout + live-drift) — triage-only; 2 DeclareEmbed failures are parallel-load flakes (pass solo + at HEAD, pass on lanes re-run).
- Green: targeted 016+050 33 passed; lanes 1441 passed + 12 HEAD-proven pre-existing + 6 skipped; `prove --lane both --out /tmp/opencode/` clean, certs rm'd; DEPTH `parents[3]` intact.
- Close-out: WORK.md DONE row + oldest DONE rotated to archive, T1_SIGNOFF_V9 R4 note, `omt_complete` → Done.

### Next

- **R5/R6 per saved dry-runs (user go, each fresh canary):** R5 product features 13 dirs/56 files → `tests/agentx/` (LIT 4 sentinels, fixtures move WITH dir); R6 138 goldens 2 files → `split_proof_meta/`.
- After R5–R6: `tests/features` fully retired (only 138 dir + ignored `__pycache__` shells left) → T3 lanes CI, telemetry isolation, T4–T6 per pause map.

---

## 2026-10-11 (resume session — R3 blocker cleared, feature_142 complete, tests/scripts/ retired)

### Done

- Resumed per `sandbox/pause_2026-10-11.md` verbatim; baseline verified (HEAD `8074515`, 24 staged R3 renames, ledger 51, `M WORK.md` pointer). Declared `omt_phase` test Analysis `feature_142.reason_session_inspect_bucket_moves` + fresh `omt_skip` tests canary (phase-then-skip order).
- **R3 `fe890f1`:** 24-file mirror `tests/scripts/session_inspect → tests/harness_meta/session_inspect` (conftest WITH dir, no `__init__`, `parents[3]` kept, 16 bare-conftest siblings untouched) + 2 dotted-import fixes (`slice5:8`, `slice6:12` → `harness_meta`). Session 72 passed+2 skipped; both lanes 1140 passed+same 5 triaged (kb_akb×2, net_history, dashboard, omt_q_audit_t1_1)+6 skipped; `prove --lane both --out /tmp/opencode/` clean, certs rm'd.
- **R3b `b864dbf`:** 4 docstring LIT (toolbox hermetic note + bridges 131/132/134) — completes the 6-site map. Targeted 99 passed+2 skipped; zero-literal sweep 0 live (2 exempt TA: `new_feature.py:158`, `conftest.py:157`).
- **`rm -rf tests/scripts`** (stale `__pycache__` only — sources already moved in R2/R3): `tests/scripts/` GONE, fully retired. `harnessc check` 281/0.
- Close-out: WORK.md `[~]`→`[x]` DONE row, T1_SIGNOFF_V9 `tests/scripts/ RETIRED` header note, `omt_complete` → Done.

### Next

- **R4/R5/R6 per saved dry-runs (user go, each fresh canary):** R4 harness features 39 files/35 dirs → `tests/harness_meta/` (LIT 13); R5 product features 56/13 → `tests/agentx/` (LIT 4); R6 138 goldens 2 files → `split_proof_meta/`.
- After R4–R6: `tests/features` buckets per T1_SIGNOFF rows, T3 lanes CI, omt_q telemetry isolation (owns the 5 triaged), T4 TA strip, T5 receipts, T6 multi-root sync + 4 project relocations (re-read the relocations-gap note in the 2026-10-10 block first), UC0 archival, `bridge:` backlog, CI cert pinning.

---

## 2026-10-10d (resume session — omt bucket R3 LANDED, unit feature_141 complete)

### Done

- Resumed per `.sandbox/pause_2026-10-10b.md` §2 verbatim; baseline re-verified (tree clean @ `f34c75c`, check 281/0, suite 2118 + the same 5 triaged live-drift + 6 skipped). Canary + phase records still valid at resume (22:00Z; expiry ~04:15Z next day — no re-declare needed).
- **R3 `c2b5e2c`:** 10-file `git mv` (e2e+receipt+template cluster) + `rm -rf tests/scripts/omt` — **omt bucket complete: 72 files in `tests/harness_meta/omt/` across R1–R3.**
- Stage protocol honored end-to-end: stage(8) → harness-source batch (harnessc.py init-template segmented :2092/:2158, `omt_shared.ts` ×5 incl. `isOmtHarness:594` fallback set-equal to `.omt:38`, preflight.ts, omt_q.ts, bench/tasks.py, new_feature.py :86, split_proof.py docstring, lessons.json ×2) → `.omt` LAST (:23/:24/:38) → re-stage → e2e self-LIT first (receipt-exempt) → single e2e from new home (receipt minted) → `harnessc build` → check 281/0.
- Tests-side LIT: in-bucket self-LIT (receipt_batch_mode :141 command-string assert, harnessc, harnessc_workflows, budget_diet, docs_drift_pins ×2, project_lifecycle header), segmented catches (guard_source_pins :46, 059 test_init_fs :8/:37, 054 fake-path :232), 030 sentinel import pair, kb acceptance :14/:166.
- **5 map-missed sites** caught by the extended segmented sweep (plain-rg class): 055 test_gate_preflight :39, 058 test_thought_review :35, 016 test_tdd_enforcement :141, test_scaffolds_lsp_allowlist :366, test_omt_q U11 :516/:531/:534 (asserts live-IR refresh_tests/refresh_cmd — functional, not cosmetic).
- Green gates: suite 2118 + same 5 triaged + 6 skipped; check 281/0 (ir_json 22583/24064, nav_index 68812/69120, agents_md unchanged); prove `--lane both --out /tmp/opencode/` clean, certs deleted (§1 root-stray gotcha honored, 0 untracked); zero-literal sweep 0 hits (only exempt dated TA xref new_feature.py:158); extended segmented sweep 0.
- Close-out: R3 commit, WORK.md `[~]` → `[x]` DONE row, T1_SIGNOFF_V9 LANDED header note, `omt_complete` → Done.

### Next

- **feature_142 per `.sandbox/pause_2026-10-10b.md` §2 (self-sufficient map, user-confirmed ONE round):** last two `tests/scripts/` buckets — reason (3 files, zero edits) + session_inspect (24 incl. conftest), 6 LIT sites total, stage-free (no harness surface — no stage/receipt/build, canary only). Nothing minted yet (no expiry pressure): declare `omt_phase` FIRST, then tests canary. PAUSED same day (fourth close) — `[~]` row @ WORK.md.
- After feature_142: `tests/scripts/` fully retired → remaining backlog (pause §2 tail): `tests/features` buckets per T1_SIGNOFF rows, T3 lanes CI, omt_q telemetry isolation (owns the audit_t1_1 live-probe family + the 5 triaged), T4 TA strip, T5 receipts, T6 multi-root sync + 4 project relocations (re-read the relocations-gap note in the 2026-10-10 block first), UC0 archival, `bridge:` backlog, CI cert pinning.

---

## 2026-10-10c (pause session — omt bucket R1+R2 LANDED, R3 researched + paused)

### Done

- Baseline verified; **5th triaged failure classified** (prior pause's "4" undercounted): `test_omt_q_audit_t1_1::test_bootstrap_templates_last_three_live` — real ledger (current+archive) has zero `kind:skip`+bootstrap rows (ledger lifecycle ate them); live-probe family, user-approved triage-only (the omt_q telemetry-isolation follow-up owns the class).
- User-approved decisions: one-commit-first (`9f786aa`: features 138–140), 3-round referencer-owned granularity, triage-only 5th failure, all-3-rounds go-ahead, bookkeeping commits per pause.
- **R1 `858d4c9`:** net×28 → `tests/harness_meta/omt/` (mirror move, zero content edits) + 13 referencer fixes (039/040/041 sentinel lists + docstrings, 114/118/043 docstrings, `scripts/omt/net/{__init__,conformance,io,cli}.py` docstrings; cli.py think-gate).
- **R2 `8f5a8e6`:** 34-file cluster + 28 fixes (026 golden-smoke import, 051 ×2, `tdd/state.py` ×3 + `tdd_check.py` + `lessons.json` gate_two_hats lesson + kb_akb docstring, `gate.py` stale test_net_gate path → features lane, `omt_shared.ts` ×5, `lsp_filter.ts` ×2, `omt_net.ts` + `omt_session.ts` pins). Receipt round-robin fired as designed: state.py + lsp_filter.ts 2nd edits blocked → 2 mid-round e2e mints.
- **prove-certs root-stray gotcha** root-caused + fixed + TA'd (`test_split_proof_gate.py:33`): R1 `prove --out .` → root certs → `add -A` committed them → the FILESYSTEM-based root_allowlist stray-hygiene check broke 4 check-expecting tests; `git rm` + delete + `.gitignore` entries; future proves `--out /tmp/opencode/`.

### Next

- **R3 per `.sandbox/pause_2026-10-10b.md` §2** (self-sufficient map — no re-research): 10-file move, stage protocol (.omt LAST → re-stage → e2e from new home → build), `omt_shared.ts:594` ↔ `.omt` harness_paths set-sync, segmented catches plain rg misses (`guard_source_pins:46`, `test_init_fs:37`, `054:232`), 030 import pair, budget expectations, green gates + close-out + `omt_complete`. **Canary + phase records expire ~04:15Z 2026-10-11** — re-declare phase FIRST, then re-mint canary (pause §0).

---

## 2026-10-10b (resume session — T2 goldens + first lane bucket + REVIEW bucket LANDED)

### Done

- **Review bucket resolved (unit 2, feature_140):** 5 files, one line each — `feature_015` → `tests/agentx/` (zero harness imports: pure product hardening), `feature_030` pair (conftest + goldens sentinel) → `tests/harness_meta/` (import still points at the unmoved `tests.scripts.omt.test_project_lifecycle`; updates with the omt bucket), `feature_043` → `tests/harness_meta/` (single-lane call: runtime imports `scripts/omt/net` only, product half exercised via subprocess), `feature_kb_akb` → `tests/harness_meta/` (harness-source structural pins; product knowledge is index data). Zero content edits needed — all LIT refs point at the still-unmoved omt bucket.
- **Enabling harness edits (lane-aware completion, receipt flow honored — e2e minted per round):** `phase_gate.ts` — checkPhaseExitArtifacts "Unit tests" now searches `tests/{features,agentx,harness_meta}` (first match wins; no-dir-anywhere still reports missing) + declare-embed probe follows the feature's lane + description string updated; `receipt_guard.ts` — `isOwnTestDir` (RED own-dir auto-unlock) lane-aware with slash-bounded short-form matching preserved; `scripts/omt/tdd/gates.py` — `_feature_test_dirs()` union across lanes for BOTH the behavioral run and coverage targets (no silent drop while a feature straddles lanes). Without these, every harness-bucket move would have silently weakened omt_complete.
- **054 golden extended (strengthened, not weakened):** own-dir allow in `tests/harness_meta/{F}` + `tests/agentx/{F}`, evil `feature_054evil` blocks in lanes too (bun scenarios green).
- **Live proof:** `tdd_check.py validate-exit --feature feature_043...` → `test_files: 1` found at its ONLY home (`tests/harness_meta/`), behavioral `ran: true`; legacy `feature_007` still resolves from `tests/features`. Suite **2118 + 4 triaged** (043 drift now fails from its new lane home — same test, same class), check 281/0, guard pins + e2e + receipt-batch green.
- **T2 goldens (unit 1, feature_139, earlier this session):** `tests/harness_meta/split_proof_meta/` (9 hermetic) + first lane bucket `tests/scripts/toolbox → tests/harness_meta/toolbox` (6 files, LIT fixes incl. `scripts/toolbox/toolbox.py` promote/prune). 3 suite flakes fixed (WORK_BUDGET 10240→11264 re-pin; atomic e2e receipt mint tmp+os.replace; racy-honest ledger windows). **Triage item 3 root-caused:** omt_q live-root probes (`test_omt_q.py` +1/run, `test_omt_q_audit.py` +4/run) self-log `kind:q` telemetry to the real ledger — follow-up: telemetry isolation (receipt-covered `omt_q.ts` edit).

### Next

- **Next unit: the `tests/scripts/omt` bucket** (71 files → `tests/harness_meta/omt/`; biggest LIT cluster: 33 path-literal files + the segmented `"tests"/"scripts"/"omt"` sites — harnessc init template (2092/2158), 055/016/058/137 guard pins, `test_omt_harness_e2e.py` self-references, plus the 030 sentinel import update rides here). Suggest splitting into 2–3 sub-buckets (net_* family / kb+workflows+misc / e2e+receipt cluster) to keep each round reviewable.
- omt_q telemetry-isolation follow-up (above) — candidate small feature; must ride the receipt flow.

---

## 2026-10-10 (UC8 promotion — program home scaffolded, feature_138 linked)

### Done

- **UC8 executed (user explicit go):** manual scaffold `.projects/agentx/harness_wrapper_split/{PROJECT.md,CURRENT_STATE.md}` (this home) + `project.py link feature_138.split_proof_oracle_firewall_slice harness_wrapper_split --origin manual` (run with `OMT_PROJECTS_ROOT=.projects/agentx` + `OMT_WORK_PATH=<tmp>` — hermetic idiom — so `WORK.md ## Projects` and the agentx `META.md` pending-moves draft were byte-untouched; verified by diff after).
- **Gap (stated, not hidden):** the "4 pending-move links" in UC8/pause prose conflate project-relocations with the feature-level `link` tool — `link <feature> <project>` cannot express a project move, and same-slug re-links are no-ops. The 4 project dirs are NOT moved (pre-T6: single-root sync would clobber `WORK.md`); relocation rides T6 multi-root sync. Next session: re-read this gap before attempting moves.
- **Lanes sign-off delivered:** `sandbox/orthogonality_001_wrapper_split/T1_SIGNOFF_V9.md` (225 files: 70 agentx / 146 harness_meta / 5 review / 4 exclude; 40 LIT + 7 product-DEPTH pre-move fixes listed; mirror-move rule keeps `parents[N]` depth-safe). Zero files moved (grandfather rule stands).

### Next

- Per-bucket lanes moves per the sign-off table (each: move + LIT fixes + suite green + canary) → T2 goldens in the new lanes → T6 multi-root sync + 4 project relocations.
