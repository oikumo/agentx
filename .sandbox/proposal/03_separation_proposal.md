# 03 — Separation proposal (options, recommendation, migration)

## 1. Design goals

- G1: a product contributor can build/test `agentx` without learning OMT-HDL.
- G2: a harness contributor can change gates without risking the console REPL.
- G3: no silent coupling — every cross-boundary touch is a declared contract.
- G4: solo-dev cheap — no extra repos/CI until volume demands it.

## 2. Options

### Option A — Monorepo, hard package boundaries (RECOMMENDED)

Keep one repo. Enforce §02 ownership by **paths + gates + docs**, not by repo split.

- Product: `src/agentx/**`, `tools/petri-net-studio/**`, product tests, product docs.
- Harness: `.meta/META_HARNESS.omt`, `.opencode/**`, `scripts/omt/**`, `.meta/software_development_process/**`, `.meta/templates/**`, harness tests/docs/state.
- Contract: `shared/petri-net/**` (unchanged, exemplary).
- Transverse stays namespaced: `.workflows/{agentx,meta_harness,app_knowledge_base}/`, `.projects/meta/<ns>_*`, ONE scratch root.
- Enforcement is mechanical: extend existing `@var harness_paths` / `@var root_allowlist` + `receipt_guard` + CODEOWNERS-style doc table (no new runtime).

Pros: zero migration risk, keeps `harnessc` + gates working, reversible per-step.
Cons: root still shared (`WORK.md`, `pyproject.toml`, `opencode.jsonc`); discipline, not physics.

### Option B — Two repos (product ←→ harness plugin)

- `agentx` (product + contract + product tests/docs) and `agentx-harness` (DSL + plugins + engines + methodology + harness tests) as an opencode plugin installed via config `plugin:` (npm path, per official docs).
- Product repo keeps a *pinned harness version*; harness repo dogfoods itself.

Pros: true versioning, clean CI, product contributors never see gates.
Cons: highest cost — plugin packaging, cross-repo e2e, ledger/state split, `.workflows` dual-home, pause/resume across repos. Premature at current team size (1 dev + agent).

### Option C — Document + gate-narrow only (minimal)

Adopt the §02 ownership table + gate matrix as docs, fix only the stray files (§04 P0), no moves.

Pros: hours, not days. Cons: boundary stays conventional; drift re-accumulates.

## 3. Recommendation

**Adopt A now; keep B as a named future door; execute C's P0 items as A's Phase 1.**

Rationale: the repo already has the machinery for A (`harness_paths`, `root_allowlist`, receipt guard, `harnessc` drift pins, `shared/` contract precedent). The pain is *stray files + mixed docs + dual scratch*, not repo topology. A fixes the pain without paying B's packaging bill.

## 4. Target tree (A — deltas only, everything else stays)

```text
/                          ← repo root: pool + contracts, no code
├── src/agentx/**           ← PRODUCT (no harness imports, no harness tests inside)
├── tools/petri-net-studio/ ← PRODUCT-TS (standalone)
├── shared/petri-net/       ← CONTRACT (spec/schema/examples only)
├── tests/
│   ├── product/            ← MOVED: controllers/, model/, views/, unit/, features/feature_{007,010,013,015,018,019,024,025,027,029}
│   └── scripts/omt/        ← HARNESS (unchanged path, now explicitly harness-owned)
├── scripts/omt/**          ← HARNESS-ENG (unchanged)
├── .opencode/**            ← HARNESS-RT (unchanged)
├── .meta/
│   ├── META_HARNESS.omt    ← HARNESS-DECL (unchanged)
│   ├── software_development_process/ ← HARNESS-STORE (unchanged)
│   ├── templates/          ← HARNESS-STORE (unchanged)
│   └── doc/
│       ├── product/        ← MOVED: omt++/ + petri_nets/ (product arch)
│       └── harness/        ← MOVED: harness/ + opencode_plugins/ + tdd/ (harness design)
├── .workflows/{agentx,meta_harness,app_knowledge_base}/ ← OPS (unchanged, stance line 1 kept)
├── .projects/meta/        ← PLAN (naming rule: product/* vs harness/* prefixes enforced, no moves)
├── .sandbox/              ← SINGLE scratch root (absorb sandbox/; see Phase 1)
├── README.md              ← PRODUCT manual (harness chapter shrinks to pointer → .meta/doc/harness/)
├── AGENTS.md, opencode.jsonc, GETTING_STARTED.md ← HARNESS projections/config (unchanged role)
└── WORK.md                ← POOL (single pool + per-domain views via headers, not split files)
```

Naming rules going forward:

- `.projects/meta/product_*` vs `.projects/meta/harness_*` (legacy names grandfathered, new ones prefixed).
- `.sandbox/<domain>/<topic>/` — `product/`, `harness/`, `ops/` top-level folders; `sandbox/` becomes a compat symlink/pointer, then removed.
- `tests/product/` vs `tests/scripts/omt/` — no new top-level test dirs without a domain prefix.

## 5. Phased migration (each phase independently shippable, no `src/` behavior change)

**Phase 1 — Hygiene, docs-only + moves of non-code (hours, zero risk).**
1. Create `.sandbox/{product,harness,ops}/` + move luose `.sandbox/*.md` into domain folders by topic (pauses→`ops/`, `meta_harness_*`→`harness/`, `feature_024*`→`product/`); leave compat `README` pointers.
2. Absorb `sandbox/` into `.sandbox/ops/workflows-archive/` (the workflows spec's `./sandbox/` vs real `.sandbox/` ambiguity ends; update `.workflows/META.md` §5 output paths).
3. Shrink `README.md` harness chapter to a pointer table (product chapters stay); full harness narrative lives in `.meta/doc/harness/`.
4. Move `src/agentx/test_omt_mvc_gate.py` + `src/agentx/ui/test_omt_mvc_gate.py` → `tests/scripts/omt/` (harness tests out of product source).
5. Split `.meta/doc/` into `product/` + `harness/` subdirs with index pointers (no content edits).
6. Extend `@var harness_paths` / `@var root_allowlist` + drift pins for the new paths; `harnessc check --verify-projections` green.

**Phase 2 — Gate narrowing (small, reversible).**
1. Scope `g.mvc` to product Python paths only; TS/engines use own lints.
2. Scope `g.receipt` strictly to harness surface (already intent — pin it).
3. Confirm `g.net` solo-skip (`active>1`) so product solo sessions never pay net ceremony.
4. Re-run: `harnessc check`, e2e receipt, `pytest -m "not opencode_live"`.

**Phase 3 — Pool views (optional, when volume hurts).**
1. Keep ONE `WORK.md` pool; add per-domain header views (`## Product`, `## Harness`) generated from the same rows (no split files until rows > capacity).
2. Enforce `.projects` prefix rule for new projects.

**Phase 4 — Door to B (deferred, explicit trigger).**
Trigger only when: product needs external contributors who must not install the harness, or harness needs independent versioning. Then extract `agentx-harness` as an opencode plugin repo (npm `plugin:` path), pin it from product config, split CI. Until then, B stays a paragraph, not a project.

## 6. Risks / non-goals

- R1: moves break pinned paths in tests/pins — mitigate by doing Phase 1 with `harnessc check` + full suite after each move batch.
- R2: doc-link rot — keep index pointer files at old locations for one cycle.
- R3: over-separation (duplicated tooling) — explicitly out of scope: ONE `uv` env, ONE `pytest`, ONE `WORK.md` pool.
- Non-goal: no behavior change to console REPL, Studio, gates, or nets in this proposal. Pure development-boundary work.
