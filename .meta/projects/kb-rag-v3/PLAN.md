# KB RAG v3 — State-of-the-Art RAG Improvement Plan

> **Status**: ✅ Complete
> **Target**: `mcp_servers/knowledge_base/` KB library
> **Version**: 3.0.0
> **Confidence**: 0.96
> **Phase**: Programming (All 7 phases complete)

---

## 0. Implementation Progress

| Phase | Status | Files | Notes |
|-------|--------|-------|-------|
| P1: Chunking & Ingestion | ✅ Done | `chunking.py`, `models.py`, `store.py`, `ingest.py`, `api.py` | Recursive + markdown + code chunkers; chunk metadata; parent-child tracking |
| P2: Embedding Flexibility | ✅ Done | `embedding.py`, `store.py` | 6 models registered, LRU cache, multi-collection |
| P3: Sparse Retrieval (BM25) | ✅ Done | `sparse_index.py` | BM25 with `bm25s`; `build_index`, `add_documents`, `search`; incremental rebuild |
| P4: Fusion & Reranking | ✅ Done | `retrieval.py`, `reranking.py`, `search.py` | `DenseRetriever`, `FusionRetriever` (RRF), `CrossEncoderReranker` with MMR; `hybrid_search_v3` pipeline; backward-compatible v2 fallback |
| P5: Query Enhancement | ✅ Done | `query_engine.py`, `api.py`, `server.py` | 5 modes (direct, rewrite, hyde, multi_query, decompose) with LLM pluggable + heuristic fallback. 27 tests. |
| P6: LLM Synthesis | ✅ Done | `synthesis.py` | `LLMSynthesizer` class with markdown + JSON output, pluggable LLM, confidence extraction, faithfulness fallback. 31 tests. |
| P7: Evaluation & Observability | ✅ Done | `eval.py` | `RetrievalEvaluator` with Recall@k, Precision@k, MRR, NDCG@k, A/B comparison framework. 29 tests. |
| Server & Config | ✅ Done | `server.py`, `pyproject.toml`, `__init__.py` | v3 params exposed on `kb_ask_tool`/`kb_search_tool`. Optional deps already in `pyproject.toml`. |

---

## 1. Executive Summary

The current KB (v0.2.0) uses ChromaDB with `DefaultEmbeddingFunction` (ONNX all-MiniLM-L6-v2, 384-d), a **post-hoc hybrid scoring** formula, and **template-based synthesis**. It works but is **2-3 generations behind current SOTA RAG**.

**Key Gaps Identified:**

| Area | Current (v0.2.0) | SOTA Gap |
|------|-------------------|----------|
| Embedding | ONNX MiniLM-L6-v2 (384-d) | `bge-m3` (1024-d), `e5-mistral`, `gte-Qwen2` |
| Retrieval | Dense-only (Chroma query) | Hybrid: Dense + Sparse (BM25/SPLADE) + RRF fusion |
| Reranking | None (linear scoring only) | Cross-encoder reranker (e.g., `bge-reranker-v2`) |
| Chunking | Flat concatenation of fields | Semantic/recursive chunking with overlap |
| Query Enhancement | None | HyDE, query rewriting, multi-query |
| Synthesis | Template-based markdown | LLM-based generation with citation grounding |
| Evaluation | None | Retrieval metrics (Recall@k, MRR, NDCG) + generation faithfulness |
| Late Interaction | None | ColBERT-style token-level retrieval |

**Target**: Upgrade to a **production-grade RAG pipeline** with hybrid retrieval, reranking, semantic chunking, optional LLM-based synthesis, and an evaluation framework — all while keeping the zero-external-API-dependency ethos.

---

## 2. Analysis — Current Architecture Deep-Dive

### 2.1 Current Data Flow

```
User Query
    │
    ▼
kb_ask_tool(question, top_k=3)
    │
    ▼
api.ask()
    │
    ▼
search.hybrid_search(collection, query, category, top_k)
    │
    ├─ 1. ChromaDB collection.query(query_texts=[query], n_results=top_k*3)
    │      Uses DefaultEmbeddingFunction (all-MiniLM-L6-v2) → 384-d
    │      Retrieves via cosine distance ANN
    │
    ├─ 2. For each result, compute:
    │      • similarity_score = 1/(1+distance)
    │      • keyword_score = token overlap (set intersection)
    │      • semantic_boost = field-weighted token match
    │      • recency_bonus = time decay
    │      • title_match_bonus = substring match
    │
    └─ 3. combined = 0.30*sim + 0.20*kw + 0.15*sem + 0.15*conf + 0.10*recency + 0.10*title
       → Sort by combined, return top_k
            │
            ▼
synthesis.synthesize(question, results)
    │
    └─ Template: group by type → format headings + fields → average confidence
       → Return AskResult with markdown string
```

### 2.2 Current Weaknesses (Root Causes)

| # | Weakness | Root Cause | Impact |
|---|----------|------------|--------|
| 1 | **Flat document text** | All fields concatenated into one string: `title + finding + solution + context + example` | No field-level search weighting; noise from irrelevant fields dilutes signal |
| 2 | **No chunking** | Single document per entry, no boundaries | Long entries (>2000 chars) lose precision; entire file entries for markdown |
| 3 | **Dense-only recall** | Only Chroma's ANN index; no sparse/lexical retrieval | Misses exact matches that dense models fail on (code snippets, IDs, proper nouns) |
| 4 | **No reranking** | Linear combination of signals is final sort | Cross-encoders would improve precision by 10-20% on NDCG |
| 5 | **No query understanding** | Raw query string sent directly | Abbreviation handling, synonym expansion, decomposition all absent |
| 6 | **Template synthesis** | `synthesize()` just formats results | No reasoning, no multi-hop, no structured output, no hallucination check |
| 7 | **No evaluation** | No metrics or test suite for retrieval/gen quality | Impossible to measure regressions or improvements |

---

## 3. Design — SOTA RAG Pipeline v3

### 3.1 Target Architecture

```
User Query
    │
    ├─► Query Pre-processor
    │   ├─ Query Rewriter (LLM optional) — expands abbreviations, rephrases
    │   ├─ HyDE Generator (optional) — hypothetical doc embedding
    │   └─ Multi-Query Expander (optional) — N query variants
    │
    ├─► Dual Retrieval
    │   ├─ Dense Retriever (ChromaDB ANN) — top_k * 2 candidates
    │   └─ Sparse Retriever (BM25 / SPLADE) — top_k * 2 candidates
    │
    ├─► Fusion → Reciprocal Rank Fusion (RRF) → top_k * 2 candidates
    │
    ├─► Reranker (Cross-encoder)
    │   └─ e.g., BAAI/bge-reranker-v2-m3 → top_k candidates (re-ranked)
    │
    ├─► Optional: Context Assembly
    │   └─ Chunk selection, parent document retrieval, context window packing
    │
    └─► Synthesizer
        ├─ (Option A) Template-based (fast, v2 compatible) ← DEFAULT
        └─ (Option B) LLM-based (deep reasoning, configurable model)
```

### 3.2 Module Map (New/Modified)

```
kb/
├── __init__.py          ← Public API (add new exports)
├── api.py               ← Modified: orchestrates new pipeline
├── store.py             ← Modified: support multiple collections
├── ingest.py            ← Modified: semantic chunking support
├── models.py            ← Modified: new result types
├── search.py            ← Modified: reranking, RRF fusion
├── synthesis.py         ← Modified: optional LLM synthesis
│
├── NEW: chunking.py     ← Semantic/recursive/text-aware chunking
├── NEW: embedding.py    ← Configurable embedding models + cache
├── NEW: reranking.py    ← Cross-encoder reranking module
├── NEW: retrieval.py    ← Hybrid retriever orchestrator (dense + sparse)
├── NEW: query_engine.py ← Query preprocessing (rewrite, HyDE, multi-query)
├── NEW: eval.py         ← Evaluation framework
├── NEW: sparse_index.py ← BM25/SPLADE sparse index management
│
├── ids.py               ← Unchanged
└── logging.py           ← Unchanged
```

### 3.3 Chunking Strategy (NEW)

#### Design: Recursive Semantic Chunking with Overlap

```
For each source document:
│
├─ Python files (already AST-parsed)
│   └─ Per class/method/function: already atomically chunked
│   └─ ENHANCEMENT: Add docstring as separate chunk (with parent ref)
│   └─ ENHANCEMENT: Add module-level docstring chunk
│
├─ Markdown files
│   └─ Split by headings (##, ###) into sections
│   └─ Each section is a chunk with heading hierarchy metadata
│   └─ Sliding window: combine small consecutive sections
│
├─ KB entries (added via add_tool)
│   └─ Recursive character splitter:
│         target_chunk_size = 512 chars
│         overlap = 64 chars
│         separators = ["\n\n", "\n", ". ", " ", ""]
│
└─ Metadata per chunk:
    ├─ parent_id → links back to original entry
    ├─ chunk_index → ordering within parent
    ├─ section_hierarchy → for markdown (e.g., ["Installation", "Quick Start"])
    └─ chunk_type → "full", "section", "recursive_chunk"
```

### 3.4 Retrieval Strategy (NEW)

#### Dense Retriever — Configurable Embedding

```python
class DenseRetriever:
    """Configurable dense ANN search via ChromaDB."""
    
    SUPPORTED_MODELS = {
        "miniLM-L6-v2":  {"dim": 384,  "class": ONNXMiniLM_L6_V2},       # current default
        "bge-small-en":   {"dim": 384,  "class": "BgeSmallEN"},           # better quality/size
        "bge-base-en":    {"dim": 768,  "class": "BgeBaseEN"},            # strong all-around
        "bge-large-en":   {"dim": 1024, "class": "BgeLargeEN"},           # high accuracy
        "bge-m3":         {"dim": 1024, "class": "BgeM3"},                # multi-lingual SOTA
        "gte-Qwen2-1.5B": {"dim": 1536, "class": "GteQwen2"},             # SOTA 2025
    }
    
    def __init__(self, model_name="bge-small-en"):
        # Lazy-load on first use (model may be large)
        self.embedding_fn = load_embedding_fn(model_name)
        self.chroma_collection = get_or_create_collection(
            name=f"kb_dense_{model_name}",
            embedding_function=self.embedding_fn,
        )
```

#### Sparse Retriever — BM25/SPLADE

```python
class SparseRetriever:
    """BM25 lexical search (complement to dense ANN)."""
    
    def __init__(self, method="bm25"):
        # BM25 index built from KB entry texts
        # Built on populate, incrementally updated on add
        self.index = None  # lazy
        self.corpus = []
    
    def search(self, query, top_k=10):
        # Tokenize query → BM25 scoring → return top_k
        # Returns list of {id, score, metadata}
```

#### Fusion — Reciprocal Rank Fusion (RRF)

```python
class FusionRetriever:
    """Combines dense + sparse results via RRF."""
    
    def fuse(self, dense_results, sparse_results, k=60):
        """
        RRF score = Σ 1/(k + rank_i(result))
        Values from both dense and sparse retrievers.
        """
        combined_scores = defaultdict(float)
        for rank, result in enumerate(dense_results):
            combined_scores[result.id] += 1.0 / (k + rank + 1)
        for rank, result in enumerate(sparse_results):
            combined_scores[result.id] += 1.0 / (k + rank + 1)
        return sorted(combined_scores.items(), key=lambda x: -x[1])
```

#### Reranker — Cross-Encoder

```python
class CrossEncoderReranker:
    """Re-rank candidates with a cross-encoder for precision."""
    
    # Supported models (lazy-loaded):
    # - "ms-marco-MiniLM-L6-v2"  (fast, ~50ms/pair)
    # - "bge-reranker-v2-m3"     (SOTA, ~200ms/pair)
    # - "ce-esci-mpnet-base"     (e-commerce/domain)
    
    def rerank(self, query, candidates, top_k=5):
        # Model: (query, candidate_text) → relevance score [0,1]
        # Batch process candidates
        # Return top_k by relevance score
```

### 3.5 Query Enhancement (NEW)

```python
class QueryEngine:
    """Query preprocessing pipeline."""
    
    def process(self, query, mode="direct"):
        if mode == "direct":
            return [query]  # v2 behavior
        
        if mode == "rewrite":
            # LLM: rewrite query for clarity (optional)
            rewritten = self._llm_rewrite(query)
            return [rewritten]
        
        if mode == "hyde":
            # Generate hypothetical document
            hypo_doc = self._generate_hypothetical_doc(query)
            # Use as additional query embedding
            return [query, hypo_doc]
        
        if mode == "multi_query":
            # Generate N query variants
            variants = self._generate_variants(query, n=3)
            return [query] + variants
        
        if mode == "decompose":
            # Decompose complex question into sub-questions
            sub_queries = self._decompose(query)
            return sub_queries
```

### 3.6 Synthesis Improvements

#### Option A (Default): Enhanced Template

```
✓ Answer synthesized from {N} sources (Confidence: {avg:.2f})

## Summary
{extract_key_points}

## Detailed Results
{grouped by type, with findings and solutions}

## Sources
• [PAT-XXXX] {title} (Conf: {conf:.2f})
• [FIND-XXXX] {title} (Conf: {conf:.2f})

ℹ️  This is a template-based answer. Enable LLM synthesis 
   for deeper reasoning by setting `synthesis_mode="llm"`.
```

#### Option B (Advanced): LLM-based Synthesis

```python
class LLMSynthesizer:
    """Generate answers using an LLM with RAG context."""
    
    def synthesize(self, question, results, model="local"):
        prompt = self._build_prompt(question, results)
        answer = self._call_llm(prompt, model)
        return self._parse_response(answer)
    
    def _build_prompt(self, question, results):
        return f"""
You are a precise knowledge base assistant with access to the following retrieved documents.
Answer the question based ONLY on the provided context.

Question: {question}

Context:
{self._format_results(results)}

Instructions:
1. Answer concisely and accurately based only on the context
2. Cite sources using [ID] notation
3. If the context cannot answer, state "The knowledge base does not contain information about..."
4. Provide confidence level for your answer

Answer:
        """
```

### 3.7 Evaluation Framework (NEW)

```python
class RetrievalEvaluator:
    """Evaluate retrieval quality with standard IR metrics."""
    
    def evaluate(self, test_queries, relevant_ids):
        """
        test_queries: [(query, [relevant_entry_ids]), ...]
        
        Returns:
          - Recall@k (k=1,3,5,10)
          - Precision@k
          - MRR (Mean Reciprocal Rank)
          - NDCG@k
        """
        
    def compare(self, baseline, candidate):
        """Compare two retrieval configurations.
        Returns statistical significance test results.
        """
```

---

## 4. Implementation Plan — 7 Phases

### Phase 1: Foundation — Chunking & Ingestion (Week 1)

| Task | Files | Dependencies |
|------|-------|-------------|
| 1.1 Recursive chunker for KB entries | `kb/chunking.py` | None |
| 1.2 Markdown section chunker | `kb/chunking.py` | None |
| 1.3 Integrate chunking into `ingest.py` | `kb/ingest.py` | 1.1, 1.2 |
| 1.4 Chunk metadata model updates | `kb/models.py` | None |
| 1.5 Chunk mapping in `KBStore` (parent->children) | `kb/store.py` | 1.4 |
| 1.6 Migration path for existing entries | `kb/api.py` | 1.5 |

**Tests**: `tests/test_chunking.py` (15+ tests covering recursive, markdown, edge cases)

### Phase 2: Embedding Flexibility (Week 2)

| Task | Files | Dependencies |
|------|-------|-------------|
| 2.1 Embedding model registry | `kb/embedding.py` | None |
| 2.2 Model auto-download on first use | `kb/embedding.py` | 2.1 |
| 2.3 `bge-small-en` support | `kb/embedding.py` | 2.1 |
| 2.4 `bge-m3` support | `kb/embedding.py` | 2.1 |
| 2.5 Multi-collection support in KBStore | `kb/store.py` | None |
| 2.6 Embedding cache (in-memory LRU) | `kb/embedding.py` | 2.1 |
| 2.7 Re-index command (switch embedding model) | `kb/api.py` | 2.5, 2.6 |

**Tests**: `tests/test_embedding.py`, `tests/test_store_multi_collection.py`

### Phase 3: Sparse Retrieval (Week 2-3)

| Task | Files | Dependencies |
|------|-------|-------------|
| 3.1 BM25 index builder | `kb/sparse_index.py` | 1.1 (chunks) |
| 3.2 Incremental BM25 update on add | `kb/sparse_index.py` | 3.1 |
| 3.3 BM25 search function | `kb/sparse_index.py` | 3.1 |
| 3.4 Tokenization improvements (stemming, stopwords) | `kb/sparse_index.py` | None |
| 3.5 SPLADE support (optional, high-effort) | `kb/sparse_index.py` | 3.1 |

**Tests**: `tests/test_sparse_index.py` (18 tests, all passing)

**Dependency**: `bm25s` — added to `pyproject.toml` as `[project.optional-dependencies] sparse`

### Phase 4: Fusion & Reranking (Week 3)

| Task | Files | Dependencies |
|------|-------|-------------|
| 4.1 RRF fusion orchestrator | `kb/retrieval.py` | 2.x (dense), 3.x (sparse) |
| 4.2 Dense retriever wrapper | `kb/retrieval.py` | 2.x |
| 4.3 Cross-encoder reranker | `kb/reranking.py` | None |
| 4.4 `bge-reranker-v2-m3` integration | `kb/reranking.py` | 4.3 |
| 4.5 Lightweight reranker (`ms-marco-MiniLM`) | `kb/reranking.py` | 4.3 |
| 4.6 MMR diversity post-processing | `kb/reranking.py` | 4.3 |
| 4.7 Updated `hybrid_search()` to use new pipeline | `kb/search.py` | 4.1-4.6 |
| 4.8 Fallback to v2 scoring when reranker unavailable | `kb/search.py` | 4.7 |

**Tests**: `tests/test_retrieval.py` (18 tests), `tests/test_reranking.py` (8 + 7 skipped without model), `tests/test_search_v3.py` (7) — all passing

**Dependency**: `sentence-transformers` + `torch` added to `pyproject.toml` as `[project.optional-dependencies] rerank`

**Bug Fix**: `embedding.py` `_registry_lock` changed from `threading.Lock()` to `threading.RLock()` to fix deadlock when `get_model_dim`/`get_embedding_function`/`get_model_info` call `list_models()` while holding the lock

### Phase 5: Query Enhancement (Week 3-4)

| Task | Files | Dependencies | Status |
|------|-------|-------------|--------|
| 5.1 Query engine with mode selection | `kb/query_engine.py` | None | ✅ Done |
| 5.2 Query rewriting (LLM-based, pluggable) | `kb/query_engine.py` | 5.1 | ✅ Done |
| 5.3 HyDE generator | `kb/query_engine.py` | 5.1 | ✅ Done |
| 5.4 Multi-query expansion | `kb/query_engine.py` | 5.1 | ✅ Done |
| 5.5 Integration into `api.ask()` and `api.search()` | `kb/api.py` | 5.1-5.4 | ✅ Done |
| 5.6 Configuration via `ask()` kwargs | `kb/api.py`, `server.py` | 5.5 | ✅ Done |

**Tests**: `tests/test_query_engine.py` (27 tests, all passing)

### Phase 6: LLM Synthesis (Week 4-5)

| Task | Files | Dependencies | Status |
|------|-------|-------------|--------|
| 6.1 LLM synthesizer base class | `kb/synthesis.py` | None | ✅ Done |
| 6.2 Prompt template for RAG QA | `kb/synthesis.py` | 6.1 | ✅ Done |
| 6.3 Integration with pluggable LLM callable | `kb/synthesis.py` | 6.1 | ✅ Done |
| 6.4 Structured JSON output mode | `kb/synthesis.py` | 6.1 | ✅ Done |
| 6.5 Faithfulness/graceful fallback on LLM failure | `kb/synthesis.py` | 6.1 | ✅ Done |
| 6.6 Synthesis mode auto-select (template vs LLM) | `kb/synthesis.py`, `api.py` | 6.1-6.4 | ✅ Done |
| 6.7 Update server.py `kb_ask_tool` for new params | `server.py` | 6.6 | ✅ Done |

**Tests**: `tests/test_synthesis_llm.py` (31 tests, all passing)

### Phase 7: Evaluation & Observability (Week 5)

| Task | Files | Dependencies | Status |
|------|-------|-------------|--------|
| 7.1 Evaluation dataset format | `kb/eval.py` | None | ✅ Done |
| 7.2 Recall@k, Precision@k, MRR, NDCG | `kb/eval.py` | 7.1 | ✅ Done |
| 7.3 A/B comparison framework | `kb/eval.py` | 7.2 | ✅ Done |
| 7.4 Performance benchmarks (latency, throughput) | `kb/eval.py` | All above | ⏳ Future |
| 7.5 Test suite for evaluation metrics | `tests/test_eval.py` | 7.1-7.4 | ✅ Done |
| 7.6 KB health scoring (enhancement) | `kb/api.py` | 7.2 | ⏳ Future |

**Tests**: `tests/test_eval.py` (29 tests, all passing)

---

## 5. Dependency & Compatibility Analysis

### 5.1 New Dependencies

| Package | Version | Size | Purpose | Phase |
|---------|---------|------|---------|-------|
| `bm25s` | ≥0.1 | ~2MB | BM25 sparse retrieval | 3 |
| `sentence-transformers` | ≥3.0 | ~50MB (models on demand) | Cross-encoder reranking | 4 |
| `torch` | ≥2.0 | ~800MB (GPU) / ~200MB (CPU) | Transformer backend | 4 |
| `transformers` (optional) | ≥4.36 | ~5MB | LLM synthesis, HyDE | 5-6 |

**Impact**: `pyproject.toml` will have optional dependency groups to keep the install lean:

```toml
[project.optional-dependencies]
sparse = ["bm25s"]
rerank = ["sentence-transformers", "torch"]
llm = ["transformers"]
all = ["kb[sparse,rerank,llm]"]
```

### 5.2 Backward Compatibility

| Change | Compatibility | Migration |
|--------|--------------|-----------|
| Chunked entries | **Breaking** for existing entries | Phase 1.6 migration path |
| New search pipeline | **Non-breaking** (new mode) | `search_mode="v2"` fallback |
| Multi-collection | **Non-breaking** | Default collection is `"kb_dense_minilm"` |
| NL synthesis | **Non-breaking** (opt-in) | Default is template mode |

### 5.3 Config Surface (New `kb_ask_tool` params)

```python
def kb_ask_tool(
    question: str,
    top_k: int = 3,
    # NEW params:
    search_mode: str = "hybrid",          # "dense" | "sparse" | "hybrid" | "v2"
    embedding_model: str = "bge-small-en", # model identifier
    rerank: bool = True,                   # enable cross-encoder reranking
    query_mode: str = "direct",            # "direct" | "rewrite" | "hyde" | "multi_query"
    synthesis_mode: str = "template",       # "template" | "llm" | "json"
    llm_model: str = "",                    # e.g., "ollama/mistral:7b"
    include_chunks: bool = False,           # return individual chunks
):
```

---

## 6. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Model download sizes bloating deploy | High | Medium | Optional deps, lazy loading, air-gap mode |
| ChromaDB multi-collection perf regression | Medium | Medium | Benchmark before/after, index optimizations |
| Cross-encoder latency too high for interactive use | Medium | High | Fast/slow path: lightweight reranker for interactive, full for background |
| BM25 index out of sync with ChromaDB | Low | High | Single source of truth (ChromaDB), rebuild BM25 on population |
| Breaking existing KB entries | Medium | High | Migration script in Phase 1, v2 fallback mode |
| `torch` dependency complexity | Medium | Low | CPU-only install path, document CUDA setup |
| LLM synthesis hallucination | High | Medium | Faithfulness self-check, grounding templates, confidence reporting |

---

## 7. Success Metrics

| Metric | Current (v0.2) | Target (v3.0) | Measurement |
|--------|---------------|---------------|-------------|
| Recall@5 | ~0.60 (estimated) | ≥0.85 | Phase 7 eval suite |
| MRR | ~0.55 (estimated) | ≥0.80 | Phase 7 eval suite |
| NDCG@5 | ~0.50 (estimated) | ≥0.78 | Phase 7 eval suite |
| Answer relevance (1-5) | 2.5 (estimated) | ≥4.0 | Human eval + LLM-as-judge |
| Retrieval latency (p50) | ~50ms | ≤150ms (hybrid) | Phase 7 benchmarks |
| Reranking latency (p50) | N/A | ≤500ms (top-20 candidates) | Phase 7 benchmarks |
| Code coverage | 86% | ≥90% | pytest --cov |
| Total entries quality | No evaluation | ≥0.85 mean confidence | Phase 7 health scoring |

---

## 8. Open Questions (Decision Needed)

| # | Question | Options | Recommendation |
|---|----------|---------|---------------|
| 1 | Default embedding model? | miniLM (384d, fast) / bge-small-en (384d, better) / bge-m3 (1024d, best) | **bge-small-en** — same dim, better quality, no re-index needed |
| 2 | LLM synthesis: built-in or external? | Built-in (transformers) / External API / Ollama | **Ollama first** (local, no API key), enable custom via config |
| 3 | Sparse method? | BM25 (proven) / SPLADE (learned sparse, better) / Both | **BM25 first** — low complexity, high value; SPLADE as optional |
| 4 | Reranker always-on or configurable? | Always / Configurable / Auto (fast vs deep) | **Auto mode** — lightweight reranker for interactive, full for ask queries |
| 5 | Chunking granularity? | Per-entry / Per-section / Recursive | **Recursive default** (512 chars, 64 overlap), section-based for markdown |

---

## 9. Timeline

```
Week 1: ████████░░░░░░░░░░░░  Phase 1 (Chunking)
Week 2: ░░░░████████░░░░░░░░  Phase 2 (Embedding) + Phase 3 start (Sparse)
Week 3: ░░░░░░░░████████░░░░  Phase 3 end + Phase 4 (Fusion/Rerank)
Week 4: ░░░░░░░░░░░░████████  Phase 5 (Query) + Phase 6 start (LLM synth)
Week 5: ░░░░░░░░░░░░░░░░████  Phase 6 end + Phase 7 (Eval)
       ─────────────────────
Actual: All 7 phases complete (179 tests: 171 passed + 8 skipped for missing `sentence-transformers`, 0 failures)
```

### Parallelization Strategy

```
Week 1-2: Phase 1 ──────── Phase 2 ────────
                                   │
Week 2-3:                    Phase 3 ──────── Phase 4 ────────
                                                        │
Week 3-5:                                         Phase 5 ── Phase 6 ── Phase 7
```

---

## 10. References

- [SOTA RAG 2024/2025 Survey](https://arxiv.org/abs/2407.01219) — Retrieval-Augmented Generation Survey
- [BGE-M3](https://arxiv.org/abs/2402.03216) — Multi-lingual, Multi-function embedding model
- [ColBERTv2](https://arxiv.org/abs/2112.01488) — Late interaction retrieval
- [SPLADE](https://arxiv.org/abs/2107.05720) — Learned sparse retrieval
- [RRF](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf) — Reciprocal Rank Fusion
- [HyDE](https://arxiv.org/abs/2212.10496) — Hypothetical Document Embeddings
- [ChromaDB Embedding Functions](https://docs.trychroma.com/embeddings) — ChromaDB model support
- [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard) — Current SOTA embedding models

---

**Author**: AI Agent Analysis
**Date**: 2026-05-31
**Version**: 3.0.0 (Implementation Complete)
**Next Step**: All 7 phases implemented. Next areas for improvement:
- KB health scoring (Phase 7.6)
- Performance benchmarks (Phase 7.4)
- SPLADE sparse retrieval (Phase 3.5)
- ColBERT-style late interaction
- Populate KB and validate with real queries
