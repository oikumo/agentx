# KB v4 Accuracy Fixes — Plan

> **Status**: ✅ Complete — all changes applied and verified (see §0) | **2026-06-06**
> **Target**: `mcp_servers/knowledge_base/kb/` (stats) + `README.md` / `AGENTS.md` (tool-name drift)
> **Version**: 0.1.0
> **Confidence**: 0.9
> **OMT++ Phase**: Analysis + Design (Programming/Testing gated on approval)
> **Created**: 2026-06-06
> **Origin**: Follow-up to the `meta-harness.md` v4 update (KB entry `COR-6F6D`)

---

## 0. Scope & Progress

This project fixes **two accuracy defects** discovered while updating `.meta/doc/meta-harness.md` to v4:

| # | Issue | Type | Status |
|---|-------|------|--------|
| **A** | `kb_stats_tool` reports `total=1879` but type/category/confidence rows sum to `1000` (sampling cap) | Code bug | ✅ Complete |
| **B** | `README.md` & `AGENTS.md` list graph tools as `kb_graph_analyze/query/impact/export/sync` — these do **not** exist; `server.py` exposes 7 different extended tools | Documentation drift | ✅ Complete |

**Out of scope**: any new RAG features, re-populating the KB, renaming the live MCP tool surface. `.meta/doc/meta-harness.md` is already corrected (precedent for the target wording).

---

## 1. Executive Summary

The KB v4 surface is functionally healthy (1879 entries, 443 tests passing), but two
**accuracy** problems mislead agents and humans:

1. **Stats don't reconcile.** `kb_stats_tool` mixes an *exact* total with *sampled*
   breakdowns, so the numbers visibly disagree (1879 vs 1000) and the distribution is
   biased toward whatever ChromaDB returns first.
2. **Docs describe a non-existent API.** `README.md` and `AGENTS.md` advertise five
   graph tools (`kb_graph_analyze`, `kb_graph_query`, `kb_graph_impact`,
   `kb_graph_export`, `kb_graph_sync`) that are **not** in `server.py`. The real surface
   is **14 tools** (7 core + 7 extended). An agent calling the documented names will fail.

Both are low-risk, high-clarity fixes. Issue A is a contained code change plus a test;
Issue B is documentation alignment to the ground truth (`server.py`).

---

## 2. Problem Analysis (OMT++ Analysis Phase)

### 2.1 Issue A — Stats sampling vs. total mismatch

**Evidence (live `kb_stats_tool`):**

```
Total Entries: 1879
By Type:     pattern: 197 | finding: 803            → sums to 1000
By Category: class: 197 | method: 641 | function: 162 → sums to 1000
Confidence:  High (≥0.9): 1000                       → sums to 1000
```

**Root cause (`kb/api.py:330-369`):**

```python
def stats(store=None) -> StatsResult:
    total = store.count()                       # L334  → EXACT (1879)
    ...
    for metadata in store.sample_metadata(limit=1000):   # L338 → CAPPED at 1000
        by_type[t] += 1
        by_category[c] += 1
        confidences.append(...)
```

`kb/store.py:238-247`:

```python
def sample_metadata(self, limit=1000, collection_name=None):
    col = self.get_or_create_collection(...)
    sample = col.get(limit=limit)               # L244 → only first `limit` rows
    ...
```

So `total_entries` is the true collection count while `by_type`, `by_category`,
`confidence_distribution`, `mean_confidence`, and `median_confidence` are computed over
only the first 1000 rows. Beyond the obvious sum mismatch, the **sample is not random** —
`col.get(limit=...)` returns rows in storage order, so the distribution is biased.

**Impact**: Misleading health metrics; any agent reasoning about KB composition gets wrong
proportions once the KB exceeds 1000 entries.

### 2.2 Issue B — Graph tool-name drift across docs

**Ground truth** — `server.py` exposes **14** `@mcp.tool()` functions:

| Core RAG (7) | Extended / Graph (7) |
|--------------|----------------------|
| `kb_search_tool` | `kb_graph_tool` (ops: list/traverse/layers/entry_points) |
| `kb_ask_tool` | `kb_impact_tool` |
| `kb_add_tool` | `kb_visualize_tool` |
| `kb_stats_tool` | `kb_trace_flow_tool` |
| `kb_reset_tool` | `kb_code_location_tool` |
| `kb_populate_workspace_tool` | `kb_find_pattern_tool` |
| `kb_list_categories` | `kb_session_tool` |

**Drift locations:**

| File | What it says | Reality |
|------|--------------|---------|
| `mcp_servers/knowledge_base/README.md` (L11, L98-106) | "10 tools"; graph tools = `kb_graph_analyze/query/impact/export/sync` | 14 tools; names above |
| `AGENTS.md` (§ "Knowledge Graph Tools (v4 - 5 tools)") | 5 tools = `kb_graph_analyze/query/impact/export/sync` | 7 extended tools; names above |
| `.meta/doc/meta-harness.md` | — | ✅ already corrected (use as wording reference) |

**Impact**: Tool calls using documented names fail; internal contradiction (README even
says "10 tools" but lists 12).

---

## 3. Design (OMT++ Design Phase)

### 3.1 Issue A — Exact, batched stats

**Decision**: compute distributions from **all** metadata, not a 1000-row sample, using
**batched pagination** to bound memory.

**3.1.1 New store method** (`kb/store.py`)

```python
def iter_metadata(self, batch_size=1000, collection_name=None):
    """Yield every metadata dict in the collection, paged by (limit, offset)."""
    col = self.get_or_create_collection(collection_name or self._collection_name)
    offset = 0
    while True:
        page = col.get(limit=batch_size, offset=offset)
        metas = page.get("metadatas") or []
        if not metas:
            break
        for m in metas:
            if m:
                yield m
        if len(metas) < batch_size:
            break
        offset += batch_size
```

- Keep `sample_metadata()` for cheap previews (or mark deprecated) — non-breaking.
- **Verify** the pinned `chromadb` version supports `offset` on `Collection.get()`.
  Fallback if not: `col.get(include=["metadatas"])` once (no limit) — acceptable for the
  current scale (<10k) — or page via `col.get(ids=...)` over `col.peek`/`count`.

**3.1.2 Rework `stats()`** (`kb/api.py`)

```python
total = store.count()
for metadata in store.iter_metadata():     # was sample_metadata(limit=1000)
    ...
# Invariant check: sum(by_type.values()) should equal total
if sum(by_type.values()) != total:
    get_logger().warning("stats mismatch: sum(by_type)=%s total=%s", ...)
```

Result: `by_type`/`by_category` sum to `total`; mean/median computed over the full set.

**3.1.3 Optional safety valve**: add `exact: bool = True` to `stats()` (and a
`--sample` escape hatch) so very large KBs can opt back into sampling with an explicit,
clearly-labelled "(estimated from N of M)" note. Default = exact.

**Rejected alternative**: keep sampling but relabel output as "(sampled)". Cheaper, but
leaves health metrics inaccurate — rejected in favour of correctness at current scale.

### 3.2 Issue B — Align docs to `server.py`

- Rewrite the **graph/extended tools** tables in `README.md` and `AGENTS.md` to the real
  7 tools (mirror the table already in `meta-harness.md`).
- Fix tool **counts**: README "10 tools" → "14 tools (7 core + 7 extended)"; AGENTS
  "(v4 - 5 tools)" → "(v4 - 7 tools)".
- Add a one-line note: *tools are namespaced `knowledge_base_<tool>` when called via opencode*.
- Cross-check the **resources (15)** and **prompts (10)** descriptions against `server.py`
  decorators while editing, to prevent a repeat drift.

---

## 4. Implementation Plan (Programming — gated on approval)

| Phase | Task | Files | Approval gate |
|-------|------|-------|---------------|
| **P1** Stats code | Add `iter_metadata()` (batched) | `kb/store.py` | standard |
| | Verify `chromadb` `offset` support; choose fallback if needed | `kb/store.py` | standard |
| | Switch `stats()` to `iter_metadata()` + invariant log | `kb/api.py` | standard |
| | (Optional) `exact`/sample flag + labelled output | `kb/api.py`, `server.py` | standard |
| **P2** Stats tests | Fixture with >1000 entries; assert `sum(by_type)==total`, `sum(by_category)==total`, confidence counts == total | `mcp_servers/knowledge_base/tests/test_*` | **⚠️ tests/ approval (Core Directive #4)** |
| **P3** Docs | Fix graph-tool tables + counts | `mcp_servers/knowledge_base/README.md` | **⚠️ README approval (Core Directive #5)** |
| | Fix graph-tool table + count | `AGENTS.md` | **⚠️ system-file approval** |
| **P4** Verify | Run KB suite; run live `kb_stats_tool`; grep docs for stale names | — | standard |

**Suggested order**: P1 → P2 → P4 (validate code), then P3 → P4 (validate docs).
Issue B (docs) can also be executed independently/first since it is zero-risk.

---

## 5. Approvals & Guardrails (MANDATORY before execution)

Per `AGENTS.md` Core Directives, the following require **explicit user approval** and are
**NOT** performed by creating this plan:

1. **README.md changes** — *NEVER #5: "Change README.md (unless explicitly asked)"*.
   Applies to `mcp_servers/knowledge_base/README.md`. → Need explicit "yes, edit the KB README".
2. **tests/ changes** — *NEVER #4: "Modify tests/ dir … requires approval"*.
   Applies to adding `test_stats` cases under `mcp_servers/knowledge_base/tests/`.
3. **AGENTS.md change** — system-rules file; confirm before editing.
4. **No dependencies added** — *NEVER #3*. The fix must use the existing `chromadb` only.
5. **No commit/push** — *NEVER #1*.

If approval for docs (1/3) or tests (2) is withheld, P1 (the code fix) can still proceed
on its own.

---

## 6. Test Plan (OMT++ Testing Phase)

| Level | Test | Pass criteria |
|-------|------|---------------|
| Unit | `iter_metadata()` pages correctly across batch boundaries (e.g., 0, 1, batch_size, batch_size+1, 2500 entries) | Yields every metadata exactly once |
| Unit | `stats()` on a known fixture (e.g., 1500 mixed entries) | `sum(by_type)==sum(by_category)==total==1500`; confidence buckets sum to total |
| Regression | Existing KB suite (443 tests) | Still green |
| Manual/System | Live `kb_stats_tool` after fix | Breakdown rows reconcile with `Total Entries` |
| Docs | `rg "kb_graph_analyze|kb_graph_query|kb_graph_export|kb_graph_sync"` across repo | **0 matches** outside this plan/precedent notes |
| Docs | `rg -o "kb_[a-z_]+_tool" README.md AGENTS.md` vs `server.py` | Identical sets |

---

## 7. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| `chromadb` `.get()` lacks `offset` in pinned version | Medium | Medium | Detect & fallback to single full `get()` (fine <10k) or id-batched fetch |
| Full scan slows `stats()` on huge KBs | Low (now) | Low | Batched generator; optional `exact=False` sampling escape hatch |
| Editing AGENTS.md/README breaks other references | Low | Medium | Limit edits to the tool tables/counts; grep-verify afterwards |
| Memory spike loading all metadata | Low | Low | Generator yields per-batch; never holds full corpus |
| Scope creep into RAG behaviour | Low | Medium | Explicit out-of-scope list (§0) |

---

## 8. Success Criteria (Acceptance)

- [ ] `kb_stats_tool` breakdown rows sum to `Total Entries` (verified on live KB).
- [ ] `mean`/`median` confidence computed over the full collection.
- [ ] New stats tests pass; full KB suite stays green (≥443).
- [ ] `README.md` + `AGENTS.md` list exactly the 14 real tools; phantom names gone.
- [ ] Repo-wide grep for the 5 phantom graph names returns 0 (excluding this plan).
- [ ] No new dependencies; no commits/pushes; approvals obtained for README/tests/AGENTS.

---

## 9. Rollback

- Code: revert `kb/store.py` + `kb/api.py` changes (single logical diff); `sample_metadata`
  retained so reverting `stats()` to sampling is trivial.
- Docs: revert the table edits. All changes are text-only and individually reversible.

---

## 10. References

- Source of truth: `mcp_servers/knowledge_base/server.py` (14 `@mcp.tool()` defs)
- Bug site: `kb/api.py:330-369` (`stats`), `kb/store.py:238-247` (`sample_metadata`)
- Precedent fix: `.meta/doc/meta-harness.md` (v4 update, this session)
- KB entry: `COR-6F6D` — "Meta Harness doc updated v3.1.0 → v4.0.0"
- Conventions: `.meta/projects/kb-rag-v3/PLAN.md`, `.meta/projects/META.md`
- Methodology: `.meta/doc/omt_agent_guide.md`

---

**Author**: AI Agent (opencode)
**Date**: 2026-06-06
**Phase**: ✅ All phases complete (P1-P4 executed and verified)
**Next Step**: None — plan fulfilled. Changes can be reviewed and committed when ready.
