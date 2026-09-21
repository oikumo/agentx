# 05 — Free-commit proposal: let the meta harness commit without user permission

> Location: `.sandbox/proposal/05_free_commit_proposal.md` · Status: DRAFT for review · Mode: advisory (no `omt_*` ceremony, no ledger writes, no `src/` edits, no harness edits applied).
> Date: 2026-09-21. Trigger: "make that meta harness make commit freely without user permission required."

## 1. Problem

Today the agent **cannot commit freely**. Every commit to `main` is gated by human permission — socially ("main mutated only via user commit/join") and procedurally (`.workflows` mandatory approval gate: "no workflow auto-applies a fix"). The user wants the meta harness to commit on its own, without a permission prompt per commit.

## 2. Current state (verified on disk 2026-09-21)

| Layer | What it says | Effect on `git commit` |
|---|---|---|
| `opencode.jsonc` `permission.bash` | `"*": "ask"`, `"git *": "allow"` (L75), deny-block `push/pull/fetch/ls-remote/remote/clone/submodule` (L79–85, generated from `@deny bash.*`) | `git commit`, `git add`, `git branch`, `git checkout`, `git stash`, `git worktree`, `git status/log/diff/show` already match `"git *": "allow"` → **no opencode prompt**. `git push` is hard-denied (remote stays denied). |
| `.meta/META_HARNESS.omt` `@doc git.plane` (L291) | "local git (branch/worktree/status/log/diff/stash/commit) allowed in `@var.git_worktree_root` sidecars only (branch `@var.git_branch_prefix`+task_id, gen-fenced claim); … main mutated only via user commit/join" | Agent may commit **in `.sandbox/bench` sidecars only**; `main` commits are user-owned by policy, not by jsonc deny. |
| `.meta/META_HARNESS.omt` `@gate g.net` (L132) + `@pred net_marking` (L123) | `fire` needs `expected_revision` + git-clean; `invariant` triple-checks net↔ledger↔git (local-only) | Commits that dirty the tree or desync the net block the next `fire`. Autonomous commits must stay ledger-visible or they become drift. |
| `.workflows/META.md` §4.3 + every workflow `# Rules` | "no multi-step workflow auto-applies a fix — stops at proposed-alternatives, user picks" | Even with commit allowed, workflows **still stop for approval** before applying. Free-commit needs an explicit carve-out here, not just jsonc. |
| `AGENTS.md` / `opencode.jsonc` | GENERATED from `.omt` via `uv run scripts/omt/harnessc.py build` (never hand-edit) | Any durable change goes in `.omt` → `harnessc check` → `build` → e2e receipt. |

Net: **the permission prompt for `git commit` is already gone at the opencode layer** (`git * = allow`). The remaining "permission required" is (a) the `main`-is-user-owned policy and (b) the workflow approval gate. This proposal targets exactly those two.

## 3. Goal / non-goals

- Goal: agent may run `git add` + `git commit` locally **without asking the user per commit**, with a recorded convention (message format, scope, no push).
- Non-goals: `git push/pull/fetch` stay denied (remote stays denied — no change to `@deny bash.git_push/*`). No `--force`, no `--amend` on shared history, no secret reads (`.env` deny stands). No auto-push, no auto-PR.

## 4. Options

### Option A — Free local commit everywhere (RECOMMENDED)

Agent may commit on any local branch **including `main`**, no per-commit ask. Push stays denied; user still owns remote motion.

- `.omt` change (canonical, then `harnessc build`):
  - `@doc git.plane`: "local git (branch/worktree/status/log/diff/stash/commit) allowed repo-wide for the agent (add+commit without per-commit ask; push/pull/fetch stay denied); main commits use `<type>(<scope>): <subject>` + `Co-authored-by: agentx-harness` trailer; no `--force/--amend` on pushed history; every commit references the ledger session/feature" (replaces "sidecars only … main mutated only via user commit/join").
  - Optionally add explicit pins (defense-in-depth, intent-visible; behavior already allowed via `git *`): extend the generated bash-allow region with `"git add *": "allow"`, `"git commit *": "allow"` above the deny block so a future `git *` narrowing can't silently re-gate commit. Source the intent in `.omt` (new `@var` or `@doc` line) so `harnessc check --verify-projections` pins it.
  - Net hygiene (no new gate): `fire`/`invariant` already require clean-tree + revision match — autonomous commits that leave the tree dirty or desync `expected_revision` block the next claim/fire by design. Add a ledger convention `kind:"commit"` (sha + message + feature) so `omt_q op=audit` can trace commit→phase.
- `.workflows` change: narrow §4.3 approval gate — "the proposal doc itself still needs user pick (step 4); **the mechanical `git commit` of an already-approved alternative does not need a second ask**." Each workflow's `# Rules` line 1 keeps its OMT stance; only the commit sub-step becomes ask-free.
- Pros: one rule, zero branch juggling; pause/resume and harness-evolution loops stop blocking on "please commit this for me"; solo-dev cheap.
- Cons: `main` history gains agent-authored commits (mitigate: message convention + atomic commits + tests green before commit + never force).

### Option B — Free commit in sidecars only (SAFE INCREMENTAL)

Agent may commit freely **only** under `@var.git_worktree_root` (`.sandbox/bench/*`, branch `feat/<task_id>`, gen-fenced claim). `main` stays user-only ("mutated only via user commit/join" kept).

- `.omt` change: keep `git.plane` sidecar scope, append "sidecar commits are ask-free (add+commit, no push); main join/commit stays a user action."
- `.workflows` change: same §4.3 narrowing but scoped to sidecar paths.
- Pros: `main` stays pristine; matches today's G1/git-plane design; smallest blast radius.
- Cons: keeps the exact friction the user complained about for `main` work (every main commit still pings the user); two-tier rule to remember; sidecar→main join still manual.

### Option C — Full auto-commit + auto-push (REJECTED, parked)

Remove `@deny bash.git_push` (and pull/fetch) so the agent can push without ask.

- Pros: end-to-end autonomy (commit → push with zero prompts).
- Cons: breaks the harness's hardest invariant ("remote access is NEVER allowed — local git only"); opens credential/remote-mutation risk; every drift-pin test (`test_omt_docs_drift_pins.py`) and the `DENY`→jsonc projection assumes push-denied; audit trail leaves the machine. **Do not do.** Park until there is a credential-scoped push design (signed, allowlisted remote, per-push ledger record) — explicitly out of scope here.

### Option D — Clarify-only (no behavior change)

Pin today's behavior explicitly (`git add/commit = allow` lines + doc sentence "commit is already ask-free; main commits remain user-owned") without changing the `main`/approval policy.

- Pros: removes confusion for zero risk.
- Cons: does not satisfy the request — commits to `main` still need the user.

## 5. Recommendation

**Adopt A now; keep C parked; D's pin-lines ship inside A as Phase 1.**

Rationale: the opencode layer already allows commit — the remaining gates are policy prose, not denys. A converts two prose gates (git.plane main-ownership + workflow commit sub-step) into an ask-free rule with guardrails, while keeping the load-bearing safeties (push denied, `.env` denied, net revision/dirty checks, e2e receipt, approval gate for *what* to do — only *committing the approved what* goes ask-free). B preserves the friction being removed; C trades a local-convenience win for a remote-safety loss.

## 6. Guardrails (ship with A, non-negotiable)

1. Local-only: `push/pull/fetch/ls-remote/remote/clone/submodule` stay `deny` (no `.omt`/`jsonc` change there).
2. No history rewriting on shared branches: no `--force`, no `--amend` after a sha has left the session, no `rebase -i` on `main` without explicit user pick.
3. Message convention: `<type>(<scope>): <subject>` + body (`why`, feature/slug, `net_rev`) + `Co-authored-by: agentx-harness` trailer; one logical change per commit.
4. Green-before-commit: `uv run pytest` (or scoped suite per phase exit) + `git status --short` + `git diff --stat` reviewed by the agent before `git add`; never commit `.env*`, `.meta/.omt/ledger.jsonl` rotations except via tooling, or scratch outside the approved scope.
5. Ledger visibility: every autonomous commit appends `kind:"commit"` (sha, message, feature/session) so `omt_q op=audit` and `invariant` can correlate net↔ledger↔git.
6. Approval gate stays for *decisions*: workflows still stop at proposed-alternatives (step 4). Only the mechanical commit of the user-picked alternative goes ask-free. No workflow auto-applies an unpicked alternative.

## 7. Migration (each phase independently shippable, no `src/` behavior change)

**Phase 1 — Pins + prose (minutes, zero risk).**
1. `.omt`: reword `@doc git.plane` per Option A; add commit-intent pins (`git add/commit = allow`) to the generated allow region source.
2. `uv run scripts/omt/harnessc.py check` → `build` → `uv run pytest tests/scripts/omt/test_omt_harness_e2e.py -q` (refresh receipt).
3. `.workflows/META.md` §4.3 + `meta_harness/META.md` notes: append the "approved-alternative commit is ask-free" sentence (docs-only).

**Phase 2 — Ledger commit record (small, reversible).**
1. Emit `kind:"commit"` on autonomous commits (net/cli or session helper); `omt_q op=audit` surfaces sha→feature.
2. Re-run: `harnessc check`, e2e receipt, `pytest -m "not opencode_live"`.

**Phase 3 — Door to C (deferred, explicit trigger).**
Trigger only when: unattended remote sync is required (CI publish bot with scoped credentials). Then design credential-scoped push (allowlisted remote, signed commits, per-push ledger approval) as its own proposal. Until then C stays a paragraph, not a project.

## 8. Risks

- R1: noisy `main` history — mitigate with convention (§6.3–6.4) + atomic commits.
- R2: commit-then-drift (net `expected_revision` stale) — already blocked by `fire`/`invariant` by design; ledger `kind:"commit"` makes it auditable.
- R3: accidental scope creep in `git add` (scratch/secret files) — mitigate with pre-commit `git status` review + `.env` hard-deny + explicit pathspec (`git add <scope>` not `git add -A` until allowlisted).
- Non-goal restated: no `src/` gate change (`g.phase/g.net/g.kb/g.think` untouched), no push, no budget change.

## 9. Approval gate (STOP — pick one)

This doc is advisory until you approve. Reply with the option to execute (or amend):

- **A** — free local commit everywhere (recommended): prose + pins + ledger convention per §5–§7.
- **B** — sidecars-only free commit (`main` stays user-owned).
- **D** — clarify-only pins, keep current `main` policy.
- **C** — parked (needs a credential-scoped push design first; not recommended now).

Do NOT execute moves/commits from this doc directly — promote the picked option into harness edits (`.omt` → `harnessc build` → e2e) only after your pick.
