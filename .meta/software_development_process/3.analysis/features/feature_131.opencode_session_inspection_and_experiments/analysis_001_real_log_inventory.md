# Analysis 001 — Real-log inventory (M1)

Feature: `feature_131.opencode_session_inspection_and_experiments` · Phase: Analysis · Date: 2026-09-26
Source of truth: live `~/.local/share/opencode/opencode.db` (3.2 GB, WAL mode, `-shm`/`-wal` present), opened read-only (`file:...?mode=ro`) for every query below. Counts: **1850 sessions · 46,678 messages · 192,947 parts · 470,827 events**. All evidence queries are reproducible against that DB; no content was copied into tracked fixtures (raw captures stay out of the repo; sanitized extracts only).

## 1. Adapter scope: OpenCode SQLite schema (verified 2026-09-26)

Tables that matter to inspection, with observed role:

| Table | Rows (obs.) | Role |
|---|---|---|
| `session` | 1850 | Root record: identity, hierarchy (`parent_id`), `directory`, `title`, model/agent, cumulative token/cost columns, lifecycle timestamps. |
| `message` | 46,678 | One row per user/assistant message; `data` JSON carries role, `parentID`, per-message `tokens`, `cost`, model. |
| `part` | 192,947 | Typed parts attached to messages (`step-start`, `step-finish`, `tool`, `text`, `reasoning`, `patch`, `file`, `compaction`, `agent`). |
| `event` / `event_sequence` | 470,827 | Append-only per-session update stream (`aggregate_id` = session id, per-aggregate `seq`); carries full part/message JSON payloads → viable incremental-capture cursor. |
| `session_message` | 23 | Session-level entries, type `model-switched` only (observed), unique `(session_id, seq)`. |
| `session_input` | **0** | Auxiliary prompt table — **empty in the real DB**. Label binding MUST NOT depend on it. |
| `project`, `project_directory`, `workspace` | — | Project/worktree/directory grouping (`session.directory` observed to be the practical filter: 1717 rows for this repo's abs path). |
| `todo` | — | Per-session todo list; candidate future surface, out of M1 scope. |
| `__drizzle_migrations`, `data_migration`, `migration`, `account*`, `credential`, `permission`, `session_share`, `session_context_epoch` | — | Schema/version discovery + out-of-scope domains. Capability discovery: `__drizzle_migrations` latest `created_at` = `1778520877000` (ms) + row count; `data_migration` = 2 named completed rows. |

## 2. Field-by-field mapping — real session record (`session` row)

| Source field | Observed shape / unit | Normalized meaning |
|---|---|---|
| `id` | `ses_<base62>` | session_id (stable identity) |
| `parent_id` | NULL (1751 roots) / `ses_...` (99 children) | hierarchy link; child = subagent session |
| `directory`, `project_id`, `workspace_id` | abs path / id / id | project scoping; `directory` = practical filter |
| `title` | free text; **label echo observed** (e.g. `[harness_reason:discharge arm=harness case=H1] (@general subagent)`) | convenience only, never the attribution key |
| `agent` | `build`(1551), `explore`(59), `general`(26), `plan`(1), ''(213) | agent name |
| `model` | JSON `{"id":"z-ai/glm-5.3","providerID":"nvidia","variant":"max"}` | normalize to (model_id, provider_id, variant) |
| `time_created`, `time_updated`, `time_compacting`, `time_archived` | epoch **milliseconds** (verified: feature_130 test report §"Latency units" supersedes the ×1000 formula) | wall-clock anchors; `latency_ms = time_updated − time_created` |
| `tokens_input`, `tokens_output`, `tokens_reasoning`, `tokens_cache_read`, `tokens_cache_write`, `cost` | integer counters (defaults 0), `cost` real (observed 0.0) | **session cumulative basis**; `input` excludes `cache_read` |

## 3. Field-by-field mapping — message + parts

`message.data` (assistant): `{"parentID","role","mode","agent","variant","path"{cwd,root},"cost","tokens"{total,input,output,reasoning,cache{read,write}},"modelID","providerID","time"{created}}`. Observed semantics:

- **Turn pairing:** both assistant messages of one user turn share `parentID` = the user message id → `parentID` is the *turn* link, not a linear predecessor chain.
- **User messages carry no `tokens`** (keys absent) — usage lives on assistant messages only.
- **Per-message tokens are per-generation increments** (not cumulative): msg₁ `input 100, output 18, cache.read 9920, total 10038` = 100+18+9920 ✓.
- **KEY AMBIGUITY A1 (verified, quantified):** of 40,096 nonzero-token assistant messages, **39,421 satisfy `total = input+output+reasoning+cache.read+cache.write`** but **675 satisfy `total = input+output+cache.read` with `output ⊇ reasoning`** (e.g. `total 16367 = input 15615 + output 752` where `reasoning 704` is already inside `output 752`). Two reporting variants coexist in one DB. An adapter must compute the per-message variant (residual test) and expose it; a metric definition must never blind-sum `output + reasoning`.
- **Reconciliation verified:** on all 6 sampled mid-size sessions, session cumulative columns equal per-message sums exactly (e.g. `tokens_input 51105 = Σ message.tokens.input 51105`, incl. output/reasoning/cache_read). Session-total and message-sum bases reconcile when inclusion variant is respected. Samples had `reasoning=0`; A2 below tracks the reasoning-bearing case.
- **Valid zeros:** assistant messages with all-zero token objects exist (aborted/empty steps) — keep, never zero-fill-detect.

Part taxonomy (`part.data.type`, counts across DB): `tool` 49,811 · `step-start` 41,055 · `step-finish` 40,740 · `reasoning` 27,123 · `text` 24,417 · `patch` 9,148 · `file` 632 · `compaction` 23 · `agent` 5.

| Part type | Observed payload | Notes |
|---|---|---|
| `step-start` | `{"snapshot":"<sha1>","type":"step-start"}` | snapshot = repo commit state marker |
| `step-finish` | `{"reason":"tool-calls","snapshot","tokens"{total,input,output,reasoning,cache{write,read}},"cost"}` | **per-step usage basis**; same A1 inclusion caveat applies |
| `tool` | `{"tool","callID","state"{status,input,metadata}}`; statuses observed: `completed` 48,480 · `error` 1,331 · `pending` 3 · `running` 6 | call identity + args + output; unfinished states mark live sessions |
| `reasoning` | `{"type":"reasoning","text":"..."}` | **recorded reasoning text IS stored and retrievable**; availability flag per part |
| `text` | `{"type":"text","text","time"{start,end}}` (ms) | content + generation interval |
| `patch` | `{"type":"patch","hash","files":[...]}` | file-edit witness (hash, paths) |
| `compaction` | `{"type":"compaction","auto":true}` | 23 parts across 10 sessions — compaction marker |
| `agent` | `{"type":"agent","name":"explore","source"{value,start,end}}` | subagent delegation marker in parent session |
| `file` | file parts | attachments (not deep-sampled in M1) |

## 4. Field-by-field mapping — legacy labeled capture (feature_130 discharge set)

All **6** labeled sessions verified present and complete, e.g. `ses_f204f9861ffeAbWzh4GTXkcRdZ` = `[harness_reason:discharge arm=harness case=H1] (@general subagent)`, agent `general`, model `z-ai/glm-5.3` (nvidia/max), `time_created 1790459275166`, `tokens_input 27362 · output 9123 · reasoning 7759 · cache_read 304128 · cost 0.0`.

- **Label location verified:** first `part` of the first user `message` starts byte-exact with the label line `[harness_reason:discharge arm=harness case=H1]\n\nYou are doing...` — **while `session_input` is empty** → label binding via message-part text is the correct primary path (the PROJECT.md requirement is confirmed by data).
- Title carries the same label as an echo (convenience). Grammar: `^\[harness_reason:discharge arm=(harness|planner|kernel) case=(H1|H3)\]`.
- All 6 are child sessions (`parent_id` NOT NULL) under this repo's directory; spawned in 2 batches (H1 @ ~1790459275166–281749, H3 @ ~1790460374046–383218 — the rotated order from the design is visible in `time_created`).
- Legacy token mapping (feature_130, preserved as explicit legacy metric): `prompt = input + cache_read`, `completion = output + reasoning`, `latency_ms = time_updated − time_created` (ms, post-correction).
- 6 sessions ↔ 6 labels, one-to-one — matches the harvest uniqueness rule; duplicates/foreign labels would have failed `harvest_label_conflict`.

## 5. Ambiguity register (recorded before coding assumptions)

- **A1 — dual inclusion semantics (CRITICAL):** `output ⊇ reasoning` on 675/40,096 messages; residual test required per message AND per step-finish; every derived metric must name its variant; never silently sum. Failure name: `inclusion_semantics_ambiguous`.
- **A2 — reasoning-bearing reconciliation:** session=Σmessage verified only on `reasoning=0` samples; must be verified on reasoning-bearing sessions with variant-aware summation before claiming exact reconciliation generally.
- **A3 — valid zeros:** all-zero token objects are real (aborted/empty steps); a zero is data, not "missing".
- **A4 — cost column:** observed 0.0 on all sampled sessions (local captures don't store monetary cost); treat as null-able counter with reason, never synthesize prices.
- **A5 — units:** all timestamps epoch ms (verified); `text` parts additionally carry `time.start/end` ms; do not re-derive units per adapter — assert ms once at adapter level.
- **A6 — deletion coverage:** storage is update-in-place; no tombstones observed → deletion detection is **unavailable**, must be reported as such.
- **A7 — liveness markers:** `pending`/`running` tool parts and absent completion evidence ⇒ session coverage is `incomplete` until proven otherwise.
- **A8 — ordering:** event `seq` (per aggregate) is the causal append order; timestamps (ms) are wall time; ties broken by stable id, never by invented causal order.
- **A9 — model normalization:** `model` JSON `{id, providerID, variant}` → `(model_id, provider_id, variant)`; `session_message` `model-switched` entries give in-session model changes (23 observed).
- **A10 — snapshot consistency:** live DB is WAL-backed; read with a single read transaction per capture; `immutable=1` is invalid here (active DB).

## 6. M1 contract seeds (input to design_001)

1. **Normalized record set:** `Session{ids, hierarchy, directory, agent, model triple, cumulative tokens/cost, timestamps, lifecycle flags}`, `Message{role, parentID, tokens?, model}`, `Part{type union with per-type payloads}`, `StepUsage`, `Label`, `TrialIdentity`. Stable ids preserved everywhere; epoch-ms asserted at adapter boundary.
2. **Token bases (three, never mixed):** session-cumulative · message-incremental · step-incremental (step-finish). Legacy metric `prompt/completion` preserved under an explicit versioned name. A1 residual test on every message/step before any derived sum.
3. **Label protocol v1 (from PROJECT.md §Label protocol):** `[mh13.experiment] {"v":1,...}` exact-prefix JSON lines; closed event set `trial_start|trial_end|span_start|span_end|checkpoint`; binding via first-user-message part text (verified path); legacy `[harness_reason:discharge ...]` adapter with explicit run mapping; echoes (titles, tool-output) never mint trials.
4. **Incremental capture:** `event` stream (`aggregate_id`, `seq`, full payloads) is the cursor basis; idempotent replay by seq; A6/A7 as named coverage findings.
5. **Failure vocabulary (seed):** `inclusion_semantics_ambiguous` · `label_grammar_invalid` · `label_identity_conflict` · `label_orphan_event` · `span_reversed` · `trial_incomplete` · `deletion_coverage_unavailable` · `session_incomplete` · `schema_unsupported` · `query_limit_exceeded` · `source_unreadable`.
6. **Fixture policy:** regression fixtures are hand-sanitized minimal extracts (schema-faithful, content-redacted); no raw transcript bodies in the repo.

## 7. Conclusion

M1 exit evidence met: one real ordinary session (user→assistant turn with tools/steps, §3) and the legacy labeled capture (6 sessions, §4) are mapped field by field from live data, and every coding assumption that would otherwise be silent is recorded as a numbered ambiguity. Ready for design_001: normalized schema, label/experiment contracts, module architecture, and the TDD behavior list.
