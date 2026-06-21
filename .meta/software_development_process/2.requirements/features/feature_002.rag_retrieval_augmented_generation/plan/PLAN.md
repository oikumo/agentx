# PLAN: RAG (Retrieval Augmented Generation) Implementation

## Current Implementation Status

### ✅ Completed Components

#### 1. Core RAG Engine
- **Rag class** (`src/agentx/model/rag/rag.py`): Main orchestrator
  - Working directory management
  - Vector DB path configuration (ChromaDB)
  - Documents JSONL storage
  - SQLite metadata database
  - Web ingestion integration
  - Query interface

#### 2. Database Layer
- **RagDatabase** (`src/agentx/model/rag/rag_db.py`): SQLite metadata store
  - Ingestion tracking table
  - Timestamp recording
  - CRUD operations for ingestion entries

#### 3. Query System
- **RagQuery** (`src/agentx/model/rag/query/rag_query.py`): Query engine
  - History-aware retrieval using LangChain
  - Document chain creation
  - Source attribution
  - Chat history management

#### 4. Web Ingestion Pipeline
- **WebIngestionApp** (`src/agentx/model/rag/web_ingestion/web_ingestion_app.py`): Async orchestrator
  - Site mapping via Tavily
  - Batch URL processing
  - Document saving (JSONL)
  - Chunking and indexing
- **WebExtract**: Configurable depth/breadth extraction limits

#### 5. UI Screens (MVC++ Pattern)
- **Main RAG Screen**: Controller + View with menu options
- **Repository Selection**: List and select repositories
- **Web Ingestion Screen**: URL input + extraction level selection
- **Chat Screen**: Interactive chat with history

#### 6. Repository Management
- **RagProvider**: Repository discovery and listing
- **RagRepository**: Repository data structure
- Auto-discovery of `rag_*` prefixed directories

---

## ⚠️ Incomplete Features

### 1. Repository Creation
**Location**: `src/agentx/ui/screens/rag/rag_create_repository_controller.py`
**Status**: Placeholder (empty implementation)
**Required**:
- User input for repository name
- Directory creation with `rag_` prefix
- Initialize SQLite database
- Register with session manager

### 2. Repository Selection Return Value
**Location**: `src/agentx/ui/screens/rag/rag_repository_selection_controller.py:24`
**Status**: Returns `None`
**Required**:
- Capture user selection from view
- Return selected `RagRepository` object
- Update `RagController.current_rag_repository`

### 3. RAG State Management
**Location**: `src/agentx/ui/screens/rag/rag_controller.py:49-67`
**Status**: Method returns `None` (implementation commented out)
**Required**:
- Uncomment and refactor state retrieval
- Ensure `Rag` instance is properly initialized
- Return `RagState` with URL, database path, documents path

### 4. Multi-Repository Session Support
**Status**: Architecture supports it, but session switching is incomplete
**Required**:
- Load repository state on selection
- Switch RAG instance context
- Maintain separate chat histories per repository

---

## 📋 Next Steps (Prioritized)

### Phase 1: Complete Core Functionality (HIGH PRIORITY)
1. **Implement Repository Creation**
   - Create `RagCreateRepositoryView` with name input
   - Implement controller logic for directory/DB creation
   - Integrate with repository selection screen

2. **Fix Repository Selection**
   - Implement `get_selected_repository()` method
   - Connect view selection to controller return value
   - Test repository loading flow

3. **Enable State Management**
   - Restore and fix `get_rag_state()` method
   - Ensure UI displays correct repository state
   - Add state validation checks

### Phase 2: Enhance Features (MEDIUM PRIORITY)
4. **Add PDF/MD Document Ingestion**
   - Extend `Rag` class with `ingest_pdf()` and `ingest_markdown()` methods
   - Create document ingestion UI screen
   - Implement document parsing (PyPDF2, markdown parser)

5. **Improve Repository Management**
   - Add repository deletion
   - Add repository rename
   - Add repository metadata (creation date, document count, etc.)

### Phase 3: Polish and Testing (LOW PRIORITY)
6. **Add Error Handling**
   - Network errors during web ingestion
   - Invalid repository states
   - Vector DB corruption recovery

7. **Performance Optimization**
   - Batch size tuning for indexing
   - Caching for frequently accessed repositories
   - Lazy loading of vector stores

8. **User Experience**
   - Progress indicators for long-running ingestions
   - Repository statistics (document count, sources)
   - Chat history persistence across sessions

---

## Technical Debt

### Known Issues
1. **Hardcoded Paths**: Vector DB and document paths use string concatenation
   - **Fix**: Use `pathlib.Path` throughout

2. **Async/Await Pattern**: Web ingestion uses `asyncio.run()` in synchronous context
   - **Fix**: Consider full async integration or document limitation

3. **Error Silencing**: Multiple `try/except` blocks return `False` without logging
   - **Fix**: Add proper logging and error propagation

4. **Commented Code**: `get_rag_state()` has commented implementation
   - **Fix**: Either implement or remove

### Refactoring Opportunities
1. **Dependency Injection**: `Rag` class creates `AIService` instances directly
   - **Improve**: Inject dependencies for testability

2. **Singleton Pattern**: Consider singleton for shared vector store instances

3. **Repository Validation**: Add validation for repository integrity on load

---

## Testing Strategy

### Unit Tests Needed
- `RagDatabase` CRUD operations
- `RagQuery` query processing (mock LLM)
- `WebExtract` depth/breadth limits
- `RagProvider` repository discovery

### Integration Tests Needed
- Full web ingestion pipeline (mock Tavily)
- Chat conversation flow
- Repository creation → ingestion → query cycle

### Manual Testing Checklist
- [ ] Create new repository
- [ ] Select existing repository
- [ ] Web ingestion with low/mid/high settings
- [ ] Chat with context-aware responses
- [ ] Verify source attribution
- [ ] Multiple repository switching

---

## Dependencies

### External Services
- **Tavily API**: Web extraction and site mapping
- **OpenRouter**: LLM access
- **ChromaDB**: Vector storage (local)

### Python Packages
- `langchain_chroma`: ChromaDB integration
- `langchain_classic`: Chain utilities
- `langchain_core`: Core abstractions
- `sqlite3`: Metadata storage (stdlib)
- `asyncio`: Async processing (stdlib)

---

## Success Criteria

### Functional Requirements
- ✅ User can create multiple RAG repositories
- ✅ User can select and load repositories
- ✅ User can ingest web content via URL
- ✅ User can chat with context-aware responses
- ✅ Sources are attributed in responses
- ⚠️ User can ingest PDF/MD documents (NOT IMPLEMENTED)

### Non-Functional Requirements
- ✅ Repository isolation (separate DBs and vector stores)
- ✅ Conversation history maintained per session
- ⚠️ Repository state persistence across sessions (PARTIAL)
- ⚠️ Error handling and recovery (MINIMAL)

---

## Last Updated
2026-06-21 (Implementation analysis completed)