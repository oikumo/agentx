# Global state (P1 advisory projection — read-only, never authority)
`rev 57 @ f66d268d4682 · built 2026-09-18T15:25:39+00:00` (per-section as-of; no global as-of)

## tasks — pool {'pending': 0, 'active': 0, 'done': 7} · marking {'work_pending': 0, 'work_active': 0, 'work_done': 7}
resources {'free': 5, 'total': 5} · workers {'workers_used': 0, 'workers_total': 2, 'free': 2} · NEXT: none

## divergence — projection(B) vs marking(M): omissions, never firings
| B vs M: pending 0/0, active 0/0, done 7/7 — agree, no fired transition (OMISSION class) |
| omissions: claim_task/recovery/lane via _move_pool_token scripts/omt/net/state.py:819-834,scripts/omt/net/state.py:837+ (claim_task); absent-lane scripts/omt/net/state.py:296-300 vs fire() :763-768 — never firings |
| crash: clear-before-record scripts/omt/net/state.py:730-742 vs WAL :672-675 — P1 never depends on replay |

## join keys — WORK.md pool rows <-> ledger `feature` slug <-> net task bindings `id` <-> project slugs (`.projects/meta/<slug>`). C4 residual: identities differ per domain — rows without a shared key are juxtaposed, flagged `join:unmatched`, never interpolated.

## workflows — subjects ['agentx', 'app_knowledge_base', 'meta_harness'] · last round `.sandbox/meta_harness_8_idea_r2.md`
(doc-shaped domain: catalog is agent-read markdown, zero machine state; catalog position + round pointer only)

## features — phases 2 tracked (join key = feature slug; `join:unmatched` never interpolated)

## projects (derived sync rows — never source)
- meta_harness_10 (active) · feature_102.mh10_p1_global_projection
- petri_net_studio (active) · feature_032.petri_net_format, feature_033.petri_net_io +4 more
- project_lifecycle (active) · feature_030.project_lifecycle
- rag_v2 (active) · feature_027.rag_v2, feature_029.rag_v2_slash_commands
- agentx_concurrent_development (draft) · —
- feature_kb_akb (draft) · —
… continued in projection.json (cap 2KB; cut at line boundary)
