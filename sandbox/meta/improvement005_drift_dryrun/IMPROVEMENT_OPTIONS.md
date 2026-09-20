# IMPROVEMENT_OPTIONS — drift dry-run fix preview (IDEA from improvement004 SUGGESTED NEXT)

> Workflow: `.workflows/meta_harness/loops/meta_harness_evolution.md` — step 3 proposal (sandbox only).
> Trigger: user pick `IDEA: drift dry-run` from OPT-B demo + live drift 17 records.
> Fresh-start: toolbox only (`omt_net probe` rev60 drained_complete, `omt_q drift` 17, `omt_status`), no src search.

## 1. Problem

`omt_q drift` reports 17 actionable records but every fix is a mutating CLI (`project.py link/sync/close`, WORK.md sync) with no preview. Agent either (a) describes fixes in prose (unverifiable) or (b) runs them blind (risky, unauditable). SUGGESTED NEXT (improvement004 OPT-B) needs a trustworthy action behind each suggestion — a dry-run diff that shows *exactly* what would change before the approval gate.

Live cases right now:
- `unlinked-project-backed ×11` (10× feature_kb_akb + 1× meta.workflows_definition_layer) — fix is 2× `link` cmds.
- `aging-draft ×2` (feature_kb_akb, workflows — 28d, no linked features) — fix is triage (scope or archive), NOT auto-linkable.
- `iteration-log ×5` (concurrent, mh2/3/5, net_enforced — PROJECT.md newer than top log) — fix is `log` append or PROJECT.md revert, needs human judgment.

A blind auto-fix would mis-fire on classes 2–3. Hence preview-first.

## 2. Options

### OPT-A — Minimal: `--dry-run` flag on existing mutators, prose diff
- Add `--dry-run` to `project.py link/sync` + document `omt_q drift` detail lines as the preview source. Agent pastes planned cmds in SUGGESTED NEXT, user approves, agent re-runs without flag.
- Pros: smallest diff, no new tool/op, fits token diet (0 new schemas).
- Cons: prose, not machine-checkable; no rev guard (TOCTOU between preview and apply); no net↔ledger↔git re-check; iteration-log/aging still need prose judgment.
- Cost: S/M. Good as stopgap.

### OPT-B — Structured preview op (RECOMMENDED): `omt_q op=fix_preview` ⭐
- New read-only op (no new gate — `gates max 10/12` untouched): input = drift class filter; output = deterministic DSL diff, e.g.
  ```
  preview rev:60
  - link feature_kb_akb → feature_kb_akb (ledger project_link +1, clears 10 drift)
  - link meta.workflows_definition_layer → workflows (ledger +1, clears 1 drift)
  - SKIP aging-draft:feature_kb_akb (needs scope/archive — human pick)
  - SKIP iteration-log ×5 (needs log entry — human pick)
  apply: <exact cmds with expected_revision:60>
  ```
- Contract: preview carries `expected_revision`; apply refuses on stale rev (same pattern as `omt_net fire`); net `invariant` re-runs post-apply in the same transaction description. Never auto-applied — SUGGESTED NEXT renders the preview, approval gate executes.
- Pros: machine-readable, rev-safe, auditable; makes OPT-B startup suggestions actionable; token-cheap per session (one op call replaces 2–3 explain rounds); DSL-first per strategy rule 3.
- Cons: new op + tests + nav index entry (budget `nav_index 65862/66560` — 698B headroom, fits one record); needs `harnessc check/build` + e2e receipt round.
- Cost: M. Pays back in 2–3 sessions (11 drift clearable in 2 cmds once preview is trusted).
- Execution: `.meta/META_HARNESS.omt` (`@tool omt_q` args + `@doc` record) → `build` → e2e → goldens for the 3 drift classes above.

### OPT-C — Full auto-fix daemon with journal
- Preview + atomic apply + transaction journal + `invariant` triple-check + auto `CURRENT_STATE.md` log append. Closest to `omt_net synthesize/mine` authority model.
- Pros: one-shot hygiene; strongest audit.
- Cons: largest surface (new splice-like authority, journal rotation, tombstone policy); overkill while pool is `drained_complete`; risks auto-firing on judgment classes (aging/iter-log).
- Cost: L. Defer until OPT-B wild usage N≥10 proves preview trust.

## 3. Recommendation

**OPT-B.** It turns the 17-record backlog into 2 safe auto-linkable actions + 7 human-picks with exact cmds, feeds directly into the new SUGGESTED NEXT section, and respects the improvement rules (DSL, token-min, flexibility, no new gate).

## 4. Approval gate (STOP)

Pick: **OPT-A** / **OPT-B** (recommended) / **OPT-C** / **defer**. On approval: edit ONLY `.meta/META_HARNESS.omt` → `check` → `build` → e2e → goldens for unlinked/aging/iter-log.

# Result (2026-09-20 — OPT-B executed)

- Approved: OPT-B preview op.
- Patched `.meta/META_HARNESS.omt` (tool omt_q +filter?/fix_preview, budgets tool_schemas 1920→2048 / tool_args 2464→2592, new `@doc q.fix_preview`) + `.opencode/plugins/omt_q.ts` (seed sync, filter arg, `fix_preview` case + read-only impl with unlinked→link alias) — 2-file round, think-consulted, one refresh.
- `check` OK 275/0, `build` OK 5 projections, e2e 1 passed (×2 rounds incl. filter fix).
- Live probe verified via bun: full preview (2 links + 2 aging SKIPs + iter-log SKIP + apply cmd rev60) and `filter:unlinked` subset correct.
- Backend is intentionally minimal/read-only (static mapping of the 3 live drift classes); full ledger-backed preview is the natural first feature for `agentx_concurrent_development`.
