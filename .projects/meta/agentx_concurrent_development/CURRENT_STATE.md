# CURRENT_STATE: agentx_concurrent_development

> Session-by-session log + resume point. Companion to `PROJECT.md` (canonical).
> Newest entry on top. One `## <date>` block per session.

---

## 2026-09-20 (auto — feature_119.ledger_backed_fix_preview Done)

- shipped: minor_feature · test report @ 6.testing/features/feature_119.ledger_backed_fix_preview/test_report.md
- logged by omt_complete; expand by hand if resume needs more.

---


## 2026-09-20 (iter 2 — scope drafted + drift-preview OPT-B shipped)

### Done

- PROJECT.md §§ Quick Start/Summary/Purpose/Scope drafted (sidecar 2-worker agreement; success = 2 concurrent claimed/fired/joined, invariant clean).
- improvement005 OPT-B executed: `omt_q fix_preview(filter?)` read-only rev-pinned DSL diff (2 links + SKIPs + apply cmd); check 275/0, build 5 projections, e2e green, bun-probe verified (full + unlinked filter).

### In progress / Blocked

- Nothing active (pool drained_complete rev60). First linked feature not yet spawned — needs user go-ahead.

### Next

- Spawn first feature (`new_feature.py --project agentx_concurrent_development`): candidate A = ledger-backed fix_preview (replace static map); candidate B = first 2-worker sidecar trial. Pick one.

---

## 2026-09-12 (iter 0 — project created)

### Done

- Project home created (`project.py new`, state: draft).

### In progress / Blocked

- _(nothing)_

### Next

- <!-- the single next action -->

### Notes / context

- Resume entry point: `PROJECT.md` §New Session Quick Start → this entry → §Next.
