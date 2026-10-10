# EXECUTE_V8 — re-verify-only execution record (sandbox only, no promotion, no moves)

> Status: **execution record** (2026-10-10, re-verify-only scope per your go).
> Canonical stays `PROPOSAL_V7.md`. Baselines frozen: `PROPOSAL.md` v4,
> `USE_CASES.md` v4, `CRITIQUE_V5.md`, `REFINE_V6.md`.
> This file writes nothing outside `sandbox/` (UC0 unaffected — no deletion done).
> Next move (T1 audit or Oracle scaffold or UC8 promotion) needs a fresh explicit go.

## 0. Preflight + scope

- Preflight: `omt_status{op:preflight, path:sandbox/.../EXECUTE_V8.md, tool:edit}` → all clear (0/7 fire).
- Scope done in this pass: read-only §9 re-measure + this plan file. Zero `src/`,
  `tests/`, `.projects/`, `.meta/`, `.opencode/` writes. No `omt_phase` needed
  (no src edits); no `omt_skip` canary needed (no `tests/` moves).

## 1. Re-verification (2026-10-10T17:40:38Z sweep — re-count at signing, never pin)

| # | V7 baseline (§9) | Re-measured now | Verdict |
|---|---|---|---|
| git tree | `M opencode.jsonc` + 3× `??` (V6) | clean, ahead `origin/main` by 1 (`56e470a` test-speed 72s→42s) | CHANGED — Q5 resolved, sandbox committed |
| sandbox | untracked `??`, invisible to harness | TRACKED: 8 files in `git ls-files` | STALE premise — UC0 "trivially true" no longer holds; deletion = tracked deletion + commit + ledger close-out (UC0 Alt applies) |
| Q5 webfetch | `M opencode.jsonc` (`-"webfetch":"deny"`) | `opencode.jsonc:102 "webfetch":"deny"` present; `git diff -- opencode.jsonc` empty; AGENTS + `META_HARNESS.omt:74,145` agree | RESOLVED — promotion pre-check now clean |
| ledger | 9 rows (V6, think_consult/net_sync kinds) | **10 rows** at `2026-10-10T17:40:38Z` via `wc -l`; kinds `q/audit/phase/complete` only (10th = `complete feature_999.x Testing`) | RE-BASELINED — old think_consult history rotated; observer-effect rule holds: format "`N` rows at `<date -u>` via `wc -l`" |
| suite | 2103/2105 (2 deselected) | **2103/2105 (2 deselected) in 5.53s** via `uv run pytest --collect-only -q` | HOLDS (collect faster after speed pass) |
| tests/scripts | 103 (`rg --files`) | **104** | +1 — HEAD added `tests/scripts/toolbox/hermetic_toolbox.py`; T1 audit denominator updates to 104 |
| tests/scripts/omt | 71 | 71 | HOLDS |
| tests/features | 100 | 100 | HOLDS |
| lanes | both absent | `tests/agentx/*` none, `tests/harness_meta/*` none | HOLDS — T1/T2/T3 still T-gated |
| plugins | 11 files for 14 tools | 11 | HOLDS |
| perms | 11 `omt_*` + `reason_check` (12 lines) | 11 `omt_*` + `reason_check`; `grep -c omt_` = 13 (11 perms + 2 comment lines) | HOLDS |
| enforcer lib | 12 | 12 | HOLDS |
| scripts/omt CLIs | 13 | 13 | HOLDS |
| net | 21 inc `__init__` (20 modules) | 21 | HOLDS — 20+1 pin stands |
| `.meta/.omt/` | 7 files | **12 entries**: `harness.ir.json, harness.report, kb.index.jsonl, kb.ir.json, ledger-202610.jsonl, ledger.jsonl, META_NET.petri.json, nav.index.jsonl, net_state.sidecar.json, net.lock, omt_harness_e2e_last_run.json, supervisor.overlay.json` | CHANGED — 5 new files; T2 projection pin (Q4) must re-list before any "read-only" claim |
| TA | 30 lines / 18 files | 30 / 18 | HOLDS — T4 still open, no strip test |
| mvc_gate | real import + `print`, 0 fns | `from agentx.model.session import Session` + `print('ok')`, 2 lines | HOLDS — T1 row #1 still open |
| bridge tags | 0 conforming (1 prose `meta_harness_11:50`) | 1 prose hit, same line | HOLDS — backlog for T1 |
| pending-moves | 4-row draft | same 4 rows | HOLDS |
| startup revs | file rev 60 NEXT=`agentx_concurrent_development` vs live rev 0 `next:none` | file rev 60 (unchanged) vs live rev 0 `idle_empty` (this session probe) | HOLDS — STALE by construction; record both revs in every receipt |
| unchecked | DSL 277, 52 dirs, idea-002, tool-map | not re-run in V8 | CARRIED — verify or drop before promotion |

## 2. T1–T7 + Oracle plan (deferred — needs fresh go + gates each)

- T1 audit (first, sandbox-plan only until go): legacy slug + test-file mapping over
  `tests/scripts (104) + tests/features (100)` **plus** `tests_automated/, tests/test_sandbox/,`
  `toolbox/ tests, tools/*/tests, .sandbox/` (one scope-or-exclude line each); build roots
  (`pyproject/uv.lock/.venv/.python-version`) as shared prerequisite; `.workflows/` scope line
  (catalog above harness); `.meta/.omt/` 12-file projection re-pin; file→tool map
  (`phase/skip/complete/tdd` provider); conforming-`bridge:` backlog (0 today); `tools/`-as-product
  + `shared/`-as-contract scoping; T1 row #1 `test_omt_mvc_gate.py` delete-or-move-with-assertion.
  Gate: `omt_phase` + `omt_skip{scope:tests}` canary where it touches `tests/`.
- T2 boundary goldens: AST import firewall (Python `ast` + TS imports, versioned exemption
  manifest incl. bench fixture-strings + path-strings) + ledger projection contract pin +
  read-only test. Template: studio `check-independence + conformance`.
- T3 lanes CI: split runs + nightly full + `opencode_live`; build-roots prerequisite declared.
- T4 TA strip golden: Python `ast.dump`-identical + TS `tsc --noEmit` + snapshot rule.
- T5 per-mechanic receipts: slice-by-slice design first; global `g.receipt` still guards.
- T6 multi-root sync: both homes without clobbering `WORK.md ## Projects`.
- T7 Oracle `split_proof_meta` v2 (§E V7): `prove --lane both` → 2 certs + `verify`
  byte-identical + `attest-bridge` (studio slices only) + `newcomer-probe` (`uv run agentx` → `c`).
  Advisory CLI, zero registry rows (`reason_check` precedent); CI-strict / local-advisory;
  ephemeral overlay; hash-chained certs. Only executable close — still design until E4 lands.
- Each T: own canary (tests/harness-surface) + `omt_session` evidence
  (`capture/profile/query`) or benchmark golden + real-token measurement for cost claims +
  newcomer-cost check ("student still `uv run agentx` → `c` with zero harness knowledge?").

## 3. Promotion (UC8 — NOT executed, on your explicit go only)

Manual scaffold `.projects/agentx/harness_wrapper_split/{PROJECT.md,CURRENT_STATE.md}` →
`project.py link <feature> <project> --origin manual` per pending move (feature-first) →
ledger records → multi-root sync only after T6. Never `project.py new` into
`.projects/agentx/`; never `sync` with root override before T6. Pre-checks at signing:
`git diff -- opencode.jsonc` (now clean) + `wc -l ledger.jsonl` + `git status --short` +
file rev + live rev. Sandbox retained until then (no UC0 deletion done — now tracked,
so UC0 needs commit + close-out when/if ever taken).
