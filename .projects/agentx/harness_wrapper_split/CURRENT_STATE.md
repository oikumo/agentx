# CURRENT_STATE: harness_wrapper_split

> Session-by-session log + resume point. Companion to `PROJECT.md` (canonical).
> Newest entry on top. One `## <date>` block per session.

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
