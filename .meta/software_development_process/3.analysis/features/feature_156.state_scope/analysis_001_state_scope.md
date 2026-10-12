# Analysis 001 — StateScope ownership

Feature: feature_156.state_scope · Phase: Analysis · Date: 2026-10-12
Builds on: 154 (state_owner=external) + 155 (envelope stateRevision).

## Problem

Skills drift toward statefulness (`.skill-state.json`, cached verdicts, copied policy)
unless ownership is written down. Callers then can't tell where memory lives
(invocation vs session vs feature vs project vs harness) and resume invents state.
D4 already decides stateless — but no doc pins the 5 owners.

## Evidence

- 154 contract: `state_owner=external` enforced; `skill.py` rejects otherwise.
- 155 envelope: `stateRevision?` pointer (not store) + `evidence[]` pointers.
- Recover-block procedure step 1: preserve operation/path/identity (owner: invocation);
  doctor reads skill dir (owner: harness); CURRENT_STATE logs sessions (owner: project).
- Analisys §Permisos + D4 rationale: LangGraph checkpointer-vs-store split.

## Constraints

- Doc-first, new files only: `.meta/templates/state.scope.md` (ownership table) + optional
  `doctor` scope-lint (no `.skill-state.json`, no `state_owner!=external`).
- No second store, no RPC, no policy copy; skills NOT a scope (stateless routers).
- Do NOT touch net reconciliation (STALE owned elsewhere).

## Alternatives

- A) Ownership table doc + `skill.py doctor` lint for `.skill-state.json` + contract `state_owner` check (chosen — testable, minimal).
- B) Code-enforced scoped store API (rejected — second harness, violates D4).
- C) No doc, prose-only (rejected — drifts, untestable).

## Scope lock

5 scopes: invocation (single attempt, ephemeral) / session (transcript, opencode DB read-only) /
feature (FEATURE.md + phase docs) / project (PROJECT.md + CURRENT_STATE.md) / harness
(OMT tools, gates, ledger, net). Skills own NOTHING (no `.skill-state.json`).
`doctor` lint: fail on `state_owner!=external` (already) + warn on stray state files.
Pilots reference owners only.
