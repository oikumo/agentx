# analysis_001 — T3-6 selective verifiable knowledge pilot (scope lock)

> Source: Improvement002 E (mh7 intake → mh8 T3-6 per D7) + P0-3/P1-1.
> Acceptance (PROJECT.md T3-6 row): relevant change refreshes, unrelated edits don't
> re-consult; retrieval-quality check green.
> Full E text: `sandbox/meta/improvement002/IMPROVEMENT_OPTIONS.md` §E (lines 84-94).

## Current state (no invention — live evidence this session)

- Consultation proves *happened*, not *relevance*: g.think (order 50, think_consult
  ledger), g.kb (order 55, session kb_consulted flag), g.nav — all event checks.
- Prose corpus: 18 `GOTCHA_*` nav records in `.meta/META_HARNESS.omt` (lines 237-256),
  103 TA thoughts across 48 files, WORK.md scratchpad top-3 (tdd-node, testlist-prose,
  receipt round-robin). KB nav: `omt_kb_nav{nav}` returned no records for this
  surface (consult recorded, expected — same pattern as T3-4).
- Stale-knowledge precedent (live, paid this program): 092 re-pinned 3 stale pins in
  the same batch (055 static text, budget_diet live numbers, 059 NAV_INDEX_CEIL
  64956→64990 — nav records carry @tool description text, design prediction missed
  +34B). 089 established pin-STRUCTURE-not-counts + date-literal lint as the
  promote-to-check pattern E asks for.
- Repeated-discovery candidates (observed, not hypothesized): TDD node-granularity
  (blocked `omt_tdd done` twice), receipt round-robin / stage-vs-policy_ver ordering
  (089 hit), tests-canary shadow (phase-after-skip shadows approval), probe
  serialization (`JSON.stringify`, 092 root cause + 093 double-encode), read-recency
  mis-attribution (088 built per-file reads because think-consult mirror was wrong).

## What E demands (mechanism sketch from PROJECT.md)

1. Lightweight metadata on top repeated-discovery lessons ONLY (not all 103
   thoughts): affected symbol/contract, evidence/test ref, content version, expiry
   condition.
2. Change-surface retrieval (+dependents): prep delivers material once, refreshes
   when the relevant version changes; unrelated edits don't re-consult.
3. Promote hot testable lessons to checks, then retire prose; keep rationale as
   prose when not rule-able; retire obsolete recovery with documented reason.
4. Guardrail: no automatic learning path may silently grant authority or alter
   protective policy (no auto-`omt_skip`, think/protect untouched, Tier-3 excludes net).

## Pilot boundary proposal (to be approved — see question gate)

- Corpus: 3-5 lessons maximum (top repeated-discovery only), metadata as a
  sidecar JSON next to the existing nav index (no `.omt` policy change, no new gate).
- Retrieval: read-only advisory — a `kb_surface` lookup by changed-file/symbol used
  by `op:plan` prep path only; never blocks, never grants.
- Verification: golden set — relevant-change refreshes / unrelated-edit silent /
  retrieval-quality on representative tasks / promotion-retirement record shape.
- Non-goals: no auto-learning, no gate semantics change, no full-corpus migration
  (that is the broaden-after-measure step E sequences after the benchmark shows value).

## D5 overlap check (recorded)

- T3-5 prep slice (073) delivers obligations in one call; T4-1 typed policy (072)
  unifies evaluators; 088 per-file read-recency is a substrate, not retrieval.
- None attaches lesson metadata, version-triggered refresh, or promotion-to-check
  lifecycle. No re-implementation — pilot is net-new, additive, read-only.
