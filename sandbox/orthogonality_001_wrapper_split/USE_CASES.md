# USE_CASES — orthogonality (sandbox copy) — refined v4

> Format per UC: Actor / Goal / Pre / Flow / Post / Alt. Pre = required setup.
> Post = observable proof. Alt = what happens on deviation.
> v4 note: re-measured 2026-10-10 ~16:00 UTC; v3 staleness corrected inline
> (ledger 5 rows not 2, test-file denominators, 5 bench hits, mvc_gate content,
> pending-moves populated, `link` syntax). T-gated steps are marked as such
> instead of reading as runnable today. No *conforming* `bridge:` tags exist yet (§1 format pin).

## UC0 — Delete sandbox, zero churn (runnable now)

- Actor: any dev. Goal: prove sandbox is proposal-only.
- Pre: sandbox unpromoted (no `.projects/` link, no ledger rows — true today: sandbox is untracked `??`, 2026-10-10; note `.projects/README.md` + `.projects/agentx/` are equally untracked, so promotion must carry them or drop the mirror).
- Flow: `rm -rf sandbox/orthogonality_001_wrapper_split` → `git status` → `uv run pytest --collect-only -q` (count unchanged: 2103/2105 baseline 2026-10-10).
- Post: `git status` shows only the deletion; suite count identical; no manifest churn.
- Alt: if promoted (UC8 done), deletion requires ledger close-out — UC0 no longer applies.
- Honesty note: the proof is trivially true *because* the sandbox is invisible to the harness (no tracking: `project.py status`, `workc`, nav index ignore it). It proves isolation, not value.

## UC1 — Product fix with harness absent (T-gated)

- Actor: AgentX dev. Goal: fix REPL bug with zero harness.
- Pre: four harness dirs renamed away — `scripts/omt/`, `scripts/session_inspect/`, `.opencode/`, `.meta/` (there is no top-level `harness/`; "rename harness away" without this list is unactionable). Product lane present.
- Flow: `uv run pytest tests/agentx` → edit `src/agentx/…` (no `omt_phase`) → green → ship product bump.
- Post: boundary golden green (import-statement regex finds no `scripts.omt`/`.meta`/`opencode` runtime imports from the product lane; `scripts/omt/bench/tasks.py` exemptions pinned: `:32,:44` fixture-strings + `:11,:12,:35` path-strings — v3 listed only 2 of the 5 substring hits).
- Alt: harness runtime import found → boundary test red, fix rejected before merge.
- Gate: **blocked until T1/T2/T3 land** — `tests/agentx/` does not exist today. Side note: renaming `.opencode/` away breaks the `omt_*` dev loop even if product tests pass; the "workflow continues" half of this UC needs its own proof. Grandfather backlog: `src/agentx/ui/test_omt_mvc_gate.py` (53 bytes: a real `from agentx.model.session import Session` + `print('ok')`, zero test functions — v3's "2-line print" understated it) must be deleted or moved with a real assertion in T1, or this UC's Post is self-falsified.

## UC2 — Harness fix with product frozen (T-gated)

- Actor: harness dev. Goal: fix `tdd_hats` coercion without touching product.
- Pre: `src/agentx/` frozen (read-only checkout or clean tree + no product diff).
- Flow: `uv run pytest tests/harness_meta/tdd_meta` red → edit `.opencode/lib/enforcer/tdd_hats.ts` only (prior doc path `harness/enforcer/tdd_hats.ts` was wrong) → per-mechanic receipt green → bump tdd slice only.
- Post: startup A–J IDs stable (record file rev + live rev — they diverge today: `WORK.compiled.md` rev 60 vs live rev 0); product suite untouched and still green.
- Alt: product file touched → full `omt_phase` + product-lane re-run required.
- Gate: **blocked until T3/T5 land** — `tests/harness_meta/` does not exist and per-mechanic receipts are T5 design (global `g.receipt` guard still in force via `harnessc.py`).

## UC3 — TA inversion (T4-gated)

- Actor: harness analyst. Goal: annotate a product line without owning it.
- Pre: target line in `src/agentx/**` (exactly 30 `# TA:` lines / 18 files 2026-10-10 — v3 "≈" confirmed); `omt_think list` consulted.
- Flow: `omt_think add owner:harness` → TA-only diff bypasses phase, satisfies think-gate → `strip-TA === AST-identical` check green.
- Post: index holds `{location:product, owner:harness}`; product behaviour unchanged.
- Alt: logic touched alongside TA → bypass denied, full phase required.
- Gate: the `strip-TA` golden **does not exist today** (T4). The bypass rule is discipline-only until then.

## UC4 — Net down, work continues (two branches)

- Actor: any dev. Goal: keep shipping when the net is unavailable.
- Pre (branch A — never bootstrapped): `probe → net_not_bootstrapped` in `.meta/.omt`. Pre (branch B — down after bootstrap): `net.lock` held / supervisor unreachable, `live_marking` stale. (Prior v2 Pre quoted branch A as "live now" — true until the 2026-10-10 session bootstrapped rev 0; the doc rotted the same day. Both branches are now stated.)
- Flow: `preflight` marks `g.net` fail-open (one gate *verdict*, not "one predicate file" — core gate slice is `scripts/omt/net/{cli,gate,state,history,lock,sync_md}` inside a 20-file subsystem, v3 listed only the slice — plus `META_NET.petri.json` + `supervisor.overlay` + enforcer wiring at `gate_driver.ts:308-315,451-452`) → `omt_tdd red/green`, `omt_think` proceed normally.
- Post: only net ops (`fire`/`splice`/`claim`) blocked; everything else green.
- Alt: treating net as a hard requirement → all work stalls; this is the failure mode the fail-open verdict exists to prevent.

## UC5 — Lanes (T-gated)

- Actor: CI. Goal: prove each side stands alone + together.
- Pre: both lanes present (or one absent for the standalone proofs) — **not true today** (no lane dirs; `ls tests/agentx`, `ls tests/harness_meta` both absent 2026-10-10).
- Flow (three runs): `tests/agentx` with the four harness dirs absent → `tests/harness_meta` contract-pinned → nightly full + `opencode_live`.
- Post: three greens; failure is attributable to exactly one lane.
- Alt: single mixed run only → a harness break masks as a product break (current pain this proposal removes). Denominators for the audit: `rg --files tests/scripts` → 103 (71 in `omt/`), `tests/features` → 100 — v3's 206/189 are retired.

## UC6 — New mechanic, no churn

- Actor: harness dev. Goal: add a mechanic without rebuilding the world.
- Pre: new slice needs CLI + pure predicate (over preflight snapshot — see PROPOSAL §3 correction, order numbers `gate_driver.ts:308-315`) + ledger kinds + tests + doc SECTION (one each).
- Flow: add CLI + predicate + `tests/harness_meta/foo_meta/` + doc SECTION → advisory (no `omt_` prefix) = zero *registry* rows (still one `opencode.jsonc` perm line + plugin file each — prior "zero rows" oversold; perms today gate only `reason_check`, not `reason_table`/`startup_table`) → per-slice receipt green (T5).
- Post: existing receipts still green; startup IDs unchanged (record file rev + live rev — they diverge today: `WORK.compiled.md` rev 60 vs live rev 0; ledger is 5 rows — re-count at signing, v3's "2 rows" rotted via its own refine).
- Alt: needs `omt_` prefix / registry row → goes through full harness-surface second-edit gate + e2e receipt.

## UC7 — Right home, right tests (+ `tools/` leg)

- Actor: any dev. Goal: put work where it belongs on the first try.
- Pre: new fix classified product vs harness vs bridge.
- Flow: `rag_v2` fix → `.projects/agentx/rag_v2`, code `src/agentx/model/rag_v2/`, tests `tests/agentx/`. Harness experiment on top logged in `.projects/meta/*_meta`, read-only on product traces.
- Post: home + code + tests agree (all product or all harness); bridge carries a conforming `bridge:` tag (no conforming tags exist yet — backlog for T1; substring `bridge:` hits in `meta_harness_11/PROJECT.md:50` + `idea-002` are prose, not tags).
- Alt: bridge without tag → review asks for owner-side move + tag before merge.
- Tri-home note: `petri_net_studio` spans `tools/petri-net-studio/` + `src/agentx/model/petri_net/` + `.projects/meta/petri_net_studio/` — v4 recommendation: scope `tools/` as product in T1 (one-line rule), studio PROJECT.md carries a conforming tag only for harness-driven analysis slices; UC7's Post checks all three legs for studio work.

## UC8 — Promotion with approval (the only way out of sandbox)

- Actor: you (owner). Goal: promote without silent churn.
- Pre: your explicit go (no auto-promotion, ever). Re-verify at promotion time: `git diff -- opencode.jsonc` (v4 found the `webfetch:deny` removal — must be resolved first), `wc -l .meta/.omt/ledger.jsonl` (5 at v4, will grow), `git status --short` (four untracked/modified paths at v4).
- Flow: manual scaffold `.projects/agentx/harness_wrapper_split/{PROJECT.md,CURRENT_STATE.md}` → `project.py link <feature> <project> --origin manual` for each pending move (flag verified `--origin {backfill,inferred,manual,scaffold}`; v3's bare `link --origin manual` omitted the required feature/project args — fixed) → ledger records → multi-root sync only after T6 lands. (`project.py new` targets `.projects/meta/` by default with no root-override flag — `rg OMT_PROJECTS_ROOT` → no hits, verified; never run `sync` with a root override before T6. The four pending moves are listed — populated, not "empty-by-design" — in `.projects/agentx/META.md`.)
- Post: `.projects/agentx/` populated; `WORK.md ## Projects` covers both homes; sandbox deleted via UC0 or archived.
- Alt: `sync` with a root override before T6 → `WORK.md` clobbered to one home; recovery = re-sync from `.projects/meta/`.
