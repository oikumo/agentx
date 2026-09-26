# Discharge Analysis — feature_130 (sandbox only)

Source: `stage_real_tokens_analysis.md` + `stage_real_tokens_design.md` (feature_129: seam + `--ledger` + threshold-on-measured-tokens, digest `40e6ab74b10b038a`) + CURRENT_STATE.md discharge path ("hand-capture real H1/H3 sessions per arm ... or wire a live exporter through `_read_host_total`") + proposal §§14.2 (fair comparison), 14.3 (token discipline), 15.6 (cost-benefit gate).
Rule: sandbox only; no src/net/ledger/toolbox change; advisory-only holds. **User direction (2026-09-26): use opencode real logs; add labels in the prompts to check opencode logs.**

## Problem

feature_129 left Tier-2 gate item (1) **ready-not-discharged**: the span seam, ledger mode, and threshold-on-measured-tokens exist and replay byte-stable, but no real H1/H3 token capture exists (`stage_real_tokens_ledger.json` absent) → the honest report reads `inconclusive_host_usage_unavailable`. Discharge is a **data change, not a design change** (design.md §Expected first-run outcome).

## Data source (verified live, read-only)

opencode stores sessions in `~/.local/share/opencode/opencode.db` (sqlite). Verified on 2026-09-26:

- `session` rows carry cumulative `tokens_input`, `tokens_output`, `tokens_reasoning`, `tokens_cache_read`, `tokens_cache_write`, `cost`, `model`, `agent`, `directory`, `parent_id`.
- Subagent (Task-tool) sessions land as **dedicated child sessions** (`parent_id` set, `directory` = this project, title echoing the task description) — a session devoted to exactly one (arm, case) gives clean attribution with no slicing.
- Column semantics verified against per-message sums on a real session (`ses_f3eb2547bf*`): `tokens_input` excludes cache reads; `tokens_output` excludes reasoning — all five columns are separate sums over messages.
- **Measurement mapping:** `prompt_tokens = tokens_input + tokens_cache_read` (total context processed) · `completion_tokens = tokens_output + tokens_reasoning` (total generated). Disclosed in ledger provenance.

## Attribution mechanism (user-directed): labels in prompts

Every capture session's prompt starts with `[harness_reason:discharge arm=<arm> case=<H1|H3>]` and the task description carries the same marker. Harvest (read-only sqlite) finds this project's child sessions created after capture start, verifies the label in the session's first user part, and maps each session to exactly one ledger key `<arm>:<case>`. Labels make the logs checkable after the fact without trusting titles alone.

## Session matrix (6 sessions — minimal design-conformant discharge)

| # | arm | case | batch/order |
|---|-----|------|-------------|
| 1 | harness | H1 | batch 1 slot 0 |
| 2 | planner | H1 | batch 1 slot 1 |
| 3 | kernel | H1 | batch 1 slot 2 |
| 4 | kernel | H3 | batch 2 slot 0 (rotated) |
| 5 | planner | H3 | batch 2 slot 1 |
| 6 | harness | H3 | batch 2 slot 2 |

H1/H3 are the reuse-sensitive §15.6 cases (the only ones where kernel savings may appear; feature_129's own next-obligation says "capture ledger (H1/H3 first)"). R=3 replay discipline is preserved by the runner (one capture replayed across reps — the documented feature_129 caveat, per-rep keys remain a future refinement).

## Task specs (identical inputs for all arms — §14.2 fairness)

- **H1 (reuse across two real contexts — R2 pattern):** candidate re-instantiates the `verify_candidate` macro for Ctx-A (artifact = content-digest of `stage0_contracts.json`) and Ctx-B (artifact = content-digest of `stage0_ir.json`). Deliver: per-context verdicts + fresh obligations, an explicit h2-with-h1 refusal demonstration (location), and a reused-vs-fresh step accounting.
- **H3 (interruption/resume with reuse — R3 pattern):** on a `/tmp` copy of `.sandbox/harness_reason/`: build sha256 manifest (pre-interruption state), record one small derivation for each of 4 named files, mutate exactly one, resume → preserved (digest-equal → reuse) vs stale (re-import + re-derive), never mixed-epoch, count avoided steps.

Arm method instructions (the only inter-arm difference, by design):

- **harness (A0):** existing harness discipline as-is — receipt/dependency-authority thinking (features 075/085 class): evidence is per-artifact, freshness is digest-match, stale inputs re-import.
- **planner (A1):** FIRST write a conventional typed plan (signatures/templates + per-step obligations), then execute it. No kernel scripts.
- **kernel (A2):** derive verdicts by calling the kernel ops (`run_composer.expand_verify_candidate` / `run_composer.rewrite` / `run_checker.make_cert` / `run_checker.explain`) via /tmp drivers under `uv run --no-sync python`; read verdicts from certs/refusals.

Fairness disclosures: same task text verbatim, same model (inherited by all subagents), same subagent type, repo read-only + `/tmp` scratch budgets, rotated spawn order; arms are told to work naturally (neither artificially brief nor padded) since session token usage is the measurand.

## What stays identical from feature_129

`run_real_tokens.py` unchanged (seam, `--ledger` override, ORACLE replay, ORDERS R=3, V1–V8, digest discipline); ledger row shape `{prompt_tokens, completion_tokens}` (+ optional `latency_ms`; provenance keys are ignored by the runner); threshold rule `>=15% median measured-token reduction, no correctness loss, no authority divergence`.

## Honest caveats (stated, never silently promoted)

- One capture per (arm, case), replayed across R=3 reps — medians sit on 2 distinct real points per arm.
- `proxy` stays **`mixed`** (T01–T12 + H2 remain unmeasured) — the verdict is a measured reading on the reuse-sensitive cases only.
- Kernel arm drives the sandbox kernel scripts (the Tier-1 `reason_check` tool is not exposed to subagents) — that is the Tier-0/1 reality being measured.
- Small pilot; variability note unchanged ("small pilot proves nothing universal").

## Alternatives (rejected)

- **Hand-capture from user-run UI sessions** — same ledger, but manual, slower, and not reproducible from labels; the labeled-subagent path is the same honesty with mechanical provenance.
- **Wire `_read_host_total` to the live DB** — span deltas around instant deterministic replays would be ~0 tokens (nothing runs inside a span); misleading, and V8 forbids zero-token measured rows.
- **Calibrated proxy (alt C from feature_129)** — stays `proxy:true` family; does not discharge gate item (1).

## Exit criteria (Design gate)

- This analysis covers data source (verified), label mechanism, matrix, task specs, arm methods, measurement mapping, caveats, alternatives.
- Design (`discharge_design.md`) lists: exact label spec + full session prompts, harvest query + harvester outline, ledger schema with provenance, `--ledger` re-run procedure, regression set.
- Probe outcome: 6 labeled sessions harvested → ledger parses → `run_real_tokens.py --ledger` 8/8 with threshold verdict on measured medians.
- No src/tests/net/toolbox change — `git status` shows only `.projects/meta`, `WORK.md`, `.meta/.../feature_130/`, `.sandbox/harness_reason/`.
