# divergence — projection(B) vs marking(M)

| `pending` pool(B)=0 | `work_pending`(M)=0 | fired? no (OMISSION class — counts agreeing with no fired transition) |
| `active` pool(B)=0 | `work_active`(M)=0 | fired? no (OMISSION class — counts agreeing with no fired transition) |
| `done` pool(B)=7 | `work_done`(M)=7 | fired? no (OMISSION class — counts agreeing with no fired transition) |
| known omission paths | `claim_task`/recovery/lane/integration via `_move_pool_token` scripts/omt/net/state.py:819-834,scripts/omt/net/state.py:837+ (claim_task); absent-lane binding-only scripts/omt/net/state.py:296-300 vs fire() :763-768 | counted as OMISSIONS, never firings |
| crash window | clear-before-record scripts/omt/net/state.py:730-742 vs WAL :672-675 — P1 never depends on replay surviving it | carried residual |

_Known paths are OMISSIONS (never firings)._
