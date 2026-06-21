# FEATURE: RAG (Retrieval Augmented Generation)

## Overview
AgentX RAG feature provides a comprehensive Retrieval Augmented Generation system that allows users to create, manage, and query multiple RAG repositories within a session. The system supports web content ingestion, vector storage, and context-aware chat interactions.

## Core Capabilities

### 1. Multi-Repository Management
- **Repository Creation**: Users can create multiple RAG repositories (named with `rag_` prefix)
- **Repository Selection**: Interactive selection interface to load existing repositories
- **Repository Persistence**: Each repository maintains its own SQLite database (`rag.db`) tracking ingestion history
- **Session Integration**: Repositories are managed within the session context via `SessionController`

### 2. Web Content Ingestion
- **URL-based Ingestion**: Extract and index content from websites via URL
- **Configurable Extraction Levels**:
  - **Low**: Conservative crawling (max_depth=1, max_breadth=5, max_pages=10)
  - **Mid**: Moderate crawling (max_depth=2, max_breadth=10, max_pages=50)
  - **High**: Deep crawling (max_depth=3, max_breadth=20, max_pages=100)
- **Automated Pipeline**:
  1. Site mapping via Tavily API
  2. Content extraction with depth/breadth controls
  3. Document processing and chunking
  4. Batch indexing into ChromaDB vector store (batch_size=500)
  5. Persistence to JSONL documents file

### 3. Context-Aware Chat System
- **Conversation History**: Maintains chat history for context-aware responses
- **History-Aware Retrieval**: Uses LangChain's `create_history_aware_retriever` to rephrase queries based on conversation context
- **Document Chain**: Employs `create_stuff_documents_chain` for intelligent document combination
- **Source Attribution**: Displays source URLs for all retrieved documents
- **Interactive Interface**: Chat loop with quit/exit commands

### 4. Architecture Components

#### Model Layer (`src/agentx/model/rag/`)
- **`Rag`**: Main orchestrator class managing working directory, vector DB, documents, and SQLite database
- **`RagDatabase`**: SQLite database manager for ingestion tracking (table: `ingestion`)
- **`RagRepository`**: Data class representing a RAG repository (path, id)
- **`RagProvider`**: Repository provider managing discovery and listing of repositories
- **`RagQuery`**: Query engine using LangChain chains for retrieval and generation
- **`RagChatHistory`**: Chat history management (prompts, answers, conversation turns)
- **`WebIngestionApp`**: Async web ingestion orchestrator
- **`WebExtract`**: Web extraction controller with depth/breadth limits

#### UI Layer (`src/agentx/ui/screens/rag/`)
- **`RagController`**: Main RAG screen controller (MVC pattern)
- **`RagView`**: Main menu interface with options: Select Repository, Web Ingestion, RAG Chat, Quit
- **`RagRepositorySelectionController`**: Repository selection and creation
- **`RagWebIngestionController`**: Web ingestion workflow (URL input, extraction level selection)
- **`RagChatController`**: Chat interaction processor
- **`RagCreateRepositoryController`**: Repository creation (placeholder)

#### Data Storage
- **Vector Store**: ChromaDB (`chroma_db/` directory)
- **Documents**: JSONL format (`documents.jsonl`)
- **Metadata**: SQLite database (`rag.db`) with ingestion tracking
- **Repository Structure**: `{working_directory}/rag_{repository_name}/`

## Technical Stack
- **Vector Database**: ChromaDB via `langchain_chroma`
- **LLM Provider**: OpenRouter via `AIService`
- **LangChain Components**:
  - `create_stuff_documents_chain`
  - `create_history_aware_retriever`
  - `create_retrieval_chain`
- **Web Extraction**: Tavily API for site mapping and content extraction
- **Async Processing**: Python asyncio for web ingestion pipeline
- **UI Framework**: Custom MVC++ pattern with console-based interface

## Data Flow

### Repository Selection Flow
```
User → RagController → RagRepositorySelectionController → RagProvider
    → List repositories (rag_*) → Filter by rag.db existence → Return selected repository
```

### Web Ingestion Flow
```
User URL → InputUrlController → RagWebIngestionController → Rag
    → WebIngestionApp → Tavily Map → WebExtract (async)
    → Document Processing → ChromaDB Indexing → rag.db tracking
```

### Chat Query Flow
```
User Query → RagChatController → Rag → RagQuery
    → History-Aware Retriever → LLM (OpenRouter)
    → Document Chain → Formatted Response with Sources
```

## Current Limitations
1. **Repository Creation**: `RagCreateRepositoryController` is a placeholder (not implemented)
2. **Repository Selection**: `get_selected_repository()` returns `None` (incomplete implementation)
3. **State Management**: `get_rag_state()` in `RagController` returns `None` (commented out code)
4. **Document Types**: Currently supports web ingestion only (PDF/MD mentioned in original spec but not implemented)
5. **Multi-Repository Session**: While architecture supports multiple repositories, session management for switching between repositories is incomplete

## File Structure
```
src/agentx/
├── model/rag/
│   ├── rag.py                      # Main RAG orchestrator
│   ├── rag_db.py                   # SQLite database manager
│   ├── rag_repository.py           # Repository data class
│   ├── rag_provider.py             # Repository discovery
│   ├── query/
│   │   ├── rag_query.py            # Query engine with LangChain
│   │   └── rag_prompts.py          # Chat and rephrasing prompts
│   └── web_ingestion/
│       ├── web_ingestion_app.py    # Async ingestion orchestrator
│       ├── web_extract.py          # Web extraction logic
│       ├── documents.py            # Document processing
│       └── helpers.py              # Utility functions
└── ui/screens/rag/
    ├── rag_controller.py           # Main RAG controller
    ├── rag_view.py                 # Main RAG view
    ├── rag_repository_selection_controller.py
    ├── rag_repostitory_selection_view.py
    ├── rag_create_repository_controller.py
    ├── rag_web_ingestion_controller.py
    ├── rag_web_ingestion_view.py
    ├── rag_chat_controller.py
    ├── rag_chat_view.py
    └── constants.py                # Extraction level presets
```

## Integration Points
- **Session Management**: `SessionController.get_directory_rag()` for working directory
- **AI Services**: `AIService` for LLM and ChromaDB instances
- **Utilities**: Directory/file validation, URL validation

## Status
**Implementation Phase**: Core functionality implemented with some incomplete features
- ✅ Repository discovery and listing
- ✅ Web ingestion pipeline (async)
- ✅ Context-aware chat with history
- ⚠️ Repository creation (placeholder)
- ⚠️ Repository selection return value (returns None)
- ⚠️ State management (commented out)
