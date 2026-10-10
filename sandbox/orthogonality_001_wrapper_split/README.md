# Sandbox project: orthogonality_001_wrapper_split (bridge demo) — v4 + V5 critique + V6 oracle + V7 canonical

> Context: agentx 0.2.0 = console REPL (chat/rag/fast-agent/advanced-agent/react/coding/models) + Petri Net Studio + 2103/2105 tests collected 2026-10-10 (2 deselected). Developed with opencode under META HARNESS (OMT++ Analysis→Design→Programming→Testing, 11 `omt_*` tools + 3 advisory tools in 11 plugin files, IR-ordered gates at `gate_driver.ts:308-315,451-452`, `WORK.compiled.md` rev 60 / live net rev 0 bootstrapped 2026-10-10, ledger timestamped — re-count at signing, never pin).
> This sandbox project changes nothing outside `sandbox/` — proposal only.
> Status: **draft proposal** (V7 canonical 2026-10-10, no approval, no promotion, no moves). v4 / V5 / V6 frozen as baselines; `PROPOSAL_V7.md` is canonical.

## Layout demo (mirrors the proposed split)

- `meta/` — harness-only notes (`*_meta` suffix for new items). See `meta/README.md`.
- `agentx/` — product-only notes (no `meta` affix). See `agentx/README.md`.
- This `README.md` is the bridge tag: owner = harness, location = sandbox.
- Homes reference: untracked draft at `.projects/README.md` — this sandbox **inlines**
  the rule with measurements and wins on conflict until both are promoted together.
  Do not cite `.projects/README.md` as canonical (it is `??` unreviewed and contains
  the unexecutable `OMT_PROJECTS_ROOT` line — see PROPOSAL §1).

## What this sandbox holds

- `PROPOSAL_V7.md` — **canonical V7**: merges v4+V5+V6, closes Q2 as decision (tools/ product + shared/ contract), pins denominators + ledger-count rule + 20+1 net pin, adds Oracle v2 `split_proof_meta` (CLI + predicate + kinds + tests + SECTION, CI-strict/local-advisory, ephemeral overlay, hash-chained certs, AST firewall, newcomer probe), T1–T7 plan with evidence + newcomer checks, executable acceptance, promotion via UC8 only.
- `PROPOSAL.md` — homes + `meta`-suffix rule + testing lanes + orthogonal mechanics (as verdicts, §3) + non-goals + migration (T1–T6 deferred) + T-gated acceptance + open questions (now 5, incl. `opencode.jsonc` webfetch-deny drift) + verification log with v4 re-measurement. **Frozen baseline — see V7 for canonical.**
- `USE_CASES.md` — 9 use cases: UC0 delete-guarantee, UC1–UC7 boundary behaviour, UC8 promotion-with-approval. Each: Actor / Goal / Pre / Flow / Post / Alt. T-gated steps marked as such; v3 staleness fixed in v4 (ledger rows, `link` syntax with feature/project args, 5 bench hits, mvc_gate content, populated pending-moves).
- `meta/README.md` + `agentx/README.md` — labelled placeholders proving folder separation is *readable* with zero tooling changes. Readability ≠ enforceability: enforcement is T1 (audit) + T2 (boundary goldens), both deferred.

## Guarantees

- No `src/`, `tests/`, `.projects/`, `.meta/`, `.opencode/` writes from this project (v4 verified: `git status` shows only the pre-existing `M opencode.jsonc` drift + three `??` paths, none authored by this sandbox).
- Delete with `rm -rf sandbox/orthogonality_001_wrapper_split` — no ledger records, no manifest churn (see UC0; trivially true while untracked — isolation proof, not value proof).
- Promotion path (only with your explicit go): manual scaffold under `.projects/agentx/` + `harness_wrapper_split` PROJECT.md via `project.py link <feature> <project> --origin manual`. No `sync` with a root override until multi-root lands (it would clobber `WORK.md ## Projects`). Pre-promotion re-checks (v4): `git diff -- opencode.jsonc`, `wc -l ledger.jsonl`, `git status --short`. See UC8.

## Refinement log

- v7 (this, 2026-10-10): canonical rewrite — new `PROPOSAL_V7.md` (runtime-orthogonal/dev-coupled language, D-tri decision closing Q2, full test-scope + build-roots prerequisite, 20+1 net pin, file→tool map admission, TA T4 close via Oracle, ledger-count + STALE-rev rules, T1–T7 with evidence/newcomer/canary per T, Oracle v2 E1–E5 CI-strict/local-advisory with ephemeral overlay + hash-chained certs + AST firewall + newcomer probe, vision fit, UC8 promotion only). v4/V5/V6 frozen. No src/tests/projects writes; `write` + 3 `edit` in sandbox only (preflight clear, 0 TA thoughts).

- v6 (prior, 2026-10-10): workspace-deep critical rewrite + SOTA Oracle — `REFINE_V6.md` (30-entry root, fourth leg `shared/`, build-roots + workflows-above-harness scoping, harder verdicts B9–B10, vision alignment with token budgets + harness_reason numbers, D1–D10 sharpened, `split_proof_meta` E1–E5 design, re-verification §F). Frozen baseline.

- v5 (prior, 2026-10-10 ~16:20 UTC): critical-revision addendum — new `CRITIQUE_V5.md` (workspace deep analysis + claim-by-claim verdicts + root-README vision alignment + 10 required fixes + re-verification log). PROPOSAL/USE_CASES v4 frozen as baselines. Key deltas: "runtime-orthogonal, dev-coupled" language; ledger 9 rows (5 rotted again — never pin counts without timestamp); net 21 files inc `__init__` (20 modules); Q5 webfetch drift still open; tri-home → decision (tools/ as product + shared/ as contract, studio as exemplar); T-scope gaps (tests_automated/test_sandbox/toolbox/tools-tests/build roots); evidence-per-T + newcomer-cost check.

- v1 (prior): terse PROPOSAL (4 sections) + terse USE_CASES (7 one-liners) + empty `meta/`, `agentx/`.
- v2 (prior): terminology pinned, non-goals + migration + acceptance + open questions added; UCs structured + UC0/UC8 added; folder placeholders labelled. Aspirational wording presented as fact — the v3 pass below corrects that with measurements.
- v3 (prior, 2026-10-10): critical-revision pass. Pinned real paths/counts; corrected "pure predicates, no I/O" → ordered predicates over preflight snapshot; "one predicate" → one `g.net` verdict; per-mechanic receipts → T5 design; acceptance → T-gated; UC4 two-branch Pre; UC8 manual-scaffold flow; `petri_net_studio` tri-home admitted; `bridge:`-tag backlog + `test_omt_mvc_gate.py` counterexample + verification log added.
- v4 (this, 2026-10-10 ~16:00 UTC): second critical pass — v3 fact-checked against the live tree. Fixed: 14 tools **in 11 files** (not "14 plugins"); test denominators `rg --files` 103/100/71 (not 206/189); net subsystem 20 files (not 6); bench 5 hits with path-string class (not 2); mvc_gate real content (`from agentx…import Session` + `print`, not "2-line print"); pending-moves **populated 4 rows** (not "empty-by-design"); `bridge:` format pin (prose hits in `meta_harness_11` + `idea-002` are not tags); `link` arg order (`link <feature> <project> --origin manual`); ledger 5 rows (v3's "2 rows" rotted via its own refine — observer effect); mirror note demoted (`.projects/README.md` untracked + `OMT_PROJECTS_ROOT` unexecutable); NEW Q5 `opencode.jsonc` webfetch-deny removal drift; enforcer order numbers cited; Q2 → recommendation (scope `tools/` as product). No semantic change to the split intent — honesty and testability only.
