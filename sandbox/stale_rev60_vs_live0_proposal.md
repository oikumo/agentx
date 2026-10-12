# STALE rev60-vs-live rev0 — reconciliation proposal (harness_wrapper_split close-tail A)

> Program: harness_wrapper_split (active, .projects/agentx/) — T1-T6 + Oracle DONE, HEAD 8965049
> Baseline: WORK.md net_rev:60 Pool 0/0/7 places 15/15 Options 11 NEXT proj:agentx_concurrent_development
> Live: sidecar rev0 2026-10-10T15:45:34 marking [1,1,0,1,1,1,1] (7 places, no work_*, no fNNN_ bindings) idle_empty menu next:none
> Freshness: stamped 0 vs live 0 fresh=true (sidecar-vs-live, NOT file-vs-live) — file-vs-live STALE by construction after bootstrap
> Evidence: probe max_states=100 enabled[] tasks[] coverage 0/0/0, push tasks_block net_rev:0 NEXT options[0] (same NEXT), invariant hold true drift false, sync proposal 141 pending subnets, drift phantom-link x10 (incl 138,152), fix_preview rev:60 nothing linkable

## Why bare net_to_md is unsafe (dry-run)
- render_tasks_block (sync_md.py:130): enabled=[] → NEXT=options[0] (same), but is_pool_net false → Pool line DELETED, rev 60→0 downgrade, per-subnet rows none
- TA gotcha sync_md.py:144: REPLACES region net_rev→## Projects — Pool 7-done + 15/15 evidence lost
- md_to_net_propose: 141 add_subnets pending → floods live 7-place net, D4 never auto-applied, needs conformance + e2e

## Alternatives
- A1 (recommended, doc-only): No net/file mutation. Record both revs in CURRENT_STATE + next pause, keep file rev60 authoritative for menu, live rev0 idle expected. Re-run workc check + harnessc check to prove no drift. Cost: 0 risk.
- A2 (surgical annotation): A1 + one-line STALE note in WORK.md Tasks (outside replaced region? must go AFTER ## Projects per gotcha — e.g. ## Paused tail) + workc build. Preserves menu, makes STALE explicit. Needs preflight clear (verified 0/8).
- A3 (safe resync, heavy): Migrate live to pool template (15 places, restore 7 done) via splice + ledger net_* + prove/verify + e2e receipt. Requires major_feature + design doc + TDD, high ceremony. Only if menu/net agreement work demands live WIP.
- A4 (DISCOURAGED, listed for completeness): Bare sync net_to_md. Demonstrates clobber, do NOT pick without explicit override.

## Approval gate
- Pick A1/A2/A3/A4. No mutation until pick. Execute writes result back here.
- Suggested: A1 now (close tail stays green), A2 if you want file-explicit STALE, defer A3 to menu/net agreement project.

## Result
- A1 executed 2026-10-12a (docs Analysis): no net/file mutation, both revs recorded in CURRENT_STATE ##2026-10-12a, file rev60 authoritative, live rev0 idle expected. Checks: workc ok fresh 11 lines, harnessc OK 282/0 work_md 10983/11264.
